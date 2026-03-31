---
title: Prediction Strategy Backtester Bot (B2C/B2B) — PRD-lite
status: draft
updated: 2026-03-27
owner: Trend Researcher
---

## TL;DR
Telegram-бот, который принимает стратегию на естественном языке, превращает её в формальные правила и прогоняет на исторических данных prediction markets. На выходе: performance, risk-метрики, sensitivity analysis и отчёт “где стратегия работает/ломается”.

## Problem → Opportunity
- Пользователи формулируют идеи, но не могут быстро проверить их на исторических данных.
- Большинство backtesting-инструментов сложны и не Telegram-native.
- Возможность: “describe strategy in words” → за минуты получить честный отчёт и сравнение с бенчмарками.

## Target users
- **B2C**: розничные трейдеры prediction markets.
- **B2B**: исследовательские команды, авторы сигналов, комьюнити-админы.

## Core value proposition
- **Natural language to strategy**: минимальный порог входа.
- **Transparent assumptions**: бот показывает, как интерпретировал правила.
- **Risk-first outputs**: не только return, но и drawdown, volatility, regime dependency.

## Input model (strategy DSL)
Пользователь может отправить:
- free-text правило (например, “ставить против консенсуса, когда вероятность <30% и растёт объём”)
- параметры: период, комиссии, slippage, max concurrent positions
- universe: категории рынков, min liquidity, min age

Бот строит strategy spec:
- entry condition
- exit condition
- sizing rule
- risk limits
- execution assumptions

## Backtest engine (MVP assumptions)
- event-driven симуляция по таймсрезам данных рынка
- исполнение с проскальзыванием (configurable)
- комиссии/fees включены
- no-lookahead checks (без знания будущего)
- out-of-sample split

## Outputs (what user receives)
### Performance
- cumulative return
- win rate
- avg payoff / loss
- Sharpe-like ratio (упрощённо, если применимо)

### Risk
- max drawdown
- volatility
- downside concentration
- exposure by category

### Robustness
- sensitivity to slippage/fees
- sensitivity to threshold params
- regime analysis (high-volatility vs low-volatility periods)

### Explainability
- “Top 5 profitable patterns”
- “Top 5 failure patterns”
- “When not to use this strategy”

## Telegram UX
- `/start` quick tutorial
- `/new_backtest` create run
- `/templates` popular strategies
- `/runs` history of runs
- `/compare` compare two runs
- `/export` CSV/PDF summary

Flow:
1) User submits idea  
2) Bot returns parsed strategy spec (confirm/edit)  
3) User sets assumptions (period/slippage/fees)  
4) Bot runs backtest  
5) Bot sends summary + deep report + risk warnings

## Templates (MVP)
- momentum shift
- mean reversion
- low-probability contrarian
- volume-confirmed breakout

## Monetization
- **Freemium**: лимит запусков/длины периода.
- **Pro**: advanced sensitivity analysis, multi-run compare, export.
- **Team**: shared workspace, strategy library, collaboration.
- **API tier**: интеграция в внешние пайплайны.

Pricing strawman:
- Free: 5 runs/month
- Pro: $29–$99/mo
- Team: $199–$999/mo

## MVP scope (4–8 weeks)
P0:
- parser free-text → strategy spec (с подтверждением пользователем)
- single-run backtest
- базовые метрики return/risk
- run history + simple compare

P1:
- parameter sweep (grid search light)
- robustness report
- template library

P2:
- collaborative team mode
- API access
- experiment tracking v2

## Metrics
- runs/user/week
- parse acceptance rate (пользователь согласен с интерпретацией)
- report completion rate
- pro conversion
- backtest repeat rate
- “confidence to deploy” score (опрос)

## Risks & mitigations
- **Overfitting**:
  - Mitigation: out-of-sample reports, warning badges, complexity penalty.
- **Garbage in, garbage out**:
  - Mitigation: data quality labels + assumption transparency.
- **Misinterpretation of strategy text**:
  - Mitigation: confirm step before run + editable DSL.
- **False certainty**:
  - Mitigation: explicit disclaimer “backtest is not guarantee”.

## 3–6 months roadmap
- richer DSL + composable strategy blocks
- portfolio backtesting (multi-strategy allocation)
- scenario stress testing

## 12 months roadmap
- auto strategy discovery assistants
- adaptive walk-forward optimization
- integration with live signal/fund layers (optional)
