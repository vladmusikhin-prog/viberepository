from __future__ import annotations

import asyncio
import time
from typing import Optional
from unittest.mock import AsyncMock
from src.config import Settings
from src.middleware.interaction_update_parser import parse_update_interaction
from src.repositories.in_memory import UserRepository
from src.services.interaction_log_service import (
    InteractionLogService,
    InteractionSession,
    SessionAction,
    UserSnapshot,
    format_session_report,
)


def _settings(
    *,
    analytics_enabled: bool = True,
    analytics_chat_id: Optional[int] = -1001234567890,
    timeout_sec: int = 180,
) -> Settings:
    return Settings(
        bot_token="token",
        bot_username="test_bot",
        whale_threshold_usd=100_000,
        whale_threshold_crypto_usd=20_000,
        whale_threshold_economics_usd=75_000,
        signal_poll_interval_sec=30,
        alert_max_price=0.95,
        alert_max_price_crypto=0.999,
        log_level="INFO",
        signal_source="polymarket",
        polymarket_data_api_base="https://data-api.polymarket.com",
        polymarket_trades_limit=100,
        polymarket_max_trade_age_sec=600,
        polymarket_backfill_enabled=False,
        polymarket_backfill_age_sec=86400,
        polymarket_backfill_limit=200,
        polymarket_backfill_max_pages=8,
        polymarket_resolution_enabled=True,
        polymarket_resolution_poll_interval_sec=120,
        polymarket_resolution_batch_size=25,
        polymarket_gamma_api_base="https://gamma-api.polymarket.com",
        trader_stats_enabled=True,
        trader_stats_positions_limit=100,
        trader_stats_cache_ttl_sec=3600,
        admin_user_ids=(),
        persistence_mode="memory",
        sqlite_db_path=":memory:",
        analytics_enabled=analytics_enabled,
        analytics_chat_id=analytics_chat_id,
        analytics_session_timeout_sec=timeout_sec,
    )


def test_format_session_report_contains_timeline_and_outcome() -> None:
    now = time.time()
    session = InteractionSession(
        user=UserSnapshot(
            telegram_user_id=62036930,
            first_name="Vladislav",
            username="vlad",
            language_code="ru",
        ),
        started_at=now - 126,
        last_at=now,
        actions=[
            SessionAction("cmd_start", now - 126, user_text="/start"),
            SessionAction("category_selected", now - 60, detail="Crypto"),
            SessionAction(
                "alert_whale_delivered",
                now - 30,
                detail="Crypto, $215,000, Bitcoin",
            ),
        ],
    )
    report = format_session_report(
        session,
        categories=["Crypto"],
        is_live_enabled=True,
    )
    assert "Whale Signals Bot Logs" in report
    assert "62036930" in report
    assert "cmd_start" in report
    assert "category_selected (Crypto)" in report
    assert "alert_whale_delivered" in report
    assert '"/start"' in report
    assert "live enabled" in report
    assert "whale alerts: 1" in report


def test_parse_start_invite_deep_link() -> None:
    from aiogram.types import Chat, Message, Update, User

    update = Update(
        update_id=1,
        message=Message(
            message_id=1,
            date=1,
            chat=Chat(id=1, type="private"),
            from_user=User(id=1, is_bot=False, first_name="Test"),
            text="/start invite_62036930",
        ),
    )
    parsed = parse_update_interaction(update)
    assert parsed is not None
    user_id, action, detail, user_text, _snapshot = parsed
    assert user_id == 1
    assert action == "cmd_start"
    assert user_text == "/start invite_62036930"
    assert detail is not None
    assert "invite_from=62036930" in detail


def test_flush_expired_session_posts_to_group() -> None:
    async def _run() -> None:
        bot = AsyncMock()
        user_repo = UserRepository()
        user_repo.get_or_create(42)
        user_repo.update_categories(42, ["Crypto"])
        user_repo.set_live_enabled(42, True)

        service = InteractionLogService(
            bot=bot,
            settings=_settings(timeout_sec=60),
            user_repo=user_repo,
        )
        snapshot = UserSnapshot(telegram_user_id=42, first_name="Alice", username="alice")
        past = time.time() - 120
        service._sessions[42] = InteractionSession(
            user=snapshot,
            started_at=past,
            last_at=past,
            actions=[SessionAction("cmd_start", past, user_text="/start")],
        )

        await service.flush_expired_sessions()

        bot.send_message.assert_awaited_once()
        assert bot.send_message.await_args.kwargs["chat_id"] == -1001234567890
        assert "Alice" in bot.send_message.await_args.kwargs["text"]
        assert 42 not in service._sessions

    asyncio.run(_run())


def test_no_op_when_analytics_chat_id_missing() -> None:
    async def _run() -> None:
        bot = AsyncMock()
        service = InteractionLogService(
            bot=bot,
            settings=_settings(analytics_chat_id=None),
            user_repo=UserRepository(),
        )
        assert service.is_active is False
        await service.record_action(1, "cmd_start")
        bot.send_message.assert_not_awaited()

    asyncio.run(_run())
