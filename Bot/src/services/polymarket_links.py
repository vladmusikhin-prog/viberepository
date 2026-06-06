from __future__ import annotations

import re

_WALLET_RE = re.compile(r"^0x[a-fA-F0-9]{40}$")


def build_polymarket_profile_url(
    proxy_wallet: str,
    *,
    tab: str = "activity",
) -> str | None:
    """
    Public Polymarket profile URL for a trader's proxy wallet.
    `tab=activity` opens the trades / activity feed.
    """
    wallet = (proxy_wallet or "").strip()
    if not _WALLET_RE.fullmatch(wallet):
        return None
    base = f"https://polymarket.com/profile/{wallet}"
    tab_name = (tab or "").strip()
    if tab_name:
        return f"{base}?tab={tab_name}"
    return base
