START_TEXT = """Whale Signals Bot

Лови уведомления о whale-size ставках по выбранным рынкам.
Сигнал приходит в Telegram сразу после крупного размещения.

Готов включить сигналы?"""

CATEGORY_PROMPT_TEXT = "Выбери, что тебе сейчас важнее."

ACTIVATION_SUCCESS_TEXT = """Готово. Подписка на категории включена.
Дальше ты будешь получать уведомления о whale-size ставках по выбранным рынкам."""

PREVIEW_INTRO_TEXT = """Ниже тестовое уведомление в формате, как в live.
Если всё ок — жди реальные сигналы по своим категориям.
Настройки доступны в /settings."""


def format_alert_text(
    market: str,
    side: str,
    size_usd: float,
    price: float,
    timestamp_utc: str,
    whale_threshold_usd: int,
    category: str,
) -> str:
    return f"""Whale Alert: крупное размещение

Рынок: {market}
Платформа: Polymarket
Сторона: {side}
Размер: ${size_usd:,.0f}
Цена: {price:.2f}
Время: {timestamp_utc} UTC

Критерий whale: >= ${whale_threshold_usd / 1000:.0f}k
Категория: {category}"""


def share_text(bot_username: str, inviter_user_id: int) -> str:
    return (
        "Я использую Whale Signals Bot для алертов по крупным ставкам на Polymarket.\n"
        f"Если хочешь, подключайся: https://t.me/{bot_username}?start=invite_{inviter_user_id}"
    )
