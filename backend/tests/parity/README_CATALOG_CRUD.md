# Catalog CRUD Parity Tests

This directory contains parity tests for the `catalog-crud` seam, comparing the new Python/React implementation against the golden baselines captured from the legacy ASP.NET WebForms application.

## Test Files

### Backend API Parity

**File:** `test_catalog_crud_exports.py`

Tests that verify API responses match golden baselines:

- `test_get_brands_matches_golden_baseline` - Verifies GET /api/catalog/brands returns exact brand list
- `test_get_types_matches_golden_baseline` - Verifies GET /api/catalog/types returns exact type list
- `test_get_product_1_matches_golden_baseline` - Verifies GET /api/catalog/items/1 returns product with correct structure
- `test_create_product_returns_correct_structure` - Verifies POST creates product with correct response format
- `test_update_product_preserves_structure` - Verifies PUT updates product and returns correct format
- `test_delete_product_returns_no_content` - Verifies DELETE returns 204 and removes product
- `test_product_not_found_returns_404` - Verifies 404 handling for non-existent products

**Golden Baselines Used:**
- `legacy-golden/catalog-crud/exports/synthetic_brands.json` (5 brands)
- `legacy-golden/catalog-crud/exports/synthetic_types.json` (4 types)
- `legacy-golden/catalog-crud/exports/synthetic_product_1.json` (product ID 1)

**Run Command:**
```bash
cd backend
pytest tests/parity/test_catalog_crud_exports.py -v
```

---

### Backend Validation Parity

**File:** `test_catalog_crud_validation.py`

Tests that verify validation rules match golden baselines:

- `test_name_required_validation` - Name field must not be empty (BR-005)
- `test_price_range_validation_negative` - Price must be >= 0 (BR-001)
- `test_price_decimal_places_validation` - Price max 2 decimals (BR-001)
- `test_price_exceeds_max_validation` - Price range limit (BR-001)
- `test_available_stock_range_validation` - Stock 0-10,000,000 (BR-002)
- `test_restock_threshold_range_validation` - Restock 0-10,000,000 (BR-003)
- `test_max_stock_threshold_range_validation` - Max stock 0-10,000,000 (BR-004)
- `test_brand_required_validation` - Brand (catalog_brand_id) required
- `test_type_required_validation` - Type (catalog_type_id) required
- `test_submit_empty_form_validation` - Empty form shows all required field errors

**Golden Baselines Used:**
- `legacy-golden/catalog-crud/exports/synthetic_validation_errors.json` (all validation rules and test scenarios)

**Run Command:**
```bash
cd backend
pytest tests/parity/test_catalog_crud_validation.py -v
```

---

## Known Differences (Documented & Acceptable)

### 1. Error Message Wording

**Difference:**
- Legacy (ASP.NET): `"The Name field is required."`
- New (Pydantic): `"Field required"` or `"String should have at least 1 character"`

**Impact:** Low - Constraint is enforced correctly, only message text differs

**Rationale:** Pydantic uses its own validation message format. The business rule (field is required) is enforced identically.

---

### 2. Price Maximum Limit

**Difference:**
- Legacy: Hard limit at $1,000,000
- New: Much higher limit (Decimal max ~10^28)

**Impact:** Low - New system is more permissive (intentional improvement)

**Rationale:** The arbitrary 1 million limit is removed. The new system validates that price is a valid positive Decimal with max 2 decimal places, which is the real business constraint.

---

### 3. Error Response Format

**Difference:**
- Legacy: HTML form validation messages displayed inline, server-rendered
- New: JSON array of validation errors with field locations

**Example:**

Legacy (HTML):
```html
<span class="field-validation-error text-danger">The Name field is required.</span>
```

New (JSON):
```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "name"],
      "msg": "String should have at least 1 character",
      "input": "",
      "ctx": {"min_length": 1}
    }
  ]
}
```

**Impact:** Medium - Frontend must parse JSON format instead of server-rendered HTML

**Rationale:** REST API best practice. The frontend can format errors however it wants, enabling better UX.

---

### 4. Validation Timing

**Difference:**
- Legacy: Server-side only (postback)
- New: Both client-side (Zod) and server-side (Pydantic)

**Impact:** Positive - Better UX with immediate feedback before form submission

**Rationale:** Modern web app best practice. Users get instant feedback without network round-trip.

---

## Test Result Interpretation

### PASS ✅

The new system matches the legacy system's behavior (within documented tolerances). The test verifies:
- Correct data structure
- Correct field values
- Correct validation constraint enforcement
- Correct HTTP status codes

### FAIL ❌

A real difference was found. Review the test output to determine:
1. Is this a regression? (bug in new code)
2. Is this a missing field or validation rule?
3. Is this an undocumented intentional change?

If it's a regression, fix the code. If it's intentional, document it as a "Known Difference" above.

### SKIP ⏭️

The baseline for this scenario is not available. Check `BASELINE_INDEX.md` for why (e.g., "NOT CAPTURED - synthetic baseline only").

---

## Running All Parity Tests

### Backend Only
```bash
cd backend
pytest tests/parity/test_catalog_crud_*.py -v
```

### With Coverage
```bash
cd backend
pytest tests/parity/test_catalog_crud_*.py --cov=app.catalog --cov-report=html
```

### Fast Fail (Stop on First Error)
```bash
cd backend
pytest tests/parity/test_catalog_crud_*.py -x
```

---

## Synthetic Baselines Notice

⚠️ **All baselines for catalog-crud are SYNTHETIC** (not captured from running legacy app)

**Why?**
Browser automation tools (Playwright/Selenium) were not available in the Claude Code environment when baselines were captured.

**What does this mean?**
- Baselines were generated from:
  - `backend/app/core/seed.py` (sample data)
  - `docs/seams/catalog-crud/ui-behavior.md` (UI specifications)
  - `docs/context-fabric/business-rules.json` (validation rules)
- Data is accurate and matches seeded database
- Validation rules match documented business rules
- Visual appearance NOT captured (no real screenshots)

**Validation Approach:**
1. Automated tests verify data structure and validation logic
2. Manual user validation required for visual appearance
3. See `docs/SYNTHETIC_BASELINE_STRATEGY.md` for details

---

## Next Steps After Tests Pass

1. Run frontend E2E tests (see `frontend/tests/e2e/parity/README_CATALOG_CRUD.md`)
2. Perform manual visual validation (compare running apps side-by-side)
3. Document results in `docs/seams/catalog-crud/evidence/parity-test-results.md`
4. If all tests pass, mark seam as "PARITY VERIFIED" in seam tracker

---

## Troubleshooting

### Tests fail with "File not found" error

**Cause:** Golden baseline files are missing

**Fix:**
```bash
# Verify golden baselines exist
ls -la legacy-golden/catalog-crud/exports/
```

Expected files:
- `synthetic_brands.json`
- `synthetic_types.json`
- `synthetic_product_1.json`
- `synthetic_validation_errors.json`

If missing, they need to be regenerated from seed data.

---

### Tests fail with "Product not found"

**Cause:** Database not seeded with test data

**Fix:**
```bash
cd backend
python -m app.core.seed
```

This will populate the database with the expected seed data (Product ID 1, brands, types).

---

### Validation tests fail with "unexpected error message"

**Cause:** Pydantic validation messages differ from ASP.NET messages

**Expected:** This is a KNOWN DIFFERENCE (see above). The test should verify:
- The field IS validated (status code 422)
- An error message IS returned for the correct field
- The constraint IS enforced (e.g., negative price rejected)

The exact wording of the message is allowed to differ.

---

## Contact

For questions about parity test strategy or interpretation, see:
- `docs/SYNTHETIC_BASELINE_STRATEGY.md` - Baseline capture strategy
- `legacy-golden/catalog-crud/BASELINE_INDEX.md` - What was captured and why
- `docs/seams/catalog-crud/spec.md` - Seam specification
