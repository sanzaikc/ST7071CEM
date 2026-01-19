from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from collections import OrderedDict


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class CacheEntry:
    value: Any
    expires_at: datetime


class TTLCache:
    def __init__(self, *, max_entries: int, ttl_s: int):
        self._store: OrderedDict[str, CacheEntry] = OrderedDict()
        self._max_entries = max_entries
        self._ttl = timedelta(seconds=ttl_s)

    def get(self, key: str) -> Optional[Any]:
        entry = self._store.get(key)
        if not entry:
            return None
        if entry.expires_at <= _utcnow():
            self._store.pop(key, None)
            return None
        self._store.move_to_end(key)
        return entry.value

    def set(self, key: str, value: Any) -> None:
        self._store[key] = CacheEntry(value=value, expires_at=_utcnow() + self._ttl)
        self._store.move_to_end(key)
        while len(self._store) > self._max_entries:
            self._store.popitem(last=False)

