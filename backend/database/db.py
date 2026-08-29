import os
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Test connection validity before checkout
    pool_size=10,        # Base connection pool size
    max_overflow=20      # Allow temporary spikes up to 30 connections
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db():
    """
    FastAPI Dependency that provides a transactional database session per request 
    and guarantees that the session is closed when the request finishes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_session():
    """
    Context manager for database sessions outside of FastAPI route handlers.
    Usage:
        with get_db_session() as db:
            db.execute(...)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()