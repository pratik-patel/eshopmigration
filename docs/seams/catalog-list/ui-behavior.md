# UI Behavior: Catalog List & Pagination

**Seam**: catalog-list
**Legacy Page**: Default.aspx + Default.aspx.cs
**Route**: `/` or `/Default.aspx` or `/Products/Page/{index}/Size/{size}`

---

## Page Layout

### Master Page
Inherits from `Site.Master` which provides:
- Site header with logo
- Navigation menu
- Content placeholder: `MainContent`
- Footer

### Main Content Structure

```
┌─────────────────────────────────────────────────────────┐
│ [Create New Button]                                     │
├─────────────────────────────────────────────────────────┤
│ Product Table                                           │
│ ┌───────┬──────┬─────────────┬───────┬──────┬─────┐   │
│ │ Image │ Name │ Description │ Brand │ Type │ ... │   │
│ ├───────┼──────┼─────────────┼───────┼──────┼─────┤   │
│ │ [img] │ .NET │ Desc text   │ MS    │ Cat  │ ... │   │
│ │ [img] │ Java │ Desc text   │ Oracle│ Cat  │ ... │   │
│ │  ...  │  ... │     ...     │  ...  │  ... │ ... │   │
│ └───────┴──────┴─────────────┴───────┴──────┴─────┘   │
├─────────────────────────────────────────────────────────┤
│ [< Previous]  Showing X of Y products - Page N - M     │
│                                            [Next >]      │
└─────────────────────────────────────────────────────────┘
```

## Controls Inventory

### Create New Button
- **Type**: Hyperlink button
- **Text**: "Create New"
- **CSS Classes**: `btn esh-button esh-button-primary`
- **Link**: Routes to `CreateProductRoute` (Catalog/Create page)
- **Position**: Top-left, above product table
- **Container**: `<p class="esh-link-wrapper">`

### Product List (ListView)
- **Control ID**: `productList`
- **Type**: `asp:ListView` (WebForms data-bound control)
- **Item Type**: `eShopLegacyWebForms.Models.CatalogItem`
- **Item Placeholder ID**: `itemPlaceHolder`
- **Data Binding**: Bound to `Model.Data` (list of CatalogItem)

#### Empty Data Template
```html
<table>
    <tr>
        <td>No data was returned.</td>
    </tr>
</table>
```

#### Layout Template
HTML `<table class="table">` with the following columns:

| # | Column Header | Width | Alignment |
|---|---------------|-------|-----------|
| 1 | (Image) | ~80px | Center |
| 2 | Name | Auto | Left |
| 3 | Description | Auto | Left |
| 4 | Brand | Auto | Left |
| 5 | Type | Auto | Left |
| 6 | Price | ~100px | Right |
| 7 | Picture name | ~150px | Left |
| 8 | Stock | ~80px | Right |
| 9 | Restock | ~80px | Right |
| 10 | Max stock | ~80px | Right |
| 11 | (Actions) | ~150px | Left |

CSS Class: `esh-table-header` on `<tr>` for header row

#### Item Template

**Row Structure** (each `<tr>`):

1. **Image Cell** (`<td>`)
   - `<image class="esh-thumbnail" src='/Pics/<%#:Item.PictureFileName%>' />`
   - Displays product thumbnail
   - Path: `/Pics/{PictureFileName}`
   - Dimensions: Constrained by CSS `.esh-thumbnail`

2. **Name Cell** (`<td>`)
   - `<p><%#:Item.Name%></p>`
   - Binds to CatalogItem.Name

3. **Description Cell** (`<td>`)
   - `<p><%#:Item.Description%></p>`
   - Binds to CatalogItem.Description

4. **Brand Cell** (`<td>`)
   - `<p><%#:Item.CatalogBrand.Brand%></p>`
   - Binds to navigation property CatalogBrand.Brand

5. **Type Cell** (`<td>`)
   - `<p><%#:Item.CatalogType.Type%></p>`
   - Binds to navigation property CatalogType.Type

6. **Price Cell** (`<td>`)
   - `<p><span class="esh-price"><%#:Item.Price%></span></p>`
   - Binds to CatalogItem.Price
   - Special CSS class `esh-price` for currency formatting/styling

7. **Picture Name Cell** (`<td>`)
   - `<p><%#:Item.PictureFileName%></p>`
   - Displays filename as text

8. **Stock Cell** (`<td>`)
   - `<p><%#:Item.AvailableStock%></p>`
   - Current inventory count

9. **Restock Cell** (`<td>`)
   - `<p><%#:Item.RestockThreshold%></p>`
   - Reorder threshold

10. **Max Stock Cell** (`<td>`)
    - `<p><%#:Item.MaxStockThreshold%></p>`
    - Maximum inventory limit

11. **Actions Cell** (`<td>`)
    - Three hyperlinks separated by "|":
    ```html
    <asp:HyperLink NavigateUrl='<%# GetRouteUrl("EditProductRoute", new {id =Item.Id}) %>'
                   runat="server" CssClass="esh-table-link">
        Edit
    </asp:HyperLink>
    |
    <asp:HyperLink NavigateUrl='<%# GetRouteUrl("ProductDetailsRoute", new {id =Item.Id}) %>'
                   runat="server" CssClass="esh-table-link">
        Details
    </asp:HyperLink>
    |
    <asp:HyperLink NavigateUrl='<%# GetRouteUrl("DeleteProductRoute", new {id =Item.Id}) %>'
                   runat="server" CssClass="esh-table-link">
        Delete
    </asp:HyperLink>
    ```
    - CSS Class: `esh-table-link`

### Pagination Controls

Container: `<div class="esh-pager">` → `<div class="container">` → `<article class="esh-pager-wrapper row">` → `<nav>`

#### Previous Link
- **Control ID**: `PaginationPrevious`
- **Type**: `asp:HyperLink`
- **Text**: "Previous"
- **CSS Classes**: `esh-pager-item esh-pager-item--navigable` (+ `esh-pager-item--hidden` when on first page)
- **NavigateUrl**: Routes to `ProductsByPageRoute` with `{index: ActualPage - 1, size: ItemsPerPage}`
- **Hidden when**: `ActualPage == 0`

#### Page Info Span
- **Type**: `<span class="esh-pager-item">`
- **Text Format**: `"Showing {ItemsPerPage} of {TotalItems} products - Page {ActualPage + 1} - {TotalPages}"`
- **Example**: "Showing 10 of 42 products - Page 1 - 5"
- **Data Binding**: Uses Model properties from code-behind

#### Next Link
- **Control ID**: `PaginationNext`
- **Type**: `asp:HyperLink`
- **Text**: "Next"
- **CSS Classes**: `esh-pager-item esh-pager-item--navigable` (+ `esh-pager-item--hidden` when on last page)
- **NavigateUrl**: Routes to `ProductsByPageRoute` with `{index: ActualPage + 1, size: ItemsPerPage}`
- **Hidden when**: `ActualPage >= TotalPages - 1`

## Code-Behind Logic (Default.aspx.cs)

### Constants
- `DefaultPageIndex = 0` (zero-based)
- `DefaultPageSize = 10`

### Page Load Event
```csharp
protected void Page_Load(object sender, EventArgs e)
{
    if (PaginationParamsAreSet()) // Check if size & index in route data
    {
        var size = Convert.ToInt32(Page.RouteData.Values["size"]);
        var index = Convert.ToInt32(Page.RouteData.Values["index"]);
        Model = CatalogService.GetCatalogItemsPaginated(size, index);
    }
    else
    {
        Model = CatalogService.GetCatalogItemsPaginated(DefaultPageSize, DefaultPageIndex);
    }

    productList.DataSource = Model.Data;
    productList.DataBind();
    ConfigurePagination();
}
```

**Flow**:
1. Check if pagination parameters (`size`, `index`) exist in route data
2. If yes: use those values; if no: use defaults (size=10, index=0)
3. Call `CatalogService.GetCatalogItemsPaginated(size, index)`
4. Assign result to `Model` property
5. Bind `Model.Data` to `productList` ListView
6. Configure pagination links (NavigateUrl and visibility)

### ConfigurePagination Method
```csharp
private void ConfigurePagination()
{
    // Next button
    PaginationNext.NavigateUrl = GetRouteUrl("ProductsByPageRoute",
        new { index = Model.ActualPage + 1, size = Model.ItemsPerPage });

    var pagerNextExtraStyles = Model.ActualPage < Model.TotalPages - 1 ? "" : " esh-pager-item--hidden";
    PaginationNext.CssClass = PaginationNext.CssClass + pagerNextExtraStyles;

    // Previous button
    PaginationPrevious.NavigateUrl = GetRouteUrl("ProductsByPageRoute",
        new { index = Model.ActualPage - 1, size = Model.ItemsPerPage });

    var pagerPreviousExtraStyles = Model.ActualPage > 0 ? "" : " esh-pager-item--hidden";
    PaginationPrevious.CssClass = PaginationPrevious.CssClass + pagerPreviousExtraStyles;
}
```

**Logic**:
- **Next button**: Hidden if on last page (`ActualPage >= TotalPages - 1`)
- **Previous button**: Hidden if on first page (`ActualPage == 0`)
- Both buttons get dynamic URLs with updated page index

## User Interactions

### View Page
1. User navigates to `/` (default route) or `/Products/Page/{index}/Size/{size}`
2. Page loads with 10 products (or specified page size)
3. Product images, details, and action links render
4. Pagination controls appear at bottom

### Click "Create New"
- Navigate to `/Catalog/Create` (Create product page)

### Click "Edit" Link
- Navigate to `/Catalog/Edit/{id}` where {id} is the product ID

### Click "Details" Link
- Navigate to `/Catalog/Details/{id}`

### Click "Delete" Link
- Navigate to `/Catalog/Delete/{id}`

### Click "Next" Pagination
- Navigate to next page: `index = currentIndex + 1`
- URL: `/Products/Page/{index+1}/Size/10`
- Page reloads with next set of products

### Click "Previous" Pagination
- Navigate to previous page: `index = currentIndex - 1`
- URL: `/Products/Page/{index-1}/Size/10`
- Page reloads with previous set of products

## Styling Classes

| Class | Applied To | Purpose |
|-------|------------|---------|
| `esh-table` | Outer div | Table container styling |
| `esh-link-wrapper` | Paragraph | Wraps Create New button |
| `esh-button` | Link | Button base styling |
| `esh-button-primary` | Link | Primary button styling (blue) |
| `table` | Table | Bootstrap table |
| `esh-table-header` | Table row | Header row styling |
| `esh-thumbnail` | Image | Product thumbnail sizing/styling |
| `esh-price` | Span | Price formatting/styling |
| `esh-table-link` | Hyperlink | Action link styling |
| `esh-pager` | Div | Pagination container |
| `esh-pager-wrapper` | Article | Pagination wrapper |
| `esh-pager-item` | Link/Span | Individual pager element |
| `esh-pager-item--navigable` | Link | Clickable pager link |
| `esh-pager-item--hidden` | Link | Hidden state (display: none) |

## Data Model

**Page Model**: `PaginatedItemsViewModel<CatalogItem>`

Properties used:
- `Data` (IEnumerable<CatalogItem>) - List of items for current page
- `ItemsPerPage` (int) - Page size (10)
- `TotalItems` (int) - Total count of all products
- `ActualPage` (int) - Current page index (zero-based)
- `TotalPages` (int) - Total number of pages

**CatalogItem Properties** (displayed):
- Id (int)
- Name (string)
- Description (string)
- Price (decimal)
- PictureFileName (string)
- AvailableStock (int)
- RestockThreshold (int)
- MaxStockThreshold (int)
- CatalogBrand (navigation property) → Brand (string)
- CatalogType (navigation property) → Type (string)

## Static Assets

### Product Images
**Source**: `Pics/*.png`
**Destination**: `frontend/public/pics/`
**Count**: 14 files
**Files**:
- `1.png` through `13.png` - Product images
- `dummy.png` - Default/fallback image

**Usage**:
- Referenced in catalog table: `<img src="/Pics/{PictureFileName}" />`
- CSS class: `esh-thumbnail`
- Binding: `Item.PictureFileName`
- Path template in React: `/pics/{pictureFileName}` (lowercase directory)

**Migration Action**: **CRITICAL - REQUIRED**
```bash
# Copy all product images
Copy-Item -Path "Pics\*.png" -Destination "frontend\public\pics\" -Recurse
```

### CSS Stylesheets
**Source**: `Content/Site.css`
**Destination**: `frontend/src/styles/catalog.css`

**Custom Classes Used** (esh-* prefix):
- `esh-table` - Table container div
- `esh-link-wrapper` - Button wrapper
- `esh-button` - Base button style
- `esh-button-primary` - Primary button variant
- `esh-table-header` - Table header row
- `esh-thumbnail` - Product image sizing
- `esh-price` - Price formatting
- `esh-table-link` - Action links
- `esh-pager` - Pagination container
- `esh-pager-wrapper` - Pagination wrapper
- `esh-pager-item` - Pager element
- `esh-pager-item--navigable` - Clickable pager
- `esh-pager-item--hidden` - Hidden pager state

**Migration Action**: **CRITICAL - REQUIRED**
1. Read `Content/Site.css`
2. Extract all `.esh-*` class definitions
3. Create `frontend/src/styles/eshop.css` with extracted styles
4. Import in React components: `import '@/styles/eshop.css'`

**Priority**: HIGH - Required for visual parity

### Framework CSS
**Source**: `Content/bootstrap.css`
**Action**: REPLACE with modern Bootstrap 5 or Tailwind CSS
**Do Not Copy**: Old Bootstrap 3.x CSS

### JavaScript Libraries
**Source**: `Scripts/jquery*.js`, `Scripts/bootstrap.js`
**Action**: DO NOT COPY - Not needed in React
**Notes**: All jQuery/Bootstrap JS functionality replaced by React state management

## Migration Notes for React

### Component Hierarchy
```
CatalogListPage
├── CreateNewButton
├── CatalogTable
│   ├── CatalogTableHeader
│   └── CatalogTableRow (repeated)
│       ├── ProductThumbnail
│       ├── ProductName
│       ├── ProductDescription
│       ├── ProductBrand
│       ├── ProductType
│       ├── ProductPrice
│       ├── ProductStock
│       └── ProductActions
│           ├── EditLink
│           ├── DetailsLink
│           └── DeleteLink
└── Pagination
    ├── PreviousButton
    ├── PageInfo
    └── NextButton
```

### React Router Routes
- `/` → CatalogListPage (default: page_index=0, page_size=10)
- `/?page={index}&size={size}` → CatalogListPage (with query params)

### TanStack Query Hook
```typescript
useCatalogItems(pageIndex: number, pageSize: number) {
  return useQuery({
    queryKey: ['catalog-items', pageIndex, pageSize],
    queryFn: () => fetchCatalogItems(pageIndex, pageSize),
    keepPreviousData: true, // Smooth pagination UX
  });
}
```

### State Management
- Page index: URL query param `?page={index}`
- Page size: URL query param `?size={size}` (default: 10)
- Current data: TanStack Query cache

### Styling
- Use Tailwind CSS or import legacy CSS classes from Content/Site.css
- Preserve exact class names for visual parity
- Ensure responsive table design

### Images
- Copy all files from `Pics/*.png` to `frontend/public/pics/`
- Image path in React: `/pics/{pictureFileName}`
- Use `<img>` with `loading="lazy"` for performance

### Pagination Logic
- Show/hide Previous: `pageIndex > 0`
- Show/hide Next: `pageIndex < totalPages - 1`
- Calculate total pages: `Math.ceil(totalItems / pageSize)`
- Display text: ``Showing ${pageSize} of ${totalItems} products - Page ${pageIndex + 1} - ${totalPages}``

## Asset Migration Checklist

- [ ] Copy `Pics/*.png` to `frontend/public/pics/` (14 files)
- [ ] Extract `.esh-*` CSS classes from `Content/Site.css`
- [ ] Create `frontend/src/styles/eshop.css` with extracted styles
- [ ] Verify image paths: `/Pics/{file}` → `/pics/{file}` (lowercase)
- [ ] Test dummy.png fallback for missing images
- [ ] Verify CSS class names match legacy exactly
- [ ] Test responsive behavior of table and pagination
- [ ] Validate thumbnail sizing with `.esh-thumbnail` class
- [ ] Compare visual output to legacy screenshot

## Test Scenarios (UI Behavior)

1. **Load default page (page 1)**
   - Verify 10 products displayed
   - Verify all columns populated
   - Verify Previous button hidden
   - Verify Next button visible (if > 10 products exist)

2. **Navigate to page 2**
   - Click Next
   - Verify URL changes to `/?page=1&size=10`
   - Verify different products displayed
   - Verify Previous button visible
   - Verify page counter shows "Page 2"

3. **Image rendering**
   - Verify each product shows thumbnail image
   - Verify images load from `/pics/` path
   - Verify broken images show dummy.png

4. **Action links**
   - Click Edit → navigates to `/catalog/edit/{id}`
   - Click Details → navigates to `/catalog/details/{id}`
   - Click Delete → navigates to `/catalog/delete/{id}`

5. **Empty state**
   - Remove all products from database
   - Reload page
   - Verify "No data was returned." message displays

6. **Pagination boundaries**
   - Navigate to last page
   - Verify Next button hidden
   - Navigate to first page
   - Verify Previous button hidden

7. **Styling preservation**
   - Compare screenshot of legacy page vs new React page
   - Verify table layout identical
   - Verify button styles match
   - Verify pagination styling matches

8. **Asset loading**
   - Verify all product images load without 404 errors
   - Verify CSS classes applied correctly
   - Verify no broken image links
   - Check browser console for missing asset errors
