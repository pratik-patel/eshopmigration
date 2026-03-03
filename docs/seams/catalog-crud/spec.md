# Seam Specification: Catalog CRUD Operations

**Seam ID**: `catalog-crud`
**Priority**: 2 (High)
**Complexity**: High
**Status**: Pending Discovery

---

## Purpose

Create, Edit, View Details, and Delete operations for catalog items with full form validation and database persistence.

## Scope

### In-Scope
- Create new catalog item with form validation
- Edit existing catalog item
- View catalog item details (read-only)
- Delete catalog item with confirmation
- Form field validation (client-side and server-side)
- Dropdown lists for Brand and Type selection
- Error message display
- Navigation back to catalog list

### Out-of-Scope
- Image upload functionality (legacy uses filename input only)
- Bulk operations
- Duplicate product detection

## Legacy Implementation

### Create Page
**Page**: `Catalog/Create.aspx` + `Catalog/Create.aspx.cs`
**Route**: `/Catalog/Create`
**Operation**: `ICatalogService.CreateCatalogItem(item)`

**Form Fields**:
- Name (TextBox, required)
- Description (TextBox)
- Price (TextBox, decimal validation, required)
- CatalogTypeId (DropDownList, required)
- CatalogBrandId (DropDownList, required)
- AvailableStock (TextBox, integer, default: 0)
- RestockThreshold (TextBox, integer, default: 0)
- MaxStockThreshold (TextBox, integer, default: 0)
- PictureFileName (TextBox, default: 'dummy.png')

### Edit Page
**Page**: `Catalog/Edit.aspx` + `Catalog/Edit.aspx.cs`
**Route**: `/Catalog/Edit/{id}`
**Operations**:
- Load: `ICatalogService.FindCatalogItem(id)`
- Save: `ICatalogService.UpdateCatalogItem(item)`

**Form Fields**: Same as Create, but pre-populated with existing data

### Details Page
**Page**: `Catalog/Details.aspx` + `Catalog/Details.aspx.cs`
**Route**: `/Catalog/Details/{id}`
**Operation**: `ICatalogService.FindCatalogItem(id)`

**Display**: Read-only view of all catalog item fields

### Delete Page
**Page**: `Catalog/Delete.aspx` + `Catalog/Delete.aspx.cs`
**Route**: `/Catalog/Delete/{id}`
**Operations**:
- Load: `ICatalogService.FindCatalogItem(id)`
- Delete: `ICatalogService.RemoveCatalogItem(item)`

**Display**: Read-only confirmation view with Delete button

## Dependencies

### Services
- `ICatalogService.FindCatalogItem(id)` - all pages
- `ICatalogService.CreateCatalogItem(item)` - Create
- `ICatalogService.UpdateCatalogItem(item)` - Edit
- `ICatalogService.RemoveCatalogItem(item)` - Delete
- `ICatalogService.GetCatalogBrands()` - Create, Edit (for dropdown)
- `ICatalogService.GetCatalogTypes()` - Create, Edit (for dropdown)

### Models
- `CatalogItem`
- `CatalogBrand`
- `CatalogType`

### Cross-Seam Dependencies
- Returns to **catalog-list** seam after Create/Edit/Delete operations

## Validation Rules (BR-001 to BR-006)

### Price Validation
- **Pattern**: `^\\d+(\\.\\d{0,2})*$`
- **Range**: 0 to 9999999999999999.99
- **Type**: decimal(18,2)
- **Error**: "The field Price must be a positive number with maximum two decimals."

### Stock Fields Validation
- **Fields**: AvailableStock, RestockThreshold, MaxStockThreshold
- **Range**: 0 to 10,000,000
- **Type**: int
- **Error**: "The field Stock must be between 0 and 10 million."

### Required Fields
- Name (required)
- Price (required)
- CatalogTypeId (required)
- CatalogBrandId (required)

### Default Values
- PictureFileName: 'dummy.png'
- AvailableStock: 0
- RestockThreshold: 0
- MaxStockThreshold: 0
- OnReorder: false

## UI Components

### Form Layout (Create/Edit)
```
[Name field]
[Description field]
[Price field]
[Type dropdown]
[Brand dropdown]
[Available Stock field]
[Restock Threshold field]
[Max Stock Threshold field]
[Picture Filename field]

[Create/Save Button] [Back to List Link]
```

### Details Layout
Read-only display of all fields in label-value pairs

### Delete Layout
Read-only display with confirmation:
- Display all item details
- Warning message: "Are you sure you want to delete this?"
- Delete button
- Back to List link

## Business Rules

- **BR-001 to BR-006**: See validation rules above
- **ID Generation**: New items get auto-generated ID (HiLo pattern in legacy)
- **Navigation**: After successful Create/Edit/Delete, redirect to catalog list
- **Error Handling**: Display validation errors inline next to fields
- **Concurrency**: No optimistic concurrency check in legacy (may be added in migration)

## Migration Target

### Backend Routes

1. **GET /api/catalog/items/{id}**
   - Fetch single item with Brand and Type joined
   - Used by Edit, Details, Delete pages

2. **POST /api/catalog/items**
   - Create new catalog item
   - Validate all fields
   - Return created item with ID

3. **PUT /api/catalog/items/{id}**
   - Update existing catalog item
   - Validate all fields
   - Return updated item

4. **DELETE /api/catalog/items/{id}**
   - Delete catalog item
   - Return success status

5. **GET /api/catalog/brands**
   - Get all brands for dropdown

6. **GET /api/catalog/types**
   - Get all types for dropdown

### Frontend Routes

1. **`/catalog/create`** → `CatalogCreatePage.tsx`
2. **`/catalog/edit/:id`** → `CatalogEditPage.tsx`
3. **`/catalog/details/:id`** → `CatalogDetailsPage.tsx`
4. **`/catalog/delete/:id`** → `CatalogDeletePage.tsx`

### React Components

- `CatalogForm` - reusable form component for Create/Edit
- `FormField` - individual field with validation display
- `FormDropdown` - dropdown with options
- `CatalogDetails` - read-only detail display
- `DeleteConfirmation` - delete confirmation UI

### React Hooks

- `useCatalogItem(id)` - fetch single item
- `useCreateCatalogItem()` - create mutation
- `useUpdateCatalogItem()` - update mutation
- `useDeleteCatalogItem()` - delete mutation
- `useCatalogBrands()` - fetch brands for dropdown
- `useCatalogTypes()` - fetch types for dropdown

### Validation

- **Client-side**: Zod schemas matching Pydantic models
- **Server-side**: Pydantic validators
- **Display**: Inline error messages below each field

## Success Criteria

- [ ] Create form validates all fields before submission
- [ ] Edit form pre-populates with existing data
- [ ] Details page displays all fields in read-only mode
- [ ] Delete page shows confirmation and executes delete
- [ ] Validation errors display inline with correct messages
- [ ] Dropdowns populate with database data
- [ ] Navigation works (Back to List, after save/delete)
- [ ] Form styling matches legacy application
- [ ] All validation rules preserved exactly

## Test Scenarios

1. **Create new product - happy path**
   - Navigate to /catalog/create
   - Fill all required fields with valid data
   - Click Create button
   - Verify redirects to catalog list
   - Verify new product appears in list

2. **Create with validation errors**
   - Leave required fields empty
   - Enter invalid price (e.g., "abc", "-5", "999.999")
   - Enter invalid stock (e.g., "20000000")
   - Verify error messages display
   - Verify form does not submit

3. **Edit existing product**
   - Click Edit link on a product
   - Verify form pre-populated
   - Change Name and Price
   - Click Save
   - Verify redirects to catalog list
   - Verify changes persisted

4. **View product details**
   - Click Details link on a product
   - Verify all fields displayed in read-only mode
   - Verify Back to List link works

5. **Delete product**
   - Click Delete link on a product
   - Verify confirmation page shows product details
   - Click Delete button
   - Verify redirects to catalog list
   - Verify product no longer in list

6. **Edit non-existent product**
   - Navigate to /catalog/edit/99999
   - Verify 404 or "Not Found" error

## Notes

- Form validation is critical - must match legacy exactly
- Validation error messages must be identical to legacy
- Dropdown population requires separate API calls
- Consider using shared CatalogForm component for Create and Edit
- Delete confirmation is a separate page (not a modal dialog in legacy)
