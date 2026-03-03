"""
Pytest configuration for all tests.

Provides shared fixtures for unit, integration, and parity tests.
"""

import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.db import Base
from app.dependencies import get_db_session
from app.core.seed import seed_database


# Use function-scoped event loop for async tests
@pytest.fixture(scope="function")
def event_loop():
    """Create new event loop for each test."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def test_db_engine():
    """
    Create in-memory SQLite database engine for testing.

    Uses StaticPool to maintain same database across connections.
    """
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Cleanup
    await engine.dispose()


@pytest.fixture
async def db_session(test_db_engine):
    """
    Create database session for testing.

    Automatically seeds database with initial data.
    """
    async_session_maker = async_sessionmaker(
        test_db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session_maker() as session:
        # Seed database with initial data
        await seed_database(session)
        yield session
        await session.rollback()


@pytest.fixture
async def client(db_session):
    """
    Create async HTTP client for FastAPI app with test database.

    Overrides app's database dependency to use test database.
    """

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db_session] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
async def async_client(client):
    """Alias for client fixture (backwards compatibility)."""
    return client
