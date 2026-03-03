# Seam Specification: Catalog List & Pagination

**Seam ID**: `catalog-list`
**Priority**: 1 (High)
**Complexity**: Medium
**Status**: Pending Discovery

---

## Purpose

Product catalog listing page displaying paginated products with thumbnail images, prices, stock information, and navigation to CRUD operations.

## Scope

### In-Scope
- Display paginated list of catalog items
- Show product thumbnail images from Pics folder
- Display product details in table format (Name, Description, Brand, Type, Price, Stock info)
- Pagination controls (Previous/Next, page counter)
- Navigation links to Edit, Details, Delete pages
- Create New button
- Preserve exact table layout and styling

### Out-of-Scope
- Product filtering/search (not in legacy)
- Sorting controls (not in legacy)
- Grid view vs List view toggle (not in legacy)

## Legacy Implementation

**Page**: `Default.aspx` + `Default.aspx.cs`
**Master Page**: `Site.Master`
**Route**: `/` (default page)

**Key Controls**:
- `productList` (ListView) - displays paginated catalog items
- `PaginationPrevious` (HyperLink) - previous page link
- `PaginationNext` (HyperLink) - next page link

**Data Binding**:
- Binds to `Model` of type `PaginatedItemsViewModel<CatalogItem>`
- Model properties used: `ItemsPerPage`, `TotalItems`, `ActualPage`, `TotalPages`, `Data`

## Dependencies

### Services
- `ICatalogService.GetCatalogItemsPaginated(pageSize, pageIndex)`

### Models
- `CatalogItem` (with navigation properties: CatalogBrand, CatalogType)
- `CatalogBrand`
- `CatalogType`
- `PaginatedItemsViewModel<T>`

### Cross-Seam Dependencies
- Links to **catalog-crud** seam (Edit, Details, Delete, Create pages)

## UI Layout

### Table Columns (in order)
1. Thumbnail image (from /Pics/{PictureFileName})
2. Name
3. Description
4. Brand (from CatalogBrand.Brand)
5. Type (from CatalogType.Type)
6. Price (currency formatted, class: esh-price)
7. Picture name (PictureFileName)
8. Stock (AvailableStock)
9. Restock (RestockThreshold)
10. Max stock (MaxStockThreshold)
11. Actions (Edit | Details | Delete links)

### Styling Classes
- `esh-table` - table wrapper div
- `esh-table-header` - table header row
- `esh-thumbnail` - product image
- `esh-price` - price display
- `esh-table-link` - action links
- `esh-button`, `esh-button-primary` - Create New button
- `esh-pager`, `esh-pager-wrapper`, `esh-pager-item` - pagination controls

## Business Rules

- **Page size**: 10 items per page (hardcoded default)
- **Image source**: `/Pics/{PictureFileName}` (static file serving)
- **Empty state**: Display "No data was returned." if no products
- **Pagination display**: "Showing X of Y products - Page N - M"
- **Default image**: If PictureFileName is null, use 'dummy.png'

## Migration Target

### Backend
- **Route**: `GET /api/catalog/items?page_size=10&page_index=0`
- **Response**: PaginatedItemsResponse DTO with items[], total_items, page_index, page_size, total_pages
- **Service**: CatalogService.get_catalog_items_paginated()
- **Database**: Query with JOIN to CatalogBrands and CatalogTypes, with OFFSET/LIMIT

### Frontend
- **Route**: `/` (React Router)
- **Page**: `frontend/src/pages/catalog-list/CatalogListPage.tsx`
- **Components**:
  - `CatalogTable` - product table
  - `CatalogRow` - single product row
  - `ProductThumbnail` - image component
  - `Pagination` - pagination controls
- **Hooks**: `useCatalogItems(pageSize, pageIndex)` with TanStack Query
- **Styling**: Copy CSS classes from Content/ or convert to Tailwind

### Assets
- **Images**: Copy all files from `Pics/*.png` to `frontend/public/pics/`
- **CSS**: Extract relevant styles from `Content/Site.css`

## Success Criteria

- [ ] Table displays all 10 columns in correct order
- [ ] Product images load from /pics/ folder
- [ ] Pagination works (Previous/Next buttons, page counter)
- [ ] Create New button navigates to /catalog/create
- [ ] Action links navigate to correct pages (/catalog/edit/{id}, etc.)
- [ ] Empty state displays when no products
- [ ] Styling matches legacy application
- [ ] Page loads in < 500ms
- [ ] Images are lazy-loaded or optimized

## Test Scenarios

1. **View first page of products**
   - Navigate to home page
   - Verify 10 products displayed
   - Verify all columns populated
   - Verify images load

2. **Navigate to next page**
   - Click "Next" button
   - Verify page 2 products displayed
   - Verify page counter updates

3. **Navigate to previous page**
   - Click "Previous" button
   - Verify returns to page 1

4. **Click action links**
   - Click "Edit" link on a product
   - Verify navigates to /catalog/edit/{id}
   - Repeat for Details and Delete

5. **Empty catalog**
   - Clear all products from database
   - Reload page
   - Verify "No data was returned." message displays

## Notes

- This is the entry point page for the application
- High priority for migration - demonstrates core functionality
- Images must be preserved and copied to new frontend
- Exact visual parity required
