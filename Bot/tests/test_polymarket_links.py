from src.services.polymarket_links import build_polymarket_profile_url
from src.services.texts import format_trader_name_label, format_trader_stats_block


def test_build_polymarket_profile_url_activity_tab() -> None:
    wallet = "0x56687bf447db6ffa42ffe2204a05edaa20f55839"
    assert (
        build_polymarket_profile_url(wallet)
        == f"https://polymarket.com/profile/{wallet}?tab=activity"
    )


def test_build_polymarket_profile_url_invalid_wallet() -> None:
    assert build_polymarket_profile_url("") is None
    assert build_polymarket_profile_url("0xshort") is None


def test_format_trader_name_label_html_link() -> None:
    url = "https://polymarket.com/profile/0xabc?tab=activity"
    label = format_trader_name_label(
        "VPenguin (Pastel-Push)",
        profile_url=url,
        html_mode=True,
    )
    assert label == (
        f'<a href="https://polymarket.com/profile/0xabc?tab=activity">'
        "VPenguin (Pastel-Push)</a>"
    )


def test_format_trader_stats_block_escapes_html_in_name() -> None:
    text = format_trader_stats_block(
        display_name="A & B <C>",
        wins=1,
        losses=0,
        win_rate_pct=100,
        total_realized_pnl_usd=10,
        positions_sampled=1,
        positions_limit=100,
        profile_url="https://polymarket.com/profile/0x56687bf447db6ffa42ffe2204a05edaa20f55839",
        html_mode=True,
    )
    assert "A &amp; B &lt;C&gt;" in text
