# Parity Tests for catalog-list Seam

This directory contains parity tests that compare the new Python + React implementation to the legacy ASP.NET WebForms application.

## Purpose

Parity tests ensure that the migrated system produces **exactly the same outputs** as the legacy system. These tests are the ultimate proof that the migration is correct.

## Golden Baseline

**Source**: `legacy-golden/grid-data.json`

This file contains the actual data captured from the legacy application running at `http://localhost:50586/`.

**Capture Method**: Browser automation script extracted table data from Default.aspx

**Capture Date**: 2026-03-02

**Coverage**: First page of catalog (10 products)

## Test Files

### 1. `test_catalog_list_api_parity.py`

**Purpose**: Compare API responses to golden baseline

**Tests**:
- Row count matches (10 products)
- Pagination metadata calculations
- Product field structure (all required fields present)
- Product data matches golden baseline exactly
- Product order preserved
- Default parameters work correctly
- Edge cases (empty catalog, pagination beyond data)
- Price precision (2 decimal places)
- Validation rules (page_size, page_index constraints)

**Run**: `pytest backend/tests/parity/test_catalog_list_api_parity.py -v`

### 2. `test_catalog_list_data_validation.py`

**Purpose**: Deep validation of individual product data

**Tests**:
- Individual validation for each of 10 products
- Brand and type navigation properties populated
- Brand distribution matches golden baseline
- Type distribution matches golden baseline

**Run**: `pytest backend/tests/parity/test_catalog_list_data_validation.py -v`

## Expected Results

### PASS Criteria

All tests should **PASS** if:
- Backend returns exactly the same 10 products as legacy system
- All field values match (name, description, brand, type, price, stock, etc.)
- Pagination metadata is calculated correctly
- Products appear in the same order

### FAIL Scenarios

Tests will **FAIL** if:
- Product count differs (e.g., 9 products instead of 10)
- Any field value differs (e.g., price 19.50 vs 19.49)
- Product order changes (e.g., Mug appears before Hoodie)
- Brand/Type JOIN fails (e.g., null instead of ".NET")
- Pagination math is wrong (e.g., total_pages = 3 instead of 2)

## Exclusions

These fields are **excluded** from exact comparison (documented in test code):

- `id`: Auto-generated primary key (not in baseline HTML)
- `catalog_type_id`: Foreign key (not displayed in legacy UI)
- `catalog_brand_id`: Foreign key (not displayed in legacy UI)
- `picture_uri`: Legacy field (always null, not used)
- `on_reorder`: Calculated field (not in baseline table)

## Running the Tests

### Prerequisites

1. Backend server must be running: `cd backend && uvicorn app.main:app --reload`
2. Database must be seeded with test data: `python -m app.core.seed`

### Run All Parity Tests

```bash
pytest backend/tests/parity/test_catalog_list_* -v
```

### Run with Coverage

```bash
pytest backend/tests/parity/test_catalog_list_* -v --cov=app.catalog --cov-report=html
```

### Run Specific Test

```bash
pytest backend/tests/parity/test_catalog_list_api_parity.py::TestCatalogListAPIParity::test_product_data_matches_golden_baseline -v
```

## Interpreting Results

### Example: PASS (Perfect Match)

```
test_catalog_list_api_parity.py::TestCatalogListAPIParity::test_first_page_row_count PASSED
test_catalog_list_api_parity.py::TestCatalogListAPIParity::test_product_data_matches_golden_baseline PASSED
test_catalog_list_data_validation.py::TestProductDataValidation::test_product_1_net_bot_black_hoodie PASSED
```

**Interpretation**: New system matches legacy system exactly. Migration is correct.

### Example: FAIL (Data Mismatch)

```
test_catalog_list_api_parity.py::TestCatalogListAPIParity::test_product_data_matches_golden_baseline FAILED
...
AssertionError: Product 0: price mismatch - expected Decimal('19.5'), got Decimal('19.49')
```

**Interpretation**: Price calculation is incorrect. Check service layer logic.

### Example: FAIL (Missing Data)

```
test_catalog_list_api_parity.py::TestCatalogListAPIParity::test_first_page_row_count FAILED
...
AssertionError: Expected 10 products, got 9
```

**Interpretation**: Database seed is incomplete or query is filtering incorrectly.

## Limitations

### What These Tests Do NOT Cover

1. **Visual styling**: Tests compare data, not CSS/HTML rendering
2. **Timestamps**: Auto-generated timestamps are excluded
3. **User interactions**: Click events, form submissions (covered by E2E tests)
4. **Performance**: Response time, load testing (separate suite)
5. **Cross-browser**: Browser compatibility (covered by Playwright E2E tests)

### Why These Limitations Exist

Parity tests focus on **data correctness** only. Visual and interactive behavior is validated by frontend E2E tests in `frontend/tests/e2e/parity/`.

## Troubleshooting

### Test fails with "golden baseline not found"

**Cause**: `legacy-golden/grid-data.json` is missing

**Fix**:
```bash
# Ensure golden baseline exists
ls legacy-golden/grid-data.json
```

If missing, re-capture from legacy application (see `docs/seams/catalog-list/evidence-capture.md`).

### Test fails with "connection refused"

**Cause**: Backend server not running or wrong URL

**Fix**:
```bash
# Start backend server
cd backend
uvicorn app.main:app --reload --port 8000
```

### Test passes but products look wrong in UI

**Cause**: Parity tests only validate data, not visual rendering

**Fix**: Run frontend E2E tests:
```bash
cd frontend
npx playwright test tests/e2e/parity/catalog-list-parity.spec.ts
```

## Maintenance

### When to Update Tests

- **Database schema changes**: Update field assertions
- **Business rule changes**: Update validation tests
- **New golden baseline captured**: Tests should automatically use new data
- **Field exclusions change**: Document in test comments

### When NOT to Update Tests

- **Visual changes only**: Parity tests don't check CSS
- **Performance optimizations**: Parity tests check correctness, not speed
- **Refactoring**: If outputs are identical, tests should still pass

## Related Documentation

- **Golden baseline capture**: `docs/seams/catalog-list/evidence-capture.md`
- **API contract**: `docs/seams/catalog-list/contracts/openapi.yaml`
- **Frontend E2E tests**: `frontend/tests/e2e/parity/catalog-list-parity.spec.ts`
- **Parity strategy**: `docs/SYNTHETIC_BASELINE_STRATEGY.md`

## Success Criteria

**Seam is complete** when:
- ✅ All parity tests pass
- ✅ Frontend E2E tests pass
- ✅ Manual validation confirms visual match
- ✅ Evidence documented in `docs/seams/catalog-list/evidence/evidence.md`
