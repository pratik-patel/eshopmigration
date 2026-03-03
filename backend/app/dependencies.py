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


# Simple approach: Check settings and return appropriate service
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


async def get_catalog_service_with_session(
    session: AsyncSession = Depends(get_db_session),
):
    """
    Dependency for catalog service that always gets a database session.
    Use this in real mode or when the mode is determined at runtime.
    """
    settings = get_settings()

    if settings.use_mock_adapters:
        from app.core.service import CatalogServiceMock
        return CatalogServiceMock()

    from app.core.service import CatalogService
    return CatalogService(session)
