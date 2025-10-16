from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db import db
from app.models import Course, Instructor


class ICourseRepository(ABC):
    """
    This interface defines all CRUD operations for courses.
    """

    @abstractmethod
    def list_courses(self) -> Sequence[Course]:
        """List all courses ordered by end date (descending), then by ID.
        
        Returns:
            Sequence of all courses with relationships loaded.
        """
        ...
        
    @abstractmethod
    def get_course_by_id(self, course_id: int) -> Course | None:
        """Get a specific course by ID.
        
        Args:
            course_id: Unique identifier of the course.
            
        Returns:
            The course if found, None otherwise.
        """
        ...
        
    @abstractmethod
    def list_past_courses(self) -> Sequence[Course]:
        """List all courses that have ended.
        
        Returns:
            Sequence of past courses ordered by end date (descending), then by ID.
        """
        ...
        
    @abstractmethod
    def list_upcoming_courses(self) -> Sequence[Course]:
        """List all courses that have not started yet.
        
        Returns:
            Sequence of upcoming courses ordered by start date (ascending), then by ID.
        """
        ...
        
    @abstractmethod
    def search_courses(self, q: str) -> Sequence[Course]:
        """Search courses by title (case-insensitive partial match).
        
        Args:
            q: Search query string to match against course titles.
        
        Returns:
            Matching courses ordered by relevance, then by date.
        """
        ...
        
    @abstractmethod
    def create_course(
        self,
        *,
        title: str,
        description: str | None,
        delivery_mode_id: int,
        venue_id: int | None,
        instructor_ids: list[int],
        start_date: datetime | None,
        end_date: datetime | None,
        **kwargs: Any,
    ) -> Course:
        """Create a new course.
        
        Args:
            title: Course title
            description: Optional course description
            delivery_mode_id: ID of delivery mode (online/in-person)
            venue_id: Optional ID of venue
            instructor_ids: List of instructor IDs to assign
            start_date: Optional course start date
            end_date: Optional course end date
            **kwargs: Additional course fields
            
        Returns:
            The created course with all relationships loaded.
            
        Raises:
            ValueError: If course data is invalid
            IntegrityError: If referenced entities don't exist
        """
        ...


class CourseRepository(ICourseRepository):
    """SQLAlchemy-based implementation of ICourseRepository.
    
    This implementation uses eager loading of relationships (instructors,
    delivery mode, venue) for optimal performance.
    """
    
    def __init__(self, session: Any = None) -> None:
        """Initialize repository with optional session.
        
        Args:
            session: SQLAlchemy session to use. If None, uses db.session.
        """
        self.session = session or db.session
    
    def _base_query(self):
        """Build base SQLAlchemy query with eager loading.
        
        Returns:
            SQLAlchemy select statement with eager loading of related entities.
        """
        return (
            select(Course)
            .options(
                selectinload(Course.instructors),
                selectinload(Course.delivery_mode),
                selectinload(Course.venue),
            )
        )

    def list_courses(self) -> Sequence[Course]:
        stmt = (
            self._base_query()
            .order_by(Course.end_date.desc().nulls_last(), Course.id.desc())
        )
        return self.session.execute(stmt).scalars().all()

    def get_course_by_id(self, course_id: int) -> Course | None:
        stmt = self._base_query().where(Course.id == course_id)
        return self.session.execute(stmt).scalars().first()

    def list_past_courses(self) -> Sequence[Course]:
        now = datetime.now(UTC).date()
        stmt = (
            self._base_query()
            .where(Course.end_date.is_not(None), Course.end_date < now)
            .order_by(Course.end_date.desc(), Course.id.desc())
        )
        return self.session.execute(stmt).scalars().all()

    def list_upcoming_courses(self) -> Sequence[Course]:
        now = datetime.now(UTC).date()
        stmt = (
            self._base_query()
            .where(Course.start_date.is_not(None), Course.start_date > now)
            .order_by(Course.start_date.asc(), Course.id.asc())
        )
        return self.session.execute(stmt).scalars().all()

    def search_courses(self, q: str) -> Sequence[Course]:
        like = f"%{q.lower()}%"
        stmt = (
            self._base_query()
            .where(db.func.lower(Course.title).like(like))
            .order_by(Course.start_date.desc().nulls_last(), Course.id.desc())
        )
        return self.session.execute(stmt).scalars().all()

    def create_course(
        self,
        *,
        title: str,
        description: str | None = None,
        delivery_mode_id: int,
        venue_id: int | None = None,
        instructor_ids: list[int],
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        **kwargs: Any,
    ) -> Course:
        start_date = start_date.date() if start_date else None  
        end_date = end_date.date() if end_date else None

        course = Course(
            title=title,
            description=description,
            delivery_mode_id=delivery_mode_id,
            venue_id=venue_id,
            start_date=start_date,
            end_date=end_date,
            **kwargs
        )
        
        if instructor_ids:
            instructors = (
                self.session.execute(
                    select(Instructor).where(Instructor.id.in_(instructor_ids))
                )
                .scalars()
                .all()
            )
            if len(instructors) != len(instructor_ids):
                raise ValueError("One or more instructor IDs not found")
            course.instructors.extend(instructors)

        self.session.add(course)
        self.session.flush()
        
        return course
