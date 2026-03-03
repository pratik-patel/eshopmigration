# Discovery Summary: catalog-list (Runtime-Verified)

**Date**: 2026-03-02
**Status**: COMPLETE ✅
**Runtime Verification**: COMPLETE ✅
**Confidence**: HIGH

---

## Readiness Assessment

**GO**: ✅ YES

**Confidence**: HIGH

**Reason**: Read-only workflow with clear boundaries, well-defined service interface, no external dependencies, no shared writes. Runtime verification completed with browser-agent capturing 10 products, all CSS selectors, and form field IDs. Visual baseline screenshot saved for parity testing.

**Blockers**: NONE

**Warnings**:
- Low severity: Cannot fully test multi-page pagination with current dataset (only 10 products = 1 page)
- Mitigation: Test with >10 products in staging

---

## Runtime Data Summary

### Products
- **Total**: 10 (runtime-verified from legacy-golden/grid-data.json)
- **Original assumption**: 12 products (from seed.py) ❌ INCORRECT
- **Actual in live DB**: 10 products ✅ CONFIRMED

### Grid Structure (Runtime-Verified)
**10 Columns** (from legacy-golden/grid-data.json):
1. (Image thumbnail)
2. Name
3. Description
4. Brand
5. Type
6. Price
7. Picture name
8. Stock
9. Restock
10. Max stock

### CSS Selectors (Runtime-Captured)

**Home Page Controls** (from legacy-golden/ui-elements.json):
- Create New Button: `.btn.esh-button.esh-button-primary` → href="/Catalog/Create"
- Edit Links: `.esh-table-link` → href="/Catalog/Edit/{id}"
- Details Links: `.esh-table-link` → href="/Catalog/Details/{id}"
- Delete Links: `.esh-table-link` → href="/Catalog/Delete/{id}"

**Create Form Fields** (runtime-captured, ASP.NET ViewState pattern):

| Field | Selector | Name Attribute | Input Type | Default |
|-------|----------|----------------|------------|---------|
| Name | `#MainContent_Name` | `ctl00$MainContent$Name` | text | (empty) |
| Description | `#MainContent_Description` | `ctl00$MainContent$Description` | text | (empty) |
| Brand | `#MainContent_Brand` | `ctl00$MainContent$Brand` | select | Options: Azure, .NET, Visual Studio, SQL Server, Other |
| Type | `#MainContent_Type` | `ctl00$MainContent$Type` | select | Options: Mug, T-Shirt, Sheet, USB Memory Stick |
| Price | `#MainContent_Price` | `ctl00$MainContent$Price` | text | 0.00 |
| Stock | `#MainContent_Stock` | `ctl00$MainContent$Stock` | text | 0 |
| Restock | `#MainContent_Restock` | `ctl00$MainContent$Restock` | text | 0 |
| Max Stock | `#MainContent_Maxstock` | `ctl00$MainContent$Maxstock` | text | 0 |
| Create Button | `[name='ctl00$MainContent$ctl06']` | `ctl00$MainContent$ctl06` | submit | value="[ Create ]" |
| Cancel Link | `.btn.esh-button.esh-button-secondary` | N/A | link | href="../" |

**All form fields use CSS class**: `form-control`

---

## Data Targets (Runtime-Verified)

### Read Targets

**CatalogItems Table**:
- **Access Pattern**: SELECT with INNER JOIN, paginated (OFFSET/FETCH)
- **Runtime Row Count**: 10
- **Columns**: Id, Name, Description, Price, PictureFileName, CatalogTypeId, CatalogBrandId, AvailableStock, RestockThreshold, MaxStockThreshold
- **Evidence**: Services/CatalogService.cs:26-31
- **Shared With**: catalog-crud seam
- **Conflict Risk**: NONE (read-only)

**CatalogBrands Table**:
- **Access Pattern**: INNER JOIN
- **Runtime Values**: ".NET" (6 products), "Other" (4 products)
- **Columns**: Id, Brand
- **Evidence**: Services/CatalogService.cs:27
- **Shared With**: catalog-crud seam
- **Conflict Risk**: NONE (read-only)

**CatalogTypes Table**:
- **Access Pattern**: INNER JOIN
- **Runtime Values**: "T-Shirt" (6), "Mug" (2), "Sheet" (2)
- **Columns**: Id, Type
- **Evidence**: Services/CatalogService.cs:28
- **Shared With**: catalog-crud seam
- **Conflict Risk**: NONE (read-only)

### Write Targets

**NONE** - This seam is strictly read-only.

---

## Required Fields for Contract

### Input Parameters

| Field | Type | Required | Default | Validation |
|-------|------|----------|---------|------------|
| `page_size` | integer | No | 10 | Min: 1, Max: 100 |
| `page_index` | integer | No | 0 | Min: 0 (zero-based) |

### Output Fields (Pagination Metadata)

| Field | Type | Example | UI Display |
|-------|------|---------|------------|
| `page_index` | integer | 0 | "Page {page_index + 1}" |
| `page_size` | integer | 10 | "Showing {page_size} of {total_items}" |
| `total_items` | integer | 10 | "Showing X of {total_items} products" |
| `total_pages` | integer | 1 | "Page X - {total_pages}" |

### Output Fields (Product Data Array)

**Array**: `data[]` - List of CatalogItem objects

**Each CatalogItem must include**:

| Field | Type | Nullable | UI Column | Runtime Examples |
|-------|------|----------|-----------|------------------|
| `id` | integer | No | (hidden, used in links) | 1, 2, 3, ... |
| `name` | string | No | Column 2: Name | ".NET Bot Black Hoodie" |
| `description` | string | Yes | Column 3: Description | ".NET Bot Black Hoodie" |
| `price` | decimal | No | Column 6: Price ($XX.XX) | 19.5, 8.5, 12.0 |
| `picture_file_name` | string | No | Column 1 (img), Column 7 (text) | "1.png", "2.png" |
| `picture_uri` | string | Yes | (not displayed) | null |
| `catalog_type_id` | integer | No | (not displayed, FK) | N/A |
| `catalog_brand_id` | integer | No | (not displayed, FK) | N/A |
| `available_stock` | integer | No | Column 8: Stock | 100 |
| `restock_threshold` | integer | No | Column 9: Restock | 0 |
| `max_stock_threshold` | integer | No | Column 10: Max stock | 0 |
| `on_reorder` | boolean | No | (not displayed) | false |

**Navigation Properties** (must be eagerly loaded):

| Field | Type | Nested Fields | UI Column | Runtime Examples |
|-------|------|---------------|-----------|------------------|
| `catalog_brand` | object | `{id: int, brand: string}` | Column 4: Brand | {id: X, brand: ".NET"} |
| `catalog_type` | object | `{id: int, type: string}` | Column 5: Type | {id: Y, type: "T-Shirt"} |

**Sorting**: Always `ORDER BY id ASC` (not user-configurable)

---

## Evidence Map

### Triggers

**Trigger ID**: `page-load`
- **Screen**: Default.aspx
- **Event**: Page_Load (ASP.NET lifecycle)
- **Handler**: `_Default.Page_Load` (Default.aspx.cs:22-41)
- **Runtime URL**: http://localhost:50586
- **Screenshot**: legacy-golden/screenshots/screen_000_depth0.png
- **Confidence**: HIGH

### Flows

**Flow 1**: `view-catalog-list`
- **Description**: Load and display paginated product catalog
- **Call Path**:
  1. `_Default.Page_Load` (Default.aspx.cs:22)
  2. `CatalogService.GetCatalogItemsPaginated` (CatalogService.cs:22)
  3. Entity Framework 6 query with INNER JOINs
- **Boundaries**: Data access (stable boundary at EF6)
- **Side Effects**: NONE (read-only)
- **Runtime**: 10 products, 1 page

**Flow 2**: `configure-pagination`
- **Description**: Configure pagination links after data binding
- **Call Path**:
  1. `_Default.ConfigurePagination` (Default.aspx.cs:48)
  2. ASP.NET `GetRouteUrl()` for URL generation
- **Boundaries**: Framework routing (stable)
- **Side Effects**: NONE (UI-only)
- **Runtime**: Both Previous/Next disabled (single page)

### Cross-Seam Edges (Navigation Only)

All navigation dependencies are **soft coupling** (hyperlinks):

| Target Seam | Link Type | href Pattern | Runtime Verified |
|-------------|-----------|--------------|------------------|
| catalog-crud | Create | /Catalog/Create | ✅ |
| catalog-crud | Edit | /Catalog/Edit/{id} | ✅ |
| catalog-crud | Details | /Catalog/Details/{id} | ✅ |
| catalog-crud | Delete | /Catalog/Delete/{id} | ✅ |

---

## Runtime Sources Used

1. **BASELINE_INDEX.md**: 4 workflows captured, 4 screenshots
2. **grid-data.json**: 10 products with complete table structure
3. **ui-elements.json**: 39 home page elements + 16 create form elements
4. **screen_000_depth0.png**: Visual baseline for parity testing

---

## Test Scenarios (Runtime Status)

| Scenario | Status | Notes |
|----------|--------|-------|
| View first page (10 products) | ✅ VERIFIED | All columns populated with real data |
| Navigate to page 2 | ⚠️ NOT APPLICABLE | Only 1 page exists with current data |
| Edit link navigation | ✅ VERIFIED | /Catalog/Edit/1 captured |
| Create New navigation | ✅ VERIFIED | /Catalog/Create captured |
| Cancel navigation | ✅ VERIFIED | Returns to home page |
| Empty state (0 products) | ⚠️ NOT TESTED | Need DB with 0 products |
| CSS classes | ✅ VERIFIED | All selectors captured |

---

## Next Steps

1. ✅ **Discovery complete** - discovery.md written with runtime data
2. → **Contract generation** - Use runtime-verified fields above
3. ✅ **Backend implementation** - Already complete
4. ✅ **Frontend implementation** - Already complete
5. → **Parity testing** - Compare against screen_000_depth0.png
6. → **Add pagination test** - Test with >10 products

**Estimated Time**: 1 hour (testing and contract generation only)

---

## Key Corrections from Runtime Data

❌ **Original Assumption**: 12 products in database (from seed.py)
✅ **Runtime Reality**: 10 products in live database

❌ **Original Assumption**: Multi-page pagination needed for testing
✅ **Runtime Reality**: Single page (10 products with page_size=10)

✅ **New Discovery**: All form field IDs and CSS selectors captured
✅ **New Discovery**: ASP.NET ViewState pattern documented (ctl00$ prefix)
✅ **New Discovery**: Brand/Type dropdown options captured from running app

---

**Files Updated**:
- ✅ `docs/seams/catalog-list/discovery.md` (comprehensive runtime-verified report)
- ✅ `docs/seams/catalog-list/DISCOVERY_SUMMARY.md` (this file)

**Files Pending** (JSON outputs - awaiting tool fix):
- → `docs/seams/catalog-list/readiness.json`
- → `docs/seams/catalog-list/evidence-map.json`
- → `docs/seams/catalog-list/data/targets.json`
- → `docs/seams/catalog-list/contracts/required-fields.json`

**Note**: All required discovery data is documented in discovery.md and this summary. JSON files can be generated from these markdown documents if needed.
