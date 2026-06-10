from __future__ import annotations

import logging
import time
from typing import Any, Optional

import aiohttp

from src.integrations.polymarket_client import fetch_trades_for_market
from src.services.bet_analytics import MarketAnomaly, compute_market_anomaly

logger = logging.getLogger(__name__)

CACHE_TTL_SEC = 600


class MarketBaselineService:
    def __init__(
        self,
        *,
        data_api_base: str,
        trades_limit: int = 100,
        min_samples: int = 5,
        cache_ttl_sec: int = CACHE_TTL_SEC,
    ) -> None:
        self._data_api_base = data_api_base
        self._trades_limit = trades_limit
        self._min_samples = min_samples
        self._cache_ttl_sec = cache_ttl_sec
        self._cache: dict[str, tuple[float, list[float]]] = {}

    async def get_anomaly(
        self,
        session: Optional[aiohttp.ClientSession],
        trade: dict[str, Any],
    ) -> Optional[MarketAnomaly]:
        if session is None:
            return None

        condition_id = str(trade.get("conditionId") or "").strip()
        if not condition_id:
            return None

        try:
            size_usd = float(trade.get("size") or 0)
        except (TypeError, ValueError):
            return None
        if size_usd <= 0:
            return None

        sizes = await self._market_sizes(session, condition_id)
        return compute_market_anomaly(
            trade_size_usd=size_usd,
            market_sizes_usd=sizes,
            min_samples=self._min_samples,
        )

    async def _market_sizes(
        self,
        session: aiohttp.ClientSession,
        condition_id: str,
    ) -> list[float]:
        now = time.time()
        cached = self._cache.get(condition_id)
        if cached and cached[0] > now:
            return cached[1]

        trades = await fetch_trades_for_market(
            session,
            base_url=self._data_api_base,
            condition_id=condition_id,
            limit=self._trades_limit,
        )
        sizes: list[float] = []
        for t in trades:
            try:
                s = float(t.get("size") or 0)
            except (TypeError, ValueError):
                continue
            if s > 0:
                sizes.append(s)

        self._cache[condition_id] = (now + self._cache_ttl_sec, sizes)
        return sizes
