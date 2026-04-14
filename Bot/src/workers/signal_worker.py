from __future__ import annotations

import asyncio
import logging
from itertools import cycle

from aiogram import Bot

from src.handlers.common import AppContext

logger = logging.getLogger(__name__)


class SignalWorker:
    def __init__(self, bot: Bot, context: AppContext, poll_interval_sec: int) -> None:
        self.bot = bot
        self.context = context
        self.poll_interval_sec = poll_interval_sec
        self._categories = cycle(["Politics", "Crypto", "Sports"])

    async def run(self) -> None:
        while True:
            await self._tick()
            await asyncio.sleep(self.poll_interval_sec)

    async def _tick(self) -> None:
        next_category = next(self._categories)
        for user in self.context.user_service.user_repo.all_users():
            if not user.is_live_enabled:
                continue
            if user.categories and next_category not in user.categories:
                continue

            signal_id, text, share_url = self.context.signal_service.build_live_signal_for_user(
                user,
                next_category,
            )
            if not self.context.signal_service.mark_signal_delivered(signal_id, user.telegram_user_id):
                continue

            try:
                from src.services.keyboards import signal_keyboard

                await self.bot.send_message(
                    chat_id=user.telegram_user_id,
                    text=text,
                    reply_markup=signal_keyboard(share_url),
                )
            except Exception:  # noqa: BLE001
                logger.exception("Failed to deliver live signal", extra={"user_id": user.telegram_user_id})
