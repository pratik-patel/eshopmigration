# Discovery Report: catalog-management

**Extraction Date**: 2026-03-03T00:00:00Z
**Status**: GO
**Confidence**: High

---

## Seam Summary

**Purpose**: Product catalog management (browse, CRUD, image upload)

**Boundaries**:
- **In-Scope**:
  - Catalog item list with pagination
  - Create new catalog items
  - Edit existing catalog items
  - Delete catalog items (with confirmation)
  - View catalog item details
  - Image upload for catalog items
  - Brand and Type lookup lists

- **Out-of-Scope**:
  - Order management
  - Shopping cart
  - User management (authentication handled by Azure AD)

**Assumptions**:
- Database schema remains unchanged (Catalog, CatalogBrand, CatalogType tables)
- Image storage pattern will be preserved (file system or cloud storage)
- Authentication will migrate from OpenID Connect to JWT-based auth
- Pagination defaults (pageSize=10, pageIndex=0) will be preserved

---

## Verified UI Triggers

| Screen | Control | Event | Handler | File | Confidence |
|--------|---------|-------|---------|------|------------|
| Default.aspx | CreateNewLink | Click | Navigate to Create.aspx | Client-side routing | high |
| Default.aspx | PaginationNext | Click | Navigate to next page | Client-side routing | high |
| Default.aspx | PaginationPrevious | Click | Navigate to previous page | Client-side routing | high |
| Create.aspx | CreateButton | Click | Create_Click | Catalog/Create.aspx.cs:50 | high |
| Create.aspx | CancelButton | Click | Navigate to Default.aspx | Client-side link | high |
| Create.aspx | uploadEditorImage | change | Client-side upload | JavaScript (not in evidence) | medium |
| Edit.aspx | SaveButton | Click | Save_Click | Catalog/Edit.aspx.cs:62 | high |
| Edit.aspx | CancelButton | Click | Navigate to Default.aspx | Client-side link | high |
| Edit.aspx | uploadEditorImage | change | Client-side upload | JavaScript (not in evidence) | medium |
| Delete.aspx | DeleteButton | Click | Delete_Click | Catalog/Delete.aspx.cs:34 | high |
| Delete.aspx | CancelButton | Click | Navigate to Default.aspx | Client-side link | high |
| Details.aspx | BackToListButton | Click | Navigate to Default.aspx | Client-side link | high |
| Details.aspx | EditButton | Click | Navigate to Edit.aspx | Client-side link | high |

---

## Verified Flows

### Flow 1: List Catalog Items (Default.aspx Page Load)

**Call Chain**:
1. `Default.aspx.cs:Page_Load()` → Entry point
2. `Default.aspx.cs:35` → `CatalogService.GetCatalogItemsPaginated(size, index)`
3. `CatalogService.cs:20` → `GetCatalogItemsPaginated(pageSize, pageIndex)`
4. `CatalogService.cs:22` → `db.CatalogItems.LongCount()` (get total count)
5. `CatalogService.cs:24-30` → `db.CatalogItems.Include(CatalogBrand).Include(CatalogType).OrderBy(Id).Skip().Take()`
6. **Boundary**: Database read

**Side Effects**:
- Reads: `Catalog` table (all columns)
- Reads: `CatalogBrand` table (Id, Brand) via JOIN
- Reads: `CatalogType` table (Id, Type) via JOIN
- Writes: None

**Business Rules** (extracted from code):
- Default page size: 10 items (constant `DefaultPageSize`)
- Default page index: 0 (constant `DefaultPageIndex`)
- Sort order: By `Id` ascending (line 27)
- Eager loading: Always include `CatalogBrand` and `CatalogType` relations
- Pagination calculation: `Skip(pageSize * pageIndex).Take(pageSize)`
- Image URI construction: Delegated to `ImageService.BuildUrlImage()` (line 70)

**Evidence**:
- `Default.aspx.cs:16-17` (constants)
- `Default.aspx.cs:31-40` (pagination logic)
- `CatalogService.cs:20-34` (query execution)

---

### Flow 2: Create Catalog Item (Create.aspx Create_Click)

**Call Chain**:
1. `Create.aspx.cs:50` → `Create_Click()` event handler
2. `Create.aspx.cs:52` → `ModelState.IsValid` validation check
3. `Create.aspx.cs:54-65` → Construct `CatalogItem` from form inputs
4. `Create.aspx.cs:67-71` → Extract filename from `TempImageName` if present
5. `Create.aspx.cs:73` → `CatalogService.CreateCatalogItem(catalogItem)`
6. `CatalogService.cs:52` → `indexGenerator.GetNextSequenceValue(db)` (HiLo ID generation)
7. `CatalogService.cs:53` → `db.CatalogItems.Add(catalogItem)`
8. `CatalogService.cs:54` → `db.SaveChanges()` (commit transaction)
9. `Create.aspx.cs:75-78` → `ImageService.UpdateImage(catalogItem)` if image uploaded
10. `Create.aspx.cs:80` → `Response.Redirect("~")` (return to list)
11. **Boundary**: Database write, file I/O

**Side Effects**:
- Writes: `INSERT INTO Catalog` with all fields
- Writes: Image file copy (if uploaded) to `~/Pics/` or Azure Blob

**Business Rules** (extracted from code):
- Name: Required, MaxLength 50 (model validation)
- Description: Optional (no validation)
- Price: Required, Range 0-9999999999999999.99, Currency format, 2 decimals max (model annotation)
- Stock fields: Range 0-10000000 (model annotation)
- Brand and Type: Required (dropdown selection, FK constraint)
- Image: Optional, defaults to "dummy.png" if not provided (line 11)
- ID generation: Uses HiLo pattern, not auto-increment
- Transaction: Implicit via EF6 SaveChanges (no explicit transaction scope)
- Redirect: Always returns to home page on success

**Evidence**:
- `Create.aspx.cs:50-82` (handler logic)
- `CatalogItem.cs:20-23` (Price validation)
- `CatalogItem.cs:43-55` (Stock validations)
- `CatalogService.cs:50-54` (persistence)

---

### Flow 3: Edit Catalog Item (Edit.aspx Save_Click)

**Call Chain**:
1. `Edit.aspx.cs:24` → `Page_Load()` - Load existing item for display
2. `Edit.aspx.cs:40` → Extract `id` from RouteData
3. `Edit.aspx.cs:41` → `CatalogService.FindCatalogItem(productId)` (initial load)
4. `Edit.aspx.cs:62` → `Save_Click()` event handler
5. `Edit.aspx.cs:64` → `ModelState.IsValid` validation check
6. `Edit.aspx.cs:66-79` → Construct updated `CatalogItem` from form inputs
7. `Edit.aspx.cs:81-86` → Update image if `TempImageName` present
8. `Edit.aspx.cs:88` → `CatalogService.UpdateCatalogItem(catalogItem)`
9. `CatalogService.cs:59` → `db.Entry(catalogItem).State = EntityState.Modified`
10. `CatalogService.cs:60` → `db.SaveChanges()` (commit transaction)
11. `Edit.aspx.cs:90` → `Response.Redirect("~")` (return to list)
12. **Boundary**: Database write, file I/O

**Side Effects**:
- Writes: `UPDATE Catalog SET ... WHERE Id = ?`
- Writes: Image file copy (if uploaded) to `~/Pics/` or Azure Blob

**Business Rules** (extracted from code):
- Same validation rules as Create (inherited from model)
- PictureFileName: Read-only in UI (line 74, Tooltip="Not allowed for edition")
- ID: Must be present in RouteData (from URL parameter)
- Image update: Only if `TempImageName` is populated (new upload)
- Transaction: Implicit via EF6 SaveChanges
- Redirect: Always returns to home page on success

**Evidence**:
- `Edit.aspx.cs:24-49` (Page_Load logic)
- `Edit.aspx.cs:62-92` (Save handler)
- `CatalogService.cs:57-60` (update logic)

---

### Flow 4: Delete Catalog Item (Delete.aspx Delete_Click)

**Call Chain**:
1. `Delete.aspx.cs:20` → `Page_Load()` - Load item for confirmation
2. `Delete.aspx.cs:27` → Extract `id` from RouteData
3. `Delete.aspx.cs:29` → `CatalogService.FindCatalogItem(productId)`
4. `Delete.aspx.cs:34` → `Delete_Click()` event handler
5. `Delete.aspx.cs:36` → `CatalogService.RemoveCatalogItem(productToDelete)`
6. `CatalogService.cs:65` → `db.CatalogItems.Remove(catalogItem)`
7. `CatalogService.cs:66` → `db.SaveChanges()` (commit transaction)
8. `Delete.aspx.cs:38` → `Response.Redirect("~")` (return to list)
9. **Boundary**: Database write

**Side Effects**:
- Writes: `DELETE FROM Catalog WHERE Id = ?`
- Writes: **Does NOT delete image file** (orphaned files may accumulate)

**Business Rules** (extracted from code):
- Confirmation screen: Always shown before delete (via separate page)
- ID: Must be present in RouteData
- Transaction: Implicit via EF6 SaveChanges
- No cascade delete: FK relationships preserved (only item deleted)
- Image cleanup: NOT performed (potential file system leak)
- Redirect: Always returns to home page on success

**Evidence**:
- `Delete.aspx.cs:20-39` (delete flow)
- `CatalogService.cs:63-66` (delete logic)
- No image deletion code found in evidence

---

### Flow 5: View Catalog Item Details (Details.aspx Page_Load)

**Call Chain**:
1. `Details.aspx.cs:17` → `Page_Load()` entry point
2. `Details.aspx.cs:19` → Extract `id` from RouteData
3. `Details.aspx.cs:21` → `CatalogService.FindCatalogItem(productId)`
4. `CatalogService.cs:38` → `db.CatalogItems.Include(CatalogBrand).Include(CatalogType).FirstOrDefault(ci => ci.Id == id)`
5. **Boundary**: Database read

**Side Effects**:
- Reads: `Catalog` table (single row with Id = ?)
- Reads: `CatalogBrand` table (via JOIN)
- Reads: `CatalogType` table (via JOIN)
- Writes: None

**Business Rules** (extracted from code):
- ID: Must be present in RouteData
- Eager loading: Always include related Brand and Type
- Not found handling: `FirstOrDefault` returns null (not explicitly handled in code)
- Display: Read-only view with navigation to Edit page

**Evidence**:
- `Details.aspx.cs:17-24` (page load logic)
- `CatalogService.cs:36-38` (query logic)

---

### Flow 6: Authentication Check (Create/Edit/Delete Pages)

**Call Chain**:
1. `Create.aspx.cs:26` → `Request.IsAuthenticated` check
2. `Create.aspx.cs:28` → `Context.GetOwinContext().Authentication.Challenge()` if not authenticated
3. **Boundary**: Authentication (Azure AD redirect)

**Side Effects**:
- Redirect: Sends user to Azure AD login page
- Cookie: Sets OWIN authentication cookie on success
- Redirect: Returns to original page after successful login

**Business Rules** (extracted from code):
- Protected pages: Create, Edit, Delete (Details is NOT protected)
- Authentication mechanism: OpenID Connect (Azure AD)
- Redirect URI: "/" (home page)
- Challenge triggered: Only on `!Request.IsAuthenticated`

**Evidence**:
- `Create.aspx.cs:26-28` (auth check)
- `Edit.aspx.cs:30-33` (auth check)
- `Delete.aspx.cs:23-25` (auth check)

---

## Data Ownership

### Read Targets

| Table/File | Columns/Fields | Evidence | Confidence |
|------------|----------------|----------|------------|
| Catalog (CatalogItem) | All columns | CatalogService.cs:24-30, CatalogService.cs:38 | high |
| CatalogBrand | Id, Brand | CatalogService.cs:45, eager loaded in queries | high |
| CatalogType | Id, Type | CatalogService.cs:42, eager loaded in queries | high |
| ~/Pics/*.png/jpg | Image files | ImageMockStorage.cs:40-47 | high |
| Setup/*.csv | Seed data | external-dependencies.json | high |

### Write Targets

| Table/File | Operations | Evidence | Conflicts |
|------------|------------|----------|-----------|
| Catalog (CatalogItem) | INSERT, UPDATE, DELETE | CatalogService.cs:50-66 | None |
| ~/Pics/*.png/jpg | WRITE (copy) | Create.aspx.cs:77, Edit.aspx.cs:83 | None |

**Transaction Scope**:
- All database writes use EF6 implicit transactions (via `SaveChanges()`)
- No explicit `TransactionScope` detected
- Image file operations NOT transactional (can fail independently)

---

## External Dependencies

| Type | Description | Evidence | Wrapper Needed |
|------|-------------|----------|----------------|
| SQL Server (EF6) | Database access via Entity Framework 6 | CatalogDBContext.cs, CatalogService.cs | No (replace with SQLAlchemy) |
| File I/O | Image storage in ~/Pics/ or Azure Blob | ImageMockStorage.cs, ImageAzureStorage.cs | No (Python file I/O) |
| OpenID Connect | Azure AD authentication | Create.aspx.cs:26-28, Edit.aspx.cs:30-33 | No (replace with JWT) |
| log4net | Logging framework | Default.aspx.cs:14, Create.aspx.cs:15 | No (replace with structlog) |

---

## Cross-Seam Dependencies

**None detected** ✅

This seam is completely self-contained with no dependencies on other seams.

---

## Readiness Assessment

**Status**: ✅ **GO**

**Confidence**: **High**

**Blockers**: None

**Warnings**:
1. **Authentication** (Medium severity): Uses OpenID Connect (Azure AD). Migration requires JWT-based auth implementation.
2. **File Storage** (Low severity): Two modes (local file system or Azure Blob). Requires abstraction layer in Python.
3. **ID Generation** (Low severity): Uses HiLo ID generator. Replace with database auto-increment or UUID.

---

## Inputs for Downstream Agents

### For Requirements Generator (105-requirements-agent)

**Business Rules Extracted**:
1. **Pagination**:
   - Default page size: 10 items
   - Default page index: 0 (0-based)
   - Sort order: By Id ascending
2. **Validation**:
   - Name: Required, MaxLength 50
   - Price: Required, Range 0-9999999999999999.99, Currency format, 2 decimals
   - Stock fields: Range 0-10000000
   - Brand and Type: Required (FK constraints)
3. **Image Handling**:
   - Default image: "dummy.png" if not provided
   - Upload: Client-side (async) via hidden field `TempImageName`
   - Storage: ~/Pics/ or Azure Blob (configurable)
4. **Authentication**:
   - Protected pages: Create, Edit, Delete
   - Public pages: Default (list), Details
   - Mechanism: OpenID Connect (Azure AD)
5. **Navigation**:
   - All success operations redirect to home page (Default.aspx)
   - All cancel operations return to home page

### For Contract Generator (106-contract-agent)

**Required Fields** (documented in `contracts/required-fields.json`):
- **Inputs**: name, description, catalogBrandId, catalogTypeId, price, availableStock, restockThreshold, maxStockThreshold, tempImageName
- **Outputs**: id, name, description, brandName, typeName, price, pictureFileName, pictureUri, availableStock, restockThreshold, maxStockThreshold
- **Filters/Sorts/Paging**: pageSize, pageIndex, sortColumn (Id)

**Suggested Endpoints**:
- `GET /api/catalog/items?pageSize={size}&pageIndex={index}` - List items with pagination
- `GET /api/catalog/items/{id}` - Get single item details
- `POST /api/catalog/items` - Create new item
- `PUT /api/catalog/items/{id}` - Update existing item
- `DELETE /api/catalog/items/{id}` - Delete item
- `GET /api/catalog/brands` - List all brands (lookup)
- `GET /api/catalog/types` - List all types (lookup)
- `POST /api/catalog/items/{id}/image` - Upload item image

### For Implementation (107-implementation-agent, 108-frontend-agent)

**Platform-Specific Wrappers Needed**: None

**Test Scenarios**:
1. **Happy Path - List**: Load Default.aspx, verify 10 items displayed, pagination controls work
2. **Happy Path - Create**: Create new item with all fields, verify redirect to list, item appears
3. **Happy Path - Edit**: Edit existing item, change price, verify update persisted
4. **Happy Path - Delete**: Delete item via confirmation screen, verify removal from list
5. **Happy Path - Details**: View item details, verify all fields displayed correctly
6. **Validation - Create**: Submit form with invalid price, verify error message
7. **Authentication - Protected**: Access Create page without login, verify redirect to Azure AD
8. **Pagination - Edge**: Navigate to last page, verify "Next" button hidden
9. **Image Upload - Optional**: Create item without image, verify default "dummy.png" used
10. **Image Upload - Success**: Upload image, verify preview displayed, item saved with correct filename

**Technical Notes**:
- Image upload is client-side (JavaScript not in evidence) - needs modern implementation
- HiLo ID generator needs replacement in Python (auto-increment or UUID)
- No cascade delete - FK relationships preserved
- Image files NOT cleaned up on delete (potential file system leak)
- No explicit error handling for database failures (rely on framework)
- No explicit null checks for `FindCatalogItem` (can return null)

---

## Pagination, Filtering, Sorting & Format Rules

### Grid Defaults
- **Page size**: 10 rows (constant `DefaultPageSize`)
- **Default page index**: 0 (constant `DefaultPageIndex`)
- **Default sort**: Id ascending (line `OrderBy(c => c.Id)`)
- **No default filters**: All items displayed

### Display Rules
- **Dates**: Not applicable (no date fields displayed)
- **Currency**: Price displayed with `$` prefix via CSS (`.esh-price:before { content: '$'; }`)
- **Numbers**: Integer fields (stock) displayed as-is
- **Decimals**: Price allows 2 decimal places (validation: `@"^\d+(\.\d{0,2})*$"`)
- **Booleans**: Not applicable (no boolean fields displayed)

**Evidence**:
- `Default.aspx.cs:16-17` (pagination constants)
- `CatalogService.cs:27` (sort order)
- `design-tokens.json:276-278` (price prefix CSS)
- `CatalogItem.cs:20` (price validation regex)

---

## Multi-Step Workflows

**None detected** ✅

All operations are single-step (create, read, update, delete). No orchestrated multi-step workflows or background jobs.

---

## Additional UI Elements (from code analysis)

All UI elements were captured in `ui-specification.json`. No additional elements discovered during code analysis.

---

## Shared Dependencies

- **Site.Master**: Master page providing header, hero section, footer (shared infrastructure)
- **Content/Site.css**: Global styles and design tokens (shared infrastructure)
- **Global.asax / Startup.cs**: Application startup and dependency injection (shared infrastructure)
- **App_Start/RouteConfig.cs**: Route definitions (shared infrastructure)

**Evidence**: seam-proposals.json:28 (shared_infrastructure)

---

## Stop Condition

✅ **All discovery outputs completed**:
- discovery.md ✅
- readiness.json ✅
- evidence-map.json ✅
- required-fields.json ✅
- targets.json ✅
- ui-specification.json ✅ (Phase A)
- design-tokens.json ✅ (Phase A)
- navigation-spec.json ✅ (Phase A)
- static-assets.json ✅ (Phase A)
- database-schema.json ✅ (Phase A)
- external-dependencies.json ✅ (Phase A)

**Readiness status**: GO ✅
**Technical analysis**: Complete ✅

---

## End of Discovery Report
