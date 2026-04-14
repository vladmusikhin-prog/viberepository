from __future__ import annotations

import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from src.handlers.common import AppContext
from src.services.keyboards import (
    activation_success_keyboard,
    categories_keyboard,
    preview_keyboard,
    settings_keyboard,
    signal_keyboard,
    start_keyboard,
)
from src.services.texts import (
    ACTIVATION_SUCCESS_TEXT,
    CATEGORY_PROMPT_TEXT,
    PREVIEW_INTRO_TEXT,
    START_TEXT,
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
        await message.answer("Используй /start для запуска и /settings для настройки сигналов.")

    @router.message(Command("settings"))
    async def cmd_settings(message: Message) -> None:
        if not message.from_user:
            return
        text = context.settings_service.render_settings(message.from_user.id)
        await message.answer(text, reply_markup=settings_keyboard())

    @router.callback_query(F.data == "activate")
    async def cb_activate(callback: CallbackQuery) -> None:
        await callback.answer()
        await callback.message.answer(CATEGORY_PROMPT_TEXT, reply_markup=categories_keyboard())

    @router.callback_query(F.data == "how_it_works")
    async def cb_how_it_works(callback: CallbackQuery) -> None:
        await callback.answer()
        await callback.message.answer(PREVIEW_INTRO_TEXT, reply_markup=preview_keyboard())

    @router.callback_query(F.data.startswith("category:"))
    async def cb_category(callback: CallbackQuery) -> None:
        if not callback.from_user:
            return
        await callback.answer()
        category = callback.data.split(":", maxsplit=1)[1]
        context.user_service.activate_categories(callback.from_user.id, category)
        await callback.message.answer(
            ACTIVATION_SUCCESS_TEXT,
            reply_markup=activation_success_keyboard(),
        )

    @router.callback_query(F.data == "test_signal")
    @router.callback_query(F.data == "open_test_signal")
    async def cb_test_signal(callback: CallbackQuery) -> None:
        if not callback.from_user:
            return
        await callback.answer()
        user = context.user_service.ensure_user(callback.from_user.id)
        category = user.categories[0] if user.categories else "Politics"
        text, share_url = context.signal_service.build_test_signal(callback.from_user.id, category)
        await callback.message.answer(text, reply_markup=signal_keyboard(share_url))

    @router.callback_query(F.data == "go_live")
    async def cb_go_live(callback: CallbackQuery) -> None:
        await callback.answer()
        await callback.message.answer("Live-сигналы включены. Жди реальные алерты по выбранным категориям.")

    @router.callback_query(F.data.startswith("feedback:"))
    async def cb_feedback(callback: CallbackQuery) -> None:
        if not callback.from_user:
            return
        await callback.answer("Спасибо за фидбек")
        reaction = callback.data.split(":", maxsplit=1)[1]
        context.feedback_service.record_feedback(callback.from_user.id, reaction)

    @router.callback_query(F.data == "disable_live")
    async def cb_disable_live(callback: CallbackQuery) -> None:
        if not callback.from_user:
            return
        await callback.answer()
        context.user_service.disable_live(callback.from_user.id)
        text = context.settings_service.render_settings(callback.from_user.id)
        await callback.message.answer(text, reply_markup=settings_keyboard())

    return router
