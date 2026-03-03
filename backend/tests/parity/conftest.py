"""
Pytest configuration for parity tests.

Provides fixtures for comparing new system to golden baselines.
"""

import pytest
from httpx import AsyncClient

from app.main import app


@pytest.fixture
async def client():
    """
    Create async HTTP client for FastAPI app.

    Used for making API requests in parity tests.
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
async def async_client():
    """
    Create async HTTP client for FastAPI app (alias for backwards compatibility).

    Used for making API requests in parity tests.
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
