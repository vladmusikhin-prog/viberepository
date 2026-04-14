# Bot

MVP Telegram-бот `Polymarket Signals` на `Python + aiogram`.

**Версия:** 0.1.1 · **Полная документация:** [DOCUMENTATION.md](DOCUMENTATION.md)

## Структура

- `src/handlers` — Telegram handlers и callback-обработка.
- `src/services` — бизнес-логика (сигналы, настройки, фидбек).
- `src/repositories` — in-memory репозитории для MVP.
- `src/workers` — polling worker для live-сигналов.
- `tests` — unit-тесты ключевой логики.

## Запуск

1. Скопируй `.env.example` в `.env` и задай `BOT_TOKEN`.
2. `BOT_USERNAME` опционален: если не задан, при старте запрашивается `getMe` у Telegram.
3. Установи зависимости (из папки `Bot/`):

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

4. Запусти бота (из папки `Bot/`):

```bash
.venv/bin/python -m src.main
```

Или: `./run.sh` (после `chmod +x run.sh`).

## Реализованные MVP-возможности

- `/start` онбординг и выбор категорий (`Politics`, `Crypto`, `Sports`, `All`).
- `/settings` с управлением категориями и статистикой пользы (`N/M`).
- Шаблон test/live whale-alert сообщений.
- Кнопки `Полезно` / `Не полезно`.
- Кнопка `Поделиться с другом` с deep-link инвайтом.
- Live-сигналы в polling-режиме (demo worker для MVP).
