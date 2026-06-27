from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# Create engine with standard connection pooling parameters for Postgres
engine = create_engine(
    settings.clean_database_url,
    pool_size=10,
    max_overflow=20
)

# SessionLocal is the session factory used to spawn database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for declarative database models
Base = declarative_base()
