from __future__ import annotations

import re
from typing import Any, Dict, Literal

ProductCategory = Literal["Politics", "Crypto", "Sports"]

# Polymarket sports match markets often use "Will X win on YYYY-MM-DD?"
_SPORTS_WIN_ON_DATE = re.compile(r" win on 20\d{2}-\d{2}-\d{2}")

_CRYPTO = (
    "btc",
    "bitcoin",
    "eth",
    "ethereum",
    "sol",
    "solana",
    "crypto",
    "defi",
    "token",
    "stablecoin",
    "usdc",
    "usdt",
)

_SPORTS = (
    "nba",
    "nfl",
    "mlb",
    "nhl",
    "ucl",
    "champions league",
    "premier league",
    "la liga",
    "bundesliga",
    "serie a",
    "counter-strike",
    "cs2",
    "dota",
    "valorant",
    "f1",
    "ufc",
    "boxing",
    "tennis",
    "golf",
    "super bowl",
    "world cup",
    "olympic",
    " vs ",
    " vs.",
    "spread:",
    "moneyline",
    "trail blazers",
    "lakers",
    "celtics",
    "barcelona",
    "real madrid",
    "fc ",
)


def classify_polymarket_trade(trade: Dict[str, Any]) -> ProductCategory:
    title = str(trade.get("title") or "")
    slug = str(trade.get("slug") or "")
    event = str(trade.get("eventSlug") or "")
    blob = f"{title} {slug} {event}".lower()
    if any(k in blob for k in _CRYPTO):
        return "Crypto"
    if _SPORTS_WIN_ON_DATE.search(blob):
        return "Sports"
    if any(k in blob for k in _SPORTS):
        return "Sports"
    return "Politics"
