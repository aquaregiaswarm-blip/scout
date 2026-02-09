"""Async SQLAlchemy database configuration."""

from typing import AsyncGenerator
import structlog
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings

logger = structlog.get_logger()
settings = get_settings()

# Create async engine
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

# Create session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


async def init_db() -> None:
    """Initialize database connection."""
    try:
        async with engine.begin() as conn:
            # Just verify connection, don't create tables (use Alembic)
            await conn.run_sync(lambda _: None)
        logger.info("Database connection established")
    except Exception as e:
        logger.error("Database connection failed", error=str(e))
        raise


async def close_db() -> None:
    """Close database connection."""
    await engine.dispose()
    logger.info("Database connection closed")


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency that provides a database session."""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Aliases for convenience
get_db = get_session
AsyncSessionLocal = async_session_maker
