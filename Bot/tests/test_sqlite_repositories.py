import os
from pathlib import Path

from src.repositories.sqlite_repo import SQLiteSignalRepository, SQLiteUserRepository


def test_sqlite_user_repo_persists_state(tmp_path: Path) -> None:
    db_path = str(tmp_path / "bot.sqlite3")
    user_repo = SQLiteUserRepository(db_path)

    u = user_repo.get_or_create(1)
    assert u.is_live_enabled is False
    assert u.categories == []

    user_repo.update_categories(1, ["Sports"])
    u2 = user_repo.get_or_create(1)
    assert u2.is_live_enabled is True
    assert u2.categories == ["Sports"]

    user_repo.set_live_enabled(1, False)
    u3 = user_repo.get_or_create(1)
    assert u3.is_live_enabled is False


def test_sqlite_signal_delivery_guard(tmp_path: Path) -> None:
    db_path = str(tmp_path / "bot.sqlite3")
    signal_repo = SQLiteSignalRepository(db_path)

    assert signal_repo.is_delivered("pm-x", 10) is False
    assert signal_repo.mark_delivered("pm-x", 10) is True
    assert signal_repo.is_delivered("pm-x", 10) is True
    assert signal_repo.mark_delivered("pm-x", 10) is False

    assert signal_repo.delivered_count() == 1

