from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend.models.message import (
    DeleteMessageRequest,
    EditMessageRequest,
    ForwardMessageRequest,
    MessageListResponse,
    MessageResponse,
    SendMessageRequest,
)
from backend.services.message_service import (
    message_service,
)


router = APIRouter(
    prefix="/api/messages",
    tags=["Messages"],
)


@router.get(
    "",
    response_model=MessageListResponse,
)
async def get_messages(
    session_id: str,
    chat_id: str,
    limit: int = 50,
    offset_id: int = 0,
) -> MessageListResponse:
    """Return messages from a Telegram chat."""
    if limit < 1 or limit > 100:
        raise HTTPException(
            status_code=400,
            detail="Limit must be between 1 and 100.",
        )

    try:
        messages = await message_service.get_messages(
            session_id=session_id,
            chat_id=chat_id,
            limit=limit,
            offset_id=offset_id,
        )

        return MessageListResponse(
            messages=[
                MessageResponse(**message)
                for message in messages
            ],
            has_more=len(messages) >= limit,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@router.post(
    "",
    response_model=MessageResponse,
)
async def send_message(
    session_id: str,
    request: SendMessageRequest,
) -> MessageResponse:
    """Send a text message."""
    try:
        message = await message_service.send_message(
            session_id=session_id,
            chat_id=request.chat_id,
            text=request.text,
            reply_to=request.reply_to,
        )

        return MessageResponse(**message)

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@router.put(
    "",
    response_model=MessageResponse,
)
async def edit_message(
    session_id: str,
    request: EditMessageRequest,
) -> MessageResponse:
    """Edit a message."""
    try:
        message = await message_service.edit_message(
            session_id=session_id,
            chat_id=request.chat_id,
            message_id=request.message_id,
            text=request.text,
        )

        return MessageResponse(**message)

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@router.delete(
    "",
)
async def delete_messages(
    session_id: str,
    request: DeleteMessageRequest,
) -> dict:
    """Delete messages."""
    try:
        await message_service.delete_messages(
            session_id=session_id,
            chat_id=request.chat_id,
            message_ids=request.message_ids,
        )

        return {
            "success": True,
            "message": "Messages deleted successfully.",
        }

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@router.post(
    "/forward",
)
async def forward_messages(
    session_id: str,
    request: ForwardMessageRequest,
) -> dict:
    """Forward messages to another chat."""
    try:
        messages = await message_service.forward_messages(
            session_id=session_id,
            from_chat_id=request.from_chat_id,
            to_chat_id=request.to_chat_id,
            message_ids=request.message_ids,
        )

        return {
            "success": True,
            "messages": messages,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc
