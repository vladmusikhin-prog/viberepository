---
title: Polymarket Signals & Social Layer Bot (B2C/B2B) — PRD-lite
status: draft
updated: 2026-03-27
owner: Trend Researcher
---

## TL;DR
Telegram-бот, который агрегирует сигналы по prediction markets (новые рынки, резкие сдвиги вероятностей, объёмы, whale-активность), а затем превращает их в social-слой: публичные портфели прогнозов, рейтинги аналитиков, копирование идей (без автоторговли на MVP).

## Problem → Opportunity
- Пользователи тонут в данных Polymarket и не успевают замечать “режимные” изменения.
- Текущие сигнал-каналы часто непрозрачны и трудно валидируются.
- Возможность: дать **оперативные сигналы + доверяемый social ranking** в одном Telegram-интерфейсе.

## Target users
- **B2C**: активные трейдеры/наблюдатели prediction markets.
- **B2B**: трейдинг-комьюнити, private groups, аналитические desks.

## Core value proposition
- **Fast detection**: важные события рынка в течение минут.
- **Context, not noise**: бот не просто шлёт алерт, а объясняет “что произошло и почему важно”.
- **Reputation layer**: кто стабильно даёт качественные идеи по категориям/горизонтам.

## Product pillars
- **Signals**: real-time алерты по аномалиям.
- **Analytics**: срезы по объёму, ликвидности, probability shifts.
- **Social**: публичные портфели и рейтинги.
- **Distribution**: channel/white-label режим для комьюнити.

## Functional scope
### 1) Signal feed
- New market alerts (по избранным категориям)
- Probability jump alerts (например, >8–12% за N минут)
- Volume spike alerts
- Whale activity alerts (крупные сделки/серии сделок)
- Market reopen / resolution window alerts

### 2) Aggregated analytics
- Heatmap: топ рынков по изменению вероятности
- Top movers (1h/6h/24h)
- Unusual flow (объём относительно среднего)
- Category momentum (politics/sports/crypto/business)
- Market quality flags (тонкая ликвидность, высокий спред)

### 3) Social layer
- “Analyst profiles”: hit-rate, calibration, avg horizon
- Social portfolios: “ideas book” без исполнения
- Leaderboards: daily/weekly/monthly + category-specific
- Copy ideas (MVP): follow analyst feed and get same alerts

## Telegram UX
- `/start` choose categories + alert thresholds
- `/feed` live signals
- `/movers` top movers snapshot
- `/portfolio` social ideas portfolio
- `/leaders` rankings
- `/watchlist` custom markets
- `/alerts` sensitivity settings

## Signal scoring model (MVP)
Каждый алерт получает priority score:
- magnitude (сила сдвига вероятности)
- speed (как быстро произошёл сдвиг)
- liquidity quality (объём/спред)
- novelty (насколько аномально для данного рынка)
- confidence flag (качество данных)

Формат алерта:
- “Market X moved from 41% to 54% in 22m, volume +240%, spread medium, risk flag: low liquidity.”

## Social ranking model
Оценка аналитиков должна учитывать:
- точность по резолвнутым рынкам
- калибровку confidence (если есть)
- риск-скорректированную эффективность (не только hit-rate)
- устойчивость по времени (не one-hit wonder)

## Monetization
- **B2C Premium**: расширенные алерты, более низкая задержка, advanced analytics.
- **Pro tiers**: API/webhook, кастомные правила сигналов.
- **B2B White-label**: branded bot для трейдинг-комьюнити/каналов.
- **Research packs**: weekly/monthly intelligence report.

Pricing strawman:
- Premium: $19–$49/mo
- Pro: $79–$199/mo
- White-label: $300–$2,000/mo

## MVP (4–6 weeks)
P0:
- подключение к источникам market data
- new market + top mover + probability jump alerts
- simple feed + watchlist + categories
- базовый leaderboard по идеи-постам и резолвам

P1:
- whale flags
- social portfolios
- copy-ideas subscriptions

P2:
- white-label mode
- webhooks/API
- richer risk/correlation views

## Metrics
- alert open rate
- alert-to-action rate (клик в рынок/добавление в watchlist)
- D7/D30 retention
- premium conversion
- analyst follow rate
- signal precision (доля “полезных” алертов по опросам/поведению)

## Risks & mitigations
- **Signal noise**: слишком много алертов.
  - Mitigation: adaptive thresholds + user sensitivity profiles.
- **False confidence**: “сигнал = гарантия”.
  - Mitigation: вероятностный язык + risk disclaimer в каждом алерте.
- **Data quality gaps**:
  - Mitigation: multi-source checks + confidence labels.
- **Market manipulation in thin markets**:
  - Mitigation: liquidity flags, penalize low-quality markets in rankings.

## 3–6 months roadmap
- category-specific intelligence channels
- analyst reputation v2 (калибровка + stability)
- team/workspace mode for communities

## 12 months roadmap
- cross-market narrative detection
- strategy marketplace (signal providers)
- deeper B2B suite (SLA, custom compliance controls)
