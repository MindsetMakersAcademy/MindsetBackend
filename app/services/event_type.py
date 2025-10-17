# app/services/event_type.py
from __future__ import annotations

from typing import Literal

from flask import current_app
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, scoped_session

from app.db import db
from app.dtos import EventTypeCreateDTO, EventTypeReadDTO, EventTypeUpdateDTO
from app.exceptions import AlreadyExistsError, NotFoundError, ValidationError
from app.repositories.event_type import EventTypeRepository


class EventTypeService:
    def __init__(self, session: Session | scoped_session[Session] | None = None):
        self.session = session or db.session
        self.repo = EventTypeRepository(self.session)

    def _validate_label(self, label: str) -> None:
        if not label or not label.strip():
            raise ValidationError("label is required")
        if len(label) > 160:
            raise ValidationError("label must be <= 160 characters")

    def get(self, id_: int) -> EventTypeReadDTO:
        m = self.repo.get_by_id(id_)
        if not m:
            raise NotFoundError(f"EventType {id_} not found")
        return EventTypeReadDTO.model_validate(m)

    def get_by_label(self, label: str) -> EventTypeReadDTO:
        m = self.repo.get_by_label(label)
        if not m:
            raise NotFoundError(f"EventType label={label!r} not found")
        return EventTypeReadDTO.model_validate(m)

    def list(
        self,
        *,
        q: str | None = None,
        sort: Literal["id", "label"] = "label",
        direction: Literal["asc", "desc"] = "asc",
    ) -> list[EventTypeReadDTO]:
        rows = self.repo.list(q=q, sort=sort, direction=direction)
        return [EventTypeReadDTO.model_validate(r) for r in rows]

    def create(self, payload: EventTypeCreateDTO) -> EventTypeReadDTO:
        label = payload.label
        self._validate_label(label)
        if self.repo.get_by_label(label):
            raise AlreadyExistsError(f"EventType with label={label!r} already exists")
        try:
            with self.session.begin_nested():
                m = self.repo.create(label=label, description=payload.description)
            return EventTypeReadDTO.model_validate(m)
        except IntegrityError as e:
            current_app.logger.exception("Integrity error creating EventType")
            raise AlreadyExistsError(f"EventType with label={label!r} already exists") from e

    def update(self, id_: int, payload: EventTypeUpdateDTO) -> EventTypeReadDTO:
        m = self.repo.get_by_id(id_)
        if not m:
            raise NotFoundError(f"EventType {id_} not found")
        if payload.label is not None:
            self._validate_label(payload.label)
            if payload.label != m.label and self.repo.get_by_label(payload.label):
                raise AlreadyExistsError(f"EventType with label={payload.label!r} already exists")
        with self.session.begin():
            self.repo.update(m, label=payload.label, description=payload.description)
        return EventTypeReadDTO.model_validate(m)

    def delete(self, id_: int) -> None:
        m = self.repo.get_by_id(id_)
        if not m:
            raise NotFoundError(f"EventType {id_} not found")
        with self.session.begin_nested():
            self.session.delete(m)
