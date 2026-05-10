from __future__ import annotations

import json
import sqlite3
import threading
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from src.models.entities import Signal, User


def _parse_dt(value: Optional[str]) -> datetime:
    if not value:
        return datetime.utcnow()
    try:
        # Python 3.9: fromisoformat supports most ISO 8601 emitted strings.
        return datetime.fromisoformat(value)
    except ValueError:
        return datetime.utcnow()


class SQLiteUserRepository:
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
                CREATE TABLE IF NOT EXISTS users (
                    telegram_user_id INTEGER PRIMARY KEY,
                    categories_json TEXT NOT NULL,
                    is_live_enabled INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    signals_received INTEGER NOT NULL,
                    helpful_count INTEGER NOT NULL
                );
                """
            )
            conn.commit()

    def get_or_create(self, telegram_user_id: int) -> User:
        with self._lock, self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE telegram_user_id=?",
                (telegram_user_id,),
            ).fetchone()
            if row is None:
                now = datetime.utcnow().isoformat()
                conn.execute(
                    """
                    INSERT INTO users (
                        telegram_user_id, categories_json, is_live_enabled, created_at, signals_received, helpful_count
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (telegram_user_id, json.dumps([]), 0, now, 0, 0),
                )
                conn.commit()
                row = conn.execute(
                    "SELECT * FROM users WHERE telegram_user_id=?",
                    (telegram_user_id,),
                ).fetchone()

            assert row is not None
            return User(
                telegram_user_id=row["telegram_user_id"],
                categories=json.loads(row["categories_json"]),
                is_live_enabled=bool(row["is_live_enabled"]),
                created_at=_parse_dt(row["created_at"]),
                signals_received=int(row["signals_received"]),
            )

    def get(self, telegram_user_id: int) -> Optional[User]:
        with self._lock, self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE telegram_user_id=?",
                (telegram_user_id,),
            ).fetchone()
            if row is None:
                return None
            return User(
                telegram_user_id=row["telegram_user_id"],
                categories=json.loads(row["categories_json"]),
                is_live_enabled=bool(row["is_live_enabled"]),
                created_at=_parse_dt(row["created_at"]),
                signals_received=int(row["signals_received"]),
            )

    def update_categories(self, telegram_user_id: int, categories: List[str]) -> User:
        with self._lock, self._connect() as conn:
            now = datetime.utcnow().isoformat()
            conn.execute(
                """
                INSERT INTO users (
                    telegram_user_id, categories_json, is_live_enabled, created_at, signals_received, helpful_count
                ) VALUES (?, ?, 1, ?, 0, 0)
                ON CONFLICT(telegram_user_id) DO UPDATE SET
                    categories_json=excluded.categories_json,
                    is_live_enabled=excluded.is_live_enabled
                """,
                (telegram_user_id, json.dumps(categories), now),
            )
            conn.commit()
            return self.get_or_create(telegram_user_id)

    def set_live_enabled(self, telegram_user_id: int, enabled: bool) -> User:
        with self._lock, self._connect() as conn:
            conn.execute(
                """
                INSERT INTO users (
                    telegram_user_id, categories_json, is_live_enabled, created_at, signals_received, helpful_count
                ) VALUES (?, ?, ?, ?, 0, 0)
                ON CONFLICT(telegram_user_id) DO UPDATE SET
                    is_live_enabled=excluded.is_live_enabled
                """,
                (
                    telegram_user_id,
                    json.dumps([]),
                    1 if enabled else 0,
                    datetime.utcnow().isoformat(),
                ),
            )
            conn.commit()
            return self.get_or_create(telegram_user_id)

    def increment_signals(self, telegram_user_id: int) -> None:
        with self._lock, self._connect() as conn:
            conn.execute(
                """
                UPDATE users
                SET signals_received = signals_received + 1
                WHERE telegram_user_id=?
                """,
                (telegram_user_id,),
            )
            conn.commit()

    def all_users(self) -> List[User]:
        with self._lock, self._connect() as conn:
            rows = conn.execute("SELECT * FROM users").fetchall()
            out: List[User] = []
            for row in rows:
                out.append(
                    User(
                        telegram_user_id=row["telegram_user_id"],
                        categories=json.loads(row["categories_json"]),
                        is_live_enabled=bool(row["is_live_enabled"]),
                        created_at=_parse_dt(row["created_at"]),
                        signals_received=int(row["signals_received"]),
                    )
                )
            return out

    def debug_dump(self) -> List[dict]:
        return [asdict(u) for u in self.all_users()]


class SQLiteSignalRepository:
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
                CREATE TABLE IF NOT EXISTS signals (
                    signal_id TEXT PRIMARY KEY,
                    market TEXT,
                    side TEXT,
                    size_usd REAL,
                    price REAL,
                    category TEXT,
                    timestamp_utc TEXT,
                    is_test INTEGER NOT NULL DEFAULT 0
                );
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS delivery_guard (
                    signal_id TEXT NOT NULL,
                    user_id INTEGER NOT NULL,
                    delivered_at TEXT NOT NULL,
                    PRIMARY KEY(signal_id, user_id)
                );
                """
            )
            conn.commit()

    def save(self, signal: Signal) -> None:
        with self._lock, self._connect() as conn:
            conn.execute(
                """
                INSERT INTO signals (
                    signal_id, market, side, size_usd, price, category, timestamp_utc, is_test
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(signal_id) DO NOTHING
                """,
                (
                    signal.signal_id,
                    signal.market,
                    signal.side,
                    float(signal.size_usd),
                    float(signal.price),
                    signal.category,
                    signal.timestamp_utc.isoformat(),
                    1 if signal.is_test else 0,
                ),
            )
            conn.commit()

    def mark_delivered(self, signal_id: str, user_id: int) -> bool:
        with self._lock, self._connect() as conn:
            cur = conn.execute(
                """
                INSERT OR IGNORE INTO delivery_guard (signal_id, user_id, delivered_at)
                VALUES (?, ?, ?)
                """,
                (signal_id, user_id, datetime.utcnow().isoformat()),
            )
            conn.commit()
            return cur.rowcount == 1

    def is_delivered(self, signal_id: str, user_id: int) -> bool:
        with self._lock, self._connect() as conn:
            row = conn.execute(
                """
                SELECT 1 FROM delivery_guard
                WHERE signal_id=? AND user_id=?
                """,
                (signal_id, user_id),
            ).fetchone()
            return row is not None

    def delivered_count(self) -> int:
        with self._lock, self._connect() as conn:
            row = conn.execute("SELECT COUNT(*) as c FROM delivery_guard").fetchone()
            return int(row["c"] if row else 0)

    def signal_count(self) -> int:
        with self._lock, self._connect() as conn:
            row = conn.execute("SELECT COUNT(*) as c FROM signals").fetchone()
            return int(row["c"] if row else 0)

    def get(self, signal_id: str) -> Optional[Signal]:
        with self._lock, self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM signals WHERE signal_id=?",
                (signal_id,),
            ).fetchone()
            if row is None:
                return None
            return Signal(
                signal_id=row["signal_id"],
                market=row["market"] or "",
                side=row["side"] or "",
                size_usd=float(row["size_usd"] or 0),
                price=float(row["price"] or 0),
                category=row["category"] or "",
                timestamp_utc=_parse_dt(row["timestamp_utc"]),
                is_test=bool(row["is_test"]),
                delivered_to_user_id=None,
            )

