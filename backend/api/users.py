from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend.models.user import (
    ProfileResponse,
    UserResponse,
)
from backend.services.user_service import user_service


router = APIRouter(
    prefix="/api/users",
    tags=["Users"],
)


@router.get(
    "/me",
    response_model=ProfileResponse,
)
async def get_my_profile(
    session_id: str,
) -> ProfileResponse:
    """Return the current user's Telegram profile."""
    try:
        user = await user_service.get_me(
            session_id
        )

        return ProfileResponse(
            user=UserResponse(**user)
        )

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@router.get(
    "/{user_id}",
    response_model=UserResponse,
)
async def get_user(
    user_id: str,
    session_id: str,
) -> UserResponse:
    """Return a Telegram user's profile."""
    try:
        user = await user_service.get_user(
            session_id=session_id,
            user_id=user_id,
        )

        return UserResponse(**user)

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc
