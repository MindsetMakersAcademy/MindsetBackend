from __future__ import annotations

from datetime import date, datetime
from zoneinfo import ZoneInfo

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Index,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base, db

TEHRAN_TZ = ZoneInfo("Asia/Tehran")


class DeliveryMode(Base):
    __tablename__ = "delivery_modes"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    label: Mapped[str] = mapped_column(db.String(160), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(db.Text, nullable=True)


class RegistrationStatus(Base):
    __tablename__ = "registration_statuses"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    label: Mapped[str] = mapped_column(db.String(160), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(db.Text, nullable=True)


class User(Base):
    """The course attendants."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    full_name: Mapped[str] = mapped_column(db.String(160), nullable=False, index=True)
    email: Mapped[str] = mapped_column(db.String(160), nullable=False, unique=True)
    phone: Mapped[str | None] = mapped_column(db.String(40), nullable=True, unique=True)
    created_at: Mapped[datetime] = mapped_column(
        db.DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        db.DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (CheckConstraint("full_name <> ''", name="ck_user_full_name_not_empty"),)


class Venue(Base):
    __tablename__ = "venues"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(db.String(160), nullable=False, index=True)
    address: Mapped[str | None] = mapped_column(db.Text, nullable=True)
    map_url: Mapped[str | None] = mapped_column(db.Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(db.Text, nullable=True)
    room_capacity: Mapped[int | None] = mapped_column(db.Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        db.DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        db.DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        CheckConstraint(
            "room_capacity IS NULL OR room_capacity > 0", name="ck_venue_room_capacity_pos"
        ),
    )


course_instructors = db.Table(
    "course_instructors",
    db.metadata,
    db.Column("course_id", ForeignKey("courses.id", ondelete="CASCADE"), primary_key=True),
    db.Column("instructor_id", ForeignKey("instructors.id", ondelete="CASCADE"), primary_key=True),
    db.Index("ix_course_instructor_course", "course_id"),
    db.Index("ix_course_instructor_instructor", "instructor_id"),
)


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    title: Mapped[str] = mapped_column(db.String(160), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(db.Text, nullable=True)

    delivery_mode_id: Mapped[int] = mapped_column(
        ForeignKey("delivery_modes.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    delivery_mode: Mapped[DeliveryMode] = relationship(lazy="joined")

    venue_id: Mapped[int | None] = mapped_column(
        ForeignKey("venues.id", ondelete="SET NULL"), nullable=True, index=True
    )
    venue: Mapped[Venue | None] = relationship(lazy="joined")

    capacity: Mapped[int | None] = mapped_column(db.Integer, nullable=True)
    session_counts: Mapped[int | None] = mapped_column(db.Integer, nullable=True)
    session_duration_minutes: Mapped[int | None] = mapped_column(db.Integer, nullable=True)
    start_date: Mapped[date | None] = mapped_column(db.Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(db.Date, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        db.DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        db.DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    instructors: Mapped[list[Instructor]] = relationship(
        secondary=course_instructors,
        back_populates="courses",
        lazy="selectin",
        passive_deletes=True,
    )
    registrations: Mapped[list[Registration]] = relationship(
        back_populates="course",
        lazy="selectin",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    __table_args__ = (
        CheckConstraint("capacity IS NULL OR capacity > 0", name="ck_course_capacity_pos"),
        CheckConstraint(
            "session_counts IS NULL OR session_counts >= 0", name="ck_course_session_counts_nonneg"
        ),
        CheckConstraint(
            "session_duration_minutes IS NULL OR session_duration_minutes > 0",
            name="ck_course_session_duration_pos",
        ),
        CheckConstraint(
            "(start_date IS NULL OR end_date IS NULL) OR (start_date <= end_date)",
            name="ck_course_date_range",
        ),
    )


class Instructor(Base):
    __tablename__ = "instructors"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    full_name: Mapped[str] = mapped_column(db.String(120), nullable=False, index=True)
    phone: Mapped[str | None] = mapped_column(db.String(40), nullable=True, unique=True)
    email: Mapped[str | None] = mapped_column(db.String(160), unique=True, nullable=True)
    bio: Mapped[str | None] = mapped_column(db.Text, nullable=True)

    courses: Mapped[list[Course]] = relationship(
        secondary=course_instructors,
        back_populates="instructors",
        lazy="selectin",
        passive_deletes=True,
    )


class Registration(Base):
    __tablename__ = "registrations"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)

    course_id: Mapped[int] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True
    )
    course: Mapped[Course] = relationship(back_populates="registrations", lazy="joined")

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user: Mapped[User] = relationship(lazy="joined")

    status_id: Mapped[int] = mapped_column(
        ForeignKey("registration_statuses.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    status: Mapped[RegistrationStatus] = relationship(lazy="joined")

    submitted_at: Mapped[datetime] = mapped_column(
        db.DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        db.DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (UniqueConstraint("course_id", "user_id", name="uq_registration_course_user"),)


class EventType(Base):
    """
    Lookup for event types (e.g., book_club, webinar, talk).
    """

    __tablename__ = "event_types"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    label: Mapped[str] = mapped_column(db.String(160), nullable=False)
    description: Mapped[str | None] = mapped_column(db.Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        db.DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        db.DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )


class Event(Base):
    """
    Lightweight occurrences like a book-club session, talk, or meetup.
    Uses DeliveryMode lookup too (consistent with Course).
    """

    __tablename__ = "events"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    title: Mapped[str] = mapped_column(db.String(160), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(db.Text, nullable=True)

    event_type_id: Mapped[int] = mapped_column(
        ForeignKey("event_types.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    event_type: Mapped[EventType] = relationship(lazy="joined")

    delivery_mode_id: Mapped[int] = mapped_column(
        ForeignKey("delivery_modes.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    delivery_mode: Mapped[DeliveryMode] = relationship(lazy="joined")

    venue_id: Mapped[int | None] = mapped_column(
        ForeignKey("venues.id", ondelete="SET NULL"), nullable=True, index=True
    )
    venue: Mapped[Venue | None] = relationship(lazy="joined")

    capacity: Mapped[int | None] = mapped_column(db.Integer, nullable=True)
    starts_at: Mapped[datetime | None] = mapped_column(db.DateTime(timezone=True), nullable=True)
    ends_at: Mapped[datetime | None] = mapped_column(db.DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        db.DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        db.DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        CheckConstraint("capacity IS NULL OR capacity > 0", name="ck_event_capacity_pos"),
        CheckConstraint(
            "(starts_at IS NULL OR ends_at IS NULL) OR (ends_at > starts_at)",
            name="ck_event_timespan",
        ),
    )


class Admin(Base):
    """Admin"""

    __tablename__ = "admin"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    email: Mapped[str] = mapped_column(db.String(160), nullable=False, unique=True, index=True)
    full_name: Mapped[str] = mapped_column(db.String(160), nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(db.String(256), nullable=False)
    is_active: Mapped[bool] = mapped_column(db.Boolean, nullable=False, server_default=db.text("1"))
    created_at: Mapped[datetime] = mapped_column(
        db.DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        db.DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    posts: Mapped[list[BlogPost]] = relationship(back_populates="author", lazy="selectin")

    __table_args__ = (
        CheckConstraint("email <> ''", name="ck_admin_email_not_empty"),
        CheckConstraint("full_name <> ''", name="ck_admin_full_name_not_empty"),
    )


class BlogPost(Base):
    __tablename__ = "blog_posts"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(db.String(160), nullable=False, unique=True, index=True)
    title: Mapped[str] = mapped_column(db.String(160), nullable=False, index=True)
    summary: Mapped[str | None] = mapped_column(db.String(300), nullable=True)
    content: Mapped[str] = mapped_column(db.Text, nullable=False)

    status: Mapped[str] = mapped_column(db.String(20), nullable=False, server_default="draft")
    published_at: Mapped[datetime | None] = mapped_column(db.DateTime(timezone=True), nullable=True)

    author_id: Mapped[int] = mapped_column(
        ForeignKey("admin.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    author: Mapped[Admin] = relationship(back_populates="posts", lazy="joined")

    created_at: Mapped[datetime] = mapped_column(
        db.DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        db.DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        UniqueConstraint("slug", name="uq_blog_slug"),
        Index("ix_blog_status_published_at", "status", "published_at"),
        CheckConstraint("title <> ''", name="ck_blog_title_not_empty"),
        CheckConstraint("content <> ''", name="ck_blog_content_not_empty"),
    )
