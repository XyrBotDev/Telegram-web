from __future__ import annotations

from collections import defaultdict

from fastapi import WebSocket


class WebSocketManager:
    """Manage active WebSocket connections."""

    def __init__(self) -> None:
        self._connections: dict[str, set[WebSocket]] = defaultdict(set)

    async def connect(
        self,
        session_id: str,
        websocket: WebSocket,
    ) -> None:
        """Accept and register a WebSocket connection."""
        await websocket.accept()

        self._connections[session_id].add(websocket)

    def disconnect(
        self,
        session_id: str,
        websocket: WebSocket,
    ) -> None:
        """Remove a WebSocket connection."""
        connections = self._connections.get(session_id)

        if not connections:
            return

        connections.discard(websocket)

        if not connections:
            self._connections.pop(session_id, None)

    async def send(
        self,
        session_id: str,
        message: dict,
    ) -> None:
        """Send a JSON message to all connections of a session."""
        connections = list(
            self._connections.get(session_id, set())
        )

        disconnected: list[WebSocket] = []

        for websocket in connections:
            try:
                await websocket.send_json(message)
            except Exception:
                disconnected.append(websocket)

        for websocket in disconnected:
            self.disconnect(session_id, websocket)

    async def broadcast(
        self,
        message: dict,
    ) -> None:
        """Broadcast a JSON message to every connected session."""
        all_connections: list[tuple[str, WebSocket]] = []

        for session_id, connections in self._connections.items():
            for websocket in connections:
                all_connections.append(
                    (session_id, websocket)
                )

        for session_id, websocket in all_connections:
            try:
                await websocket.send_json(message)
            except Exception:
                self.disconnect(
                    session_id,
                    websocket,
                )

    def connection_count(
        self,
        session_id: str | None = None,
    ) -> int:
        """Return the number of active WebSocket connections."""
        if session_id is not None:
            return len(
                self._connections.get(
                    session_id,
                    set(),
                )
            )

        return sum(
            len(connections)
            for connections in self._connections.values()
        )

    def clear_session(
        self,
        session_id: str,
    ) -> None:
        """Remove all connections for a session."""
        self._connections.pop(session_id, None)


websocket_manager = WebSocketManager()
