from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field


class AdminOut(BaseModel):
    id: int
    email: str
    full_name: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AdminCreate(BaseModel):
    email: str = Field(..., min_length=3, max_length=160)
    full_name: str = Field(..., min_length=1, max_length=160)
    password: str = Field(..., min_length=8, max_length=128)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class AdminUpdate(BaseModel):
    email: str = Field(..., min_length=3, max_length=160)
    full_name: str | None = Field(None, min_length=1, max_length=160)
    password: str | None = Field(None, min_length=8, max_length=128)
    is_active: bool | None = None
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    model_config = ConfigDict(extra="forbid")


class AuthorMini(BaseModel):
    id: int
    full_name: str
    email: str
    model_config = ConfigDict(from_attributes=True)


class AdminLoginIn(BaseModel):
    """DTO for admin login request."""

    email: str = Field(..., min_length=3, max_length=160)
    password: str = Field(..., min_length=8, max_length=128)


class AdminLoginOut(BaseModel):
    """DTO for admin login response."""

    access_token: str


class AdminAuthPayload(BaseModel):
    """DTO for JWT payload (decoded)."""

    user_id: int
    email: str
    is_admin: bool
    exp: int
