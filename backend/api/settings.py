from __future__ import annotations

from fastapi import APIRouter


router = APIRouter(
    prefix="/api/settings",
    tags=["Settings"],
)


@router.get(
    "",
)
async def get_settings() -> dict:
    """Return public application settings."""
    return {
        "success": True,
        "app_name": "Telefarm",
        "theme_modes": [
            "light",
            "dark",
        ],
        "language": "en",
    }
