from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Literal, cast

from sqlalchemy import select
from sqlalchemy.orm import Session, scoped_session
from sqlalchemy.orm.attributes import InstrumentedAttribute

from app.models import Instructor
from app.repositories.base import BaseRepository


class IInstructorRepository(ABC):
    """Abstract interface for Instructor repository."""

    @abstractmethod
    def get_by_id(self, id_: int) -> Instructor | None:
        """Retrieve instructor by ID."""
        ...

    @abstractmethod
    def get_by_email(self, email: str) -> Instructor | None:
        """Retrieve instructor by email."""
        ...

    @abstractmethod
    def list(
        self,
        *,
        q: str | None = None,
        sort: str = "full_name",
        direction: Literal["asc", "desc"] = "asc",
    ) -> list[Instructor]:
        """List instructors with optional filtering and sorting."""
        ...

    @abstractmethod
    def create(
        self,
        *,
        full_name: str,
        email: str | None = None,
        phone: str | None = None,
        bio: str | None = None,
    ) -> Instructor:
        """Create a new instructor."""
        ...

    @abstractmethod
    def update(
        self,
        entity: Instructor,
        *,
        full_name: str | None = None,
        email: str | None = None,
        phone: str | None = None,
        bio: str | None = None,
    ) -> Instructor:
        """Update an existing instructor."""
        ...


class InstructorRepository(BaseRepository[Instructor], IInstructorRepository):
    """Repository implementation for Instructor entities."""

    def __init__(self, session: Session | scoped_session[Session]):
        super().__init__(session, Instructor)

    def get_by_id(self, id_: int) -> Instructor | None:
        return self.get(id_)

    def get_by_email(self, email: str) -> Instructor | None:
        stmt = select(Instructor).where(Instructor.email == email)
        return self.session.execute(stmt).scalars().one_or_none()

    def _sort_column(self, key: str) -> InstrumentedAttribute[int] | InstrumentedAttribute[str]:
        if key == "id":
            return Instructor.id
        return Instructor.full_name

    def list(
        self,
        *,
        q: str | None = None,
        sort: str = "full_name",
        direction: Literal["asc", "desc"] = "asc",
    ) -> list[Instructor]:
        stmt = select(Instructor)
        if q:
            stmt = stmt.where(Instructor.full_name.ilike(f"%{q}%"))
        sort_col = self._sort_column(sort)
        stmt = stmt.order_by(sort_col.desc() if direction == "desc" else sort_col.asc())
        return cast(list[Instructor], self.session.execute(stmt).scalars().all())

    def create(
        self,
        *,
        full_name: str,
        email: str | None = None,
        phone: str | None = None,
        bio: str | None = None,
    ) -> Instructor:
        entity = Instructor(full_name=full_name, email=email, phone=phone, bio=bio)
        self.add(entity)
        return entity

    def update(
        self,
        entity: Instructor,
        *,
        full_name: str | None = None,
        email: str | None = None,
        phone: str | None = None,
        bio: str | None = None,
    ) -> Instructor:
        if full_name is not None:
            entity.full_name = full_name
        if email is not None:
            entity.email = email
        if phone is not None:
            entity.phone = phone
        if bio is not None:
            entity.bio = bio
        return entity
