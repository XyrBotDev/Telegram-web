from __future__ import annotations

from backend.core.exceptions import (
    SessionError,
    TelegramAuthenticationError,
)
from backend.core.pyrogram_client import pyrogram_manager
from backend.core.sessions import session_manager
from backend.services.pyrogram_service import pyrogram_auth_service


class AuthService:
    async def create_phone_login(
        self,
        phone_number: str,
    ) -> dict:
        phone_number = phone_number.strip()

        if not phone_number:
            raise TelegramAuthenticationError(
                "Phone number cannot be empty."
            )

        app_session = session_manager.create(
            metadata={
                "phone_number": phone_number,
                "auth_stage": "code",
                "auth_client": "pyrogram",
            }
        )

        try:
            result = await pyrogram_auth_service.create_phone_login(
                session_id=app_session.session_id,
                phone_number=phone_number,
            )

            phone_code_hash = result.get("phone_code_hash")

            if not phone_code_hash:
                raise TelegramAuthenticationError(
                    "Telegram did not return a verification code hash."
                )

            session_manager.update_metadata(
                app_session.session_id,
                {
                    "phone_code_hash": phone_code_hash,
                    "code_type": result.get("code_type"),
                    "next_type": result.get("next_type"),
                    "code_timeout": result.get("code_timeout"),
                },
            )

            return {
                "success": True,
                "session_id": app_session.session_id,
                "requires_code": True,
                "requires_password": False,
                "code_type": result.get("code_type"),
                "next_type": result.get("next_type"),
                "code_timeout": result.get("code_timeout"),
                "message": result.get(
                    "message",
                    "Verification code request accepted.",
                ),
            }

        except Exception:
            await pyrogram_manager.disconnect(
                app_session.session_id
            )
            session_manager.remove(
                app_session.session_id
            )
            raise

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

        phone_number = session.metadata.get(
            "phone_number"
        )

        phone_code_hash = session.metadata.get(
            "phone_code_hash"
        )

        if not phone_number or not phone_code_hash:
            raise TelegramAuthenticationError(
                "Authentication information is incomplete."
            )

        result = await pyrogram_auth_service.verify_code(
            session_id=session_id,
            phone_number=phone_number,
            phone_code_hash=phone_code_hash,
            code=code,
        )

        if result.get("requires_password"):
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
                "message": result["message"],
            }

        return await self._complete_authentication(
            session_id
        )

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

        result = await pyrogram_auth_service.verify_password(
            session_id=session_id,
            password=password,
        )

        if not result.get("success"):
            raise TelegramAuthenticationError(
                "Two-step verification failed."
            )

        return await self._complete_authentication(
            session_id
        )

    async def logout(
        self,
        session_id: str,
    ) -> bool:
        session = session_manager.get(session_id)

        if session is None:
            return False

        try:
            await pyrogram_manager.disconnect(
                session_id
            )
        finally:
            session_manager.remove(
                session_id
            )

        return True

    async def get_current_user(
        self,
        session_id: str,
    ) -> dict | None:
        session = session_manager.get(session_id)

        if session is None:
            return None

        if not session.metadata.get("authenticated"):
            return None

        try:
            user = await pyrogram_auth_service.get_me(
                session_id
            )
        except Exception:
            return None

        return self._serialize_user(user)

    async def _complete_authentication(
        self,
        session_id: str,
    ) -> dict:
        session = session_manager.get(session_id)

        if session is None:
            raise SessionError(
                "Authentication session has expired."
            )

        user = await pyrogram_auth_service.get_me(
            session_id
        )

        telegram_session = (
            await pyrogram_auth_service.export_session(
                session_id
            )
        )

        session_manager.update_telegram_session(
            session_id,
            telegram_session,
        )

        session_manager.update_metadata(
            session_id,
            {
                "authenticated": True,
                "auth_stage": "authenticated",
                "user_id": user.id,
                "auth_client": "pyrogram",
            },
        )

        return {
            "success": True,
            "session_id": session_id,
            "requires_code": False,
            "requires_password": False,
            "message": "Authentication successful.",
        }

    @staticmethod
    def _serialize_user(user) -> dict:
        return {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "username": user.username,
            "phone": user.phone,
        }


auth_service = AuthService()
