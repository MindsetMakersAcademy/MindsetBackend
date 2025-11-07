from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


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


class AdminUpdate(BaseModel):
    email: str = Field(..., min_length=3, max_length=160)
    full_name: str | None = Field(None, min_length=1, max_length=160)
    password: str | None = Field(None, min_length=8, max_length=128)
    is_active: bool | None = None

    model_config = ConfigDict(extra="forbid")


class AuthorMini(BaseModel):
    id: int
    full_name: str
    email: str
    model_config = ConfigDict(from_attributes=True)


class PostCreate(BaseModel):
    slug: str = Field(..., min_length=1, max_length=160)
    title: str = Field(..., min_length=1, max_length=160)
    summary: str | None = Field(None, max_length=300)
    content: str = Field(..., min_length=1)
    status: Literal["draft", "published", "archived"] = Field(default="draft")
    published_at: datetime | None = None
    author_id: int

    @field_validator("status")
    @classmethod
    def _status_ok(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if v not in {"draft", "published", "archived"}:
            raise ValueError("status must be one of: draft|published|archived")
        return v


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
