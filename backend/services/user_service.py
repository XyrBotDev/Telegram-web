from __future__ import annotations

from backend.core.exceptions import SessionError
from backend.core.sessions import session_manager
from backend.core.telegram import telegram_manager


class UserService:
    """Handle Telegram user and profile operations."""

    def _get_client(self, session_id: str):
        session = session_manager.get(session_id)

        if session is None:
            raise SessionError(
                "Telefarm session has expired."
            )

        client = telegram_manager.get_client(
            session_id
        )

        if client is None:
            raise SessionError(
                "Telegram client is not available."
            )

        return client

    async def get_me(
        self,
        session_id: str,
    ) -> dict:
        """Return the authenticated user's profile."""
        client = self._get_client(session_id)

        user = await client.get_me()

        return self._serialize_user(user)

    async def get_user(
        self,
        session_id: str,
        user_id: int | str,
    ) -> dict:
        """Return another Telegram user's profile."""
        client = self._get_client(session_id)

        user = await client.get_entity(user_id)

        return self._serialize_user(user)

    @staticmethod
    def _serialize_user(user) -> dict:
        """Convert a Telegram user into API-safe data."""
        return {
            "id": user.id,
            "first_name": getattr(
                user,
                "first_name",
                None,
            ),
            "last_name": getattr(
                user,
                "last_name",
                None,
            ),
            "username": getattr(
                user,
                "username",
                None,
            ),
            "phone": getattr(
                user,
                "phone",
                None,
            ),
            "bio": getattr(
                user,
                "about",
                None,
            ),
            "verified": bool(
                getattr(
                    user,
                    "verified",
                    False,
                )
            ),
            "online": False,
        }


user_service = UserService()
