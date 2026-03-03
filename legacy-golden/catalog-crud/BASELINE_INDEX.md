# Baseline Index: catalog-crud

**Captured**: 2026-03-02T00:00:00Z
**Application Type**: Web (ASP.NET WebForms 4.7.2)
**Framework**: ASP.NET WebForms
**Capture Tools**: SYNTHETIC (browser automation not available)
**Environment**: N/A (baselines generated from documentation)
**Status**: ⚠️ **SYNTHETIC BASELINES** - See limitations below

---

## ⚠️ SYNTHETIC BASELINE NOTICE

**These baselines were NOT captured from the running legacy application.**

**Reason**: Browser automation tools (Playwright/Selenium) not available in Claude Code environment.

**Source**: Generated from:
- `backend/app/core/seed.py` (sample data)
- `docs/seams/catalog-crud/ui-behavior.md` (UI layout specification)
- `docs/context-fabric/business-rules.json` (validation rules)

**Validation Approach**: Manual user validation required (see `docs/SYNTHETIC_BASELINE_STRATEGY.md`)

---

## Screenshots

**Status**: NOT CAPTURED

| File | Step | Notes |
|------|------|-------|
| N/A | N/A | ⚠️ SYNTHETIC BASELINE - No real screenshots captured |

**Alternative**: Layout specifications and field descriptions in `docs/seams/catalog-crud/ui-behavior.md`

---

## Exports

### Dropdown Data

| File | Source | Row Count | Notes |
|------|--------|-----------|-------|
| `exports/synthetic_brands.json` | seed.py | 5 | All brands for dropdown |
| `exports/synthetic_types.json` | seed.py | 4 | All types for dropdown |

### Product Data

| File | Source | Notes |
|------|--------|-------|
| `exports/synthetic_product_1.json` | seed.py | Product ID 1 for Edit/Details/Delete |

### Validation Rules

| File | Source | Notes |
|------|--------|-------|
| `exports/synthetic_validation_errors.json` | business-rules.json | All error messages and test scenarios |

**Data Accuracy**: ✅ Matches seeded database and documented business rules exactly

---

## Database Snapshots

**Status**: NOT CAPTURED (synthetic data only)

| Workflow | Before | After | Diff | Notes |
|----------|--------|-------|------|-------|
| Create product | N/A | N/A | N/A | ⚠️ Would show new row in CatalogItems |
| Edit product | N/A | N/A | N/A | ⚠️ Would show Name/Price changed |
| Delete product | N/A | N/A | N/A | ⚠️ Would show row removed |

**Expected Behavior**:
- Create: INSERT INTO CatalogItems
- Edit: UPDATE CatalogItems SET Name = ..., Price = ... WHERE Id = 1
- Delete: DELETE FROM CatalogItems WHERE Id = X

---

## API/HTTP Captures

**Status**: NOT CAPTURED (localhost WebFetch blocked)

| Endpoint | File | Status Code | Notes |
|----------|------|-------------|-------|
| GET /Catalog/Create | N/A | N/A | ⚠️ Cannot capture localhost |
| POST /Catalog/Create | N/A | N/A | ⚠️ Cannot capture localhost |
| GET /Catalog/Edit/1 | N/A | N/A | ⚠️ Cannot capture localhost |
| POST /Catalog/Edit/1 | N/A | N/A | ⚠️ Cannot capture localhost |
| GET /Catalog/Details/1 | N/A | N/A | ⚠️ Cannot capture localhost |
| GET /Catalog/Delete/1 | N/A | N/A | ⚠️ Cannot capture localhost |
| POST /Catalog/Delete/1 | N/A | N/A | ⚠️ Cannot capture localhost |

**Alternative**: OpenAPI contract will be generated in contract-generator step.

---

## User Journeys

**File**: `user-journeys.md` (to be created)
**Source**: `docs/seams/catalog-crud/ui-behavior.md`
**Status**: ✅ Documented from static analysis

---

## Coverage

**Spec Workflows Captured**: 0/4 (SYNTHETIC fallback used)

### Workflows
1. ❌ Create new product - SYNTHETIC data only
2. ❌ Edit existing product - SYNTHETIC data only
3. ❌ View product details - SYNTHETIC data only
4. ❌ Delete product - SYNTHETIC data only

**Edge Cases Captured**: 0
- ❌ Empty form submission (validation)
- ❌ Invalid price values
- ❌ Invalid stock values
- ❌ Picture filename read-only on Edit
- ❌ Product not found (404)

**Synthetic Baselines**: YES (all baselines are synthetic)

---

## Parity Test Strategy

### What CAN Be Validated

✅ **API Contracts**:
- POST /api/catalog/items with valid data
- PUT /api/catalog/items/{id} with valid data
- DELETE /api/catalog/items/{id}
- GET /api/catalog/brands
- GET /api/catalog/types

✅ **Validation Rules**:
- Name required validation
- Price range validation (0-1000000)
- Price decimal places validation (max 2)
- Stock range validation (0-10000000)
- Brand/Type required validation

✅ **Business Logic**:
- Create operation inserts row
- Edit operation updates row
- Delete operation removes row
- Dropdowns populated correctly

### What CANNOT Be Validated (Requires Real Baselines)

❌ **Visual Styling**:
- Form layouts (1-column Create vs 2-column Edit)
- Image display on Edit/Details/Delete
- Button positions and styling
- Error message positioning

❌ **Interactive Behavior**:
- Form submission flow
- Redirect after save
- Dropdown interactions
- Read-only picture field behavior

---

## Manual Validation Required

**User must verify visually by comparing**:
- Legacy app: http://localhost:50586/Catalog/Create
- New app: http://localhost:5173/catalog/create

**Checklist**: See `docs/SYNTHETIC_BASELINE_STRATEGY.md` → "User Manual Validation Checklist"

**Documentation**: Results should be saved to `docs/seams/catalog-crud/evidence/manual-validation.md`

---

## Validation Test Cases

### Create Page
- [ ] Empty form displays with default values (price: 0.00, stock fields: 0)
- [ ] Brand dropdown populates with 5 brands
- [ ] Type dropdown populates with 4 types
- [ ] Submit empty form shows "The Name field is required."
- [ ] Submit with price=-5 shows validation error
- [ ] Submit with price=12.999 shows validation error
- [ ] Submit with valid data creates product and redirects

### Edit Page
- [ ] Form pre-fills with product data
- [ ] Product image displays on left
- [ ] Picture filename is read-only
- [ ] Changing name and price works
- [ ] Submit saves changes and redirects

### Details Page
- [ ] All fields display read-only
- [ ] Product image displays
- [ ] Edit button navigates to edit page
- [ ] Back to List button navigates to catalog list

### Delete Page
- [ ] Confirmation message displays
- [ ] Product details display
- [ ] Delete button removes product and redirects
- [ ] Back to List button cancels without deleting

---

## Limitations

**Known Gaps Due to Synthetic Baselines**:
1. Cannot auto-generate screenshot comparison tests
2. Cannot verify exact form layouts
3. Cannot validate image positioning
4. Cannot capture HTTP POST payloads
5. Visual parity requires manual user sign-off

**Mitigation**:
- Unit tests for backend CRUD operations
- Component tests for frontend forms
- Integration tests for API contracts
- Manual visual validation by user

---

## Future Improvements

**If real capture becomes possible**:
1. Install Playwright: `npm install -D @playwright/test`
2. Run automated capture script
3. Replace this BASELINE_INDEX.md with real captures
4. Enable screenshot-based parity tests
5. Remove "SYNTHETIC" warnings

**Estimated Effort**: 2-4 hours setup + 1 hour per workflow

---

## Validation Status

- ✅ Synthetic data generated (brands, types, product, validation rules)
- ✅ Documentation complete
- ⏳ **Awaiting user manual validation**
- ⏳ Parity tests TBD (synthetic baseline support)

---

**Next Step**: Proceed to STEP 6 (discovery) for this seam, or capture real baselines if tools become available.
