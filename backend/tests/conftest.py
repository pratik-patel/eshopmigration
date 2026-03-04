"""
Pytest configuration and shared fixtures.
"""

import pytest
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))


@pytest.fixture
def anyio_backend():
    """Configure asyncio as the async backend for pytest-asyncio."""
    return "asyncio"
