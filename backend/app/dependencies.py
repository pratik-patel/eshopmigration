"""
FastAPI dependency injection factories.
"""

from typing import AsyncGenerator
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


# Catalog Service DI Factory
def get_catalog_service(
    session: AsyncSession = Depends(get_db_session),
):
    """
    Dependency injection factory for CatalogService.

    Returns mock implementation if use_mock_adapters=True in config,
    otherwise returns real database-backed implementation.
    """
    settings = get_settings()

    if settings.use_mock_adapters:
        from app.core.service import CatalogServiceMock

        return CatalogServiceMock()

    from app.core.service import CatalogService

    return CatalogService(session)
