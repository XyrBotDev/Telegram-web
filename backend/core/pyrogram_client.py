from __future__ import annotations

from pyrogram import Client

from backend.config import settings


class PyrogramManager:
    """Manage temporary in-memory Pyrogram clients."""

    def __init__(self) -> None:
        self._clients: dict[str, Client] = {}

    def get_client(self, session_key: str) -> Client | None:
        return self._clients.get(session_key)

    async def create_client(
        self,
        session_key: str,
        session_string: str | None = None,
    ) -> Client:
        existing = self._clients.get(session_key)

        if existing is not None:
            return existing

        client = Client(
            name=f"telefarm_{session_key}",
            api_id=settings.telegram_api_id,
            api_hash=settings.telegram_api_hash,
            session_string=session_string,
            in_memory=True,
        )

        self._clients[session_key] = client
        return client

    async def connect(
        self,
        session_key: str,
        session_string: str | None = None,
    ) -> Client:
        client = self._clients.get(session_key)

        if client is None:
            client = await self.create_client(
                session_key=session_key,
                session_string=session_string,
            )

        if not client.is_connected:
            await client.connect()

        return client

    async def disconnect(self, session_key: str) -> None:
        client = self._clients.pop(session_key, None)

        if client is None:
            return

        if client.is_connected:
            await client.disconnect()

    async def disconnect_all(self) -> None:
        session_keys = list(self._clients.keys())

        for session_key in session_keys:
            await self.disconnect(session_key)

    def is_connected(self, session_key: str) -> bool:
        client = self._clients.get(session_key)

        if client is None:
            return False

        return client.is_connected


pyrogram_manager = PyrogramManager()
