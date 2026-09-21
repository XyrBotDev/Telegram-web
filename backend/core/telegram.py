from __future__ import annotations

from typing import Any

from telethon import TelegramClient

from backend.config import settings


class TelegramManager:
    """Central manager for Telegram client instances."""

    def __init__(self) -> None:
        self._clients: dict[str, TelegramClient] = {}

    def get_client(self, session_key: str) -> TelegramClient | None:
        """Return an existing client for a session key."""
        return self._clients.get(session_key)

    async def create_client(
        self,
        session_key: str,
        session: str | bytes | None = None,
    ) -> TelegramClient:
        """Create and register a Telegram client."""
        existing_client = self._clients.get(session_key)

        if existing_client is not None:
            return existing_client

        client = TelegramClient(
            session=session,
            api_id=settings.telegram_api_id,
            api_hash=settings.telegram_api_hash,
        )

        self._clients[session_key] = client

        return client

    async def connect(
        self,
        session_key: str,
        session: str | bytes | None = None,
    ) -> TelegramClient:
        """Create a client if necessary and connect it."""
        client = await self._get_or_create(
            session_key=session_key,
            session=session,
        )

        if not client.is_connected():
            await client.connect()

        return client

    async def disconnect(self, session_key: str) -> None:
        """Disconnect and remove a client."""
        client = self._clients.pop(session_key, None)

        if client is None:
            return

        if client.is_connected():
            await client.disconnect()

    async def disconnect_all(self) -> None:
        """Disconnect all registered clients."""
        session_keys = list(self._clients.keys())

        for session_key in session_keys:
            await self.disconnect(session_key)

    async def is_connected(self, session_key: str) -> bool:
        """Return whether a session is currently connected."""
        client = self._clients.get(session_key)

        if client is None:
            return False

        return client.is_connected()

    async def call(
        self,
        session_key: str,
        request: Any,
    ) -> Any:
        """Execute a Telegram request using an active client."""
        client = self._clients.get(session_key)

        if client is None:
            raise RuntimeError(
                "Telegram session is not initialized."
            )

        if not client.is_connected():
            await client.connect()

        return await client(request)

    async def _get_or_create(
        self,
        session_key: str,
        session: str | bytes | None = None,
    ) -> TelegramClient:
        """Return an existing client or create a new one."""
        client = self._clients.get(session_key)

        if client is not None:
            return client

        return await self.create_client(
            session_key=session_key,
            session=session,
        )


telegram_manager = TelegramManager()
