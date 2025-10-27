from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Literal, cast

from sqlalchemy import select
from sqlalchemy.orm import Session, scoped_session
from sqlalchemy.sql.elements import ColumnElement

from app.models import DeliveryMode
from app.repositories.base import BaseRepository


class IDeliveryModeRepository(ABC):
    @abstractmethod
    def get_by_id(self, id_: int) -> DeliveryMode | None: ...
    @abstractmethod
    def get_by_label(self, label: str) -> DeliveryMode | None: ...
    @abstractmethod
    def list(self, *, q: str | None = None, sort: str = "label",
             direction: Literal["asc","desc"] = "asc") -> list[DeliveryMode]: ...
    @abstractmethod
    def create(self, *, label: str, description: str | None = None) -> DeliveryMode: ...
    @abstractmethod
    def update(self, entity: DeliveryMode, *,
               label: str | None = None, description: str | None = None) -> DeliveryMode: ...

class DeliveryModeRepository(BaseRepository[DeliveryMode], IDeliveryModeRepository):
    def __init__(self, session: Session | scoped_session[Session]):
        super().__init__(session, DeliveryMode)

    def get_by_id(self, id_: int) -> DeliveryMode | None:
        return self.get(id_)

    def get_by_label(self, label: str) -> DeliveryMode | None:
        stmt = select(DeliveryMode).where(DeliveryMode.label == label)
        return self.session.execute(stmt).scalars().one_or_none()

    def _sort_column(self, key: str) -> ColumnElement[int | str]:
        if key == "id":
            return DeliveryMode.id
        return DeliveryMode.label

    def list(self, *, q: str | None = None, sort: str = "label",
             direction: Literal["asc","desc"] = "asc") -> list[DeliveryMode]:
        stmt = select(DeliveryMode)
        if q:
            stmt = stmt.where(DeliveryMode.label.ilike(f"%{q}%"))
        sort_col = self._sort_column(sort)
        stmt = stmt.order_by(sort_col.desc() if direction == "desc" else sort_col.asc())
        return cast(list[DeliveryMode], self.session.execute(stmt).scalars().all())

    def create(self, *, label: str, description: str | None = None) -> DeliveryMode:
        e = DeliveryMode(label=label, description=description)
        self.add(e)
        return e

    def update(self, entity: DeliveryMode, *,
               label: str | None = None, description: str | None = None) -> DeliveryMode:
        if label is not None:
            entity.label = label
        if description is not None:
            entity.description = description
        return entity
