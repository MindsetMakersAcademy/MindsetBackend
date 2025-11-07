# MindsetBackend
This repository contains the backend part of the Mindset website.
A Flask-based REST API for managing courses, blogs, instructors, and admin users. Built with Flask, SQLAlchemy 2.x, and Pydantic v2.

 ## Documentation

- **[Database Schema & ERD](docs/DATABASE.md)** - Complete database entity relationship diagram, table definitions, and relationships
- **[Environment Variables](docs/ENV.md)** - Complete guide to .env configuration flags
- **[Postman Setup](docs/POSTMAN.md)** - Detailed Postman collection setup and usage

## Postman Collection

The project includes a ready-to-use Postman collection in `postman/`:

```
postman/
└── MindsetBackend API.postman_collection.json   # Complete API collection
```

Features:
- Example requests for all endpoints (admin, blog, course, instructor)
- Automatic JWT token handling via collection variables
- Environment-aware with configurable base URL

Quick import:
1. Open Postman
2. Import → Browse → select `postman/MindsetBackend API.postman_collection.json`
3. Set collection variables (base_url, admin credentials)

See [docs/POSTMAN.md](docs/POSTMAN.md) for detailed setup instructions, variables, and usage tips.

## Codebase Structure

The project follows a clean, modular architecture:

```
app/
├── api/                      # HTTP layer
│   └── v1/
│       ├── admin.py         # Admin endpoints
│       ├── blog.py          # Blog endpoints
│       ├── course.py        # Course endpoints
│       ├── instructor.py    # Instructor endpoints
│       └── swagger_docs.py  # Swagger documentation
├── auth/
│   └── jwt.py              # JWT auth implementation
├── cli/                     # CLI commands implementation
│   ├── admin.py            # Admin management commands
│   ├── db.py               # Database commands (seed, etc)
│   ├── delivery_mode.py    # Delivery mode management
│   ├── event_type.py       # Event type management
│   ├── registration_status.py  # Registration status commands
│   └── venue.py            # Venue management commands
├── dtos/                    # Request/Response DTOs (Pydantic)
│   ├── admin.py            # Admin DTOs
│   ├── blog.py             # Blog DTOs
│   ├── common.py           # Shared DTO components
│   ├── course.py           # Course DTOs
│   ├── delivery.py         # Delivery mode DTOs
│   ├── event.py            # Event DTOs
│   ├── instructor.py       # Instructor DTOs
│   ├── registration.py     # Registration DTOs
│   └── venue.py            # Venue DTOs
├── models.py               # SQLAlchemy models
├── services/               # Business logic layer
├── repositories/           # Data access layer
├── config.py              # Application configuration
├── db.py                  # Database connection setup
└── exceptions.py          # Custom exceptions
```

### Key components:

1. **API Layer** (`app/api/`)
   - Route handlers for all entities (admin, blog, course, instructor)
   - Input validation via Pydantic DTOs
   - Swagger documentation

2. **Service Layer** (`app/services/`)
   - Business logic implementation
   - Coordinates between API and repositories
   - Handles data transformations and error handling

3. **Repository Layer** (`app/repositories/`)
   - Database operations
   - Implements data access patterns
   - Abstracts database implementation details

4. **Models** (`app/models.py`)
   - SQLAlchemy model definitions
   - Database schema representation
   - Type-safe with SQLAlchemy 2.x annotations
   - See [DATABASE.md](docs/DATABASE.md) for complete entity relationships and schema details

5. **DTOs** (`app/dtos.py`)
   - Request/response data models
   - Input validation schemas
   - API contract definitions

## Tech Stack

- Python 3.13
- Flask + SQLAlchemy 2.x
- Pydantic v2
- Alembic (migrations)
- passlib[argon2] (password hashing)
- rich-click (CLI)

## API Endpoints

All endpoints are versioned under `/api/v1/`.

- **Admin:** `/api/v1/admins/`
- **Blog:** `/api/v1/blogs/`
- **Course:** `/api/v1/courses/`
- **Instructor:** `/api/v1/instructors/`

See the Postman collection for example requests and authentication flows.

## Testing & Development

- Use the Postman collection in `postman/` for API testing.
- Run migrations with `flask db upgrade`.
- Create a superuser with CLI or via environment variables.
- All config/secrets are loaded from `.env` using Pydantic settings.

## How to Run

1. Install dependencies: `uv sync --frozen --no-dev`
2. Run migrations: `flask db upgrade`
3. Start the server: `uv run flask --app app:create_app run --host=0.0.0.0 --port=8000`
4. Use Postman for API testing (see `postman/`)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.
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
- `Event`: Standalone events (webinars, book clubs, talks)
- `User`: System users who register for courses

**For detailed schema information including relationships, constraints, and field definitions, see [DATABASE.md](docs/DATABASE.md).**

### Data Transfer Objects (`app/dtos/`)

Pydantic v2 models are now grouped under `app/dtos/` with one module per resource.

Examples:

```
app/dtos/
├── admin.py           # Admin DTOs (AdminIn, AdminOut, etc.)
├── blog.py            # BlogCreateIn, BlogOut, BlogUpdateIn
├── course.py          # CourseCreateIn, CourseOut, CourseUpdateIn
├── instructor.py      # Instructor DTOs
└── common.py          # Shared DTO fragments and helpers
```

DTO naming convention:
- `*Out` — response models (e.g., `CourseOut`)
- `*In` — request models (e.g., `CourseCreateIn`, `CourseUpdateIn`)

All DTOs include validation rules. Move validation logic into DTOs where appropriate (for example dates and input normalization).

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

Environment variables are loaded from `.env` using the project's settings code. For a complete listing and explanation see `docs/ENV.md`.

Important variables include (short summary):

- `PORT` — Server port (default: 8000)
- `DATABASE_URL` — SQLAlchemy URL (default: SQLite)
- `SECRET_KEY` — Flask secret key
- `RUN_MIGRATIONS_ON_START` — If `true`, run Alembic migrations during container start (default: `true`).
- `RUN_SEEDS_ON_START` — If `true`, run the DB seed command after migrations. Useful for first-time setup to populate lookup data. (default: `false`).
- `CREATE_SUPERUSER_ON_BOOT` — If `true`, the entrypoint will attempt to create a superuser from `SUPERUSER_*` vars if none exists.

See [ENV.md](docs/ENV.md) for details and recommended dev `.env` examples.


## 🧭 Command Line Interface (CLI)

The project includes a structured CLI for **database and reference data management**, built with **rich-click**.

### General CLI Usage

```bash
flask cli --help
flask cli <command> --help
```


### 🗄️ Database Operations

```bash
flask cli db init                # Initialize database schema
flask cli db seed                # Seed all reference data
flask cli db seed-modes          # Seed delivery modes
flask cli db seed-event-types    # Seed event types
flask cli db seed-registration-statuses
```


### 🚚 Delivery Modes

```bash
flask cli delivery-mode list
flask cli delivery-mode create "Online" -D "Remote sessions"
flask cli delivery-mode update 1 --label "In-Person"
flask cli delivery-mode delete 1
flask cli delivery-mode get 1
```

Options:

* `-q` — query by label
* `--json` — JSON output
* `--sort` / `--dir` — sorting and ordering


### 📅 Event Types

```bash
flask cli event-type list
flask cli event-type create "Webinar"
flask cli event-type update 1 --label "Talk"
flask cli event-type delete 1
flask cli event-type get 1
```


### 🪄 Registration Status

```bash
flask cli registration-status list
flask cli registration-status create "Registered" -D "Fully confirmed"
flask cli registration-status update 2 --label "Waitlisted"
flask cli registration-status delete 2
flask cli registration-status get 1
```


### 🏛️ Venue Management

```bash
flask cli venue list
flask cli venue create "Place A" --address "Address A" --room-capacity 50
flask cli venue update 1 --name "Updated Place A"
flask cli venue delete 1
flask cli venue get 1
```

Options:

* `--address`, `--map-url`, `--notes`, `--room-capacity`
* `--json` for machine-readable output

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

Read more about the testing strategy and conventions in [TESTING.md](./docs/TESTING.md).

### Testing

Short guide to run tests locally and run a single test file or folder.

Run the full test suite:

```bash
pytest
```

Run a single test file:

```bash
pytest tests/unit/services/test_course_service.py -q
```

For more details on the testing strategy, fixtures, and conventions see [TESTING.md](./docs/TESTING.md).

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
