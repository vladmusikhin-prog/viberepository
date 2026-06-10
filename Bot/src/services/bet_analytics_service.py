from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Optional

import aiohttp

from src.integrations.polymarket_gamma_client import fetch_market_by_slug
from src.services.bet_analytics import (
    MarketAnomaly,
    SignalVerdict,
    SkillHintKey,
    TradeContext,
    build_trade_context,
    compute_signal_verdict,
)
from src.services.market_baseline_service import MarketBaselineService
from src.services.tier_service import TierService
from src.services.trader_stats_service import TraderStats

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class BetAnalyticsBundle:
    verdict: SignalVerdict
    trade_context: TradeContext
    anomaly: Optional[MarketAnomaly]
    trader_stats: Optional[TraderStats]
    is_pro: bool
    skill_hint_key: SkillHintKey


class BetAnalyticsService:
    def __init__(
        self,
        *,
        market_baseline_service: MarketBaselineService,
        tier_service: TierService,
        gamma_api_base: str,
        flash_hours_threshold: float = 24.0,
    ) -> None:
        self._baseline = market_baseline_service
        self._tier = tier_service
        self._gamma_api_base = gamma_api_base
        self._flash_hours = flash_hours_threshold
        self._gamma_cache: dict[str, tuple[float, dict[str, Any]]] = {}

    async def build_for_trade(
        self,
        session: Optional[aiohttp.ClientSession],
        trade: dict[str, Any],
        *,
        telegram_user_id: int,
        trader_stats: Optional[TraderStats],
    ) -> BetAnalyticsBundle:
        is_pro = self._tier.is_pro(telegram_user_id)

        try:
            price = float(trade.get("price") or 0)
        except (TypeError, ValueError):
            price = 0.0

        hours = await self._hours_to_resolution(session, trade)
        trade_ctx = build_trade_context(
            entry_price=price,
            hours_to_resolution=hours,
            flash_hours_threshold=self._flash_hours,
        )

        anomaly = await self._baseline.get_anomaly(session, trade)

        skill_key = SkillHintKey.INSUFFICIENT
        if trader_stats is not None:
            skill_key = trader_stats.skill_hint_key

        verdict = compute_signal_verdict(
            anomaly=anomaly,
            trade_ctx=trade_ctx,
            skill_hint_key=skill_key,
        )

        return BetAnalyticsBundle(
            verdict=verdict,
            trade_context=trade_ctx,
            anomaly=anomaly,
            trader_stats=trader_stats,
            is_pro=is_pro,
            skill_hint_key=skill_key,
        )

    async def _hours_to_resolution(
        self,
        session: Optional[aiohttp.ClientSession],
        trade: dict[str, Any],
    ) -> Optional[float]:
        if session is None:
            return None
        slug = str(trade.get("slug") or "").strip()
        if not slug:
            return None

        now = time.time()
        cached = self._gamma_cache.get(slug)
        if cached and cached[0] > now:
            market = cached[1]
        else:
            market = await fetch_market_by_slug(
                session,
                base_url=self._gamma_api_base,
                slug=slug,
            )
            if market is None:
                return None
            self._gamma_cache[slug] = (now + 300, market)

        end_raw = market.get("endDate") or market.get("endDateIso")
        if not end_raw:
            return None
        try:
            end_s = str(end_raw).replace("Z", "+00:00")
            end_dt = datetime.fromisoformat(end_s)
            if end_dt.tzinfo is None:
                end_dt = end_dt.replace(tzinfo=timezone.utc)
            delta = (end_dt - datetime.now(timezone.utc)).total_seconds()
            return max(delta / 3600.0, 0.0)
        except (TypeError, ValueError):
            return None
