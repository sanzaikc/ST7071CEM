from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import WebSocket


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class CrawlEventHub:
    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._subscribers: dict[str, set[WebSocket]] = {}

    async def subscribe(self, job_id: str, websocket: WebSocket) -> None:
        async with self._lock:
            self._subscribers.setdefault(job_id, set()).add(websocket)

    async def unsubscribe(self, job_id: str, websocket: WebSocket) -> None:
        async with self._lock:
            subs = self._subscribers.get(job_id)
            if not subs:
                return
            subs.discard(websocket)
            if not subs:
                self._subscribers.pop(job_id, None)

    async def publish(self, job_id: str, event: dict[str, Any]) -> None:
        async with self._lock:
            subs = list(self._subscribers.get(job_id) or [])

        if not subs:
            return

        dead: list[WebSocket] = []
        for ws in subs:
            try:
                await ws.send_json(event)
            except Exception:
                dead.append(ws)

        if dead:
            async with self._lock:
                current = self._subscribers.get(job_id)
                if not current:
                    return
                for ws in dead:
                    current.discard(ws)
                if not current:
                    self._subscribers.pop(job_id, None)


hub = CrawlEventHub()


async def emit_crawl_event(
    job_id: str,
    *,
    stage: str,
    message: str,
    level: str = "info",
    url: Optional[str] = None,
    counters: Optional[dict[str, Any]] = None,
    data: Optional[dict[str, Any]] = None,
) -> None:
    payload: dict[str, Any] = {
        "job_id": job_id,
        "ts": _now_iso(),
        "level": level,
        "stage": stage,
        "message": message,
    }
    if url:
        payload["url"] = url
    if counters:
        payload["counters"] = counters
    if data:
        payload["data"] = data
    await hub.publish(job_id, payload)

