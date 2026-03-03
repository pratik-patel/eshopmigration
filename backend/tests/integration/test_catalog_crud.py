"""
Integration tests for catalog CRUD API endpoints.

Tests full CRUD workflow against OpenAPI contract.
Evidence: docs/seams/catalog-crud/contracts/openapi.yaml
"""

import pytest
from decimal import Decimal
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models import CatalogBrand, CatalogType


@pytest.mark.asyncio
class TestCatalogBrandsEndpoint:
    """Test GET /api/catalog/brands endpoint."""

    async def test_get_brands_returns_all_brands(self, client: AsyncClient, db_session: AsyncSession):
        """Test brands endpoint returns all 5 brands in correct order."""
        response = await client.get("/api/catalog/brands")

        assert response.status_code == 200
        brands = response.json()

        # Should return exactly 5 brands (from seed data)
        assert len(brands) == 5

        # Verify order by ID
        assert brands[0]["id"] == 1
        assert brands[0]["brand"] == "Azure"
        assert brands[1]["id"] == 2
        assert brands[1]["brand"] == ".NET"
        assert brands[2]["id"] == 3
        assert brands[2]["brand"] == "Visual Studio"
        assert brands[3]["id"] == 4
        assert brands[3]["brand"] == "SQL Server"
        assert brands[4]["id"] == 5
        assert brands[4]["brand"] == "Other"

    async def test_get_brands_schema(self, client: AsyncClient):
        """Test brands response matches CatalogBrandDto schema."""
        response = await client.get("/api/catalog/brands")

        assert response.status_code == 200
        brands = response.json()

        for brand in brands:
            assert "id" in brand
            assert "brand" in brand
            assert isinstance(brand["id"], int)
            assert isinstance(brand["brand"], str)


@pytest.mark.asyncio
class TestCatalogTypesEndpoint:
    """Test GET /api/catalog/types endpoint."""

    async def test_get_types_returns_all_types(self, client: AsyncClient, db_session: AsyncSession):
        """Test types endpoint returns all 4 types in correct order."""
        response = await client.get("/api/catalog/types")

        assert response.status_code == 200
        types = response.json()

        # Should return exactly 4 types (from seed data)
        assert len(types) == 4

        # Verify order by ID
        assert types[0]["id"] == 1
        assert types[0]["type"] == "Mug"
        assert types[1]["id"] == 2
        assert types[1]["type"] == "T-Shirt"
        assert types[2]["id"] == 3
        assert types[2]["type"] == "Sheet"
        assert types[3]["id"] == 4
        assert types[3]["type"] == "USB Memory Stick"

    async def test_get_types_schema(self, client: AsyncClient):
        """Test types response matches CatalogTypeDto schema."""
        response = await client.get("/api/catalog/types")

        assert response.status_code == 200
        types = response.json()

        for catalog_type in types:
            assert "id" in catalog_type
            assert "type" in catalog_type
            assert isinstance(catalog_type["id"], int)
            assert isinstance(catalog_type["type"], str)


@pytest.mark.asyncio
class TestCreateCatalogItem:
    """Test POST /api/catalog/items endpoint."""

    async def test_create_item_minimal_fields(self, client: AsyncClient):
        """Test creating item with minimal required fields."""
        response = await client.post(
            "/api/catalog/items",
            json={
                "name": "Test Product",
                "price": 19.99,
                "catalog_brand_id": 1,
                "catalog_type_id": 2,
            },
        )

        assert response.status_code == 201
        item = response.json()

        assert item["name"] == "Test Product"
        assert item["price"] == "19.99"
        assert item["catalog_brand_id"] == 1
        assert item["catalog_type_id"] == 2
        assert item["available_stock"] == 0  # Default
        assert item["restock_threshold"] == 0  # Default
        assert item["max_stock_threshold"] == 0  # Default
        assert item["picture_file_name"] == "dummy.png"  # Default
        assert item["on_reorder"] is False

        # Navigation properties must be populated
        assert item["catalog_brand"]["id"] == 1
        assert item["catalog_brand"]["brand"] == "Azure"
        assert item["catalog_type"]["id"] == 2
        assert item["catalog_type"]["type"] == "T-Shirt"

        # Must have ID assigned
        assert "id" in item
        assert isinstance(item["id"], int)

    async def test_create_item_complete_fields(self, client: AsyncClient):
        """Test creating item with all fields."""
        response = await client.post(
            "/api/catalog/items",
            json={
                "name": ".NET Bot Black Hoodie",
                "description": ".NET Bot Black Hoodie, and more",
                "price": 19.50,
                "catalog_brand_id": 2,
                "catalog_type_id": 2,
                "available_stock": 100,
                "restock_threshold": 10,
                "max_stock_threshold": 200,
                "picture_file_name": "1.png",
            },
        )

        assert response.status_code == 201
        item = response.json()

        assert item["name"] == ".NET Bot Black Hoodie"
        assert item["description"] == ".NET Bot Black Hoodie, and more"
        assert item["price"] == "19.50"
        assert item["available_stock"] == 100
        assert item["restock_threshold"] == 10
        assert item["max_stock_threshold"] == 200
        assert item["picture_file_name"] == "1.png"

    async def test_create_item_validation_empty_name(self, client: AsyncClient):
        """Test BR-005: Name required validation."""
        response = await client.post(
            "/api/catalog/items",
            json={
                "name": "",
                "price": 19.99,
                "catalog_brand_id": 1,
                "catalog_type_id": 2,
            },
        )

        assert response.status_code == 422
        error = response.json()
        assert "detail" in error
        # Check error message contains expected text
        error_str = str(error["detail"])
        assert "Name" in error_str or "name" in error_str

    async def test_create_item_validation_negative_price(self, client: AsyncClient):
        """Test BR-001: Price validation - negative."""
        response = await client.post(
            "/api/catalog/items",
            json={
                "name": "Test Product",
                "price": -5.00,
                "catalog_brand_id": 1,
                "catalog_type_id": 2,
            },
        )

        assert response.status_code == 422
        error = response.json()
        error_str = str(error["detail"])
        assert "Price" in error_str or "price" in error_str

    async def test_create_item_validation_price_decimals(self, client: AsyncClient):
        """Test BR-001: Price validation - too many decimals."""
        response = await client.post(
            "/api/catalog/items",
            json={
                "name": "Test Product",
                "price": 12.999,
                "catalog_brand_id": 1,
                "catalog_type_id": 2,
            },
        )

        assert response.status_code == 422

    async def test_create_item_validation_stock_exceeds_max(self, client: AsyncClient):
        """Test BR-002: Stock validation."""
        response = await client.post(
            "/api/catalog/items",
            json={
                "name": "Test Product",
                "price": 19.99,
                "catalog_brand_id": 1,
                "catalog_type_id": 2,
                "available_stock": 99999999,
            },
        )

        assert response.status_code == 422

    async def test_create_item_invalid_brand(self, client: AsyncClient):
        """Test validation: Invalid brand ID."""
        response = await client.post(
            "/api/catalog/items",
            json={
                "name": "Test Product",
                "price": 19.99,
                "catalog_brand_id": 999,  # Non-existent
                "catalog_type_id": 2,
            },
        )

        # Should return 404 or 422 (foreign key violation)
        assert response.status_code in [404, 422, 500]


@pytest.mark.asyncio
class TestGetCatalogItem:
    """Test GET /api/catalog/items/{id} endpoint."""

    async def test_get_item_by_id(self, client: AsyncClient):
        """Test getting existing item by ID."""
        # First create an item
        create_response = await client.post(
            "/api/catalog/items",
            json={
                "name": "Test Product",
                "price": 19.99,
                "catalog_brand_id": 1,
                "catalog_type_id": 2,
            },
        )
        created_item = create_response.json()
        item_id = created_item["id"]

        # Now get it
        response = await client.get(f"/api/catalog/items/{item_id}")

        assert response.status_code == 200
        item = response.json()

        assert item["id"] == item_id
        assert item["name"] == "Test Product"
        assert item["catalog_brand"]["id"] == 1
        assert item["catalog_type"]["id"] == 2

    async def test_get_item_not_found(self, client: AsyncClient):
        """Test getting non-existent item."""
        response = await client.get("/api/catalog/items/99999")

        assert response.status_code == 404
        error = response.json()
        assert "detail" in error
        assert "99999" in error["detail"]


@pytest.mark.asyncio
class TestUpdateCatalogItem:
    """Test PUT /api/catalog/items/{id} endpoint."""

    async def test_update_item(self, client: AsyncClient):
        """Test updating existing item."""
        # Create an item first
        create_response = await client.post(
            "/api/catalog/items",
            json={
                "name": "Original Name",
                "price": 19.99,
                "catalog_brand_id": 1,
                "catalog_type_id": 2,
            },
        )
        item_id = create_response.json()["id"]

        # Update it
        response = await client.put(
            f"/api/catalog/items/{item_id}",
            json={
                "name": "Updated Name",
                "description": "Updated description",
                "price": 22.50,
                "catalog_brand_id": 2,
                "catalog_type_id": 2,
                "available_stock": 150,
                "restock_threshold": 20,
                "max_stock_threshold": 300,
                "picture_file_name": "updated.png",
            },
        )

        assert response.status_code == 200
        updated_item = response.json()

        assert updated_item["id"] == item_id
        assert updated_item["name"] == "Updated Name"
        assert updated_item["description"] == "Updated description"
        assert updated_item["price"] == "22.50"
        assert updated_item["available_stock"] == 150
        assert updated_item["catalog_brand"]["id"] == 2
        assert updated_item["catalog_brand"]["brand"] == ".NET"

    async def test_update_item_not_found(self, client: AsyncClient):
        """Test updating non-existent item."""
        response = await client.put(
            "/api/catalog/items/99999",
            json={
                "name": "Updated Name",
                "price": 22.50,
                "catalog_brand_id": 1,
                "catalog_type_id": 2,
                "available_stock": 150,
                "restock_threshold": 20,
                "max_stock_threshold": 300,
                "picture_file_name": "dummy.png",
            },
        )

        assert response.status_code == 404

    async def test_update_item_validation(self, client: AsyncClient):
        """Test update validation is same as create."""
        # Create an item first
        create_response = await client.post(
            "/api/catalog/items",
            json={
                "name": "Original Name",
                "price": 19.99,
                "catalog_brand_id": 1,
                "catalog_type_id": 2,
            },
        )
        item_id = create_response.json()["id"]

        # Try to update with invalid price
        response = await client.put(
            f"/api/catalog/items/{item_id}",
            json={
                "name": "Updated Name",
                "price": -5.00,  # Invalid
                "catalog_brand_id": 1,
                "catalog_type_id": 2,
                "available_stock": 100,
                "restock_threshold": 10,
                "max_stock_threshold": 200,
                "picture_file_name": "dummy.png",
            },
        )

        assert response.status_code == 422


@pytest.mark.asyncio
class TestDeleteCatalogItem:
    """Test DELETE /api/catalog/items/{id} endpoint."""

    async def test_delete_item(self, client: AsyncClient):
        """Test deleting existing item."""
        # Create an item first
        create_response = await client.post(
            "/api/catalog/items",
            json={
                "name": "To Be Deleted",
                "price": 19.99,
                "catalog_brand_id": 1,
                "catalog_type_id": 2,
            },
        )
        item_id = create_response.json()["id"]

        # Delete it
        response = await client.delete(f"/api/catalog/items/{item_id}")

        assert response.status_code == 204
        assert response.content == b""  # No content

        # Verify it's gone
        get_response = await client.get(f"/api/catalog/items/{item_id}")
        assert get_response.status_code == 404

    async def test_delete_item_not_found(self, client: AsyncClient):
        """Test deleting non-existent item."""
        response = await client.delete("/api/catalog/items/99999")

        assert response.status_code == 404


@pytest.mark.asyncio
class TestFullCRUDWorkflow:
    """Test complete CRUD workflow."""

    async def test_full_crud_workflow(self, client: AsyncClient):
        """Test Create → Read → Update → Delete workflow."""
        # 1. CREATE
        create_response = await client.post(
            "/api/catalog/items",
            json={
                "name": "Workflow Test Product",
                "description": "Testing full CRUD workflow",
                "price": 29.99,
                "catalog_brand_id": 1,
                "catalog_type_id": 2,
                "available_stock": 50,
            },
        )
        assert create_response.status_code == 201
        created_item = create_response.json()
        item_id = created_item["id"]

        # 2. READ
        read_response = await client.get(f"/api/catalog/items/{item_id}")
        assert read_response.status_code == 200
        read_item = read_response.json()
        assert read_item["name"] == "Workflow Test Product"
        assert read_item["available_stock"] == 50

        # 3. UPDATE
        update_response = await client.put(
            f"/api/catalog/items/{item_id}",
            json={
                "name": "Workflow Test Product (Updated)",
                "description": "Updated description",
                "price": 39.99,
                "catalog_brand_id": 2,
                "catalog_type_id": 2,
                "available_stock": 75,
                "restock_threshold": 10,
                "max_stock_threshold": 100,
                "picture_file_name": "test.png",
            },
        )
        assert update_response.status_code == 200
        updated_item = update_response.json()
        assert updated_item["name"] == "Workflow Test Product (Updated)"
        assert updated_item["price"] == "39.99"
        assert updated_item["available_stock"] == 75

        # 4. DELETE
        delete_response = await client.delete(f"/api/catalog/items/{item_id}")
        assert delete_response.status_code == 204

        # 5. VERIFY DELETED
        verify_response = await client.get(f"/api/catalog/items/{item_id}")
        assert verify_response.status_code == 404
