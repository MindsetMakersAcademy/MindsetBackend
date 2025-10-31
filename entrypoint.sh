#!/bin/sh
set -euo pipefail

echo ">> Starting container initialization"

# --- helpers ---------------------------------------------------------------

run_flask() {
  # Wrapper so we don't repeat flags everywhere
  uv run flask --app app:create_app "$@"
}

# Extract a filesystem path from a sqlite URL (or print empty if not sqlite)
sqlite_path_from_url() {
  # Expected forms:
  #   sqlite:////abs/path/to.db
  #   sqlite:///./rel/path/to.db     (relative to /app)
  #   sqlite:///:memory:
  # Anything else -> empty
  url="${1:-}"
  case "$url" in
    sqlite:///:memory:)
      echo ""
      ;;
    sqlite:////*)
      # absolute path
      printf "%s" "${url#sqlite:////}"
      ;;
    sqlite:///./*)
      # path relative to CWD (/app)
      printf "%s" "/app/${url#sqlite:///./}"
      ;;
    sqlite:///[^.]*)
      # generic sqlite:///path (relative to CWD)
      printf "%s" "/app/${url#sqlite:///}"
      ;;
    sqlite://*)
      # other sqlite forms, best effort
      printf "%s" "${url#sqlite://}"
      ;;
    *)
      echo ""
      ;;
  esac
}

# Try a CLI subcommand; prefer "cli admin ..." then fallback to "admin ..."
admin_cli() {
  if run_flask --help 2>/dev/null | grep -qE '^\s+cli\s'; then
    run_flask cli admin "$@"
  else
    run_flask admin "$@"
  fi
}

# --- ensure DB directory exists (for sqlite) -------------------------------

DB_URL="${DATABASE_URL:-}"
DB_PATH="$(sqlite_path_from_url "$DB_URL")"

if [ -n "$DB_PATH" ]; then
  DB_DIR="$(dirname "$DB_PATH")"
  echo ">> Ensuring SQLite directory exists: $DB_DIR"
  mkdir -p "$DB_DIR"
fi

# --- migrations (run once for sqlite, always safe for others) --------------

if [ "${RUN_MIGRATIONS_ON_START:-true}" = "true" ]; then
  if [ -n "$DB_PATH" ]; then
    # SQLite: skip migrations if the DB file already exists (assume already initialized)
    if [ -f "$DB_PATH" ]; then
      echo ">> SQLite DB file exists at $DB_PATH — skipping migrations."
    else
      echo ">> Running migrations (SQLite, first-time init)..."
      run_flask db upgrade
    fi
  else
    # Non-sqlite (e.g., Postgres): safe to run every boot (idempotent per revision)
    echo ">> Running migrations (non-SQLite)..."
    run_flask db upgrade
  fi
fi

# --- superuser bootstrap (idempotent) --------------------------------------

if [ "${CREATE_SUPERUSER_ON_BOOT:-false}" = "true" ]; then
  EMAIL="${SUPERUSER_EMAIL:-}"
  NAME="${SUPERUSER_NAME:-Admin}"
  PASSWORD="${SUPERUSER_PASSWORD:-}"

  if [ -z "$EMAIL" ] || [ -z "$PASSWORD" ]; then
    echo "!! CREATE_SUPERUSER_ON_BOOT is true, but SUPERUSER_EMAIL/PASSWORD are missing. Skipping."
  else
    echo ">> Checking if superuser exists: $EMAIL"
    # list admins and look for the exact email; if not found, create it
    if admin_cli list | awk '{print $0}' | grep -Fq "$EMAIL"; then
      echo ">> Superuser '$EMAIL' already exists — skipping creation."
    else
      echo ">> Creating superuser '$EMAIL'..."
      admin_cli create --email "$EMAIL" --full-name "$NAME" --password "$PASSWORD"
    fi
  fi
fi

echo ">> ✅ Launching Flask app"
exec "$@"
