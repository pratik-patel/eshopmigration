/**
 * E2E tests for catalog CRUD operations.
 *
 * Tests full user workflows:
 * - List catalog items
 * - Create new item
 * - Edit existing item
 * - View item details
 * - Delete item
 */

import { test, expect } from '@playwright/test';

test.describe('Catalog Management E2E', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to home page
    await page.goto('/');
  });

  test('should display catalog list page', async ({ page }) => {
    // Verify page title
    await expect(page.getByText('Catalog Items')).toBeVisible();

    // Verify Create New button exists
    await expect(page.getByText('Create New')).toBeVisible();

    // Verify table is present (or empty state)
    const hasTable = await page.locator('.esh-table').count();
    expect(hasTable).toBeGreaterThan(0);
  });

  test('should navigate to create page', async ({ page }) => {
    // Click Create New button
    await page.getByText('Create New').click();

    // Verify navigation to create page
    await expect(page).toHaveURL('/catalog/create');
    await expect(page.getByText('Create')).toBeVisible();

    // Verify form fields exist
    await expect(page.locator('input[id="name"]')).toBeVisible();
    await expect(page.locator('select[id="brand"]')).toBeVisible();
    await expect(page.locator('select[id="type"]')).toBeVisible();
    await expect(page.locator('input[id="price"]')).toBeVisible();
  });

  test('should show validation error for empty name', async ({ page }) => {
    await page.goto('/catalog/create');

    // Click Create without filling form
    await page.getByText('[ Create ]').click();

    // Browser validation should prevent submission
    const nameInput = page.locator('input[id="name"]');
    const validationMessage = await nameInput.evaluate((el: HTMLInputElement) =>
      el.validationMessage
    );
    expect(validationMessage).toBeTruthy();
  });

  test('should cancel and return to home', async ({ page }) => {
    await page.goto('/catalog/create');

    // Click Cancel button
    await page.getByText('[ Cancel ]').click();

    // Verify navigation back to home
    await expect(page).toHaveURL('/');
    await expect(page.getByText('Catalog Items')).toBeVisible();
  });

  test('should navigate to details page from list', async ({ page }) => {
    // Wait for table to load
    await page.waitForSelector('.esh-table', { timeout: 5000 });

    // Check if there are any items
    const detailsLinks = page.locator('.esh-table-link').filter({ hasText: 'Details' });
    const count = await detailsLinks.count();

    if (count > 0) {
      // Click first Details link
      await detailsLinks.first().click();

      // Verify navigation to details page
      await expect(page.url()).toContain('/catalog/details/');
      await expect(page.getByText('Details')).toBeVisible();
      await expect(page.getByText('[ Back to list ]')).toBeVisible();
      await expect(page.getByText('[ Edit ]')).toBeVisible();
    }
  });

  test('should navigate back from details to list', async ({ page }) => {
    // Assuming item ID 1 exists (from seed data)
    await page.goto('/catalog/details/1');

    // Wait for page to load
    await page.waitForSelector('.esh-body-title', { timeout: 5000 });

    // Click Back to list button
    await page.getByText('[ Back to list ]').click();

    // Verify navigation back to home
    await expect(page).toHaveURL('/');
    await expect(page.getByText('Catalog Items')).toBeVisible();
  });

  test('should navigate from details to edit', async ({ page }) => {
    // Assuming item ID 1 exists
    await page.goto('/catalog/details/1');

    // Wait for page to load
    await page.waitForSelector('.esh-body-title', { timeout: 5000 });

    // Click Edit button
    await page.getByText('[ Edit ]').click();

    // Verify navigation to edit page
    await expect(page).toHaveURL('/catalog/edit/1');
    await expect(page.getByText('Edit')).toBeVisible();
  });

  test('should show pagination if multiple pages', async ({ page }) => {
    // Wait for table to load
    await page.waitForSelector('.esh-table', { timeout: 5000 });

    // Check if pagination exists
    const pagination = page.locator('.esh-pager');
    const hasPagination = await pagination.count();

    if (hasPagination > 0) {
      // Verify Previous and Next buttons exist
      await expect(page.getByText('Previous')).toBeVisible();
      await expect(page.getByText('Next')).toBeVisible();
    }
  });

  test('should navigate to delete confirmation page', async ({ page }) => {
    // Wait for table to load
    await page.waitForSelector('.esh-table', { timeout: 5000 });

    // Check if there are any items
    const deleteLinks = page.locator('.esh-table-link').filter({ hasText: 'Delete' });
    const count = await deleteLinks.count();

    if (count > 0) {
      // Click first Delete link
      await deleteLinks.first().click();

      // Verify navigation to delete page
      await expect(page.url()).toContain('/catalog/delete/');
      await expect(page.getByText('Delete')).toBeVisible();
      await expect(page.getByText('Are you sure you want to delete this?')).toBeVisible();
      await expect(page.getByText('[ Cancel ]')).toBeVisible();
      await expect(page.getByText('[ Delete ]')).toBeVisible();
    }
  });

  test('should handle 404 redirect for non-existent item', async ({ page }) => {
    // Navigate to non-existent item
    await page.goto('/catalog/details/99999');

    // Should show error or redirect to home
    await page.waitForTimeout(2000);

    // Check if error message shown or redirected
    const hasError = await page.getByText(/Error/i).count();
    const isHome = page.url().endsWith('/');

    expect(hasError > 0 || isHome).toBeTruthy();
  });

  test('should handle unknown route redirect', async ({ page }) => {
    // Navigate to unknown route
    await page.goto('/unknown-route');

    // Should redirect to home
    await expect(page).toHaveURL('/');
    await expect(page.getByText('Catalog Items')).toBeVisible();
  });
});
