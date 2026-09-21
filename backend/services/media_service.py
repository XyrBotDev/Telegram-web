from __future__ import annotations

from pathlib import Path

from backend.core.exceptions import SessionError
from backend.core.sessions import session_manager
from backend.core.telegram import telegram_manager


class MediaService:
    """Handle Telegram media operations."""

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

    async def download_media(
        self,
        session_id: str,
        chat_id: int | str,
        message_id: int,
        destination: str,
    ) -> str | None:
        """Download media from a Telegram message."""
        client = self._get_client(session_id)

        message = await client.get_messages(
            chat_id,
            ids=message_id,
        )

        if message is None:
            return None

        if not message.media:
            return None

        destination_path = Path(destination)
        destination_path.mkdir(
            parents=True,
            exist_ok=True,
        )

        downloaded = await client.download_media(
            message,
            file=str(destination_path),
        )

        return str(downloaded) if downloaded else None


media_service = MediaService()
