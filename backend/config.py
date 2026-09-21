import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    telegram_api_id: int
    telegram_api_hash: str

    session_timeout: int
    max_upload_size: int

    debug: bool
    allowed_origins: list[str]


def _get_required(name: str) -> str:
    value = os.getenv(name)

    if not value:
        raise RuntimeError(
            f"Required environment variable '{name}' is not configured."
        )

    return value


def _get_int(name: str, default: int) -> int:
    value = os.getenv(name)

    if value is None or value.strip() == "":
        return default

    try:
        return int(value)
    except ValueError as exc:
        raise RuntimeError(
            f"Environment variable '{name}' must be an integer."
        ) from exc


def _get_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)

    if value is None:
        return default

    return value.strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def _get_origins() -> list[str]:
    value = os.getenv("ALLOWED_ORIGINS", "*")

    origins = [
        origin.strip()
        for origin in value.split(",")
        if origin.strip()
    ]

    return origins or ["*"]


def load_settings() -> Settings:
    api_id = _get_required("TELEGRAM_API_ID")

    try:
        telegram_api_id = int(api_id)
    except ValueError as exc:
        raise RuntimeError(
            "TELEGRAM_API_ID must be an integer."
        ) from exc

    telegram_api_hash = _get_required("TELEGRAM_API_HASH")

    return Settings(
        telegram_api_id=telegram_api_id,
        telegram_api_hash=telegram_api_hash,
        session_timeout=_get_int(
            "SESSION_TIMEOUT",
            3600,
        ),
        max_upload_size=_get_int(
            "MAX_UPLOAD_SIZE",
            52428800,
        ),
        debug=_get_bool(
            "DEBUG",
            False,
        ),
        allowed_origins=_get_origins(),
    )


settings = load_settings()
