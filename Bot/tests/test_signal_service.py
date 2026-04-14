from src.repositories.in_memory import SignalRepository, UserRepository
from src.services.signal_service import SignalService


def test_mark_signal_delivered_is_idempotent() -> None:
    user_repo = UserRepository()
    signal_repo = SignalRepository()
    service = SignalService(user_repo, signal_repo, 100000, "test_bot")

    first = service.mark_signal_delivered("s1", 1)
    second = service.mark_signal_delivered("s1", 1)

    assert first is True
    assert second is False
