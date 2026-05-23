from src.services.category_mapper import classify_polymarket_trade


def test_classify_crypto_from_title() -> None:
    t = {"title": "Will ETH flip Bitcoin by 2027?", "slug": "eth-flip", "eventSlug": "eth-flip"}
    assert classify_polymarket_trade(t) == "Crypto"


def test_classify_sports_nba() -> None:
    t = {"title": "Lakers vs Celtics", "slug": "nba-lal-bos", "eventSlug": "nba-2026"}
    assert classify_polymarket_trade(t) == "Sports"


def test_classify_sports_football_win_on_date() -> None:
    t = {
        "title": "Will Atalanta BC win on 2026-05-24?",
        "slug": "will-atalanta-bc-win-on-2026-05-24",
        "eventSlug": "sea-atalanta-match",
    }
    assert classify_polymarket_trade(t) == "Sports"


def test_classify_politics_default() -> None:
    t = {
        "title": "Will the next Prime Minister of Hungary be Péter Magyar?",
        "slug": "pm-hungary",
        "eventSlug": "next-pm",
    }
    assert classify_polymarket_trade(t) == "Politics"


def test_seen_trade_store_bounded() -> None:
    from src.repositories.seen_trades import SeenTradeStore

    s = SeenTradeStore(max_size=3)
    assert s.try_consume("a") is True
    assert s.try_consume("a") is False
    assert s.try_consume("b") is True
    assert s.try_consume("c") is True
    assert s.try_consume("d") is True
    assert s.try_consume("a") is True
