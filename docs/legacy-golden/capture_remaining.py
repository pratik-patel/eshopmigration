"""
Capture remaining baseline pages (Details, Edit, Delete) using known product IDs.
"""

import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path
from playwright.async_api import async_playwright

BASE_URL = "http://localhost:50586"
OUTPUT_DIR = Path(__file__).parent / "catalog-management"
SCREENSHOTS_DIR = OUTPUT_DIR / "screenshots"
DATA_DIR = OUTPUT_DIR / "data-snapshots"

VIEWPORT_WIDTH = 1920
VIEWPORT_HEIGHT = 1080

# Use product ID 1 (found in the HTML)
PRODUCT_ID = "1"


async def capture_page(page, url, name, description):
    """Capture a single page."""
    print(f"Capturing: {name} ({url})")

    full_url = f"{BASE_URL}{url}"
    try:
        await page.goto(full_url, wait_until="networkidle", timeout=10000)
        await page.wait_for_selector("body", timeout=5000)
        await asyncio.sleep(0.5)

        screenshot_path = SCREENSHOTS_DIR / f"{name}.png"
        await page.screenshot(path=str(screenshot_path), full_page=True)

        title = await page.title()
        print(f"  [OK] Screenshot saved: {screenshot_path.name} (Title: {title})")
        return True

    except Exception as e:
        print(f"  [FAIL] Failed to capture {name}: {e}")
        return False


async def extract_product_details(page):
    """Extract product details from the Details page."""
    try:
        product_data = await page.evaluate("""
            () => {
                const getText = (selector) => {
                    const el = document.querySelector(selector);
                    return el ? el.innerText.trim() : null;
                };

                return {
                    name: getText('h2, .product-name, [class*="name"]'),
                    price: getText('.esh-price, .price, [class*="price"]'),
                    description: getText('.esh-catalog-description, .description'),
                    brand: getText('.esh-catalog-brand, .brand'),
                    type: getText('.esh-catalog-type, .type')
                };
            }
        """)

        snapshot = {
            "page": "product_details",
            "product_id": PRODUCT_ID,
            "captured_at": datetime.now(timezone.utc).isoformat(),
            "data": product_data
        }

        data_path = DATA_DIR / f"product_{PRODUCT_ID}_details.json"
        with open(data_path, "w") as f:
            json.dump(snapshot, f, indent=2)

        print(f"  [OK] Saved product details data")
        return product_data

    except Exception as e:
        print(f"  [FAIL] Failed to extract product details: {e}")
        return None


async def main():
    print("=" * 60)
    print("Capturing Remaining Baseline Pages")
    print("=" * 60)
    print()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": VIEWPORT_WIDTH, "height": VIEWPORT_HEIGHT}
        )
        page = await context.new_page()

        # Capture Details page
        success = await capture_page(
            page,
            f"/Catalog/Details/{PRODUCT_ID}",
            "03_product_details",
            "Product details view"
        )

        if success:
            await extract_product_details(page)

        # Capture Edit page
        await capture_page(
            page,
            f"/Catalog/Edit/{PRODUCT_ID}",
            "04_edit_product",
            "Edit product form"
        )

        # Capture Delete page
        await capture_page(
            page,
            f"/Catalog/Delete/{PRODUCT_ID}",
            "05_delete_confirmation",
            "Delete product confirmation"
        )

        await browser.close()

    print()
    print("=" * 60)
    print("Remaining pages captured successfully!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
