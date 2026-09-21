from __future__ import annotations

from backend.core.exceptions import (
    SessionError,
    TelegramAuthenticationError,
)
from backend.core.sessions import session_manager
from backend.core.telegram import telegram_manager


class AuthService:
    """Handle Telefarm authentication operations."""

    async def create_phone_login(
        self,
        phone_number: str,
    ) -> dict:
        """
        Start the Telegram phone authentication flow.

        The actual Telegram authorization implementation will be
        connected here in the authentication integration stage.
        """
        if not phone_number.strip():
            raise TelegramAuthenticationError(
                "Phone number cannot be empty."
            )

        return {
            "success": False,
            "requires_code": False,
            "requires_password": False,
            "message": (
                "Telegram authentication is not configured yet."
            ),
        }

    async def verify_code(
        self,
        session_id: str,
        code: str,
    ) -> dict:
        """Verify a Telegram authentication code."""
        if not session_id:
            raise SessionError(
                "Authentication session is required."
            )

        if not code.strip():
            raise TelegramAuthenticationError(
                "Authentication code cannot be empty."
            )

        return {
            "success": False,
            "message": (
                "Authentication code verification "
                "is not configured yet."
            ),
        }

    async def verify_password(
        self,
        session_id: str,
        password: str,
    ) -> dict:
        """Verify a Telegram two-step verification password."""
        if not session_id:
            raise SessionError(
                "Authentication session is required."
            )

        if not password:
            raise TelegramAuthenticationError(
                "Password cannot be empty."
            )

        return {
            "success": False,
            "message": (
                "Two-step verification is not configured yet."
            ),
        }

    async def logout(
        self,
        session_id: str,
    ) -> bool:
        """Disconnect Telegram and remove the application session."""
        session = session_manager.get(session_id)

        if session is None:
            return False

        try:
            await telegram_manager.disconnect(
                session_id
            )
        finally:
            session_manager.remove(session_id)

        return True

    async def get_current_user(
        self,
        session_id: str,
    ) -> dict | None:
        """Return the currently authenticated Telegram user."""
        session = session_manager.get(session_id)

        if session is None:
            return None

        client = telegram_manager.get_client(
            session_id
        )

        if client is None:
            return None

        if not client.is_connected():
            await client.connect()

        if not await client.is_user_authorized():
            return None

        user = await client.get_me()

        return {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "username": user.username,
            "phone": user.phone,
        }


auth_service = AuthService()
