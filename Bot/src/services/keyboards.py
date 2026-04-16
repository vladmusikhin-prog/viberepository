from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def start_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Активировать", callback_data="activate"),
                InlineKeyboardButton(text="Как это работает", callback_data="how_it_works"),
            ]
        ]
    )


def categories_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Politics", callback_data="category:Politics"),
                InlineKeyboardButton(text="Crypto", callback_data="category:Crypto"),
            ],
            [
                InlineKeyboardButton(text="Sports", callback_data="category:Sports"),
                InlineKeyboardButton(text="All", callback_data="category:All"),
            ],
        ]
    )


def activation_success_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Получить тестовый сигнал", callback_data="test_signal")],
            [InlineKeyboardButton(text="Изменить категории", callback_data="activate")],
        ]
    )


def preview_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Открыть тестовый сигнал", callback_data="open_test_signal")],
            [InlineKeyboardButton(text="Получить live-сигналы", callback_data="go_live")],
        ]
    )


def signal_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Полезно", callback_data="feedback:helpful"),
                InlineKeyboardButton(text="Не полезно", callback_data="feedback:not_helpful"),
            ],
            [InlineKeyboardButton(text="Поделиться с другом", callback_data="share_friend")],
        ]
    )


def settings_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Изменить категории", callback_data="activate")],
            [InlineKeyboardButton(text="Выключить сигналы", callback_data="disable_live")],
        ]
    )
