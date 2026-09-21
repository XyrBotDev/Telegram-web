from __future__ import annotations

from pydantic import BaseModel, Field


class PhoneLoginRequest(BaseModel):
    phone_number: str = Field(min_length=5, max_length=32)


class CodeVerificationRequest(BaseModel):
    session_id: str
    code: str = Field(min_length=1, max_length=32)


class TwoFactorRequest(BaseModel):
    session_id: str
    password: str = Field(min_length=1, max_length=256)


class SessionLoginRequest(BaseModel):
    session: str = Field(min_length=1)


class LogoutRequest(BaseModel):
    session_id: str


class AuthResponse(BaseModel):
    success: bool
    session_id: str | None = None
    requires_code: bool = False
    requires_password: bool = False
    message: str


class CurrentUserResponse(BaseModel):
    authenticated: bool
    user: dict | None = None
