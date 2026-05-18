# LapVisualizer

Backend API for visualizing and analyzing racing lap and session data.

It ingests **RMonitor / AMB timing logs** (`rmon.log`) produced by Orbits race
timing software, stores every driver's laps, and serves lap-analysis endpoints.
The protocol reference lives in [`docs/`](./docs); a real sample log is in
[`sample_data/`](./sample_data).

## Stack

- **Python** 3.14
- **FastAPI** — HTTP API
- **PostgreSQL** — database (via `psycopg` 3)
- **SQLAlchemy** — ORM
- **Alembic** — database migrations
- **Pydantic** — request/response schemas
- **Loguru** — application logging
- **uv** — dependency and environment management
- **Ruff** — linting and formatting

## Getting started

Install [uv](https://docs.astral.sh/uv/), then sync the environment:

```sh
uv sync
```

Create your local config from the template. `.env` is git-ignored and is the
**only** place credentials live — the app refuses to start without it:

```sh
cp .env.example .env
```

The app needs a PostgreSQL database. The simplest option is the bundled
container — it reads the same `.env`:

```sh
docker compose up -d db
```

Apply migrations, then run the development server:

```sh
uv run alembic upgrade head
uv run uvicorn backend.app.main:app --reload
```

The API is then available at http://127.0.0.1:8000 (interactive docs at `/docs`).

All configuration — database credentials (`POSTGRES_USER` / `POSTGRES_PASSWORD`
/ `POSTGRES_DB`), `CORS_ORIGINS`, `MAX_UPLOAD_MB` — is read from environment
variables / `.env`. See [`.env.example`](./.env.example) for the full list.

## Database migrations

The schema is owned by [Alembic](https://alembic.sqlalchemy.org/); the app does
**not** create tables on startup.

```sh
uv run alembic upgrade head                       # apply all migrations
uv run alembic revision --autogenerate -m "..."   # generate one after a model change
uv run alembic downgrade -1                       # roll back the last migration
```

After editing an ORM model, autogenerate a migration and review it before
committing. `uv run alembic check` reports whether the models and the latest
migration are in sync.

## API

All endpoints are served under `/api`.

| Method   | Path                                          | Purpose                                   |
| -------- | --------------------------------------------- | ----------------------------------------- |
| `POST`   | `/sessions/upload`                            | Upload and parse an RMonitor log          |
| `GET`    | `/sessions`                                   | List stored sessions                      |
| `GET`    | `/sessions/{id}`                              | Session detail with driver summaries      |
| `DELETE` | `/sessions/{id}`                              | Delete a session                          |
| `GET`    | `/sessions/{id}/drivers`                      | Drivers in a session                      |
| `GET`    | `/sessions/{id}/drivers/{reg}`                | Driver detail with full lap list          |
| `GET`    | `/sessions/{id}/leaderboard`                  | Best-lap ranking (`?race_class=`)         |
| `GET`    | `/sessions/{id}/progression`                  | Lap-by-lap times (`?drivers=&race_class=`)|
| `GET`    | `/sessions/{id}/comparison`                   | Side-by-side laps (`?drivers=11,22`)      |
| `GET`    | `/sessions/{id}/stats`                        | Per-driver lap statistics                 |

## Development

Run the test suite:

```sh
uv run pytest
```

Lint and format with Ruff:

```sh
uv run ruff check .         # lint
uv run ruff check --fix .   # lint + autofix
uv run ruff format .        # format
```

Ruff is configured in [`ruff.toml`](./ruff.toml) with the full rule set enabled.

## Docker

Bring up the database and the API together:

```sh
docker compose up --build
```

The `server` container waits for PostgreSQL to be healthy, runs
`alembic upgrade head`, and then starts the API on port 8000.

See [README.Docker.md](./README.Docker.md) for details.
