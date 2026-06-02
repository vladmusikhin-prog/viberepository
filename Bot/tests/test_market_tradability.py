from src.services.market_tradability import is_tradable_market, market_skip_reason


def test_tradable_open_market() -> None:
    market = {"closed": False, "acceptingOrders": True, "active": True}
    assert is_tradable_market(market) is True
    assert market_skip_reason(market) is None


def test_not_tradable_when_closed() -> None:
    market = {"closed": True, "acceptingOrders": True, "active": True}
    assert is_tradable_market(market) is False
    assert market_skip_reason(market) == "closed"


def test_not_tradable_when_not_accepting_orders() -> None:
    market = {"closed": False, "acceptingOrders": False, "active": True}
    assert is_tradable_market(market) is False
    assert market_skip_reason(market) == "not_accepting_orders"


def test_not_tradable_when_inactive() -> None:
    market = {"closed": False, "acceptingOrders": True, "active": False}
    assert is_tradable_market(market) is False
    assert market_skip_reason(market) == "inactive"


def test_tradable_when_optional_fields_missing() -> None:
    market = {"closed": False}
    assert is_tradable_market(market) is True
