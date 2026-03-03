# Parity Tests Summary - catalog-list Seam

**Generated**: 2026-03-02
**Seam**: catalog-list
**Status**: Tests Generated, Ready for Execution

## Overview

Comprehensive parity tests have been generated to compare the new Python + React implementation against the legacy ASP.NET WebForms application.

## Generated Test Files

### Backend Parity Tests (Python/pytest)

#### 1. `backend/tests/parity/test_catalog_list_api_parity.py`

**Purpose**: Compare API responses to golden baseline

**Test Coverage**:
- ✅ Row count validation (10 products)
- ✅ Pagination metadata calculations
- ✅ Product field structure validation
- ✅ Product data matches golden baseline exactly
- ✅ Product order preservation
- ✅ Default parameters behavior
- ✅ Edge case handling (empty catalog, pagination beyond data)
- ✅ Price precision validation (2 decimal places)
- ✅ API validation rules (page_size, page_index constraints)

**Test Count**: 10 test methods

**Comparison Method**:
- Loads `legacy-golden/grid-data.json`
- Extracts expected product data from HTML table rows
- Compares field-by-field with API response
- Uses Decimal type for price comparison (avoids floating-point issues)

**Exclusions** (documented in test):
- `id`: Auto-generated primary key
- `catalog_type_id`: Foreign key (not in baseline)
- `catalog_brand_id`: Foreign key (not in baseline)
- `picture_uri`: Legacy field (always null)
- `on_reorder`: Calculated field (not in baseline)

#### 2. `backend/tests/parity/test_catalog_list_data_validation.py`

**Purpose**: Deep validation of individual products

**Test Coverage**:
- ✅ Individual validation for each of 10 products
- ✅ Brand and type navigation properties
- ✅ Brand distribution matches baseline (.NET: 5, Other: 5)
- ✅ Type distribution matches baseline (T-Shirt: 6, Mug: 2, Sheet: 2)
- ✅ Comprehensive all-products validation

**Test Count**: 13 test methods

**Validation Strategy**: Each product validated individually by name, allowing precise failure reporting

#### 3. `backend/tests/parity/conftest.py`

**Purpose**: Shared pytest fixtures for parity tests

**Fixtures**:
- `async_client`: AsyncClient for FastAPI app
- Enables async test execution with httpx

### Frontend E2E Tests (Playwright/TypeScript)

#### 4. `frontend/tests/e2e/parity/catalog-list-parity.spec.ts`

**Purpose**: Visual regression and interactive behavior testing

**Test Coverage**:

**Suite 1: Parity Tests**
- ✅ Visual regression (screenshot comparison)
- ✅ Table structure matches legacy
- ✅ All products from golden baseline rendered
- ✅ Product order preserved
- ✅ Action links present (Edit | Details | Delete)
- ✅ Create New button visible
- ✅ Pagination controls (conditional rendering)
- ✅ Product images loaded
- ✅ Prices formatted correctly ($XX.XX)
- ✅ Loading state shown
- ✅ Error state handled gracefully

**Suite 2: Data Validation**
- ✅ Deep validation of first 3 products
- ✅ Exact field values match golden baseline

**Suite 3: Interactive Elements**
- ✅ Edit link navigation
- ✅ Details link navigation
- ✅ Delete link navigation

**Test Count**: 14 test scenarios

**Comparison Method**:
- Loads `legacy-golden/grid-data.json` directly in TypeScript
- Uses Playwright's `toHaveScreenshot()` for visual regression
- Validates rendered text content matches expected values
- Tests navigation and interactive behavior

### Supporting Files

#### 5. `backend/tests/parity/README.md`

Comprehensive documentation covering:
- Test purpose and strategy
- Golden baseline description
- How to run tests
- How to interpret results
- Troubleshooting guide
- Maintenance guidelines

#### 6. `frontend/tests/e2e/parity/README.md`

Comprehensive documentation covering:
- E2E test setup and configuration
- Visual regression testing strategy
- Manual validation requirements
- How to establish baselines
- Troubleshooting common issues
- CI integration examples

#### 7. `frontend/playwright.config.ts`

Playwright configuration:
- Test directory: `./tests/e2e`
- Base URL: `http://localhost:5173`
- Browser: Chromium (Firefox/WebKit commented out)
- Auto-start dev server
- Screenshot/video on failure
- Trace on retry

## Golden Baseline Sources

### Real Capture (Browser Agent)

**File**: `legacy-golden/grid-data.json`
- ✅ **Real data** captured from running legacy app
- Source URL: `http://localhost:50586/`
- Capture date: 2026-03-02 22:40:57
- Contains: 10 products with all field values
- Format: JSON array of table data

**File**: `legacy-golden/screenshots/screen_000_depth0.png`
- ✅ **Real screenshot** of legacy Default.aspx
- Shows: Home page with catalog table
- Contains: All visual layout information

### Synthetic Baseline (Fallback)

**File**: `legacy-golden/catalog-list/BASELINE_INDEX.md`
- ⚠️ Synthetic baseline documentation
- Notes that real capture is available in parent directory
- Describes capture strategy and limitations

## Test Execution

### Backend Tests

```bash
# Install dependencies (if not already done)
cd backend
poetry install

# Run all catalog-list parity tests
poetry run pytest tests/parity/test_catalog_list_* -v

# Run specific test file
poetry run pytest tests/parity/test_catalog_list_api_parity.py -v

# Run with coverage
poetry run pytest tests/parity/test_catalog_list_* -v --cov=app.catalog --cov-report=html
```

### Frontend Tests

```bash
# Install Playwright (first time only)
cd frontend
npm install -D @playwright/test
npx playwright install

# Establish visual baseline (first run)
npx playwright test tests/e2e/parity/catalog-list-parity.spec.ts --update-snapshots

# Run parity tests
npx playwright test tests/e2e/parity/catalog-list-parity.spec.ts

# Run with UI (interactive mode)
npx playwright test tests/e2e/parity/catalog-list-parity.spec.ts --ui

# Run in debug mode
npx playwright test tests/e2e/parity/catalog-list-parity.spec.ts --debug
```

## Expected Test Results

### All Pass Scenario

When implementation is correct, all tests should pass:

**Backend**:
```
tests/parity/test_catalog_list_api_parity.py::TestCatalogListAPIParity::test_first_page_row_count PASSED
tests/parity/test_catalog_list_api_parity.py::TestCatalogListAPIParity::test_pagination_metadata PASSED
tests/parity/test_catalog_list_api_parity.py::TestCatalogListAPIParity::test_product_field_structure PASSED
tests/parity/test_catalog_list_api_parity.py::TestCatalogListAPIParity::test_product_data_matches_golden_baseline PASSED
...
23 passed in 2.34s
```

**Frontend**:
```
Running 14 tests using 1 worker

✓ Catalog List Page - Parity Tests › visual regression - page layout matches legacy
✓ Catalog List Page - Parity Tests › table structure matches legacy
✓ Catalog List Page - Parity Tests › all products from golden baseline are rendered
...
14 passed (8.5s)
```

### Failure Scenarios

#### Data Mismatch

```
FAILED tests/parity/test_catalog_list_api_parity.py::TestCatalogListAPIParity::test_product_data_matches_golden_baseline
AssertionError: Product 0: price mismatch - expected Decimal('19.5'), got Decimal('19.49')
```

**Root Cause**: Price calculation or rounding error in service layer

#### Missing Products

```
FAILED tests/parity/test_catalog_list_api_parity.py::TestCatalogListAPIParity::test_first_page_row_count
AssertionError: Expected 10 products, got 9
```

**Root Cause**: Database seed incomplete or query filtering issue

#### Visual Regression

```
✗ Catalog List Page - Parity Tests › visual regression - page layout matches legacy
Error: Screenshot comparison failed: 152 pixels differ (0.05% difference)
```

**Root Cause**: CSS change or layout shift (check diff image)

## Test Type Mapping

Follows the parity test harness rules:

| Baseline Artifact | Test Type | Test File | Comparison Method |
|-------------------|-----------|-----------|-------------------|
| `grid-data.json` (CSV-like data) | API data parity | `test_catalog_list_api_parity.py` | Field-by-field JSON comparison |
| `grid-data.json` (product data) | Data validation | `test_catalog_list_data_validation.py` | Individual product validation |
| `screen_000_depth0.png` | Visual regression | `catalog-list-parity.spec.ts` | `toHaveScreenshot()` with tolerance |
| N/A (read-only workflow) | DB state parity | Not applicable | No DB writes in this seam |
| Navigation behavior | Workflow E2E | `catalog-list-parity.spec.ts` | Interactive element testing |

## Test Quality Assertions

✅ **No trivial passes**: All tests compare actual data, not just `assert True`

✅ **No hard-coded values**: All expected values loaded from golden baseline files

✅ **Exclusions documented**: Every excluded field (id, timestamps) documented with comments

✅ **No baseline modification**: Tests read baselines, never write to them

✅ **Meaningful failures**: Each assertion provides context (product index, field name, expected vs actual)

## Prerequisites for Running Tests

### Backend Tests

1. ✅ Backend server running: `uvicorn app.main:app --reload`
2. ✅ Database seeded: `python -m app.core.seed`
3. ✅ Poetry dependencies installed: `poetry install`
4. ✅ Golden baseline exists: `legacy-golden/grid-data.json`

### Frontend Tests

1. ✅ Backend API running (frontend depends on it)
2. ✅ Frontend dev server: `npm run dev` (or auto-start via Playwright)
3. ✅ Playwright installed: `npx playwright install`
4. ✅ Golden baseline exists: `legacy-golden/grid-data.json`
5. ⚠️ Visual baseline established: `--update-snapshots` (first run only)

## Manual Validation Required

Even with all automated tests passing, manual validation is required:

### Visual Comparison

User must compare:
- **Legacy**: `legacy-golden/screenshots/screen_000_depth0.png`
- **New Baseline**: `frontend/tests/e2e/parity/catalog-list-parity.spec.ts-snapshots/catalog-list-page-chromium.png`

**Checklist**:
- [ ] Table layout matches
- [ ] Column widths reasonable
- [ ] Font sizes similar
- [ ] Colors match brand guidelines
- [ ] Image thumbnails display correctly
- [ ] Action links formatted correctly
- [ ] Pagination text matches format

**Document results**: `docs/seams/catalog-list/evidence/manual-validation.md`

## Success Criteria

Seam catalog-list is complete when:

- ✅ All backend parity tests pass
- ✅ All frontend E2E parity tests pass
- ✅ Visual baseline manually validated and approved
- ✅ Manual validation documented
- ✅ Evidence gate satisfied (evidence.md created)

## Known Limitations

### Backend Tests

**Cannot validate**:
- Visual styling (CSS, layout)
- Browser rendering differences
- User interaction timing
- Real-time updates (covered by integration tests)

### Frontend Tests

**Cannot validate directly**:
- Backend business logic correctness
- Database transaction integrity
- API performance under load

### Visual Regression

**Cannot validate automatically**:
- Exact match to legacy (different tech stack)
- Font rendering differences (browser/OS)
- Minor anti-aliasing differences

**Mitigation**: Manual validation required for initial baseline approval

## Next Steps

1. **Install dependencies**:
   ```bash
   cd backend && poetry install
   cd ../frontend && npm install && npm install -D @playwright/test && npx playwright install
   ```

2. **Seed database**:
   ```bash
   cd backend && poetry run python -m app.core.seed
   ```

3. **Run backend parity tests**:
   ```bash
   cd backend && poetry run pytest tests/parity/test_catalog_list_* -v
   ```

4. **Establish frontend baseline**:
   ```bash
   cd frontend && npx playwright test tests/e2e/parity/catalog-list-parity.spec.ts --update-snapshots
   ```

5. **Run frontend parity tests**:
   ```bash
   cd frontend && npx playwright test tests/e2e/parity/catalog-list-parity.spec.ts
   ```

6. **Manual validation**:
   - Compare screenshots visually
   - Document results in evidence/manual-validation.md

7. **Create evidence document**:
   - Consolidate test results
   - Add screenshots of test runs
   - Create `docs/seams/catalog-list/evidence/evidence.md`

## File Locations

### Generated Test Files

```
backend/tests/parity/
├── conftest.py                              # NEW - Pytest fixtures
├── test_catalog_list_api_parity.py          # NEW - API response parity (10 tests)
├── test_catalog_list_data_validation.py     # NEW - Individual product validation (13 tests)
└── README.md                                # NEW - Backend parity test documentation

frontend/tests/e2e/parity/
├── catalog-list-parity.spec.ts              # NEW - E2E parity tests (14 tests)
└── README.md                                # NEW - Frontend E2E test documentation

frontend/
└── playwright.config.ts                     # NEW - Playwright configuration
```

### Golden Baselines (Already Exist)

```
legacy-golden/
├── BASELINE_INDEX.md                        # Real browser-agent capture manifest
├── grid-data.json                           # Real catalog data (10 products)
├── screenshots/
│   └── screen_000_depth0.png                # Real screenshot of Default.aspx
└── catalog-list/
    └── BASELINE_INDEX.md                    # Synthetic baseline fallback notes
```

### Documentation

```
docs/seams/catalog-list/
└── PARITY_TESTS_SUMMARY.md                  # NEW - This file
```

## Test Statistics

- **Total test files**: 3 (2 backend, 1 frontend)
- **Total test scenarios**: 37 (23 backend, 14 frontend)
- **Golden baselines used**: 2 (grid-data.json, screen_000_depth0.png)
- **Lines of test code**: ~800 lines
- **Documentation pages**: 3 (2 READMEs + this summary)

## Maintenance

### When to Update Tests

- Database schema changes → Update field assertions
- Business rule changes → Update validation logic
- New golden baseline captured → Tests use new data automatically
- Intentional UI changes → Update visual baseline with `--update-snapshots`

### When NOT to Update Tests

- Backend refactoring (if outputs identical)
- Performance optimizations (parity tests check correctness, not speed)
- CSS framework upgrades (if visual result unchanged)

## Related Documentation

- **Seam specification**: `docs/seams/catalog-list/spec.md`
- **API contract**: `docs/seams/catalog-list/contracts/openapi.yaml`
- **UI behavior**: `docs/seams/catalog-list/ui-behavior.md`
- **Evidence capture strategy**: `legacy-golden/BASELINE_INDEX.md`
- **Synthetic baseline strategy**: `docs/SYNTHETIC_BASELINE_STRATEGY.md`

---

**Status**: ✅ Parity tests generated and ready for execution
**Next Action**: Run tests and document results in evidence.md
