from __future__ import annotations

from typing import Literal

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, scoped_session

from app.db import db
from app.dtos import InstructorCreateDTO, InstructorReadDTO, InstructorUpdateDTO
from app.exceptions import AlreadyExistsError, NotFoundError, ValidationError
from app.repositories.instructor import IInstructorRepository, InstructorRepository


class InstructorService:
    """Service for instructor-related operations."""

    def __init__(
        self,
        session: Session | scoped_session[Session] | None = None,
        repo: IInstructorRepository | None = None,
    ):
        self.session = session or db.session
        self.repo = repo or InstructorRepository(self.session)

    def _validate(self, payload: InstructorCreateDTO | InstructorUpdateDTO) -> None:
        """Validate instructor data."""
        full_name = getattr(payload, "full_name", None)
        if full_name is not None and not full_name.strip():
            raise ValidationError("full_name cannot be empty")

    def get(self, id_: int) -> InstructorReadDTO:
        """Retrieve instructor by ID."""
        entity = self.repo.get_by_id(id_)
        if not entity:
            raise NotFoundError(f"Instructor {id_} not found")
        return InstructorReadDTO.model_validate(entity)

    def list(
        self,
        *,
        q: str | None = None,
        sort: Literal["id", "full_name"] = "full_name",
        direction: Literal["asc", "desc"] = "asc",
    ) -> list[InstructorReadDTO]:
        """List instructors with optional filtering."""
        rows = self.repo.list(q=q, sort=sort, direction=direction)
        return [InstructorReadDTO.model_validate(r) for r in rows]

    def create(self, payload: InstructorCreateDTO) -> InstructorReadDTO:
        """Create a new instructor."""
        self._validate(payload)

        if payload.email and self.repo.get_by_email(payload.email):
            raise AlreadyExistsError(f"Instructor with email={payload.email!r} already exists")

        try:
            with self.session.begin_nested():
                entity = self.repo.create(**payload.model_dump(exclude_none=True))
            return InstructorReadDTO.model_validate(entity)
        except IntegrityError as e:
            raise AlreadyExistsError("Instructor with this email or phone already exists") from e

    def update(self, id_: int, payload: InstructorUpdateDTO) -> InstructorReadDTO:
        """Update an existing instructor."""
        entity = self.repo.get_by_id(id_)
        if not entity:
            raise NotFoundError(f"Instructor {id_} not found")

        self._validate(payload)

        if payload.email and payload.email != entity.email:
            if self.repo.get_by_email(payload.email):
                raise AlreadyExistsError(f"Instructor with email={payload.email!r} already exists")

        with self.session.begin():
            self.repo.update(entity, **payload.model_dump(exclude_none=True))
        return InstructorReadDTO.model_validate(entity)

    def delete(self, id_: int) -> None:
        """Delete an instructor."""
        entity = self.repo.get_by_id(id_)
        if not entity:
            raise NotFoundError(f"Instructor {id_} not found")
        with self.session.begin_nested():
            self.session.delete(entity)
