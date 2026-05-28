from __future__ import annotations

from typing import Optional, Tuple

from aiogram.types import CallbackQuery, Message, Update, User

from src.handlers.start_helpers import parse_invite_inviter_id
from src.services.interaction_log_service import UserSnapshot

ParsedInteraction = Tuple[int, str, Optional[str], Optional[str], UserSnapshot]


def user_snapshot_from_tg(user: User) -> UserSnapshot:
    return UserSnapshot(
        telegram_user_id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        username=user.username,
        language_code=user.language_code,
    )


def parse_update_interaction(update: Update) -> Optional[ParsedInteraction]:
    if update.message and update.message.chat.type == "private":
        return _parse_message(update.message)
    if update.callback_query and update.callback_query.message:
        chat = update.callback_query.message.chat
        if chat and chat.type == "private":
            return _parse_callback(update.callback_query)
    return None


def _parse_message(message: Message) -> Optional[ParsedInteraction]:
    if not message.from_user:
        return None

    user = user_snapshot_from_tg(message.from_user)
    text = (message.text or "").strip()

    if text.startswith("/start"):
        parts = text.split(maxsplit=1)
        args = parts[1] if len(parts) > 1 else None
        detail_parts = []
        inviter = parse_invite_inviter_id(args)
        if args:
            detail_parts.append(f"args={args}")
        if inviter is not None:
            detail_parts.append(f"invite_from={inviter}")
        detail = ", ".join(detail_parts) if detail_parts else None
        return user.telegram_user_id, "cmd_start", detail, text, user

    if text.startswith("/help"):
        return user.telegram_user_id, "cmd_help", None, text, user
    if text.startswith("/share"):
        return user.telegram_user_id, "cmd_share", None, text, user
    if text.startswith("/settings"):
        return user.telegram_user_id, "cmd_settings", None, text, user
    if text.startswith("/admin_stats"):
        return user.telegram_user_id, "cmd_admin_stats", None, text, user

    if text:
        preview = text[:120] + ("…" if len(text) > 120 else "")
        return user.telegram_user_id, "free_text", preview, text[:120], user

    return None


def _parse_callback(callback: CallbackQuery) -> Optional[ParsedInteraction]:
    if not callback.from_user:
        return None

    user = user_snapshot_from_tg(callback.from_user)
    data = callback.data or ""

    if data == "activate":
        return user.telegram_user_id, "onboarding_activate", None, None, user
    if data.startswith("cat_toggle:"):
        parts = data.split(":", maxsplit=2)
        detail = parts[1] if len(parts) > 1 else None
        return user.telegram_user_id, "category_toggle", detail, None, user
    if data.startswith("cat_confirm:"):
        encoded = data.split(":", maxsplit=1)[1] if ":" in data else ""
        return user.telegram_user_id, "categories_confirmed", encoded or None, None, user
    if data.startswith("category:"):
        category = data.split(":", maxsplit=1)[1]
        return user.telegram_user_id, "category_selected_legacy", category, None, user
    if data == "share_friend":
        return user.telegram_user_id, "share_friend", None, None, user
    if data == "disable_live":
        return user.telegram_user_id, "notifications_disabled", None, None, user
    if data == "main_menu":
        return user.telegram_user_id, "main_menu_open", None, None, user
    if data in ("go_live", "test_signal", "open_test_signal", "how_it_works"):
        return user.telegram_user_id, "legacy_callback", data, None, user

    return user.telegram_user_id, "unknown_callback", data, None, user
