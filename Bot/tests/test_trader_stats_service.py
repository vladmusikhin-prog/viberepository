from src.services.signal_service import SignalService
from src.services.trader_stats_service import (
    TraderStats,
    compute_trader_stats,
    format_trader_display_name,
)
from src.services.texts import format_trader_stats_block
from src.repositories.in_memory import SignalRepository, UserRepository


def test_format_trader_display_name_both() -> None:
    trade = {"name": "VPenguin", "pseudonym": "Pastel-Push", "proxyWallet": "0xabc"}
    assert format_trader_display_name(trade) == "VPenguin (Pastel-Push)"


def test_format_trader_display_name_pseudonym_only() -> None:
    trade = {"name": "", "pseudonym": "Pastel-Push", "proxyWallet": "0xabc"}
    assert format_trader_display_name(trade) == "Pastel-Push"


def test_compute_trader_stats_zero_closed() -> None:
    stats = compute_trader_stats([], display_name="New Whale")
    assert stats.wins == 0
    assert stats.losses == 0
    assert stats.win_rate_pct == 0
    assert stats.total_realized_pnl_usd == 0.0
    assert stats.positions_sampled == 0


def test_compute_trader_stats_mixed() -> None:
    positions = [
        {"realizedPnl": 1000},
        {"realizedPnl": -200},
        {"realizedPnl": 500},
        {"realizedPnl": 0},
    ]
    stats = compute_trader_stats(positions, display_name="VPenguin (Pastel-Push)")
    assert stats.wins == 2
    assert stats.losses == 1
    assert stats.win_rate_pct == 67
    assert stats.total_realized_pnl_usd == 1300
    assert stats.positions_sampled == 4


def test_format_trader_stats_block_zero_zero() -> None:
    text = format_trader_stats_block(
        display_name="VPenguin (Pastel-Push)",
        wins=0,
        losses=0,
        win_rate_pct=0,
        total_realized_pnl_usd=0.0,
        positions_sampled=0,
        positions_limit=100,
    )
    assert "WR: 0% (0/0" in text
    assert "VPenguin (Pastel-Push)" in text
    assert "+$0" in text


def test_build_alert_includes_trader_stats() -> None:
    service = SignalService(UserRepository(), SignalRepository(), 100_000, 20_000, 75_000, "bot", 100)
    stats = TraderStats(
        display_name="VPenguin (Pastel-Push)",
        wins=3,
        losses=1,
        win_rate_pct=75,
        total_realized_pnl_usd=250_000,
        positions_sampled=4,
    )
    _signal_id, text, _url = service.build_polymarket_trade_alert(
        {
            "transactionHash": "0x1",
            "title": "Test market",
            "side": "BUY",
            "outcome": "Yes",
            "size": 100000,
            "price": 0.5,
            "timestamp": 1_700_000_000,
        },
        "Crypto",
        1,
        trader_stats=stats,
    )
    assert "WR: 75% (3/4" in text
    assert "VPenguin (Pastel-Push)" in text
    assert "+$250,000" in text
