from __future__ import annotations

from typing import Literal, cast

from sqlalchemy import select
from sqlalchemy.orm import Session, scoped_session
from sqlalchemy.sql.elements import ColumnElement

from app.models import Venue
from app.repositories.base import BaseRepository


class VenueRepository(BaseRepository[Venue]):
    def __init__(self, session: Session | scoped_session[Session]):
        super().__init__(session, Venue)

    def _sort_column(self, key: str) -> ColumnElement[int | str]:
        return Venue.id if key == "id" else Venue.name

    def list(
        self, *, q: str | None = None, sort: str = "name", direction: Literal["asc", "desc"] = "asc"
    ) -> list[Venue]:
        stmt = select(Venue)
        if q:
            stmt = stmt.where(Venue.name.ilike(f"%{q}%"))
        sort_col = self._sort_column(sort)
        stmt = stmt.order_by(sort_col.desc() if direction == "desc" else sort_col.asc())
        return cast(list[Venue], self.session.execute(stmt).scalars().all())

    def create(self, **kwargs) -> Venue:
        e = Venue(**kwargs)
        self.add(e)
        return e

    def update(self, entity: Venue, **kwargs) -> Venue:
        for k, v in kwargs.items():
            if v is not None:
                setattr(entity, k, v)
        return entity
