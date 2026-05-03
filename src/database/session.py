from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from src.config import settings

# SQLite specific arguments
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

# Engine configuration
engine_kwargs = {
    "echo": settings.DATABASE_ECHO,
    "connect_args": connect_args
}

# Only add pooling arguments for non-SQLite databases
if not settings.DATABASE_URL.startswith("sqlite"):
    engine_kwargs["pool_size"] = settings.DATABASE_POOL_SIZE
    engine_kwargs["max_overflow"] = settings.DATABASE_MAX_OVERFLOW

engine = create_engine(settings.DATABASE_URL, **engine_kwargs)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    Dependency to get a database session.
    Used in FastAPI endpoints.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def init_db():
    """Initialize database connection (can be used for health checks)."""
    # In a real app, you might want to check connectivity here
    pass

async def close_db():
    """Close database connection."""
    engine.dispose()
