from __future__ import annotations

from typing import Any

from backend.core.exceptions import SessionError
from backend.core.sessions import session_manager
from backend.core.telegram import telegram_manager


class TelegramService:
    """Provide high-level operations through Telethon."""

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
    ) -> Any:
        """Return the authenticated Telegram user."""
        client = self._get_client(session_id)

        if not client.is_connected():
            await client.connect()

        return await client.get_me()

    async def get_entity(
        self,
        session_id: str,
        entity: int | str,
    ) -> Any:
        """Resolve a Telegram entity."""
        client = self._get_client(session_id)

        return await client.get_entity(entity)

    async def get_messages(
        self,
        session_id: str,
        chat_id: int | str,
        limit: int = 50,
    ) -> list[Any]:
        """Retrieve messages from a Telegram chat."""
        client = self._get_client(session_id)

        return await client.get_messages(
            chat_id,
            limit=limit,
        )


telegram_service = TelegramService()
