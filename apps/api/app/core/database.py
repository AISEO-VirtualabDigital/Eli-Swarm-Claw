"""
Database connection and session management.
Uses SQLAlchemy with async support.
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import NullPool
from typing import AsyncGenerator

from .config import settings


# Create async engine - use postgresql+asyncpg for async support
# If DATABASE_URL uses postgresql://, convert it to postgresql+asyncpg://
db_url = settings.DATABASE_URL
if db_url.startswith("postgresql://") and not db_url.startswith("postgresql+asyncpg://"):
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

engine = create_async_engine(
    db_url,
    echo=settings.DEBUG,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_pre_ping=True,
)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Sync session factory (for scripts and migrations) - use sync create_engine
from sqlalchemy import create_engine as sync_create_engine

# For Alembic migrations, we need a way to get the URL from env
def get_sync_engine(db_url: str):
    """Create a sync engine for migrations."""
    # Convert async URL to sync if needed
    sync_db_url = db_url.replace("+asyncpg", "+psycopg2", 1) if "+asyncpg" in db_url else db_url
    if sync_db_url.startswith("postgresql://"):
        sync_db_url = sync_db_url.replace("postgresql://", "postgresql+psycopg2://", 1)
    
    return sync_create_engine(
        sync_db_url,
        echo=False,
        pool_pre_ping=True,
    )

sync_engine_instance = get_sync_engine(db_url)

SessionLocal = sessionmaker(
    bind=sync_engine_instance,
    class_=Session,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting async database sessions.
    Yields a session and ensures it's closed after use.
    """
    db = AsyncSessionLocal()
    try:
        yield db
        await db.commit()
    except Exception:
        await db.rollback()
        raise
    finally:
        await db.close()


async def init_db() -> None:
    """Initialize database tables."""
    async with engine.begin() as conn:
        # Import all models to ensure they're registered
        from app.models import user, organization, workspace, project, domain, page, crawl, keyword, entity, asset, indexing, citation, recommendation
        
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Close database connections."""
    await engine.dispose()
