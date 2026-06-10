from __future__ import annotations


class TierService:
    """Free vs Pro gating for bet analytics fields."""

    def __init__(self, pro_user_ids: tuple[int, ...]) -> None:
        self._pro_ids = set(pro_user_ids)

    def is_pro(self, telegram_user_id: int) -> bool:
        return telegram_user_id in self._pro_ids
