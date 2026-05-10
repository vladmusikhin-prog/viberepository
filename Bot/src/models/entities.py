from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class User:
    telegram_user_id: int
    categories: List[str] = field(default_factory=list)
    is_live_enabled: bool = False
    created_at: datetime = field(default_factory=utc_now)
    signals_received: int = 0


@dataclass
class Signal:
    signal_id: str
    market: str
    side: str
    size_usd: float
    price: float
    category: str
    timestamp_utc: datetime
    is_test: bool = False
    delivered_to_user_id: Optional[int] = None
