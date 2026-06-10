from src.services.bet_analytics import (
    MarketAnomaly,
    OddsBucket,
    SignalStrength,
    SkillHintKey,
    build_trade_context,
    classify_odds_bucket,
    compute_market_anomaly,
    compute_signal_verdict,
    derive_skill_hint,
    format_anomaly_line,
    format_trade_context_line,
)


def test_classify_odds_bucket() -> None:
    assert classify_odds_bucket(0.95) == OddsBucket.HIGH_CERTAINTY
    assert classify_odds_bucket(0.50) == OddsBucket.MID
    assert classify_odds_bucket(0.10) == OddsBucket.LONGSHOT


def test_compute_market_anomaly_insufficient_samples() -> None:
    assert compute_market_anomaly(trade_size_usd=1000, market_sizes_usd=[100, 200]) is None


def test_compute_market_anomaly_ratio() -> None:
    anomaly = compute_market_anomaly(
        trade_size_usd=50_000,
        market_sizes_usd=[1000, 2000, 3000, 4000, 5000],
    )
    assert anomaly is not None
    assert anomaly.typical_trade_usd == 3000
    assert round(anomaly.anomaly_ratio, 1) == 16.7


def test_build_trade_context_flash() -> None:
    ctx = build_trade_context(entry_price=0.34, hours_to_resolution=6.0)
    assert ctx.implied_pct == 34
    assert ctx.odds_bucket == OddsBucket.MID
    assert ctx.is_flash is True


def test_derive_skill_hint_grinder() -> None:
    key, text = derive_skill_hint(positions_sampled=20, high_certainty_pct=70)
    assert key == SkillHintKey.GRINDER
    assert "85%" in text


def test_compute_signal_verdict_strong() -> None:
    anomaly = MarketAnomaly(typical_trade_usd=10_000, anomaly_ratio=8.0, sample_n=20)
    trade_ctx = build_trade_context(entry_price=0.34, hours_to_resolution=48.0)
    verdict = compute_signal_verdict(
        anomaly=anomaly,
        trade_ctx=trade_ctx,
        skill_hint_key=SkillHintKey.MIXED,
    )
    assert verdict.strength == SignalStrength.STRONG


def test_compute_signal_verdict_notable_longshot() -> None:
    trade_ctx = build_trade_context(entry_price=0.20, hours_to_resolution=None)
    verdict = compute_signal_verdict(
        anomaly=None,
        trade_ctx=trade_ctx,
        skill_hint_key=SkillHintKey.MIXED,
    )
    assert verdict.strength == SignalStrength.NOTABLE


def test_format_anomaly_line_brief() -> None:
    anomaly = MarketAnomaly(typical_trade_usd=12_000, anomaly_ratio=17.0, sample_n=30)
    assert "≈17×" in format_anomaly_line(anomaly, brief=True)


def test_format_trade_context_line_pro_timing() -> None:
    ctx = build_trade_context(entry_price=0.08, hours_to_resolution=5.0)
    text = format_trade_context_line(ctx, pro=True)
    assert "8%" in text
    assert "До закрытия" in text
    assert "flash" in text
