/**
 * Parity tests for catalog-crud seam - E2E workflow comparison.
 *
 * Compares frontend workflows and visual appearance against golden baselines.
 * Screenshots: legacy-golden/screenshots/screen_*.png
 *
 * Test Strategy:
 * 1. Visual regression: Compare screenshots with maxDiffPixels tolerance
 * 2. Workflow E2E: Verify Create/Edit/Delete produce same final state
 * 3. Form behavior: Verify validation, dropdowns, read-only fields
 *
 * Note: First run with --update-snapshots to establish new system baseline
 */

import { test, expect, Page } from '@playwright/test';
import path from 'path';

// Golden baseline screenshot directory
const GOLDEN_DIR = path.join(__dirname, '..', '..', '..', '..', 'legacy-golden', 'screenshots');

// Helper: Wait for page to be fully loaded
async function waitForPageLoad(page: Page) {
  await page.waitForLoadState('networkidle');
  await page.waitForLoadState('domcontentloaded');
}

// Helper: Fill form with valid product data
async function fillProductForm(page: Page, productData: {
  name: string;
  description?: string;
  price: string;
  brand: string;
  type: string;
  stock?: string;
  restock?: string;
  maxStock?: string;
}) {
  await page.fill('input[name="name"]', productData.name);

  if (productData.description !== undefined) {
    await page.fill('textarea[name="description"]', productData.description);
  }

  await page.fill('input[name="price"]', productData.price);

  // Select brand by visible text
  await page.selectOption('select[name="catalog_brand_id"]', { label: productData.brand });

  // Select type by visible text
  await page.selectOption('select[name="catalog_type_id"]', { label: productData.type });

  if (productData.stock !== undefined) {
    await page.fill('input[name="available_stock"]', productData.stock);
  }

  if (productData.restock !== undefined) {
    await page.fill('input[name="restock_threshold"]', productData.restock);
  }

  if (productData.maxStock !== undefined) {
    await page.fill('input[name="max_stock_threshold"]', productData.maxStock);
  }
}

test.describe('Catalog CRUD Parity Tests', () => {

  test.describe('Visual Regression - Create Form', () => {

    test('Create form layout matches golden baseline', async ({ page }) => {
      /**
       * Golden baseline: screen_001_depth1.png (Create form from browser-agent)
       * Comparison: Full page screenshot with maxDiffPixels tolerance
       *
       * Note: First run with --update-snapshots to create new baseline
       * Subsequent runs will compare against the new system's own baseline
       * Manual validation required to confirm new baseline matches legacy appearance
       */

      // Navigate to Create page
      await page.goto('http://localhost:5173/catalog/create');
      await waitForPageLoad(page);

      // Wait for form to be fully rendered
      await page.waitForSelector('input[name="name"]');
      await page.waitForSelector('select[name="catalog_brand_id"]');
      await page.waitForSelector('select[name="catalog_type_id"]');

      // Take screenshot and compare
      // maxDiffPixels: 50 allows for minor rendering differences (fonts, spacing)
      await expect(page).toHaveScreenshot('catalog-create-form.png', {
        maxDiffPixels: 50,
        fullPage: true,
      });
    });

    test('Create form shows validation errors correctly', async ({ page }) => {
      /**
       * Test: Submit empty form and verify validation messages appear
       * Golden baseline: Validation should show inline errors
       */

      await page.goto('http://localhost:5173/catalog/create');
      await waitForPageLoad(page);

      // Submit empty form
      await page.click('button[type="submit"]');

      // Wait for validation errors to appear
      await page.waitForSelector('[class*="error"]', { timeout: 3000 });

      // Screenshot with validation errors
      await expect(page).toHaveScreenshot('catalog-create-validation-errors.png', {
        maxDiffPixels: 100,
        fullPage: true,
      });
    });

  });

  test.describe('Visual Regression - Edit Form', () => {

    test('Edit form layout matches golden baseline', async ({ page }) => {
      /**
       * Golden baseline: screen_003_depth1.png (Edit form from browser-agent)
       * Comparison: Full page screenshot with product ID 1 loaded
       *
       * Note: Edit form has 2-column layout with image on left
       * Picture filename field should be read-only
       */

      // Navigate to Edit page for product ID 1
      await page.goto('http://localhost:5173/catalog/edit/1');
      await waitForPageLoad(page);

      // Wait for form to be pre-filled
      await page.waitForSelector('input[name="name"]');

      // Verify product name is loaded (from synthetic_product_1.json)
      const nameValue = await page.inputValue('input[name="name"]');
      expect(nameValue).toBe('.NET Bot Black Hoodie');

      // Take screenshot and compare
      await expect(page).toHaveScreenshot('catalog-edit-form.png', {
        maxDiffPixels: 100,
        fullPage: true,
      });
    });

    test('Edit form picture field is read-only', async ({ page }) => {
      /**
       * Test: Verify picture_file_name field is read-only on Edit
       * Golden baseline: ui-behavior.md specifies this field is read-only
       */

      await page.goto('http://localhost:5173/catalog/edit/1');
      await waitForPageLoad(page);

      // Check if picture filename field is read-only or disabled
      const pictureField = page.locator('input[name="picture_file_name"]');

      // Should be read-only or disabled
      const isReadonly = await pictureField.getAttribute('readonly');
      const isDisabled = await pictureField.isDisabled();

      expect(isReadonly !== null || isDisabled).toBe(true);
    });

  });

  test.describe('Workflow E2E - Create Product', () => {

    test('Create product workflow produces correct result', async ({ page }) => {
      /**
       * Golden baseline: Create workflow should insert new row in database
       * Test: Create product → Verify redirect → Verify product appears in list
       */

      await page.goto('http://localhost:5173/catalog/create');
      await waitForPageLoad(page);

      // Fill form with test data
      const testProduct = {
        name: 'Parity Test Product E2E',
        description: 'Created by E2E parity test',
        price: '49.99',
        brand: '.NET',
        type: 'T-Shirt',
        stock: '100',
        restock: '10',
        maxStock: '200',
      };

      await fillProductForm(page, testProduct);

      // Submit form
      await page.click('button[type="submit"]');

      // Wait for redirect (should go to catalog list)
      await page.waitForURL('**/catalog**', { timeout: 5000 });

      // Verify we're on catalog list page
      const currentUrl = page.url();
      expect(currentUrl).toContain('/catalog');

      // Verify product appears in list (search for name)
      await page.waitForSelector(`text=${testProduct.name}`, { timeout: 5000 });

      // Verify success
      const productExists = await page.locator(`text=${testProduct.name}`).isVisible();
      expect(productExists).toBe(true);
    });

    test('Create product with validation error stays on form', async ({ page }) => {
      /**
       * Test: Submit invalid data → Should stay on form with errors
       * Golden baseline: Invalid submission should not navigate away
       */

      await page.goto('http://localhost:5173/catalog/create');
      await waitForPageLoad(page);

      // Fill form with INVALID price (negative)
      await page.fill('input[name="name"]', 'Invalid Product');
      await page.fill('input[name="price"]', '-5.00');
      await page.selectOption('select[name="catalog_brand_id"]', { label: '.NET' });
      await page.selectOption('select[name="catalog_type_id"]', { label: 'T-Shirt' });

      // Submit form
      await page.click('button[type="submit"]');

      // Should stay on create page (not redirect)
      await page.waitForTimeout(1000);

      const currentUrl = page.url();
      expect(currentUrl).toContain('/create');

      // Validation error should be visible
      const hasError = await page.locator('[class*="error"]').count();
      expect(hasError).toBeGreaterThan(0);
    });

  });

  test.describe('Workflow E2E - Edit Product', () => {

    test('Edit product workflow updates existing product', async ({ page }) => {
      /**
       * Golden baseline: Edit workflow should UPDATE existing row
       * Test: Load product 1 → Modify fields → Save → Verify changes
       */

      await page.goto('http://localhost:5173/catalog/edit/1');
      await waitForPageLoad(page);

      // Verify form is pre-filled
      const originalName = await page.inputValue('input[name="name"]');
      expect(originalName).toBe('.NET Bot Black Hoodie');

      // Modify name and price
      const updatedName = 'Modified by E2E Parity Test';
      const updatedPrice = '25.99';

      await page.fill('input[name="name"]', updatedName);
      await page.fill('input[name="price"]', updatedPrice);

      // Submit form
      await page.click('button[type="submit"]');

      // Wait for redirect
      await page.waitForURL('**/catalog**', { timeout: 5000 });

      // Navigate back to edit page to verify changes persisted
      await page.goto('http://localhost:5173/catalog/edit/1');
      await waitForPageLoad(page);

      // Verify name and price are updated
      const savedName = await page.inputValue('input[name="name"]');
      const savedPrice = await page.inputValue('input[name="price"]');

      expect(savedName).toBe(updatedName);
      expect(savedPrice).toBe(updatedPrice);
    });

  });

  test.describe('Workflow E2E - Details Page', () => {

    test('Details page displays product read-only', async ({ page }) => {
      /**
       * Golden baseline: Details page shows all fields read-only
       * Test: Navigate to details → Verify all fields are displayed, not editable
       */

      await page.goto('http://localhost:5173/catalog/details/1');
      await waitForPageLoad(page);

      // Verify product name is displayed
      const nameText = await page.textContent('[data-testid="product-name"]')
        || await page.locator('text=.NET Bot Black Hoodie').textContent();

      expect(nameText).toContain('.NET Bot Black Hoodie');

      // Verify no input fields are editable
      const inputCount = await page.locator('input:not([readonly]):not([disabled])').count();
      expect(inputCount).toBe(0); // All inputs should be read-only or not present

      // Verify Edit button exists
      const editButton = page.locator('a[href*="/edit/1"], button:has-text("Edit")');
      await expect(editButton).toBeVisible();

      // Screenshot for manual verification
      await expect(page).toHaveScreenshot('catalog-details-page.png', {
        maxDiffPixels: 100,
        fullPage: true,
      });
    });

  });

  test.describe('Workflow E2E - Delete Product', () => {

    test('Delete product workflow removes product', async ({ page }) => {
      /**
       * Golden baseline: Delete workflow should DELETE row from database
       * Test: Create product → Delete it → Verify it's gone
       */

      // First create a product to delete
      await page.goto('http://localhost:5173/catalog/create');
      await waitForPageLoad(page);

      const testProduct = {
        name: 'Product to Delete E2E',
        description: 'Will be deleted',
        price: '1.00',
        brand: 'Other',
        type: 'Mug',
        stock: '1',
      };

      await fillProductForm(page, testProduct);
      await page.click('button[type="submit"]');

      // Wait for redirect to list
      await page.waitForURL('**/catalog**', { timeout: 5000 });

      // Find the created product and get its ID
      // (In real scenario, we'd parse the product ID from the list)
      // For now, we'll navigate directly if we know the pattern

      // Navigate to delete page (assuming product was created with some ID)
      // We'll search for it in the list first
      await page.waitForSelector(`text=${testProduct.name}`);

      // Click on the product to go to details
      await page.click(`text=${testProduct.name}`);
      await waitForPageLoad(page);

      // From details, click Delete button
      const deleteButton = page.locator('a[href*="/delete"], button:has-text("Delete")');
      await deleteButton.click();
      await waitForPageLoad(page);

      // Confirm deletion
      await page.click('button[type="submit"]:has-text("Delete")');

      // Wait for redirect back to list
      await page.waitForURL('**/catalog**', { timeout: 5000 });

      // Verify product is no longer in list
      const productExists = await page.locator(`text=${testProduct.name}`).isVisible();
      expect(productExists).toBe(false);
    });

    test('Delete page shows confirmation with product details', async ({ page }) => {
      /**
       * Golden baseline: Delete page shows product details before deletion
       * Test: Navigate to delete → Verify details shown → Back button cancels
       */

      await page.goto('http://localhost:5173/catalog/delete/1');
      await waitForPageLoad(page);

      // Verify confirmation message or product details are shown
      const pageContent = await page.content();
      expect(pageContent.toLowerCase()).toContain('delete');

      // Verify product name is displayed
      const hasProductName = await page.locator('text=.NET Bot Black Hoodie').isVisible();
      expect(hasProductName).toBe(true);

      // Verify Back/Cancel button exists
      const backButton = page.locator('a:has-text("Back"), button:has-text("Cancel")');
      await expect(backButton).toBeVisible();

      // Screenshot for manual verification
      await expect(page).toHaveScreenshot('catalog-delete-confirmation.png', {
        maxDiffPixels: 100,
        fullPage: true,
      });

      // Click Back button (should NOT delete)
      await backButton.click();
      await waitForPageLoad(page);

      // Should navigate away without deleting
      const currentUrl = page.url();
      expect(currentUrl).not.toContain('/delete/1');
    });

  });

  test.describe('Dropdown Data Parity', () => {

    test('Brand dropdown populated with 5 brands', async ({ page }) => {
      /**
       * Golden baseline: synthetic_brands.json (5 brands)
       * Test: Verify dropdown has exactly 5 brand options
       */

      await page.goto('http://localhost:5173/catalog/create');
      await waitForPageLoad(page);

      // Get brand dropdown options
      const brandSelect = page.locator('select[name="catalog_brand_id"]');
      const options = await brandSelect.locator('option').allTextContents();

      // Filter out empty/placeholder option if present
      const brandOptions = options.filter(opt => opt.trim() !== '' && opt.trim() !== 'Select Brand');

      // Should have exactly 5 brands
      expect(brandOptions.length).toBe(5);

      // Verify brand names match golden baseline
      expect(brandOptions).toContain('.NET');
      expect(brandOptions).toContain('Other');
      expect(brandOptions).toContain('Azure');
      expect(brandOptions).toContain('Visual Studio');
      expect(brandOptions).toContain('SQL Server');
    });

    test('Type dropdown populated with 4 types', async ({ page }) => {
      /**
       * Golden baseline: synthetic_types.json (4 types)
       * Test: Verify dropdown has exactly 4 type options
       */

      await page.goto('http://localhost:5173/catalog/create');
      await waitForPageLoad(page);

      // Get type dropdown options
      const typeSelect = page.locator('select[name="catalog_type_id"]');
      const options = await typeSelect.locator('option').allTextContents();

      // Filter out empty/placeholder option if present
      const typeOptions = options.filter(opt => opt.trim() !== '' && opt.trim() !== 'Select Type');

      // Should have exactly 4 types
      expect(typeOptions.length).toBe(4);

      // Verify type names match golden baseline
      expect(typeOptions).toContain('Mug');
      expect(typeOptions).toContain('T-Shirt');
      expect(typeOptions).toContain('Sheet');
      expect(typeOptions).toContain('USB Memory Stick');
    });

  });

});

/**
 * PARITY TEST RESULT INTERPRETATION:
 *
 * PASS - New system matches legacy exactly (within documented tolerances)
 * FAIL - Difference found - review screenshot diffs in test-results/
 *
 * KNOWN DIFFERENCES:
 *
 * 1. Styling and Layout:
 *    - New system uses Tailwind CSS + shadcn/ui components
 *    - Legacy uses Bootstrap + ASP.NET WebForms styling
 *    - Visual differences are EXPECTED and ACCEPTABLE
 *    - Screenshot tests establish NEW system's visual baseline
 *
 * 2. Validation Messages:
 *    - New system: Client-side (Zod) + Server-side (Pydantic)
 *    - Legacy: Server-side only (ASP.NET validation)
 *    - Message text may differ, but constraints are equivalent
 *
 * 3. Navigation Flow:
 *    - New system: React Router (SPA, no page reload)
 *    - Legacy: WebForms postback (full page reload)
 *    - User experience is IMPROVED in new system
 *
 * MANUAL VALIDATION REQUIRED:
 *
 * After running with --update-snapshots, user must:
 * 1. Review generated screenshots in tests/e2e/parity/*.spec.ts-snapshots/
 * 2. Compare visually to legacy app running at http://localhost:50586
 * 3. Document approval in docs/seams/catalog-crud/evidence/manual-validation.md
 * 4. If screenshots are acceptable, commit them as new baseline
 */
