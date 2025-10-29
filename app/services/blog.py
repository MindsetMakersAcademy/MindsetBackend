from __future__ import annotations

from collections.abc import Sequence

from app.dtos import PostCreate, PostOut, PostUpdate
from app.exceptions import ConflictError, NotFoundError
from app.repositories.blog import BlogRepository, IBlogRepository


class BlogService:
    """Application service for blog posts."""

    def __init__(self, repo: IBlogRepository | None = None) -> None:
        self.repo = repo or BlogRepository()

    def list_published(self, *, limit: int = 100, offset: int = 0) -> Sequence[PostOut]:
        rows = self.repo.list_published(limit=limit, offset=offset)
        return [PostOut.model_validate(r) for r in rows]

    def list_all(self, *, limit: int = 100, offset: int = 0) -> Sequence[PostOut]:
        rows = self.repo.list_posts(limit=limit, offset=offset)
        return [PostOut.model_validate(r) for r in rows]

    def get_by_id(self, post_id: int) -> PostOut:
        row = self.repo.get_post_by_id(post_id)
        if not row:
            raise NotFoundError("Post not found")
        return PostOut.model_validate(row)

    def get_by_slug(self, slug: str) -> PostOut:
        row = self.repo.get_post_by_slug(slug)
        if not row:
            raise NotFoundError("Post not found")
        return PostOut.model_validate(row)

    def search(self, q: str, *, limit: int = 100, offset: int = 0) -> Sequence[PostOut]:
        rows = self.repo.search_posts(q, limit=limit, offset=offset)
        return [PostOut.model_validate(r) for r in rows]

    def create_post(self, payload: PostCreate) -> PostOut:
        if self.repo.get_post_by_slug(payload.slug):
            raise ConflictError("Slug already exists")

        row = self.repo.create_post(
            slug=payload.slug,
            title=payload.title,
            content=payload.content,
            author_id=payload.author_id,
            summary=payload.summary,
            status=payload.status or "draft",
            published_at=payload.published_at,
        )
        return PostOut.model_validate(row)

    def update_post(self, post_id: int, payload: PostUpdate) -> PostOut:
        row = self.repo.update_post(
            post_id=post_id,
            slug=payload.slug,
            title=payload.title,
            content=payload.content,
            summary=payload.summary,
            status=payload.status,
            published_at=payload.published_at,
            author_id=payload.author_id,
        )
        if not row:
            raise NotFoundError("Post not found")
        return PostOut.model_validate(row)

    def delete_post(self, post_id: int) -> None:
        row = self.repo.delete_post(post_id)
        if not row:
            raise NotFoundError("Post not found")
