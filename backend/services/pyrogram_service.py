from __future__ import annotations

from typing import Any

from backend.core.exceptions import SessionError
from backend.core.pyrogram_client import pyrogram_manager
from backend.core.sessions import session_manager


class PyrogramService:
    """Provide high-level operations through Pyrogram."""

    def _validate_session(
        self,
        session_id: str,
    ) -> None:
        session = session_manager.get(session_id)

        if session is None:
            raise SessionError(
                "Telefarm session has expired."
            )

    def _get_client(
        self,
        session_id: str,
    ):
        self._validate_session(session_id)

        client = pyrogram_manager.get_client(
            session_id
        )

        if client is None:
            raise SessionError(
                "Pyrogram client is not available."
            )

        return client

    async def get_me(
        self,
        session_id: str,
    ) -> Any:
        """Return the authenticated user through Pyrogram."""
        client = self._get_client(session_id)

        if not client.is_connected:
            await client.start()

        return await client.get_me()

    async def get_chat(
        self,
        session_id: str,
        chat_id: int | str,
    ) -> Any:
        """Retrieve a chat through Pyrogram."""
        client = self._get_client(session_id)

        return await client.get_chat(chat_id)

    async def get_chat_history(
        self,
        session_id: str,
        chat_id: int | str,
        limit: int = 50,
    ) -> list[Any]:
        """Retrieve chat history through Pyrogram."""
        client = self._get_client(session_id)

        messages = []

        async for message in client.get_chat_history(
            chat_id,
            limit=limit,
        ):
            messages.append(message)

        return messages

    async def send_message(
        self,
        session_id: str,
        chat_id: int | str,
        text: str,
    ) -> Any:
        """Send a text message through Pyrogram."""
        client = self._get_client(session_id)

        return await client.send_message(
            chat_id=chat_id,
            text=text,
        )


pyrogram_service = PyrogramService()
