# Catalog CRUD E2E Parity Tests

This directory contains end-to-end Playwright tests for the `catalog-crud` seam, verifying that the new React frontend produces the same user experience and visual appearance as the legacy ASP.NET WebForms application.

## Test File

**File:** `catalog_crud_parity.spec.ts`

Contains visual regression tests and workflow E2E tests.

---

## Test Suites

### Visual Regression - Create Form

**Tests:**
- `Create form layout matches golden baseline` - Screenshot comparison
- `Create form shows validation errors correctly` - Validation error display

**Golden Baseline:** `legacy-golden/screenshots/screen_001_depth1.png`

**Strategy:**
- First run with `--update-snapshots` to establish new system's visual baseline
- Subsequent runs compare against the new baseline
- Manual user validation required to approve initial baseline

---

### Visual Regression - Edit Form

**Tests:**
- `Edit form layout matches golden baseline` - Screenshot comparison with product ID 1
- `Edit form picture field is read-only` - Verify picture filename cannot be edited

**Golden Baseline:** `legacy-golden/screenshots/screen_003_depth1.png`

**Strategy:**
- Verifies 2-column layout with product image on left
- Verifies picture_file_name field is read-only (per ui-behavior.md)

---

### Workflow E2E - Create Product

**Tests:**
- `Create product workflow produces correct result` - Full create workflow
- `Create product with validation error stays on form` - Error handling

**Verification:**
- Fill form with valid data
- Submit form
- Verify redirect to catalog list
- Verify new product appears in list

---

### Workflow E2E - Edit Product

**Tests:**
- `Edit product workflow updates existing product` - Full edit workflow

**Verification:**
- Load product ID 1
- Verify form pre-filled with existing data
- Modify name and price
- Submit form
- Verify changes persisted

---

### Workflow E2E - Details Page

**Tests:**
- `Details page displays product read-only` - Verify read-only display

**Verification:**
- Load product ID 1 details
- Verify all fields displayed (not editable)
- Verify Edit button exists
- Screenshot for manual validation

---

### Workflow E2E - Delete Product

**Tests:**
- `Delete product workflow removes product` - Full delete workflow
- `Delete page shows confirmation with product details` - Confirmation UI

**Verification:**
- Create product
- Navigate to delete page
- Verify confirmation message
- Click Delete
- Verify product removed from list
- Test Cancel button (should NOT delete)

---

### Dropdown Data Parity

**Tests:**
- `Brand dropdown populated with 5 brands` - Verify dropdown options
- `Type dropdown populated with 4 types` - Verify dropdown options

**Golden Baselines:**
- `synthetic_brands.json` - 5 brands (.NET, Other, Azure, Visual Studio, SQL Server)
- `synthetic_types.json` - 4 types (Mug, T-Shirt, Sheet, USB Memory Stick)

---

## Running Tests

### First Run - Establish Visual Baseline

**IMPORTANT:** The first run must use `--update-snapshots` to create the new system's visual baseline.

```bash
cd frontend
npx playwright test tests/e2e/parity/catalog_crud_parity.spec.ts --update-snapshots
```

This will:
1. Run all tests
2. Capture screenshots of the NEW system
3. Save them as baseline snapshots in `tests/e2e/parity/catalog_crud_parity.spec.ts-snapshots/`

**Manual Validation Required:**
After running with `--update-snapshots`, you MUST:
1. Review generated screenshots in the snapshots directory
2. Compare visually to legacy app at `http://localhost:50586/Catalog/Create`
3. If appearance is acceptable, commit the snapshots as the new baseline
4. Document approval in `docs/seams/catalog-crud/evidence/manual-validation.md`

---

### Subsequent Runs - Regression Detection

After establishing the baseline, run without `--update-snapshots`:

```bash
cd frontend
npx playwright test tests/e2e/parity/catalog_crud_parity.spec.ts
```

This will:
1. Run all tests
2. Compare screenshots to the established baseline
3. FAIL if visual differences exceed `maxDiffPixels` threshold
4. Generate a diff image showing what changed

---

### Run Specific Test

```bash
# Just visual regression tests
npx playwright test tests/e2e/parity/catalog_crud_parity.spec.ts -g "Visual Regression"

# Just workflow tests
npx playwright test tests/e2e/parity/catalog_crud_parity.spec.ts -g "Workflow E2E"

# Just one test
npx playwright test tests/e2e/parity/catalog_crud_parity.spec.ts -g "Create form layout"
```

---

### Debug Mode

Run with headed browser to see what's happening:

```bash
npx playwright test tests/e2e/parity/catalog_crud_parity.spec.ts --headed --workers=1
```

---

### UI Mode (Interactive)

Run with Playwright UI for debugging:

```bash
npx playwright test tests/e2e/parity/catalog_crud_parity.spec.ts --ui
```

---

## Test Result Interpretation

### PASS ✅

The new system's visual appearance and behavior match the established baseline (within `maxDiffPixels` tolerance).

**What This Means:**
- Screenshots match (allowing for minor font rendering differences)
- Workflows complete successfully
- Navigation flow is correct
- Validation behavior is correct

---

### FAIL ❌ - Visual Regression

A screenshot does not match the baseline.

**What To Do:**

1. **Check the diff image:**
   ```bash
   # Playwright generates diff images in:
   test-results/catalog-crud-parity-*-failed-*.png
   ```

2. **Determine if the difference is acceptable:**
   - Minor font rendering difference? → ACCEPTABLE, update baseline
   - Wrong layout? → FIX the code
   - Missing field? → FIX the code
   - Intentional design change? → UPDATE baseline and DOCUMENT

3. **If acceptable, update baseline:**
   ```bash
   npx playwright test tests/e2e/parity/catalog_crud_parity.spec.ts --update-snapshots
   ```

4. **If not acceptable, fix the code and re-run.**

---

### FAIL ❌ - Workflow Error

A workflow test failed (e.g., product not found after creation).

**What To Do:**

1. **Check the error message:**
   - API error? Check backend logs
   - Navigation error? Check React Router configuration
   - Selector not found? Check if frontend HTML structure changed

2. **Debug with headed browser:**
   ```bash
   npx playwright test tests/e2e/parity/catalog_crud_parity.spec.ts -g "failing test name" --headed
   ```

3. **Check Playwright trace:**
   ```bash
   npx playwright show-trace test-results/.../trace.zip
   ```

---

## Known Differences (Acceptable)

### 1. Styling and Visual Design

**Difference:**
- Legacy: Bootstrap 3.x styling + ASP.NET WebForms default theme
- New: Tailwind CSS + shadcn/ui components

**Impact:** High visual difference, but functionally equivalent

**Acceptance Criteria:**
- All fields are present and labeled correctly
- Layout is clear and usable
- Form validation is visible
- Buttons are clearly identified

**Manual Validation Required:** User must approve that new design is acceptable replacement for legacy design.

---

### 2. Navigation Flow

**Difference:**
- Legacy: Full page reload on form submission (WebForms postback)
- New: SPA navigation with React Router (no page reload)

**Impact:** Smoother UX in new system (IMPROVEMENT)

**Acceptance Criteria:**
- After Create/Edit/Delete, user is redirected to appropriate page
- Back button works correctly
- No unexpected page reloads

---

### 3. Validation Error Display

**Difference:**
- Legacy: Server-side validation only, errors shown after postback
- New: Client-side validation (Zod) + server-side (Pydantic), immediate feedback

**Impact:** Better UX in new system (IMPROVEMENT)

**Acceptance Criteria:**
- All validation rules are enforced
- Error messages are clear and visible
- User knows which fields have errors

---

### 4. Image Display

**Difference:**
- Legacy: Product images stored in `/pics` directory
- New: Images may be served differently (CDN, different path, etc.)

**Impact:** Visual difference acceptable if images are displayed correctly

**Acceptance Criteria:**
- Product images are visible on Edit/Details/Delete pages
- Image sizing is reasonable
- Broken image icon does NOT appear (if image missing, show placeholder)

---

## Screenshot Baseline Strategy

### Why We Use Screenshots

Screenshots serve as a **visual regression test** to catch unintended UI changes. They answer the question: "Does the page LOOK right?"

### What Screenshots DON'T Catch

- Functional bugs (e.g., button doesn't work) → Use workflow E2E tests
- Data accuracy (e.g., wrong product name) → Use backend parity tests
- Performance issues → Use separate performance tests

### When to Update Screenshots

**Update the baseline when:**
1. Intentional design change approved by stakeholders
2. New feature added to the page
3. Bug fix that changes appearance
4. Framework/library upgrade that changes rendering

**DO NOT update the baseline to "make the test pass" without understanding WHY it changed.**

---

## maxDiffPixels Tolerance

Tests use `maxDiffPixels: 50` to `maxDiffPixels: 100` as tolerance.

**Why?**
- Font rendering differs between browsers and OS
- Anti-aliasing can cause pixel-level differences
- Subpixel positioning may vary

**What value means:**
- `maxDiffPixels: 50` → Allow up to 50 pixels to differ
- For a 1920x1080 screenshot (2,073,600 pixels), 50 pixels = 0.0024% difference

**If test fails despite looking identical:**
- Increase `maxDiffPixels` slightly (e.g., from 50 to 100)
- Document why in a comment
- Consider using `maxDiffPixelRatio` instead (percentage-based)

---

## Prerequisites

### Backend Must Be Running

Tests make real HTTP requests to `http://localhost:5173` (frontend) which calls `http://localhost:8000` (backend API).

**Start backend:**
```bash
cd backend
uvicorn app.main:app --reload
```

**Start frontend:**
```bash
cd frontend
npm run dev
```

### Database Must Be Seeded

Tests expect product ID 1, brands, and types to exist.

**Seed database:**
```bash
cd backend
python -m app.core.seed
```

### Playwright Must Be Installed

```bash
cd frontend
npm install
npx playwright install
```

---

## Troubleshooting

### Error: "page.goto: net::ERR_CONNECTION_REFUSED"

**Cause:** Frontend dev server is not running

**Fix:**
```bash
cd frontend
npm run dev
```

Verify it's running at `http://localhost:5173`

---

### Error: "Selector not found"

**Cause:** Frontend HTML structure doesn't match test expectations

**Fix:**
1. Inspect the page in browser dev tools
2. Update the selector in the test to match actual HTML
3. Add `data-testid` attributes to frontend components for stable selectors

**Example:**
```tsx
// In React component
<input data-testid="product-name" name="name" />
```

```typescript
// In test
await page.fill('[data-testid="product-name"]', 'Test Product');
```

---

### Error: "Screenshot comparison failed"

**Cause:** Visual difference detected

**Fix:**
1. View the diff image in `test-results/`
2. Determine if difference is acceptable
3. If acceptable: `--update-snapshots`
4. If not acceptable: fix the frontend code

---

### Error: "Product not found after creation"

**Cause:** API call failed or navigation incorrect

**Fix:**
1. Check backend logs for API errors
2. Verify network requests in Playwright trace
3. Ensure backend is running and healthy
4. Check if product was actually created in database

---

## Manual Validation Checklist

After running tests with `--update-snapshots`, manually validate:

### Create Page
- [ ] Form layout is clear and usable
- [ ] All fields are labeled correctly
- [ ] Brand dropdown shows 5 options
- [ ] Type dropdown shows 4 options
- [ ] Create button is visible
- [ ] Back to List link works

### Edit Page
- [ ] Form pre-fills with product data
- [ ] Product image displays on left (or appropriate position)
- [ ] Picture filename field is read-only/disabled
- [ ] All fields are editable except picture filename
- [ ] Save button is visible
- [ ] Cancel/Back link works

### Details Page
- [ ] All product fields are displayed
- [ ] Product image displays
- [ ] No fields are editable
- [ ] Edit button navigates to Edit page
- [ ] Back to List link works

### Delete Page
- [ ] Confirmation message is clear
- [ ] Product details are shown
- [ ] Delete button is clearly marked
- [ ] Cancel/Back button is available
- [ ] Cancel does NOT delete the product

### Validation Errors
- [ ] Empty name shows error
- [ ] Negative price shows error
- [ ] Invalid stock value shows error
- [ ] Error messages are visible and clear
- [ ] Form does not submit with validation errors

---

## Next Steps After Tests Pass

1. Document manual validation results in `docs/seams/catalog-crud/evidence/manual-validation.md`
2. Commit screenshot baselines to version control
3. Update seam tracker: Mark `catalog-crud` as "E2E TESTS PASSING"
4. Proceed to user acceptance testing (UAT)

---

## Contact

For questions about E2E test strategy or Playwright usage:
- [Playwright Documentation](https://playwright.dev/docs/intro)
- `docs/seams/catalog-crud/spec.md` - Seam specification
- `legacy-golden/catalog-crud/BASELINE_INDEX.md` - Baseline capture details
