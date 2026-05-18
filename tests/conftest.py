"""Shared pytest fixtures for the LapVisualizer test suite."""

import os

# `Settings` requires PostgreSQL credentials; provide throwaway values before
# any application module is imported. Tests run against an isolated in-memory
# SQLite database (see the fixtures below), so this URL is never connected.
os.environ.setdefault("POSTGRES_USER", "test")
os.environ.setdefault("POSTGRES_PASSWORD", "test")
os.environ.setdefault("POSTGRES_DB", "test")

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.core.db import Base, get_db
from backend.app.main import app


def _in_memory_engine() -> Engine:
    """Create a fresh in-memory SQLite engine with the schema applied."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def db_session() -> Iterator[Session]:
    """Yield a SQLAlchemy session on an isolated in-memory database."""
    factory = sessionmaker(bind=_in_memory_engine(), autoflush=False, expire_on_commit=False)
    db = factory()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client() -> Iterator[TestClient]:
    """Yield a TestClient backed by an isolated in-memory SQLite database."""
    factory = sessionmaker(bind=_in_memory_engine(), autoflush=False, expire_on_commit=False)

    def override_get_db() -> Iterator[Session]:
        db = factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
