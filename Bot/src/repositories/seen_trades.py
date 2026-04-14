from __future__ import annotations

from collections import deque
from typing import Deque, Set


class SeenTradeStore:
    """Bounded set of processed transaction hashes (Data API trades)."""

    def __init__(self, max_size: int) -> None:
        self._max_size = max(1, int(max_size))
        self._queue: Deque[str] = deque()
        self._seen: Set[str] = set()

    def try_consume(self, tx_hash: str) -> bool:
        if not tx_hash or tx_hash in self._seen:
            return False
        self._seen.add(tx_hash)
        self._queue.append(tx_hash)
        while len(self._queue) > self._max_size:
            old = self._queue.popleft()
            self._seen.discard(old)
        return True
