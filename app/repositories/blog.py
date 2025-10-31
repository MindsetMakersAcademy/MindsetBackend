from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from datetime import datetime
from typing import Any, Literal

from sqlalchemy import Select, select
from sqlalchemy.orm import Session, scoped_session, selectinload

from app.db import db
from app.models import BlogPost
from app.repositories.base import BaseRepository


class IBlogRepository(ABC):
    """
    CRUD interface for blog posts.
    """

    @abstractmethod
    def list_posts(self, *, limit: int = 100, offset: int = 0) -> Sequence[BlogPost]:
        """List posts (any status), newest first."""
        ...

    @abstractmethod
    def list_published(self, *, limit: int = 100, offset: int = 0) -> Sequence[BlogPost]:
        """List only published posts, ordered by published_at desc."""
        ...

    @abstractmethod
    def get_post_by_id(self, post_id: int) -> BlogPost | None:
        """Get a post by id."""
        ...

    @abstractmethod
    def get_post_by_slug(self, slug: str) -> BlogPost | None:
        """Get a post by unique slug."""
        ...

    @abstractmethod
    def search_posts(self, q: str, *, limit: int = 100, offset: int = 0) -> Sequence[BlogPost]:
        """Case-insensitive search over title/summary/content."""
        ...

    @abstractmethod
    def create_post(
        self,
        *,
        slug: str,
        title: str,
        content: str,
        author_id: int,
        summary: str | None = None,
        status: Literal["draft", "published", "archived"] = "draft",
        published_at: datetime | None = None,
        **kwargs: Any,
    ) -> BlogPost:
        """Create a post and return it fully loaded."""
        ...

    @abstractmethod
    def update_post(
        self,
        post_id: int,
        *,
        slug: str | None = None,
        title: str | None = None,
        content: str | None = None,
        summary: str | None = None,
        status: str | None = None,
        published_at: datetime | None = None,
        author_id: int | None = None,
        **kwargs: Any,
    ) -> BlogPost | None:
        """Update a post and return it fully loaded (None if not found)."""
        ...

    @abstractmethod
    def delete_post(self, post_id: int) -> BlogPost | None:
        """Delete a post and return the deleted row (None if not found)."""
        ...


class BlogRepository(BaseRepository[BlogPost], IBlogRepository):
    """
    Repository for BlogPost.

    - Eager-loads `author` to avoid N+1 on reads.
    - Commits inside write methods for simplicity (matches your BaseRepository.save style).
    """

    def __init__(self, session: Session | scoped_session[Session] | None = None) -> None:
        super().__init__(session or db.session, BlogPost)

    def _base_query(self) -> Select[tuple[BlogPost]]:
        return select(BlogPost).options(selectinload(BlogPost.author))

    def _get_fully_loaded(self, post_id: int) -> BlogPost | None:
        stmt = self._base_query().where(BlogPost.id == post_id)
        return self.session.execute(stmt).scalars().first()

    def list_posts(self, *, limit: int = 100, offset: int = 0) -> Sequence[BlogPost]:
        stmt = self._base_query().order_by(BlogPost.id.desc()).limit(limit).offset(offset)
        return self.session.execute(stmt).scalars().all()

    def list_published(self, *, limit: int = 100, offset: int = 0) -> Sequence[BlogPost]:
        stmt = (
            self._base_query()
            .where(BlogPost.status == "published")
            .order_by(BlogPost.published_at.desc().nulls_last(), BlogPost.id.desc())
            .limit(limit)
            .offset(offset)
        )
        return self.session.execute(stmt).scalars().all()

    def get_post_by_id(self, post_id: int) -> BlogPost | None:
        return self._get_fully_loaded(post_id)

    def get_post_by_slug(self, slug: str) -> BlogPost | None:
        stmt = self._base_query().where(BlogPost.slug == slug)
        return self.session.execute(stmt).scalars().first()

    def search_posts(self, q: str, *, limit: int = 100, offset: int = 0) -> Sequence[BlogPost]:
        q = (q or "").strip()
        if not q:
            return []
        like = f"%{q.lower()}%"
        stmt = (
            self._base_query()
            .where(
                db.func.lower(BlogPost.title).like(like)
                | db.func.lower(BlogPost.summary).like(like)
                | db.func.lower(BlogPost.content).like(like)
            )
            .order_by(BlogPost.published_at.desc().nulls_last(), BlogPost.id.desc())
            .limit(limit)
            .offset(offset)
        )
        return self.session.execute(stmt).scalars().all()

    def create_post(
        self,
        *,
        slug: str,
        title: str,
        content: str,
        author_id: int,
        summary: str | None = None,
        status: str = "draft",
        published_at: datetime | None = None,
        **kwargs: Any,
    ) -> BlogPost:
        post = BlogPost(
            slug=slug,
            title=title,
            summary=summary,
            content=content,
            status=status,
            published_at=published_at,
            author_id=author_id,
            **kwargs,
        )
        self.session.add(post)
        self.session.commit()
        return self._get_fully_loaded(post.id) or post

    def update_post(
        self,
        post_id: int,
        *,
        slug: str | None = None,
        title: str | None = None,
        content: str | None = None,
        summary: str | None = None,
        status: str | None = None,
        published_at: datetime | None = None,
        author_id: int | None = None,
        **kwargs: Any,
    ) -> BlogPost | None:
        post = self.get_post_by_id(post_id)
        if not post:
            return None

        if slug is not None:
            post.slug = slug
        if title is not None:
            post.title = title
        if summary is not None:
            post.summary = summary
        if content is not None:
            post.content = content
        if status is not None:
            post.status = status
        if published_at is not None:
            post.published_at = published_at
        if author_id is not None:
            post.author_id = author_id

        for k, v in kwargs.items():
            if v is not None and hasattr(post, k):
                setattr(post, k, v)

        self.session.commit()
        return self._get_fully_loaded(post.id)

    def delete_post(self, post_id: int) -> BlogPost | None:
        post = self.get_post_by_id(post_id)
        if not post:
            return None
        self.session.delete(post)
        self.session.commit()
        return post
