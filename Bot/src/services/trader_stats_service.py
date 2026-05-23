from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any, Optional

import aiohttp

from src.integrations.polymarket_client import fetch_closed_positions

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class TraderStats:
    display_name: str
    wins: int
    losses: int
    win_rate_pct: int
    total_realized_pnl_usd: float
    positions_sampled: int


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


def compute_trader_stats(
    positions: list[dict[str, Any]],
    *,
    display_name: str,
) -> TraderStats:
    wins = 0
    losses = 0
    total_pnl = 0.0

    for position in positions:
        try:
            pnl = float(position.get("realizedPnl") or 0.0)
        except (TypeError, ValueError):
            pnl = 0.0
        total_pnl += pnl
        if pnl > 0:
            wins += 1
        elif pnl < 0:
            losses += 1

    resolved = wins + losses
    win_rate_pct = round(100 * wins / resolved) if resolved else 0

    return TraderStats(
        display_name=display_name,
        wins=wins,
        losses=losses,
        win_rate_pct=win_rate_pct,
        total_realized_pnl_usd=total_pnl,
        positions_sampled=len(positions),
    )


class TraderStatsService:
    def __init__(
        self,
        *,
        enabled: bool,
        positions_limit: int,
        cache_ttl_sec: int,
        data_api_base: str,
    ) -> None:
        self.enabled = enabled
        self.positions_limit = max(1, positions_limit)
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
            )

        positions = await self._fetch_positions(session, wallet)
        stats = compute_trader_stats(
            positions,
            display_name=format_trader_display_name(trade),
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
