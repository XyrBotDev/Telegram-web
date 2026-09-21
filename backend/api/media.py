from __future__ import annotations

from fastapi import APIRouter, HTTPException


router = APIRouter(
    prefix="/api/media",
    tags=["Media"],
)


@router.get(
    "/status",
)
async def media_status() -> dict:
    """Return media service status."""
    return {
        "success": True,
        "available": True,
        "message": "Media service is ready.",
    }
