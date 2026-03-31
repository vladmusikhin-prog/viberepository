---
title: Social Prediction Game Bot (B2C) — PRD-lite
status: draft
updated: 2026-03-27
owner: Trend Researcher
---

## TL;DR
Легковесная социальная игра в Telegram вокруг прогнозов (без ставок на деньги): пользователи выбирают исходы событий, получают XP/роли/внутриигровые награды, соревнуются в лигах и делятся карточками прогнозов. Опционально: часть рынков “зеркалит” Polymarket как **источник истины** для резолва (read-only, без трейдинга/кошельков).

## Problem → Opportunity
- **Проблема**: людям нравится “быть правыми” и обсуждать исходы событий, но prediction markets имеют порог входа (кошелёк/риск/регуляторика).
- **Возможность**: дать тот же азарт “быть точным” как **социальный спорт** — быстро, вирусно, безопасно, без money-betting.

## Product principles (guardrails)
- **No betting UX**: не использовать “bet/wager/odds to win money”. Только “predict/forecast/vote/accuracy”.
- **Explainable outcomes**: формулы скоринга, правила резолва и источники — публичны.
- **Social-first**: карточки/лиги/сквады важнее сложной “рыночной модели”.
- **Operator-light**: контент должен масштабироваться (шаблоны, полуавто-импорт, модерация по чеклисту).

## JTBD
- **User**: “Сделать прогноз за 10 секунд и узнать, прав ли я.”
- **Competitive user**: “Подниматься в лигах и показать статус.”
- **Social user**: “Челленджить друзей и спорить, кто прав.”
- **Channel owner**: “Запускать ‘market of the day’ для роста вовлечения.”

## Target users (global)
- **Crypto-native**: следят за Polymarket/X, любят лидерборды и метрики.
- **Sports / pop culture**: короткие интерактивы “перед матчем/релизом”.
- **Community-first**: Telegram-комьюнити, которым нужен “ритуал” и спор.

## Positioning
**“Polymarket-style predictions as a social game in Telegram.”**

Чем отличаемся:
- **No money betting**: только XP/очки/косметика.
- **Social-first**: лиги, сквады, каналовые лидерборды.
- **Fast**: 1–2 тапа, daily markets, уведомления.

## Core loop
1) **Discover** → 2) **Predict** → 3) **Share** → 4) **Resolve** → 5) **Reward** → 6) **Progress**

## UX in Telegram (flows)
### Main screens
- **Home**: Today’s markets + streak + rank + CTA “Make 1 prediction”
- **Market**: вопрос, варианты, close time, rules, source-of-truth, CTA Predict
- **Confirm**: выбранный исход (+ optional confidence) + CTA Share
- **Profile**: accuracy, streak, badges, category performance
- **Leaderboard**: global + league weekly + squad + channel
- **Inbox**: резолвы, промо/демо, event drops

### Commands (minimal)
- `/start` onboarding
- `/markets` today markets
- `/profile` stats
- `/leaderboard` weekly
- `/settings` interests/notifications/privacy
- Admin-only: `/admin_markets`, `/admin_resolve`, `/admin_disputes`

### Onboarding (MVP)
1) Interests → 2) Notifications → 3) First prediction (показать 1–3 starter markets)

## Market formats (non-betting friendly)
- **Binary**: “Will X happen by date?”
- **Multiple choice**: “Which team wins?”
- **Confidence (post-MVP)**: пользователь задаёт вероятность \(p\) → proper scoring.

## Market spec (operator checklist)
Каждый рынок обязан иметь:
- **Question** (однозначно)
- **Choices** (2–6)
- **Close time** (UTC)
- **Resolve rule** (как считается outcome)
- **Source links** (1–3)
- **Category** + **tags**
- **Dispute window**: 24h

Anti-ambiguity:
- никаких “примерно/скорее всего”
- tie-break правила при ничьих/переносах
- заранее определённая версия источника (официальный сайт/репорт/пост)

## Scoring & leagues (detailed)
### Mode A (MVP): outcome-only
- **Participation XP**: +5 (чтобы новичок прогрессировал)
- **Correct bonus**: +20…+60 (в зависимости от сложности/категории)
- **Streak**: мягкий множитель (cap)

### Mode B (post-MVP): confidence + Brier
- \(BS=(p-o)^2\), где \(o\in\{0,1\}\)
- Перевод в очки: \(score = max(0, 1 - BS)\) → масштабировать в XP/league points

### League points
- **Weekly points** = сумма top-N рынков недели (например, N=20) → анти-спам
- Промо/демо: top 20% ↑, bottom 20% ↓

## Social mechanics (growth)
### Share cards (viral unit)
Содержимое карточки:
- question + pick (+ optional confidence)
- “closes in Xh”
- CTA deep-link “Join & challenge me”

### Squads (friends leaderboard)
- Opt-in “squad” (по рефералке): общий лидерборд + weekly squad quest.

### Channel mode (B2B2C)
Для владельцев каналов:
- автогенерация поста “Market of the day”
- каналовый лидерборд и weekly recap
- брендирование (в платном пакете)

## Content ops (how it runs weekly)
- **Daily set**: 10–20 рынков
- **Event drops**: Oscar week / Apple event / big sports day
- **Moderation SLA**: резолв в течение X часов после resolve time

Роли:
- Content operator (создаёт рынки)
- Resolver (подтверждает исход)
- Dispute admin (апелляции)

## Resolution (“source of truth”)
Уровни:
1) **Manual (MVP)**: модератор резолвит + ссылка на источник  
2) **API**: спорт/бокс‑офис/цены/выборы  
3) **Polymarket mirror**: read-only резолв по оригинальной формулировке (без ставок)

### Disputes (MVP)
- Dispute в 24h с evidence link
- Очередь для админа: market_id, proposed outcome, evidence, reporter
- Решение: accept (пересчёт) / reject (cooldown за спам)

## Rewards & economy (safe-by-design)
- **XP + roles**
- **Cosmetics**
- **Points/credits** (не “token” публично), без вывода, без P2P на старте
- **Partner NFTs (optional)**: achievement badges без “yield”/доходности

## Monetization
- **Premium**: аналитика/инсайты/больше слотов рынков
- **Season pass**: косметика/ивенты
- **Creator pack (channels)**: инструменты для каналов
- **Sponsorships**: бренд‑недели

Pricing strawman:
- Premium: $7–$15/mo
- Season pass: $10–$25/season
- Creator pack: $49–$199/mo

## MVP scope (2–4 weeks) + backlog
P0:
- сущности: users, markets, predictions, resolutions, xp_ledger
- флоу: browse → predict → resolve → score
- weekly leaderboard (global + league)
- share card + deep-link + referral
- базовый anti-abuse: rate limits, 1 prediction/market, new-user league

P1:
- personalization (interest feed)
- streaks + badges
- squads leaderboard
- dispute queue tooling

P2:
- confidence mode
- channel mode MVP
- seasonal pass

## Validation plan (7–10 days)
- 3–5 каналов, “market of the day” 7 дней
- Метрики:
  - activation (first prediction <5 min)
  - D1/D7 retention
  - predictions/user/day
  - share rate
  - K-factor
- Qual: 15–20 интервью + анализ “какие рынки цепляют”

## Instrumentation (events)
- `onboarding_started`, `interests_selected`, `prediction_submitted`
- `share_card_created`, `referral_accepted`
- `market_resolved_viewed`, `leaderboard_viewed`
- `dispute_opened`, `dispute_resolved`
- `premium_paywall_viewed`, `purchase_completed`

## Risks & mitigations
- **Regulatory confusion**: no-cash, no-withdrawal, no “betting language”
- **Disputes**: строгие правила резолва + источники + апелляции
- **Ops load**: шаблоны + полуавто-импорт
- **Fraud**: rate limits, anti-sybil, league separation, delayed reveal (post-MVP)

## Roadmap
### 3–6 months
- Creator pack как основной ростовой канал
- squads + командные события
- confidence + calibration insights
- полуавто-резолв (API) + event drops

### 12 months
- community markets с репутацией авторов
- “pro mode”: Polymarket mirror + сравнение “crowd vs you”
- open API/интеграции для каналов/mini-apps
