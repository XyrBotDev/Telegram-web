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
                "phone_code_hash": sent_code.phone_code_hash,
                "message": "Verification code request accepted.",
            }

        except Exception as exc:
            await pyrogram_manager.disconnect(session_id)

            raise TelegramAuthenticationError(
                "Unable to request the Telegram verification code."
            ) from exc

    async def verify_code(
        self,
        session_id: str,
        phone_number: str,
        phone_code_hash: str,
        code: str,
    ) -> dict:
        client = pyrogram_manager.get_client(session_id)

        if client is None:
            raise SessionError(
                "Pyrogram authentication client is unavailable."
            )

        try:
            result = await client.sign_in(
                phone_number=phone_number,
                phone_code_hash=phone_code_hash,
                phone_code=code,
            )

            return {
                "success": True,
                "requires_password": False,
                "result_type": type(result).__name__,
                "message": "Authentication successful.",
            }

        except Exception as exc:
            error_name = type(exc).__name__

            if error_name == "SessionPasswordNeeded":
                return {
                    "success": True,
                    "requires_password": True,
                    "message": "Two-step verification is required.",
                }

            raise TelegramAuthenticationError(
                "Invalid or expired verification code."
            ) from exc

    async def verify_password(
        self,
        session_id: str,
        password: str,
    ) -> dict:
        client = pyrogram_manager.get_client(session_id)

        if client is None:
            raise SessionError(
                "Pyrogram authentication client is unavailable."
            )

        if not password:
            raise TelegramAuthenticationError(
                "Password cannot be empty."
            )

        try:
            await client.check_password(password)

            return {
                "success": True,
                "requires_password": False,
                "message": "Authentication successful.",
            }

        except Exception as exc:
            raise TelegramAuthenticationError(
                "Invalid two-step verification password."
            ) from exc

    async def export_session(
        self,
        session_id: str,
    ) -> str:
        client = pyrogram_manager.get_client(session_id)

        if client is None:
            raise SessionError(
                "Pyrogram authentication client is unavailable."
            )

        try:
            return await client.export_session_string()

        except Exception as exc:
            raise TelegramAuthenticationError(
                "Unable to create the temporary Telegram session."
            ) from exc

    async def get_me(
        self,
        session_id: str,
    ):
        client = pyrogram_manager.get_client(session_id)

        if client is None:
            raise SessionError(
                "Pyrogram authentication client is unavailable."
            )

        return await client.get_me()


pyrogram_auth_service = PyrogramAuthService()
