# Environment variables (.env)

This document explains the environment variables used by the project and what they do. The project reads configuration from the `.env` file (see the root `.env` file for examples). Many of these are used by the container entrypoint script during startup.

Important vars

- `ENV` — Flask environment (development/production). Controls Flask debug mode in some setups.
- `DEBUG` — true/false. Enables extra logging and Flask debug tools when true.
- `SECRET_KEY` — Flask secret key used for session signing.

Database

- `DATABASE_URL` — SQLAlchemy connection string. Example: `sqlite:////app/data/mindsetbackend.db`.
- `SQLITE_CREATE_IF_MISSING` — (boolean) used by the entrypoint to decide whether to create the SQLite file/directory if missing.

Startup flags (controls behavior during container initialization)

- `RUN_MIGRATIONS_ON_START` (default: `true`) — When `true`, the entrypoint runs the Alembic migrations on container start. For SQLite the script will skip migrations if the DB file already exists; for other DB backends it runs migrations every startup.

- `CREATE_SUPERUSER_ON_BOOT` (default: `true` in `.env.example`) — When `true`, the entrypoint will attempt to create a superuser using `SUPERUSER_EMAIL`, `SUPERUSER_NAME`, and `SUPERUSER_PASSWORD` if no admin with `SUPERUSER_EMAIL` exists.

- `RUN_SEEDS_ON_START` (default: `false`) — When `true`, the entrypoint will run the project's seed command after running migrations. The seed command is run via the CLI helper so both `flask cli db seed` and `flask db seed` are supported (depending on how the Flask app exposes the CLI group). This populates reference / lookup tables (delivery modes, event types, registration statuses, etc.).

JWT

- `JWT_ALGORITHM` — Algorithm used to sign JWT tokens (e.g., `HS256`).
- `JWT_ACCESS_TOKEN_EXPIRES` — Integer seconds for access token expiry (example `120`).

Server

- `PORT` — HTTP port the container publishes (default set in `.env`).
- `FRONTEND_URLS` — JSON array (string) of allowed frontend origins used by CORS or OAuth callbacks.

Superuser bootstrap

- `SUPERUSER_EMAIL` — Email to create on boot if `CREATE_SUPERUSER_ON_BOOT` is true.
- `SUPERUSER_NAME` — Full name for the auto-created superuser.
- `SUPERUSER_PASSWORD` — Password for the auto-created superuser.

Best practices

- Keep sensitive values (e.g., `SECRET_KEY`, `SUPERUSER_PASSWORD`) out of version control. Use a secrets store for production setups.
- For development, `.env` in the project root is convenient; in CI/CD, set variables in pipeline settings or use a secrets manager.
- For running seeds in CI or during first-time development setup, set `RUN_SEEDS_ON_START=true` and `RUN_MIGRATIONS_ON_START=true` — the entrypoint will run migrations then the seed command.

Examples

Local dev `.env` (recommended minimal):

```env
ENV=development
DEBUG=true
SECRET_KEY=change-me-local
DATABASE_URL=sqlite:////app/data/mindsetbackend_dev.db
SQLITE_CREATE_IF_MISSING=true
RUN_MIGRATIONS_ON_START=true
RUN_SEEDS_ON_START=false
CREATE_SUPERUSER_ON_BOOT=true
SUPERUSER_EMAIL=admin@example.com
SUPERUSER_NAME=Admin
SUPERUSER_PASSWORD=devpassword
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRES=120
PORT=8000
FRONTEND_URLS=["http://localhost:5173"]
```

If you want me to add a small shell script that toggles seeds on/off or a set of recommended `.env` templates (`.env.local`, `.env.production`) I can add those as a follow-up.
