from __future__ import annotations

from pydantic import BaseModel


class ChatResponse(BaseModel):
    id: int | str
    title: str
    username: str | None = None
    chat_type: str
    photo: str | None = None
    unread_count: int = 0
    pinned: bool = False
    archived: bool = False
    last_message: dict | None = None


class ChatListResponse(BaseModel):
    chats: list[ChatResponse]
    total: int
