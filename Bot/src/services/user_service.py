from src.services.category_mapper import ALL_PRODUCT_CATEGORIES


class UserService:
    def __init__(self, user_repo) -> None:
        self.user_repo = user_repo

    def ensure_user(self, user_id: int):
        return self.user_repo.get_or_create(user_id)

    def activate_categories(self, user_id: int, category: str):
        categories = list(ALL_PRODUCT_CATEGORIES) if category == "All" else [category]
        return self.user_repo.update_categories(user_id, categories)

    def disable_live(self, user_id: int):
        # Keep persistence logic in repository implementation.
        return self.user_repo.set_live_enabled(user_id, False)
