import pytest

from src.models.entities import TrackedMarket
from src.repositories.pending_resolution_repo import InMemoryPendingResolutionRepository
from src.services.resolution_service import MarketResolution, ResolutionService


@pytest.fixture
def service() -> ResolutionService:
    return ResolutionService(InMemoryPendingResolutionRepository())


def test_track_whale_trade_once_per_condition(service: ResolutionService) -> None:
    trade = {
        "conditionId": "0xabc",
        "slug": "market-slug",
        "title": "Test market",
        "side": "BUY",
        "outcome": "Yes",
        "price": 0.4,
        "size": 100000,
        "timestamp": 1_700_000_000,
        "transactionHash": "0xtx1",
    }
    assert service.track_whale_trade(trade, "Politics", "pm-0xtx1") is True
    assert service.track_whale_trade(trade, "Politics", "pm-0xtx1") is False


def test_parse_market_resolution_winner(service: ResolutionService) -> None:
    market = {
        "closed": True,
        "umaResolutionStatus": "resolved",
        "outcomes": '["Team A", "Team B"]',
        "outcomePrices": '["0", "1"]',
        "closedTime": "2026-05-23 15:00:00+00",
    }
    resolution = service.parse_market_resolution(market)
    assert resolution is not None
    assert resolution.winning_outcome == "Team B"
    assert resolution.is_split is False


def test_parse_market_resolution_split(service: ResolutionService) -> None:
    market = {
        "closed": True,
        "outcomes": '["Odd", "Even"]',
        "outcomePrices": '["0.5", "0.5"]',
    }
    resolution = service.parse_market_resolution(market)
    assert resolution is not None
    assert resolution.is_split is True


def test_assess_buy_win(service: ResolutionService) -> None:
    tracked = TrackedMarket(
        condition_id="0x1",
        slug="s",
        title="T",
        category="Sports",
        trade_side="BUY",
        outcome="Yes",
        price=0.5,
        size_usd=100_000,
        placement_signal_id="pm-tx",
        trade_timestamp=1,
    )
    resolution = MarketResolution(
        winning_outcome="Yes",
        is_split=False,
        closed_time=None,
    )
    assessment = service.assess_whale_outcome(tracked, resolution)
    assert assessment.result == "win"
    assert assessment.pnl_usd == pytest.approx(100_000)


def test_assess_buy_loss(service: ResolutionService) -> None:
    tracked = TrackedMarket(
        condition_id="0x1",
        slug="s",
        title="T",
        category="Sports",
        trade_side="BUY",
        outcome="Yes",
        price=0.5,
        size_usd=100_000,
        placement_signal_id="pm-tx",
        trade_timestamp=1,
    )
    resolution = MarketResolution(
        winning_outcome="No",
        is_split=False,
        closed_time=None,
    )
    assessment = service.assess_whale_outcome(tracked, resolution)
    assert assessment.result == "loss"
    assert assessment.pnl_usd == pytest.approx(-100_000)


def test_build_resolution_alert_contains_outcome(service: ResolutionService) -> None:
    tracked = TrackedMarket(
        condition_id="0xcond",
        slug="s",
        title="Who wins?",
        category="Politics",
        trade_side="BUY",
        outcome="Alice",
        price=0.45,
        size_usd=250_000,
        placement_signal_id="pm-tx",
        trade_timestamp=1,
    )
    resolution = MarketResolution(
        winning_outcome="Alice",
        is_split=False,
        closed_time="2026-05-23 12:00 UTC",
    )
    signal_id, text = service.build_resolution_alert(tracked, resolution)
    assert signal_id == "pm-res-0xcond"
    assert "ВЫИГРЫШ" in text
    assert "Alice" in text
    assert "Who wins?" in text
