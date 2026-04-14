from src.repositories.in_memory import UserRepository


class UserService:
    def __init__(self, user_repo: UserRepository) -> None:
        self.user_repo = user_repo

    def ensure_user(self, user_id: int):
        return self.user_repo.get_or_create(user_id)

    def activate_categories(self, user_id: int, category: str):
        categories = ["Politics", "Crypto", "Sports"] if category == "All" else [category]
        return self.user_repo.update_categories(user_id, categories)

    def disable_live(self, user_id: int):
        user = self.user_repo.get_or_create(user_id)
        user.is_live_enabled = False
        return user
