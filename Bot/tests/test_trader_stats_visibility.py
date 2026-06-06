import asyncio
from unittest.mock import AsyncMock, MagicMock

from src.services.trader_stats_visibility import (
    is_trader_stats_recipient_by_id,
    parse_trader_stats_visible_to,
    user_can_see_trader_stats,
)


def test_parse_trader_stats_visible_to() -> None:
    assert parse_trader_stats_visible_to("@VladislavMusikhin, 12345") == frozenset(
        {"vladislavmusikhin", "12345"}
    )


def test_is_trader_stats_recipient_by_id() -> None:
    visible = frozenset({"12345", "alice"})
    assert is_trader_stats_recipient_by_id(12345, visible) is True
    assert is_trader_stats_recipient_by_id(99, visible) is False


def test_user_can_see_trader_stats_by_username() -> None:
    bot = MagicMock()
    bot.get_chat = AsyncMock(return_value=MagicMock(username="VladislavMusikhin"))
    visible = frozenset({"vladislavmusikhin"})
    assert asyncio.run(user_can_see_trader_stats(bot, 1, visible)) is True


def test_user_can_see_trader_stats_denied() -> None:
    bot = MagicMock()
    bot.get_chat = AsyncMock(return_value=MagicMock(username="someone_else"))
    visible = frozenset({"vladislavmusikhin"})
    assert asyncio.run(user_can_see_trader_stats(bot, 1, visible)) is False


def test_user_can_see_trader_stats_empty_allowlist() -> None:
    bot = MagicMock()
    assert asyncio.run(user_can_see_trader_stats(bot, 1, frozenset())) is False
