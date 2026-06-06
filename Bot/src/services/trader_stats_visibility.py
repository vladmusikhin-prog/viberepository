from __future__ import annotations

import logging
from typing import TYPE_CHECKING, FrozenSet

if TYPE_CHECKING:
    from aiogram import Bot

logger = logging.getLogger(__name__)


def parse_trader_stats_visible_to(raw: str) -> FrozenSet[str]:
    """Usernames (no @, lowercased) and/or numeric telegram user ids as strings."""
    out: set[str] = set()
    for part in (raw or "").split(","):
        cleaned = part.strip().lstrip("@").lower()
        if cleaned:
            out.add(cleaned)
    return frozenset(out)


def is_trader_stats_recipient_by_id(
    telegram_user_id: int,
    visible_to: FrozenSet[str],
) -> bool:
    return str(telegram_user_id) in visible_to


async def user_can_see_trader_stats(
    bot: Bot,
    telegram_user_id: int,
    visible_to: FrozenSet[str],
) -> bool:
    if not visible_to:
        return False
    if is_trader_stats_recipient_by_id(telegram_user_id, visible_to):
        return True
    try:
        chat = await bot.get_chat(telegram_user_id)
    except Exception:
        logger.debug(
            "get_chat failed for trader stats visibility (user_id=%s)",
            telegram_user_id,
            exc_info=True,
        )
        return False
    username = (chat.username or "").strip().lower()
    return username in visible_to
