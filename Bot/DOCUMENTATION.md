# Документация — Polymarket Signals (Telegram Bot)

**Версия документа:** 0.1.0 (MVP, апрель 2026)  
**Стек:** Python 3.9+, [aiogram](https://docs.aiogram.dev/) 3.13, polling  
**Спецификация продукта:** [Docs/TELEGRAM_BOT_MVP_SPEC.md](../Docs/TELEGRAM_BOT_MVP_SPEC.md) (если файл есть в репозитории)

---

## 1. Назначение

Telegram-бот доставляет **whale-style алерты** по шаблону из Product Card: онбординг, выбор категорий, тестовый сигнал, демо live-поток, фидбек и инвайт по ссылке. **Реальная интеграция с Polymarket API в этой версии не подключена** — «live» сигналы генерирует фоновый worker для проверки UX и пайплайна доставки.

---

## 2. Возможности текущей версии

| Область | Статус |
|--------|--------|
| `/start`, онбординг, кнопки из Product Card | Да |
| Категории: Politics, Crypto, Sports, All | Да |
| Тестовый сигнал (шаблон whale-alert) | Да |
| Демо live-сигналы по таймеру (worker) | Да |
| `/settings`, смена категорий, выключение live | Да |
| Метрики: получено сигналов `N`, полезных `M` | Да |
| Кнопки «Полезно» / «Не полезно» | Да |
| «Поделиться с другом» (deep-link `t.me/<bot>?start=invite_<id>`) | Да |
| Хранение данных между перезапусками | Нет (in-memory) |
| Реальные сделки Polymarket | Нет (следующий этап) |

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
    ├── handlers/        # Telegram updates
    ├── services/        # бизнес-логика, тексты, клавиатуры
    ├── repositories/    # in-memory хранилище
    ├── models/
    └── workers/         # SignalWorker — демо-генерация live-сигналов
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
| `SIGNAL_POLL_INTERVAL_SEC` | Нет (по умолчанию `30`) | Интервал тика демо-worker |
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

### Callback-данные (основные)

| `callback_data` | Действие |
|-----------------|----------|
| `activate` | Выбор категорий |
| `how_it_works` | Текст превью + клавиатура теста |
| `category:<name>` | Сохранение категорий (`All` → все три) |
| `test_signal`, `open_test_signal` | Отправка тестового алерта |
| `go_live` | Подтверждение ожидания live |
| `feedback:helpful`, `feedback:not_helpful` | Учёт фидбека (`helpful` увеличивает `M`) |
| `disable_live` | Отключение live-флага у пользователя |

Кнопка «Поделиться с другом» — `url` на `https://t.me/share/url?...` с текстом инвайта и deep-link `https://t.me/<username>?start=invite_<telegram_user_id>`.

---

## 7. Метрики в `/settings`

- **Получено сигналов (`N`):** инкремент при успешной доставке live-сигнала пользователю (после дедупа по паре `signal_id` + `user_id`).
- **Отмечено полезными (`M`):** число нажатий «Полезно».

Данные хранятся в памяти процесса и **обнуляются при рестарте**.

---

## 8. Демо worker (`SignalWorker`)

Циклически перебирает категории `Politics` → `Crypto` → `Sports`, для пользователей с `is_live_enabled` и подходящей подпиской создаёт сообщение live-формата и шлёт в личку. Используется для **отладки UX**, не как рыночный источник истины.

---

## 9. Тесты

```bash
cd Bot
.venv/bin/pytest -q
```

---

## 10. Ограничения и риски

- Нет персистентного хранилища — пользователи и статистика не переживают рестарт.
- Нет вызовов Gamma/Data/CLOB Polymarket — сигналы шаблонные.
- Инвайт по `start=invite_<id>` на MVP **без** серверной реферальной логики.
- Секреты только в `.env`; токен не должен попадать в git.

---

## 11. История версий (кратко)

| Версия | Изменения |
|--------|-----------|
| 0.1.0 | MVP: онбординг, категории, тест/live шаблоны, settings, N/M, фидбек, share, демо-worker; импорты `src.*`, загрузка `.env` из `Bot/`, опциональный `getMe` для username, глобальный лог ошибок dispatcher |

---

## 12. Полезные ссылки

- [Product Card](../Docs/product/Product%20Card.md)
- [Архитектура репозитория](../Docs/ARCHITECTURE.md)
