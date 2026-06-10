from src.services.bet_analytics import SkillHintKey
from src.services.bet_analytics_service import BetAnalyticsBundle
from src.services.bet_analytics import (
    MarketAnomaly,
    SignalStrength,
    SignalVerdict,
    TradeContext,
    OddsBucket,
    build_trade_context,
)
from src.services.signal_service import SignalService
from src.services.trader_stats_service import TraderStats, compute_trader_stats
from src.repositories.in_memory import SignalRepository, UserRepository


def test_compute_trader_stats_extended_fields() -> None:
    positions = [{"realizedPnl": 100, "timestamp": 1_700_000_000 + i * 1000} for i in range(12)]
    positions[1]["realizedPnl"] = -500
    trades = [
        {"price": 0.92, "timestamp": 1_700_000_000},
        {"price": 0.93, "timestamp": 1_700_050_000},
        {"price": 0.30, "timestamp": 1_700_100_000},
    ]
    stats = compute_trader_stats(
        positions,
        display_name="Whale",
        user_trades=trades,
    )
    assert stats.wins_usd > 0
    assert stats.losses_usd == 500
    assert stats.high_certainty_pct == 67
    assert stats.skill_hint_key == SkillHintKey.GRINDER


def test_build_alert_includes_bet_analytics() -> None:
    service = SignalService(UserRepository(), SignalRepository(), 100_000, 20_000, 75_000, "bot", 100)
    trade_ctx = build_trade_context(entry_price=0.34, hours_to_resolution=6.0)
    bundle = BetAnalyticsBundle(
        verdict=SignalVerdict(
            strength=SignalStrength.NOTABLE,
            reason="test",
            label_ru="ЗАМЕТНЫЙ",
        ),
        trade_context=trade_ctx,
        anomaly=MarketAnomaly(typical_trade_usd=15_000, anomaly_ratio=17.0, sample_n=40),
        trader_stats=None,
        is_pro=False,
        skill_hint_key=SkillHintKey.INSUFFICIENT,
    )
    _signal_id, text, _url, _use_html = service.build_polymarket_trade_alert(
        {
            "transactionHash": "0x2",
            "title": "Spread Ukraine (-1.5)",
            "side": "BUY",
            "outcome": "Ukraine",
            "size": 252_000,
            "price": 0.34,
            "timestamp": 1_700_000_000,
        },
        "Geopolitics",
        1,
        bet_analytics=bundle,
    )
    assert "Сила сигнала: ЗАМЕТНЫЙ" in text
    assert "≈17×" in text
    assert "~34%" in text
    assert "коэф." in text


def test_build_alert_pro_trader_stats_block() -> None:
    service = SignalService(UserRepository(), SignalRepository(), 100_000, 20_000, 75_000, "bot", 100)
    stats = TraderStats(
        display_name="VPenguin (Pastel-Push)",
        wins=60,
        losses=24,
        win_rate_pct=71,
        total_realized_pnl_usd=420_000,
        positions_sampled=84,
        wins_usd=500_000,
        losses_usd=80_000,
        trades_per_month=12.5,
        high_certainty_pct=20,
        avg_entry_price=0.45,
        period_days=60,
        skill_hint_key=SkillHintKey.MIXED,
        skill_hint_text="Смешанные исходы (много longshot/mid)",
    )
    bundle = BetAnalyticsBundle(
        verdict=SignalVerdict(
            strength=SignalStrength.STRONG,
            reason="test",
            label_ru="СИЛЬНЫЙ",
        ),
        trade_context=build_trade_context(entry_price=0.08, hours_to_resolution=5.0),
        anomaly=MarketAnomaly(typical_trade_usd=15_000, anomaly_ratio=17.0, sample_n=40),
        trader_stats=stats,
        is_pro=True,
        skill_hint_key=SkillHintKey.MIXED,
    )
    _signal_id, text, _url, use_html = service.build_polymarket_trade_alert(
        {
            "transactionHash": "0x3",
            "title": "Test",
            "side": "BUY",
            "outcome": "Yes",
            "size": 252_000,
            "price": 0.08,
            "timestamp": 1_700_000_000,
            "proxyWallet": "0x56687bf447db6ffa42ffe2204a05edaa20f55839",
        },
        "Geopolitics",
        1,
        trader_stats=stats,
        bet_analytics=bundle,
    )
    assert use_html is True
    assert "84 закрытых / 60д" in text
    assert "Смешанные исходы" in text
    assert "До закрытия" in text
