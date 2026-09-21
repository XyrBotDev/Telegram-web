from __future__ import annotations

from backend.core.exceptions import (
    SessionError,
)
from backend.core.sessions import session_manager
from backend.core.telegram import telegram_manager


class MessageService:
    """Handle Telegram message operations."""

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

    async def get_messages(
        self,
        session_id: str,
        chat_id: int | str,
        limit: int = 50,
        offset_id: int = 0,
    ) -> list[dict]:
        """Fetch messages from a chat."""
        client = self._get_client(session_id)

        messages = await client.get_messages(
            chat_id,
            limit=limit,
            offset_id=offset_id,
        )

        return [
            self._serialize_message(message)
            for message in messages
        ]

    async def send_message(
        self,
        session_id: str,
        chat_id: int | str,
        text: str,
        reply_to: int | None = None,
    ) -> dict:
        """Send a text message."""
        client = self._get_client(session_id)

        message = await client.send_message(
            entity=chat_id,
            message=text,
            reply_to=reply_to,
        )

        return self._serialize_message(message)

    async def edit_message(
        self,
        session_id: str,
        chat_id: int | str,
        message_id: int,
        text: str,
    ) -> dict:
        """Edit an existing message."""
        client = self._get_client(session_id)

        message = await client.edit_message(
            entity=chat_id,
            message=message_id,
            text=text,
        )

        return self._serialize_message(message)

    async def delete_messages(
        self,
        session_id: str,
        chat_id: int | str,
        message_ids: list[int],
    ) -> bool:
        """Delete messages."""
        client = self._get_client(session_id)

        await client.delete_messages(
            entity=chat_id,
            message_ids=message_ids,
        )

        return True

    async def forward_messages(
        self,
        session_id: str,
        from_chat_id: int | str,
        to_chat_id: int | str,
        message_ids: list[int],
    ) -> list[dict]:
        """Forward messages between chats."""
        client = self._get_client(session_id)

        messages = await client.forward_messages(
            entity=to_chat_id,
            messages=message_ids,
            from_peer=from_chat_id,
        )

        return [
            self._serialize_message(message)
            for message in messages
        ]

    @staticmethod
    def _serialize_message(message) -> dict:
        """Convert a Telethon message into API-safe data."""
        return {
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
            "edited": bool(
                getattr(
                    message,
                    "edit_date",
                    None,
                )
            ),
            "outgoing": bool(
                getattr(
                    message,
                    "out",
                    False,
                )
            ),
            "reply_to": (
                message.reply_to_msg_id
                if getattr(
                    message,
                    "reply_to",
                    None,
                )
                else None
            ),
        }


message_service = MessageService()
