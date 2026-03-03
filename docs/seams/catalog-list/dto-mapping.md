# DTO Mapping: catalog-list

**Seam**: catalog-list
**Date**: 2026-03-02
**Status**: Runtime-Verified
**Source**: discovery.md (UPDATED with runtime data), grid-data.json, ui-elements.json

---

## Overview

This document maps legacy C# entities to OpenAPI DTOs for the catalog-list seam.

**Verification Status**: All field mappings confirmed through:
1. Code inspection (discovery.md)
2. Runtime capture (grid-data.json with 10 real products)
3. UI element capture (ui-elements.json with CSS selectors)
4. Visual baseline (screen_000_depth0.png)

---

## PaginatedItemsViewModel → PaginatedCatalogResponse

Maps the legacy pagination wrapper to the API response envelope.

| Legacy Field | C# Type | OpenAPI Field | JSON Type | Notes | Runtime Verified |
|--------------|---------|---------------|-----------|-------|------------------|
| `ActualPage` | int | `page_index` | integer | Zero-based page index | ✅ Value: 0 |
| `ItemsPerPage` | int | `page_size` | integer | Items per page | ✅ Value: 10 |
| `TotalItems` | long | `total_items` | integer | Total count across all pages | ✅ Value: 10 |
| `TotalPages` | int | `total_pages` | integer | Calculated: ceil(total_items / page_size) | ✅ Value: 1 |
| `Data` | List\<CatalogItem\> | `data` | array | Array of catalog items | ✅ 10 items |

**Legacy Source**: `ViewModel/PaginatedItemsViewModel.cs`

**Evidence**: discovery.md lines 336-341

**Runtime Observation**: With 10 products and page_size=10, all items fit on single page (total_pages=1).

---

## CatalogItem → CatalogItem DTO

Maps the EF6 entity to the API DTO, including navigation properties.

| Legacy Field | C# Type | OpenAPI Field | JSON Type | Notes | Runtime Verified |
|--------------|---------|---------------|-----------|-------|------------------|
| `Id` | int | `id` | integer | Primary key | ✅ Range: 1-10 |
| `Name` | string | `name` | string | Product name, max 255 chars | ✅ Real names captured |
| `Description` | string (nullable) | `description` | string (nullable) | Product description, max 1000 chars | ✅ Matches name in dataset |
| `Price` | decimal | `price` | number (decimal) | Price in USD, 2 decimal places | ✅ Values: 19.50, 8.50, 12.00 |
| `PictureFileName` | string | `picture_file_name` | string | Image filename (without path) | ✅ Pattern: "1.png" - "10.png" |
| `PictureUri` | string (nullable) | `picture_uri` | string (nullable) | Full image URI (legacy, unused) | ✅ Always null |
| `CatalogTypeId` | int | `catalog_type_id` | integer | FK to CatalogTypes | ✅ Values: 1, 2, 3 |
| `CatalogBrandId` | int | `catalog_brand_id` | integer | FK to CatalogBrands | ✅ Values: 2, 5 |
| `AvailableStock` | int | `available_stock` | integer | Current stock level | ✅ All 100 |
| `RestockThreshold` | int | `restock_threshold` | integer | Reorder trigger level | ✅ All 0 |
| `MaxStockThreshold` | int | `max_stock_threshold` | integer | Max stock capacity | ✅ All 0 |
| `OnReorder` | bool | `on_reorder` | boolean | Reorder status flag | ✅ All false |
| `CatalogBrand` (nav) | CatalogBrand | `catalog_brand` | object | Eager-loaded brand info | ✅ JOIN verified |
| `CatalogType` (nav) | CatalogType | `catalog_type` | object | Eager-loaded type info | ✅ JOIN verified |

**Legacy Source**: `Models/CatalogItem.cs` (lines 11-22 for properties)

**Eager Loading**: `CatalogService.cs:27-28`
```csharp
.Include(c => c.CatalogBrand)
.Include(c => c.CatalogType)
```

**Evidence**: discovery.md lines 345-378

**Runtime Examples**:
- Product 1: ".NET Bot Black Hoodie", $19.50, "1.png", 100 stock
- Product 2: ".NET Black & White Mug", $8.50, "2.png", 100 stock
- Product 9: "Cup\<T\> White Mug", $12.00, "9.png", 100 stock

---

## CatalogBrand → CatalogBrand DTO

Maps brand reference data.

| Legacy Field | C# Type | OpenAPI Field | JSON Type | Notes | Runtime Verified |
|--------------|---------|---------------|-----------|-------|------------------|
| `Id` | int | `id` | integer | Primary key | ✅ Values in use: 2, 5 |
| `Brand` | string | `brand` | string | Brand name, max 100 chars | ✅ ".NET", "Other" |

**Legacy Source**: `Models/CatalogBrand.cs`

**Evidence**: discovery.md lines 359-361

**Runtime Brands in Dataset**:
- ID 2: ".NET" (5 products)
- ID 5: "Other" (5 products)

**All Available Brands** (from ui-elements.json dropdown):
- Azure
- .NET
- Visual Studio
- SQL Server
- Other

---

## CatalogType → CatalogType DTO

Maps product type reference data.

| Legacy Field | C# Type | OpenAPI Field | JSON Type | Notes | Runtime Verified |
|--------------|---------|---------------|-----------|-------|------------------|
| `Id` | int | `id` | integer | Primary key | ✅ Values in use: 1, 2, 3 |
| `Type` | string | `type` | string | Type name, max 100 chars | ✅ "Mug", "T-Shirt", "Sheet" |

**Legacy Source**: `Models/CatalogType.cs`

**Evidence**: discovery.md lines 362-364

**Runtime Types in Dataset**:
- ID 1: "Mug" (2 products)
- ID 2: "T-Shirt" (6 products)
- ID 3: "Sheet" (2 products)

**All Available Types** (from ui-elements.json dropdown):
- Mug
- T-Shirt
- Sheet
- USB Memory Stick

---

## Unmapped Fields

**NONE**

All fields from the legacy `CatalogItem`, `CatalogBrand`, and `CatalogType` entities are mapped to the OpenAPI schema.

---

## Query Parameters

Maps legacy page load parameters to API query parameters.

| Legacy Parameter | Source | OpenAPI Parameter | Type | Default | Validation | Runtime Verified |
|------------------|--------|-------------------|------|---------|------------|------------------|
| `pageSize` | Route/constant | `page_size` | integer | 10 | 1-100 | ✅ Default: 10 |
| `pageIndex` | Route/constant | `page_index` | integer | 0 | ≥0 | ✅ Default: 0 |

**Legacy Source**: `Default.aspx.cs:15-16, 26-27`

**Constants**:
```csharp
private const int DefaultPageSize = 10;
private const int DefaultPageIndex = 0;
```

**Route Pattern**: `/Catalog/Page/{index}/{size}` (for pagination navigation)

**Evidence**: discovery.md lines 50-54

---

## UI Column Mapping

Maps table columns to DTO fields (runtime-verified).

| Column # | UI Label | DTO Field Path | Display Format | CSS Class | Runtime Verified |
|----------|----------|----------------|----------------|-----------|------------------|
| 1 | _(empty, image)_ | `data[].picture_file_name` | `<img src="/pics/{value}">` | `esh-thumbnail` | ✅ 1.png - 10.png |
| 2 | Name | `data[].name` | Plain text | - | ✅ Real names |
| 3 | Description | `data[].description` | Plain text | - | ✅ Matches name |
| 4 | Brand | `data[].catalog_brand.brand` | Plain text | - | ✅ ".NET", "Other" |
| 5 | Type | `data[].catalog_type.type` | Plain text | - | ✅ "T-Shirt", "Mug", "Sheet" |
| 6 | Price | `data[].price` | `${value.toFixed(2)}` | `esh-price` | ✅ 19.50, 8.50, 12.00 |
| 7 | Picture name | `data[].picture_file_name` | Plain text | - | ✅ "1.png" - "10.png" |
| 8 | Stock | `data[].available_stock` | Integer | - | ✅ All 100 |
| 9 | Restock | `data[].restock_threshold` | Integer | - | ✅ All 0 |
| 10 | Max stock | `data[].max_stock_threshold` | Integer | - | ✅ All 0 |
| 11 | _(Actions)_ | `data[].id` | Edit \| Details \| Delete links | `esh-table-link` | ✅ Links verified |

**Legacy Source**: `Default.aspx` (ItemTemplate)

**Evidence**: discovery.md lines 443-456

**Runtime Capture**: `legacy-golden/grid-data.json` (10 rows)

---

## Navigation Links

Maps action links to route parameters.

| Action | Legacy Route | OpenAPI Parameter | DTO Field | CSS Class | Runtime Verified |
|--------|--------------|-------------------|-----------|-----------|------------------|
| Edit | `/Catalog/Edit/{id}` | `id` | `data[].id` | `esh-table-link` | ✅ href="/Catalog/Edit/1" |
| Details | `/Catalog/Details/{id}` | `id` | `data[].id` | `esh-table-link` | ✅ href="/Catalog/Details/1" |
| Delete | `/Catalog/Delete/{id}` | `id` | `data[].id` | `esh-table-link` | ✅ href="/Catalog/Delete/1" |
| Create | `/Catalog/Create` | - | - | `esh-button-primary` | ✅ href="/Catalog/Create" |

**Evidence**: discovery.md lines 272-276

**Runtime Capture**: `legacy-golden/ui-elements.json` (CSS selectors and hrefs)

---

## Type Conversions

| Legacy C# Type | OpenAPI Type | JSON Type | Notes |
|----------------|--------------|-----------|-------|
| `int` | `integer` | number | 32-bit signed integer |
| `long` | `integer` | number | Used for TotalItems (count query) |
| `decimal` | `number (decimal)` | number | Precision: 2 decimal places for price |
| `string` | `string` | string | UTF-8 encoded |
| `string?` (nullable) | `string` (nullable: true) | string or null | Explicit null handling |
| `bool` | `boolean` | boolean | true/false |
| `List<T>` | `array` (items: $ref) | array | Typed array with schema reference |
| `CatalogBrand` (nav) | `object` ($ref: CatalogBrand) | object | Nested object via reference |
| `CatalogType` (nav) | `object` ($ref: CatalogType) | object | Nested object via reference |

**Migration Notes**:
- **decimal → number**: Python decimal.Decimal serialized as JSON number
- **nullable strings**: Pydantic Optional[str] with `nullable: true` in OpenAPI
- **navigation properties**: Always included (eager-loaded), never null in response

---

## Pagination UI Mapping

Maps UI pagination elements to DTO fields.

| UI Element | Calculation/Source | DTO Fields Used | Runtime Verified |
|------------|-------------------|-----------------|------------------|
| "Showing X of Y products" | `X = page_index * page_size + 1`<br>`Y = total_items` | `page_index`, `page_size`, `total_items` | ✅ "Showing 10 of 10" |
| "Page N - M" | `N = page_index + 1`<br>`M = total_pages` | `page_index`, `total_pages` | ✅ "Page 1 - 1" |
| Previous button enabled | `page_index > 0` | `page_index` | ✅ Disabled (page 0) |
| Next button enabled | `page_index < total_pages - 1` | `page_index`, `total_pages` | ✅ Disabled (only 1 page) |

**Legacy Source**: `Default.aspx.cs:48-56` (ConfigurePagination method)

**Evidence**: discovery.md lines 458-464

**CSS Classes** (runtime-verified):
- `.esh-pager` (pagination wrapper)
- `.esh-pager-item` (individual button/link)
- `.esh-pager-item--hidden` (hidden state, applied conditionally)

---

## Business Rules Mapping

| Rule ID | Rule Description | DTO Fields Enforced | Validation Location | Runtime Verified |
|---------|------------------|---------------------|---------------------|------------------|
| BR-001 | Default pagination: 10 items per page, page 0 | `page_size=10`, `page_index=0` | FastAPI Query() defaults | ✅ Defaults work |
| BR-002 | Page size validation: 1-100 | `page_size` | FastAPI Query(ge=1, le=100) | ✅ Contract specifies |
| BR-003 | Image path: /pics/{picture_file_name} or dummy.png | `picture_file_name` | Frontend image component | ✅ All have valid filenames |
| BR-004 | Empty state: "No data was returned." | `total_items=0`, `data=[]` | Frontend conditional render | ⚠️ Not tested (DB has 10 products) |
| BR-005 | Pagination button visibility | `page_index`, `total_pages` | Frontend conditional CSS classes | ✅ Both buttons disabled |

**Evidence**: discovery.md lines 469-500

---

## Runtime Data Summary

**Total Products**: 10 (verified from grid-data.json)

**Product ID Range**: 1-10

**Price Range**: $8.50 - $19.50

**Image Files**: 1.png - 10.png (all present in /pics/)

**Brands in Use**: .NET (5 products), Other (5 products)

**Types in Use**: T-Shirt (6 products), Mug (2 products), Sheet (2 products)

**Stock Levels**: All products have 100 units

**Reorder Settings**: All products have 0 threshold and 0 max (no limits configured)

**Pagination State**: Single page (10 items ÷ 10 per page = 1 page)

---

## Validation Rules

### Request Validation (FastAPI)

```python
from pydantic import Field, conint

page_size: conint(ge=1, le=100) = 10  # Default 10, range 1-100
page_index: conint(ge=0) = 0          # Default 0, minimum 0
```

### Response Validation (Pydantic)

```python
from pydantic import BaseModel, Field
from decimal import Decimal

class CatalogItem(BaseModel):
    id: int = Field(..., ge=1)
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1000)
    price: Decimal = Field(..., ge=0, decimal_places=2)
    picture_file_name: str = Field(..., max_length=255)
    # ... etc
```

---

## Migration Notes

### Backend (Python/FastAPI)

1. **SQLAlchemy Models**: Already exist, match legacy schema
2. **Eager Loading**: Use `.options(joinedload(CatalogItem.catalog_brand), joinedload(CatalogItem.catalog_type))`
3. **Ordering**: Always `.order_by(CatalogItem.id.asc())`
4. **Pagination**: Use `.offset()` and `.limit()`
5. **Count Query**: Separate `SELECT COUNT(*)` query for total_items

### Frontend (React/TypeScript)

1. **Types**: Generate from OpenAPI using `openapi-typescript`
2. **Data Fetching**: TanStack Query with `useCatalogItems(pageSize, pageIndex)` hook
3. **Image Path**: Construct as `/pics/${item.picture_file_name}`
4. **Price Format**: Use `Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' })`
5. **Pagination UI**: Calculate "Showing X of Y" client-side
6. **CSS Classes**: Preserve exact classes from ui-elements.json for visual parity

---

## Traceability Matrix

| OpenAPI Schema | Legacy Source File | Legacy Symbol | Discovery Evidence Line | Runtime Evidence |
|----------------|-------------------|---------------|-------------------------|------------------|
| `PaginatedCatalogResponse` | ViewModel/PaginatedItemsViewModel.cs | PaginatedItemsViewModel<T> | 336-341 | grid-data.json (1 page) |
| `CatalogItem` | Models/CatalogItem.cs | CatalogItem | 345-378 | grid-data.json (10 items) |
| `CatalogBrand` | Models/CatalogBrand.cs | CatalogBrand | 359-361 | grid-data.json (brand values) |
| `CatalogType` | Models/CatalogType.cs | CatalogType | 362-364 | grid-data.json (type values) |
| `GET /api/catalog/items` | Default.aspx.cs | _Default.Page_Load | 22-41 | BASELINE_INDEX.md (workflow 0) |
| `page_size` parameter | Default.aspx.cs | DefaultPageSize | 15 | grid-data.json (10 items) |
| `page_index` parameter | Default.aspx.cs | DefaultPageIndex | 16 | grid-data.json (page 0) |

---

## Confidence Assessment

**Mapping Confidence**: HIGH

**Reasons**:
- ✅ All fields traced to source code
- ✅ All fields verified in runtime capture (10 real products)
- ✅ Navigation properties confirmed via SQL JOIN evidence
- ✅ UI column order verified via grid-data.json headers
- ✅ CSS classes captured via ui-elements.json
- ✅ Visual baseline screenshot available for comparison
- ✅ No invented fields (all evidence-based)
- ✅ No dropped fields (complete mapping)

**Gaps**:
- ⚠️ Empty state (total_items=0) not tested with runtime data
- ⚠️ Multi-page pagination not testable (only 10 products exist)
- ⚠️ Image fallback (dummy.png) not tested (all products have valid filenames)

**Recommendation**: **APPROVED** for contract generation and implementation. Gaps are edge cases that can be tested later with modified data.

---

**Document Version**: 1.0 (Runtime-Verified)
**Last Updated**: 2026-03-02
**Next Review**: After parity testing with visual baseline
