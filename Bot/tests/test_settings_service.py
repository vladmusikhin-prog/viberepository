from src.repositories.in_memory import UserRepository
from src.services.settings_service import SettingsService


def test_settings_stats_rendered() -> None:
    repo = UserRepository()
    user = repo.get_or_create(1)
    user.categories = ["Politics"]
    user.is_live_enabled = True
    user.signals_received = 5

    text = SettingsService(repo).render_settings(1)

    assert "Получено сигналов: 5" in text
