# Legacy Golden Baselines

This directory contains the golden baselines captured from the running eShop WebForms application on 2026-03-03.

## Purpose

Golden baselines serve as the **ground truth** for parity validation. They document the exact state of the legacy application's UI, data, and behavior before migration.

## Contents

### Documentation
- **BASELINE_CAPTURE_SUMMARY.md**: Executive summary of capture process
- **coverage-report.json**: Coverage analysis (100% of screens captured)
- **exploration/discovered-screens.json**: Screen discovery results

### Seam: catalog-management
- **BASELINE_INDEX.md**: Comprehensive baseline manifest
- **user-journeys.md**: 6 user journeys with step-by-step workflows
- **screenshots/**: 10 screenshots (desktop, tablet, mobile viewports)
- **data/**: 7 JSON files with product data and page metadata

## Capture Details

- **Date:** 2026-03-03T19:04:39Z
- **Method:** Browser automation (Playwright, Chromium headless)
- **Coverage:** 100% (6/6 screens from seam-proposals.json)
- **Quality:** HIGH (real screenshots from running application)
- **Total Size:** ~6.64 MB

## Screens Captured

| Screen | URL | Auth | Screenshots | Status |
|--------|-----|------|-------------|--------|
| Product List (Default) | / | No | 3 (desktop, tablet, mobile) | COMPLETE |
| Product List (Paginated) | /products/1/10 | No | 1 (desktop) | COMPLETE |
| Product Details | /Catalog/Details/1 | No | 2 (desktop, tablet) | COMPLETE |
| Create Product | /Catalog/Create | Yes | 2 (desktop, filled) | COMPLETE |
| Edit Product | /Catalog/Edit/1 | Yes | 1 (desktop) | COMPLETE |
| Delete Product | /Catalog/Delete/1 | Yes | 1 (desktop) | COMPLETE |

## Usage

### For Parity Testing (Agent 110)
- Use screenshots for visual regression tests
- Use product_list_data.json for API response validation
- Use form metadata for validation rule comparison
- Use user journeys for workflow validation

### For Spec Generation (Agent 105)
- Reference screenshots for UI requirements
- Use data exports for API response schemas
- Use form metadata for validation rules
- Use user journeys for acceptance criteria

### For Discovery (Agent 104)
- Use baselines as reference for discovery documentation
- Compare running app behavior against captured state
- Validate data model assumptions

## Validation Status

- UI Inventory (ui-behavior.md): NO GAPS FOUND
- All screens from seam-proposals.json: CAPTURED
- Responsive layouts: VERIFIED (desktop, tablet, mobile)
- Data exports: COMPLETE (10 products)

## Next Steps

1. Review captured screenshots for completeness
2. Proceed to Phase 1 (Discovery) with agent 104
3. Use baselines for parity validation in Phase 4

## Notes

- Authentication was disabled during capture (UseAzureActiveDirectory=false)
- Image upload flow not tested (requires interactive AJAX testing)
- Database snapshots not captured (read-only access)
- Error states not captured (validation errors, 404s, 500s)

---

**Status:** COMPLETE
**Ready for Phase 1:** YES
