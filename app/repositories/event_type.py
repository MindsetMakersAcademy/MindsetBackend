from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Literal, cast

from sqlalchemy import select
from sqlalchemy.orm import Session, scoped_session
from sqlalchemy.sql.elements import ColumnElement

from app.models import EventType
from app.repositories.base import BaseRepository


class IEventTypeRepository(ABC):
    @abstractmethod
    def get_by_id(self, id_: int) -> EventType | None: ...
    @abstractmethod
    def get_by_label(self, label: str) -> EventType | None: ...
    @abstractmethod
    def list(self, *, q: str | None = None, sort: str = "label",
             direction: Literal["asc","desc"] = "asc") -> list[EventType]: ...
    @abstractmethod
    def create(self, *, label: str, description: str | None = None) -> EventType: ...
    @abstractmethod
    def update(self, entity: EventType, *,
               label: str | None = None, description: str | None = None) -> EventType: ...

class EventTypeRepository(BaseRepository[EventType], IEventTypeRepository):
    def __init__(self, session: Session | scoped_session[Session]):
        super().__init__(session, EventType)

    def get_by_id(self, id_: int) -> EventType | None:
        return self.get(id_)

    def get_by_label(self, label: str) -> EventType | None:
        stmt = select(EventType).where(EventType.label == label)
        return self.session.execute(stmt).scalars().one_or_none()

    def _sort_column(self, key: str) -> ColumnElement[int | str]:
        if key == "id":
            return EventType.id
        return EventType.label

    def list(self, *, q: str | None = None, sort: str = "label",
             direction: Literal["asc","desc"] = "asc") -> list[EventType]:
        stmt = select(EventType)
        if q:
            stmt = stmt.where(EventType.label.ilike(f"%{q}%"))
        sort_col = self._sort_column(sort)
        stmt = stmt.order_by(sort_col.desc() if direction == "desc" else sort_col.asc())
        return cast(list[EventType], self.session.execute(stmt).scalars().all())

    def create(self, *, label: str, description: str | None = None) -> EventType:
        e = EventType(label=label, description=description)
        self.add(e)
        return e

    def update(self, entity: EventType, *,
               label: str | None = None, description: str | None = None) -> EventType:
        if label is not None:
            entity.label = label
        if description is not None:
            entity.description = description
        return entity
