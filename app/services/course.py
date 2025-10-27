from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy.orm import Session, scoped_session

from app.db import db
from app.dtos import CourseCreateIn, CourseOut, CoursePastOut, CourseUpdateIn
from app.exceptions import NotFoundError
from app.models import Course
from app.repositories.course import CourseRepository, ICourseRepository


class CourseService:
    """Business logic for course-related operations.

    This service handles:
    - Converting between domain models and DTOs
    - Providing current timestamp for past-course calculations
    - Error handling and validation
    """

    def __init__(
        self,
        session: Session | scoped_session[Session] | None = None,
        repo: ICourseRepository | None = None,
    ) -> None:
        self.session = session or db.session
        self.repo = repo or CourseRepository(session)

    def list_courses(self) -> list[CoursePastOut]:
        """List all courses as DTOs.

        Returns:
            List of all courses ordered by date.
        """
        rows = self.repo.list_courses()
        return [CoursePastOut.model_validate(r) for r in rows]

    def get_course_by_id(self, course_id: int) -> CoursePastOut:
        """Get a specific course by ID.

        Args:
            course_id: Unique identifier of the course to retrieve.

        Returns:
            Course DTO with all relationships loaded.

        Raises:
            NotFoundError: If course doesn't exist.
        """
        row = self.repo.get_course_by_id(course_id)
        if not row:
            raise NotFoundError("Course not found")
        return CoursePastOut.model_validate(row)

    def list_past_courses(self) -> Sequence[CoursePastOut]:
        """List all past courses as DTOs.

        Returns:
            Sequence of past courses ordered by end date (desc), then ID.
            Each course includes its instructors, delivery mode, and venue.
        """
        rows = self.repo.list_past_courses()
        return [CoursePastOut.model_validate(r) for r in rows]

    def search_courses(self, q: str) -> list[CoursePastOut]:
        """Search all courses by title.

        Args:
            q: Case-insensitive search string to match against course titles.

        Returns:
            Matching courses ordered by date (desc), then ID.
            Empty sequence if no matches found.
        """
        rows = self.repo.search_courses(q)
        return [CoursePastOut.model_validate(r) for r in rows]

    def create_course(self, data: CourseCreateIn) -> CourseOut:
        """Create a new course using validated DTO."""
        row = self.repo.create_course(**data.model_dump())
        return CourseOut.model_validate(row)
    
    def update_course(self, course_id: int, data: CourseUpdateIn) -> CourseOut:
        """Update an existing course.
        
        Args:
            course_id: ID of course to update
            data: Validated update data
            
        Returns:
            Updated course DTO
            
        Raises:
            NotFoundError: If course doesn't exist
            ValueError: If update data is invalid
        """
        with self.session.begin():
            row = self.repo.update_course(course_id, **data.model_dump(exclude_none=True))
            if not row:
                raise NotFoundError(f"Course {course_id} not found")
        return CourseOut.model_validate(row)
    
    def delete_course(self, course_id: int) -> Course:
        """
        Delete an existing course.

        Args:
            course_id: ID of course to delete

        Raises:
            NotFoundError: If course does not exist
        """
        with self.session.begin():
            row = self.repo.delete_course(course_id)
            if row is None:
                raise NotFoundError(f"Course {course_id} not found")
            return row