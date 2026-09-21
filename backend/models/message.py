from __future__ import annotations

from pydantic import BaseModel, Field


class SendMessageRequest(BaseModel):
    chat_id: int | str
    text: str = Field(min_length=1, max_length=4096)
    reply_to: int | None = None


class EditMessageRequest(BaseModel):
    chat_id: int | str
    message_id: int
    text: str = Field(min_length=1, max_length=4096)


class DeleteMessageRequest(BaseModel):
    chat_id: int | str
    message_ids: list[int]


class ForwardMessageRequest(BaseModel):
    from_chat_id: int | str
    to_chat_id: int | str
    message_ids: list[int]


class MessageResponse(BaseModel):
    id: int
    chat_id: int | str
    sender_id: int | None = None
    text: str | None = None
    date: str | None = None
    edited: bool = False
    outgoing: bool = False
    reply_to: int | None = None


class MessageListResponse(BaseModel):
    messages: list[MessageResponse]
    has_more: bool = False
