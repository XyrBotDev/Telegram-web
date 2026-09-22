from __future__ import annotations

from typing import Any

from backend.core.exceptions import SessionError
from backend.core.pyrogram_client import pyrogram_manager
from backend.core.sessions import session_manager


class ChatService:
    """Handle chat-related Telegram operations using Pyrogram."""

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

        client = pyrogram_manager.get_client(
            session_id
        )

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

    async def list_chats(
        self,
        session_id: str,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Return the authenticated user's dialogs."""

        client = await self._get_client(
            session_id
        )

        chats: list[dict[str, Any]] = []

        async for dialog in client.get_dialogs(
            limit=limit
        ):
            chat = dialog.chat

            if chat is None:
                continue

            chat_type = getattr(
                chat,
                "type",
                None,
            )

            if chat_type is not None:
                chat_type = str(chat_type)
                if "." in chat_type:
                    chat_type = chat_type.split(".")[-1]

            chats.append(
                {
                    "id": chat.id,
                    "title": (
                        getattr(
                            chat,
                            "title",
                            None,
                        )
                        or getattr(
                            chat,
                            "first_name",
                            None,
                        )
                        or ""
                    ),
                    "username": getattr(
                        chat,
                        "username",
                        None,
                    ),
                    "chat_type": chat_type,
                    "unread_count": getattr(
                        dialog,
                        "unread_messages",
                        0,
                    ),
                    "pinned": bool(
                        getattr(
                            dialog,
                            "is_pinned",
                            False,
                        )
                    ),
                    "archived": bool(
                        getattr(
                            dialog,
                            "folder_id",
                            None,
                        ) == 1
                    ),
                }
            )

        return chats

    async def get_chat(
        self,
        session_id: str,
        chat_id: int | str,
    ) -> dict[str, Any]:
        """Resolve and return a Telegram chat."""

        client = await self._get_client(
            session_id
        )

        chat = await client.get_chat(
            chat_id
        )

        return {
            "id": chat.id,
            "title": (
                getattr(
                    chat,
                    "title",
                    None,
                )
                or getattr(
                    chat,
                    "first_name",
                    None,
                )
                or ""
            ),
            "username": getattr(
                chat,
                "username",
                None,
            ),
            "chat_type": str(
                getattr(
                    chat,
                    "type",
                    "",
                )
            ).split(".")[-1],
        }


chat_service = ChatService()
