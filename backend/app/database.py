"""
Database setup: SQLAlchemy engine, session factory, and declarative Base.

Models (created in Phase 2's next step) should inherit from `Base`.
Endpoints get a DB session via the `get_db` dependency in app/api/deps.py.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # avoids stale-connection errors after DB idles
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
