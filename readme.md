# LapVisualizer

Backend API for visualizing and analyzing racing lap and session data.

It ingests **RMonitor / AMB timing logs** (`rmon.log`) produced by Orbits race
timing software, stores every driver's laps, and serves lap-analysis endpoints.
The protocol reference lives in [`docs/`](./docs); a real sample log is in
[`sample_data/`](./sample_data).

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

Configuration is read from the environment / a `.env` file — copy
[`.env.example`](./.env.example) to `.env` to override defaults.

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

```sh
docker compose up --build
```

See [README.Docker.md](./README.Docker.md) for details.
