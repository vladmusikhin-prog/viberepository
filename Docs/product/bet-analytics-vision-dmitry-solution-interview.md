# Видение аналитики ставки (по solution interview Дмитрия)

**Версия:** 1.0  
**Дата:** 2026-06-09  
**Источники:** [dmitry-solution-interview-analysis-2026-05-28.md](./dmitry-solution-interview-analysis-2026-05-28.md), [product-change-plan-v1-dmitry-solution-interview.md](./product-change-plan-v1-dmitry-solution-interview.md) (E4, E5, E6)

## Главный тезис

Публичную сделку можно увидеть на Polymarket самому; платная ценность — **интерпретация**, которую пользователь не соберёт быстро вручную: аномальность для рынка, контекст входа, качество кита.

## Три слоя

| Слой | Вопрос | Метрики v1 |
|------|--------|------------|
| Market | Насколько сделка необычна? | p50 size по `condition_id`, `anomaly_ratio` |
| Trade | Насколько информативна ставка? | implied %, odds bucket, flash (<24h до закрытия) |
| Trader | Насколько надёжен кит? | WR + N, PnL split, частота, skill hint |

## Signal strength

Rule-based verdict: **сильный / заметный / слабый** + одна строка «почему». Не grade S/A без explainability.

## Free vs Pro

- **Free:** факт сделки, краткая аномальность (≈N×), implied %; trader block — WR + PnL без имени кита.
- **Pro:** полный baseline, trade timing, skill hint, PnL split, частота; имя кита + ссылка — только для `TRADER_STATS_VISIBLE_TO`.

Конфиг: `PRO_USER_IDS` (Telegram user id через запятую).

## Реализация в коде

- `Bot/src/services/bet_analytics.py` — pure logic (verdict, odds bucket, formatting)
- `Bot/src/services/market_baseline_service.py` — baseline по рынку
- `Bot/src/services/bet_analytics_service.py` — сборка контекста для алерта
- `Bot/src/services/tier_service.py` — Free/Pro gating
- Расширенный `TraderStats` в `trader_stats_service.py`

## Принципы

1. Не обещать «инсайд» — только публичные данные + интерпретация.
2. Не блокировать доставку алерта ради тяжёлой аналитики (timeout + cache).
3. При малой выборке — «недостаточно истории», не ложный score.
