# Frontend E2E Parity Tests for catalog-list

This directory contains Playwright E2E tests that compare the new React frontend to the legacy ASP.NET WebForms UI.

## Purpose

These tests validate that the migrated frontend:
1. **Renders the same data** as the legacy system
2. **Matches the visual layout** (via screenshot comparison)
3. **Provides the same interactive behavior** (navigation, actions)

## Golden Baseline

**Visual Baseline**: `legacy-golden/screenshots/screen_000_depth0.png`
- Captured from legacy app at `http://localhost:50586/`
- Shows Default.aspx with 10 products displayed

**Data Baseline**: `legacy-golden/grid-data.json`
- Contains table data extracted from legacy HTML
- 10 products with all field values

## Test File

### `catalog-list-parity.spec.ts`

**Test Suites**:

1. **Catalog List Page - Parity Tests**
   - Visual regression (screenshot comparison)
   - Table structure validation
   - Product data rendering
   - Product order preservation
   - Action links presence
   - Create New button
   - Pagination controls
   - Product images
   - Price formatting
   - Loading state
   - Error handling

2. **Catalog List Page - Data Validation**
   - Deep validation of first 3 products
   - Exact field value matching

3. **Catalog List Page - Interactive Elements**
   - Edit link navigation
   - Details link navigation
   - Delete link navigation

## Setup

### Install Playwright

```bash
npm install -D @playwright/test
npx playwright install
```

This installs Playwright and browser binaries (Chromium, Firefox, WebKit).

### Update package.json

Add test scripts:

```json
{
  "scripts": {
    "test:e2e": "playwright test",
    "test:e2e:ui": "playwright test --ui",
    "test:e2e:debug": "playwright test --debug"
  }
}
```

## Running Tests

### Prerequisites

1. **Backend server running**: `cd backend && uvicorn app.main:app --reload`
2. **Database seeded**: `python -m app.core.seed`
3. **Frontend dev server running**: `npm run dev` (or Playwright will start it)

### First Run: Establish Visual Baseline

On the first run, you must establish the **new system's visual baseline**:

```bash
npx playwright test tests/e2e/parity/catalog-list-parity.spec.ts --update-snapshots
```

This creates: `tests/e2e/parity/catalog-list-parity.spec.ts-snapshots/catalog-list-page-chromium.png`

**Important**: This is the NEW system's baseline, not the legacy system's screenshot.

### Subsequent Runs: Detect Regressions

After establishing the baseline, run normally:

```bash
npx playwright test tests/e2e/parity/catalog-list-parity.spec.ts
```

This compares against the baseline and detects visual regressions.

### Run All Parity Tests

```bash
npx playwright test tests/e2e/parity/
```

### Run with UI Mode (Interactive)

```bash
npx playwright test tests/e2e/parity/catalog-list-parity.spec.ts --ui
```

This opens Playwright's interactive UI for debugging.

### Run in Debug Mode

```bash
npx playwright test tests/e2e/parity/catalog-list-parity.spec.ts --debug
```

This opens the Playwright Inspector for step-by-step debugging.

## Test Results

### Expected Results

#### PASS Scenario

```
Running 14 tests using 1 worker

✓ Catalog List Page - Parity Tests › visual regression - page layout matches legacy (1.2s)
✓ Catalog List Page - Parity Tests › table structure matches legacy (0.5s)
✓ Catalog List Page - Parity Tests › all products from golden baseline are rendered (0.8s)
✓ Catalog List Page - Parity Tests › product order matches golden baseline (0.6s)
✓ Catalog List Page - Parity Tests › action links present for each product (0.7s)
...

14 passed (12.3s)
```

**Interpretation**: Frontend matches legacy behavior exactly.

#### FAIL Scenario: Visual Regression

```
✗ Catalog List Page - Parity Tests › visual regression - page layout matches legacy (1.5s)

Error: Screenshot comparison failed:
  Expected: catalog-list-page-chromium.png
  Actual:   catalog-list-page-chromium-actual.png
  Diff:     catalog-list-page-chromium-diff.png

  152 pixels differ (0.05% difference)
```

**Interpretation**: Visual layout changed. Check diff image to see what changed.

#### FAIL Scenario: Data Mismatch

```
✗ Catalog List Page - Parity Tests › all products from golden baseline are rendered (0.8s)

Error: expect(locator).toContainText(expected)

Expected string: ".NET Bot Black Hoodie"
Received string: ".NET Bot Black Hoodie V2"
```

**Interpretation**: Product data differs from golden baseline. Check backend API or seed data.

## Visual Regression Testing

### How It Works

1. **First Run**: `--update-snapshots` captures the new system's current state as baseline
2. **Subsequent Runs**: Playwright compares current render to baseline pixel-by-pixel
3. **Tolerance**: Tests allow up to 50 pixel differences (configurable via `maxDiffPixels`)

### Manual Validation Required

**Critical**: The automated visual regression test does NOT compare to the legacy screenshot directly.

You must manually compare:
- **Legacy**: `legacy-golden/screenshots/screen_000_depth0.png`
- **New Baseline**: `tests/e2e/parity/catalog-list-parity.spec.ts-snapshots/catalog-list-page-chromium.png`

Open both images side-by-side and verify:
- Table layout matches
- Column widths similar
- Font sizes reasonable
- Colors match brand guidelines
- Spacing consistent

Document results in: `docs/seams/catalog-list/evidence/manual-validation.md`

### Updating Visual Baseline

If you intentionally change the UI (e.g., design improvement), update the baseline:

```bash
npx playwright test tests/e2e/parity/catalog-list-parity.spec.ts --update-snapshots
```

**Warning**: Only update snapshots for intentional changes, not to hide bugs.

## Interactive Tests

### Navigation Tests

These tests verify that clicking action links navigates correctly:

- **Edit**: Click Edit → Should navigate to `/catalog/edit/{id}`
- **Details**: Click Details → Should navigate to `/catalog/details/{id}`
- **Delete**: Click Delete → Should navigate to `/catalog/delete/{id}`

### Loading and Error States

- **Loading State**: Uses route interception to delay API response and verify loading UI
- **Error State**: Mocks API failure to verify error message display

## Troubleshooting

### Test fails with "page.goto: net::ERR_CONNECTION_REFUSED"

**Cause**: Frontend dev server not running

**Fix**:
```bash
# Start dev server
npm run dev
```

Or let Playwright start it automatically (configured in `playwright.config.ts`).

### Test fails with "timeout 30000ms exceeded"

**Cause**: Page takes too long to load or element not found

**Fix**:
- Check backend API is responding
- Verify database is seeded
- Increase timeout in test: `await page.waitForSelector('table', { timeout: 60000 })`

### Visual regression test always fails

**Cause**: Minor rendering differences (fonts, anti-aliasing, screen resolution)

**Fix**:
- Increase `maxDiffPixels` tolerance
- Run tests in consistent environment (CI uses same OS/browser)
- Use `animations: 'disabled'` to prevent animation-related differences

### Test passes but UI looks wrong

**Cause**: Test may be checking wrong elements or baseline is incorrect

**Fix**:
- Open Playwright UI mode to inspect: `--ui`
- Use Playwright trace viewer: `npx playwright show-trace trace.zip`
- Manually validate against legacy screenshot

## CI Integration

### GitHub Actions Example

```yaml
name: E2E Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 18
      - name: Install dependencies
        run: |
          cd frontend
          npm ci
          npx playwright install --with-deps
      - name: Run backend
        run: |
          cd backend
          pip install -r requirements.txt
          python -m app.core.seed
          uvicorn app.main:app --host 0.0.0.0 --port 8000 &
      - name: Run E2E tests
        run: |
          cd frontend
          npx playwright test tests/e2e/parity/
      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report
          path: frontend/playwright-report/
```

## Exclusions and Limitations

### What These Tests Do NOT Validate

1. **Backend business logic**: That's covered by backend parity tests
2. **Performance**: Response time, load testing (separate suite)
3. **Accessibility**: WCAG compliance (separate suite using axe-core)
4. **Mobile responsive**: Tests run on desktop viewport only (add mobile projects if needed)

### Known Differences from Legacy

Document any intentional differences here:

- **None yet** - Frontend should match legacy exactly for initial migration

## Maintenance

### When to Update Tests

- **New products added**: Update expected product count
- **UI redesign**: Update visual baseline with `--update-snapshots`
- **Route changes**: Update navigation assertions
- **New golden baseline captured**: Tests will automatically use new data

### When NOT to Update Tests

- **Backend refactoring**: If frontend output is identical, tests should still pass
- **CSS framework changes**: If visual result is same, no update needed
- **Performance optimizations**: Parity tests check correctness, not speed

## Related Documentation

- **Backend parity tests**: `backend/tests/parity/README.md`
- **Golden baseline capture**: `docs/seams/catalog-list/evidence-capture.md`
- **API contract**: `docs/seams/catalog-list/contracts/openapi.yaml`
- **Manual validation checklist**: `docs/SYNTHETIC_BASELINE_STRATEGY.md`

## Success Criteria

**Seam is complete** when:
- ✅ All E2E parity tests pass
- ✅ Backend parity tests pass
- ✅ Visual baseline manually validated against legacy screenshot
- ✅ Manual validation documented in evidence.md
