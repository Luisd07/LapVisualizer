"""Application settings, loaded from the environment and an optional `.env`."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL


class Settings(BaseSettings):
    """Runtime configuration, sourced from environment variables or `.env`.

    Database credentials intentionally have **no in-code defaults**:
    `postgres_user`, `postgres_password`, and `postgres_db` must be supplied by
    the environment, so no credentials are ever committed to source. Copy
    `.env.example` to `.env` (which is git-ignored) and fill in real values.

    Attributes:
        postgres_user: PostgreSQL role name.
        postgres_password: PostgreSQL role password.
        postgres_db: PostgreSQL database name.
        postgres_host: Database host — `localhost` for host runs, `db` in Docker.
        postgres_port: Database port.
        echo_sql: When true, SQLAlchemy logs every emitted statement.
        log_level: Minimum level for application logging (e.g. INFO, DEBUG).
        max_upload_mb: Largest accepted timing-log upload, in MiB.
        cors_origins: Comma-separated browser origins allowed to call the API.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Database: credentials are required, never defaulted in source ---
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str = "localhost"
    postgres_port: int = 5432

    # --- Application ---
    echo_sql: bool = False
    log_level: str = "INFO"
    max_upload_mb: int = 25
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    @property
    def database_url(self) -> str:
        """Assemble the SQLAlchemy/psycopg connection URL from the settings."""
        return URL.create(
            "postgresql+psycopg",
            username=self.postgres_user,
            password=self.postgres_password,
            host=self.postgres_host,
            port=self.postgres_port,
            database=self.postgres_db,
        ).render_as_string(hide_password=False)

    @property
    def cors_origins_list(self) -> list[str]:
        """Return `cors_origins` parsed into a list of origin strings."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
