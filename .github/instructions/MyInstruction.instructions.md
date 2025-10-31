# Copilot Instructions for MindsetBackend

## Project Architecture
- **Layered structure:**
  - `app/api/v1/`: API route handlers (Flask), input validation (Pydantic DTOs), Swagger docs
  - `app/models.py`: SQLAlchemy 2.x models, type-annotated, all core entities
  - `app/dtos.py`: Pydantic v2 DTOs for request/response validation
  - `app/services/`: Business logic, data transformation, error handling
  - `app/repositories/`: Data access, SQLAlchemy queries, abstract base classes
  - `app/config.py`: Typed config, loads all secrets from `.env` (use pydantic-settings)
  - `app/db.py`: DB engine/session setup
- **Docs:** See `docs/DATABASE.md` for schema, relationships, constraints

## Key Patterns & Conventions
- **DTOs:**
  - Use Pydantic v2 models for all API input/output
  - Suffix: `*Out` for responses, `*In` for requests
  - Validation and documentation via Pydantic
- **Models:**
  - Use SQLAlchemy 2.x `Mapped`/`mapped_column` for all fields
  - Relationships: use `relationship()` and `secondary` for many-to-many
- **Service Layer:**
  - All business logic goes in `app/services/`, not in API routes
  - Services transform between DTOs and models, enforce rules, handle errors
- **Repository Layer:**
  - All DB queries in `app/repositories/`, not in services or API
  - Use abstract base classes for interface consistency
- **Config:**
  - All secrets/config read from `.env` via `app/config.py` (pydantic-settings)
  - Use `Settings` class, access via `settings = Settings()`
- **Testing:**
  - Tests in `tests/` (unit/integration)
  - Use pytest, ruff, black, mypy --strict
  - See `docs/TESTING.md` for conventions

## Developer Workflows
- **Run app:**
  - `uv run flask --app app:create_app run --host 0.0.0.0 --port 8000`
  - Or use Docker Compose
- **Migrations:**
  - Use Alembic for schema changes
  - Migration files in `migrations/versions/`
- **CLI:**
  - Use `flask cli ...` for DB/data management
- **API Docs:**
  - Swagger UI at `/docs`
- **Testing:**
  - `pytest` for tests, `ruff check .`, `black .`, `mypy --strict`

## Integration Points
- **External dependencies:**
  - SQLAlchemy, Pydantic, Flask, Flasgger, Alembic, passlib[argon2], Flask-Login, Flask-WTF, Flask-Limiter, Flask-Talisman
- **Config:**
  - All sensitive config from `.env` (see `.env.example`)
- **Data flow:**
  - API → DTO → Service → Repository → Model → DB
  - Service returns DTOs to API

## Examples
- **Add a new API route:**
  - Define DTO in `app/dtos.py`
  - Add route in `app/api/v1/` (use DTO for validation)
  - Implement logic in `app/services/`
  - Query DB via `app/repositories/`
- **Add a new model field:**
  - Update `app/models.py` (use type hints)
  - Create Alembic migration
  - Update DTOs/services as needed

## Special Notes
- **Do not put business logic in API routes.**
- **Always use type hints.**
- **All config/secrets must come from `.env` via `app/config.py`.**
- **Follow the layered architecture for maintainability.**
