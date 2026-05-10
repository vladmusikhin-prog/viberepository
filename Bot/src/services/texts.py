START_TEXT = """🐋 Whale Signals Bot

Лови уведомления о whale-size ставках по выбранным рынкам.
⚡ Сигнал приходит в Telegram сразу после крупного размещения.

Готов включить сигналы?"""

CATEGORY_PROMPT_TEXT = "🎯 Выбери, что тебе сейчас важнее."

ACTIVATION_SUCCESS_TEXT = """✅ Готово. Подписка на категории включена.
🔔 Как только по Polymarket пройдёт крупное размещение в твоих категориях, пришлём алерт сюда.
⚙️ Пороги и категории — в /settings."""

HOW_IT_WORKS_TEXT = """ℹ️ Как это работает

Бот мониторит Polymarket и шлёт одно короткое сообщение при whale-size сделке в выбранных категориях.

Нажми «Активировать», выбери Politics / Crypto / Sports или All — после этого можно только ждать живые сигналы (без автокопирования сделок).

⚙️ Настройки: /settings"""


def format_alert_text(
    market: str,
    side: str,
    size_usd: float,
    price: float,
    timestamp_utc: str,
    whale_threshold_usd: int,
    category: str,
) -> str:
    return f"""🐋 Whale Alert: крупное размещение

🎯 Рынок: {market}
🧭 Платформа: Polymarket
📈 Сторона: {side}
💵 Размер: ${size_usd:,.0f}
💲 Цена: {price:.2f}
🕒 Время: {timestamp_utc} UTC

📏 Критерий whale: >= ${whale_threshold_usd / 1000:.0f}k
🏷 Категория: {category}"""


def share_text(bot_username: str, inviter_user_id: int) -> str:
    return (
        "🐋 Я использую Whale Signals Bot для алертов по крупным ставкам на Polymarket.\n"
        f"Если хочешь, подключайся: https://t.me/{bot_username}?start=invite_{inviter_user_id}"
    )
