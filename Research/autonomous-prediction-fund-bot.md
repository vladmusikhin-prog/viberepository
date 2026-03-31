---
title: Autonomous Prediction Fund Bot — PRD-lite
status: draft
updated: 2026-03-27
owner: Trend Researcher
---

## TL;DR
Telegram-бот “фонда прогнозов”: пользователи подписываются на стратегии, а система исполняет сделки на prediction markets (Polymarket/аналоги), публикуя **on-chain проверяемые** отчёты, риск‑метрики, лимиты и аудит‑лог прямо в Telegram.

Ключевая ставка продукта: **“proof-of-execution”** + **risk-first UX** (а не просто “сигналы”).

> Важно: это регулируемая зона. Юридическая квалификация, гео‑ограничения, KYC/AML, disclosures и маркетинговые ограничения должны быть частью MVP-дизайна.

## Problem → Opportunity
- Пользователь не может стабильно зарабатывать на prediction markets: дисциплина/ресерч/исполнение/риски.
- “Сигналы” легко подделывать: нет доказательства реальных сделок.
- Решение: **подписка на стратегии** с прозрачной историей сделок и “невозможностью нарисовать PnL”.

## Product principles (guardrails)
- **Safety defaults**: консервативные лимиты, паузы, kill switch.
- **Transparency**: всё важное имеет публичные артефакты (адреса, tx, позиции, отчёты).
- **Separation of concerns**: стратегии не могут обходить риск‑политику.
- **Compliance by design**: запрещённые юрисдикции/профили не видят продукта.

## Target users
- **B2C advanced**: трейдеры, которым важны метрики/прозрачность и автоматизация.
- **B2B**: ресерч‑команды/инфлюенсеры/фонды, которые хотят упаковать стратегии в продукт с комплаенсом и отчётностью.

## Positioning
**“Strategy-first prediction market fund in Telegram with on-chain transparency.”**

Дифференциаторы:
- proof-of-execution (tx-level)
- риск‑метрики + guardrails в интерфейсе
- explainability: “почему сделка” (ссылки на данные/новости)

## Product modes (staged rollout)
Чтобы пройти путь от идеи к live исполнению безопасно:
1) **Read-only analytics**: стратегии публикуют сигналы + backtests + on-chain “paper” записи.  
2) **Paper trading**: симуляция исполнения + отчёты/алерты.  
3) **Live execution (whitelist)**: небольшой AUM, строгие лимиты, KYC/geo gating.  
4) **Scale + B2B licensing**: white-label и/или маркетплейс стратегов.

## Telegram UX (flows)
### Subscriber (B2C)
- Browse strategies → open “strategy card” → suitability/risk disclosures → subscribe → choose risk profile → watch reports/alerts.

Основные экраны:
- **Strategy marketplace**: список стратегий + risk labels.
- **Strategy card**: цель, горизонт, комиссии, “when it loses”, лимиты, live/paper status, публичные адреса.
- **Portfolio**: allocation, текущие позиции, PnL, drawdown, risk budget.
- **Reports**: daily/weekly digest, performance attribution.
- **Alerts**: risk limits hit, pause, abnormal slippage, downtime.

### Strategist (B2B)
- Create strategy → define params → submit for risk review → publish (paper) → request live (whitelist).

### Risk admin / operator
- Approve strategy → set hard limits → monitor → pause/kill → incident log.

## Architecture (high level)
```mermaid
flowchart LR
  TG[Telegram Bot UI] --> API[Backend API]
  API --> STRAT[Strategy Engine]
  API --> RISK[Risk Policy Engine]
  STRAT -->|signals| RISK
  RISK --> EXEC[Execution Adapter]
  EXEC --> MKT[Prediction Market(s)]
  EXEC --> CHAIN[(On-chain Wallet/Contract)]
  API --> ACC[Accounting & Reporting]
  CHAIN --> ACC
  MKT --> ACC
  API --> OBS[Monitoring/Alerts]
```

## Data model (minimum)
- **User**: id, KYC status, geo, risk_profile, limits
- **Strategy**: id, owner, params, fees, status (draft/paper/live/paused), hard_limits
- **Subscription**: user_id, strategy_id, allocation, start_ts, tier
- **Order/Trade**: strategy_id, market_id, side, qty, price, slippage, tx_hash, timestamps
- **Position**: per market, avg entry, current value
- **PnL snapshot**: daily NAV, returns, drawdown
- **Audit log**: actions + hashes (optional merkle)

## Strategy model (what “a strategy” is)
Чёткая спецификация стратегии:
- **Signal generation**: rule-based / model-based
- **Universe**: какие рынки допустимы
- **Entry/exit**: условия, лимиты
- **Sizing**: из risk_budget → order size
- **Cooldown**: анти-overtrading
- **Explainability hooks**: текстовый “reason” + ссылки на данные

Примеры стратегий (MVP-friendly):
- **Momentum**: изменения вероятности + объём
- **Mean reversion**: вход против всплеска при откате

## Risk management (non-negotiable)
### Hard limits (risk policy engine)
- max position per market
- max exposure per category (e.g., politics/sports/crypto)
- max daily loss (stop trading)
- liquidity/spread thresholds
- correlation cap (группы рынков)
- slippage cap + “no trade” on anomalies

### Guardrails & controls
- **Kill switch**: мгновенная остановка исполнения (manual + auto)
- **Circuit breakers**: при проскальзывании/ошибках API/аномалиях цены
- **Two-man rule** (B2B): критические действия требуют 2 админов

### Risk metrics shown in UI
- current exposure + remaining risk budget
- realized/unrealized PnL
- drawdown + max drawdown limit
- hit rate / payoff distribution
- “tail event” exposure map

## Transparency & reporting (Telegram-native)
### What users get daily
- NAV, daily return, MTD
- top contributors (markets)
- trades executed (with tx links)
- risk events (limits hit, pauses)

### Strategy card (decision surface)
- “When it loses” (режимы/риски)
- fees + high-water mark policy
- live vs paper
- public addresses / proof links
- last 30d volatility/drawdown

## Compliance & safety checklist (MVP)
Минимум, чтобы не “сломаться” на старте:
- **Geo gating**: denylist/allowlist стран
- **KYC/AML**: хотя бы для live execution (whitelist)
- **Disclosures**: risk warnings, no guarantees, suitability gating
- **Marketing rules**: запрет “guaranteed returns”, аккуратные формулировки
- **Incident response**: runbook, pausing, уведомления

## Monetization
- **Management fee** (monthly)
- **Performance fee** (% прибыли, high-water mark)
- **Subscription tiers** (premium strategies/analytics)
- **B2B licensing**: white-label bot + reporting stack

## MVP scope (6–10 weeks) + backlog
### MVP goal
Доказать: доверие к прозрачности + работоспособность риск‑контроля + willingness-to-pay за подписку.

P0 (ship):
- 1 стратегия (простая) в paper + возможность перейти в live (whitelist)
- proof-of-execution артефакты: публичный адрес + tx links
- отчёты в Telegram: daily digest + weekly
- risk policy engine: max position, max daily loss, slippage cap, kill switch
- monitoring/alerts: downtime, failed trades, limit hits

P1:
- 2–3 стратегии + аллокация портфеля
- attribution (почему PnL такой)
- strategist console (B2B) + review workflow

P2:
- third-party strategist onboarding + рейтинг
- merkle-proof отчётов
- публичный веб-дашборд (доп. доверие)

## Validation plan
Stage 1 (paper):
- 200–500 пользователей читают отчёты/подписываются на paper
- Метрики: report open rate, subscribe conversion, churn intent, trust score

Stage 2 (small-AUM live, whitelist):
- стабильность исполнения (error rate)
- adherence к лимитам (сколько раз сработали guardrails)
- discrepancy rate (“заявлено vs on-chain факт”) ~0
- retention 4 недели + willingness-to-pay

## Key risks & mitigations
- **Regulatory**: продукт может квалифицироваться как investment management/advice.
  - Mitigation: юр‑структура, geo+KYC, disclosures, партнёрство с лицензированными провайдерами.
- **Security**: ключи/кошельки/эксплойты.
  - Mitigation: multisig, custody, лимиты, аудит, алерты.
- **Market integrity**: тонкая ликвидность/манипуляции.
  - Mitigation: liquidity thresholds, no-trade режим, slippage controls.
- **Reputation**: просадки.
  - Mitigation: честные ожидания, conservative defaults, kill switch, explainability.

## Roadmap
### 3–6 months
- 1–2 стратегии + paper→whitelist live
- risk-first UX довести до “must read”
- B2B пилоты (white-label для комьюнити)

### 12 months
- маркетплейс стратегов + стандарты листинга
- proof stack (merkle/audit)
- публичный performance dashboard
