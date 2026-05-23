from __future__ import annotations

import re
from typing import Any, Dict, Literal, Tuple

ProductCategory = Literal["Politics", "Crypto", "Sports", "Geopolitics", "Economics"]

ALL_PRODUCT_CATEGORIES: Tuple[ProductCategory, ...] = (
    "Politics",
    "Crypto",
    "Sports",
    "Geopolitics",
    "Economics",
)

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

_GEOPOLITICS = (
    "ceasefire",
    "cease-fire",
    "sanctions",
    "ukraine",
    "gaza",
    "hamas",
    "hezbollah",
    "invasion",
    "annex",
    "geopolit",
    "missile strike",
    "airstrike",
    "war in ",
    " troop",
    "occupied",
    "border clash",
    "putin",
    "zelensky",
    "taiwan strait",
    "north korea",
    "iran strike",
    "iran conflict",
    "israel strike",
    "military action",
    "nato ",
    "peace deal between",
    "russia withdraw",
)

_ECONOMICS = (
    "fed ",
    " fomc",
    "federal reserve",
    "cpi ",
    "inflation rate",
    "gdp ",
    "unemployment",
    "jobs report",
    "nonfarm",
    "payroll",
    "interest rate",
    "rate cut",
    "rate hike",
    "recession",
    "pce ",
    "retail sales",
    "consumer price",
    "core inflation",
    "macro indicator",
)


def classify_polymarket_trade(trade: Dict[str, Any]) -> ProductCategory:
    title = str(trade.get("title") or "")
    slug = str(trade.get("slug") or "")
    event = str(trade.get("eventSlug") or "")
    blob = f"{title} {slug} {event}".lower()
    if any(k in blob for k in _CRYPTO):
        return "Crypto"
    if any(k in blob for k in _GEOPOLITICS):
        return "Geopolitics"
    if any(k in blob for k in _ECONOMICS):
        return "Economics"
    if _SPORTS_WIN_ON_DATE.search(blob):
        return "Sports"
    if any(k in blob for k in _SPORTS):
        return "Sports"
    return "Politics"
