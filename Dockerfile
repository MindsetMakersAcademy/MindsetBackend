FROM python:3.13-slim-trixie

# uv binary
COPY --from=ghcr.io/astral-sh/uv:python3.13-trixie \
  /usr/local/bin/uv /usr/local/bin/uvx /usr/local/bin/

WORKDIR /app

# Install deps first (cacheable)
COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-dev

COPY app ./app
COPY migrations ./migrations

# Entrypoint will run migrations / bootstrap if desired
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["/entrypoint.sh"]
CMD ["uv", "run", "flask", "--app", "app:create_app", "run", "--host=0.0.0.0", "--port=8000"]
