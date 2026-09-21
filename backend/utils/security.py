from __future__ import annotations

import hashlib
import hmac
import secrets


def generate_token(length: int = 32) -> str:
    """Generate a cryptographically secure random token."""
    if length < 16:
        raise ValueError("Token length must be at least 16.")

    return secrets.token_urlsafe(length)


def generate_session_key() -> str:
    """Generate a secure application session key."""
    return secrets.token_urlsafe(48)


def hash_value(value: str) -> str:
    """Create a SHA-256 hash of a value."""
    return hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()


def verify_hash(
    value: str,
    expected_hash: str,
) -> bool:
    """Safely compare a value against a SHA-256 hash."""
    actual_hash = hash_value(value)

    return hmac.compare_digest(
        actual_hash,
        expected_hash,
    )


def sanitize_text(value: str) -> str:
    """Normalize basic user-provided text."""
    return value.strip()
