# Документация — Polymarket Signals (Telegram Bot)

**Версия документа:** 0.2.6 (MVP, май 2026)  
**Стек:** Python 3.9+, [aiogram](https://docs.aiogram.dev/) 3.13, polling  
**Спецификация продукта:** [Docs/TELEGRAM_BOT_MVP_SPEC.md](../Docs/TELEGRAM_BOT_MVP_SPEC.md) (если файл есть в репозитории)

---

## 1. Назначение

Telegram-бот доставляет **whale-style алерты** по шаблону из Product Card: онбординг, выбор категорий, живые сигналы из мониторинга, фидбек и инвайт по ссылке (отдельного «тестового» алерта по кнопке нет).

**Режим `SIGNAL_SOURCE=polymarket` (по умолчанию):** опрос [Polymarket Data API](https://docs.polymarket.com/api-reference/core/get-trades-for-a-user-or-markets) `GET /trades` с `filterType=CASH` и `filterAmount=<WHALE_THRESHOLD_USD>`. Подбор категории пользователя (`Politics` / `Crypto` / `Sports`) — **эвристика по тексту** `title` + `slug` + `eventSlug` (не теги Gamma). Дедуп по `transactionHash`.

**Режим `SIGNAL_SOURCE=demo`:** фоновый worker **отключён** (нет периодических сигналов). Остаётся только онбординг и ручные команды; первый whale-alert пользователь получает уже из live-режима при `polymarket`.

---

## 2. Возможности текущей версии

| Область | Статус |
|--------|--------|
| `/start`, онбординг, кнопки из Product Card | Да |
| Категории: Politics, Crypto, Sports, All | Да |
| Отдельный тестовый whale-alert по кнопке в онбординге | Нет (только живые события) |
| Фоновые сигналы по таймеру без Polymarket | Нет (ранее demo worker; убрано) |
| `/settings`, смена категорий, выключение live | Да |
| Метрики: получено сигналов `N`, полезных `M` | Да |
| Кнопки «Полезно» / «Не полезно» | Да |
| «Поделиться с другом» (deep-link `t.me/<bot>?start=invite_<id>`) | Да |
| Хранение данных между перезапусками | Нет (in-memory) |
| Реальные сделки Polymarket (Data API) | Да (`SIGNAL_SOURCE=polymarket`) |

---

## 3. Структура репозитория (`Bot/`)

```
Bot/
├── .env                 # не коммитится; создаётся локально из .env.example
├── .env.example
├── requirements.txt
├── run.sh               # запуск: ./run.sh из каталога Bot/
├── README.md            # краткий вход
├── DOCUMENTATION.md     # этот файл
└── src/
    ├── main.py          # точка входа, Dispatcher, polling, worker
    ├── config.py        # настройки, загрузка .env из корня Bot/, getMe → username
    ├── logging_setup.py
    ├── integrations/    # HTTP-клиент Polymarket Data API
    ├── handlers/        # Telegram updates
    ├── services/        # бизнес-логика, тексты, клавиатуры, маппинг категорий
    ├── repositories/    # in-memory хранилище + dedup сделок
    ├── models/
    └── workers/         # SignalWorker — только Polymarket polling
└── tests/
```

Слои: **handlers → services → repositories** (см. [Docs/ARCHITECTURE.md](../Docs/ARCHITECTURE.md)).

---

## 4. Переменные окружения

Файл `.env` в каталоге `Bot/` (см. `.env.example`):

| Переменная | Обязательно | Описание |
|------------|-------------|----------|
| `BOT_TOKEN` | Да | Токен от [@BotFather](https://t.me/BotFather) |
| `BOT_USERNAME` | Нет | Username бота без `@`. Если пусто — подставляется из Telegram `getMe` при загрузке конфига |
| `WHALE_THRESHOLD_USD` | Нет (по умолчанию `100000`) | Порог для текста «Критерий whale» в шаблоне |
| `ALERT_MAX_PRICE` | Нет (`0.95`) | Верхняя граница цены для алертов (`0.00` и выше порога игнорируются) |
| `SIGNAL_POLL_INTERVAL_SEC` | Нет (по умолчанию `30`) | Интервал опроса Polymarket Data API (только при `SIGNAL_SOURCE=polymarket`) |
| `SIGNAL_SOURCE` | Нет (`polymarket`) | `polymarket` — фоновый опрос `/trades`; `demo` — без фонового worker |
| `POLYMARKET_DATA_API_BASE` | Нет | Базовый URL Data API (по умолчанию официальный) |
| `POLYMARKET_TRADES_LIMIT` | Нет (`100`) | Сколько последних сделок запрашивать за тик (макс. 500 на стороне клиента) |
| `POLYMARKET_MAX_TRADE_AGE_SEC` | Нет (`600`) | Не уведомлять о сделках старше N секунд (защита от «прострела» истории после рестарта) |
| `POLYMARKET_BACKFILL_ENABLED` | Нет (`true`) | Включить разовый backfill при старте бота |
| `POLYMARKET_BACKFILL_AGE_SEC` | Нет (`86400`) | Окно backfill (например 24 часа) |
| `POLYMARKET_BACKFILL_LIMIT` | Нет (`200`) | `limit` для backfill-запросов `/trades` |
| `POLYMARKET_BACKFILL_MAX_PAGES` | Нет (`8`) | Максимум страниц (offset = page*limit) |
| `ADMIN_USER_IDS` | Нет (пусто) | Список Telegram user id через запятую для доступа к `/admin_stats` (если пусто — команда доступна всем в локальном MVP) |
| `PERSISTENCE_MODE` | Нет (`sqlite`) | `sqlite` — подписки и дедуп переживают рестарт; `memory` — состояние сбрасывается |
| `SQLITE_DB_PATH` | Нет | Путь к SQLite базе (например `./data/bot.sqlite3`) |
| `LOG_LEVEL` | Нет (`INFO`) | Уровень логирования |

Загрузка: `src/config.py` сначала читает `Bot/.env`, затем стандартный `load_dotenv()` (cwd).

---

## 5. Запуск

Из каталога `Bot/`:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env   # отредактируй BOT_TOKEN
.venv/bin/python -m src.main
```

Или:

```bash
chmod +x run.sh
./run.sh
```

**Важно:** одновременно должен работать **только один** процесс polling для данного `BOT_TOKEN`, иначе Telegram вернёт конфликт.

---

## 6. Команды и сценарии

### Команды

- `/start` — приветствие и клавиатура «Активировать» / «Как это работает»
- `/help` — краткая подсказка
- `/settings` — категории, статус live, блок «Твоя статистика», кнопки изменения категорий и выключения сигналов
- `/admin_stats` — сводка метрик процесса (доступ только для `ADMIN_USER_IDS`)

### Callback-данные (основные)

| `callback_data` | Действие |
|-----------------|----------|
| `activate` | Выбор категорий |
| `how_it_works` | Экран «Как это работает» + кнопки `Активировать` / `Главное меню` |
| `category:<name>` | Сохранение категорий (`All` → все три) |
| `test_signal`, `open_test_signal`, `go_live` | Устаревшие `callback_data`: короткий ответ пользователю (старые сообщения с прошлых версий бота) |
| `feedback:helpful`, `feedback:not_helpful` | Учёт фидбека (`helpful` увеличивает `M`) |
| `disable_live` | Отключение live-флага у пользователя |

Кнопка «Поделиться с другом» — `url` на `https://t.me/share/url?...` с текстом инвайта и deep-link `https://t.me/<username>?start=invite_<telegram_user_id>`.

---

## 7. Метрики в `/settings`

- **Получено сигналов (`N`):** инкремент при успешной доставке live-сигнала пользователю (после дедупа по паре `signal_id` + `user_id`).
- **Отмечено полезными (`M`):** число нажатий «Полезно».

Данные хранятся в памяти процесса и **обнуляются при рестарте**.

---

## 8. Worker сигналов (`SignalWorker`)

### Polymarket (`SIGNAL_SOURCE=polymarket`)

- Каждые `SIGNAL_POLL_INTERVAL_SEC` запрашиваются крупные сделки с порогом `WHALE_THRESHOLD_USD` (через `filterType=CASH`).
- Сделки старше `POLYMARKET_MAX_TRADE_AGE_SEC` отбрасываются.
- Повтор одной и той же сделки одному пользователю блокируется парой `(signal_id, user_id)` в памяти процесса (`SignalRepository._delivery_guard`), в т.ч. при каждом опросе API (раньше кольцевой `SeenTradeStore` мог вытеснить hash и давать ложные повторы).
- Пользователям с подходящей категорией отправляется сообщение; учёт доставки — `DeliveryLog` / `mark_signal_delivered` **после** успешной отправки.
- При старте бота выполняется разовый `backfill` за `POLYMARKET_BACKFILL_AGE_SEC`: несколько страниц `/trades` с `offset`, чтобы догнать пропущенные события после простоя.

### Режим `SIGNAL_SOURCE=demo`

Фоновый `SignalWorker` **не запускается**. Периодической рассылки нет; онбординг без демо-алерта.

---

## 9. Тесты

```bash
cd Bot
.venv/bin/pytest -q
```

---

## 10. Ограничения и риски

- Нет персистентного хранилища — пользователи, статистика и журнал доставок не переживают рестарт (после рестарта возможен повтор по свежему ответу API в окне `POLYMARKET_MAX_TRADE_AGE_SEC`).
- Категория рынка для фильтра пользователя — **эвристика по строкам**, не официальные теги Gamma; возможны ошибки классификации.
- Поля Data API могут меняться; при сбоях сети тик логируется и пропускается.
- Инвайт по `start=invite_<id>` на MVP **без** серверной реферальной логики.
- Секреты только в `.env`; токен не должен попадать в git.

---

## 11. История версий (кратко)

| Версия | Изменения |
|--------|-----------|
| 0.1.0 | MVP: онбординг, категории, тест/live шаблоны, settings, N/M, фидбек, share, демо-worker; импорты `src.*`, загрузка `.env` из `Bot/`, опциональный `getMe` для username, глобальный лог ошибок dispatcher |
| 0.1.1 | Демо live: кулдаун `DEMO_LIVE_MIN_INTERVAL_SEC` на пользователя; шаблон рынка зависит от категории (Politics/Crypto/Sports) |
| 0.2.0 | Реальные сигналы: Polymarket Data API `/trades` + CASH filter; dedup по `transactionHash`; маппинг категорий; `SIGNAL_SOURCE` |
| 0.2.1 | Убран таймерный demo-worker; `SIGNAL_SOURCE=demo` = без фоновой рассылки |
| 0.2.2 | Дедуп Polymarket: только `(pm-<tx>, user_id)` без кольцевого `SeenTradeStore` (исправлены повторы из-за eviction) |
| 0.2.3 | Добавлена админ-команда `/admin_stats` с доступом по `ADMIN_USER_IDS` |
| 0.2.4 | Добавлена персистентность подписок и delivery-dedup через SQLite (24/7 при всегда запущенном процессе) |
| 0.2.6 | Убран тестовый whale-alert из онбординга; «Как это работает» ведёт к активации без демо-сообщения |

---

## 12. Полезные ссылки

- [Product Card](../Docs/product/Product%20Card.md)
- [Архитектура репозитория](../Docs/ARCHITECTURE.md)
