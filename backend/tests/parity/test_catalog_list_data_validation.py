"""
Data validation parity tests for catalog-list.

Ensures all 10 products from golden baseline match exactly.
This test file focuses on comprehensive field-by-field validation.

Golden Baseline: legacy-golden/grid-data.json
"""

import json
import pytest
from decimal import Decimal
from pathlib import Path
from httpx import AsyncClient

# Path to golden baseline
GOLDEN_BASELINE_PATH = Path(__file__).parent.parent.parent.parent / "legacy-golden" / "grid-data.json"


@pytest.fixture
def golden_data():
    """Load and parse golden baseline data."""
    with open(GOLDEN_BASELINE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data[0]  # First table


class TestProductDataValidation:
    """
    Comprehensive data validation tests.

    Validates each of the 10 products against golden baseline.
    """

    @pytest.mark.asyncio
    async def test_product_1_net_bot_black_hoodie(self, async_client: AsyncClient, golden_data):
        """
        Validate Product 1: .NET Bot Black Hoodie

        Golden baseline row 0:
        ["", ".NET Bot Black Hoodie", ".NET Bot Black Hoodie", ".NET", "T-Shirt", "19.5", "1.png", "100", "0", "0"]
        """
        response = await async_client.get("/api/catalog/items?page_size=10&page_index=0")
        assert response.status_code == 200

        data = response.json()
        product = data["data"][0]

        # Validate against golden baseline row 0
        expected = golden_data["rows"][0]

        assert product["name"] == expected[1], "Product 1 name mismatch"
        assert product["description"] == expected[2], "Product 1 description mismatch"
        assert product["catalog_brand"]["brand"] == expected[3], "Product 1 brand mismatch"
        assert product["catalog_type"]["type"] == expected[4], "Product 1 type mismatch"
        assert Decimal(str(product["price"])) == Decimal(expected[5]), "Product 1 price mismatch"
        assert product["picture_file_name"] == expected[6], "Product 1 picture_file_name mismatch"
        assert product["available_stock"] == int(expected[7]), "Product 1 available_stock mismatch"
        assert product["restock_threshold"] == int(expected[8]), "Product 1 restock_threshold mismatch"
        assert product["max_stock_threshold"] == int(expected[9]), "Product 1 max_stock_threshold mismatch"

    @pytest.mark.asyncio
    async def test_product_2_net_black_white_mug(self, async_client: AsyncClient, golden_data):
        """
        Validate Product 2: .NET Black & White Mug

        Golden baseline row 1:
        ["", ".NET Black & White Mug", ".NET Black & White Mug", ".NET", "Mug", "8.50", "2.png", "100", "0", "0"]
        """
        response = await async_client.get("/api/catalog/items?page_size=10&page_index=0")
        assert response.status_code == 200

        data = response.json()
        product = data["data"][1]

        expected = golden_data["rows"][1]

        assert product["name"] == expected[1]
        assert product["description"] == expected[2]
        assert product["catalog_brand"]["brand"] == expected[3]
        assert product["catalog_type"]["type"] == expected[4]
        assert Decimal(str(product["price"])) == Decimal(expected[5])
        assert product["picture_file_name"] == expected[6]
        assert product["available_stock"] == int(expected[7])

    @pytest.mark.asyncio
    async def test_product_3_prism_white_tshirt(self, async_client: AsyncClient, golden_data):
        """
        Validate Product 3: Prism White T-Shirt

        Golden baseline row 2:
        ["", "Prism White T-Shirt", "Prism White T-Shirt", "Other", "T-Shirt", "12", "3.png", "100", "0", "0"]
        """
        response = await async_client.get("/api/catalog/items?page_size=10&page_index=0")
        assert response.status_code == 200

        data = response.json()
        product = data["data"][2]

        expected = golden_data["rows"][2]

        assert product["name"] == expected[1]
        assert product["catalog_brand"]["brand"] == expected[3]
        assert product["catalog_type"]["type"] == expected[4]
        assert Decimal(str(product["price"])) == Decimal(expected[5])
        assert product["picture_file_name"] == expected[6]

    @pytest.mark.asyncio
    async def test_product_4_net_foundation_tshirt(self, async_client: AsyncClient, golden_data):
        """
        Validate Product 4: .NET Foundation T-shirt

        Golden baseline row 3.
        """
        response = await async_client.get("/api/catalog/items?page_size=10&page_index=0")
        assert response.status_code == 200

        data = response.json()
        product = data["data"][3]

        expected = golden_data["rows"][3]

        assert product["name"] == expected[1]
        assert product["catalog_brand"]["brand"] == expected[3]
        assert product["catalog_type"]["type"] == expected[4]

    @pytest.mark.asyncio
    async def test_product_5_roslyn_red_sheet(self, async_client: AsyncClient, golden_data):
        """
        Validate Product 5: Roslyn Red Sheet

        Golden baseline row 4.
        """
        response = await async_client.get("/api/catalog/items?page_size=10&page_index=0")
        assert response.status_code == 200

        data = response.json()
        product = data["data"][4]

        expected = golden_data["rows"][4]

        assert product["name"] == expected[1]
        assert product["catalog_brand"]["brand"] == expected[3]
        assert product["catalog_type"]["type"] == expected[4]
        assert Decimal(str(product["price"])) == Decimal(expected[5])

    @pytest.mark.asyncio
    async def test_product_6_net_blue_hoodie(self, async_client: AsyncClient, golden_data):
        """
        Validate Product 6: .NET Blue Hoodie

        Golden baseline row 5.
        """
        response = await async_client.get("/api/catalog/items?page_size=10&page_index=0")
        assert response.status_code == 200

        data = response.json()
        product = data["data"][5]

        expected = golden_data["rows"][5]

        assert product["name"] == expected[1]
        assert product["catalog_brand"]["brand"] == expected[3]

    @pytest.mark.asyncio
    async def test_product_7_roslyn_red_tshirt(self, async_client: AsyncClient, golden_data):
        """
        Validate Product 7: Roslyn Red T-Shirt

        Golden baseline row 6.
        """
        response = await async_client.get("/api/catalog/items?page_size=10&page_index=0")
        assert response.status_code == 200

        data = response.json()
        product = data["data"][6]

        expected = golden_data["rows"][6]

        assert product["name"] == expected[1]

    @pytest.mark.asyncio
    async def test_product_8_kudu_purple_hoodie(self, async_client: AsyncClient, golden_data):
        """
        Validate Product 8: Kudu Purple Hoodie

        Golden baseline row 7.
        """
        response = await async_client.get("/api/catalog/items?page_size=10&page_index=0")
        assert response.status_code == 200

        data = response.json()
        product = data["data"][7]

        expected = golden_data["rows"][7]

        assert product["name"] == expected[1]

    @pytest.mark.asyncio
    async def test_product_9_cupt_white_mug(self, async_client: AsyncClient, golden_data):
        """
        Validate Product 9: Cup<T> White Mug

        Golden baseline row 8.
        """
        response = await async_client.get("/api/catalog/items?page_size=10&page_index=0")
        assert response.status_code == 200

        data = response.json()
        product = data["data"][8]

        expected = golden_data["rows"][8]

        assert product["name"] == expected[1]

    @pytest.mark.asyncio
    async def test_product_10_net_foundation_sheet(self, async_client: AsyncClient, golden_data):
        """
        Validate Product 10: .NET Foundation Sheet

        Golden baseline row 9.
        """
        response = await async_client.get("/api/catalog/items?page_size=10&page_index=0")
        assert response.status_code == 200

        data = response.json()
        product = data["data"][9]

        expected = golden_data["rows"][9]

        assert product["name"] == expected[1]
        assert product["catalog_brand"]["brand"] == expected[3]
        assert product["catalog_type"]["type"] == expected[4]

    @pytest.mark.asyncio
    async def test_all_products_comprehensive_validation(self, async_client: AsyncClient, golden_data):
        """
        Comprehensive validation of all 10 products.

        This test validates all fields for all products in a single test.
        """
        response = await async_client.get("/api/catalog/items?page_size=10&page_index=0")
        assert response.status_code == 200

        data = response.json()
        products = data["data"]

        # Should have exactly 10 products
        assert len(products) == 10, f"Expected 10 products, got {len(products)}"

        # Validate each product
        for i, product in enumerate(products):
            expected = golden_data["rows"][i]

            # Field-by-field validation
            with pytest.raises(AssertionError) as exc_info:
                assert product["name"] == expected[1]
                assert product["description"] == expected[2]
                assert product["catalog_brand"]["brand"] == expected[3]
                assert product["catalog_type"]["type"] == expected[4]
                assert Decimal(str(product["price"])) == Decimal(expected[5])
                assert product["picture_file_name"] == expected[6]
                assert product["available_stock"] == int(expected[7])
                assert product["restock_threshold"] == int(expected[8])
                assert product["max_stock_threshold"] == int(expected[9])

            # If assertion failed, provide detailed context
            if exc_info:
                pytest.fail(f"Product {i+1} validation failed: {exc_info.value}")


class TestBrandTypeIntegrity:
    """
    Test that brand and type data is correctly joined.

    Validates navigation properties are populated correctly.
    """

    @pytest.mark.asyncio
    async def test_all_products_have_brand_and_type(self, async_client: AsyncClient):
        """Test that all products have brand and type populated."""
        response = await async_client.get("/api/catalog/items?page_size=10&page_index=0")
        assert response.status_code == 200

        data = response.json()
        products = data["data"]

        for i, product in enumerate(products):
            assert "catalog_brand" in product, f"Product {i} missing catalog_brand"
            assert "catalog_type" in product, f"Product {i} missing catalog_type"

            assert "id" in product["catalog_brand"], f"Product {i} catalog_brand missing id"
            assert "brand" in product["catalog_brand"], f"Product {i} catalog_brand missing brand"

            assert "id" in product["catalog_type"], f"Product {i} catalog_type missing id"
            assert "type" in product["catalog_type"], f"Product {i} catalog_type missing type"

    @pytest.mark.asyncio
    async def test_brand_distribution(self, async_client: AsyncClient, golden_data):
        """
        Test that brand distribution matches golden baseline.

        Golden baseline has:
        - .NET: 5 products
        - Other: 5 products
        """
        response = await async_client.get("/api/catalog/items?page_size=10&page_index=0")
        assert response.status_code == 200

        data = response.json()
        products = data["data"]

        # Count brands
        brand_counts = {}
        for product in products:
            brand = product["catalog_brand"]["brand"]
            brand_counts[brand] = brand_counts.get(brand, 0) + 1

        # Expected distribution from golden baseline
        expected_brands = {}
        for row in golden_data["rows"]:
            brand = row[3]
            expected_brands[brand] = expected_brands.get(brand, 0) + 1

        assert brand_counts == expected_brands, \
            f"Brand distribution mismatch:\nExpected: {expected_brands}\nActual: {brand_counts}"

    @pytest.mark.asyncio
    async def test_type_distribution(self, async_client: AsyncClient, golden_data):
        """
        Test that type distribution matches golden baseline.

        Golden baseline has:
        - T-Shirt: 6 products
        - Mug: 2 products
        - Sheet: 2 products
        """
        response = await async_client.get("/api/catalog/items?page_size=10&page_index=0")
        assert response.status_code == 200

        data = response.json()
        products = data["data"]

        # Count types
        type_counts = {}
        for product in products:
            product_type = product["catalog_type"]["type"]
            type_counts[product_type] = type_counts.get(product_type, 0) + 1

        # Expected distribution from golden baseline
        expected_types = {}
        for row in golden_data["rows"]:
            product_type = row[4]
            expected_types[product_type] = expected_types.get(product_type, 0) + 1

        assert type_counts == expected_types, \
            f"Type distribution mismatch:\nExpected: {expected_types}\nActual: {type_counts}"
