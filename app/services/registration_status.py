from __future__ import annotations

from typing import Literal

from flask import current_app
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, scoped_session

from app.db import db
from app.dtos import (
    RegistrationStatusCreateDTO,
    RegistrationStatusReadDTO,
    RegistrationStatusUpdateDTO,
)
from app.exceptions import AlreadyExistsError, NotFoundError, ValidationError
from app.repositories.registration_status import RegistrationStatusRepository


class RegistrationStatusService:
    """Application service for RegistrationStatus (no paging/counts)."""

    def __init__(self, session: Session | scoped_session[Session] | None = None):
        self.session = session or db.session
        self.repo = RegistrationStatusRepository(self.session)

    def get(self, id_: int) -> RegistrationStatusReadDTO:
        m = self.repo.get_by_id(id_)
        if not m:
            raise NotFoundError(f"RegistrationStatus {id_} not found")
        return RegistrationStatusReadDTO.model_validate(m)

    def get_by_label(self, label: str) -> RegistrationStatusReadDTO:
        m = self.repo.get_by_label(label)
        if not m:
            raise NotFoundError(f"RegistrationStatus label={label!r} not found")
        return RegistrationStatusReadDTO.model_validate(m)

    def list(
        self,
        *,
        q: str | None = None,
        sort: Literal["id","label"] = "id",
        direction: Literal["asc", "desc"] = "desc",
    ) -> list[RegistrationStatusReadDTO]:
        rows = self.repo.list(q=q, sort=sort, direction=direction)
        return [RegistrationStatusReadDTO.model_validate(r) for r in rows]

    def create(self, payload: RegistrationStatusCreateDTO) -> RegistrationStatusReadDTO:
        label = payload.label
        self._validate_label(label)

        if self.repo.get_by_label(label):
            raise AlreadyExistsError(f"RegistrationStatus with label={label!r} already exists")

        try:
            with self.session.begin_nested():
                m = self.repo.create(label=label, description=payload.description)
            return RegistrationStatusReadDTO.model_validate(m)
        except IntegrityError as e:
            current_app.logger.exception("Integrity error creating RegistrationStatus")
            raise AlreadyExistsError(f"RegistrationStatus with label={label!r} already exists") from e

    def update(self, id_: int, payload: RegistrationStatusUpdateDTO) -> RegistrationStatusReadDTO:
        m = self.repo.get_by_id(id_)
        if not m:
            raise NotFoundError(f"RegistrationStatus {id_} not found")

        new_label = payload.label
        if new_label is not None:
            self._validate_label(new_label)
            if new_label != m.label and self.repo.get_by_label(new_label):
                raise AlreadyExistsError(f"RegistrationStatus with label={new_label!r} already exists")

        with self.session.begin():
            self.repo.update(m, label=new_label, description=payload.description)

        return RegistrationStatusReadDTO.model_validate(m)

    def delete(self, id_: int) -> None:
        m = self.repo.get_by_id(id_)
        if not m:
            raise NotFoundError(f"RegistrationStatus {id_} not found")
        with self.session.begin_nested():
            self.session.delete(m)

    @staticmethod
    def _validate_label(label: str) -> None:
        if not label or not label.strip():
            raise ValidationError("label is required")
        if len(label) > 64:
            raise ValidationError("label must be <= 64 characters")
