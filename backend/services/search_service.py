from __future__ import annotations

from typing import Any

from backend.core.exceptions import SessionError
from backend.core.pyrogram_client import pyrogram_manager
from backend.core.sessions import session_manager


class SearchService:
    """Handle Telegram search operations through Pyrogram."""

    async def _get_client(self, session_id: str):
        session = session_manager.get(session_id)

        if session is None:
            raise SessionError(
                "Telefarm session has expired."
            )

        if not session.metadata.get("authenticated"):
            raise SessionError(
                "Telefarm session is not authenticated."
            )

        client = pyrogram_manager.get_client(session_id)

        if client is None:
            telegram_session = session.telegram_session

            if not telegram_session:
                raise SessionError(
                    "Telegram session is not available."
                )

            client = await pyrogram_manager.create_client(
                session_key=session_id,
                session_string=telegram_session,
            )

        if not client.is_connected:
            await client.connect()

        return client

    async def search_messages(
        self,
        session_id: str,
        query: str,
        chat_id: int | str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Search Telegram messages."""

        client = await self._get_client(session_id)

        target_chat = (
            int(chat_id)
            if chat_id is not None
            else None
        )

        messages = []

        async for message in client.search_messages(
            chat_id=target_chat,
            query=query,
            limit=limit,
        ):
            messages.append(
                self._serialize_message(message)
            )

        return messages

    @staticmethod
    def _serialize_message(message) -> dict[str, Any]:
        date = getattr(message, "date", None)

        chat = getattr(
            message,
            "chat",
            None,
        )

        from_user = getattr(
            message,
            "from_user",
            None,
        )

        return {
            "id": getattr(
                message,
                "id",
                None,
            ),
            "chat_id": getattr(
                chat,
                "id",
                None,
            ),
            "sender_id": getattr(
                from_user,
                "id",
                None,
            ),
            "text": (
                getattr(message, "text", None)
                or getattr(message, "caption", None)
            ),
            "date": (
                date.isoformat()
                if date
                else None
            ),
            "outgoing": bool(
                getattr(
                    message,
                    "outgoing",
                    False,
                )
            ),
        }


search_service = SearchService()
