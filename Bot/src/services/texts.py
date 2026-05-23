from __future__ import annotations

START_TEXT = """🐋 Whale Signals Bot

Лови уведомления о whale-size ставках по выбранным рынкам.
⚡ Сигнал приходит в Telegram сразу после крупного размещения.

Готов включить сигналы?"""

CATEGORY_PROMPT_TEXT = "🎯 Выбери, что тебе сейчас важнее."

INVITE_ALREADY_ACTIVE_TEXT = """🙌 Спасибо, что вы с нами!

🔔 Твоя подписка уже активна — whale-сигналы продолжают приходить сюда.
⚙️ Настройки можно посмотреть ниже или через /settings."""

NOTIFICATIONS_DISABLED_TEXT = """🔕 Уведомления деактивированы.

Ты остаёшься в боте — whale-сигналы не будут приходить, пока снова не нажмёшь «Активировать».
Так можно сделать паузу без отписки от бота."""

ACTIVATION_SUCCESS_TEXT = """✅ Готово. Подписка на категории включена."""

_ACTIVATION_EXAMPLES: dict[str, dict[str, str | float]] = {
    "Politics": {
        "market": "Will the next Prime Minister of Hungary be Péter Magyar?",
        "side": "BUY Yes",
        "size_usd": 142_500,
        "price": 0.38,
        "time": "14:05",
        "category": "Politics",
    },
    "Crypto": {
        "market": "Will Bitcoin reach $150k in 2026?",
        "side": "BUY Yes",
        "size_usd": 215_000,
        "price": 0.52,
        "time": "09:30",
        "category": "Crypto",
    },
    "Sports": {
        "market": "Will Atalanta BC win on 2026-05-24?",
        "side": "BUY Yes",
        "size_usd": 298_888,
        "price": 0.43,
        "time": "18:20",
        "category": "Sports",
    },
    "Geopolitics": {
        "market": "Will there be a ceasefire in Ukraine before July 2026?",
        "side": "BUY Yes",
        "size_usd": 186_000,
        "price": 0.34,
        "time": "11:15",
        "category": "Geopolitics",
    },
    "Economics": {
        "market": "Will the Fed cut rates in June 2026?",
        "side": "BUY Yes",
        "size_usd": 124_000,
        "price": 0.58,
        "time": "15:40",
        "category": "Economics",
    },
    "All": {
        "market": "Will Bitcoin reach $150k in 2026?",
        "side": "BUY Yes",
        "size_usd": 215_000,
        "price": 0.52,
        "time": "09:30",
        "category": "Crypto",
    },
}


def format_activation_example_text(*, category: str, whale_threshold_usd: int) -> str:
    sample = _ACTIVATION_EXAMPLES.get(category, _ACTIVATION_EXAMPLES["All"])
    alert = format_alert_text(
        market=str(sample["market"]),
        side=str(sample["side"]),
        size_usd=float(sample["size_usd"]),
        price=float(sample["price"]),
        timestamp_utc=str(sample["time"]),
        whale_threshold_usd=whale_threshold_usd,
        category=str(sample["category"]),
    )
    threshold_k = whale_threshold_usd / 1000
    return f"""{ACTIVATION_SUCCESS_TEXT}

📋 Пример: так будет выглядеть уведомление о крупной сделке

{alert}

ℹ️ Это демо-пример, не реальная сделка.

🔎 Мы мониторим Polymarket 24/7. Как только появится whale-сделка от ${threshold_k:.0f}k+ в твоих категориях — сразу пришлём алерт сюда.

🏁 После закрытия рынка придёт второе сообщение с итогом (выигрыш или проигрыш ставки кита)."""


def format_trader_stats_block(
    *,
    display_name: str,
    wins: int,
    losses: int,
    win_rate_pct: int,
    total_realized_pnl_usd: float,
    positions_sampled: int,
    positions_limit: int,
) -> str:
    pnl_label = _format_pnl(total_realized_pnl_usd)
    sample_note = (
        f"последние {positions_sampled} закрытых позиций"
        if positions_sampled < positions_limit
        else f"последние {positions_limit} закрытых позиций"
    )
    return (
        f"👤 Кит: {display_name}\n"
        f"📊 WR: {win_rate_pct}% ({wins}/{wins + losses} успешных закрытых позиций)\n"
        f"💰 Realized P&L ({sample_note}): {pnl_label}"
    )


def format_alert_text(
    market: str,
    side: str,
    size_usd: float,
    price: float,
    timestamp_utc: str,
    whale_threshold_usd: int,
    category: str,
    trader_stats_block: str | None = None,
) -> str:
    trader_section = f"\n{trader_stats_block}\n" if trader_stats_block else ""
    return f"""🐋 Whale Alert: крупное размещение

🎯 Рынок: {market}
🧭 Платформа: Polymarket
📈 Сторона: {side}
💵 Размер: ${size_usd:,.0f}
💲 Цена: {price:.2f}
🕒 Время: {timestamp_utc} UTC
{trader_section}
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
