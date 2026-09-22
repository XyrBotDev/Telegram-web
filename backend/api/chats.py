from __future__ import annotations

from fastapi import (
    APIRouter,
    HTTPException,
)
from fastapi.responses import Response

from backend.models.chat import (
    ChatListResponse,
    ChatResponse,
)
from backend.services.chat_service import (
    chat_service,
)


router = APIRouter(
    prefix="/api/chats",
    tags=["Chats"],
)


@router.get(
    "",
    response_model=ChatListResponse,
)
async def list_chats(
    session_id: str,
    limit: int = 50,
) -> ChatListResponse:
    """Return the user's Telegram dialogs."""

    if limit < 1 or limit > 100:
        raise HTTPException(
            status_code=400,
            detail="Limit must be between 1 and 100.",
        )

    try:
        chats = await chat_service.list_chats(
            session_id=session_id,
            limit=limit,
        )

        return ChatListResponse(
            chats=[
                ChatResponse(**chat)
                for chat in chats
            ],
            total=len(chats),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@router.get(
    "/{chat_id}/photo",
)
async def get_chat_photo(
    chat_id: str,
    session_id: str,
):
    """Return a Telegram chat profile photo."""

    try:
        photo = (
            await chat_service.get_chat_photo(
                session_id=session_id,
                chat_id=chat_id,
            )
        )

        if photo is None:
            return Response(
                status_code=404
            )

        content = photo.getvalue()

        content_type = (
            getattr(
                photo,
                "content_type",
                None,
            )
            or "image/jpeg"
        )

        return Response(
            content=content,
            media_type=content_type,
            headers={
                "Cache-Control":
                    "private, max-age=300"
            },
        )

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@router.get(
    "/{chat_id}",
)
async def get_chat(
    chat_id: str,
    session_id: str,
) -> dict:
    """Return a Telegram chat."""

    try:
        chat = await chat_service.get_chat(
            session_id=session_id,
            chat_id=chat_id,
        )

        return {
            "success": True,
            "chat": chat,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc
