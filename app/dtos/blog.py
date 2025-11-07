from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.dtos.admin import AuthorMini


class PostOut(BaseModel):
    id: int
    slug: str
    title: str
    summary: str | None = None
    content: str
    status: str
    published_at: datetime | None = None
    author: AuthorMini
    created_at: datetime
    updated_at: datetime

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


class PostUpdate(BaseModel):
    slug: str | None = Field(None, min_length=1, max_length=160)
    title: str | None = Field(None, min_length=1, max_length=160)
    summary: str | None = Field(None, max_length=300)
    content: str | None = None
    status: str | None = None
    published_at: datetime | None = None
    author_id: int | None = None

    model_config = ConfigDict(extra="forbid")
