from __future__ import annotations

import secrets
import time
from dataclasses import dataclass
from typing import Any


@dataclass
class SessionData:
    """Temporary authenticated session information."""

    session_id: str
    telegram_session: str | bytes
    created_at: float
    last_activity: float
    metadata: dict[str, Any]


class SessionManager:
    """In-memory session manager for active Telefarm users."""

    def __init__(self, timeout: int = 3600) -> None:
        self.timeout = timeout
        self._sessions: dict[str, SessionData] = {}

    def create(
        self,
        telegram_session: str | bytes,
        metadata: dict[str, Any] | None = None,
    ) -> SessionData:
        """Create a temporary application session."""
        now = time.time()

        session_id = secrets.token_urlsafe(32)

        session = SessionData(
            session_id=session_id,
            telegram_session=telegram_session,
            created_at=now,
            last_activity=now,
            metadata=metadata or {},
        )

        self._sessions[session_id] = session

        return session

    def get(self, session_id: str) -> SessionData | None:
        """Return an active session."""
        session = self._sessions.get(session_id)

        if session is None:
            return None

        if self._is_expired(session):
            self.remove(session_id)
            return None

        session.last_activity = time.time()

        return session

    def exists(self, session_id: str) -> bool:
        """Check whether an active session exists."""
        return self.get(session_id) is not None

    def remove(self, session_id: str) -> bool:
        """Remove a temporary session."""
        session = self._sessions.pop(session_id, None)

        return session is not None

    def clear(self) -> None:
        """Remove all active sessions."""
        self._sessions.clear()

    def cleanup(self) -> int:
        """Remove expired sessions and return the number removed."""
        now = time.time()
        expired_ids = [
            session_id
            for session_id, session in self._sessions.items()
            if self._is_expired(session, now)
        ]

        for session_id in expired_ids:
            self.remove(session_id)

        return len(expired_ids)

    def count(self) -> int:
        """Return the number of currently stored sessions."""
        self.cleanup()

        return len(self._sessions)

    def update_metadata(
        self,
        session_id: str,
        values: dict[str, Any],
    ) -> bool:
        """Update metadata for an active session."""
        session = self.get(session_id)

        if session is None:
            return False

        session.metadata.update(values)

        return True

    def _is_expired(
        self,
        session: SessionData,
        now: float | None = None,
    ) -> bool:
        """Determine whether a session has expired."""
        current_time = now if now is not None else time.time()

        return (
            current_time - session.last_activity
        ) > self.timeout


session_manager = SessionManager()
