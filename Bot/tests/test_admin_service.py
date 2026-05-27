from src.models.entities import TrackedMarket, utc_now
from src.repositories.in_memory import SignalRepository, UserRepository
from src.repositories.pending_resolution_repo import InMemoryPendingResolutionRepository
from src.services.admin_service import AdminService


def test_admin_service_permissions_and_stats() -> None:
    user_repo = UserRepository()
    signal_repo = SignalRepository()
    pending_repo = InMemoryPendingResolutionRepository()

    u1 = user_repo.get_or_create(1)
    u2 = user_repo.get_or_create(2)
    u1.is_live_enabled = True
    u1.signals_received = 3
    u2.is_live_enabled = False
    u2.signals_received = 1

    assert signal_repo.mark_delivered("pm-a", 1) is True
    assert signal_repo.mark_delivered("pm-b", 1) is True
    assert signal_repo.mark_delivered("pm-b", 2) is True

    pending_repo.track_if_new(
        TrackedMarket(
            condition_id="0xopen",
            slug="open-market",
            title="Open",
            category="Politics",
            trade_side="BUY",
            outcome="Yes",
            price=0.5,
            size_usd=100_000,
            placement_signal_id="pm-tx1",
            trade_timestamp=1,
            created_at=utc_now(),
        )
    )
    resolved = TrackedMarket(
        condition_id="0xdone",
        slug="done-market",
        title="Done",
        category="Sports",
        trade_side="BUY",
        outcome="Yes",
        price=0.5,
        size_usd=50_000,
        placement_signal_id="pm-tx2",
        trade_timestamp=2,
        created_at=utc_now(),
    )
    pending_repo.track_if_new(resolved)
    pending_repo.mark_resolved(resolved.condition_id)

    admin = AdminService(user_repo, signal_repo, pending_repo, admin_user_ids=(1, 99))

    assert admin.is_admin(1) is True
    assert admin.is_admin(2) is False

    text = admin.render_stats()
    assert "Total users: 2" in text
    assert "Active subscriptions: 1" in text
    assert "Delivered signals (guard): 3" in text
    assert "Signals counter sum (N): 4" in text
    assert "Resolution pending: 1" in text
    assert "Resolution resolved: 1" in text


def test_admin_service_allows_all_when_not_configured() -> None:
    admin = AdminService(
        UserRepository(),
        SignalRepository(),
        InMemoryPendingResolutionRepository(),
        admin_user_ids=(),
    )
    assert admin.is_admin(123456) is True
