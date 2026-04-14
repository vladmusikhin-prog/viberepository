from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from src.models.entities import Signal
from src.repositories.in_memory import SignalRepository, UserRepository
from src.services.texts import format_alert_text, share_text


def _demo_market_for_category(category: str) -> tuple[str, float, float]:
    """Placeholder markets aligned with category (MVP demo only)."""
    if category == "Crypto":
        return ("Will BTC reach new ATH this quarter?", 186_000.0, 0.58)
    if category == "Sports":
        return ("Will Team A win the championship this season?", 142_000.0, 0.52)
    return ("Will [political outcome] occur before [date]?", 198_000.0, 0.55)


class SignalService:
    def __init__(
        self,
        user_repo: UserRepository,
        signal_repo: SignalRepository,
        whale_threshold_usd: int,
        bot_username: str,
    ) -> None:
        self.user_repo = user_repo
        self.signal_repo = signal_repo
        self.whale_threshold_usd = whale_threshold_usd
        self.bot_username = bot_username

    def build_test_signal(self, user_id: int, category: str) -> tuple[str, str]:
        # Same shape as live; market/size/price match chosen category (not real API).
        market, size_usd, price = _demo_market_for_category(category)
        signal = Signal(
            signal_id=f"test-{uuid4()}",
            market=market,
            side="BUY YES",
            size_usd=size_usd,
            price=price,
            category=category,
            timestamp_utc=datetime.now(timezone.utc),
            is_test=True,
            delivered_to_user_id=user_id,
        )
        self.signal_repo.save(signal)
        text = format_alert_text(
            market=signal.market,
            side=signal.side,
            size_usd=signal.size_usd,
            price=signal.price,
            timestamp_utc=signal.timestamp_utc.strftime("%H:%M"),
            whale_threshold_usd=self.whale_threshold_usd,
            category=signal.category,
        )
        url_text = share_text(self.bot_username, user_id)
        return text, f"https://t.me/share/url?url=&text={url_text.replace(' ', '%20').replace(chr(10), '%0A')}"

    def build_polymarket_trade_alert(
        self,
        trade: dict,
        product_category: str,
        inviter_telegram_user_id: int,
    ) -> tuple[str, str, str]:
        """
        Build whale alert from Polymarket Data API trade row (CASH filter).
        Returns (signal_id, text, share_url).
        """
        tx = str(trade.get("transactionHash") or "")
        signal_id = f"pm-{tx}" if tx else f"pm-unknown-{uuid4()}"
        title = str(trade.get("title") or "Unknown market")
        side = str(trade.get("side") or "")
        outcome = str(trade.get("outcome") or "")
        side_label = f"{side} {outcome}".strip()
        size_usd = float(trade.get("size") or 0)
        price = float(trade.get("price") or 0)
        ts_raw = trade.get("timestamp")
        try:
            ts = int(ts_raw) if ts_raw is not None else 0
        except (TypeError, ValueError):
            ts = 0
        if ts > 0:
            dt = datetime.fromtimestamp(ts, tz=timezone.utc)
            time_s = dt.strftime("%H:%M")
        else:
            time_s = "--:--"

        text = format_alert_text(
            market=title,
            side=side_label,
            size_usd=size_usd,
            price=price,
            timestamp_utc=time_s,
            whale_threshold_usd=self.whale_threshold_usd,
            category=product_category,
        )
        share_payload = share_text(self.bot_username, inviter_telegram_user_id)
        share_url = f"https://t.me/share/url?url=&text={share_payload.replace(' ', '%20').replace(chr(10), '%0A')}"
        return signal_id, text, share_url

    def is_signal_delivered(self, signal_id: str, user_id: int) -> bool:
        return self.signal_repo.is_delivered(signal_id, user_id)

    def mark_signal_delivered(self, signal_id: str, user_id: int) -> bool:
        delivered = self.signal_repo.mark_delivered(signal_id, user_id)
        if delivered:
            self.user_repo.increment_signals(user_id)
        return delivered
