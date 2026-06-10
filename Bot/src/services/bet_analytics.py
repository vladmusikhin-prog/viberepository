from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class OddsBucket(str, Enum):
    HIGH_CERTAINTY = "high_certainty"
    MID = "mid"
    LONGSHOT = "longshot"


class SkillHintKey(str, Enum):
    INSUFFICIENT = "insufficient"
    GRINDER = "grinder"
    MIXED = "mixed"
    BALANCED = "balanced"


class SignalStrength(str, Enum):
    STRONG = "strong"
    NOTABLE = "notable"
    WEAK = "weak"


MIN_BASELINE_SAMPLES = 5
MIN_TRADER_HISTORY = 10
HIGH_CERTAINTY_PRICE = 0.90
LONGSHOT_PRICE = 0.25
GRINDER_HIGH_CERTAINTY_PCT = 60


@dataclass(frozen=True)
class MarketAnomaly:
    typical_trade_usd: float
    anomaly_ratio: float
    sample_n: int


@dataclass(frozen=True)
class TradeContext:
    entry_price: float
    odds_bucket: OddsBucket
    implied_pct: int
    coefficient_multiplier: float
    hours_to_resolution: Optional[float]
    is_flash: bool


@dataclass(frozen=True)
class SignalVerdict:
    strength: SignalStrength
    reason: str
    label_ru: str


def classify_odds_bucket(price: float) -> OddsBucket:
    if price > HIGH_CERTAINTY_PRICE:
        return OddsBucket.HIGH_CERTAINTY
    if price < LONGSHOT_PRICE:
        return OddsBucket.LONGSHOT
    return OddsBucket.MID


def build_trade_context(
    *,
    entry_price: float,
    hours_to_resolution: Optional[float],
    flash_hours_threshold: float = 24.0,
) -> TradeContext:
    price = max(0.0, min(entry_price, 1.0))
    implied_pct = round(price * 100)
    coef = round(1.0 / price, 1) if price > 0 else 0.0
    is_flash = hours_to_resolution is not None and 0 < hours_to_resolution <= flash_hours_threshold
    return TradeContext(
        entry_price=price,
        odds_bucket=classify_odds_bucket(price),
        implied_pct=implied_pct,
        coefficient_multiplier=coef,
        hours_to_resolution=hours_to_resolution,
        is_flash=is_flash,
    )


def compute_market_anomaly(
    *,
    trade_size_usd: float,
    market_sizes_usd: list[float],
    min_samples: int = MIN_BASELINE_SAMPLES,
) -> Optional[MarketAnomaly]:
    sizes = sorted(s for s in market_sizes_usd if s > 0)
    if len(sizes) < min_samples:
        return None
    mid = len(sizes) // 2
    p50 = sizes[mid] if len(sizes) % 2 else (sizes[mid - 1] + sizes[mid]) / 2
    if p50 <= 0:
        return None
    return MarketAnomaly(
        typical_trade_usd=p50,
        anomaly_ratio=trade_size_usd / p50,
        sample_n=len(sizes),
    )


def derive_skill_hint(
    *,
    positions_sampled: int,
    high_certainty_pct: int,
) -> tuple[SkillHintKey, str]:
    if positions_sampled < MIN_TRADER_HISTORY:
        return SkillHintKey.INSUFFICIENT, "Недостаточно истории"
    if high_certainty_pct >= GRINDER_HIGH_CERTAINTY_PCT:
        return SkillHintKey.GRINDER, f"Часто входит на высокой вероятности ({high_certainty_pct}% ставок >85%)"
    if high_certainty_pct <= 30:
        return SkillHintKey.MIXED, "Смешанные исходы (много longshot/mid)"
    return SkillHintKey.BALANCED, "Сбалансированный профиль входов"


def compute_signal_verdict(
    *,
    anomaly: Optional[MarketAnomaly],
    trade_ctx: TradeContext,
    skill_hint_key: SkillHintKey,
) -> SignalVerdict:
    ratio = anomaly.anomaly_ratio if anomaly else 0.0

    if ratio >= 5 and skill_hint_key != SkillHintKey.GRINDER and (
        trade_ctx.odds_bucket != OddsBucket.HIGH_CERTAINTY or ratio >= 10
    ):
        return SignalVerdict(
            strength=SignalStrength.STRONG,
            reason="крупная аномалия + профиль не grinder",
            label_ru="СИЛЬНЫЙ",
        )

    if ratio >= 2 or (
        skill_hint_key == SkillHintKey.MIXED and trade_ctx.entry_price < 0.40
    ):
        return SignalVerdict(
            strength=SignalStrength.NOTABLE,
            reason="аномалия рынка или интересный профиль входа",
            label_ru="ЗАМЕТНЫЙ",
        )

    return SignalVerdict(
        strength=SignalStrength.WEAK,
        reason="типичный размер или низкий edge",
        label_ru="СЛАБЫЙ",
    )


def format_anomaly_line(anomaly: MarketAnomaly, *, brief: bool) -> str:
    if brief:
        return f"📊 Рынок: ≈{anomaly.anomaly_ratio:.0f}× типичной сделки"
    return (
        f"📊 Рынок: типичная ~${anomaly.typical_trade_usd:,.0f} · "
        f"эта ${anomaly.anomaly_ratio:.0f}× выше (n={anomaly.sample_n})"
    )


def format_trade_context_line(ctx: TradeContext, *, pro: bool) -> str:
    bucket_labels = {
        OddsBucket.HIGH_CERTAINTY: "высокая вероятность",
        OddsBucket.MID: "средняя вероятность",
        OddsBucket.LONGSHOT: "маловероятный исход",
    }
    base = (
        f"🎲 Вход: ~{ctx.implied_pct}% ({bucket_labels[ctx.odds_bucket]}), "
        f"коэф. ~{ctx.coefficient_multiplier}×"
    )
    if not pro:
        return base
    flash = " · flash (<24ч)" if ctx.is_flash else ""
    if ctx.hours_to_resolution is not None and ctx.hours_to_resolution > 0:
        hrs = int(ctx.hours_to_resolution)
        return f"{base}\n⏳ До закрытия: ~{hrs} ч{flash}"
    return base
