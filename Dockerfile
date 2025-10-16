FROM python:3.13-slim-trixie

COPY --from=ghcr.io/astral-sh/uv:python3.13-trixie \
  /usr/local/bin/uv /usr/local/bin/uvx /usr/local/bin/

WORKDIR /app

COPY pyproject.toml uv.lock* ./
COPY app ./app

RUN uv sync --frozen --no-dev

EXPOSE 8000
CMD ["uv", "run", "flask", "--app", "app:create_app", "run", "--host=0.0.0.0", "--port=8000"]
