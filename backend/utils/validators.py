from __future__ import annotations

import re


PHONE_PATTERN = re.compile(
    r"^\+?[1-9]\d{4,14}$"
)


def validate_phone_number(phone_number: str) -> bool:
    """Validate a basic international phone number format."""
    normalized = phone_number.strip().replace(
        " ",
        "",
    )

    return bool(
        PHONE_PATTERN.fullmatch(normalized)
    )


def validate_session_id(session_id: str) -> bool:
    """Validate an application session identifier."""
    if not session_id:
        return False

    if len(session_id) > 512:
        return False

    return all(
        character.isalnum() or character in "-_"
        for character in session_id
    )


def validate_chat_id(chat_id: int | str) -> bool:
    """Validate a Telegram chat identifier."""
    if isinstance(chat_id, int):
        return chat_id != 0

    if isinstance(chat_id, str):
        return bool(chat_id.strip())

    return False


def validate_message_id(message_id: int) -> bool:
    """Validate a Telegram message identifier."""
    return message_id > 0


def validate_message_text(text: str) -> bool:
    """Validate a message before sending."""
    normalized = text.strip()

    return bool(normalized) and len(normalized) <= 4096
