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

    async def run(self) -> None:
        if self.settings.polymarket_backfill_enabled:
            await self._backfill_polymarket_once()

        while True:
            try:
                await self._tick_polymarket()
            except asyncio.CancelledError:
                raise
            except Exception:  # noqa: BLE001
                logger.exception("Signal worker tick failed")
            await asyncio.sleep(self.settings.signal_poll_interval_sec)

    def _trade_timestamp_utc(self, trade: dict) -> int:
        ts_raw = trade.get("timestamp")
        try:
            ts = int(ts_raw) if ts_raw is not None else 0
        except (TypeError, ValueError):
            ts = 0
        return ts

    def _page_min_timestamp(self, trades: list[dict]) -> int:
        min_ts = None
        for t in trades:
            ts = self._trade_timestamp_utc(t)
            if not ts:
                continue
            min_ts = ts if min_ts is None else min(min_ts, ts)
        return int(min_ts or 0)

    async def _backfill_polymarket_once(self) -> None:
        if self._http is None:
            return

        cut_ts = int(time.time()) - self.settings.polymarket_backfill_age_sec
        limit = self.settings.polymarket_backfill_limit
        max_pages = max(1, self.settings.polymarket_backfill_max_pages)

        offset = 0
        logger.info(
            "Backfill started: age_sec=%s limit=%s max_pages=%s",
            self.settings.polymarket_backfill_age_sec,
            limit,
            max_pages,
        )

        for page in range(max_pages):
            trades = await fetch_large_cash_trades(
                self._http,
                base_url=self.settings.polymarket_data_api_base,
                min_cash_usd=float(self.settings.whale_threshold_usd),
                limit=limit,
                offset=offset,
            )
            if not trades:
                break

            min_ts = self._page_min_timestamp(trades)

            for trade in trades:
                tx = str(trade.get("transactionHash") or "")
                if not tx:
                    continue

                ts = self._trade_timestamp_utc(trade)
                if not ts or ts < cut_ts:
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

                for user in eligible:
                    signal_id, text, share_url = self.context.signal_service.build_polymarket_trade_alert(
                        trade,
                        category,
                        user.telegram_user_id,
                    )
                    if self.context.signal_service.is_signal_delivered(
                        signal_id,
                        user.telegram_user_id,
                    ):
                        continue

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
                            "Failed to deliver Polymarket backfill signal",
                            extra={"user_id": user.telegram_user_id, "tx": tx[:18]},
                        )

            # If the oldest trade on this page is already older than cutoff,
            # next pages will only be older (API expected sorted by recency).
            if min_ts and min_ts < cut_ts:
                break

            offset += limit

        logger.info("Backfill finished")

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

            for user in eligible:
                signal_id, text, share_url = self.context.signal_service.build_polymarket_trade_alert(
                    trade,
                    category,
                    user.telegram_user_id,
                )
                if self.context.signal_service.is_signal_delivered(
                    signal_id,
                    user.telegram_user_id,
                ):
                    continue
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
