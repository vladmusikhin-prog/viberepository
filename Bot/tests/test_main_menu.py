from src.services.keyboards import main_menu_active_keyboard, main_menu_keyboard, settings_keyboard
from src.services.settings_service import SettingsService
from src.repositories.in_memory import UserRepository


def _callback_data(keyboard) -> list[str]:
    return [
        button.callback_data
        for row in keyboard.inline_keyboard
        for button in row
    ]


def test_main_menu_active_has_deactivate_and_change_category() -> None:
    data = _callback_data(main_menu_active_keyboard())
    assert "activate" in data
    assert "disable_live" in data


def test_main_menu_inactive_shows_activate_only() -> None:
    data = _callback_data(main_menu_keyboard(False))
    assert data == ["activate"]


def test_settings_keyboard_respects_live_flag() -> None:
    active = _callback_data(settings_keyboard(True))
    inactive = _callback_data(settings_keyboard(False))
    assert "disable_live" in active
    assert "disable_live" not in inactive
    assert "activate" in inactive


def test_render_main_menu_active_user() -> None:
    repo = UserRepository()
    user = repo.get_or_create(1)
    user.categories = ["Sports"]
    user.is_live_enabled = True
    text = SettingsService(repo).render_main_menu(1)
    assert "уведомления включены" in text
    assert "Sports" in text


def test_render_main_menu_inactive_user() -> None:
    repo = UserRepository()
    repo.get_or_create(1)
    text = SettingsService(repo).render_main_menu(1)
    assert "выключены" in text
