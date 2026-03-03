# Discovery Report: catalog-list

**Seam ID**: catalog-list
**Date**: 2026-03-02
**Status**: Discovery Complete
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
   ├─> ItemsPerPage: pageSize
   ├─> TotalItems: totalItems (from LongCount)
   ├─> ActualPage: pageIndex
   ├─> TotalPages: calculated
   └─> Data: List<CatalogItem> with navigation properties populated
```

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

**Boundaries Hit**:
- **Framework routing**: ASP.NET URL generation (stable boundary)
- **No database access**: Uses Model data already loaded
- **No side effects**: Pure UI configuration

---

## Data Ownership & Targets

### Read Targets

| Table/Entity | Access Pattern | Evidence | Purpose |
|--------------|----------------|----------|---------|
| **CatalogItems** | SELECT with JOIN | CatalogService.cs:26 | Fetch paginated products |
| **CatalogBrands** | INNER JOIN | CatalogService.cs:27 | Get brand name for display |
| **CatalogTypes** | INNER JOIN | CatalogService.cs:28 | Get type name for display |

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

**NONE** - All data access paths confirmed via code inspection.

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
| `total_items` | integer | PaginatedItemsViewModel.TotalItems | ViewModel/PaginatedItemsViewModel.cs | Total count of all products |
| `total_pages` | integer | PaginatedItemsViewModel.TotalPages | ViewModel/PaginatedItemsViewModel.cs | Total number of pages |

#### Product Data (per item in `data[]` array)

| Field | Type | Source | Evidence | UI Display |
|-------|------|--------|----------|------------|
| `id` | integer | CatalogItem.Id | Models/CatalogItem.cs:11 | Hidden (used for navigation) |
| `name` | string | CatalogItem.Name | Models/CatalogItem.cs:12 | Column 2: Name |
| `description` | string (nullable) | CatalogItem.Description | Models/CatalogItem.cs:13 | Column 3: Description |
| `price` | decimal | CatalogItem.Price | Models/CatalogItem.cs:14 | Column 6: Price (formatted: $XX.XX) |
| `picture_file_name` | string | CatalogItem.PictureFileName | Models/CatalogItem.cs:15 | Column 1: Image src, Column 7: filename |
| `picture_uri` | string (nullable) | CatalogItem.PictureUri | Models/CatalogItem.cs:16 | Not displayed (legacy artifact) |
| `catalog_type_id` | integer | CatalogItem.CatalogTypeId | Models/CatalogItem.cs:17 | Hidden (FK) |
| `catalog_brand_id` | integer | CatalogItem.CatalogBrandId | Models/CatalogItem.cs:18 | Hidden (FK) |
| `available_stock` | integer | CatalogItem.AvailableStock | Models/CatalogItem.cs:19 | Column 8: Stock |
| `restock_threshold` | integer | CatalogItem.RestockThreshold | Models/CatalogItem.cs:20 | Column 9: Restock |
| `max_stock_threshold` | integer | CatalogItem.MaxStockThreshold | Models/CatalogItem.cs:21 | Column 10: Max stock |
| `on_reorder` | boolean | CatalogItem.OnReorder | Models/CatalogItem.cs:22 | Not displayed |
| **catalog_brand** | object | CatalogItem.CatalogBrand (navigation) | CatalogService.cs:27 | Column 4: Brand name |
| `catalog_brand.id` | integer | CatalogBrand.Id | Models/CatalogBrand.cs | Not displayed |
| `catalog_brand.brand` | string | CatalogBrand.Brand | Models/CatalogBrand.cs | Column 4: Brand |
| **catalog_type** | object | CatalogItem.CatalogType (navigation) | CatalogService.cs:28 | Column 5: Type name |
| `catalog_type.id` | integer | CatalogType.Id | Models/CatalogType.cs | Not displayed |
| `catalog_type.type` | string | CatalogType.Type | Models/CatalogType.cs | Column 5: Type |

**Note**: Navigation properties (CatalogBrand, CatalogType) must be included (eager-loaded) to avoid N+1 queries.

### Filters/Sorts/Paging

| Feature | Type | Source | Evidence | Implementation |
|---------|------|--------|----------|----------------|
| Ordering | Sort | CatalogService.cs:29 | `.OrderBy(c => c.Id)` | Always order by ID ascending |
| Pagination | Offset/Limit | CatalogService.cs:30-31 | `.Skip().Take()` | OFFSET/LIMIT in SQL |

**No filtering**: Legacy does not support filtering/search.
**No sorting controls**: Legacy only sorts by ID.

---

## UI-to-Data Mapping

### Table Columns → Data Fields

| Column # | UI Label | Data Field | Source |
|----------|----------|------------|--------|
| 1 | (Image) | `/pics/${picture_file_name}` | CatalogItem.PictureFileName |
| 2 | Name | `name` | CatalogItem.Name |
| 3 | Description | `description` | CatalogItem.Description |
| 4 | Brand | `catalog_brand.brand` | CatalogBrand.Brand (JOIN) |
| 5 | Type | `catalog_type.type` | CatalogType.Type (JOIN) |
| 6 | Price | `price` (formatted: $XX.XX) | CatalogItem.Price |
| 7 | Picture name | `picture_file_name` | CatalogItem.PictureFileName |
| 8 | Stock | `available_stock` | CatalogItem.AvailableStock |
| 9 | Restock | `restock_threshold` | CatalogItem.RestockThreshold |
| 10 | Max stock | `max_stock_threshold` | CatalogItem.MaxStockThreshold |
| 11 | (Actions) | Edit \| Details \| Delete | Navigation links using `id` |

### Pagination UI → Data

| UI Element | Data Source | Format |
|------------|-------------|--------|
| "Showing X of Y products" | `page_index * page_size + 1` to `min((page_index + 1) * page_size, total_items)` | Calculated |
| "Page N - M" | `page_index + 1` and `total_pages` | Formatted |
| Previous button (enabled) | `page_index > 0` | Conditional |
| Next button (enabled) | `page_index < total_pages - 1` | Conditional |

---

## Business Rules

### BR-001: Default Pagination
- **Page size**: Default 10 items per page
- **Page index**: Default 0 (first page)
- **Evidence**: Default.aspx.cs:15-16 (`DefaultPageSize`, `DefaultPageIndex`)

### BR-002: Page Size Validation
- **Min**: 1
- **Max**: 100 (recommended, not enforced in legacy)
- **Evidence**: Not explicitly validated in legacy
- **Migration**: Should add validation in FastAPI route

### BR-003: Image Path
- **Pattern**: `/Pics/{PictureFileName}`
- **Default**: If PictureFileName is null → use "dummy.png"
- **Evidence**: ui-behavior.md, implicit in legacy

### BR-004: Empty State
- **Condition**: No products in database (total_items == 0)
- **Message**: "No data was returned."
- **Evidence**: ui-behavior.md

### BR-005: Pagination Button Visibility
- **Previous**: Hidden when `page_index == 0`
- **Next**: Hidden when `page_index == total_pages - 1`
- **Evidence**: Default.aspx.cs:51-56
- **CSS Class**: `esh-pager-item--hidden` added conditionally

---

## Test Scenarios

### Scenario 1: View First Page
**Input**: Navigate to `/` or `/Default.aspx`
**Expected**:
- API called with: `page_size=10, page_index=0`
- Table displays first 10 products (IDs 1-10)
- Previous button disabled/hidden
- Next button enabled (if more than 10 total products)
- Pagination text: "Showing 1 to 10 of 12 products - Page 1 - 2"

### Scenario 2: Navigate to Page 2
**Input**: Click "Next" button
**Expected**:
- API called with: `page_size=10, page_index=1`
- Table displays products 11-12
- Previous button enabled
- Next button disabled/hidden
- Pagination text: "Showing 11 to 12 of 12 products - Page 2 - 2"

### Scenario 3: Navigate Back to Page 1
**Input**: Click "Previous" button from page 2
**Expected**:
- API called with: `page_size=10, page_index=0`
- Table displays first 10 products
- State returns to Scenario 1

### Scenario 4: Empty Catalog
**Input**: Database has 0 products
**Expected**:
- API returns: `total_items=0, data=[]`
- Table shows: "No data was returned."
- Pagination controls hidden or disabled

### Scenario 5: Single Page (≤10 products)
**Input**: Database has 5 products
**Expected**:
- API returns: `total_items=5, page_size=10, total_pages=1`
- Table displays all 5 products
- Both pagination buttons disabled/hidden
- Pagination text: "Showing 1 to 5 of 5 products - Page 1 - 1"

---

## Migration Notes

### Backend Migration
- **Route**: `GET /api/catalog/items?page_size={int}&page_index={int}`
- **Controller**: `backend/app/catalog/router.py` → `get_catalog_items()`
- **Service**: `backend/app/core/service.py` → `CatalogService.get_catalog_items_paginated()`
- **Models**: SQLAlchemy models already exist
- **Validation**: Add FastAPI Query() validators for page_size (1-100) and page_index (>=0)

### Frontend Migration
- **Route**: `/` (React Router)
- **Page**: `frontend/src/pages/catalog-list/CatalogListPage.tsx`
- **Hook**: `useCatalogItems(pageSize, pageIndex)` with TanStack Query
- **Components**:
  - `<CatalogTable items={data} />` - Table with 10 columns
  - `<Pagination {...paginationProps} />` - Previous/Next controls
- **State**: TanStack Query cache (no local state needed)

### Assets Migration
- ✅ Already complete: 13 PNG files copied to `frontend/public/pics/`

### CSS Migration
- ✅ Already complete: eShop CSS classes preserved in `frontend/src/styles/index.css`

---

## Readiness Assessment

### Readiness: ✅ GO

**Confidence**: HIGH

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

---

## Next Steps

1. ✅ **Discovery complete** - This document
2. → **Contract generation** (STEP 7) - Generate OpenAPI spec
3. → **Data strategy** (STEP 8) - Document read-only strategy
4. ✅ **Backend implementation** (STEP 10) - Already complete
5. ✅ **Frontend implementation** (STEP 11) - Already complete
6. → **Parity testing** (STEP 12) - Generate parity tests (optional)

**Estimated implementation time**: Already complete (code written)
**Validation time**: 15 minutes (manual visual validation by user)

---

**Discovery completed**: 2026-03-02
**Ready for contract generation**: YES
