from __future__ import annotations

import logging

from aiogram import F, Router
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import CallbackQuery, Message

from src.handlers.common import AppContext
from src.handlers.start_helpers import is_invite_deep_link
from src.services.category_mapper import ALL_PRODUCT_CATEGORIES
from src.services.category_selection import (
    decode_selection,
    format_selection_label,
    is_product_category,
    toggle_selection,
)
from src.services.keyboards import (
    activation_success_keyboard,
    categories_keyboard,
    main_menu_keyboard,
    settings_keyboard,
    start_keyboard,
)
from src.services.texts import (
    INVITE_ALREADY_ACTIVE_TEXT,
    NOTIFICATIONS_DISABLED_TEXT,
    START_TEXT,
    format_activation_example_text_for_categories,
    format_category_selection_text,
)

router = Router()
logger = logging.getLogger(__name__)


def register_handlers(context: AppContext) -> Router:
    @router.message(CommandStart())
    async def cmd_start(message: Message, command: CommandObject) -> None:
        if not message.from_user:
            return
        user = context.user_service.ensure_user(message.from_user.id)
        if is_invite_deep_link(command.args) and user.is_live_enabled:
            await message.answer(
                INVITE_ALREADY_ACTIVE_TEXT,
                reply_markup=settings_keyboard(user.is_live_enabled),
            )
            return
        if user.is_live_enabled:
            await message.answer(
                context.settings_service.render_main_menu(message.from_user.id),
                reply_markup=main_menu_keyboard(True),
            )
            return
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
        user = context.user_service.ensure_user(message.from_user.id)
        text = context.settings_service.render_settings(message.from_user.id)
        await message.answer(text, reply_markup=settings_keyboard(user.is_live_enabled))

    @router.message(Command("chatid"))
    async def cmd_chatid(message: Message) -> None:
        chat = message.chat
        title = chat.title or "—"
        await message.answer(
            f"🆔 Chat ID: `{chat.id}`\n"
            f"📂 Type: {chat.type}\n"
            f"📝 Title: {title}"
        )

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

    def _initial_category_selection(user_id: int) -> set[str]:
        user = context.user_service.ensure_user(user_id)
        return set(user.categories)

    async def _show_category_picker(callback: CallbackQuery, selected: set[str]) -> None:
        if not callback.message:
            return
        text = format_category_selection_text(format_selection_label(selected))
        markup = categories_keyboard(selected)
        await callback.message.edit_text(text, reply_markup=markup)

    @router.callback_query(F.data == "activate")
    async def cb_activate(callback: CallbackQuery) -> None:
        if not callback.from_user:
            return
        await callback.answer()
        selected = _initial_category_selection(callback.from_user.id)
        text = format_category_selection_text(format_selection_label(selected))
        await callback.message.answer(text, reply_markup=categories_keyboard(selected))

    @router.callback_query(F.data.in_(("go_live", "test_signal", "open_test_signal", "how_it_works")))
    async def cb_legacy_removed_buttons(callback: CallbackQuery) -> None:
        """Старые inline-кнопки из прошлых версий бота."""
        await callback.answer("Онбординг обновлён: /start → Активировать.", show_alert=False)

    @router.callback_query(F.data.startswith("cat_toggle:"))
    async def cb_cat_toggle(callback: CallbackQuery) -> None:
        if not callback.from_user or not callback.data:
            return
        parts = callback.data.split(":", maxsplit=2)
        if len(parts) != 3:
            await callback.answer()
            return
        _, category, encoded = parts
        if not is_product_category(category):
            await callback.answer()
            return
        selected = toggle_selection(decode_selection(encoded), category)
        await callback.answer()
        await _show_category_picker(callback, selected)

    @router.callback_query(F.data.startswith("cat_confirm:"))
    async def cb_cat_confirm(callback: CallbackQuery) -> None:
        if not callback.from_user or not callback.data:
            return
        encoded = callback.data.split(":", maxsplit=1)[1]
        selected_set = decode_selection(encoded)
        if not selected_set:
            await callback.answer(
                "Выбери хотя бы одну категорию.",
                show_alert=True,
            )
            return
        await callback.answer()
        user = context.user_service.set_categories(
            callback.from_user.id,
            list(selected_set),
        )
        activation_text = format_activation_example_text_for_categories(
            categories=list(user.categories),
            whale_threshold_for_category=context.signal_service.whale_threshold_for_category,
        )
        await callback.message.answer(
            activation_text,
            reply_markup=activation_success_keyboard(),
        )

    @router.callback_query(F.data.startswith("category:"))
    async def cb_category_legacy(callback: CallbackQuery) -> None:
        """Старые сообщения с одним тапом по категории — открываем новый выбор."""
        if not callback.from_user:
            return
        await callback.answer()
        category = callback.data.split(":", maxsplit=1)[1]
        if category == "All":
            selected = set(context.user_service.ensure_user(callback.from_user.id).categories)
            if not selected:
                selected = set(ALL_PRODUCT_CATEGORIES)
        elif is_product_category(category):
            selected = {category}
        else:
            selected = set()
        text = format_category_selection_text(format_selection_label(selected))
        await callback.message.answer(text, reply_markup=categories_keyboard(selected))

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
        await callback.message.answer(
            NOTIFICATIONS_DISABLED_TEXT,
            reply_markup=start_keyboard(),
        )

    @router.callback_query(F.data == "main_menu")
    async def cb_main_menu(callback: CallbackQuery) -> None:
        if not callback.from_user:
            return
        await callback.answer()
        user = context.user_service.ensure_user(callback.from_user.id)
        text = context.settings_service.render_main_menu(callback.from_user.id)
        await callback.message.answer(
            text,
            reply_markup=main_menu_keyboard(user.is_live_enabled),
        )

    return router
