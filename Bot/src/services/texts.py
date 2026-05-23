from __future__ import annotations

START_TEXT = """🐋 Whale Signals Bot

Лови уведомления о whale-size ставках по выбранным рынкам.
⚡ Сигнал приходит в Telegram сразу после крупного размещения.

Готов включить сигналы?"""

CATEGORY_PROMPT_TEXT = "🎯 Выбери, что тебе сейчас важнее."

ACTIVATION_SUCCESS_TEXT = """✅ Готово. Подписка на категории включена.
🔔 Дальше ты будешь получать два уведомления по событию: whale-размещение и итог (выигрыш/проигрыш ставки кита)."""


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


def _format_pnl(pnl_usd: float) -> str:
    if pnl_usd >= 0:
        return f"+${pnl_usd:,.0f}"
    return f"-${abs(pnl_usd):,.0f}"


def _result_block(result: str, pnl_usd: float, note: str) -> str:
    if result == "win":
        return (
            "🎉 Результат ставки кита: ВЫИГРЫШ\n"
            f"💰 Примерный P&L (удержание до исхода): {_format_pnl(pnl_usd)}\n"
            f"ℹ️ {note}"
        )
    if result == "loss":
        return (
            "😞 Результат ставки кита: ПРОИГРЫШ\n"
            f"💸 Примерный убыток: {_format_pnl(pnl_usd)}\n"
            f"ℹ️ {note}"
        )
    if result == "exit_win":
        return (
            "✅ Результат для кита: УСПЕШНЫЙ ВЫХОД (продажа до исхода)\n"
            f"💰 Примерная выгода от выхода: {_format_pnl(pnl_usd)}\n"
            f"ℹ️ {note}"
        )
    if result == "exit_loss":
        return (
            "⚠️ Результат для кита: УПУЩЕННАЯ ВЫГОДА (продажа до исхода)\n"
            f"📉 Примерно не получено: {_format_pnl(pnl_usd)}\n"
            f"ℹ️ {note}"
        )
    return (
        "⚖️ Результат ставки кита: НИЧЬЯ 50/50\n"
        f"ℹ️ {note}"
    )


def format_resolution_text(
    *,
    market: str,
    whale_side: str,
    size_usd: float,
    price: float,
    winning_outcome: str | None,
    is_split: bool,
    result: str,
    pnl_usd: float,
    note: str,
    closed_time: str | None,
    category: str,
) -> str:
    outcome_line = (
        "⚖️ Исход события: ничья 50/50"
        if is_split
        else f"✅ Исход события: {winning_outcome or '—'}"
    )
    closed_line = f"🕒 Закрыто: {closed_time}\n" if closed_time else ""
    return f"""🏁 Итог события: результат ставки кита

🎯 Рынок: {market}
🧭 Платформа: Polymarket
📈 Ставка кита: {whale_side}
💵 Размер: ${size_usd:,.0f}
💲 Цена входа: {price:.2f}

{outcome_line}
{closed_line}{_result_block(result, pnl_usd, note)}
🏷 Категория: {category}"""
