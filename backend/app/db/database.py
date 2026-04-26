"""
Database connection and session management.
Supports SQLite (default) and PostgreSQL via DATABASE_URL env var.
"""
import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from .models import Base

# Default to SQLite for local development.
# For production PostgreSQL, set env: DATABASE_URL=postgresql://user:pass@host/dbname
DEFAULT_DB_PATH = os.path.join(
    os.environ.get("DATA_DIR", "data"),
    "rebound.db"
)
DEFAULT_DATABASE_URL = f"sqlite:///{DEFAULT_DB_PATH}"

DATABASE_URL = os.environ.get("DATABASE_URL", DEFAULT_DATABASE_URL)

# SQLite-specific: enable foreign key support
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False,
    )

    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
else:
    engine = create_engine(DATABASE_URL, echo=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a DB session and closes it afterwards."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create all tables if they don't exist."""
    # Ensure directory exists for SQLite
    if DATABASE_URL.startswith("sqlite"):
        db_path = DATABASE_URL.replace("sqlite:///", "")
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
    Base.metadata.create_all(bind=engine)
