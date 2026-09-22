from __future__ import annotations

from backend.core.exceptions import SessionError
from backend.core.pyrogram_client import pyrogram_manager
from backend.core.sessions import session_manager


class UserService:
    """Handle Telegram user and profile operations through Pyrogram."""

    async def _get_client(self, session_id: str):
        session = session_manager.get(session_id)

        if session is None:
            raise SessionError("Telefarm session has expired.")

        if not session.metadata.get("authenticated"):
            raise SessionError("Telefarm session is not authenticated.")

        client = pyrogram_manager.get_client(session_id)

        if client is None:
            telegram_session = session.telegram_session

            if not telegram_session:
                raise SessionError("Telegram session is not available.")

            client = await pyrogram_manager.create_client(
                session_key=session_id,
                session_string=telegram_session,
            )

        if not client.is_connected:
            await client.connect()

        return client

    async def get_me(
        self,
        session_id: str,
    ) -> dict:
        """Return the authenticated user's profile."""
        client = await self._get_client(session_id)

        user = await client.get_me()

        return self._serialize_user(user)

    async def get_user(
        self,
        session_id: str,
        user_id: int | str,
    ) -> dict:
        """Return another Telegram user's profile."""
        client = await self._get_client(session_id)

        user = await client.get_users(user_id)

        return self._serialize_user(user)

    @staticmethod
    def _serialize_user(user) -> dict:
        """Convert a Pyrogram user into API-safe data."""
        status = getattr(user, "status", None)
        status_name = getattr(status, "name", "")

        return {
            "id": user.id,
            "first_name": getattr(user, "first_name", None),
            "last_name": getattr(user, "last_name", None),
            "username": getattr(user, "username", None),
            "phone": getattr(user, "phone", None),
            "bio": getattr(user, "bio", None),
            "verified": bool(
                getattr(user, "is_verified", False)
            ),
            "online": status_name in {
                "ONLINE",
                "RECENTLY",
            },
        }


user_service = UserService()
