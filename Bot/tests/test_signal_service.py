from src.repositories.in_memory import SignalRepository, UserRepository
from src.services.signal_service import SignalService


def test_mark_signal_delivered_is_idempotent() -> None:
    user_repo = UserRepository()
    signal_repo = SignalRepository()
    service = SignalService(user_repo, signal_repo, 100000, 20000, 75000, "test_bot")

    assert service.is_signal_delivered("s1", 1) is False

    first = service.mark_signal_delivered("s1", 1)
    second = service.mark_signal_delivered("s1", 1)

    assert first is True
    assert second is False
    assert service.is_signal_delivered("s1", 1) is True


def test_build_alert_uses_crypto_whale_threshold() -> None:
    service = SignalService(UserRepository(), SignalRepository(), 100_000, 20_000, 75_000, "bot")
    _signal_id, text, _url = service.build_polymarket_trade_alert(
        {
            "transactionHash": "0xabc",
            "title": "Will Bitcoin reach $150k?",
            "side": "BUY",
            "outcome": "Yes",
            "size": 25_000,
            "price": 0.99,
            "timestamp": 1_700_000_000,
        },
        "Crypto",
        inviter_telegram_user_id=1,
    )
    assert ">= $20k" in text
    assert "Crypto" in text


def test_build_alert_uses_economics_whale_threshold() -> None:
    service = SignalService(UserRepository(), SignalRepository(), 100_000, 20_000, 75_000, "bot")
    _signal_id, text, _url = service.build_polymarket_trade_alert(
        {
            "transactionHash": "0xdef",
            "title": "Will the Fed cut rates in June 2026?",
            "side": "BUY",
            "outcome": "Yes",
            "size": 80_000,
            "price": 0.58,
            "timestamp": 1_700_000_000,
        },
        "Economics",
        inviter_telegram_user_id=1,
    )
    assert ">= $75k" in text
    assert "Economics" in text
