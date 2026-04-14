from datetime import datetime, timezone
from typing import Optional

from src.repositories.in_memory import UserRepository


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


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

    def seconds_since_last_demo_live(self, user_id: int) -> Optional[float]:
        user = self.user_repo.get_or_create(user_id)
        if user.last_demo_live_sent_at is None:
            return None
        return (_utc_now() - user.last_demo_live_sent_at).total_seconds()

    def mark_demo_live_sent(self, user_id: int) -> None:
        user = self.user_repo.get_or_create(user_id)
        user.last_demo_live_sent_at = _utc_now()
