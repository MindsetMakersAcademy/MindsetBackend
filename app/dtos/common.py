from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator


class SortQueryDTO(BaseModel):
    """DTO for sorting query parameters."""

    sort: str = Field(default="id", description="Field to sort by")
    direction: Literal["asc", "desc"] = Field(default="asc", description="Sort direction")


class Pagination(BaseModel):
    """DTO for pagination payloads."""

    offset: int = Field(default=1, ge=1, description="Offset number (1-indexed)")
    limit: int = Field(default=20, ge=1, le=100, description="Items per page")


class SearchQueryDTO(BaseModel):
    """DTO for search query parameters."""

    q: str | None = Field(default=None, min_length=1, max_length=100, description="Search query")

    @field_validator("q")
    @classmethod
    def strip_whitespace(cls, v: str | None) -> str | None:
        """Strip whitespace from query string."""
        return v.strip() if v else None
