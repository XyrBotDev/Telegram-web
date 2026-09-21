from __future__ import annotations

from backend.core.exceptions import (
    SessionError,
    TelegramAuthenticationError,
)
from backend.core.pyrogram_client import pyrogram_manager


class PyrogramAuthService:
    """Handle temporary Pyrogram Telegram authentication."""

    async def create_phone_login(
        self,
        session_id: str,
        phone_number: str,
    ) -> dict:
        try:
            client = await pyrogram_manager.connect(
                session_key=session_id,
            )

            sent_code = await client.send_code(
                phone_number,
            )

            return {
                "success": True,
                "code_type": type(sent_code.type).__name__,
                "next_type": (
                    type(sent_code.next_type).__name__
                    if sent_code.next_type is not None
                    else None
                ),
                "code_timeout": sent_code.timeout,
               
