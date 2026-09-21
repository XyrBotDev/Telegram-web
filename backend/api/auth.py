from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from backend.models.auth import (
    AuthResponse,
    CodeVerificationRequest,
    CurrentUserResponse,
    LogoutRequest,
    PhoneLoginRequest,
    TwoFactorRequest,
)
from backend.services.auth_service import auth_service


router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
)


@router.post(
    "/phone",
    response_model=AuthResponse,
)
async def phone_login(
    request: PhoneLoginRequest,
) -> AuthResponse:
    """Start phone-based Telegram authentication."""
    try:
        result = await auth_service.create_phone_login(
            request.phone_number
        )

        return AuthResponse(**result)

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.post(
    "/verify-code",
    response_model=AuthResponse,
)
async def verify_code(
    request: CodeVerificationRequest,
) -> AuthResponse:
    """Verify a Telegram authentication code."""
    try:
        result = await auth_service.verify_code(
            request.session_id,
            request.code,
        )

        return AuthResponse(**result)

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.post(
    "/verify-password",
    response_model=AuthResponse,
)
async def verify_password(
    request: TwoFactorRequest,
) -> AuthResponse:
    """Verify Telegram two-step verification."""
    try:
        result = await auth_service.verify_password(
            request.session_id,
            request.password,
        )

        return AuthResponse(**result)

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.post(
    "/logout",
)
async def logout(
    request: LogoutRequest,
) -> dict:
    """Log out and remove the temporary Telefarm session."""
    success = await auth_service.logout(
        request.session_id
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found.",
        )

    return {
        "success": True,
        "message": "Logged out successfully.",
    }


@router.get(
    "/me",
    response_model=CurrentUserResponse,
)
async def current_user(
    session_id: str,
) -> CurrentUserResponse:
    """Return the authenticated Telegram user."""
    user = await auth_service.get_current_user(
        session_id
    )

    if user is None:
        return CurrentUserResponse(
            authenticated=False,
            user=None,
        )

    return CurrentUserResponse(
        authenticated=True,
        user=user,
  )
