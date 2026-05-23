from __future__ import annotations

import asyncio
import logging
from typing import Optional

import aiohttp
from aiogram import Bot

from src.config import Settings
from src.handlers.common import AppContext
from src.integrations.polymarket_gamma_client import fetch_market_by_slug
from src.services.resolution_service import ResolutionService

logger = logging.getLogger(__name__)


class ResolutionWorker:
    def __init__(
        self,
        bot: Bot,
        context: AppContext,
        settings: Settings,
        http_session: Optional[aiohttp.ClientSession],
        resolution_service: ResolutionService,
    ) -> None:
        self.bot = bot
        self.context = context
        self.settings = settings
        self._http = http_session
        self.resolution_service = resolution_service

    async def run(self) -> None:
        while True:
            try:
                await self._tick()
            except asyncio.CancelledError:
                raise
            except Exception:  # noqa: BLE001
                logger.exception("Resolution worker tick failed")
            await asyncio.sleep(self.settings.polymarket_resolution_poll_interval_sec)

    async def _tick(self) -> None:
        if self._http is None:
            return

        pending = self.resolution_service.pending_repo.list_unresolved(
            limit=self.settings.polymarket_resolution_batch_size,
        )
        if not pending:
            return

        for tracked in pending:
            market = await fetch_market_by_slug(
                self._http,
                base_url=self.settings.polymarket_gamma_api_base,
                slug=tracked.slug,
            )
            if not market:
                continue

            resolution = self.resolution_service.parse_market_resolution(market)
            if resolution is None:
                continue

            signal_id, text = self.resolution_service.build_resolution_alert(
                tracked,
                resolution,
            )
            await self._deliver_resolution(
                signal_id=signal_id,
                text=text,
                category=tracked.category,
            )
            self.resolution_service.pending_repo.mark_resolved(tracked.condition_id)
            logger.info(
                "Resolution alert processed condition_id=%s market=%s",
                tracked.condition_id[:12],
                tracked.title[:48],
            )

    async def _deliver_resolution(
        self,
        *,
        signal_id: str,
        text: str,
        category: str,
    ) -> None:
        eligible = [
            u
            for u in self.context.user_service.user_repo.all_users()
            if u.is_live_enabled and (not u.categories or category in u.categories)
        ]
        if not eligible:
            return

        from src.services.keyboards import signal_keyboard

        for user in eligible:
            if self.context.signal_service.is_signal_delivered(signal_id, user.telegram_user_id):
                continue
            try:
                await self.bot.send_message(
                    chat_id=user.telegram_user_id,
                    text=text,
                    reply_markup=signal_keyboard(),
                )
                self.context.signal_service.mark_signal_delivered(
                    signal_id,
                    user.telegram_user_id,
                )
            except Exception:  # noqa: BLE001
                logger.exception(
                    "Failed to deliver resolution alert",
                    extra={"user_id": user.telegram_user_id, "signal_id": signal_id[:24]},
                )
