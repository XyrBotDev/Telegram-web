from __future__ import annotations

from backend.core.exceptions import SessionError
from backend.core.sessions import session_manager
from backend.core.telegram import telegram_manager


class SearchService:
    """Handle Telegram search operations."""

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

    async def search_messages(
        self,
        session_id: str,
        query: str,
        chat_id: int | str | None = None,
        limit: int = 50,
    ) -> list[dict]:
        """Search messages using Telegram's search functionality."""
        client = self._get_client(session_id)

        messages = await client.get_messages(
            entity=chat_id,
            search=query,
            limit=limit,
        )

        return [
            {
                "id": message.id,
                "chat_id": getattr(
                    message,
                    "chat_id",
                    None,
                ),
                "sender_id": getattr(
                    message,
                    "sender_id",
                    None,
                ),
                "text": message.text,
                "date": (
                    message.date.isoformat()
                    if message.date
                    else None
                ),
            }
            for message in messages
        ]


search_service = SearchService()
