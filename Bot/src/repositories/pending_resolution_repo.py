from __future__ import annotations

import sqlite3
import threading
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from src.models.entities import TrackedMarket, utc_now


def _parse_dt(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


class InMemoryPendingResolutionRepository:
    def __init__(self) -> None:
        self._markets: dict[str, TrackedMarket] = {}

    def track_if_new(self, market: TrackedMarket) -> bool:
        if market.condition_id in self._markets:
            return False
        self._markets[market.condition_id] = market
        return True

    def list_unresolved(self, *, limit: int = 50) -> List[TrackedMarket]:
        pending = [m for m in self._markets.values() if m.resolved_at is None]
        pending.sort(key=lambda m: m.created_at)
        return pending[:limit]

    def mark_resolved(self, condition_id: str) -> None:
        tracked = self._markets.get(condition_id)
        if tracked is None:
            return
        tracked.resolved_at = utc_now()

    def count_pending(self) -> int:
        return sum(1 for m in self._markets.values() if m.resolved_at is None)

    def count_resolved(self) -> int:
        return sum(1 for m in self._markets.values() if m.resolved_at is not None)


class SQLitePendingResolutionRepository:
    def __init__(self, db_path: str) -> None:
        self._db_path = Path(db_path)
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self._db_path), timeout=30, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS pending_resolutions (
                    condition_id TEXT PRIMARY KEY,
                    slug TEXT NOT NULL,
                    title TEXT NOT NULL,
                    category TEXT NOT NULL,
                    trade_side TEXT NOT NULL,
                    outcome TEXT NOT NULL,
                    price REAL NOT NULL,
                    size_usd REAL NOT NULL,
                    placement_signal_id TEXT NOT NULL,
                    trade_timestamp INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    resolved_at TEXT
                );
                """
            )
            conn.commit()

    def _row_to_market(self, row: sqlite3.Row) -> TrackedMarket:
        return TrackedMarket(
            condition_id=row["condition_id"],
            slug=row["slug"],
            title=row["title"],
            category=row["category"],
            trade_side=row["trade_side"],
            outcome=row["outcome"],
            price=float(row["price"]),
            size_usd=float(row["size_usd"]),
            placement_signal_id=row["placement_signal_id"],
            trade_timestamp=int(row["trade_timestamp"]),
            created_at=_parse_dt(row["created_at"]) or utc_now(),
            resolved_at=_parse_dt(row["resolved_at"]),
        )

    def track_if_new(self, market: TrackedMarket) -> bool:
        with self._lock, self._connect() as conn:
            row = conn.execute(
                "SELECT 1 FROM pending_resolutions WHERE condition_id=?",
                (market.condition_id,),
            ).fetchone()
            if row is not None:
                return False
            conn.execute(
                """
                INSERT INTO pending_resolutions (
                    condition_id, slug, title, category, trade_side, outcome,
                    price, size_usd, placement_signal_id, trade_timestamp,
                    created_at, resolved_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL)
                """,
                (
                    market.condition_id,
                    market.slug,
                    market.title,
                    market.category,
                    market.trade_side,
                    market.outcome,
                    market.price,
                    market.size_usd,
                    market.placement_signal_id,
                    market.trade_timestamp,
                    market.created_at.isoformat(),
                ),
            )
            conn.commit()
            return True

    def list_unresolved(self, *, limit: int = 50) -> List[TrackedMarket]:
        with self._lock, self._connect() as conn:
            rows = conn.execute(
                """
                SELECT * FROM pending_resolutions
                WHERE resolved_at IS NULL
                ORDER BY created_at ASC
                LIMIT ?
                """,
                (max(1, limit),),
            ).fetchall()
            return [self._row_to_market(row) for row in rows]

    def mark_resolved(self, condition_id: str) -> None:
        with self._lock, self._connect() as conn:
            conn.execute(
                """
                UPDATE pending_resolutions
                SET resolved_at=?
                WHERE condition_id=? AND resolved_at IS NULL
                """,
                (utc_now().isoformat(), condition_id),
            )
            conn.commit()

    def count_pending(self) -> int:
        with self._lock, self._connect() as conn:
            row = conn.execute(
                "SELECT COUNT(*) AS c FROM pending_resolutions WHERE resolved_at IS NULL"
            ).fetchone()
            return int(row["c"]) if row else 0

    def count_resolved(self) -> int:
        with self._lock, self._connect() as conn:
            row = conn.execute(
                "SELECT COUNT(*) AS c FROM pending_resolutions WHERE resolved_at IS NOT NULL"
            ).fetchone()
            return int(row["c"]) if row else 0
