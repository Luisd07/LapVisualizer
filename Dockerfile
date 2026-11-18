FROM python:3.14-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:0.9.29 /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev

COPY backend/ backend/
COPY alembic/ alembic/
COPY alembic.ini ./

# Run from the virtualenv built by `uv sync` (no runtime re-sync, no dev deps);
# /app is the importable package root.
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH=/app

# Apply database migrations, then start the API server.
CMD ["sh", "-c", "alembic upgrade head && uvicorn backend.app.main:app --host 0.0.0.0 --port 8000"]