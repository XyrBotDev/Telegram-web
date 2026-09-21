class TelefarmError(Exception):
    """Base exception for Telefarm."""


class ConfigurationError(TelefarmError):
    """Raised when application configuration is invalid."""


class SessionError(TelefarmError):
    """Raised when a session operation fails."""


class SessionNotFoundError(SessionError):
    """Raised when a requested session does not exist."""


class TelegramError(TelefarmError):
    """Base exception for Telegram-related errors."""


class TelegramConnectionError(TelegramError):
    """Raised when Telegram connection fails."""


class TelegramAuthenticationError(TelegramError):
    """Raised when Telegram authentication fails."""


class TelegramRequestError(TelegramError):
    """Raised when a Telegram request fails."""


class AuthorizationError(TelefarmError):
    """Raised when a user is not authorized for an operation."""


class ValidationError(TelefarmError):
    """Raised when supplied data is invalid."""
