from src.repositories.in_memory import SignalRepository, UserRepository
from src.services.admin_service import AdminService


def test_admin_service_permissions_and_stats() -> None:
    user_repo = UserRepository()
    signal_repo = SignalRepository()

    u1 = user_repo.get_or_create(1)
    u2 = user_repo.get_or_create(2)
    u1.is_live_enabled = True
    u1.signals_received = 3
    u2.is_live_enabled = False
    u2.signals_received = 1

    assert signal_repo.mark_delivered("pm-a", 1) is True
    assert signal_repo.mark_delivered("pm-b", 1) is True
    assert signal_repo.mark_delivered("pm-b", 2) is True

    admin = AdminService(user_repo, signal_repo, admin_user_ids=(1, 99))

    assert admin.is_admin(1) is True
    assert admin.is_admin(2) is False

    text = admin.render_stats()
    assert "Total users: 2" in text
    assert "Active subscriptions: 1" in text
    assert "Delivered signals (guard): 3" in text
    assert "Signals counter sum (N): 4" in text


def test_admin_service_allows_all_when_not_configured() -> None:
    admin = AdminService(UserRepository(), SignalRepository(), admin_user_ids=())
    assert admin.is_admin(123456) is True
