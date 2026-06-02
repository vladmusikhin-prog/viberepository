from __future__ import annotations

from typing import Any, Optional


def is_tradable_market(market: dict[str, Any]) -> bool:
    """
    Whether whale alerts should be sent for trades on this Gamma market.

    Skips resolved/closed listings and markets that stopped accepting orders.
    """
    if market.get("closed") is True:
        return False
    if market.get("acceptingOrders") is False:
        return False
    if market.get("active") is False:
        return False
    return True


def market_skip_reason(market: dict[str, Any]) -> Optional[str]:
    if market.get("closed") is True:
        return "closed"
    if market.get("acceptingOrders") is False:
        return "not_accepting_orders"
    if market.get("active") is False:
        return "inactive"
    return None
