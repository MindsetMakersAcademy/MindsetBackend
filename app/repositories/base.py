from __future__ import annotations

from collections.abc import Sequence
from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session, scoped_session

from ..db import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """
    Generic base repository providing simple CRUD operations for SQLAlchemy models.

    This class is meant to be subclassed or composed by domain-specific repositories
    (e.g., `BlogRepository`, `AdminRepository`, etc.) that provide richer behavior.

    Example
    -------
    ```python
    from app.db import db
    from app.models import BlogPost

    class BlogRepository(BaseRepository[BlogPost]):
        def __init__(self) -> None:
            super().__init__(db.session, BlogPost)
    ```
    """

    def __init__(self, session: Session | scoped_session[Session], model: type[ModelT]):
        """
        Initialize a repository bound to a SQLAlchemy session and a model.

        Parameters
        ----------
        session : Session | scoped_session[Session]
            Active SQLAlchemy session or scoped session.
        model : type[ModelT]
            The SQLAlchemy declarative model class managed by this repository.
        """
        self.session = session
        self.model: type[ModelT] = model

    def get(self, id_: int) -> ModelT | None:
        """
        Retrieve a single record by primary key.

        Parameters
        ----------
        id_ : int
            Primary key of the record.

        Returns
        -------
        ModelT | None
            The found model instance, or None if not found.
        """
        return self.session.get(self.model, id_)

    def add(self, entity: ModelT) -> ModelT:
        """
        Add a new entity to the database.

        Parameters
        ----------
        entity : ModelT
            The instance to persist.

        Returns
        -------
        ModelT
            The persisted entity (same instance).
        """
        self.session.add(entity)
        return entity

    def delete(self, entity: ModelT) -> None:
        """
        Delete an entity from the database.

        Parameters
        ----------
        entity : ModelT
            The instance to delete.
        """
        self.session.delete(entity)

    def list_all(self, limit: int = 100, offset: int = 0) -> Sequence[ModelT]:
        """
        Retrieve a paginated list of all entities of this model.

        Parameters
        ----------
        limit : int, default 100
            Maximum number of results to return.
        offset : int, default 0
            Offset into the result set.

        Returns
        -------
        Sequence[ModelT]
            List of model instances.
        """
        stmt = select(self.model).limit(limit).offset(offset)
        return self.session.execute(stmt).scalars().all()

    def save(self, entity: ModelT) -> ModelT:
        """
        Persist and refresh an entity immediately.

        This is a convenience method for cases where you want to save
        and commit within the repository scope (e.g., simple scripts or seeds).

        Parameters
        ----------
        entity : ModelT
            The instance to persist.

        Returns
        -------
        ModelT
            The persisted and refreshed entity.
        """
        self.session.add(entity)
        self.session.commit()
        self.session.refresh(entity)
        return entity
