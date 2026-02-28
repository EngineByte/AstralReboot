from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Deque, Dict, List, Optional, Type, TypeVar
from collections import deque

T = TypeVar("T")
Handler = Callable[[Any], None]


class EventBus:
    def __init__(self) -> None:
        self._handlers: Dict[Type[Any], List[Handler]] = {}
        self._queue: Deque[Any] = deque()

    def on(self, event_type: Type[Any], handler: Handler) -> None:
        self._handlers.setdefault(event_type, []).append(handler)

    def off(self, event_type: Type[Any], handler: Handler) -> bool:
        lst = self._handlers.get(event_type)
        if not lst:
            return False
        try:
            lst.remove(handler)
            return True
        except ValueError:
            return False

    def emit(self, event: Any) -> None:
        self._queue.append(event)

    def emit_now(self, event: Any) -> None:
        self._dispatch(event)

    def flush(self, max_events: Optional[int] = None) -> int:
        dispatched = 0
        while self._queue and (max_events is None or dispatched < max_events):
            ev = self._queue.popleft()
            self._dispatch(ev)
            dispatched += 1
        return dispatched

    def _dispatch(self, event: Any) -> None:
        et = type(event)
        handlers = self._handlers.get(et)
        if not handlers:
            return
        for h in list(handlers):
            h(event)

    def clear(self) -> None:
        self._queue.clear()
        self._handlers.clear()

    def stats(self) -> Dict[str, Any]:
        return {
            "queued": len(self._queue),
            "event_types": {k.__name__: len(v) for k, v in self._handlers.items()},
        }