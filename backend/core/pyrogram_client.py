from __future__ import annotations

from pyrogram import Client

from backend.config import settings


class PyrogramManager:
    """Central manager for Pyrogram client instances."""

    def __init__(self) -> None:
        self._clients: dict[str, Client] = {}

    def get_client(
        self,
        session_key: str,
    ) -> Client | None:
        """Return an existing Pyrogram client."""
        return self._clients.get(session_key)

    async def create_client(
        self,
        session_key: str,
        session_string: str | None = None,
    ) -> Client:
        """Create and register a Pyrogram client."""

        existing_client = self._clients.get(session_key)

        if existing_client is not None:
            return existing_client

        client = Client(
            name=f"telefarm_{session_key}",
            api_id=settings.telegram_api_id,
            api_hash=settings.telegram_api_hash,
            session_string=session_string,
            in_memory=True,
        )

        self._clients[session_key] = client

        return client

    async def start(
        self,
        session_key: str,
        session_string: str | None = None,
    ) -> Client:
        """Create and start a Pyrogram client."""

        client = self._clients.get(session_key)

        if client is None:
            client = await self.create_client(
                session_key=session_key,
                session_string=session_string,
            )

        if not client.is_connected:
            await client.start()

        return client

    async def stop(
        self,
        session_key: str,
    ) -> None:
        """Stop and remove a Pyrogram client."""

        client = self._clients.pop(
            session_key,
            None,
        )

        if client is None:
            return

        if client.is_connected:
            await client.stop()

    async def stop_all(self) -> None:
        """Stop all active Pyrogram clients."""

        session_keys = list(
            self._clients.keys()
        )

        for session_key in session_keys:
            await self.stop(session_key)

    def is_connected(
        self,
        session_key: str,
    ) -> bool:
        """Return the connection state of a client."""

        client = self._clients.get(session_key)

        if client is None:
            return False

        return client.is_connected


pyrogram_manager = PyrogramManager()
