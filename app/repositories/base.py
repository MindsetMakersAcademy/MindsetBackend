from __future__ import annotations

from collections.abc import Sequence
from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session, scoped_session

from ..db import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    def __init__(self, session: Session | scoped_session[Session], model: type[ModelT]):
        self.session = session
        self.model: type[ModelT] = model

    def get(self, id_: int) -> ModelT | None:
        return self.session.get(self.model, id_)

    def add(self, entity: ModelT) -> ModelT:
        self.session.add(entity)
        return entity

    def delete(self, entity: ModelT) -> None:
        self.session.delete(entity)

    def list_all(self, limit: int = 100, offset: int = 0) -> Sequence[ModelT]:
        stmt = select(self.model).limit(limit).offset(offset)
        rows = self.session.execute(stmt).scalars().all()
        return rows
