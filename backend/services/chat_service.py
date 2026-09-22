from __future__ import annotations

from typing import Any

from backend.core.exceptions import SessionError
from backend.core.pyrogram_client import pyrogram_manager
from backend.core.sessions import session_manager


class ChatService:
    """Handle Telegram chat operations through Pyrogram."""

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

    async def list_chats(
        self,
        session_id: str,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Return chats from the Telegram dialog list."""
        client = await self._get_client(session_id)

        chats = []

        async for dialog in client.get_dialogs(limit=limit):
            chat = dialog.chat

            if chat is None:
                continue

            chats.append(
                self._serialize_chat(
                    chat,
                    dialog=dialog,
                )
            )

        return chats

    async def get_chat(
        self,
        session_id: str,
        chat_id: int | str,
    ) -> dict[str, Any]:
        """Return a chat from the authenticated user's dialogs."""

        client = await self._get_client(session_id)

        target_id = int(chat_id)

        async for dialog in client.get_dialogs():
            chat = dialog.chat

            if chat is None:
                continue

            if chat.id == target_id:
                return self._serialize_chat(
                    chat,
                    dialog=dialog,
                )

        raise SessionError(
            "Chat was not found in the current dialog list."
        )

    @staticmethod
    def _serialize_chat(
        chat,
        dialog=None,
    ) -> dict[str, Any]:
        """Convert a Pyrogram chat into API-safe data."""

        chat_type = getattr(chat, "type", None)

        if chat_type is not None:
            chat_type = str(chat_type)

            if "." in chat_type:
                chat_type = chat_type.split(".")[-1]

            chat_type = chat_type.upper()

        first_name = getattr(
            chat,
            "first_name",
            None,
        )

        last_name = getattr(
            chat,
            "last_name",
            None,
        )

        full_name = " ".join(
            part
            for part in (first_name, last_name)
            if part
        ).strip()

        title = (
            getattr(chat, "title", None)
            or full_name
            or ""
        )

        return {
            "id": chat.id,
            "title": title,
            "username": getattr(
                chat,
                "username",
                None,
            ),
            "chat_type": chat_type,
            "photo": None,
            "unread_count": (
                getattr(
                    dialog,
                    "unread_messages",
                    0,
                )
                if dialog is not None
                else 0
            ),
            "pinned": bool(
                getattr(
                    dialog,
                    "is_pinned",
                    False,
                )
                if dialog is not None
                else False
            ),
            "archived": bool(
                getattr(
                    dialog,
                    "folder_id",
                    None,
                )
                == 1
                if dialog is not None
                else False
            ),
            "last_message": None,
        }


chat_service = ChatService()
