from __future__ import annotations

from collections import defaultdict
from typing import Any, Awaitable, Callable


EventHandler = Callable[..., Awaitable[None]]


class EventManager:
    """Central event manager for Telefarm real-time events."""

    def __init__(self) -> None:
        self._handlers: dict[str, list[EventHandler]] = defaultdict(list)

    def on(
        self,
        event_name: str,
        handler: EventHandler,
    ) -> None:
        """Register an asynchronous event handler."""
        if handler not in self._handlers[event_name]:
            self._handlers[event_name].append(handler)

    def off(
        self,
        event_name: str,
        handler: EventHandler,
    ) -> None:
        """Remove a registered event handler."""
        handlers = self._handlers.get(event_name)

        if not handlers:
            return

        if handler in handlers:
            handlers.remove(handler)

        if not handlers:
            self._handlers.pop(event_name, None)

    async def emit(
        self,
        event_name: str,
        **payload: Any,
    ) -> None:
        """Emit an event to all registered handlers."""
        handlers = list(
            self._handlers.get(event_name, [])
        )

        for handler in handlers:
            await handler(**payload)

    def clear(self, event_name: str | None = None) -> None:
        """Clear handlers for one event or all events."""
        if event_name is None:
            self._handlers.clear()
            return

        self._handlers.pop(event_name, None)

    def registered_events(self) -> list[str]:
        """Return all registered event names."""
        return list(self._handlers.keys())


event_manager = EventManager()
