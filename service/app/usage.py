from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from threading import Lock


@dataclass(frozen=True)
class UsageEvent:
    tool: str
    status: str
    result_count: int
    created_at: str


class UsageLog:
    def __init__(self) -> None:
        self._lock = Lock()
        self._events: list[UsageEvent] = []

    def record(self, *, tool: str, status: str, result_count: int = 0) -> None:
        event = UsageEvent(
            tool=tool,
            status=status,
            result_count=result_count,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        with self._lock:
            self._events.append(event)

    def recent(self, limit: int = 50) -> list[dict[str, object]]:
        with self._lock:
            events = list(self._events[-limit:])
        return [event.__dict__ for event in events]


usage_log = UsageLog()
