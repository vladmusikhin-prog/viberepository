from src.services.category_mapper import ALL_PRODUCT_CATEGORIES


class UserService:
    def __init__(self, user_repo) -> None:
        self.user_repo = user_repo

    def ensure_user(self, user_id: int):
        return self.user_repo.get_or_create(user_id)

    def activate_categories(self, user_id: int, category: str):
        """Legacy single-tap flow; prefer set_categories for multi-select."""
        if category == "All":
            categories = list(ALL_PRODUCT_CATEGORIES)
        else:
            categories = [category]
        return self.set_categories(user_id, categories)

    def set_categories(self, user_id: int, categories: list[str]) -> object:
        unique = []
        for name in categories:
            if name not in ALL_PRODUCT_CATEGORIES:
                raise ValueError(f"Unknown category: {name}")
            if name not in unique:
                unique.append(name)
        if not unique:
            raise ValueError("At least one category is required")
        ordered = [c for c in ALL_PRODUCT_CATEGORIES if c in unique]
        return self.user_repo.update_categories(user_id, ordered)

    def disable_live(self, user_id: int):
        # Keep persistence logic in repository implementation.
        return self.user_repo.set_live_enabled(user_id, False)
