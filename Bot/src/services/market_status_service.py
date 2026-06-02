from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any, Optional

import aiohttp

from src.integrations.polymarket_gamma_client import fetch_market_by_slug
from src.services.market_tradability import is_tradable_market, market_skip_reason

logger = logging.getLogger(__name__)

MARKET_STATUS_CACHE_TTL_SEC = 300


@dataclass
class _CachedMarketStatus:
    tradable: bool
    reason: Optional[str]
    expires_at: float


class MarketStatusService:
    def __init__(self, *, gamma_api_base: str, cache_ttl_sec: int = MARKET_STATUS_CACHE_TTL_SEC) -> None:
        self._gamma_api_base = gamma_api_base
        self._cache_ttl_sec = cache_ttl_sec
        self._cache: dict[str, _CachedMarketStatus] = {}

    async def is_trade_on_tradable_market(
        self,
        session: Optional[aiohttp.ClientSession],
        trade: dict[str, Any],
    ) -> bool:
        slug = str(trade.get("slug") or "").strip()
        if not slug:
            return True
        if session is None:
            return True

        now = time.time()
        cached = self._cache.get(slug)
        if cached is not None and cached.expires_at > now:
            return cached.tradable

        market = await fetch_market_by_slug(
            session,
            base_url=self._gamma_api_base,
            slug=slug,
        )
        if market is None:
            logger.warning(
                "Gamma market lookup failed; allowing trade alert slug=%s",
                slug[:48],
            )
            return True

        tradable = is_tradable_market(market)
        reason = market_skip_reason(market)
        self._cache[slug] = _CachedMarketStatus(
            tradable=tradable,
            reason=reason,
            expires_at=now + self._cache_ttl_sec,
        )
        if not tradable:
            logger.info(
                "Skipping trade on non-tradable market slug=%s reason=%s",
                slug[:48],
                reason,
            )
        return tradable
