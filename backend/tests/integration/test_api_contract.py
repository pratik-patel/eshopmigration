"""
Integration tests for catalog API endpoints.

Tests all endpoints against OpenAPI contract.
Uses TestClient with in-memory SQLite database.

This is the CRITICAL verification gate (Task 14).
ALL TESTS MUST PASS before proceeding to frontend.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool
import io

from app.main import app
from app.core.db import get_db
from app.catalog.models import Base, CatalogBrand, CatalogType, CatalogItem


# ============================================================================
# Test Database Setup
# ============================================================================

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def override_get_db():
    """Override database dependency for testing."""
    async with TestSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
async def setup_database():
    """Create test database schema and seed data."""
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed data
    async with TestSessionLocal() as session:
        # Brands
        brands = [
            CatalogBrand(Brand="Azure"),
            CatalogBrand(Brand=".NET"),
            CatalogBrand(Brand="Visual Studio"),
        ]
        for brand in brands:
            session.add(brand)

        # Types
        types = [
            CatalogType(Type="T-Shirt"),
            CatalogType(Type="Mug"),
            CatalogType(Type="Sheet"),
        ]
        for catalog_type in types:
            session.add(catalog_type)

        await session.commit()

        # Items (after brands/types committed to get IDs)
        items = [
            CatalogItem(
                Name=".NET Bot Black Hoodie",
                Description="A stylish black hoodie",
                Price=19.50,
                PictureFileName="1.png",
                CatalogBrandId=1,
                CatalogTypeId=1,
                AvailableStock=100,
                RestockThreshold=10,
                MaxStockThreshold=200,
            ),
            CatalogItem(
                Name=".NET Black & White Mug",
                Description="Classic mug",
                Price=8.50,
                PictureFileName="2.png",
                CatalogBrandId=2,
                CatalogTypeId=2,
                AvailableStock=89,
                RestockThreshold=10,
                MaxStockThreshold=150,
            ),
            CatalogItem(
                Name="Azure Stickers Sheet",
                Description="Sticker pack",
                Price=3.50,
                PictureFileName="3.png",
                CatalogBrandId=1,
                CatalogTypeId=3,
                AvailableStock=200,
                RestockThreshold=20,
                MaxStockThreshold=300,
            ),
        ]
        for item in items:
            session.add(item)

        await session.commit()

    yield

    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client():
    """Async HTTP client for testing."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


# ============================================================================
# Health Check Tests
# ============================================================================

@pytest.mark.asyncio
async def test_root_endpoint(client):
    """Test root health check."""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "app" in data


@pytest.mark.asyncio
async def test_health_check(client):
    """Test detailed health check."""
    response = await client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


# ============================================================================
# Catalog Items - List Tests (GET /api/v1/catalog/items)
# ============================================================================

@pytest.mark.asyncio
async def test_list_items_default_pagination(client, setup_database):
    """Test GET /api/v1/catalog/items with default pagination."""
    response = await client.get("/api/v1/catalog/items")

    assert response.status_code == 200
    data = response.json()

    # Validate structure
    assert "items" in data
    assert "pagination" in data

    # Validate pagination
    pagination = data["pagination"]
    assert pagination["page"] == 0
    assert pagination["limit"] == 10
    assert pagination["total_items"] == 3
    assert pagination["total_pages"] == 1

    # Validate items
    items = data["items"]
    assert len(items) == 3

    # Validate first item structure (matches OpenAPI contract)
    first_item = items[0]
    assert "id" in first_item
    assert "name" in first_item
    assert "price" in first_item
    assert "picture_file_name" in first_item
    assert "picture_uri" in first_item
    assert "brand" in first_item
    assert "type" in first_item
    assert "available_stock" in first_item

    # Validate nested brand
    assert "id" in first_item["brand"]
    assert "brand" in first_item["brand"]

    # Validate nested type
    assert "id" in first_item["type"]
    assert "type" in first_item["type"]


@pytest.mark.asyncio
async def test_list_items_custom_pagination(client, setup_database):
    """Test GET /api/v1/catalog/items with custom pagination."""
    response = await client.get("/api/v1/catalog/items?page=0&limit=2")

    assert response.status_code == 200
    data = response.json()

    pagination = data["pagination"]
    assert pagination["page"] == 0
    assert pagination["limit"] == 2
    assert pagination["total_items"] == 3
    assert pagination["total_pages"] == 2

    items = data["items"]
    assert len(items) == 2


@pytest.mark.asyncio
async def test_list_items_invalid_page(client, setup_database):
    """Test GET /api/v1/catalog/items with invalid page."""
    response = await client.get("/api/v1/catalog/items?page=-1")
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_list_items_invalid_limit(client, setup_database):
    """Test GET /api/v1/catalog/items with invalid limit."""
    response = await client.get("/api/v1/catalog/items?limit=0")
    assert response.status_code == 400

    response = await client.get("/api/v1/catalog/items?limit=101")
    assert response.status_code == 400


# ============================================================================
# Catalog Items - Get by ID Tests (GET /api/v1/catalog/items/{id})
# ============================================================================

@pytest.mark.asyncio
async def test_get_item_success(client, setup_database):
    """Test GET /api/v1/catalog/items/{id} with valid ID."""
    response = await client.get("/api/v1/catalog/items/1")

    assert response.status_code == 200
    data = response.json()

    assert data["id"] == 1
    assert data["name"] == ".NET Bot Black Hoodie"
    assert data["price"] == "19.5"  # JSON serializes Decimal as string
    assert data["picture_file_name"] == "1.png"
    assert data["picture_uri"] == "/Pics/1.png"
    assert data["brand"]["id"] == 1
    assert data["type"]["id"] == 1


@pytest.mark.asyncio
async def test_get_item_not_found(client, setup_database):
    """Test GET /api/v1/catalog/items/{id} with non-existent ID."""
    response = await client.get("/api/v1/catalog/items/999")
    assert response.status_code == 404


# ============================================================================
# Catalog Items - Create Tests (POST /api/v1/catalog/items)
# ============================================================================

@pytest.mark.asyncio
async def test_create_item_success(client, setup_database):
    """Test POST /api/v1/catalog/items with valid data."""
    payload = {
        "name": "New Test Product",
        "description": "Test description",
        "price": "29.99",
        "catalog_brand_id": 1,
        "catalog_type_id": 1,
        "available_stock": 50,
        "restock_threshold": 5,
        "max_stock_threshold": 100,
        "temp_image_name": None,  # Will use dummy.png
    }

    response = await client.post("/api/v1/catalog/items", json=payload)

    assert response.status_code == 201
    data = response.json()

    assert data["name"] == "New Test Product"
    assert data["price"] == "29.99"
    assert data["picture_file_name"] == "dummy.png"
    assert "id" in data
    assert data["id"] > 0


@pytest.mark.asyncio
async def test_create_item_invalid_name_too_long(client, setup_database):
    """Test POST /api/v1/catalog/items with name > 50 chars."""
    payload = {
        "name": "A" * 51,  # Exceeds 50 char limit
        "price": "29.99",
        "catalog_brand_id": 1,
        "catalog_type_id": 1,
        "available_stock": 50,
        "restock_threshold": 5,
        "max_stock_threshold": 100,
    }

    response = await client.post("/api/v1/catalog/items", json=payload)
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_create_item_invalid_price_negative(client, setup_database):
    """Test POST /api/v1/catalog/items with negative price."""
    payload = {
        "name": "Test Product",
        "price": "-10.00",
        "catalog_brand_id": 1,
        "catalog_type_id": 1,
        "available_stock": 50,
        "restock_threshold": 5,
        "max_stock_threshold": 100,
    }

    response = await client.post("/api/v1/catalog/items", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_item_invalid_brand_id(client, setup_database):
    """Test POST /api/v1/catalog/items with non-existent brand."""
    payload = {
        "name": "Test Product",
        "price": "29.99",
        "catalog_brand_id": 999,  # Doesn't exist
        "catalog_type_id": 1,
        "available_stock": 50,
        "restock_threshold": 5,
        "max_stock_threshold": 100,
    }

    response = await client.post("/api/v1/catalog/items", json=payload)
    assert response.status_code == 400


# ============================================================================
# Catalog Items - Update Tests (PUT /api/v1/catalog/items/{id})
# ============================================================================

@pytest.mark.asyncio
async def test_update_item_success(client, setup_database):
    """Test PUT /api/v1/catalog/items/{id} with valid data."""
    payload = {
        "name": "Updated Product Name",
        "description": "Updated description",
        "price": "39.99",
        "catalog_brand_id": 2,
        "catalog_type_id": 2,
        "available_stock": 75,
        "restock_threshold": 8,
        "max_stock_threshold": 150,
        "temp_image_name": None,
    }

    response = await client.put("/api/v1/catalog/items/1", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert data["id"] == 1
    assert data["name"] == "Updated Product Name"
    assert data["price"] == "39.99"


@pytest.mark.asyncio
async def test_update_item_not_found(client, setup_database):
    """Test PUT /api/v1/catalog/items/{id} with non-existent ID."""
    payload = {
        "name": "Updated Product",
        "price": "39.99",
        "catalog_brand_id": 1,
        "catalog_type_id": 1,
        "available_stock": 75,
        "restock_threshold": 8,
        "max_stock_threshold": 150,
    }

    response = await client.put("/api/v1/catalog/items/999", json=payload)
    assert response.status_code == 404


# ============================================================================
# Catalog Items - Delete Tests (DELETE /api/v1/catalog/items/{id})
# ============================================================================

@pytest.mark.asyncio
async def test_delete_item_success(client, setup_database):
    """Test DELETE /api/v1/catalog/items/{id} with valid ID."""
    response = await client.delete("/api/v1/catalog/items/1")
    assert response.status_code == 204

    # Verify item is deleted
    get_response = await client.get("/api/v1/catalog/items/1")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_item_not_found(client, setup_database):
    """Test DELETE /api/v1/catalog/items/{id} with non-existent ID."""
    response = await client.delete("/api/v1/catalog/items/999")
    assert response.status_code == 404


# ============================================================================
# Lookup Tests (GET /api/v1/catalog/brands, GET /api/v1/catalog/types)
# ============================================================================

@pytest.mark.asyncio
async def test_list_brands(client, setup_database):
    """Test GET /api/v1/catalog/brands."""
    response = await client.get("/api/v1/catalog/brands")

    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)
    assert len(data) == 3

    # Validate structure
    first_brand = data[0]
    assert "id" in first_brand
    assert "brand" in first_brand


@pytest.mark.asyncio
async def test_list_types(client, setup_database):
    """Test GET /api/v1/catalog/types."""
    response = await client.get("/api/v1/catalog/types")

    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)
    assert len(data) == 3

    # Validate structure
    first_type = data[0]
    assert "id" in first_type
    assert "type" in first_type


# ============================================================================
# Summary Test (Verification Gate)
# ============================================================================

@pytest.mark.asyncio
async def test_all_endpoints_functional(client, setup_database):
    """
    CRITICAL TEST: Verify all endpoints are functional.

    This is the Task 14 verification gate.
    If this test passes, backend is ready for frontend development.
    """
    # 1. List items
    list_response = await client.get("/api/v1/catalog/items")
    assert list_response.status_code == 200

    # 2. Get item
    get_response = await client.get("/api/v1/catalog/items/1")
    assert get_response.status_code == 200

    # 3. Create item
    create_payload = {
        "name": "Verification Test Product",
        "price": "99.99",
        "catalog_brand_id": 1,
        "catalog_type_id": 1,
        "available_stock": 10,
        "restock_threshold": 2,
        "max_stock_threshold": 20,
    }
    create_response = await client.post("/api/v1/catalog/items", json=create_payload)
    assert create_response.status_code == 201
    created_id = create_response.json()["id"]

    # 4. Update item
    update_payload = {
        "name": "Updated Verification Product",
        "price": "109.99",
        "catalog_brand_id": 1,
        "catalog_type_id": 1,
        "available_stock": 15,
        "restock_threshold": 3,
        "max_stock_threshold": 25,
    }
    update_response = await client.put(f"/api/v1/catalog/items/{created_id}", json=update_payload)
    assert update_response.status_code == 200

    # 5. List brands
    brands_response = await client.get("/api/v1/catalog/brands")
    assert brands_response.status_code == 200

    # 6. List types
    types_response = await client.get("/api/v1/catalog/types")
    assert types_response.status_code == 200

    # 7. Delete item
    delete_response = await client.delete(f"/api/v1/catalog/items/{created_id}")
    assert delete_response.status_code == 204

    print("\n" + "=" * 80)
    print("✅ TASK 14 VERIFICATION GATE PASSED")
    print("=" * 80)
    print("All backend endpoints are functional and meet contract requirements.")
    print("Backend implementation is complete and ready for frontend development.")
    print("=" * 80 + "\n")
