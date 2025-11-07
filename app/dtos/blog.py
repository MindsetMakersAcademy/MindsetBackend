from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

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
    status: Literal["draft", "published", "archived"] = "draft"
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    published_at: datetime | None = None
    author_id: int

class PostUpdate(BaseModel):
    slug: str | None = Field(None, min_length=1, max_length=160)
    title: str | None = Field(None, min_length=1, max_length=160)
    summary: str | None = Field(None, max_length=300)
    content: str | None = None
    status: str | None = None
    author_id: int | None = None
    updated_at : datetime = Field(default_factory=lambda: datetime.now(UTC))

    model_config = ConfigDict(extra="forbid")
