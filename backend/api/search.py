from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend.services.search_service import (
    search_service,
)


router = APIRouter(
    prefix="/api/search",
    tags=["Search"],
)


@router.get(
    "/messages",
)
async def search_messages(
    session_id: str,
    query: str,
    chat_id: str | None = None,
    limit: int = 50,
) -> dict:
    """Search Telegram messages."""
    if not query.strip():
        raise HTTPException(
            status_code=400,
            detail="Search query cannot be empty.",
        )

    if limit < 1 or limit > 100:
        raise HTTPException(
            status_code=400,
            detail="Limit must be between 1 and 100.",
        )

    try:
        messages = await search_service.search_messages(
            session_id=session_id,
            query=query,
            chat_id=chat_id,
            limit=limit,
        )

        return {
            "success": True,
            "results": messages,
            "total": len(messages),
        }

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc
