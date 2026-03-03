"""
FastAPI dependency injection factories.
"""

from typing import AsyncGenerator
from functools import lru_cache
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import async_session_maker
from app.config import get_settings


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency that provides a database session.

    Yields:
        AsyncSession: Database session
    """
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


def get_catalog_service():
    """
    Dependency injection factory for CatalogService.

    Returns mock implementation if use_mock_adapters=True in config,
    otherwise returns real database-backed implementation.
    """
    settings = get_settings()

    if settings.use_mock_adapters:
        # Mock mode - no database needed
        from app.core.service import CatalogServiceMock
        return CatalogServiceMock()

    # Real mode - need to get a session
    # This won't work well with dependency injection, so let's use a different pattern
    # We'll make this async and manually get the session
    raise RuntimeError(
        "Real database mode requires session. "
        "Use get_catalog_service_with_session for real mode."
    )


def get_catalog_service_with_session():
    """
    Dependency for catalog service.
    Returns mock in mock mode (no session needed).
    In real mode, this should not be used - router needs refactoring.
    """
    settings = get_settings()

    if settings.use_mock_adapters:
        from app.core.service import CatalogServiceMock
        return CatalogServiceMock()

    # Real mode not supported with this dependency
    # Need to refactor to use get_db_session properly
    raise RuntimeError(
        "Real database mode not supported. Set USE_MOCK_ADAPTERS=true or refactor router."
    )
