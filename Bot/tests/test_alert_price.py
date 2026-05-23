from dataclasses import dataclass
from unittest.mock import MagicMock

from src.workers.signal_worker import SignalWorker


@dataclass
class _PriceSettings:
    alert_max_price: float = 0.95
    alert_max_price_crypto: float = 0.999


def _worker() -> SignalWorker:
    return SignalWorker(
        bot=MagicMock(),
        context=MagicMock(),
        settings=_PriceSettings(),
        http_session=None,
    )


def test_alertable_price_crypto_allows_high_price() -> None:
    worker = _worker()
    assert worker._is_alertable_price(0.999, "Crypto") is True
    assert worker._is_alertable_price(0.999, "Politics") is False
    assert worker._is_alertable_price(0.999, "Sports") is False


def test_alertable_price_crypto_still_rejects_above_cap() -> None:
    worker = _worker()
    assert worker._is_alertable_price(1.0, "Crypto") is False


def test_alertable_price_non_crypto_unchanged() -> None:
    worker = _worker()
    assert worker._is_alertable_price(0.43, "Sports") is True
    assert worker._is_alertable_price(0.96, "Politics") is False
