"""
Pytest configuration and fixtures for testing.
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base
# Import only the models we need for testing
from app.models.user import User, UserRole
from app.models.organization import Region, School, Classroom
# Import all other models to ensure they're registered with SQLAlchemy
import app.models  # noqa: F401


# Create an in-memory SQLite database for testing
test_engine = create_async_engine(
    "sqlite+aiosqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False,
)

TestingSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@pytest.fixture(scope="function")
async def async_session():
    """Create a fresh database session for each test."""
    # Create tables for each test function
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestingSessionLocal() as session:
        yield session
        await session.rollback()

    # Drop tables after each test function
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
