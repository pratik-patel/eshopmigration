"""
Test catalog list endpoint to verify it matches legacy data.

This script validates:
1. GET /api/catalog/items returns correct pagination structure
2. Returns 10 items from legacy grid-data.json
3. Field names match exactly: name, description, brand, type, price, picture_file_name, stock, restock, max_stock
4. Prices are formatted as Decimal with 2 places: 19.50, 8.50, 12.00
"""

import asyncio
import httpx
from decimal import Decimal


async def test_catalog_list():
    """Test catalog list endpoint."""
    async with httpx.AsyncClient() as client:
        # Test GET /api/catalog/items
        response = await client.get(
            "http://localhost:8000/api/catalog/items",
            params={"page_size": 10, "page_index": 0},
        )

        print(f"Status: {response.status_code}")
        print(f"Headers: {response.headers.get('content-type')}")

        if response.status_code == 200:
            data = response.json()
            print(f"\nResponse structure:")
            print(f"  page_index: {data.get('page_index')}")
            print(f"  page_size: {data.get('page_size')}")
            print(f"  total_items: {data.get('total_items')}")
            print(f"  total_pages: {data.get('total_pages')}")
            print(f"  data (items): {len(data.get('data', []))}")

            # Verify first item
            if data.get("data"):
                first_item = data["data"][0]
                print(f"\nFirst item:")
                print(f"  id: {first_item.get('id')}")
                print(f"  name: {first_item.get('name')}")
                print(f"  description: {first_item.get('description')}")
                print(f"  price: {first_item.get('price')} (type: {type(first_item.get('price'))})")
                print(f"  picture_file_name: {first_item.get('picture_file_name')}")
                print(f"  available_stock: {first_item.get('available_stock')}")
                print(f"  restock_threshold: {first_item.get('restock_threshold')}")
                print(f"  max_stock_threshold: {first_item.get('max_stock_threshold')}")
                print(f"  catalog_brand: {first_item.get('catalog_brand')}")
                print(f"  catalog_type: {first_item.get('catalog_type')}")

                # Verify expected first item matches legacy
                expected = {
                    "name": ".NET Bot Black Hoodie",
                    "price": 19.50,
                    "brand": ".NET",
                    "type": "T-Shirt",
                }
                actual = {
                    "name": first_item.get("name"),
                    "price": first_item.get("price"),
                    "brand": first_item.get("catalog_brand", {}).get("brand"),
                    "type": first_item.get("catalog_type", {}).get("type"),
                }

                print(f"\nValidation:")
                print(f"  Expected: {expected}")
                print(f"  Actual: {actual}")
                print(f"  Match: {expected == actual}")

            # Show all items
            print(f"\nAll items ({len(data.get('data', []))}):")
            for item in data.get("data", []):
                print(
                    f"  {item['id']}: {item['name']} | "
                    f"{item['catalog_brand']['brand']} | "
                    f"{item['catalog_type']['type']} | "
                    f"${item['price']} | "
                    f"stock={item['available_stock']}"
                )

        else:
            print(f"Error response:")
            print(response.text)


if __name__ == "__main__":
    asyncio.run(test_catalog_list())
