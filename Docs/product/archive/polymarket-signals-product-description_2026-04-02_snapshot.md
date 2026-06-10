# Snapshot — Product Description — Polymarket Signals (Telegram Social Layer)

> Снимок состояния документа до актуализации pain #6 (whale signals) и MVP-объёма.
> Дата: 2026-04-02

## Original content

(Содержимое ниже сохранено как есть.)

# Product Description — Polymarket Signals (Telegram Social Layer)

## Template (как устроен документ)

1. `Краткое описание`
2. `Проблема и возможность`
3. `Целевая аудитория`
4. `Ценность (value proposition)`
5. `Решение (что делает продукт)`
6. `MVP: что именно строим в первые 4–6 недель`
7. `Данные для MVP (откуда берём)`
8. `Топ-10 болей → узкие аудитории → данные для MVP`
9. `Метрики успеха`
10. `Риски и как снижаем`

---

## 1) Краткое описание

`Polymarket Signals (Social Layer)` — Telegram-бот, который агрегирует сигналы по prediction markets (например, новые рынки, резкие сдвиги вероятностей, всплески объёма, крупная “whale”-активность) и превращает их в удобный social-слой: публичные портфели идей, профили аналитиков и рейтинги.

На MVP стадии бот фокусируется на `Signals engine + alert scoring` и `Social layer lite` (без автоторговли): пользователь получает приоритизированные алерты с контекстом и может “follow” аналитиков, чтобы получать те же уведомления.

---

## 2) Проблема и возможность

Проблемы пользователей в Polymarket-экосистеме:
- Пользователи тонут в данных и пропускают “режимные” изменения (быстрые сдвиги вероятностей/объёмов).
- Сигналы часто непрозрачны: трудно понять “что произошло” и “почему этому можно доверять”.
- Нет удобного социального слоя, который объясняет, у кого реально получается и что именно следует смотреть.

Возможность:
- Сфокусироваться на `оперативных, объяснимых и скорингованных сигналах` + `доверяемом social ranking`, упакованных в один Telegram-интерфейс.

Контекст продукта (из проектных документов):
- Telegram-бот, как платформа для автоматизации ключевого пользовательского сценария.
- Нефункциональные требования на уровне проекта: скорость реакции (до 1 секунды), надежность, безопасность токенов, логирование.

---

## 3) Целевая аудитория

### B2C
- Активные трейдеры/наблюдатели prediction markets, которые хотят видеть важное “в нужное время”.
- Пользователи, которым нужны приоритизированные сигналы вместо “шума”.
- Пограничная аудитория social-copy: люди, которые хотят следовать идеям аналитиков, но без автоторговли на MVP.

### B2B
- Трейдинг-комьюнити/админы приватных каналов.
- Аналитические desks, которые хотят “branded bot / white-label” режим и leaderboard-слой для валидации ценности сигналов.

---

## 4) Ценность (value proposition)

- `Fast detection`: события рынка, которые случились “прямо сейчас” (минуты).
- `Context, not noise`: алерт объясняет, что произошло и почему это важно.
- `Reputation layer`: рейтинг аналитиков/идей с учетом резолвнутых исходов и устойчивости (не one-hit wonder).

---

## 5) Решение (что делает продукт)

### 5.1 Signals (основа)
- `New market alerts` по избранным категориям.
- `Probability jump alerts` (например, “>8–12% за N минут” — порог настраивается пользователем).
- `Volume spike alerts`.
- `Whale activity alerts` (крупные сделки/серии сделок).
- `Market reopen / resolution window alerts`.

Каждый алерт получает `priority score` (MVP-версия):
- magnitude (сила сдвига вероятности),
- speed (насколько быстро произошёл сдвиг),
- liquidity quality (объём/спред),
- novelty (насколько аномально для данного рынка),
- confidence flag (качество данных/флаг рисков).

Пример формата алерта (идея):
- “Market X moved from 41% to 54% in 22m, volume +240%, spread medium, risk flag: low liquidity.”

### 5.2 Analytics (срезы поверх алертов)
- Heatmap топ-рынков по изменению вероятности.
- Top movers (1h/6h/24h).
- Unusual flow (объём относительно среднего).
- Category momentum (политика/спорт/крипто/бизнес и т.п.).
- Market quality flags (тонкая ликвидность, высокий спред).

### 5.3 Social layer lite (MVP)
- Analyst profiles: hit-rate, calibration, avg horizon (на MVP — упрощенно).
- Social portfolios: “ideas book” без исполнения.
- Leaderboards: daily/weekly + категориями.
- Copy ideas (MVP): пользователь подписывается на feed аналитика и получает те же алерты.

### 5.4 Монетизация (модель)

- `B2C Premium`: расширенные алерты, более низкая задержка, advanced analytics.
- `Pro tiers`: API/webhook, кастомные правила сигналов (например, пользователь задаёт свои пороги и фильтры).
- `B2B White-label`: branded bot для трейдинг-комьюнити/каналов (возможна настройка лимитов/правил, лидерборды).
- `Research packs`: еженедельные/ежемесячные дайджесты и “интеллидженс-паки” по выбранным категориям.

Ценовая гипотеза (стартовая):
- Premium: `$19–$49/mo`
- Pro: `$79–$199/mo`
- White-label: `$300–$2,000/mo`

---

## 6) MVP: что строим в первые 4–6 недель

Цель MVP:
- доказать, что приоритизированные и объяснимые сигналы реально приводят к использованию (“alert -> action”),
- и что social layer помогает доверять источникам (простая репутационная модель на резолвах).

P0 (ship, 4–6 недель):
- Подключение к источникам market data.
- `New market + top mover + probability jump alerts`.
- Простой feed + watchlist + категории.
- Базовый leaderboard по “идея-постам и резолвам”.

P1 (после MVP):
- whale flags.
- social portfolios.
- copy-ideas subscriptions.

---

## 7) Данные для MVP (откуда берём)

### Источники рыночных данных (для генерации сигналов и скоринга)
- Timeline market data по рынкам (вероятности/цены во времени).
- Объёмы и ликвидность (для volume/liq/spread quality).
- Данные по резолвам (outcomes), чтобы оценивать precision/leaderboard.
- Orderbook / trades (для “whale” и market microstructure), если доступны.

Конкретные площадки/сайты, к которым можно подключиться на MVP (проверено по наличию API/доков):
- Polymarket
  - Docs: `https://docs.polymarket.com/`
  - Gamma API (публичный): `https://docs.polymarket.com/api-reference` (markets/events/tags/search)
  - Data API (публичный): `https://docs.polymarket.com/api-reference` (positions/trades/leaderboards и т.п.)
  - CLOB API (orderbook/trading): `https://docs.polymarket.com/developers/CLOB/endpoints`
- Kalshi
  - Docs: `https://docs.kalshi.com/`
  - REST/WebSocket (market data + trading): описано в официальных доках (см. quick start по market data)
- Manifold Markets
  - Docs: `https://docs.manifold.markets/api`
  - API (alpha): `https://api.manifold.markets` (рынки, ставки, пользователи, и т.д.)
- Metaculus (как доп. источник “forecasting questions”, не рынок для трейдинга)
  - API docs: `https://www.metaculus.com/api/`
- PredictIt (как доп. источник рыночных данных, но с ограничениями по использованию)
  - Public market data API: `https://www.predictit.org/api/marketdata/all/` (non-commercial условия указаны в справке)

### Источники продуктовых данных (для валидации ценности в Telegram)
- Метрики Telegram-UX: открытие алертов, клики в рынки, добавления в watchlist, отписки.
- Локальные действия пользователя: какие категории выбрал, какие thresholds поставил.
- Микро-фидбек: “полезно/не полезно” (супер короткий опрос прямо в боте) для оценки signal precision.

### Что пользователи чаще всего ищут (интернет-сигналы спроса)

По публичным материалам и сервисам вокруг Polymarket в 2026 чаще всего встречаются запросы/темы:
- `odds / probability` (как читать шансы, что значит “вероятность”)
- `volume` (как интерпретировать объём, где смотреть всплески)
- `whale moves / large trades` (как отследить крупные сделки)
- `market tracker` / “live odds & volume” (нужен дашборд/трекер)
- `API` (как получить данные программно)

Примеры источников, откуда это видно:
- Рост интереса к Polymarket и обсуждение поискового спроса: `https://bitcoinworld.co.in/polymarket-google-search-record-high/`
- Гайды по анализу odds/volume/whales (контент, который “закрывает” типичные вопросы): `https://vpn07.com/en/blog/2026-polymarket-market-analysis-odds-volume-whale-tracking-guide.html`
- Продукты “market tracker / whale alerts” как индикатор потребности: `https://polywhaletracker.com/market-tracker/`, `https://www.polymarketflow.com/alerts-feed`
- Официальные API-доки Polymarket (частый “developer intent”): `https://docs.polymarket.com/`

---

## 8) Топ-10 болей: узкие аудитории и данные для MVP

| Топ боль | Узкая целевая аудитория | Что именно болит (в 1–2 фразы) | Откуда берём данные для MVP |
|---|---|---|---|
| 1. Пропуск быстрых “режимных” изменений | Скальперы/short-term наблюдатели (минуты–часы) | Не успевают заметить probability jumps и поэтому входят/выходят поздно | Таймсериес вероятностей + события “jump” из market data; user metrics: alert-to-action |
| 2. Сигналы без доверия/валидируемости | Сомневающиеся пользователи, которые “не верят в шум” | Неясно, почему сигнал сработал, и насколько он надежен | Резолв outcomes + вычисление hit-rate; микро-фидбек “полезность” + объяснения в алерт |
| 3. “Слишком много сигналов” → усталость | Аудитория с низким вниманием (получают много уведомлений) | Алерты создают шум и снижают retention | Метрики: opens/unsubscribes/churn intent; пороговые настройки в `thresholds` |
| 4. Отсутствие контекста “что произошло и почему важно” | Занятые пользователи (нужен смысл за секунды) | Получают число, но не получают причинно-следственный контекст | Данные для объяснения из скоринга (magnitude/speed/liquidity flags); оценка полезности |
| 5. Проблемы из-за тонкой ликвидности/спреда | Трейдеры, чувствительные к проскальзыванию | “Сигнал есть, но исполнять неприятно/рискованно” | liquidity/spread quality из market data; корреляция с плохими outcomes (precision) |
| 6. Whale-движения теряются среди общего шума | Пользователи, фокусирующиеся на крупных игроках | Не видят whale activity или видят поздно | on-chain/агрегированные events (если доступны) или proxy-сигналы из volume/flow; качество подтверждаем резолвами |
| 7. Нужен “трекер” odds+volume в одном месте | Пользователи, которые мониторят много рынков параллельно | Сложно быстро понять “что сейчас движется” без ручного просмотра десятков рынков | Polymarket Gamma/Data API (`https://docs.polymarket.com/`), Kalshi market data API (`https://docs.kalshi.com/`); свои “top movers” и heatmap |
| 8. Нужны алерты “как у whale tracker”, но в Telegram | Пользователи, которые гуглят whale moves / large trades | Хотят видеть крупные сделки/аномальные потоки без отдельного сайта | Polymarket CLOB endpoints (orderbook/trades) `https://docs.polymarket.com/developers/CLOB/endpoints` + Data API; (опц.) Kalshi orderbooks/WS `https://docs.kalshi.com/` |
| 9. Нужен программный доступ к данным (“API”, экспорт, интеграции) | Dev-аудитория, кванты, владельцы community-ботов | Хотят подключить данные к своим пайплайнам/дашбордам | Polymarket API (Gamma/Data/CLOB): `https://docs.polymarket.com/`; Kalshi API: `https://docs.kalshi.com/`; Manifold API: `https://docs.manifold.markets/api` |
| 10. Нужны “понятные правила сигналов” (какие пороги ставить) | Новички и “вернувшиеся” пользователи | Не знают, что такое “нормальный” jump/volume spike и как настроить алерты | Исторические таймсериес (Polymarket Data API / Kalshi historical data docs) + продуктовые метрики (какие настройки приводят к меньшему шуму/большей action-rate) |

---

## 9) Метрики успеха (для MVP)

По проектным метрикам:
- `alert open rate`
- `alert-to-action rate` (клик в рынок / добавление в watchlist)
- `D7/D30 retention`
- `premium conversion` (если сразу запускаем tiers)
- `analyst follow rate`
- `signal precision` (доля полезных алертов по поведению/опросам)

---

## 10) Риски и как снижаем

Риски (из PRD-lite и связанные с ML/данными):
- `Signal noise`: слишком много алертов.
  - Митигирование: adaptive thresholds + sensitivity profiles.
- `False confidence`: “сигнал = гарантия”.
  - Митигирование: language вероятностей + risk disclaimer в каждом алерте.
- `Data quality gaps`: неполные/неточные данные.
  - Митигирование: multi-source checks + confidence labels.
- `Market manipulation in thin markets`:
  - Митигирование: liquidity flags, пенализация низкокачественных рынков в рейтингах.

