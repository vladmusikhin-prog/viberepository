from __future__ import annotations

import logging
from typing import Any, List

import aiohttp

logger = logging.getLogger(__name__)


async def fetch_large_cash_trades(
    session: aiohttp.ClientSession,
    *,
    base_url: str,
    min_cash_usd: float,
    limit: int,
    offset: int = 0,
) -> List[dict[str, Any]]:
    """
    GET /trades with CASH filter — Polymarket Data API.
    See: https://docs.polymarket.com/api-reference/core/get-trades-for-a-user-or-markets
    """
    url = f"{base_url.rstrip('/')}/trades"
    params = {
        "limit": min(max(limit, 1), 500),
        "filterType": "CASH",
        # Data API accepts integer amounts; passing float can lead to server-side timeouts.
        "filterAmount": int(min_cash_usd),
        "offset": max(int(offset), 0),
    }
    timeout = aiohttp.ClientTimeout(total=45)
    try:
        async with session.get(url, params=params, timeout=timeout) as resp:
            resp.raise_for_status()
            data = await resp.json()
    except (aiohttp.ClientError, TimeoutError, OSError) as e:
        logger.warning("Polymarket trades request failed: %s", e)
        return []

    if not isinstance(data, list):
        logger.warning("Polymarket trades: unexpected JSON shape %s", type(data))
        return []
    return data


async def fetch_closed_positions(
    session: aiohttp.ClientSession,
    *,
    base_url: str,
    user_wallet: str,
    limit: int,
    offset: int = 0,
) -> List[dict[str, Any]]:
    """
    GET /closed-positions for a wallet — Polymarket Data API.
    See: https://docs.polymarket.com/api-reference/core/get-closed-positions-for-a-user
    """
    wallet = (user_wallet or "").strip()
    if not wallet:
        return []

    url = f"{base_url.rstrip('/')}/closed-positions"
    params = {
        "user": wallet,
        "limit": min(max(int(limit), 1), 50),
        "offset": max(int(offset), 0),
        "sortBy": "TIMESTAMP",
        "sortDirection": "DESC",
    }
    timeout = aiohttp.ClientTimeout(total=30)
    try:
        async with session.get(url, params=params, timeout=timeout) as resp:
            resp.raise_for_status()
            data = await resp.json()
    except (aiohttp.ClientError, TimeoutError, OSError) as e:
        logger.warning("Polymarket closed-positions request failed: %s", e)
        return []

    if not isinstance(data, list):
        logger.warning("Polymarket closed-positions: unexpected JSON shape %s", type(data))
        return []
    return data
