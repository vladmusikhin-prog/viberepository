import asyncio
from contextlib import suppress
import logging

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

    worker = SignalWorker(
        bot=bot,
        context=context,
        poll_interval_sec=settings.signal_poll_interval_sec,
        demo_live_min_interval_sec=settings.demo_live_min_interval_sec,
    )
    worker_task = asyncio.create_task(worker.run())

    logger.info("Bot started in polling mode")
    try:
        await dp.start_polling(bot)
    finally:
        worker_task.cancel()
        with suppress(asyncio.CancelledError):
            await worker_task


if __name__ == "__main__":
    asyncio.run(main())
