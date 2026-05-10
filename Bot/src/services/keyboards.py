from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def _main_menu_button() -> InlineKeyboardButton:
    return InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")


def start_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🚀 Активировать", callback_data="activate")],
        ]
    )


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
            [InlineKeyboardButton(text="⚙️ Изменить категории", callback_data="activate")],
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


def settings_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⚙️ Изменить категории", callback_data="activate")],
            [InlineKeyboardButton(text="🔕 Выключить сигналы", callback_data="disable_live")],
            [_main_menu_button()],
        ]
    )
