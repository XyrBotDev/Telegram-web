from __future__ import annotations

from pydantic import BaseModel


class UserResponse(BaseModel):
    id: int
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None
    phone: str | None = None
    bio: str | None = None
    photo: str | None = None
    verified: bool = False
    online: bool = False


class ProfileResponse(BaseModel):
    user: UserResponse
