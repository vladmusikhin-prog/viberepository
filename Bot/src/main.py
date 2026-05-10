import asyncio
from contextlib import suppress
import logging

import aiohttp
from aiogram import Bot, Dispatcher
from aiogram.types import ErrorEvent

from src.config import load_settings
from src.handlers.bot_handlers import register_handlers
from src.handlers.common import build_context
from src.logging_setup import configure_logging
from src.services.keyboards import start_keyboard
from src.workers.signal_worker import SignalWorker


async def main() -> None:
    settings = load_settings()
    configure_logging(settings.log_level)
    logger = logging.getLogger(__name__)

    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()

    context = build_context(settings=settings)
    dp.include_router(register_handlers(context))

    @dp.errors()
    async def log_errors(event: ErrorEvent) -> None:
        logger.exception(
            "Unhandled update error",
            exc_info=event.exception,
            extra={"update_id": event.update.update_id if event.update else None},
        )

    use_polymarket = settings.signal_source == "polymarket"

    async def _run_bot() -> None:
        if not use_polymarket:
            logger.info("signal_source=%s: background trade worker disabled", settings.signal_source)
            await dp.start_polling(bot)
            return

        async with aiohttp.ClientSession() as http_session:
            worker = SignalWorker(
                bot=bot,
                context=context,
                settings=settings,
                http_session=http_session,
            )
            worker_task = asyncio.create_task(worker.run())
            try:
                await dp.start_polling(bot)
            finally:
                worker_task.cancel()
                with suppress(asyncio.CancelledError):
                    await worker_task

    _start_cta_count = sum(len(row) for row in start_keyboard().inline_keyboard)
    if _start_cta_count != 1:
        logger.error(
            "start_keyboard has %s buttons in /start rows; expected exactly 1 CTA (Активировать). "
            "Check you are running THIS repo from Bot/ after git pull.",
            _start_cta_count,
        )
    else:
        logger.info(
            "start_keyboard OK: single /start CTA (no second info button). "
            "If Telegram still shows two buttons, another process with the same BOT_TOKEN is likely still running.",
        )

    logger.info(
        "Bot started in polling mode (signal_source=%s)",
        settings.signal_source,
    )
    await _run_bot()


if __name__ == "__main__":
    asyncio.run(main())
