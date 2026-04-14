from __future__ import annotations

import asyncio
import logging
import time
from typing import Optional

import aiohttp
from aiogram import Bot

from src.config import Settings
from src.handlers.common import AppContext
from src.integrations.polymarket_client import fetch_large_cash_trades
from src.repositories.seen_trades import SeenTradeStore
from src.services.category_mapper import classify_polymarket_trade

logger = logging.getLogger(__name__)


class SignalWorker:
    def __init__(
        self,
        bot: Bot,
        context: AppContext,
        settings: Settings,
        http_session: Optional[aiohttp.ClientSession],
    ) -> None:
        self.bot = bot
        self.context = context
        self.settings = settings
        self._http = http_session
        self._seen_trades = SeenTradeStore(settings.seen_trade_ids_max)

    async def run(self) -> None:
        while True:
            try:
                await self._tick_polymarket()
            except asyncio.CancelledError:
                raise
            except Exception:  # noqa: BLE001
                logger.exception("Signal worker tick failed")
            await asyncio.sleep(self.settings.signal_poll_interval_sec)

    async def _tick_polymarket(self) -> None:
        if self._http is None:
            logger.error("Polymarket mode requires aiohttp session")
            return

        trades = await fetch_large_cash_trades(
            self._http,
            base_url=self.settings.polymarket_data_api_base,
            min_cash_usd=float(self.settings.whale_threshold_usd),
            limit=self.settings.polymarket_trades_limit,
        )
        if not trades:
            return

        wall = int(time.time())
        max_age = self.settings.polymarket_max_trade_age_sec

        for trade in trades:
            tx = str(trade.get("transactionHash") or "")
            if not tx:
                continue
            ts_raw = trade.get("timestamp")
            try:
                ts = int(ts_raw) if ts_raw is not None else 0
            except (TypeError, ValueError):
                ts = 0
            if ts and wall - ts > max_age:
                continue

            category = classify_polymarket_trade(trade)

            eligible = [
                u
                for u in self.context.user_service.user_repo.all_users()
                if u.is_live_enabled
                and (not u.categories or category in u.categories)
            ]
            if not eligible:
                continue

            if not self._seen_trades.try_consume(tx):
                continue

            for user in eligible:
                signal_id, text, share_url = self.context.signal_service.build_polymarket_trade_alert(
                    trade,
                    category,
                    user.telegram_user_id,
                )
                try:
                    from src.services.keyboards import signal_keyboard

                    await self.bot.send_message(
                        chat_id=user.telegram_user_id,
                        text=text,
                        reply_markup=signal_keyboard(share_url),
                    )
                    self.context.signal_service.mark_signal_delivered(
                        signal_id,
                        user.telegram_user_id,
                    )
                except Exception:  # noqa: BLE001
                    logger.exception(
                        "Failed to deliver Polymarket signal",
                        extra={"user_id": user.telegram_user_id, "tx": tx[:18]},
                    )
