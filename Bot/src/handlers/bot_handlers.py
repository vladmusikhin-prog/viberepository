from __future__ import annotations

import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from src.handlers.common import AppContext
from src.services.keyboards import (
    activation_success_keyboard,
    categories_keyboard,
    settings_keyboard,
    start_keyboard,
)
from src.services.texts import (
    CATEGORY_PROMPT_TEXT,
    START_TEXT,
    format_activation_example_text,
)

router = Router()
logger = logging.getLogger(__name__)


def register_handlers(context: AppContext) -> Router:
    @router.message(Command("start"))
    async def cmd_start(message: Message) -> None:
        if not message.from_user:
            return
        context.user_service.ensure_user(message.from_user.id)
        await message.answer(START_TEXT, reply_markup=start_keyboard())

    @router.message(Command("help"))
    async def cmd_help(message: Message) -> None:
        await message.answer("ℹ️ Используй /start для запуска и /settings для настройки сигналов.")

    @router.message(Command("share"))
    async def cmd_share(message: Message) -> None:
        if not message.from_user:
            return
        user_id = message.from_user.id
        invite_url = context.signal_service.build_invite_link(user_id)
        share_msg = context.signal_service.build_share_text(user_id)
        await message.answer(
            "📨 Поделись с другом:\n\n"
            f"{share_msg}\n\n"
            f"🔗 Ссылка: {invite_url}"
        )

    @router.message(Command("settings"))
    async def cmd_settings(message: Message) -> None:
        if not message.from_user:
            return
        text = context.settings_service.render_settings(message.from_user.id)
        await message.answer(text, reply_markup=settings_keyboard())

    @router.message(Command("admin_stats"))
    async def cmd_admin_stats(message: Message) -> None:
        if not message.from_user:
            return
        user_id = message.from_user.id
        logger.info("Admin stats requested by user_id=%s", user_id)
        if not context.admin_service.is_admin(user_id):
            await message.answer("⛔ Команда недоступна.")
            return
        await message.answer(context.admin_service.render_stats())

    @router.callback_query(F.data == "activate")
    async def cb_activate(callback: CallbackQuery) -> None:
        await callback.answer()
        await callback.message.answer(CATEGORY_PROMPT_TEXT, reply_markup=categories_keyboard())

    @router.callback_query(F.data.in_(("go_live", "test_signal", "open_test_signal", "how_it_works")))
    async def cb_legacy_removed_buttons(callback: CallbackQuery) -> None:
        """Старые inline-кнопки из прошлых версий бота."""
        await callback.answer("Онбординг обновлён: /start → Активировать.", show_alert=False)

    @router.callback_query(F.data.startswith("category:"))
    async def cb_category(callback: CallbackQuery) -> None:
        if not callback.from_user:
            return
        await callback.answer()
        category = callback.data.split(":", maxsplit=1)[1]
        context.user_service.activate_categories(callback.from_user.id, category)
        activation_text = format_activation_example_text(
            category=category,
            whale_threshold_usd=context.signal_service.whale_threshold_usd,
        )
        await callback.message.answer(
            activation_text,
            reply_markup=activation_success_keyboard(),
        )

    @router.callback_query(F.data == "share_friend")
    async def cb_share_friend(callback: CallbackQuery) -> None:
        if not callback.from_user:
            return
        logger.info("Share callback by user_id=%s", callback.from_user.id)
        await callback.answer()
        user_id = callback.from_user.id
        invite_url = context.signal_service.build_invite_link(user_id)
        share_msg = context.signal_service.build_share_text(user_id)
        await callback.message.answer(
            "📨 Скопируй и отправь другу:\n\n"
            f"{share_msg}\n\n"
            f"🔗 Ссылка: {invite_url}"
        )

    @router.callback_query(F.data == "disable_live")
    async def cb_disable_live(callback: CallbackQuery) -> None:
        if not callback.from_user:
            return
        await callback.answer()
        context.user_service.disable_live(callback.from_user.id)
        text = context.settings_service.render_settings(callback.from_user.id)
        await callback.message.answer(text, reply_markup=settings_keyboard())

    @router.callback_query(F.data == "main_menu")
    async def cb_main_menu(callback: CallbackQuery) -> None:
        if not callback.from_user:
            return
        await callback.answer()
        context.user_service.ensure_user(callback.from_user.id)
        await callback.message.answer(START_TEXT, reply_markup=start_keyboard())

    return router
