# Baseline Index: catalog-list

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
- `docs/seams/catalog-list/ui-behavior.md` (UI layout specification)
- `docs/context-fabric/business-rules.json` (validation rules)

**Validation Approach**: Manual user validation required (see `docs/SYNTHETIC_BASELINE_STRATEGY.md`)

---

## Screenshots

**Status**: NOT CAPTURED

| File | Step | Notes |
|------|------|-------|
| N/A | N/A | ⚠️ SYNTHETIC BASELINE - No real screenshots captured |

**Alternative**: ASCII mockups and layout specifications in `docs/seams/catalog-list/ui-behavior.md`

---

## Exports

### Catalog Data

| File | Source | Row Count | Notes |
|------|--------|-----------|-------|
| `exports/synthetic_catalog_page_1.json` | seed.py | 10 | First page of products (IDs 1-10) |
| `exports/synthetic_catalog_page_2.json` | seed.py | 2 | Second page of products (IDs 11-12) |

**Data Accuracy**: ✅ Matches seeded database exactly

---

## Database Snapshots

**Status**: NOT CAPTURED (read-only workflow, no DB changes)

| Workflow | Before | After | Diff | Notes |
|----------|--------|-------|------|-------|
| View catalog list | N/A | N/A | N/A | Read-only operation |
| Navigate to page 2 | N/A | N/A | N/A | Read-only operation |

**Expected Behavior**: No database writes for this seam.

---

## API/HTTP Captures

**Status**: NOT CAPTURED (localhost WebFetch blocked)

| Endpoint | File | Status Code | Notes |
|----------|------|-------------|-------|
| GET /Default.aspx | N/A | N/A | ⚠️ Cannot capture localhost |
| GET /Default.aspx?page=2 | N/A | N/A | ⚠️ Cannot capture localhost |

**Alternative**: OpenAPI contract will be generated in contract-generator step.

---

## User Journeys

**File**: `user-journeys.md` (to be created)
**Source**: `docs/seams/catalog-list/ui-behavior.md`
**Status**: ✅ Documented from static analysis

---

## Coverage

**Spec Workflows Captured**: 0/3 (SYNTHETIC fallback used)

### Workflows
1. ❌ View catalog list - SYNTHETIC data only
2. ❌ Navigate to Create - Not captured
3. ❌ Navigate to Edit/Details/Delete - Not captured

**Edge Cases Captured**: 0
- ❌ Empty catalog (no products)
- ❌ Single page (≤10 products, no pagination)
- ✅ Multiple pages (>10 products) - SYNTHETIC data shows 12 products

**Synthetic Baselines**: YES (all baselines are synthetic)

---

## Parity Test Strategy

### What CAN Be Validated

✅ **API Response Structure**:
- Compare new API (`GET /api/catalog/items`) to synthetic JSON
- Verify pagination math (page_index, page_size, total_items, total_pages)
- Verify data types and field names

✅ **Business Logic**:
- Products displayed in correct order
- Pagination calculations correct
- Brand/Type JOIN data included

✅ **Component Rendering**:
- Table renders 10 rows for page 1
- Pagination controls show correct text
- Action links present for each row

### What CANNOT Be Validated (Requires Real Baselines)

❌ **Visual Styling**:
- Exact pixel positions
- Font sizes and colors
- CSS rendering
- Image sizes and alignment

❌ **Interactive Behavior**:
- Button hover states
- Click animations
- Page transitions
- Loading states

❌ **Cross-Browser Compatibility**:
- IE11 vs Chrome rendering
- Mobile responsive layout

---

## Manual Validation Required

**User must verify visually by comparing**:
- Legacy app: http://localhost:50586/
- New app: http://localhost:5173/

**Checklist**: See `docs/SYNTHETIC_BASELINE_STRATEGY.md` → "User Manual Validation Checklist"

**Documentation**: Results should be saved to `docs/seams/catalog-list/evidence/manual-validation.md`

---

## Limitations

**Known Gaps Due to Synthetic Baselines**:
1. Cannot auto-generate screenshot comparison tests
2. Cannot verify exact CSS rendering
3. Cannot validate page transition behavior
4. Cannot capture HAR files for HTTP analysis
5. Visual parity requires manual user sign-off

**Mitigation**:
- Unit tests for backend logic
- Component tests for frontend rendering
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

**Estimated Effort**: 2-4 hours setup + 30 minutes per seam

---

## Validation Status

- ✅ Synthetic data generated
- ✅ Documentation complete
- ⏳ **Awaiting user manual validation**
- ⏳ Parity tests TBD (synthetic baseline support)

---

**Next Step**: Proceed to STEP 6 (discovery) for this seam, or capture real baselines if tools become available.
