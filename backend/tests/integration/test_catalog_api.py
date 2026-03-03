"""
Integration tests for Catalog API endpoints.
"""

import pytest
from httpx import AsyncClient
from fastapi import status

from app.main import app


@pytest.fixture
async def client():
    """Create test client for FastAPI app."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


class TestCatalogListAPI:
    """Integration tests for catalog list endpoint."""

    async def test_get_catalog_items_default_pagination(self, client: AsyncClient):
        """Test GET /api/catalog/items with default pagination."""
        response = await client.get("/api/catalog/items")

        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "page_index" in data
        assert "page_size" in data
        assert "total_items" in data
        assert "total_pages" in data
        assert "data" in data

        # Check default pagination
        assert data["page_index"] == 0
        assert data["page_size"] == 10

        # Check items structure
        if len(data["data"]) > 0:
            item = data["data"][0]
            assert "id" in item
            assert "name" in item
            assert "price" in item
            assert "catalog_brand" in item
            assert "catalog_type" in item

            # Check nested brand
            brand = item["catalog_brand"]
            assert "id" in brand
            assert "brand" in brand

            # Check nested type
            catalog_type = item["catalog_type"]
            assert "id" in catalog_type
            assert "type" in catalog_type

    async def test_get_catalog_items_custom_pagination(self, client: AsyncClient):
        """Test GET /api/catalog/items with custom page size."""
        response = await client.get("/api/catalog/items?page_size=5&page_index=0")

        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["page_index"] == 0
        assert data["page_size"] == 5
        assert len(data["data"]) <= 5

    async def test_get_catalog_items_second_page(self, client: AsyncClient):
        """Test GET /api/catalog/items with page_index=1."""
        response = await client.get("/api/catalog/items?page_size=5&page_index=1")

        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["page_index"] == 1
        assert data["page_size"] == 5

    async def test_get_catalog_items_invalid_page_size(self, client: AsyncClient):
        """Test GET /api/catalog/items with invalid page_size."""
        # Too large
        response = await client.get("/api/catalog/items?page_size=1000")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Too small
        response = await client.get("/api/catalog/items?page_size=0")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Negative
        response = await client.get("/api/catalog/items?page_size=-1")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_get_catalog_items_invalid_page_index(self, client: AsyncClient):
        """Test GET /api/catalog/items with invalid page_index."""
        # Negative
        response = await client.get("/api/catalog/items?page_index=-1")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_get_catalog_items_empty_page(self, client: AsyncClient):
        """Test GET /api/catalog/items with page beyond available data."""
        response = await client.get("/api/catalog/items?page_size=10&page_index=100")

        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["page_index"] == 100
        assert len(data["data"]) == 0  # No items on this page
