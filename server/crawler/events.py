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
        self._history: dict[str, list[dict[str, Any]]] = {}

    async def subscribe(self, job_id: str, websocket: WebSocket) -> None:
        async with self._lock:
            self._subscribers.setdefault(job_id, set()).add(websocket)
            # Send history to new subscriber
            if job_id in self._history:
                for event in self._history[job_id]:
                    try:
                        await websocket.send_json(event)
                    except Exception:
                        pass

    async def unsubscribe(self, job_id: str, websocket: WebSocket) -> None:
        async with self._lock:
            subs = self._subscribers.get(job_id)
            if not subs:
                return
            subs.discard(websocket)
            if not subs:
                self._subscribers.pop(job_id, None)
                # Note: We keep history for a while so reloads work

    async def publish(self, job_id: str, event: dict[str, Any]) -> None:
        async with self._lock:
            # Store in history
            if job_id not in self._history:
                self._history[job_id] = []
            self._history[job_id].append(event)
            # Keep last 500 events per job
            if len(self._history[job_id]) > 500:
                self._history[job_id] = self._history[job_id][-500:]

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

