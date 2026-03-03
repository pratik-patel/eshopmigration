"""
Parity tests for catalog-list API.

Compares new API (GET /api/catalog/items) responses to legacy golden baseline data.

Golden Baseline Source:
- legacy-golden/grid-data.json (captured from http://localhost:50586/)

Test Strategy:
- Load golden baseline data from grid-data.json
- Compare API response structure and field values
- Verify pagination metadata calculations
- Ensure all 10 products from golden baseline match exactly
- Exclude auto-generated fields if needed (timestamps, picture_uri)

Expected Result: PASS if new API returns same data as legacy system
"""

import json
import pytest
from decimal import Decimal
from pathlib import Path
from httpx import AsyncClient

# Path to golden baseline
GOLDEN_BASELINE_PATH = Path(__file__).parent.parent.parent.parent / "legacy-golden" / "grid-data.json"


@pytest.fixture
def golden_baseline():
    """Load golden baseline data from grid-data.json."""
    with open(GOLDEN_BASELINE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    # Return first table (table index 0)
    return data[0]


@pytest.fixture
def expected_products(golden_baseline):
    """
    Extract expected product data from golden baseline.

    Maps HTML table rows to structured product data.

    Golden baseline row format:
    ["", "Name", "Description", "Brand", "Type", "Price", "PictureFileName", "Stock", "Restock", "MaxStock", "Actions"]
    """
    products = []

    for row in golden_baseline["rows"]:
        # Skip empty first column (checkbox/image placeholder)
        # Row structure: ["", name, description, brand, type, price, picture, stock, restock, max_stock, actions]
        product = {
            "name": row[1],
            "description": row[2],
            "brand": row[3],
            "type": row[4],
            "price": Decimal(row[5]),
            "picture_file_name": row[6],
            "available_stock": int(row[7]),
            "restock_threshold": int(row[8]),
            "max_stock_threshold": int(row[9]),
        }
        products.append(product)

    return products


class TestCatalogListAPIParity:
    """
    Parity tests comparing new API to legacy golden baseline.

    These tests verify that the migrated API returns exactly the same data
    as the legacy Default.aspx page.
    """

    @pytest.mark.asyncio
    async def test_first_page_row_count(self, async_client: AsyncClient, golden_baseline):
        """
        Test that first page returns correct number of rows.

        Golden baseline shows 10 products on first page.
        """
        response = await async_client.get("/api/catalog/items?page_size=10&page_index=0")

        assert response.status_code == 200
        data = response.json()

        # Verify row count matches golden baseline
        assert len(data["data"]) == golden_baseline["totalRows"], \
            f"Expected {golden_baseline['totalRows']} products, got {len(data['data'])}"

    @pytest.mark.asyncio
    async def test_pagination_metadata(self, async_client: AsyncClient):
        """
        Test that pagination metadata is calculated correctly.

        Golden baseline has 10 products total.
        With page_size=10, should have 1 page.
        """
        response = await async_client.get("/api/catalog/items?page_size=10&page_index=0")

        assert response.status_code == 200
        data = response.json()

        # Verify pagination structure
        assert "page_index" in data
        assert "page_size" in data
        assert "total_items" in data
        assert "total_pages" in data

        # Verify pagination values
        assert data["page_index"] == 0, "First page should have page_index=0"
        assert data["page_size"] == 10, "Page size should be 10"
        # Note: total_items may vary if database was seeded differently
        # We verify that total_pages = ceil(total_items / page_size)
        expected_total_pages = (data["total_items"] + data["page_size"] - 1) // data["page_size"]
        assert data["total_pages"] == expected_total_pages, \
            f"total_pages calculation incorrect: {data['total_pages']} != ceil({data['total_items']} / {data['page_size']})"

    @pytest.mark.asyncio
    async def test_product_field_structure(self, async_client: AsyncClient):
        """
        Test that each product has all required fields with correct types.

        Verifies API contract compliance.
        """
        response = await async_client.get("/api/catalog/items?page_size=10&page_index=0")

        assert response.status_code == 200
        data = response.json()

        assert len(data["data"]) > 0, "Should have at least one product"

        # Check first product structure
        product = data["data"][0]

        # Required fields from OpenAPI spec
        required_fields = [
            "id", "name", "description", "price", "picture_file_name",
            "catalog_type_id", "catalog_brand_id", "available_stock",
            "restock_threshold", "max_stock_threshold", "on_reorder",
            "catalog_type", "catalog_brand"
        ]

        for field in required_fields:
            assert field in product, f"Missing required field: {field}"

        # Verify nested objects
        assert "id" in product["catalog_type"]
        assert "type" in product["catalog_type"]
        assert "id" in product["catalog_brand"]
        assert "brand" in product["catalog_brand"]

    @pytest.mark.asyncio
    async def test_product_data_matches_golden_baseline(
        self, async_client: AsyncClient, expected_products
    ):
        """
        Test that product data matches golden baseline exactly.

        Compares field-by-field for all products on first page.

        Exclusions:
        - id: Auto-generated primary key (not in baseline)
        - catalog_type_id: Foreign key (not in baseline)
        - catalog_brand_id: Foreign key (not in baseline)
        - picture_uri: Legacy field (always null)
        - on_reorder: Calculated field (not in baseline)
        """
        response = await async_client.get("/api/catalog/items?page_size=10&page_index=0")

        assert response.status_code == 200
        data = response.json()

        actual_products = data["data"]

        # Should have same number of products
        assert len(actual_products) == len(expected_products), \
            f"Product count mismatch: expected {len(expected_products)}, got {len(actual_products)}"

        # Compare each product
        for i, (actual, expected) in enumerate(zip(actual_products, expected_products)):
            # Name
            assert actual["name"] == expected["name"], \
                f"Product {i}: name mismatch - expected '{expected['name']}', got '{actual['name']}'"

            # Description
            assert actual["description"] == expected["description"], \
                f"Product {i}: description mismatch - expected '{expected['description']}', got '{actual['description']}'"

            # Brand (via navigation property)
            assert actual["catalog_brand"]["brand"] == expected["brand"], \
                f"Product {i}: brand mismatch - expected '{expected['brand']}', got '{actual['catalog_brand']['brand']}'"

            # Type (via navigation property)
            assert actual["catalog_type"]["type"] == expected["type"], \
                f"Product {i}: type mismatch - expected '{expected['type']}', got '{actual['catalog_type']['type']}'"

            # Price (compare as Decimal to avoid floating point issues)
            actual_price = Decimal(str(actual["price"]))
            assert actual_price == expected["price"], \
                f"Product {i}: price mismatch - expected {expected['price']}, got {actual_price}"

            # Picture file name
            assert actual["picture_file_name"] == expected["picture_file_name"], \
                f"Product {i}: picture_file_name mismatch - expected '{expected['picture_file_name']}', got '{actual['picture_file_name']}'"

            # Available stock
            assert actual["available_stock"] == expected["available_stock"], \
                f"Product {i}: available_stock mismatch - expected {expected['available_stock']}, got {actual['available_stock']}"

            # Restock threshold
            assert actual["restock_threshold"] == expected["restock_threshold"], \
                f"Product {i}: restock_threshold mismatch - expected {expected['restock_threshold']}, got {actual['restock_threshold']}"

            # Max stock threshold
            assert actual["max_stock_threshold"] == expected["max_stock_threshold"], \
                f"Product {i}: max_stock_threshold mismatch - expected {expected['max_stock_threshold']}, got {actual['max_stock_threshold']}"

    @pytest.mark.asyncio
    async def test_product_order_preserved(self, async_client: AsyncClient, expected_products):
        """
        Test that products are returned in the same order as golden baseline.

        Order matters for pagination consistency.
        """
        response = await async_client.get("/api/catalog/items?page_size=10&page_index=0")

        assert response.status_code == 200
        data = response.json()

        actual_products = data["data"]

        # Compare product names in order
        actual_names = [p["name"] for p in actual_products]
        expected_names = [p["name"] for p in expected_products]

        assert actual_names == expected_names, \
            f"Product order mismatch:\nExpected: {expected_names}\nActual: {actual_names}"

    @pytest.mark.asyncio
    async def test_default_parameters(self, async_client: AsyncClient):
        """
        Test that default parameters work correctly.

        Default.aspx uses page_size=10, page_index=0 by default.
        """
        # Request without query parameters
        response = await async_client.get("/api/catalog/items")

        assert response.status_code == 200
        data = response.json()

        # Should use default values
        assert data["page_index"] == 0, "Default page_index should be 0"
        assert data["page_size"] == 10, "Default page_size should be 10"

    @pytest.mark.asyncio
    async def test_empty_catalog_handling(self, async_client: AsyncClient):
        """
        Test handling of empty catalog (edge case).

        Not captured in golden baseline but should return valid structure.
        """
        # Request a page beyond available data
        response = await async_client.get("/api/catalog/items?page_size=10&page_index=999")

        assert response.status_code == 200
        data = response.json()

        # Should return empty data array
        assert data["data"] == []
        assert data["page_index"] == 999
        assert data["page_size"] == 10

    @pytest.mark.asyncio
    async def test_price_precision(self, async_client: AsyncClient):
        """
        Test that prices are returned with correct decimal precision.

        Golden baseline shows prices like "19.5" and "8.50".
        API should return as numbers with max 2 decimal places.
        """
        response = await async_client.get("/api/catalog/items?page_size=10&page_index=0")

        assert response.status_code == 200
        data = response.json()

        for product in data["data"]:
            price = Decimal(str(product["price"]))

            # Check decimal places
            exponent = price.as_tuple().exponent
            assert exponent >= -2, \
                f"Price {price} has more than 2 decimal places (exponent: {exponent})"


class TestCatalogListAPIValidation:
    """
    Tests for API validation rules.

    Verifies that the API enforces business rules and constraints.
    """

    @pytest.mark.asyncio
    async def test_page_size_minimum_validation(self, async_client: AsyncClient):
        """Test that page_size < 1 is rejected."""
        response = await async_client.get("/api/catalog/items?page_size=0&page_index=0")

        # Should return validation error
        assert response.status_code == 422  # FastAPI validation error

    @pytest.mark.asyncio
    async def test_page_size_maximum_validation(self, async_client: AsyncClient):
        """Test that page_size > max is rejected."""
        response = await async_client.get("/api/catalog/items?page_size=101&page_index=0")

        # Should return validation error
        assert response.status_code == 422  # FastAPI validation error

    @pytest.mark.asyncio
    async def test_page_index_minimum_validation(self, async_client: AsyncClient):
        """Test that negative page_index is rejected."""
        response = await async_client.get("/api/catalog/items?page_size=10&page_index=-1")

        # Should return validation error
        assert response.status_code == 422  # FastAPI validation error
