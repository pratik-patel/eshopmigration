/**
 * Screenshot capture for visual parity testing.
 *
 * Captures screenshots of all pages for comparison with legacy.
 */

import { test, expect } from '@playwright/test';

test.describe('Visual Parity Screenshots', () => {
  test('capture catalog list page', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    await page.screenshot({
      path: 'tests/visual/screenshots/catalog-list.png',
      fullPage: true,
    });
  });

  test('capture create page', async ({ page }) => {
    await page.goto('/catalog/create');
    await page.waitForLoadState('networkidle');

    await page.screenshot({
      path: 'tests/visual/screenshots/create-page.png',
      fullPage: true,
    });
  });

  test('capture edit page', async ({ page }) => {
    // Assuming item ID 1 exists
    await page.goto('/catalog/edit/1');
    await page.waitForLoadState('networkidle');

    await page.screenshot({
      path: 'tests/visual/screenshots/edit-page.png',
      fullPage: true,
    });
  });

  test('capture details page', async ({ page }) => {
    await page.goto('/catalog/details/1');
    await page.waitForLoadState('networkidle');

    await page.screenshot({
      path: 'tests/visual/screenshots/details-page.png',
      fullPage: true,
    });
  });

  test('capture delete page', async ({ page }) => {
    await page.goto('/catalog/delete/1');
    await page.waitForLoadState('networkidle');

    await page.screenshot({
      path: 'tests/visual/screenshots/delete-page.png',
      fullPage: true,
    });
  });

  test('capture table with data', async ({ page }) => {
    await page.goto('/');
    await page.waitForSelector('.esh-table', { timeout: 5000 });

    // Zoom in on table
    const table = page.locator('.esh-table');
    await table.screenshot({
      path: 'tests/visual/screenshots/catalog-table.png',
    });
  });

  test('capture pagination', async ({ page }) => {
    await page.goto('/');
    await page.waitForSelector('.esh-pager', { timeout: 5000 }).catch(() => {});

    const pagination = page.locator('.esh-pager');
    const hasPagination = await pagination.count();

    if (hasPagination > 0) {
      await pagination.screenshot({
        path: 'tests/visual/screenshots/pagination.png',
      });
    }
  });

  test('capture form components', async ({ page }) => {
    await page.goto('/catalog/create');
    await page.waitForSelector('form', { timeout: 5000 });

    // Capture form fields
    const form = page.locator('form');
    await form.screenshot({
      path: 'tests/visual/screenshots/catalog-form.png',
    });
  });
});
