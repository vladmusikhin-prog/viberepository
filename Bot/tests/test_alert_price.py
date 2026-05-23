from dataclasses import dataclass
from unittest.mock import MagicMock

from src.workers.signal_worker import SignalWorker


@dataclass
class _PriceSettings:
    whale_threshold_usd: int = 100_000
    whale_threshold_crypto_usd: int = 20_000
    alert_max_price: float = 0.95
    alert_max_price_crypto: float = 0.999

    def whale_threshold_for_category(self, category: str) -> int:
        if category == "Crypto":
            return self.whale_threshold_crypto_usd
        return self.whale_threshold_usd


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


def test_meets_whale_threshold_by_category() -> None:
    worker = _worker()
    crypto_trade = {"size": 25_000}
    sports_trade = {"size": 25_000}
    assert worker._meets_whale_threshold(crypto_trade, "Crypto") is True
    assert worker._meets_whale_threshold(sports_trade, "Sports") is False
    assert worker._meets_whale_threshold({"size": 100_000}, "Sports") is True
