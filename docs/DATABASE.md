# BlogPost
Represents blog posts authored by admins.

| Column        | Type         | Constraints                | Description                  |
|--------------|--------------|----------------------------|------------------------------|
| id           | Integer      | Primary Key                | Unique identifier            |
| slug         | String(160)  | Not Null, Unique, Indexed  | URL slug for the post        |
| title        | String(160)  | Not Null, Indexed          | Post title                   |
| summary      | String(300)  | Nullable                   | Short summary                |
| content      | Text         | Not Null                   | Full post content            |
| status       | String(20)   | Not Null, Default: draft   | Post status (draft/published)|
| published_at | DateTime     | Nullable                   | Publish timestamp            |
| author_id    | Integer      | Foreign Key, Not Null      | Reference to Admin           |
| created_at   | DateTime     | Not Null, Default: now()   | Record creation timestamp    |
| updated_at   | DateTime     | Not Null, Default: now()   | Last update timestamp        |

**Relationships:**
- Many-to-One with Admin (author)

# Admin
Represents admin users who manage the system and author blog posts.

| Column      | Type         | Constraints                | Description                  |
|-------------|--------------|----------------------------|------------------------------|
| id          | Integer      | Primary Key                | Unique identifier            |
| email       | String(160)  | Not Null, Unique, Indexed  | Admin email                  |
| full_name   | String(160)  | Not Null, Indexed          | Admin full name              |
| password_hash | String(256)| Not Null                   | Hashed password              |
| is_active   | Boolean      | Not Null, Default: true    | Active status                |
| created_at  | DateTime     | Not Null, Default: now()   | Record creation timestamp    |
| updated_at  | DateTime     | Not Null, Default: now()   | Last update timestamp        |

**Relationships:**
- One-to-Many with BlogPost (posts)

# API Endpoints (Blog)

- `GET /api/v1/blogs/<int:post_id>`: Get blog post by ID
- `GET /api/v1/blogs/slug/<string:slug>`: Get blog post by slug
- `GET /api/v1/blogs/published`: List published blog posts
- `GET /api/v1/blogs/`: List all blog posts
# Database Entity Relationship Diagram

## Overview
This document describes the database schema for the Course & Event Management System.

## Tables

### Core Entities

#### User
Represents system users who can register for courses.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | Primary Key | Unique identifier |
| full_name | String(160) | Not Null, Indexed | User's full name (must not be empty) |
| email | String(160) | Not Null, Unique | User's email address |
| phone | String(40) | Unique, Nullable | User's phone number |
| created_at | DateTime | Not Null, Default: now() | Record creation timestamp |
| updated_at | DateTime | Not Null, Default: now() | Last update timestamp |

#### Course
Represents training courses with sessions and schedules.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | Primary Key | Unique identifier |
| title | String(160) | Not Null, Indexed | Course title |
| description | Text | Nullable | Detailed course description |
| delivery_mode_id | Integer | Foreign Key, Not Null | Reference to DeliveryMode |
| venue_id | Integer | Foreign Key, Nullable | Reference to Venue (SET NULL on delete) |
| capacity | Integer | Nullable, > 0 | Maximum number of participants |
| session_counts | Integer | Nullable, >= 0 | Number of sessions |
| session_duration_minutes | Integer | Nullable, > 0 | Duration of each session in minutes |
| start_date | Date | Nullable | Course start date |
| end_date | Date | Nullable | Course end date (must be >= start_date) |
| created_at | DateTime | Not Null, Default: now() | Record creation timestamp |
| updated_at | DateTime | Not Null, Default: now() | Last update timestamp |

**Relationships:**
- Many-to-Many with Instructor (via `course_instructors` table)
- One-to-Many with Registration
- Many-to-One with DeliveryMode
- Many-to-One with Venue (optional)

#### Instructor
Represents course instructors/teachers.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | Primary Key | Unique identifier |
| full_name | String(120) | Not Null, Indexed | Instructor's full name |
| phone | String(40) | Unique, Nullable | Instructor's phone number |
| email | String(160) | Unique, Nullable | Instructor's email address |
| bio | Text | Nullable | Instructor biography |

**Relationships:**
- Many-to-Many with Course (via `course_instructors` table)

#### Registration
Links users to courses with status tracking.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | Primary Key | Unique identifier |
| course_id | Integer | Foreign Key, Not Null | Reference to Course (CASCADE on delete) |
| user_id | Integer | Foreign Key, Not Null | Reference to User (CASCADE on delete) |
| status_id | Integer | Foreign Key, Not Null | Reference to RegistrationStatus |
| submitted_at | DateTime | Not Null, Default: now() | Registration submission timestamp |
| updated_at | DateTime | Not Null, Default: now() | Last update timestamp |

**Unique Constraint:** (course_id, user_id) - One registration per user per course

#### Venue
Represents physical or virtual locations for courses and events.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | Primary Key | Unique identifier |
| name | String(160) | Not Null, Indexed | Venue name |
| address | Text | Nullable | Physical address |
| map_url | Text | Nullable | Link to map/directions |
| notes | Text | Nullable | Additional venue information |
| room_capacity | Integer | Nullable, > 0 | Maximum room capacity |
| created_at | DateTime | Not Null, Default: now() | Record creation timestamp |
| updated_at | DateTime | Not Null, Default: now() | Last update timestamp |

#### Event
Represents standalone events like book clubs, webinars, and talks.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | Primary Key | Unique identifier |
| title | String(160) | Not Null, Indexed | Event title |
| description | Text | Nullable | Detailed event description |
| event_type_id | Integer | Foreign Key, Not Null | Reference to EventType |
| delivery_mode_id | Integer | Foreign Key, Not Null | Reference to DeliveryMode |
| venue_id | Integer | Foreign Key, Nullable | Reference to Venue (SET NULL on delete) |
| capacity | Integer | Nullable, > 0 | Maximum number of participants |
| starts_at | DateTime | Nullable | Event start time |
| ends_at | DateTime | Nullable | Event end time (must be > starts_at) |
| created_at | DateTime | Not Null, Default: now() | Record creation timestamp |
| updated_at | DateTime | Not Null, Default: now() | Last update timestamp |

### Lookup Tables

#### DeliveryMode
Defines how courses and events are delivered (e.g., in-person, online, hybrid).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | Primary Key | Unique identifier |
| label | String(160) | Not Null, Unique | Delivery mode name |
| description | Text | Nullable | Detailed description |

#### RegistrationStatus
Defines possible registration states (e.g., pending, confirmed, cancelled, waitlisted).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | Primary Key | Unique identifier |
| label | String(160) | Not Null, Unique | Status name |
| description | Text | Nullable | Detailed description |

#### EventType
Categorizes events (e.g., book_club, webinar, talk, meetup).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | Primary Key | Unique identifier |
| label | String(160) | Not Null | Event type name |
| description | Text | Nullable | Detailed description |
| created_at | DateTime | Not Null, Default: now() | Record creation timestamp |
| updated_at | DateTime | Not Null, Default: now() | Last update timestamp |

## Junction Tables

### course_instructors
Many-to-many relationship between courses and instructors.

| Column | Type | Constraints |
|--------|------|-------------|
| course_id | Integer | Primary Key, Foreign Key to courses (CASCADE on delete) |
| instructor_id | Integer | Primary Key, Foreign Key to instructors (CASCADE on delete) |

**Indexes:**
- ix_course_instructor_course (course_id)
- ix_course_instructor_instructor (instructor_id)

## Key Features

### Constraints
- **Check Constraints:** Ensure data integrity (positive capacities, valid date ranges, non-empty names)
- **Unique Constraints:** Prevent duplicate registrations, ensure unique emails/phones
- **Foreign Key Constraints:** Maintain referential integrity with appropriate cascade behaviors

### Cascade Behaviors
- **CASCADE:** Registration deletes when course or user is deleted
- **SET NULL:** Course/Event venue_id set to NULL when venue is deleted
- **RESTRICT:** Prevents deletion of lookup table entries if referenced

### Timezone Handling
- All datetime fields use timezone-aware timestamps
- Default timezone configured for Asia/Tehran (TEHRAN_TZ)

## Relationships Summary

1. **User ↔ Course:** Many-to-Many through Registration table
2. **Course ↔ Instructor:** Many-to-Many through course_instructors table
3. **Course → Venue:** Many-to-One (optional)
4. **Course → DeliveryMode:** Many-to-One (required)
5. **Event → Venue:** Many-to-One (optional)
6. **Event → DeliveryMode:** Many-to-One (required)
7. **Event → EventType:** Many-to-One (required)
8. **Registration → RegistrationStatus:** Many-to-One (required)