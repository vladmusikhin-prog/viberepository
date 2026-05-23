from __future__ import annotations

import logging
from typing import Any, Optional

import aiohttp

logger = logging.getLogger(__name__)


async def fetch_market_by_slug(
    session: aiohttp.ClientSession,
    *,
    base_url: str,
    slug: str,
) -> Optional[dict[str, Any]]:
    if not slug:
        return None
    url = f"{base_url.rstrip('/')}/markets"
    params = {"slug": slug}
    timeout = aiohttp.ClientTimeout(total=30)
    try:
        async with session.get(url, params=params, timeout=timeout) as resp:
            resp.raise_for_status()
            data = await resp.json()
    except (aiohttp.ClientError, TimeoutError, OSError) as e:
        logger.warning("Gamma market request failed slug=%s: %s", slug[:40], e)
        return None

    if not isinstance(data, list) or not data:
        return None
    market = data[0]
    return market if isinstance(market, dict) else None
