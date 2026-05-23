from src.repositories.in_memory import UserRepository
from src.services.user_service import UserService


def test_all_category_expands_to_all_categories() -> None:
    repo = UserRepository()
    service = UserService(repo)
    user = service.activate_categories(1, "All")
    assert user.categories == ["Politics", "Crypto", "Sports", "Geopolitics", "Economics"]
    assert user.is_live_enabled is True
