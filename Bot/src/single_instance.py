"""One running bot process per Bot/ checkout (POSIX file lock)."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)


class SingleInstanceLock:
    """Exclusive non-blocking flock on a file under Bot/data/."""

    def __init__(self, lock_path: Path) -> None:
        self._path = lock_path
        self._fp = None

    def acquire(self) -> None:
        try:
            import fcntl
        except ImportError:
            logger.warning("fcntl unavailable; skipping single-instance lock (non-POSIX OS)")
            return

        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._fp = open(self._path, "a+", encoding="utf-8")
        try:
            fcntl.flock(self._fp.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            self._fp.close()
            self._fp = None
            logger.error(
                "Уже запущен другой экземпляр бота (lock: %s). Останови процесс: "
                "pgrep -fl src.main  →  kill <PID>  или  pkill -f 'python -m src.main' из каталога Bot/.",
                self._path,
            )
            print(
                f"ERROR: Уже запущен другой экземпляр бота. Lock: {self._path}",
                file=sys.stderr,
            )
            sys.exit(1)
        self._fp.seek(0)
        self._fp.truncate()
        self._fp.write(str(__import__("os").getpid()))
        self._fp.flush()

    def release(self) -> None:
        if self._fp is None:
            return
        try:
            import fcntl

            fcntl.flock(self._fp.fileno(), fcntl.LOCK_UN)
        except OSError:
            pass
        try:
            self._fp.close()
        except OSError:
            pass
        self._fp = None

    def __enter__(self) -> "SingleInstanceLock":
        self.acquire()
        return self

    def __exit__(self, *args: object) -> None:
        self.release()
