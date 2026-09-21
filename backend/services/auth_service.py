from __future__ import annotations

from telethon.errors import SessionPasswordNeededError
from telethon.sessions import StringSession

from backend.core.exceptions import (
    SessionError,
    TelegramAuthenticationError,
)
from backend.core.sessions import session_manager
from backend.core.telegram import telegram_manager


class AuthService:
    async def create_phone_login(self, phone_number: str) -> dict:
        phone_number = phone_number.strip()

        if not phone_number:
            raise TelegramAuthenticationError(
                "Phone number cannot be empty."
            )

        app_session = session_manager.create(
            metadata={
                "phone_number": phone_number,
                "auth_stage": "code",
            }
        )

        try:
            client = await telegram_manager.connect(
                session_key=app_session.session_id,
                session=StringSession(),
            )

            sent_code = await client.send_code_request(
                phone_number
            )

            code_type = type(sent_code.type).__name__

            next_type = (
                type(sent_code.next_type).__name__
                if sent_code.next_type is not None
                else None
            )

            session_manager.update_metadata(
                app_session.session_id,
                {
                    "phone_code_hash": sent_code.phone_code_hash,
                    "code_type": code_type,
                    "next_type": next_type,
                    "code_timeout": sent_code.timeout,
                    "auth_stage": "code",
                },
            )

            return {
                "success": True,
                "session_id": app_session.session_id,
                "requires_code": True,
                "requires_password": False,
                "code_type": code_type,
                "next_type": next_type,
                "code_timeout": sent_code.timeout,
                "message": "Verification code request accepted.",
            }

        except Exception as exc:
            session_manager.remove(app_session.session_id)
            await telegram_manager.disconnect(
                app_session.session_id
            )

            raise TelegramAuthenticationError(
                "Unable to send the verification code."
            ) from exc

    async def verify_code(
        self,
        session_id: str,
        code: str,
    ) -> dict:
        session = session_manager.get(session_id)

        if session is None:
            raise SessionError(
                "Authentication session has expired."
            )

        phone_number = session.metadata.get("phone_number")
        phone_code_hash = session.metadata.get("phone_code_hash")

        if not phone_number or not phone_code_hash:
            raise TelegramAuthenticationError(
                "Authentication information is incomplete."
            )

        client = telegram_manager.get_client(session_id)

        if client is None:
            raise SessionError(
                "Telegram authentication client is unavailable."
            )

        try:
            await client.sign_in(
                phone=phone_number,
                code=code,
                phone_code_hash=phone_code_hash,
            )

        except SessionPasswordNeededError:
            session_manager.update_metadata(
                session_id,
                {
                    "auth_stage": "password",
                },
            )

            return {
                "success": True,
                "session_id": session_id,
                "requires_code": False,
                "requires_password": True,
                "message": "Two-step verification is required.",
            }

        except Exception as exc:
            raise TelegramAuthenticationError(
                "Invalid or expired verification code."
            ) from exc

        return await self._complete_authentication(session_id)

    async def verify_password(
        self,
        session_id: str,
        password: str,
    ) -> dict:
        session = session_manager.get(session_id)

        if session is None:
            raise SessionError(
                "Authentication session has expired."
            )

        if not password:
            raise TelegramAuthenticationError(
                "Password cannot be empty."
            )

        client = telegram_manager.get_client(session_id)

        if client is None:
            raise SessionError(
                "Telegram authentication client is unavailable."
            )

        try:
            await client.sign_in(password=password)

        except Exception as exc:
            raise TelegramAuthenticationError(
                "Invalid two-step verification password."
            ) from exc

        return await self._complete
