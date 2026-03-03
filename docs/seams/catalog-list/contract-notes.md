# Contract Notes: catalog-list

**Seam**: catalog-list
**Date**: 2026-03-02
**Status**: Contract Complete & Validated
**Confidence**: HIGH (Runtime-Verified)

---

## Summary

OpenAPI 3.1 contract generated for the catalog-list seam based on:

1. **Discovery evidence**: docs/seams/catalog-list/discovery.md (UPDATED with runtime data)
2. **Runtime capture**: legacy-golden/grid-data.json (10 real products)
3. **UI element capture**: legacy-golden/ui-elements.json (39 home page elements, CSS selectors)
4. **Visual baseline**: legacy-golden/screenshots/screen_000_depth0.png

**Key Fact**: Runtime verification revealed **10 products** in live database, not 12 as originally assumed from seed data.

---

## Contract Location

**File**: `docs/seams/catalog-list/contracts/openapi.yaml`

**Validation Status**: PASSED (YAML valid, structure complete)

**Validation Output**:
```
OpenAPI Version: 3.1.0
API Title: Catalog List API
API Version: v1

Paths (1):
  /catalog/items
    - GET: getCatalogItems

Schemas (5):
  - PaginatedCatalogResponse: 5 properties (5 required)
  - CatalogItem: 14 properties (13 required)
  - CatalogBrand: 2 properties (2 required)
  - CatalogType: 2 properties (2 required)
  - ErrorResponse: 3 properties (2 required)

Examples: 6 response examples defined
```

---

## Endpoint Definition

### `GET /api/catalog/items`

**Operation ID**: `getCatalogItems`

**Query Parameters**:
- `page_size` (optional, default: 10, range: 1-100)
- `page_index` (optional, default: 0, minimum: 0)

**Response**: `200 OK` with `PaginatedCatalogResponse`

**Error Responses**:
- `400 Bad Request`: Invalid query parameters
- `500 Internal Server Error`: Database or unexpected errors

---

## Key Design Decisions

### 1. Runtime Data Used for Examples

**Decision**: Use real captured data from grid-data.json as primary example.

**Rationale**:
- Provides accurate representation of live system
- All 10 products included in `firstPageTenItems` example
- Real prices, names, brands, types captured
- Enables pixel-perfect parity testing

**Alternatives Considered**:
- Using synthetic/seed data → Rejected (contradicted runtime evidence)
- Using only 2-3 example items → Rejected (incomplete coverage)

**Traceability**: grid-data.json rows → openapi.yaml `firstPageTenItems` example

---

### 2. Pagination Metadata

**Decision**: Include 4 pagination fields in response envelope.

**Fields**:
- `page_index`: Zero-based current page
- `page_size`: Items per page
- `total_items`: Total count across all pages
- `total_pages`: Calculated total pages

**Rationale**:
- Matches legacy `PaginatedItemsViewModel<T>` structure exactly
- Enables frontend to calculate "Showing X of Y" text
- Enables Previous/Next button state logic
- No need for frontend to recalculate total_pages

**Traceability**: discovery.md lines 336-341, ViewModel/PaginatedItemsViewModel.cs

---

### 3. Navigation Properties Always Included

**Decision**: `catalog_brand` and `catalog_type` are required fields in `CatalogItem` schema.

**Rationale**:
- Legacy code eager-loads via `.Include(c => c.CatalogBrand).Include(c => c.CatalogType)`
- UI displays brand and type in columns 4 and 5
- Avoids N+1 query problem
- Simplifies frontend logic (no null checks needed)

**SQL Evidence**: CatalogService.cs:27-28 (INNER JOIN)

**Traceability**: discovery.md lines 359-364

**Alternative Considered**:
- Making navigation properties optional → Rejected (always present in legacy)

---

### 4. `picture_uri` Field Marked Nullable but Included

**Decision**: Keep `picture_uri` field as nullable string, but document as legacy/unused.

**Rationale**:
- Field exists in legacy CatalogItem entity
- Always null in current runtime dataset
- May be used by other seams (catalog-crud)
- Better to keep for compatibility than drop prematurely

**Evidence**: discovery.md line 352, grid-data.json (all null)

**Migration Note**: Can be deprecated in v2 if confirmed unused across all seams

---

### 5. Real Dropdown Options Documented

**Decision**: Document all available brands and types in schema descriptions, even if not all used in current dataset.

**Brands Available** (from ui-elements.json):
- Azure
- .NET
- Visual Studio
- SQL Server
- Other

**Types Available** (from ui-elements.json):
- Mug
- T-Shirt
- Sheet
- USB Memory Stick

**Brands/Types in Current Dataset**:
- Brands: .NET, Other (2 of 5 used)
- Types: Mug, T-Shirt, Sheet (3 of 4 used)

**Rationale**:
- Provides complete reference for frontend dropdown implementation
- Documents data that exists in CatalogBrands/CatalogTypes tables
- Useful for catalog-crud seam (Create/Edit forms need full lists)

**Traceability**: ui-elements.json (Create form dropdown options)

---

### 6. Stock Fields Kept Despite All Zero/Same Values

**Decision**: Include `available_stock`, `restock_threshold`, `max_stock_threshold` despite uniform values in runtime data.

**Runtime Values**:
- `available_stock`: All 100
- `restock_threshold`: All 0
- `max_stock_threshold`: All 0

**Rationale**:
- Fields are part of core domain model (inventory management)
- Likely to have varied values in real production data
- Required for catalog-crud seam (Edit operations)
- Removing would break contract parity with legacy

**Evidence**: discovery.md lines 355-357, Models/CatalogItem.cs:19-21

---

### 7. Error Response Schema

**Decision**: Use structured error response with `code`, `message`, `detail` fields.

**Format**:
```json
{
  "code": "INVALID_PAGE_SIZE",
  "message": "page_size must be between 1 and 100",
  "detail": {
    "field": "page_size",
    "value": 0,
    "constraint": "minimum: 1"
  }
}
```

**Rationale**:
- Enables programmatic error handling (check `code` field)
- Human-readable messages for debugging
- Optional `detail` for validation errors with field-level info
- Compatible with FastAPI HTTPException pattern

**Migration Compatibility**: Legacy WebForms does not have standardized error JSON; this is new for API

---

### 8. Example Scenarios

**Decision**: Provide 3 example responses (not just 1).

**Examples**:
1. `firstPageTenItems`: Real runtime data (10 products, page 0)
2. `emptyPage`: Empty catalog scenario (0 products)
3. `secondPage`: Hypothetical multi-page scenario (not testable with current data)

**Rationale**:
- `firstPageTenItems`: Baseline for implementation and testing
- `emptyPage`: Documents BR-004 behavior (empty state)
- `secondPage`: Documents pagination logic for future growth

**Testing Notes**:
- `firstPageTenItems`: Fully testable (current state)
- `emptyPage`: Not tested (would require clearing database)
- `secondPage`: Not testable (would require adding 11+ products)

**Traceability**: discovery.md lines 503-557 (Test Scenarios)

---

## Validation Rules

### Query Parameters

| Parameter | Type | Min | Max | Default | Validation Rule |
|-----------|------|-----|-----|---------|-----------------|
| `page_size` | integer | 1 | 100 | 10 | FastAPI Query(ge=1, le=100) |
| `page_index` | integer | 0 | - | 0 | FastAPI Query(ge=0) |

**Legacy Evidence**: Default.aspx.cs:15-16 (constants)

**New Validation**: Legacy does not validate these; API will enforce limits

---

### Response Fields

| Field | Type | Validation | Source |
|-------|------|-----------|--------|
| `page_index` | integer | ≥ 0 | Must match request parameter |
| `page_size` | integer | 1-100 | Must match request parameter |
| `total_items` | integer | ≥ 0 | COUNT query from database |
| `total_pages` | integer | ≥ 0 | Calculated: ceil(total_items / page_size) |
| `data` | array | 0-100 items | Length ≤ page_size |

**Calculated Field**: `total_pages` must equal `ceil(total_items / page_size)`

**Edge Case**: If `total_items = 0`, then `total_pages = 0` and `data = []`

---

## Unmapped/Dropped Fields

**NONE**

All fields from legacy entities are present in the contract.

**Verification**: See dto-mapping.md "Unmapped Fields" section (confirmed empty)

---

## Cross-Seam Dependencies

### Navigation Links

The catalog-list API returns product IDs that are used for navigation to catalog-crud seam operations:

| Action | Frontend Route | Related Seam | DTO Field Used |
|--------|----------------|--------------|----------------|
| Edit | `/catalog/edit/{id}` | catalog-crud | `data[].id` |
| Details | `/catalog/details/{id}` | catalog-crud | `data[].id` |
| Delete | `/catalog/delete/{id}` | catalog-crud | `data[].id` |

**Contract Note**: These are **frontend routing concerns**, not API endpoints. The catalog-list API does not need to know about these operations.

**Discovery Evidence**: discovery.md lines 267-278

---

### Shared Reference Data

The catalog-list API returns brand and type data that is also used by:

- **catalog-crud** seam: Dropdown population for Create/Edit forms

**Contract Note**: Brand and type lists should be provided by a separate reference data endpoint (future work) to avoid duplication.

**Recommendation**: Add `GET /api/catalog/brands` and `GET /api/catalog/types` endpoints in future iteration.

---

## Runtime Evidence Summary

| Evidence Type | Source | Key Findings |
|---------------|--------|--------------|
| Database content | grid-data.json | 10 products (not 12) |
| UI structure | ui-elements.json | 39 home page elements, CSS selectors |
| Visual baseline | screen_000_depth0.png | Screenshot for pixel-perfect comparison |
| Discovery report | discovery.md | Updated with runtime verification |
| Call chain | discovery.md lines 88-138 | Page_Load → Service → EF6 → DB |
| SQL query | discovery.md lines 198-228 | SELECT with 2 INNER JOINs |
| Business rules | discovery.md lines 469-500 | 5 rules documented |
| Test scenarios | discovery.md lines 503-557 | 8 scenarios (3 verified) |

**Confidence Level**: HIGH

**Gaps**:
- Empty state not tested (would need to clear DB)
- Multi-page pagination not testable (only 10 products)
- Image fallback (dummy.png) not tested (all products have valid filenames)

**Recommendation**: Gaps are acceptable; edge cases can be tested later with modified test data.

---

## Implementation Checklist

### Backend (FastAPI)

- [ ] Create `backend/app/catalog/router.py` with `GET /api/catalog/items` endpoint
- [ ] Create `backend/app/catalog/schemas.py` with Pydantic models matching OpenAPI schemas
- [ ] Create `backend/app/catalog/service.py` with business logic (query, pagination)
- [ ] Implement SQLAlchemy query with `.options(joinedload(...))` for eager loading
- [ ] Implement validation for query parameters (page_size: 1-100, page_index: ≥0)
- [ ] Implement error handling with structured ErrorResponse format
- [ ] Write unit tests for service layer (mock DB)
- [ ] Write integration tests for API endpoint (TestClient)
- [ ] Write parity test comparing API response to grid-data.json

### Frontend (React/TypeScript)

- [ ] Generate TypeScript types from openapi.yaml using `openapi-typescript`
- [ ] Create `frontend/src/api/catalog.ts` with API client function
- [ ] Create `frontend/src/hooks/useCatalogItems.ts` with TanStack Query hook
- [ ] Create `frontend/src/pages/catalog-list/CatalogListPage.tsx`
- [ ] Create `frontend/src/components/catalog/CatalogTable.tsx` (10 columns)
- [ ] Create `frontend/src/components/catalog/Pagination.tsx`
- [ ] Implement image path logic: `/pics/{picture_file_name}`
- [ ] Implement price formatting: `$XX.XX`
- [ ] Implement pagination UI: "Showing X of Y products - Page N - M"
- [ ] Preserve CSS classes: `esh-table`, `esh-thumbnail`, `esh-price`, `esh-table-link`
- [ ] Write component tests (React Testing Library)
- [ ] Write E2E test (Playwright) comparing to screen_000_depth0.png

---

## Traceability

**Contract validates**:
- All fields in openapi.yaml trace to Models/ or ViewModel/ classes
- All examples use real data from grid-data.json
- All validation rules trace to business rules in discovery.md
- All UI mappings confirmed via ui-elements.json

**Forward traceability**:
- Backend Pydantic models will be generated/validated against openapi.yaml
- Frontend TypeScript types will be generated from openapi.yaml
- Integration tests will use openapi.yaml examples as fixtures

**Evidence preserved**:
- Original grid-data.json → version controlled
- Original ui-elements.json → version controlled
- Original screen_000_depth0.png → version controlled
- Discovery report with runtime annotations → version controlled

---

## Next Steps

1. **DONE**: Contract generation (this document)
2. **DONE**: DTO mapping (dto-mapping.md)
3. **DONE**: Contract validation (YAML valid)
4. **TODO**: Backend implementation (FastAPI routes + service)
5. **TODO**: Frontend implementation (React components)
6. **TODO**: Parity testing (compare API response to grid-data.json)
7. **TODO**: Visual parity testing (compare UI render to screen_000_depth0.png)

---

## Sign-off

**Contract Author**: API Contract Designer Agent
**Contract Review Status**: Self-validated (YAML structure)
**Awaiting Review By**: Migration team / Lead developer
**Approval Required Before**: Backend implementation begins

**Contract Version**: 1.0 (Runtime-Verified)
**Contract Stability**: STABLE (based on production runtime evidence)

---

**Document Created**: 2026-03-02
**Last Updated**: 2026-03-02
**Next Review**: After backend implementation (validate against real API responses)
