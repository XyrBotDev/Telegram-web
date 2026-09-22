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

    @staticmethod
    def _value(obj: Any, key: str, default=None):
        """Read a value from either an object or a dictionary."""
        if isinstance(obj, dict):
            return obj.get(key, default)

        return getattr(obj, key, default)

    async def list_chats(
        self,
        session_id: str,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Return chats from the Telegram dialog list."""

        client = await self._get_client(session_id)

        chats = []

        async for dialog in client.get_dialogs(limit=limit):
            chat = self._value(dialog, "chat")

            if chat is None:
                continue

            chats.append(
                self._serialize_chat(
                    chat,
                    dialog,
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

        try:
            target_id = int(chat_id)
        except (TypeError, ValueError) as exc:
            raise SessionError(
                "Invalid chat ID."
            ) from exc

        async for dialog in client.get_dialogs():
            chat = self._value(dialog, "chat")

            if chat is None:
                continue

            current_id = self._value(
                chat,
                "id",
            )

            if current_id == target_id:
                return self._serialize_chat(
                    chat,
                    dialog,
                )

        raise SessionError(
            "Chat was not found in the current dialog list."
        )

    def _serialize_chat(
        self,
        chat,
        dialog=None,
    ) -> dict[str, Any]:
        """Convert a Pyrogram chat into API-safe data."""

        chat_id = self._value(
            chat,
            "id",
        )

        chat_type = self._value(
            chat,
            "type",
        )

        if chat_type is not None:
            chat_type = str(chat_type)

            if "." in chat_type:
                chat_type = chat_type.split(".")[-1]

            chat_type = chat_type.upper()

        first_name = self._value(
            chat,
            "first_name",
        )

        last_name = self._value(
            chat,
            "last_name",
        )

        full_name = " ".join(
            part
            for part in (
                first_name,
                last_name,
            )
            if part
        ).strip()

        title = (
            self._value(
                chat,
                "title",
            )
            or full_name
            or ""
        )

        unread_count = self._value(
            dialog,
            "unread_messages",
            0,
        )

        pinned = bool(
            self._value(
                dialog,
                "is_pinned",
                False,
            )
        )

        folder_id = self._value(
            dialog,
            "folder_id",
        )

        archived = folder_id == 1

        return {
            "id": chat_id,
            "title": title,
            "username": self._value(
                chat,
                "username",
            ),
            "chat_type": chat_type,
            "photo": None,
            "unread_count": unread_count,
            "pinned": pinned,
            "archived": archived,
            "last_message": None,
        }


chat_service = ChatService()
