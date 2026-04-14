from __future__ import annotations

from dataclasses import asdict
from typing import Dict, List, Optional

from src.models.entities import Signal, User


class UserRepository:
    def __init__(self) -> None:
        self._users: Dict[int, User] = {}

    def get_or_create(self, telegram_user_id: int) -> User:
        user = self._users.get(telegram_user_id)
        if user is None:
            user = User(telegram_user_id=telegram_user_id)
            self._users[telegram_user_id] = user
        return user

    def get(self, telegram_user_id: int) -> Optional[User]:
        return self._users.get(telegram_user_id)

    def update_categories(self, telegram_user_id: int, categories: List[str]) -> User:
        user = self.get_or_create(telegram_user_id)
        user.categories = categories
        user.is_live_enabled = True
        return user

    def increment_signals(self, telegram_user_id: int) -> None:
        user = self.get_or_create(telegram_user_id)
        user.signals_received += 1

    def increment_helpful(self, telegram_user_id: int) -> None:
        user = self.get_or_create(telegram_user_id)
        user.helpful_count += 1

    def all_users(self) -> List[User]:
        return list(self._users.values())

    def debug_dump(self) -> List[dict]:
        return [asdict(user) for user in self._users.values()]


class SignalRepository:
    def __init__(self) -> None:
        self._signals: Dict[str, Signal] = {}
        self._delivery_guard: set[tuple[str, int]] = set()

    def save(self, signal: Signal) -> None:
        self._signals[signal.signal_id] = signal

    def mark_delivered(self, signal_id: str, user_id: int) -> bool:
        key = (signal_id, user_id)
        if key in self._delivery_guard:
            return False
        self._delivery_guard.add(key)
        return True

    def is_delivered(self, signal_id: str, user_id: int) -> bool:
        return (signal_id, user_id) in self._delivery_guard

    def get(self, signal_id: str) -> Optional[Signal]:
        return self._signals.get(signal_id)
