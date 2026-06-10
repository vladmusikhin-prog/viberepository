from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any, Optional

import aiohttp

from src.integrations.polymarket_client import fetch_closed_positions, fetch_trades_for_user
from src.services.bet_analytics import SkillHintKey, derive_skill_hint

logger = logging.getLogger(__name__)

HIGH_CERTAINTY_ENTRY = 0.85


@dataclass(frozen=True)
class TraderStats:
    display_name: str
    wins: int
    losses: int
    win_rate_pct: int
    total_realized_pnl_usd: float
    positions_sampled: int
    wins_usd: float
    losses_usd: float
    trades_per_month: float
    high_certainty_pct: int
    avg_entry_price: float
    period_days: int
    skill_hint_key: SkillHintKey
    skill_hint_text: str


def format_trader_display_name(trade: dict[str, Any]) -> str:
    name = str(trade.get("name") or "").strip()
    pseudonym = str(trade.get("pseudonym") or "").strip()
    if name and pseudonym:
        return f"{name} ({pseudonym})"
    if pseudonym:
        return pseudonym
    if name:
        return name
    wallet = str(trade.get("proxyWallet") or "").strip()
    if len(wallet) >= 10:
        return f"{wallet[:6]}...{wallet[-4:]}"
    return "Unknown trader"


def _position_period_days(positions: list[dict[str, Any]]) -> int:
    timestamps: list[int] = []
    for position in positions:
        for key in ("timestamp", "closedTime"):
            raw = position.get(key)
            if raw is None:
                continue
            try:
                ts = int(raw)
            except (TypeError, ValueError):
                continue
            if ts > 0:
                timestamps.append(ts)
    if len(timestamps) < 2:
        return 90
    span = max(timestamps) - min(timestamps)
    return max(1, int(span / 86400))


def _compute_entry_profile(trades: list[dict[str, Any]]) -> tuple[int, float]:
    prices: list[float] = []
    for trade in trades:
        try:
            price = float(trade.get("price") or 0.0)
        except (TypeError, ValueError):
            continue
        if 0.0 < price <= 1.0:
            prices.append(price)
    if not prices:
        return 0, 0.0
    high_count = sum(1 for price in prices if price > HIGH_CERTAINTY_ENTRY)
    high_pct = round(100 * high_count / len(prices))
    avg_price = sum(prices) / len(prices)
    return high_pct, avg_price


def _compute_trades_per_month(trades: list[dict[str, Any]]) -> float:
    timestamps: list[int] = []
    for trade in trades:
        try:
            ts = int(trade.get("timestamp") or 0)
        except (TypeError, ValueError):
            continue
        if ts > 0:
            timestamps.append(ts)
    if not timestamps:
        return 0.0
    if len(timestamps) == 1:
        return 1.0
    span_days = max(1.0, (max(timestamps) - min(timestamps)) / 86400.0)
    return round(len(timestamps) / span_days * 30.0, 1)


def compute_trader_stats(
    positions: list[dict[str, Any]],
    *,
    display_name: str,
    user_trades: Optional[list[dict[str, Any]]] = None,
) -> TraderStats:
    wins = 0
    losses = 0
    total_pnl = 0.0
    wins_usd = 0.0
    losses_usd = 0.0

    for position in positions:
        try:
            pnl = float(position.get("realizedPnl") or 0.0)
        except (TypeError, ValueError):
            pnl = 0.0
        total_pnl += pnl
        if pnl > 0:
            wins += 1
            wins_usd += pnl
        elif pnl < 0:
            losses += 1
            losses_usd += abs(pnl)

    resolved = wins + losses
    win_rate_pct = round(100 * wins / resolved) if resolved else 0
    period_days = _position_period_days(positions)

    trades = user_trades or []
    high_certainty_pct, avg_entry_price = _compute_entry_profile(trades)
    trades_per_month = _compute_trades_per_month(trades)
    skill_hint_key, skill_hint_text = derive_skill_hint(
        positions_sampled=len(positions),
        high_certainty_pct=high_certainty_pct,
    )

    return TraderStats(
        display_name=display_name,
        wins=wins,
        losses=losses,
        win_rate_pct=win_rate_pct,
        total_realized_pnl_usd=total_pnl,
        positions_sampled=len(positions),
        wins_usd=wins_usd,
        losses_usd=losses_usd,
        trades_per_month=trades_per_month,
        high_certainty_pct=high_certainty_pct,
        avg_entry_price=avg_entry_price,
        period_days=period_days,
        skill_hint_key=skill_hint_key,
        skill_hint_text=skill_hint_text,
    )


class TraderStatsService:
    def __init__(
        self,
        *,
        enabled: bool,
        positions_limit: int,
        user_trades_limit: int,
        cache_ttl_sec: int,
        data_api_base: str,
    ) -> None:
        self.enabled = enabled
        self.positions_limit = max(1, positions_limit)
        self.user_trades_limit = max(1, user_trades_limit)
        self.cache_ttl_sec = max(0, cache_ttl_sec)
        self.data_api_base = data_api_base
        self._cache: dict[str, tuple[float, TraderStats]] = {}

    async def get_stats_for_trade(
        self,
        session: Optional[aiohttp.ClientSession],
        trade: dict[str, Any],
    ) -> Optional[TraderStats]:
        if not self.enabled or session is None:
            return None

        wallet = str(trade.get("proxyWallet") or "").strip().lower()
        if not wallet:
            return None

        cached = self._cache.get(wallet)
        now = time.monotonic()
        if cached and now - cached[0] < self.cache_ttl_sec:
            stats = cached[1]
            return TraderStats(
                display_name=format_trader_display_name(trade),
                wins=stats.wins,
                losses=stats.losses,
                win_rate_pct=stats.win_rate_pct,
                total_realized_pnl_usd=stats.total_realized_pnl_usd,
                positions_sampled=stats.positions_sampled,
                wins_usd=stats.wins_usd,
                losses_usd=stats.losses_usd,
                trades_per_month=stats.trades_per_month,
                high_certainty_pct=stats.high_certainty_pct,
                avg_entry_price=stats.avg_entry_price,
                period_days=stats.period_days,
                skill_hint_key=stats.skill_hint_key,
                skill_hint_text=stats.skill_hint_text,
            )

        positions = await self._fetch_positions(session, wallet)
        user_trades = await fetch_trades_for_user(
            session,
            base_url=self.data_api_base,
            user_wallet=wallet,
            limit=self.user_trades_limit,
        )
        stats = compute_trader_stats(
            positions,
            display_name=format_trader_display_name(trade),
            user_trades=user_trades,
        )
        self._cache[wallet] = (now, stats)
        return stats

    async def _fetch_positions(
        self,
        session: aiohttp.ClientSession,
        wallet: str,
    ) -> list[dict[str, Any]]:
        remaining = self.positions_limit
        offset = 0
        collected: list[dict[str, Any]] = []

        while remaining > 0:
            page_size = min(50, remaining)
            batch = await fetch_closed_positions(
                session,
                base_url=self.data_api_base,
                user_wallet=wallet,
                limit=page_size,
                offset=offset,
            )
            if not batch:
                break
            collected.extend(batch)
            remaining -= len(batch)
            offset += len(batch)
            if len(batch) < page_size:
                break

        return collected[: self.positions_limit]
