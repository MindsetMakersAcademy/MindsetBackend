# MindsetBackend
This repository contains the backend part of the Mindset website.
A Flask-based REST API for managing course data, built with SQLAlchemy 2.0 and Pydantic v2.

## Codebase Structure

The project follows a clean, modular architecture:

```
app/
├── api/                    # HTTP layer
│   └── v1/
│       ├── courses.py     # Route handlers
│       └── courses_docs.py# Swagger documentation
├── models.py              # SQLAlchemy models
├── dtos.py               # Pydantic request/response models
├── services/             # Business logic layer
│   └── courses.py        # Course-related operations
├── repositories/         # Data access layer
│   └── courses.py        # Database operations
├── config.py            # Application configuration
└── db.py               # Database connection setup
```

Key components:

1. **API Layer** (`app/api/`)
   - Routes and request handling
   - Input validation via Pydantic DTOs
   - Swagger documentation

2. **Service Layer** (`app/services/`)
   - Business logic implementation
   - Coordinates between API and repositories
   - Handles data transformations

3. **Repository Layer** (`app/repositories/`)
   - Database operations
   - Implements data access patterns
   - Abstracts database implementation details

4. **Models** (`app/models.py`)
   - SQLAlchemy model definitions
   - Database schema representation
   - Type-safe with SQLAlchemy 2.0 annotations

5. **DTOs** (`app/dtos.py`)
   - Request/response data models
   - Input validation schemas
   - API contract definitions


## Tech Stack

- Python 3.13
- Flask + SQLAlchemy 2.0
- Pydantic v2 for DTOs
- Flasgger for API documentation
- UV package manager (recommended)

## Detailed Architecture

### Data Models (`app/models.py`)

The application uses SQLAlchemy 2.0's modern typed models:

```python
class Course(db.Model):
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    title: Mapped[str] = mapped_column(db.String(160), nullable=False, index=True)
    delivery_mode: Mapped[DeliveryMode] = relationship(lazy="joined")
    instructors: Mapped[list[Instructor]] = relationship(secondary=course_instructors)
```

Key entities:
- `Course`: Core entity with title, dates, capacity
- `Instructor`: Course teachers with contact info
- `DeliveryMode`: Lookup table for course formats
- `Venue`: Physical/virtual locations
- `Registration`: Student enrollments

### Data Transfer Objects (`app/dtos.py`)

Pydantic models for API request/response validation:

```python
class CourseOut(BaseModel):
    id: int
    title: str
    delivery_mode: DeliveryModeOut
    instructors: list[InstructorOut] = []
```

DTO types:
- `*Out`: Response models (e.g., `CourseOut`, `InstructorOut`)
- `*In`: Request models (e.g., `CourseCreateIn`, `CourseUpdateIn`)
- All DTOs have validation rules and documentation

### Service Layer (`app/services/`)

Business logic implementation:
- Data transformation between DTOs and models
- Business rule enforcement
- Error handling
- Transaction coordination

Example service method:
```python
def list_past_courses(self) -> Sequence[CoursePastOut]:
    rows = self.repo.list_past_courses()
    return [CoursePastOut.model_validate(r) for r in rows]
```

### Repository Layer (`app/repositories/`)

Database operations abstraction:
- Uses SQLAlchemy for querying
- Abstract base classes define interfaces
- Separates business logic from data access
- Makes it easy to switch database backends

## Quick Start

Using Docker:
```bash
docker compose up --build
```

Using UV (recommended):
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r <(uv export-requirements)
uv run flask --app app:create_app run --host 0.0.0.0 --port 8000
```

Using pip:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
flask --app app:create_app run --host 0.0.0.0 --port 8000
```

## Configuration

Environment variables:
- `PORT` - Server port (default: 8000)
- `DATABASE_URL` - SQLAlchemy URL (default: SQLite)
- `SECRET_KEY` - Flask secret key
- `SQL_ECHO` - Enable SQL logging (1/0)

## API Documentation

Swagger UI available at `/docs` after startup. Key endpoints:

- `GET /api/v1/courses` - List all courses
- `GET /api/v1/courses/<id>` - Get course details
- `GET /api/v1/courses/past` - List past courses
- `GET /api/v1/courses/search` - Search courses
- `POST /api/v1/courses` - Create new course

## Development

Run tests:
```bash
pip install -e .[dev]
pytest
```

Code quality:
```bash
ruff check . && ruff format .
uv run pyright
```


## ✅ To-Do List

* [ ] Review and document project requirements
* [ ] Improve and optimize Docker setup
* [ ] Set up CI/CD pipelines for build, test, and deployment
* [ ] Write unit and integration tests
* [ ] Improve documentation and update Swagger API docs