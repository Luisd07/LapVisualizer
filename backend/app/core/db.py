"""Database engine, session factory, and the FastAPI session dependency."""

from collections.abc import Generator

from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from backend.app.core.config import settings

engine = create_engine(
    settings.database_url,
    echo=settings.echo_sql,
    # Verify a pooled connection is still alive before handing it out; this
    # transparently recovers from PostgreSQL dropping idle connections.
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

# Deterministic index/constraint names keep Alembic autogenerate stable and
# make every migration reversible by referring to constraints by name.
_NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """Declarative base shared by every ORM model."""

    metadata = MetaData(naming_convention=_NAMING_CONVENTION)


def get_db() -> Generator[Session]:
    """Yield a database session and guarantee it is closed after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
