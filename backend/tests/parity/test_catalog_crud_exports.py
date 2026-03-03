"""
Parity tests for catalog-crud seam - API exports comparison.

Compares backend API responses against synthetic golden baselines.
All baselines are loaded from legacy-golden/catalog-crud/exports/*.json

Test Strategy:
- Dropdown data (brands, types) must match exactly
- Product data structure must match golden baseline
- Field names and types must match
- Response format must match
"""

import json
import pytest
from decimal import Decimal
from pathlib import Path
from httpx import AsyncClient

# Golden baseline paths
GOLDEN_DIR = Path(__file__).parent.parent.parent.parent / "legacy-golden" / "catalog-crud" / "exports"
GOLDEN_BRANDS = GOLDEN_DIR / "synthetic_brands.json"
GOLDEN_TYPES = GOLDEN_DIR / "synthetic_types.json"
GOLDEN_PRODUCT_1 = GOLDEN_DIR / "synthetic_product_1.json"


def load_golden_baseline(filename: str) -> dict:
    """Load golden baseline JSON file."""
    filepath = GOLDEN_DIR / filename
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.mark.asyncio
async def test_get_brands_matches_golden_baseline(client: AsyncClient):
    """
    Test GET /api/catalog/brands matches golden baseline.

    Golden baseline: synthetic_brands.json (5 brands from seed.py)
    Comparison: Exact match on id, brand fields for all 5 brands
    """
    # Load golden baseline
    golden = load_golden_baseline("synthetic_brands.json")
    expected_brands = golden["data"]

    # Call API
    response = await client.get("/api/catalog/brands")

    # Assert response structure
    assert response.status_code == 200
    actual_brands = response.json()

    # Assert count matches
    assert len(actual_brands) == len(expected_brands), (
        f"Expected {len(expected_brands)} brands, got {len(actual_brands)}"
    )

    # Assert each brand matches exactly
    for expected, actual in zip(expected_brands, actual_brands):
        assert actual["id"] == expected["id"], f"Brand ID mismatch: {actual} vs {expected}"
        assert actual["brand"] == expected["brand"], f"Brand name mismatch: {actual} vs {expected}"


@pytest.mark.asyncio
async def test_get_types_matches_golden_baseline(client: AsyncClient):
    """
    Test GET /api/catalog/types matches golden baseline.

    Golden baseline: synthetic_types.json (4 types from seed.py)
    Comparison: Exact match on id, type fields for all 4 types
    """
    # Load golden baseline
    golden = load_golden_baseline("synthetic_types.json")
    expected_types = golden["data"]

    # Call API
    response = await client.get("/api/catalog/types")

    # Assert response structure
    assert response.status_code == 200
    actual_types = response.json()

    # Assert count matches
    assert len(actual_types) == len(expected_types), (
        f"Expected {len(expected_types)} types, got {len(actual_types)}"
    )

    # Assert each type matches exactly
    for expected, actual in zip(expected_types, actual_types):
        assert actual["id"] == expected["id"], f"Type ID mismatch: {actual} vs {expected}"
        assert actual["type"] == expected["type"], f"Type name mismatch: {actual} vs {expected}"


@pytest.mark.asyncio
async def test_get_product_1_matches_golden_baseline(client: AsyncClient):
    """
    Test GET /api/catalog/items/1 matches golden baseline.

    Golden baseline: synthetic_product_1.json (product ID 1 from seed.py)
    Comparison: All fields match except picture_uri (can be null)

    Note: This test verifies the product used by Edit/Details/Delete workflows
    """
    # Load golden baseline
    golden = load_golden_baseline("synthetic_product_1.json")
    expected_product = golden["data"]

    # Call API
    response = await client.get("/api/catalog/items/1")

    # Assert response structure
    assert response.status_code == 200
    actual_product = response.json()

    # Assert core fields match exactly
    assert actual_product["id"] == expected_product["id"]
    assert actual_product["name"] == expected_product["name"]
    assert actual_product["description"] == expected_product["description"]

    # Price comparison - convert to Decimal for exact comparison
    # Note: JSON may serialize Decimal as float or string
    actual_price = Decimal(str(actual_product["price"]))
    expected_price = Decimal(str(expected_product["price"]))
    assert actual_price == expected_price, f"Price mismatch: {actual_price} vs {expected_price}"

    # Stock fields
    assert actual_product["available_stock"] == expected_product["available_stock"]
    assert actual_product["restock_threshold"] == expected_product["restock_threshold"]
    assert actual_product["max_stock_threshold"] == expected_product["max_stock_threshold"]
    assert actual_product["on_reorder"] == expected_product["on_reorder"]

    # Foreign keys
    assert actual_product["catalog_type_id"] == expected_product["catalog_type_id"]
    assert actual_product["catalog_brand_id"] == expected_product["catalog_brand_id"]

    # Picture filename
    assert actual_product["picture_file_name"] == expected_product["picture_file_name"]

    # Navigation properties
    assert actual_product["catalog_type"]["id"] == expected_product["catalog_type"]["id"]
    assert actual_product["catalog_type"]["type"] == expected_product["catalog_type"]["type"]
    assert actual_product["catalog_brand"]["id"] == expected_product["catalog_brand"]["id"]
    assert actual_product["catalog_brand"]["brand"] == expected_product["catalog_brand"]["brand"]

    # picture_uri can be null (computed field) - we don't enforce exact match
    # This field is excluded from parity comparison


@pytest.mark.asyncio
async def test_create_product_returns_correct_structure(client: AsyncClient):
    """
    Test POST /api/catalog/items returns correct response structure.

    Golden baseline: synthetic_product_1.json structure
    Comparison: Response has same fields as golden baseline (values will differ)

    Note: This test verifies the CREATE workflow structure, not exact values
    """
    # Load golden baseline to get expected structure
    golden = load_golden_baseline("synthetic_product_1.json")
    expected_fields = set(golden["data"].keys())

    # Create new product
    new_product = {
        "name": "Parity Test Product",
        "description": "Created by parity test",
        "price": 99.99,
        "catalog_type_id": 2,
        "catalog_brand_id": 1,
        "available_stock": 50,
        "restock_threshold": 10,
        "max_stock_threshold": 100,
        "picture_file_name": "test.png"
    }

    response = await client.post("/api/catalog/items", json=new_product)

    # Assert response structure
    assert response.status_code == 201
    created_product = response.json()

    # Assert all expected fields are present
    actual_fields = set(created_product.keys())
    missing_fields = expected_fields - actual_fields
    assert not missing_fields, f"Missing fields in response: {missing_fields}"

    # Assert ID is assigned
    assert created_product["id"] > 0, "Created product should have ID assigned"

    # Assert input fields match
    assert created_product["name"] == new_product["name"]
    assert Decimal(str(created_product["price"])) == Decimal(str(new_product["price"]))
    assert created_product["catalog_type_id"] == new_product["catalog_type_id"]
    assert created_product["catalog_brand_id"] == new_product["catalog_brand_id"]

    # Assert navigation properties are populated
    assert "catalog_type" in created_product
    assert "catalog_brand" in created_product
    assert created_product["catalog_type"]["id"] == new_product["catalog_type_id"]
    assert created_product["catalog_brand"]["id"] == new_product["catalog_brand_id"]


@pytest.mark.asyncio
async def test_update_product_preserves_structure(client: AsyncClient):
    """
    Test PUT /api/catalog/items/{id} returns correct response structure.

    Golden baseline: synthetic_product_1.json structure
    Comparison: Response has same fields as golden baseline

    Note: This test verifies the EDIT workflow structure
    """
    # Load golden baseline to get expected structure
    golden = load_golden_baseline("synthetic_product_1.json")
    expected_fields = set(golden["data"].keys())

    # First create a product to update
    new_product = {
        "name": "Product to Update",
        "description": "Will be updated",
        "price": 50.00,
        "catalog_type_id": 2,
        "catalog_brand_id": 1,
        "available_stock": 100,
        "restock_threshold": 0,
        "max_stock_threshold": 0,
        "picture_file_name": "dummy.png"
    }

    create_response = await client.post("/api/catalog/items", json=new_product)
    assert create_response.status_code == 201
    created_id = create_response.json()["id"]

    # Update the product
    update_data = {
        "name": "Updated Product Name",
        "description": "Updated description",
        "price": 75.50,
        "catalog_type_id": 2,
        "catalog_brand_id": 3,  # Changed brand
        "available_stock": 150,
        "restock_threshold": 20,
        "max_stock_threshold": 200,
        "picture_file_name": "dummy.png"
    }

    response = await client.put(f"/api/catalog/items/{created_id}", json=update_data)

    # Assert response structure
    assert response.status_code == 200
    updated_product = response.json()

    # Assert all expected fields are present
    actual_fields = set(updated_product.keys())
    missing_fields = expected_fields - actual_fields
    assert not missing_fields, f"Missing fields in response: {missing_fields}"

    # Assert ID is preserved
    assert updated_product["id"] == created_id

    # Assert updated fields match
    assert updated_product["name"] == update_data["name"]
    assert Decimal(str(updated_product["price"])) == Decimal(str(update_data["price"]))
    assert updated_product["catalog_brand_id"] == update_data["catalog_brand_id"]

    # Assert navigation properties reflect the update
    assert updated_product["catalog_brand"]["id"] == update_data["catalog_brand_id"]


@pytest.mark.asyncio
async def test_delete_product_returns_no_content(client: AsyncClient):
    """
    Test DELETE /api/catalog/items/{id} returns 204 No Content.

    Golden baseline: Legacy Delete.aspx returns redirect, new API returns 204
    Comparison: Status code 204, no response body

    Note: This test verifies the DELETE workflow response
    """
    # First create a product to delete
    new_product = {
        "name": "Product to Delete",
        "description": "Will be deleted",
        "price": 10.00,
        "catalog_type_id": 1,
        "catalog_brand_id": 1,
        "available_stock": 0,
        "restock_threshold": 0,
        "max_stock_threshold": 0,
        "picture_file_name": "dummy.png"
    }

    create_response = await client.post("/api/catalog/items", json=new_product)
    assert create_response.status_code == 201
    created_id = create_response.json()["id"]

    # Delete the product
    response = await client.delete(f"/api/catalog/items/{created_id}")

    # Assert response
    assert response.status_code == 204, "DELETE should return 204 No Content"
    assert len(response.content) == 0, "DELETE should return empty body"

    # Verify product is actually deleted
    get_response = await client.get(f"/api/catalog/items/{created_id}")
    assert get_response.status_code == 404, "Deleted product should return 404"


@pytest.mark.asyncio
async def test_product_not_found_returns_404(client: AsyncClient):
    """
    Test GET /api/catalog/items/{invalid_id} returns 404.

    Golden baseline: Legacy app returns error page
    Comparison: Status code 404, error response structure

    Note: This test verifies edge case handling
    """
    # Try to get non-existent product
    response = await client.get("/api/catalog/items/99999")

    # Assert 404 response
    assert response.status_code == 404

    # Assert error response has message
    error = response.json()
    assert "detail" in error, "Error response should contain 'detail' field"
