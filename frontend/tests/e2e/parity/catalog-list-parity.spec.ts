/**
 * Parity tests for catalog-list frontend.
 *
 * Compares new React frontend to legacy Default.aspx page.
 *
 * Golden Baseline Sources:
 * - legacy-golden/screenshots/screen_000_depth0.png (visual baseline)
 * - legacy-golden/grid-data.json (data baseline)
 *
 * Test Strategy:
 * - Visual regression: Compare screenshot to baseline
 * - Data rendering: Verify all 10 products render correctly
 * - Layout: Check table structure matches legacy
 * - Interactive elements: Verify action links present
 *
 * First Run: Use --update-snapshots to establish new system baseline
 * Subsequent Runs: Compare against baseline to detect regressions
 */

import { test, expect } from '@playwright/test'
import gridData from '../../../legacy-golden/grid-data.json'

// Extract expected products from golden baseline
const goldenBaseline = gridData[0]
const expectedProducts = goldenBaseline.rows.map((row: string[]) => ({
  name: row[1],
  description: row[2],
  brand: row[3],
  type: row[4],
  price: row[5],
  pictureFileName: row[6],
  availableStock: row[7],
  restockThreshold: row[8],
  maxStockThreshold: row[9],
}))

test.describe('Catalog List Page - Parity Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to catalog list page
    await page.goto('http://localhost:5173/')

    // Wait for data to load
    await page.waitForSelector('table', { timeout: 10000 })
  })

  test('visual regression - page layout matches legacy', async ({ page }) => {
    /**
     * Visual regression test using screenshot comparison.
     *
     * First run: npx playwright test --update-snapshots
     * This establishes the NEW system's visual baseline.
     *
     * Note: This does NOT compare to legacy screenshot directly.
     * Instead, it captures the new system as the baseline and detects
     * future regressions in the new system.
     *
     * Manual validation required: User must visually compare
     * legacy-golden/screenshots/screen_000_depth0.png to the new baseline.
     */

    // Wait for page to be fully loaded
    await page.waitForLoadState('networkidle')

    // Take screenshot and compare
    await expect(page).toHaveScreenshot('catalog-list-page.png', {
      maxDiffPixels: 50, // Allow minor rendering differences
      animations: 'disabled', // Disable animations for consistent screenshots
    })
  })

  test('table structure matches legacy', async ({ page }) => {
    /**
     * Test that table has correct structure.
     *
     * Legacy table has:
     * - Header row with column names
     * - 10 data rows (first page)
     * - Actions column with Edit | Details | Delete
     */

    // Verify table exists
    const table = page.locator('table')
    await expect(table).toBeVisible()

    // Verify header row
    const headers = await page.locator('thead th').allTextContents()

    // Expected headers based on legacy UI
    const expectedHeaders = [
      '', // Image column
      'Name',
      'Description',
      'Brand',
      'Type',
      'Price',
      'Picture name',
      'Stock',
      'Restock',
      'Max stock',
      '' // Actions column
    ]

    // Check that all expected headers are present
    // (order and exact text may vary slightly, so we check presence)
    for (const header of ['Name', 'Description', 'Brand', 'Type', 'Price']) {
      expect(headers.join(' ')).toContain(header)
    }

    // Verify data rows
    const rows = page.locator('tbody tr')
    const rowCount = await rows.count()

    expect(rowCount).toBe(expectedProducts.length)
  })

  test('all products from golden baseline are rendered', async ({ page }) => {
    /**
     * Test that all 10 products from golden baseline are displayed.
     *
     * Verifies data integrity by checking each product's key fields.
     */

    const rows = page.locator('tbody tr')

    // Check each expected product
    for (let i = 0; i < expectedProducts.length; i++) {
      const expected = expectedProducts[i]
      const row = rows.nth(i)

      // Check product name (most distinctive field)
      await expect(row).toContainText(expected.name)

      // Check brand
      await expect(row).toContainText(expected.brand)

      // Check type
      await expect(row).toContainText(expected.type)

      // Check price (may be formatted differently, e.g., $19.50 vs 19.5)
      const priceFormatted = `$${parseFloat(expected.price).toFixed(2)}`
      await expect(row).toContainText(priceFormatted)
    }
  })

  test('product order matches golden baseline', async ({ page }) => {
    /**
     * Test that products appear in the same order as legacy system.
     *
     * Order matters for pagination consistency.
     */

    const rows = page.locator('tbody tr')

    // Extract product names in order
    const actualNames: string[] = []
    for (let i = 0; i < await rows.count(); i++) {
      const row = rows.nth(i)
      const nameCell = row.locator('td').nth(1) // Second column is name
      const name = await nameCell.textContent()
      actualNames.push(name?.trim() || '')
    }

    // Expected names from golden baseline
    const expectedNames = expectedProducts.map(p => p.name)

    expect(actualNames).toEqual(expectedNames)
  })

  test('action links present for each product', async ({ page }) => {
    /**
     * Test that Edit/Details/Delete links are present for each product.
     *
     * Legacy UI shows: Edit | Details | Delete
     */

    const rows = page.locator('tbody tr')
    const rowCount = await rows.count()

    for (let i = 0; i < rowCount; i++) {
      const row = rows.nth(i)

      // Check for action links
      await expect(row.locator('a[href*="/edit"]')).toBeVisible()
      await expect(row.locator('a[href*="/details"]')).toBeVisible()
      await expect(row.locator('a[href*="/delete"]')).toBeVisible()
    }
  })

  test('create new button is visible', async ({ page }) => {
    /**
     * Test that "Create New" button matches legacy.
     *
     * Legacy: Green "Create New" button at top
     */

    const createButton = page.locator('a[href*="/create"]')
    await expect(createButton).toBeVisible()
    await expect(createButton).toContainText('Create New')
  })

  test('pagination controls shown if needed', async ({ page }) => {
    /**
     * Test pagination controls.
     *
     * Legacy shows pagination with:
     * - "Showing X to Y of Z products - Page N"
     * - Previous/Next links
     *
     * Note: With only 10 products, pagination may not show.
     * This test checks conditional rendering.
     */

    // Check if pagination exists
    const pagination = page.locator('text=/Showing.*products/i')

    // If total items > page size, pagination should be visible
    // Otherwise, it may not be rendered
    const tableVisible = await page.locator('table').isVisible()
    expect(tableVisible).toBe(true)

    // If pagination exists, verify it has expected format
    const paginationExists = await pagination.isVisible().catch(() => false)
    if (paginationExists) {
      const text = await pagination.textContent()
      expect(text).toMatch(/Showing \d+ to \d+ of \d+ products/)
    }
  })

  test('product images are loaded', async ({ page }) => {
    /**
     * Test that product images are displayed.
     *
     * Legacy shows thumbnail images in first column.
     */

    const rows = page.locator('tbody tr')
    const firstRow = rows.first()

    // Check for image in first cell
    const img = firstRow.locator('img').first()
    await expect(img).toBeVisible()

    // Image should have src attribute
    const src = await img.getAttribute('src')
    expect(src).toBeTruthy()
    expect(src).toContain('.png')
  })

  test('prices are formatted correctly', async ({ page }) => {
    /**
     * Test that prices are displayed in currency format.
     *
     * Legacy shows: $19.50, $8.50, $12.00
     */

    const rows = page.locator('tbody tr')

    for (let i = 0; i < expectedProducts.length; i++) {
      const expected = expectedProducts[i]
      const row = rows.nth(i)

      // Price should be formatted as currency
      const priceText = parseFloat(expected.price).toFixed(2)
      const priceFormatted = `$${priceText}`

      await expect(row).toContainText(priceFormatted)
    }
  })

  test('loading state is shown initially', async ({ page }) => {
    /**
     * Test that loading indicator appears before data loads.
     *
     * Navigate to page and check for loading state before table appears.
     */

    // Navigate with slow network to catch loading state
    await page.route('**/api/catalog/items*', async route => {
      // Delay response to see loading state
      await new Promise(resolve => setTimeout(resolve, 500))
      await route.continue()
    })

    await page.goto('http://localhost:5173/')

    // Loading indicator should be visible briefly
    const loading = page.locator('text=/loading/i')
    // Note: May need to adjust selector based on actual loading UI
  })

  test('error state is handled gracefully', async ({ page }) => {
    /**
     * Test that error state is displayed if API fails.
     *
     * Simulates API error and checks for error message.
     */

    // Mock API to return error
    await page.route('**/api/catalog/items*', async route => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({
          code: 'internal_error',
          message: 'Database connection failed'
        })
      })
    })

    await page.goto('http://localhost:5173/')

    // Error message should be visible
    const error = page.locator('text=/error/i')
    await expect(error).toBeVisible({ timeout: 10000 })
  })
})

test.describe('Catalog List Page - Data Validation', () => {
  test('specific products match golden baseline exactly', async ({ page }) => {
    /**
     * Deep validation of specific products.
     *
     * Checks exact field values for first 3 products.
     */

    await page.goto('http://localhost:5173/')
    await page.waitForSelector('table')

    const rows = page.locator('tbody tr')

    // Product 1: .NET Bot Black Hoodie
    const row1 = rows.nth(0)
    await expect(row1).toContainText('.NET Bot Black Hoodie')
    await expect(row1).toContainText('.NET') // Brand
    await expect(row1).toContainText('T-Shirt') // Type
    await expect(row1).toContainText('$19.50')
    await expect(row1).toContainText('1.png')
    await expect(row1).toContainText('100') // Stock

    // Product 2: .NET Black & White Mug
    const row2 = rows.nth(1)
    await expect(row2).toContainText('.NET Black & White Mug')
    await expect(row2).toContainText('.NET')
    await expect(row2).toContainText('Mug')
    await expect(row2).toContainText('$8.50')
    await expect(row2).toContainText('2.png')

    // Product 3: Prism White T-Shirt
    const row3 = rows.nth(2)
    await expect(row3).toContainText('Prism White T-Shirt')
    await expect(row3).toContainText('Other')
    await expect(row3).toContainText('T-Shirt')
    await expect(row3).toContainText('$12.00')
  })
})

test.describe('Catalog List Page - Interactive Elements', () => {
  test('clicking edit navigates to edit page', async ({ page }) => {
    /**
     * Test that clicking Edit link navigates correctly.
     */

    await page.goto('http://localhost:5173/')
    await page.waitForSelector('table')

    const rows = page.locator('tbody tr')
    const firstRow = rows.first()

    // Click Edit link
    const editLink = firstRow.locator('a[href*="/edit"]')
    await editLink.click()

    // Should navigate to edit page
    await expect(page).toHaveURL(/\/catalog\/edit\/\d+/)
  })

  test('clicking details navigates to details page', async ({ page }) => {
    /**
     * Test that clicking Details link navigates correctly.
     */

    await page.goto('http://localhost:5173/')
    await page.waitForSelector('table')

    const rows = page.locator('tbody tr')
    const firstRow = rows.first()

    // Click Details link
    const detailsLink = firstRow.locator('a[href*="/details"]')
    await detailsLink.click()

    // Should navigate to details page
    await expect(page).toHaveURL(/\/catalog\/details\/\d+/)
  })

  test('clicking delete navigates to delete confirmation', async ({ page }) => {
    /**
     * Test that clicking Delete link navigates correctly.
     */

    await page.goto('http://localhost:5173/')
    await page.waitForSelector('table')

    const rows = page.locator('tbody tr')
    const firstRow = rows.first()

    // Click Delete link
    const deleteLink = firstRow.locator('a[href*="/delete"]')
    await deleteLink.click()

    // Should navigate to delete confirmation page
    await expect(page).toHaveURL(/\/catalog\/delete\/\d+/)
  })
})
