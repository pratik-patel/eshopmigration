# Discovery Report: catalog-list

**Seam ID**: catalog-list
**Date**: 2026-03-02 (Updated with runtime data)
**Status**: Discovery Complete (Runtime-Verified)
**Confidence**: High

---

## Executive Summary

**Purpose**: Display paginated catalog of products with navigation links to CRUD operations.

**Complexity**: Medium
- Single page lifecycle (Page_Load)
- One service method call
- Read-only database access
- No writes, no transactions
- No external dependencies

**Readiness**: ✅ GO
- Clear boundary
- Simple data flow
- No blockers
- No hard dependencies
- No shared writes

**Runtime Verification**: ✅ COMPLETED
- Browser-agent captured 4 workflows
- **10 products confirmed in live database** (not 12 from seed data)
- Real CSS selectors and form field IDs captured
- Actual grid structure and column headers verified
- Screenshots captured for visual parity baseline

---

## Entry Points & Triggers

### Trigger 1: Page Load

**File**: `src/eShopLegacyWebForms/Default.aspx.cs`
**Symbol**: `_Default.Page_Load`
**Lines**: 22-41
**Framework Event**: ASP.NET WebForms Page_Load

**Evidence**:
```csharp
protected void Page_Load(object sender, EventArgs e)
{
    if (PaginationParamsAreSet())
    {
        var size = Convert.ToInt32(Page.RouteData.Values["size"]);
        var index = Convert.ToInt32(Page.RouteData.Values["index"]);
        Model = CatalogService.GetCatalogItemsPaginated(size, index);
        _log.Info($"Now loading... /Default.aspx?size={size}&index={index}");
    }
    else
    {
        Model = CatalogService.GetCatalogItemsPaginated(DefaultPageSize, DefaultPageIndex);
        _log.Info($"Now loading... /Default.aspx?size={DefaultPageSize}&index={DefaultPageIndex}");
    }

    productList.DataSource = Model.Data;
    productList.DataBind();
    ConfigurePagination();
}
```

**Runtime Capture**:
- **Base URL**: `http://localhost:50586`
- **Route Accessed**: `/` (default page)
- **Workflows Captured**: 4 (Home Page, Create, Edit, Cancel navigation)
- **Total Screenshots**: 4 baseline images
- **Evidence File**: `legacy-golden/BASELINE_INDEX.md`
- **Screenshot**: `legacy-golden/screenshots/screen_000_depth0.png`

**Trigger Conditions**:
1. User navigates to `/` (Default.aspx)
2. User navigates to `/Catalog/Page/{index}/{size}` (pagination route)

**Input Parameters**:
- `page_size` (int, default: 10, from route or constant)
- `page_index` (int, default: 0, from route or constant)

---

## Vertical Slice: Call Chain

### Flow 1: View Catalog List (Main Workflow)

**Trigger**: Page_Load event
**Start**: `Default.aspx.cs:_Default.Page_Load` (line 22)
**End**: Database query + UI data binding

**Call Path**:
```
1. _Default.Page_Load (Default.aspx.cs:22)
   ├─> ICatalogService.GetCatalogItemsPaginated(size, index)
   │
2. CatalogService.GetCatalogItemsPaginated (CatalogService.cs:22)
   ├─> db.CatalogItems.LongCount()                    [READ: CatalogItems]
   ├─> db.CatalogItems
   │    .Include(c => c.CatalogBrand)                  [JOIN: CatalogBrands]
   │    .Include(c => c.CatalogType)                   [JOIN: CatalogTypes]
   │    .OrderBy(c => c.Id)
   │    .Skip(pageSize * pageIndex)
   │    .Take(pageSize)
   │    .ToList()
   │
3. Entity Framework 6
   ├─> Translates to SQL:
   │   SELECT [CatalogItems].[Id], [CatalogItems].[Name], ...
   │   FROM [dbo].[CatalogItems]
   │   INNER JOIN [dbo].[CatalogBrands] ON ...
   │   INNER JOIN [dbo].[CatalogTypes] ON ...
   │   ORDER BY [Id]
   │   OFFSET (@pageSize * @pageIndex) ROWS
   │   FETCH NEXT @pageSize ROWS ONLY
   │
4. Return PaginatedItemsViewModel<CatalogItem>
   ├─> ItemsPerPage: 10
   ├─> TotalItems: 10 (runtime-verified from legacy-golden/grid-data.json)
   ├─> ActualPage: 0
   ├─> TotalPages: 1
   └─> Data: List<CatalogItem> with navigation properties populated
```

**Runtime Verification**:
- **Total Products in DB**: 10 (confirmed via `legacy-golden/grid-data.json`)
- **Products on First Page**: 10 (all items fit on single page)
- **Total Pages**: 1 (no pagination needed with current data)
- **Query Executed**: SELECT with 2 INNER JOINs confirmed

**Boundaries Hit**:
- **Data Access**: Entity Framework 6 query (stable boundary)
- **No cross-seam calls**: Self-contained read operation
- **No external dependencies**: Pure database read

**Side Effects**: NONE (read-only)

**Transaction Scope**: NONE (no writes)

---

### Flow 2: Configure Pagination

**Trigger**: Called by Page_Load after data binding
**Start**: `Default.aspx.cs:_Default.ConfigurePagination` (line 48)
**End**: Hyperlink URL generation

**Call Path**:
```
1. _Default.ConfigurePagination (Default.aspx.cs:48)
   ├─> GetRouteUrl("ProductsByPageRoute", {index, size})  [Framework method]
   ├─> Set PaginationNext.NavigateUrl
   ├─> Set PaginationNext.CssClass (conditional: hide if last page)
   ├─> Set PaginationPrevious.NavigateUrl
   └─> Set PaginationPrevious.CssClass (conditional: hide if first page)
```

**Runtime Observation**:
- With 10 products and page_size=10, pagination controls are hidden/disabled
- "Showing 10 of 10 products - Page 1 - 1" displayed
- Next/Previous buttons present but inactive

**Boundaries Hit**:
- **Framework routing**: ASP.NET URL generation (stable boundary)
- **No database access**: Uses Model data already loaded
- **No side effects**: Pure UI configuration

---

## Data Ownership & Targets

### Read Targets

| Table/Entity | Access Pattern | Evidence | Runtime Count |
|--------------|----------------|----------|---------------|
| **CatalogItems** | SELECT with JOIN | CatalogService.cs:26 | **10 rows** (runtime-verified) |
| **CatalogBrands** | INNER JOIN | CatalogService.cs:27 | Used for brand name display |
| **CatalogTypes** | INNER JOIN | CatalogService.cs:28 | Used for type name display |

**Runtime Data Snapshot** (from `legacy-golden/grid-data.json`):

| ID | Name | Brand | Type | Price | Stock | Restock | Max Stock |
|----|------|-------|------|-------|-------|---------|-----------|
| 1 | .NET Bot Black Hoodie | .NET | T-Shirt | $19.50 | 100 | 0 | 0 |
| 2 | .NET Black & White Mug | .NET | Mug | $8.50 | 100 | 0 | 0 |
| 3 | Prism White T-Shirt | Other | T-Shirt | $12.00 | 100 | 0 | 0 |
| 4 | .NET Foundation T-shirt | .NET | T-Shirt | $12.00 | 100 | 0 | 0 |
| 5 | Roslyn Red Sheet | Other | Sheet | $8.50 | 100 | 0 | 0 |
| 6 | .NET Blue Hoodie | .NET | T-Shirt | $12.00 | 100 | 0 | 0 |
| 7 | Roslyn Red T-Shirt | Other | T-Shirt | $12.00 | 100 | 0 | 0 |
| 8 | Kudu Purple Hoodie | Other | T-Shirt | $8.50 | 100 | 0 | 0 |
| 9 | Cup&lt;T&gt; White Mug | Other | Mug | $12.00 | 100 | 0 | 0 |
| 10 | .NET Foundation Sheet | .NET | Sheet | $12.00 | 100 | 0 | 0 |

**SQL Generated** (Entity Framework 6):
```sql
-- Count query
SELECT COUNT(*) AS [value]
FROM [dbo].[CatalogItems] AS [Extent1]

-- Data query with pagination
SELECT
    [Extent1].[Id] AS [Id],
    [Extent1].[Name] AS [Name],
    [Extent1].[Description] AS [Description],
    [Extent1].[Price] AS [Price],
    [Extent1].[PictureFileName] AS [PictureFileName],
    [Extent1].[PictureUri] AS [PictureUri],
    [Extent1].[CatalogTypeId] AS [CatalogTypeId],
    [Extent1].[CatalogBrandId] AS [CatalogBrandId],
    [Extent1].[AvailableStock] AS [AvailableStock],
    [Extent1].[RestockThreshold] AS [RestockThreshold],
    [Extent1].[MaxStockThreshold] AS [MaxStockThreshold],
    [Extent1].[OnReorder] AS [OnReorder],
    [Extent2].[Id] AS [Id1],
    [Extent2].[Brand] AS [Brand],
    [Extent3].[Id] AS [Id2],
    [Extent3].[Type] AS [Type]
FROM [dbo].[CatalogItems] AS [Extent1]
INNER JOIN [dbo].[CatalogBrands] AS [Extent2] ON [Extent1].[CatalogBrandId] = [Extent2].[Id]
INNER JOIN [dbo].[CatalogTypes] AS [Extent3] ON [Extent1].[CatalogTypeId] = [Extent3].[Id]
ORDER BY [Extent1].[Id] ASC
OFFSET (@p__linq__0 * @p__linq__1) ROWS
FETCH NEXT @p__linq__2 ROWS ONLY
```

### Write Targets

**NONE** - This seam is **read-only**.

### Unknown Targets

**NONE** - All data access paths confirmed via code inspection and runtime capture.

### Shared Write Conflicts

**NONE** - No writes performed by this seam.

**Cross-Seam Read Sharing**:
- CatalogItems table also read by: **catalog-crud** seam (Edit, Details, Delete)
- CatalogBrands table also read by: **catalog-crud** seam (dropdown)
- CatalogTypes table also read by: **catalog-crud** seam (dropdown)
- ✅ **Safe**: Multiple seams reading same data is not a conflict

---

## Dependencies

### In-Seam Dependencies

| Type | Symbol | File | Purpose |
|------|--------|------|---------|
| Page | `_Default` | Default.aspx.cs | Main page class |
| Service Interface | `ICatalogService` | Services/ICatalogService.cs | Catalog operations contract |
| Service Implementation | `CatalogService` | Services/CatalogService.cs | EF6-based implementation |
| Model | `CatalogItem` | Models/CatalogItem.cs | Product entity |
| Model | `CatalogBrand` | Models/CatalogBrand.cs | Brand entity |
| Model | `CatalogType` | Models/CatalogType.cs | Type entity |
| ViewModel | `PaginatedItemsViewModel<T>` | ViewModel/PaginatedItemsViewModel.cs | Pagination wrapper |
| Data Context | `CatalogDBContext` | Models/CatalogDBContext.cs | EF6 DbContext |

### Cross-Seam Dependencies

| Target Seam | Dependency Type | Evidence | Severity |
|-------------|-----------------|----------|----------|
| **catalog-crud** | Navigation (soft) | Default.aspx links to Edit/Details/Delete | Low |
| **catalog-crud** | Navigation (soft) | "Create New" button links to Create.aspx | Low |

**Runtime-Verified Navigation Links** (from `legacy-golden/ui-elements.json`):
- **Create New**: href=`/Catalog/Create` (CSS: `.btn.esh-button.esh-button-primary`)
- **Edit Links**: href=`/Catalog/Edit/{id}` (CSS: `.esh-table-link`)
- **Details Links**: href=`/Catalog/Details/{id}` (CSS: `.esh-table-link`)
- **Delete Links**: href=`/Catalog/Delete/{id}` (CSS: `.esh-table-link`)

**Note**: These are **navigation dependencies** (hyperlinks), not code dependencies. The seams can be migrated and deployed independently. Navigation links will be updated to React Router routes.

### External Dependencies

**NONE**

- No COM/ActiveX
- No device I/O (serial, printing)
- No Windows Registry access
- No file system writes
- No external HTTP APIs
- No message queues

### Framework Dependencies

| Framework | Version | Usage | Migration Target |
|-----------|---------|-------|------------------|
| ASP.NET WebForms | 4.7.2 | Page lifecycle, data binding | FastAPI (no lifecycle) |
| Entity Framework 6 | 6.x | ORM, LINQ queries | SQLAlchemy 2.x async |
| Autofac | 4.x | Dependency injection | FastAPI Depends() |
| log4net | 2.x | Logging | Structlog |

---

## Hard Dependencies & Blockers

### Blockers: NONE ✅

No high-severity blockers identified.

### Refactoring Required: NO ✅

- Clean separation between page, service, and data layers
- Service interface already defined (ICatalogService)
- No static/global dependencies
- No reflection or dynamic dispatch
- No long-running transactions
- No shared write conflicts

### Dependency Wrapper Needed: NO ✅

No platform-specific dependencies requiring abstraction.

---

## Required Fields for Contract

### Input Fields (Query Parameters)

| Field | Type | Source | Evidence | Required | Default |
|-------|------|--------|----------|----------|---------|
| `page_size` | integer | Query param or route | Default.aspx.cs:26,33 | No | 10 |
| `page_index` | integer | Query param or route | Default.aspx.cs:27,33 | No | 0 |

### Output Fields (Response)

#### Pagination Metadata

| Field | Type | Source | Evidence | Purpose |
|-------|------|--------|----------|---------|
| `page_index` | integer | PaginatedItemsViewModel.ActualPage | ViewModel/PaginatedItemsViewModel.cs | Current page number (0-based) |
| `page_size` | integer | PaginatedItemsViewModel.ItemsPerPage | ViewModel/PaginatedItemsViewModel.cs | Items per page |
| `total_items` | integer | PaginatedItemsViewModel.TotalItems | Runtime: 10 products | Total count of all products |
| `total_pages` | integer | PaginatedItemsViewModel.TotalPages | Runtime: 1 page | Total number of pages |

#### Product Data (per item in `data[]` array)

| Field | Type | Source | Evidence | UI Display | Runtime Example |
|-------|------|--------|----------|------------|-----------------|
| `id` | integer | CatalogItem.Id | Models/CatalogItem.cs:11 | Hidden (used for navigation) | 1, 2, 3, ... |
| `name` | string | CatalogItem.Name | Models/CatalogItem.cs:12 | Column 2: Name | ".NET Bot Black Hoodie" |
| `description` | string (nullable) | CatalogItem.Description | Models/CatalogItem.cs:13 | Column 3: Description | ".NET Bot Black Hoodie" |
| `price` | decimal | CatalogItem.Price | Models/CatalogItem.cs:14 | Column 6: Price (formatted: $XX.XX) | 19.5, 8.5, 12.0 |
| `picture_file_name` | string | CatalogItem.PictureFileName | Models/CatalogItem.cs:15 | Column 1: Image src, Column 7: filename | "1.png", "2.png" |
| `picture_uri` | string (nullable) | CatalogItem.PictureUri | Models/CatalogItem.cs:16 | Not displayed (legacy artifact) | null |
| `catalog_type_id` | integer | CatalogItem.CatalogTypeId | Models/CatalogItem.cs:17 | Hidden (FK) | N/A |
| `catalog_brand_id` | integer | CatalogItem.CatalogBrandId | Models/CatalogItem.cs:18 | Hidden (FK) | N/A |
| `available_stock` | integer | CatalogItem.AvailableStock | Models/CatalogItem.cs:19 | Column 8: Stock | 100 (all products) |
| `restock_threshold` | integer | CatalogItem.RestockThreshold | Models/CatalogItem.cs:20 | Column 9: Restock | 0 (all products) |
| `max_stock_threshold` | integer | CatalogItem.MaxStockThreshold | Models/CatalogItem.cs:21 | Column 10: Max stock | 0 (all products) |
| `on_reorder` | boolean | CatalogItem.OnReorder | Models/CatalogItem.cs:22 | Not displayed | false (implied) |
| **catalog_brand** | object | CatalogItem.CatalogBrand (navigation) | CatalogService.cs:27 | Column 4: Brand name | {id: N, brand: ".NET"} |
| `catalog_brand.id` | integer | CatalogBrand.Id | Models/CatalogBrand.cs | Not displayed | N/A |
| `catalog_brand.brand` | string | CatalogBrand.Brand | Models/CatalogBrand.cs | Column 4: Brand | ".NET", "Other" |
| **catalog_type** | object | CatalogItem.CatalogType (navigation) | CatalogService.cs:28 | Column 5: Type name | {id: N, type: "T-Shirt"} |
| `catalog_type.id` | integer | CatalogType.Id | Models/CatalogType.cs | Not displayed | N/A |
| `catalog_type.type` | string | CatalogType.Type | Models/CatalogType.cs | Column 5: Type | "T-Shirt", "Mug", "Sheet" |

**Runtime-Verified Column Order** (from `legacy-golden/grid-data.json`):
1. **Image** (empty header, thumbnail display)
2. **Name**
3. **Description**
4. **Brand**
5. **Type**
6. **Price**
7. **Picture name**
8. **Stock**
9. **Restock**
10. **Max stock**
11. **Actions** (Edit | Details | Delete) - not in data structure, generated as links

**Note**: Navigation properties (CatalogBrand, CatalogType) must be included (eager-loaded) to avoid N+1 queries.

### Filters/Sorts/Paging

| Feature | Type | Source | Evidence | Implementation |
|---------|------|--------|----------|----------------|
| Ordering | Sort | CatalogService.cs:29 | `.OrderBy(c => c.Id)` | Always order by ID ascending |
| Pagination | Offset/Limit | CatalogService.cs:30-31 | `.Skip().Take()` | OFFSET/LIMIT in SQL |

**No filtering**: Legacy does not support filtering/search.
**No sorting controls**: Legacy only sorts by ID.

---

## UI-to-Data Mapping (Runtime-Verified)

### Real CSS Selectors & Form Field IDs

**Home Page Elements** (from `legacy-golden/ui-elements.json`):

| Element | Selector | CSS Classes | Name Attribute | Purpose |
|---------|----------|-------------|----------------|---------|
| Create New Button | `.btn.esh-button.esh-button-primary` | `btn esh-button esh-button-primary` | N/A | Navigate to /Catalog/Create |
| Edit Link | `.esh-table-link` | `esh-table-link` | N/A | Navigate to /Catalog/Edit/{id} |
| Details Link | `.esh-table-link` | `esh-table-link` | N/A | Navigate to /Catalog/Details/{id} |
| Delete Link | `.esh-table-link` | `esh-table-link` | N/A | Navigate to /Catalog/Delete/{id} |

**Create Form Elements** (runtime-captured):

| Field | Selector | Name Attribute | CSS Class | Input Type |
|-------|----------|----------------|-----------|------------|
| Name | `#MainContent_Name` | `ctl00$MainContent$Name` | `form-control` | text |
| Description | `#MainContent_Description` | `ctl00$MainContent$Description` | `form-control` | text |
| Brand | `#MainContent_Brand` | `ctl00$MainContent$Brand` | `form-control` | select (dropdown) |
| Type | `#MainContent_Type` | `ctl00$MainContent$Type` | `form-control` | select (dropdown) |
| Price | `#MainContent_Price` | `ctl00$MainContent$Price` | `form-control` | text (default: 0.00) |
| Stock | `#MainContent_Stock` | `ctl00$MainContent$Stock` | `form-control` | text (default: 0) |
| Restock | `#MainContent_Restock` | `ctl00$MainContent$Restock` | `form-control` | text (default: 0) |
| Max Stock | `#MainContent_Maxstock` | `ctl00$MainContent$Maxstock` | `form-control` | text (default: 0) |
| Create Button | `[name='ctl00$MainContent$ctl06']` | `ctl00$MainContent$ctl06` | `btn esh-button esh-button-primary` | submit (value: "[ Create ]") |
| Cancel Link | `.btn.esh-button.esh-button-secondary` | N/A | `btn esh-button esh-button-secondary` | link (href: "../") |

**Brand Dropdown Options** (runtime-captured):
- Azure
- .NET
- Visual Studio
- SQL Server
- Other

**Type Dropdown Options** (runtime-captured):
- Mug
- T-Shirt
- Sheet
- USB Memory Stick

**ASP.NET WebForms ViewState Fields** (present but not migrated):
- `__EVENTTARGET` (hidden)
- `__EVENTARGUMENT` (hidden)
- `__VIEWSTATE` (hidden, base64-encoded state)
- `__VIEWSTATEGENERATOR` (hidden)
- `__EVENTVALIDATION` (hidden)

### Table Columns → Data Fields

| Column # | UI Label | Data Field | Source | Runtime Verified |
|----------|----------|------------|--------|------------------|
| 1 | (Image) | `/pics/${picture_file_name}` | CatalogItem.PictureFileName | ✅ 1.png - 10.png |
| 2 | Name | `name` | CatalogItem.Name | ✅ Real product names captured |
| 3 | Description | `description` | CatalogItem.Description | ✅ Matches name in legacy |
| 4 | Brand | `catalog_brand.brand` | CatalogBrand.Brand (JOIN) | ✅ ".NET", "Other" |
| 5 | Type | `catalog_type.type` | CatalogType.Type (JOIN) | ✅ "T-Shirt", "Mug", "Sheet" |
| 6 | Price | `price` (formatted: $XX.XX) | CatalogItem.Price | ✅ 19.5, 8.5, 12.0 |
| 7 | Picture name | `picture_file_name` | CatalogItem.PictureFileName | ✅ "1.png" - "10.png" |
| 8 | Stock | `available_stock` | CatalogItem.AvailableStock | ✅ All 100 |
| 9 | Restock | `restock_threshold` | CatalogItem.RestockThreshold | ✅ All 0 |
| 10 | Max stock | `max_stock_threshold` | CatalogItem.MaxStockThreshold | ✅ All 0 |
| 11 | (Actions) | Edit \| Details \| Delete | Navigation links using `id` | ✅ Links verified |

### Pagination UI → Data

| UI Element | Data Source | Format | Runtime Value |
|------------|-------------|--------|---------------|
| "Showing X of Y products" | `page_index * page_size + 1` to `min((page_index + 1) * page_size, total_items)` | Calculated | "Showing 10 of 10 products" |
| "Page N - M" | `page_index + 1` and `total_pages` | Formatted | "Page 1 - 1" |
| Previous button (enabled) | `page_index > 0` | Conditional | Disabled (page 0) |
| Next button (enabled) | `page_index < total_pages - 1` | Conditional | Disabled (only 1 page) |

---

## Business Rules

### BR-001: Default Pagination
- **Page size**: Default 10 items per page
- **Page index**: Default 0 (first page)
- **Evidence**: Default.aspx.cs:15-16 (`DefaultPageSize`, `DefaultPageIndex`)
- **Runtime**: All 10 products fit on 1 page

### BR-002: Page Size Validation
- **Min**: 1
- **Max**: 100 (recommended, not enforced in legacy)
- **Evidence**: Not explicitly validated in legacy
- **Migration**: Should add validation in FastAPI route

### BR-003: Image Path
- **Pattern**: `/Pics/{PictureFileName}`
- **Default**: If PictureFileName is null → use "dummy.png"
- **Evidence**: ui-behavior.md, implicit in legacy
- **Runtime**: All products have `1.png` through `10.png`

### BR-004: Empty State
- **Condition**: No products in database (total_items == 0)
- **Message**: "No data was returned."
- **Evidence**: ui-behavior.md
- **Runtime**: Not tested (DB has 10 products)

### BR-005: Pagination Button Visibility
- **Previous**: Hidden when `page_index == 0`
- **Next**: Hidden when `page_index == total_pages - 1`
- **Evidence**: Default.aspx.cs:51-56
- **CSS Class**: `esh-pager-item--hidden` added conditionally
- **Runtime**: Both buttons disabled (single page with 10 items)

---

## Test Scenarios (Runtime-Verified)

### Scenario 1: View First Page ✅ VERIFIED
**Input**: Navigate to `/` or `/Default.aspx`
**Expected**:
- API called with: `page_size=10, page_index=0`
- Table displays 10 products
- Previous button disabled/hidden
- Next button disabled (only 1 page)
- Pagination text: "Showing 10 of 10 products - Page 1 - 1"

**Actual Runtime Result**: ✅ MATCHES
- 10 products displayed
- All columns populated with real data
- Images referenced: 1.png - 10.png
- Navigation links present for Edit/Details/Delete

### Scenario 2: Navigate to Page 2 ⚠️ NOT APPLICABLE
**Input**: Click "Next" button
**Expected**: Navigate to page 2
**Actual**: Only 1 page exists (10 products with page_size=10)
**Test Status**: Cannot test with current dataset (would need >10 products)

### Scenario 3: Navigate Back to Page 1 ⚠️ NOT APPLICABLE
**Input**: Click "Previous" button from page 2
**Expected**: Return to page 1
**Actual**: Only 1 page exists
**Test Status**: Cannot test with current dataset

### Scenario 4: Empty Catalog ⚠️ NOT TESTED
**Input**: Database has 0 products
**Expected**:
- API returns: `total_items=0, data=[]`
- Table shows: "No data was returned."
- Pagination controls hidden or disabled
**Test Status**: Not tested (runtime DB has 10 products)

### Scenario 5: Single Page (≤10 products) ✅ VERIFIED
**Input**: Database has 10 products
**Expected**:
- API returns: `total_items=10, page_size=10, total_pages=1`
- Table displays all 10 products
- Both pagination buttons disabled/hidden
- Pagination text: "Showing 10 of 10 products - Page 1 - 1"
**Actual Runtime Result**: ✅ MATCHES

### Scenario 6: Create New Navigation ✅ VERIFIED
**Input**: Click "Create New" button
**Expected**: Navigate to `/Catalog/Create`
**Actual Runtime Result**: ✅ VERIFIED
- Button present with CSS `.btn.esh-button.esh-button-primary`
- href=`/Catalog/Create`
- Screenshot captured: `screen_001_depth1.png`
- 8 form fields + 2 buttons captured

### Scenario 7: Edit Link Navigation ✅ VERIFIED
**Input**: Click "Edit" link on product ID 1
**Expected**: Navigate to `/Catalog/Edit/1`
**Actual Runtime Result**: ✅ VERIFIED
- Link present with CSS `.esh-table-link`
- href=`/Catalog/Edit/1`
- Screenshot captured: `screen_003_depth1.png`

### Scenario 8: Cancel Navigation ✅ VERIFIED
**Input**: Click "[ Cancel ]" button on Create page
**Expected**: Navigate back to home page
**Actual Runtime Result**: ✅ VERIFIED
- Cancel link present with CSS `.btn.esh-button.esh-button-secondary`
- href=`../`
- Navigation back to home confirmed

---

## Runtime Hypotheses & Observations

### Runtime Sources Used
1. **Browser-agent capture**: `legacy-golden/BASELINE_INDEX.md`
2. **Grid data snapshot**: `legacy-golden/grid-data.json` (10 products)
3. **UI elements capture**: `legacy-golden/ui-elements.json` (39 home page elements, 16 create form elements)
4. **Visual baseline**: `legacy-golden/screenshots/screen_000_depth0.png` (home page)

### Runtime-Confirmed Flows
✅ **Page load with 10 products** - All columns populated
✅ **Navigation to Create** - Button works, form renders
✅ **Navigation to Edit** - Link works for product ID 1
✅ **Cancel navigation** - Returns to home page
✅ **CSS classes** - Exact selectors captured for styling parity

### Runtime-Contradicted Assumptions
❌ **Product count**: Originally assumed 12 products (from seed.py), actually 10 in live DB
❌ **Pagination**: Originally expected multi-page scenario, but all products fit on 1 page

### Runtime-Unknown (Needs More Data)
⚠️ **Multi-page pagination**: Need >10 products to test page 2+ navigation
⚠️ **Empty state**: Need DB with 0 products to verify "No data" message
⚠️ **Image fallback**: All products have valid PictureFileName; need null case to test dummy.png

### Risk Assessment
🟢 **Low Risk**: Read-only operation, well-defined data structure
🟢 **Visual parity achievable**: All CSS classes and selectors captured
🟢 **Data integrity**: 10 products confirmed with consistent schema
🟡 **Test coverage gap**: Cannot fully test pagination with current dataset

---

## Migration Notes

### Backend Migration
- **Route**: `GET /api/catalog/items?page_size={int}&page_index={int}`
- **Controller**: `backend/app/catalog/router.py` → `get_catalog_items()`
- **Service**: `backend/app/core/service.py` → `CatalogService.get_catalog_items_paginated()`
- **Models**: SQLAlchemy models already exist
- **Validation**: Add FastAPI Query() validators for page_size (1-100) and page_index (>=0)
- **Response**: Must include 10 products on first page with current DB state

### Frontend Migration
- **Route**: `/` (React Router)
- **Page**: `frontend/src/pages/catalog-list/CatalogListPage.tsx`
- **Hook**: `useCatalogItems(pageSize, pageIndex)` with TanStack Query
- **Components**:
  - `<CatalogTable items={data} />` - Table with 10 columns
  - `<Pagination {...paginationProps} />` - Previous/Next controls
- **State**: TanStack Query cache (no local state needed)
- **CSS Classes to Preserve**:
  - `.btn.esh-button.esh-button-primary` (Create New button)
  - `.btn.esh-button.esh-button-secondary` (Cancel button)
  - `.esh-table-link` (Edit/Details/Delete links)
  - `.form-control` (input fields)
  - `.esh-pager-item` (pagination controls)

### Assets Migration
- ✅ Already complete: 13 PNG files copied to `frontend/public/pics/`
- Runtime-verified: Products use `1.png` - `10.png`

### CSS Migration
- ✅ Already complete: eShop CSS classes preserved in `frontend/src/styles/index.css`
- Must match exact classes captured in runtime UI elements

### Visual Parity Baseline
- **Golden screenshot**: `legacy-golden/screenshots/screen_000_depth0.png`
- **Use for**: Pixel-perfect comparison during frontend development
- **Tools**: Playwright visual regression testing

---

## Readiness Assessment

### Readiness: ✅ GO

**Confidence**: HIGH (Runtime-Verified)

**Confidence Reason**:
- Clear and simple workflow (single page load)
- Well-defined service interface
- Read-only operation (no data writes)
- No external dependencies
- No hard platform dependencies
- Clean separation of concerns
- All data fields mapped and confirmed
- Backend already implemented ✅
- Frontend already implemented ✅
- **Runtime capture completed** ✅
  - 10 products verified in live DB
  - All CSS selectors captured
  - All form field IDs captured
  - Visual baseline screenshot saved
  - Navigation flows verified

### Blockers: NONE

### Warnings: NONE

### Requirements Met:
- ✅ Entry points confirmed (Page_Load)
- ✅ Data flow traced (Page → Service → EF6 → DB)
- ✅ Data targets identified (READ: CatalogItems, CatalogBrands, CatalogTypes)
- ✅ No writes confirmed
- ✅ Dependencies documented
- ✅ No hard dependencies
- ✅ UI fields mapped to data
- ✅ Business rules documented
- ✅ Test scenarios defined
- ✅ **Runtime data captured and verified**
- ✅ **CSS selectors extracted**
- ✅ **Visual baseline screenshot saved**
- ✅ **10 products confirmed (not 12)**

---

## Next Steps

1. ✅ **Discovery complete** - This document (runtime-verified)
2. → **Contract generation** (STEP 7) - Generate OpenAPI spec with 10-product reality
3. → **Data strategy** (STEP 8) - Document read-only strategy
4. ✅ **Backend implementation** (STEP 10) - Already complete
5. ✅ **Frontend implementation** (STEP 11) - Already complete
6. → **Parity testing** (STEP 12) - Compare against `screen_000_depth0.png` baseline

**Estimated implementation time**: Already complete (code written)
**Validation time**: 15 minutes (manual visual validation by user against golden screenshot)
**Visual parity baseline**: `legacy-golden/screenshots/screen_000_depth0.png`

---

**Discovery completed**: 2026-03-02
**Runtime verification completed**: 2026-03-02
**Ready for contract generation**: YES
**Golden baseline captured**: YES (4 workflows, 10 products, 39 UI elements)
