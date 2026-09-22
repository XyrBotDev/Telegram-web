from __future__ import annotations

from typing import Any

from backend.core.exceptions import SessionError
from backend.core.pyrogram_client import pyrogram_manager
from backend.core.sessions import session_manager


class MessageService:
    """Handle Telegram message operations through Pyrogram."""

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

    async def get_messages(
        self,
        session_id: str,
        chat_id: int | str,
        limit: int = 50,
        offset_id: int = 0,
    ) -> list[dict[str, Any]]:
        """Fetch messages from a chat."""
        client = await self._get_client(session_id)

        messages = []

        async for message in client.get_chat_history(
            chat_id,
            limit=limit,
        ):
            if offset_id and message.id >= offset_id:
                continue

            messages.append(
                self._serialize_message(message)
            )

        return messages

    async def send_message(
        self,
        session_id: str,
        chat_id: int | str,
        text: str,
        reply_to: int | None = None,
    ) -> dict[str, Any]:
        """Send a text message."""
        client = await self._get_client(session_id)

        message = await client.send_message(
            chat_id,
            text,
            reply_to_message_id=reply_to,
        )

        return self._serialize_message(message)

    async def edit_message(
        self,
        session_id: str,
        chat_id: int | str,
        message_id: int,
        text: str,
    ) -> dict[str, Any]:
        """Edit an existing message."""
        client = await self._get_client(session_id)

        message = await client.edit_message_text(
            chat_id,
            message_id,
            text,
        )

        return self._serialize_message(message)

    async def delete_messages(
        self,
        session_id: str,
        chat_id: int | str,
        message_ids: list[int],
    ) -> bool:
        """Delete messages."""
        client = await self._get_client(session_id)

        await client.delete_messages(
            chat_id,
            message_ids,
        )

        return True

    async def forward_messages(
        self,
        session_id: str,
        from_chat_id: int | str,
        to_chat_id: int | str,
        message_ids: list[int],
    ) -> list[dict[str, Any]]:
        """Forward messages between chats."""
        client = await self._get_client(session_id)

        messages = await client.forward_messages(
            to_chat_id,
            from_chat_id,
            message_ids,
        )

        return [
            self._serialize_message(message)
            for message in messages
        ]

    @staticmethod
    def _serialize_message(message) -> dict[str, Any]:
        """Convert a Pyrogram message into API-safe data."""

        reply_to = getattr(
            message,
            "reply_to_message_id",
            None,
        )

        date = getattr(message, "date", None)

        return {
            "id": message.id,
            "chat_id": getattr(
                getattr(message, "chat", None),
                "id",
                None,
            ),
            "sender_id": getattr(
                message,
                "from_user",
                None,
            ).id
            if getattr(message, "from_user", None)
            else None,
            "text": getattr(message, "text", None)
            or getattr(message, "caption", None),
            "date": date.isoformat() if date else None,
            "edited": bool(
                getattr(message, "edit_date", None)
            ),
            "outgoing": bool(
                getattr(message, "outgoing", False)
            ),
            "reply_to": reply_to,
        }


message_service = MessageService()
