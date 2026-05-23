from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def _main_menu_button() -> InlineKeyboardButton:
    return InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")


def start_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🚀 Активировать", callback_data="activate")],
        ]
    )


def main_menu_active_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⚙️ Изменить категорию", callback_data="activate")],
            [InlineKeyboardButton(text="🔕 Деактивировать уведомления", callback_data="disable_live")],
        ]
    )


def main_menu_keyboard(is_live_enabled: bool) -> InlineKeyboardMarkup:
    if is_live_enabled:
        return main_menu_active_keyboard()
    return start_keyboard()


def categories_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🏛 Politics", callback_data="category:Politics"),
                InlineKeyboardButton(text="₿ Crypto", callback_data="category:Crypto"),
            ],
            [
                InlineKeyboardButton(text="🏅 Sports", callback_data="category:Sports"),
                InlineKeyboardButton(text="🌐 All", callback_data="category:All"),
            ],
            [_main_menu_button()],
        ]
    )


def activation_success_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⚙️ Изменить категорию", callback_data="activate")],
            [_main_menu_button()],
        ]
    )


def signal_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📨 Поделиться с другом", callback_data="share_friend")],
            [_main_menu_button()],
        ]
    )


def settings_keyboard(is_live_enabled: bool) -> InlineKeyboardMarkup:
    rows = []
    if is_live_enabled:
        rows.append(
            [InlineKeyboardButton(text="⚙️ Изменить категорию", callback_data="activate")]
        )
        rows.append(
            [InlineKeyboardButton(text="🔕 Деактивировать уведомления", callback_data="disable_live")]
        )
    else:
        rows.append([InlineKeyboardButton(text="🚀 Активировать", callback_data="activate")])
    rows.append([_main_menu_button()])
    return InlineKeyboardMarkup(inline_keyboard=rows)
