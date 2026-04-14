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
from src.workers.signal_worker import SignalWorker


async def main() -> None:
    settings = load_settings()
    configure_logging(settings.log_level)
    logger = logging.getLogger(__name__)

    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()

    context = build_context(
        whale_threshold_usd=settings.whale_threshold_usd,
        bot_username=settings.bot_username,
    )
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
        if use_polymarket:
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
        else:
            worker = SignalWorker(
                bot=bot,
                context=context,
                settings=settings,
                http_session=None,
            )
            worker_task = asyncio.create_task(worker.run())
            try:
                await dp.start_polling(bot)
            finally:
                worker_task.cancel()
                with suppress(asyncio.CancelledError):
                    await worker_task

    logger.info(
        "Bot started in polling mode (signal_source=%s)",
        settings.signal_source,
    )
    await _run_bot()


if __name__ == "__main__":
    asyncio.run(main())
