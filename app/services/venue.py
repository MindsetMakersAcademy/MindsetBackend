# app/services/venue.py
from __future__ import annotations

from typing import Literal

from sqlalchemy.orm import Session, scoped_session

from app.db import db
from app.dtos import VenueCreateDTO, VenueReadDTO, VenueUpdateDTO
from app.exceptions import NotFoundError, ValidationError
from app.repositories.venue import VenueRepository


class VenueService:
    def __init__(self, session: Session | scoped_session[Session] | None = None):
        self.session = session or db.session
        self.repo = VenueRepository(self.session)

    def _validate(self, payload: VenueCreateDTO | VenueUpdateDTO) -> None:
        name = getattr(payload, "name", None)
        if name is not None and not name.strip():
            raise ValidationError("name cannot be empty")
        cap = getattr(payload, "room_capacity", None)
        if cap is not None and cap <= 0:
            raise ValidationError("room_capacity must be positive")

    def get(self, id_: int) -> VenueReadDTO:
        m = self.repo.get(id_)
        if not m:
            raise NotFoundError(f"Venue {id_} not found")
        return VenueReadDTO.model_validate(m)

    def list(
        self,
        *,
        q: str | None = None,
        sort: Literal["id", "name"] = "name",
        direction: Literal["asc", "desc"] = "asc",
    ) -> list[VenueReadDTO]:
        rows = self.repo.list(q=q, sort=sort, direction=direction)
        return [VenueReadDTO.model_validate(r) for r in rows]

    def create(self, payload: VenueCreateDTO) -> VenueReadDTO:
        self._validate(payload)
        with self.session.begin_nested():
            m = self.repo.create(**payload.model_dump(exclude_none=True))
        return VenueReadDTO.model_validate(m)

    def update(self, id_: int, payload: VenueUpdateDTO) -> VenueReadDTO:
        m = self.repo.get(id_)
        if not m:
            raise NotFoundError(f"Venue {id_} not found")
        self._validate(payload)
        with self.session.begin():
            self.repo.update(m, **payload.model_dump(exclude_none=True))
        return VenueReadDTO.model_validate(m)

    def delete(self, id_: int) -> None:
        m = self.repo.get(id_)
        if not m:
            raise NotFoundError(f"Venue {id_} not found")
        with self.session.begin_nested():
            self.session.delete(m)
