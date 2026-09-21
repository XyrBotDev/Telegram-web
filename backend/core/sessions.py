from __future__ import annotations

import secrets
import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class SessionData:
    """Temporary Telefarm application session."""

    session_id: str
    telegram_session: str | bytes | None
    created_at: float
    last_activity: float
    metadata: dict[str, Any] = field(default_factory=dict)


class SessionManager:
    """Manage temporary in-memory Telefarm sessions."""

    def __init__(self, timeout: int = 3600) -> None:
        self.timeout = timeout
        self._sessions: dict[str, SessionData] = {}

    def create(
        self,
        telegram_session: str | bytes | None = None,
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

    def get(
        self,
        session_id: str,
    ) -> SessionData | None:
        """Return an active session."""
        session = self._sessions.get(session_id)

        if session is None:
            return None

        if self._is_expired(session):
            self.remove(session_id)
            return None

        session.last_activity = time.time()

        return session

    def exists(
        self,
        session_id: str,
    ) -> bool:
        """Check whether an active session exists."""
        return self.get(session_id) is not None

    def remove(
        self,
        session_id: str,
    ) -> bool:
        """Remove a temporary session."""
        session = self._sessions.pop(
            session_id,
            None,
        )

        return session is not None

    def clear(self) -> None:
        """Remove all active sessions."""
        self._sessions.clear()

    def cleanup(self) -> int:
        """Remove expired sessions."""
        now = time.time()

        expired_ids = [
            session_id
            for session_id, session in self._sessions.items()
            if self._is_expired(
                session,
                now,
            )
        ]

        for session_id in expired_ids:
            self.remove(session_id)

        return len(expired_ids)

    def count(self) -> int:
        """Return the number of active sessions."""
        self.cleanup()

        return len(self._sessions)

    def update_telegram_session(
        self,
        session_id: str,
        telegram_session: str | bytes,
    ) -> bool:
        """Store the authenticated Telegram session."""
        session = self.get(session_id)

        if session is None:
            return False

        session.telegram_session = telegram_session

        return True

    def update_metadata(
        self,
        session_id: str,
        values: dict[str, Any],
    ) -> bool:
        """Update temporary session metadata."""
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
        current_time = (
            now if now is not None else time.time()
        )

        return (
            current_time - session.last_activity
        ) > self.timeout


session_manager = SessionManager()
