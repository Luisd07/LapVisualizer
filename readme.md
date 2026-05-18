# LapVisualizer

Backend API for visualizing and analyzing racing lap and session data.

## Stack

- **Python** 3.14
- **FastAPI** — HTTP API
- **SQLAlchemy** — persistence
- **Pydantic** — request/response schemas
- **uv** — dependency and environment management
- **Ruff** — linting and formatting

## Getting started

Install [uv](https://docs.astral.sh/uv/), then sync the environment:

```sh
uv sync
```

Run the development server:

```sh
uv run uvicorn backend.app.main:app --reload
```

The API is then available at http://127.0.0.1:8000 (interactive docs at `/docs`).

## Development

Lint and format with Ruff:

```sh
uv run ruff check .      # lint
uv run ruff check --fix .  # lint + autofix
uv run ruff format .     # format
```

Ruff is configured in [`ruff.toml`](./ruff.toml) with the full rule set enabled.

## Docker

```sh
docker compose up --build
```

See [README.Docker.md](./README.Docker.md) for details.
