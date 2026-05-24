from __future__ import annotations

import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update

from src.middleware.interaction_update_parser import parse_update_interaction
from src.services.interaction_log_service import InteractionLogService

logger = logging.getLogger(__name__)


class InteractionLoggingMiddleware(BaseMiddleware):
    def __init__(self, interaction_log_service: InteractionLogService) -> None:
        self._log_service = interaction_log_service

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if isinstance(event, Update) and self._log_service.is_active:
            parsed = parse_update_interaction(event)
            if parsed is not None:
                user_id, action, detail, user_text, snapshot = parsed
                try:
                    await self._log_service.record_action(
                        user_id,
                        action,
                        detail=detail,
                        user_text=user_text,
                        user_snapshot=snapshot,
                    )
                except Exception:  # noqa: BLE001
                    logger.warning(
                        "Interaction log record failed user_id=%s action=%s",
                        user_id,
                        action,
                        exc_info=True,
                    )

        return await handler(event, data)
