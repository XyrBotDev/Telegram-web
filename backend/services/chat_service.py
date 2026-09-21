from __future__ import annotations

from typing import Any

from backend.core.exceptions import (
    SessionError,
)
from backend.core.sessions import session_manager
from backend.core.telegram import telegram_manager


class ChatService:
    """Handle chat-related Telegram operations."""

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

    async def list_chats(
        self,
        session_id: str,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Return the authenticated user's dialogs."""
        client = self._get_client(session_id)

        dialogs = []

        async for dialog in client.iter_dialogs(
            limit=limit
        ):
            entity = dialog.entity

            dialogs.append(
                {
                    "id": dialog.id,
                    "title": dialog.title,
                    "username": getattr(
                        entity,
                        "username",
                        None,
                    ),
                    "chat_type": type(
                        entity
                    ).__name__,
                    "unread_count": dialog.unread_count,
                    "pinned": bool(
                        getattr(
                            dialog,
                            "pinned",
                            False,
                        )
                    ),
                    "archived": bool(
                        getattr(
                            dialog,
                            "folder_id",
                            None
                        ) == 1
                    ),
                }
            )

        return dialogs

    async def get_chat(
        self,
        session_id: str,
        chat_id: int | str,
    ) -> Any:
        """Resolve and return a Telegram chat."""
        client = self._get_client(session_id)

        return await client.get_entity(chat_id)


chat_service = ChatService()
