from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from src.services.texts import format_alert_text, format_trader_stats_block, share_text
from src.services.trader_stats_service import TraderStats


class SignalService:
    def __init__(
        self,
        user_repo,
        signal_repo,
        whale_threshold_usd: int,
        whale_threshold_crypto_usd: int,
        bot_username: str,
        trader_stats_positions_limit: int = 100,
    ) -> None:
        self.user_repo = user_repo
        self.signal_repo = signal_repo
        self.whale_threshold_usd = whale_threshold_usd
        self.whale_threshold_crypto_usd = whale_threshold_crypto_usd
        self.bot_username = bot_username
        self.trader_stats_positions_limit = trader_stats_positions_limit

    def whale_threshold_for_category(self, category: str) -> int:
        if category == "Crypto":
            return self.whale_threshold_crypto_usd
        return self.whale_threshold_usd

    def build_polymarket_trade_alert(
        self,
        trade: dict,
        product_category: str,
        inviter_telegram_user_id: int,
        trader_stats: Optional[TraderStats] = None,
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

        trader_stats_block = None
        if trader_stats is not None:
            trader_stats_block = format_trader_stats_block(
                display_name=trader_stats.display_name,
                wins=trader_stats.wins,
                losses=trader_stats.losses,
                win_rate_pct=trader_stats.win_rate_pct,
                total_realized_pnl_usd=trader_stats.total_realized_pnl_usd,
                positions_sampled=trader_stats.positions_sampled,
                positions_limit=self.trader_stats_positions_limit,
            )

        text = format_alert_text(
            market=title,
            side=side_label,
            size_usd=size_usd,
            price=price,
            timestamp_utc=time_s,
            whale_threshold_usd=self.whale_threshold_for_category(product_category),
            category=product_category,
            trader_stats_block=trader_stats_block,
        )
        return signal_id, text, self.build_invite_link(inviter_telegram_user_id)

    def build_invite_link(self, inviter_user_id: int) -> str:
        return f"https://t.me/{self.bot_username}?start=invite_{inviter_user_id}"

    def build_share_text(self, inviter_user_id: int) -> str:
        return share_text(self.bot_username, inviter_user_id)

    def is_signal_delivered(self, signal_id: str, user_id: int) -> bool:
        return self.signal_repo.is_delivered(signal_id, user_id)

    def mark_signal_delivered(self, signal_id: str, user_id: int) -> bool:
        delivered = self.signal_repo.mark_delivered(signal_id, user_id)
        if delivered:
            self.user_repo.increment_signals(user_id)
        return delivered
