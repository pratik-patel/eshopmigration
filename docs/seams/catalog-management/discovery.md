# Discovery Report: catalog-management

**Generated**: 2026-03-03
**Analyst**: Discovery Agent (Phase 1)
**Status**: Complete

---

## Seam Summary

**Purpose**: Complete product catalog management system enabling users to browse, view, and manage (CRUD) product listings with associated images, brands, and types.

**Boundaries**:
- In-scope: All catalog CRUD operations, image upload/management, pagination, reference data (brands, types)
- Out-of-scope: Shopping cart, orders, payments, customer management (not in application)

**Key Assumptions**:
- Single-seam application (entire application scope)
- No cross-seam dependencies (self-contained)
- All external dependencies have abstraction layers (IImageService, ICatalogService)
- HiLo sequence pattern is legacy-specific and will be replaced

---

## Verified UI Triggers

| Screen | Control | Event | Handler | File | Confidence |
|--------|---------|-------|---------|------|------------|
| Default.aspx | Page Load | Page_Load | Page_Load | Default.aspx.cs | high |
| Default.aspx | PaginationNext | Click (navigation) | (route navigation) | Default.aspx.cs:57 | high |
| Default.aspx | PaginationPrevious | Click (navigation) | (route navigation) | Default.aspx.cs:61 | high |
| Details.aspx | Page Load | Page_Load | Page_Load | Details.aspx.cs:17 | high |
| Create.aspx | Page Load | Page_Load | Page_Load | Create.aspx.cs:21 | high |
| Create.aspx | Create Button | Click (postback) | Create_Click | Create.aspx.cs:50 | high |
| Edit.aspx | Page Load | Page_Load | Page_Load | Edit.aspx.cs:24 | high |
| Edit.aspx | Save Button | Click (postback) | Save_Click | Edit.aspx.cs:62 | high |
| Delete.aspx | Page Load | Page_Load | Page_Load | Delete.aspx.cs:20 | high |
| Delete.aspx | Delete Button | Click (postback) | Delete_Click | Delete.aspx.cs:34 | high |
| PicUploader.asmx | AJAX POST | UploadImage | UploadImage | PicUploader.asmx.cs:32 | high |

---

## Verified Flows

### Flow 1: List Products with Pagination (Default.aspx)

**Call Chain**:
1. `Default.aspx.cs:Page_Load()` → Entry point
2. `Default.aspx.cs:31` → Check if pagination params in route
3. `CatalogService.GetCatalogItemsPaginated(size, index)` → Business logic
4. `CatalogService.cs:20` → Query database with EF6
5. **Boundary**: Database read (Catalog, CatalogBrand, CatalogType tables)

**Side Effects**:
- Reads: Catalog, CatalogBrand, CatalogType tables
- Writes: None
- DB Operations:
  - `db.CatalogItems.LongCount()` (total count)
  - `db.CatalogItems.Include(...).OrderBy(...).Skip(...).Take(...)` (paginated query)
- Image URI construction: `ImageService.BuildUrlImage(catalogItem)` for each item

**Business Rules** (extracted from code):
- Default page size: 10 items (DefaultPageSize constant)
- Default page index: 0 (DefaultPageIndex constant)
- Sorting: Always by Id ascending (`OrderBy(c => c.Id)`)
- Eager loading: Always include CatalogBrand and CatalogType navigation properties
- Image URI is computed at runtime (not stored in DB)

**Transaction Scope**: None (read-only operation)

---

### Flow 2: View Product Details (Details.aspx)

**Call Chain**:
1. `Details.aspx.cs:Page_Load()` → Entry point
2. `Details.aspx.cs:19` → Extract product ID from route data
3. `CatalogService.FindCatalogItem(productId)` → Business logic
4. `CatalogService.cs:36` → Query database with EF6
5. **Boundary**: Database read (Catalog, CatalogBrand, CatalogType tables)

**Side Effects**:
- Reads: Single Catalog record with related Brand and Type
- Writes: None
- DB Operations: `db.CatalogItems.Include(...).FirstOrDefault(ci => ci.Id == id)`

**Business Rules**:
- Returns null if product not found (no explicit error handling in code)
- Eager loads navigation properties (CatalogBrand, CatalogType)

**Transaction Scope**: None (read-only operation)

---

### Flow 3: Create Product (Create.aspx)

**Call Chain**:
1. `Create.aspx.cs:Page_Load()` → Entry point, authentication check
2. `Create.aspx.cs:26-28` → OpenID Connect authentication challenge if not authenticated
3. `Create.aspx.cs:50` → Create_Click event handler
4. `Create.aspx.cs:53` → ModelState validation check
5. `Create.aspx.cs:54-65` → Construct CatalogItem from form fields
6. `CatalogService.CreateCatalogItem(catalogItem)` → Business logic
7. `CatalogService.cs:50` → Generate HiLo ID, add to DbSet, SaveChanges
8. **Boundary**: Database write (Catalog table)
9. (Optional) `ImageService.UpdateImage(catalogItem)` → Move temp image to permanent storage
10. **Boundary**: Azure Blob Storage write or local file copy

**Side Effects**:
- Writes: INSERT into Catalog table
- External: Image storage (if TempImageName provided)
  - Source: Temp storage (uploaded via PicUploader.asmx)
  - Destination: Permanent storage (`pics/{catalogItemId}/{filename}`)
  - Method: Copy blob, delete temp (Azure) or file copy (mock)

**Business Rules**:
- Authentication required (enforced in Page_Load)
- Name field required (ASP.NET validator)
- Price validation: 0 to 1,000,000, max 2 decimals (RegularExpression + Range validators)
- Stock fields validation: 0 to 10,000,000 (Range validators)
- ID generation: HiLo sequence with increment of 10
- Default picture filename: "dummy.png" if no image uploaded
- Image upload controlled by `CatalogConfiguration.UseAzureStorage` flag

**Transaction Scope**:
- DB operation: Single SaveChanges call (atomic)
- Image operation: Separate call (not in DB transaction)
- **Risk**: If image update fails, product is still created with default or incorrect filename

---

### Flow 4: Update Product (Edit.aspx)

**Call Chain**:
1. `Edit.aspx.cs:Page_Load()` → Entry point, authentication check
2. `Edit.aspx.cs:28` → Check IsPostBack (load existing data on GET)
3. `Edit.aspx.cs:40-47` → Load product and populate dropdowns
4. `Edit.aspx.cs:62` → Save_Click event handler
5. `Edit.aspx.cs:64` → ModelState validation check
6. `Edit.aspx.cs:66-79` → Construct CatalogItem from form fields
7. (Optional) `ImageService.UpdateImage(catalogItem)` → Replace image if TempImageName provided
8. **Boundary**: Azure Blob Storage write (if image changed)
9. `CatalogService.UpdateCatalogItem(catalogItem)` → Business logic
10. `CatalogService.cs:57` → Set entity state to Modified, SaveChanges
11. **Boundary**: Database write (Catalog table)

**Side Effects**:
- Writes: UPDATE Catalog table
- External: Image storage (if TempImageName provided)
  - Action: Delete old blobs, copy temp to permanent, delete temp
  - Method: `ImageAzureStorage.UpdateImage()` or mock equivalent

**Business Rules**:
- Same validation as Create (Name required, Price/Stock ranges)
- PictureFileName field is read-only in UI (cannot be directly edited)
- Image replacement: Upload new image → sets TempImageName → updates on save
- Image retention: If no TempImageName, keeps existing PictureFileName
- Product ID preserved from route data

**Transaction Scope**:
- Image update occurs BEFORE database update
- **Risk**: If image update succeeds but DB update fails, orphaned image in storage
- **Risk**: If DB update succeeds but image update fails (unlikely order), DB has wrong filename

---

### Flow 5: Delete Product (Delete.aspx)

**Call Chain**:
1. `Delete.aspx.cs:Page_Load()` → Entry point, authentication check
2. `Delete.aspx.cs:27-29` → Load product for confirmation display
3. `Delete.aspx.cs:34` → Delete_Click event handler
4. `CatalogService.RemoveCatalogItem(productToDelete)` → Business logic
5. `CatalogService.cs:63` → Remove from DbSet, SaveChanges
6. **Boundary**: Database write (Catalog table DELETE)

**Side Effects**:
- Writes: DELETE from Catalog table
- External: None (image NOT deleted from storage)

**Business Rules**:
- Authentication required
- No confirmation dialog (confirmation is the entire page display)
- **DEFECT**: Image is not deleted from blob storage (orphaned images)
- Foreign key constraints: Cannot delete CatalogBrand or CatalogType if referenced by Catalog

**Transaction Scope**: Single SaveChanges call (atomic)

**Missing Functionality**:
- Image cleanup not implemented (should call `ImageService.DeleteImage(catalogItem)`)
- No cascade delete for images in storage

---

### Flow 6: Upload Image (PicUploader.asmx)

**Call Chain**:
1. `PicUploader.asmx.cs:UploadImage()` → Entry point (AJAX WebMethod)
2. `PicUploader.asmx.cs:36-38` → Resolve IImageService from Autofac container
3. `PicUploader.asmx.cs:40-41` → Extract file and itemId from request
4. `PicUploader.asmx.cs:43-49` → Validate image format (JPEG, PNG, GIF)
5. `ImageService.UploadTempImage(image, catalogItemId)` → Business logic
6. `ImageAzureStorage.UploadTempImage()` → Upload to temp storage
7. **Boundary**: Azure Blob Storage write (temp folder)

**Side Effects**:
- Writes: Upload image to `pics/temp/{guid}/` or `pics/{itemId}/temp/` folder
- Returns: JSON with temp image URL and path

**Business Rules**:
- **SECURITY ISSUE**: No authentication required (open endpoint)
- Image format validation: JPEG, PNG, GIF only (via `Image.FromStream()`)
- Invalid image returns 400 status code
- Temp path includes GUID or itemId for uniqueness
- Filename converted to lowercase

**Transaction Scope**: Single blob upload operation (atomic)

**Security Risks**:
- Unauthenticated endpoint allows anonymous image uploads
- No file size validation (potential DoS)
- No rate limiting
- Temp images not automatically cleaned up (orphaned files)

---

## Multi-Step Workflows

### Product Creation with Image Upload

**Workflow**:
1. User navigates to Create page (GET /Catalog/Create)
2. Page loads with default image preview
3. User selects image file
4. JavaScript triggers AJAX POST to /Catalog/PicUploader.asmx
5. Server validates image and uploads to temp storage
6. Server returns temp image URL as JSON
7. JavaScript updates preview and sets TempImageName hidden field
8. User fills form fields and clicks Create button
9. Form posts to server (Create_Click handler)
10. Server creates Catalog record with TempImageName
11. Server calls ImageService.UpdateImage() to move temp to permanent
12. Server redirects to product list

**State Management**:
- Temp image URL stored in hidden field (TempImageName)
- Image preview updated client-side (JavaScript)
- Permanent storage only happens on successful form submission

**Error Cases**:
- Image upload fails → User sees upload error, can retry
- Form validation fails → TempImageName preserved in postback, can retry
- Product creation fails → Orphaned temp image in storage (not cleaned up)
- Image move fails after product created → Product has wrong/default image

---

### Product Update with Image Replacement

**Workflow**:
1. User navigates to Edit page (GET /Catalog/Edit/{id})
2. Page loads with existing product data and current image
3. (Optional) User uploads new image via AJAX (same as Create flow)
4. User modifies form fields and clicks Save button
5. Form posts to server (Save_Click handler)
6. If TempImageName set:
   - Server deletes old product images in storage
   - Server copies temp image to permanent location
   - Server deletes temp image
   - Server updates PictureFileName in CatalogItem
7. Server updates Catalog record in database
8. Server redirects to product list

**State Management**:
- Product ID from route data
- TempImageName hidden field (empty if no new image)
- PictureFileName preserved if no new image uploaded

**Error Cases**:
- Same as Create flow, plus:
  - Old image deleted but new image copy fails → Product has no image (broken)

---

## Data Ownership

### Read Targets

| Table/File | Columns/Fields | Evidence | Confidence |
|------------|----------------|----------|------------|
| Catalog | All columns | CatalogService.cs:24-29 (GetCatalogItemsPaginated) | high |
| Catalog | All columns | CatalogService.cs:36-38 (FindCatalogItem) | high |
| CatalogType | Id, Type | CatalogService.cs:40-42 (GetCatalogTypes) | high |
| CatalogBrand | Id, Brand | CatalogService.cs:44-47 (GetCatalogBrands) | high |
| catalog_hilo sequence | NEXT VALUE | CatalogItemHiLoGenerator.cs:19 | high |

### Write Targets

| Table/File | Operations | Evidence | Conflicts |
|------------|------------|----------|-----------|
| Catalog | INSERT | CatalogService.cs:50-54 (CreateCatalogItem) | None |
| Catalog | UPDATE | CatalogService.cs:57-60 (UpdateCatalogItem) | None |
| Catalog | DELETE | CatalogService.cs:63-66 (RemoveCatalogItem) | None |
| Azure Blob Storage (`pics/` container) | Upload (temp), Copy, Delete | ImageAzureStorage.cs:87-100, 65-85 | None |

### Unknown Targets

None - all data access is explicit and traceable.

### Shared Write Conflicts

None - single seam application, no concurrent write access to same resources.

---

## External Dependencies

### 1. Azure Blob Storage (Image Storage)

**Type**: Cloud storage service
**Adapter**: IImageService interface
**Implementations**:
- `ImageAzureStorage` (production, Azure Blob)
- `ImageMockStorage` (development, local filesystem)

**Usage**:
- Upload temp images (PicUploader.asmx)
- Move images from temp to permanent (Create/Edit flows)
- Build image URLs for display (all pages)
- Initialize catalog images from local disk

**Configuration**:
- Connection string: `CatalogConfiguration.StorageConnectionString`
- Feature flag: `CatalogConfiguration.UseAzureStorage` (bool)
- Container name: `pics` (hardcoded)

**Migration Path**:
- Replace with S3-compatible storage (MinIO, AWS S3) or local filesystem
- Implement new adapter class implementing IImageService
- Update DI registration in ApplicationModule
- No code changes required in pages/services (interface-based)

**Blocker**: No (has mock implementation)

---

### 2. Azure Active Directory (Authentication)

**Type**: Identity provider (OAuth2/OpenID Connect)
**Adapter**: OWIN middleware (Microsoft.Owin.Security.OpenIdConnect)

**Usage**:
- Authenticate users for Create/Edit/Delete operations
- Challenge unauthenticated requests to protected pages
- Display user name in header

**Configuration**:
- ClientId, Tenant, Instance: Web.config appSettings
- Feature flag: `CatalogConfiguration.UseAzureActiveDirectory` (inferred)

**Migration Path**:
- Replace with JWT bearer token authentication
- Implement JWT validation middleware in FastAPI
- Remove OpenID Connect challenge code
- Add JWT token generation endpoint (login)

**Blocker**: No (can be disabled, pages check `Request.IsAuthenticated` flag)

---

### 3. SQL Server with HiLo Sequence

**Type**: Database with custom ID generation pattern
**Adapter**: Entity Framework 6 (CatalogDBContext)

**Usage**:
- CRUD operations on Catalog, CatalogBrand, CatalogType
- HiLo sequence for generating Catalog IDs (non-standard)

**Configuration**:
- Connection string: Web.config connectionStrings (CatalogDBContext)
- Sequence: `catalog_hilo` (created by DB initializer)

**Migration Path**:
- Replace with PostgreSQL or SQLite
- Use async SQLAlchemy 2.x
- Replace HiLo with auto-increment PRIMARY KEY or UUID
- Migrate data: Export/transform/import (adjust ID generation)

**Blocker**: No (HiLo is isolated in CatalogItemHiLoGenerator class)

**Technical Debt**:
- HiLo pattern is SQL Server-specific and adds complexity
- Synchronous DB access (EF6) - no async/await
- No connection pooling configuration visible
- No explicit transaction management (relies on SaveChanges)

---

### 4. Application Insights (Telemetry)

**Type**: Observability/logging service
**Adapter**: Microsoft.ApplicationInsights.Web

**Usage**:
- Request tracking
- Exception tracking
- Custom telemetry

**Configuration**:
- Instrumentation key: Environment variable or Web.config

**Migration Path**:
- Replace with OpenTelemetry + structlog
- Remove Application Insights dependency
- Add structured JSON logging

**Blocker**: No (optional, has fallback to log4net)

---

### 5. Autofac (Dependency Injection)

**Type**: IoC container
**Usage**: Property injection for ICatalogService and IImageService in pages

**Migration Path**:
- Replace with FastAPI Depends() pattern
- No IoC container needed (FastAPI handles DI)

**Blocker**: No (architectural change, straightforward migration)

---

## Cross-Seam Dependencies

### Hard Dependencies
**None** - This is the only seam in the application.

### Soft Dependencies
**None** - Self-contained seam.

### Shared Infrastructure
- Authentication middleware (OWIN, to be replaced with JWT)
- Logging (log4net, to be replaced with structlog)
- Configuration (Web.config, to be replaced with pydantic-settings)
- Dependency injection (Autofac, to be replaced with FastAPI Depends())

---

## Readiness Assessment

**Status**: GO

**Confidence**: High

**Confidence Reason**:
- Clean architecture with interface-based abstractions
- No circular dependencies or cross-seam coupling
- All external dependencies have clear migration paths
- Single seam = no coordination complexity
- Comprehensive test coverage possible (interfaces enable mocking)

### Blockers

None.

### Non-Blocking Issues

1. **Image deletion not implemented** (Severity: Low)
   - Evidence: Delete.aspx.cs:34-36 calls RemoveCatalogItem but no image cleanup
   - Mitigation: Add image deletion logic in modern API, cleanup orphaned images in migration

2. **Unauthenticated image upload endpoint** (Severity: High)
   - Evidence: PicUploader.asmx has no authentication check
   - Mitigation: Add JWT authentication to modern API image upload endpoint

3. **HiLo sequence pattern incompatibility** (Severity: Medium)
   - Evidence: CatalogItemHiLoGenerator.cs:19, SQL Server-specific
   - Mitigation: Use auto-increment PRIMARY KEY or UUID in modern database

4. **Synchronous database operations** (Severity: Low)
   - Evidence: CatalogService uses Entity Framework 6 (no async)
   - Mitigation: Rewrite with async SQLAlchemy 2.x

5. **Missing transaction management for multi-step operations** (Severity: Medium)
   - Evidence: Image update and DB update are separate operations (not atomic)
   - Mitigation: Implement proper transaction scope or compensating actions in modern API

6. **No file size validation on image upload** (Severity: Medium)
   - Evidence: PicUploader.asmx:32-62 validates format but not size
   - Mitigation: Add file size limit (e.g., 5MB) in modern API

---

## Boundary Analysis

### Seam Boundary Verification

**Status**: Clean boundaries

**Analysis**:
- All database writes confined to Catalog table (owned by seam)
- Reference tables (CatalogType, CatalogBrand) are read-only from seam perspective
- Image storage is seam-specific (no shared blob containers)
- No shared mutable state (Autofac manages per-request instances)

**Cross-Boundary Calls**: None (single seam application)

**Shared Resources**:
- Database connection pool (implicit, not a blocker)
- Log files (log4net, read-only from app perspective)
- Configuration files (read-only)

### Boundary Issues

**None detected.**

No `boundary-issues.json` file is required.

---

## Technical Debt Assessment

### Code Smells

1. **Static configuration class** (CatalogConfiguration)
   - Evidence: Used in Create.aspx.cs:31, Edit.aspx.cs:35, ImageAzureStorage.cs:19
   - Issue: Global mutable state, hard to test
   - Migration: Replace with pydantic-settings (injected configuration)

2. **Property injection via Autofac**
   - Evidence: All pages have `public ICatalogService CatalogService { get; set; }`
   - Issue: Implicit dependencies, not visible in constructor
   - Migration: Use FastAPI Depends() (explicit, testable)

3. **Tight coupling to ASP.NET WebForms lifecycle**
   - Evidence: Page_Load, IsPostBack checks, ViewState, Server.MapPath
   - Issue: Framework-specific, hard to test
   - Migration: Replace with REST API (stateless, framework-agnostic)

4. **Mixed concerns in code-behind**
   - Evidence: Create.aspx.cs:50-81 has validation, business logic, and navigation
   - Issue: Violates Single Responsibility Principle
   - Migration: Separate into route handler, service layer, and models

5. **Magic strings and hardcoded paths**
   - Evidence: "pics" container name, "temp" folder, "dummy.png" default image
   - Issue: Not configurable, scattered through code
   - Migration: Centralize in configuration

### Anti-Patterns

1. **God class tendency in CatalogService**
   - Evidence: 7 methods, all CRUD operations in single class
   - Issue: Not severe (small codebase), but could grow
   - Migration: Keep simple service pattern, but consider separate read/write services if needed

2. **Exception swallowing**
   - Evidence: PicUploader.asmx.cs:73-77 catches all exceptions, returns false
   - Issue: Loss of diagnostic information
   - Migration: Log exceptions, return specific error responses

3. **No explicit null checks**
   - Evidence: Details.aspx.cs:21 assumes product is found, no null check
   - Issue: Potential NullReferenceException if product not found
   - Migration: Return 404 response with explicit error

### Security Issues

1. **Unauthenticated image upload endpoint** (CRITICAL)
   - Evidence: PicUploader.asmx has no [Authorize] attribute or authentication check
   - Risk: Anonymous users can upload images (DoS, storage costs, abuse)
   - Mitigation: Add JWT authentication in modern API

2. **No file size limit on uploads** (HIGH)
   - Evidence: No size check in PicUploader.asmx
   - Risk: Large file uploads (DoS, storage exhaustion)
   - Mitigation: Add file size validation (e.g., 5MB max)

3. **No rate limiting** (MEDIUM)
   - Evidence: No throttling on any endpoint
   - Risk: Brute force attacks, resource exhaustion
   - Mitigation: Add rate limiting middleware in modern API

4. **No CSRF protection** (MEDIUM)
   - Evidence: ASP.NET WebForms postback mechanism lacks explicit CSRF tokens
   - Risk: Cross-site request forgery attacks
   - Mitigation: Use REST API with CORS policy and JWT tokens (stateless)

5. **Weak authorization model** (LOW)
   - Evidence: Only checks authentication, no roles or claims
   - Risk: All authenticated users can edit/delete all products
   - Mitigation: Add role-based access control (RBAC) in modern API

### Performance Issues

1. **N+1 query potential** (MITIGATED)
   - Evidence: CatalogService uses `.Include()` for navigation properties
   - Status: Already mitigated with eager loading
   - No action needed

2. **Synchronous I/O** (MEDIUM)
   - Evidence: All DB and blob operations are synchronous
   - Risk: Thread pool starvation under load
   - Mitigation: Use async/await in modern API (FastAPI, SQLAlchemy async)

3. **No caching** (LOW)
   - Evidence: No caching for reference data (brands, types)
   - Risk: Unnecessary DB queries for rarely-changing data
   - Mitigation: Add caching for reference data (Redis, in-memory)

4. **Full table scan for count** (LOW)
   - Evidence: `db.CatalogItems.LongCount()` on every page load
   - Risk: Slow on large datasets
   - Mitigation: Cache total count, invalidate on write operations

---

## Migration Planning

### Legacy to Modern Pattern Mapping

| Legacy Pattern | Modern Equivalent | Complexity |
|----------------|-------------------|------------|
| ASP.NET WebForms Page | FastAPI route handler | Low |
| Page_Load event | GET request handler | Low |
| Button_Click event | POST/PUT/DELETE handler | Low |
| ViewState | React state (useState) | Low |
| Server-side rendering | React client-side rendering | Medium |
| Postback | REST API call (fetch) | Low |
| ASP.NET Validators | Pydantic validation (backend) + Zod (frontend) | Low |
| Entity Framework 6 | SQLAlchemy 2.x async | Medium |
| Autofac property injection | FastAPI Depends() | Low |
| IImageService adapter | Same pattern (Python ABC) | Low |
| Azure Blob Storage | S3-compatible or local storage | Low |
| HiLo sequence | Auto-increment or UUID | Medium |
| OpenID Connect | JWT bearer tokens | Medium |
| log4net | structlog (JSON) | Low |

### Platform Wrappers Needed

**None required** per python-platform-wrappers.md rules:

- Azure Blob Storage → Pure config change (S3-compatible API or local storage)
- Azure AD → Architecture change (JWT tokens, not platform wrapper)
- SQL Server → Database change (PostgreSQL/SQLite, not wrapper)
- Application Insights → Replaced with OpenTelemetry (not wrapper)

**Rationale**:
- No COM/ActiveX dependencies
- No device I/O (serial ports, printers)
- No Windows Registry access (config moved to env vars)
- No named pipes or WCF services (replaced with REST)

### Migration Phases

#### Phase 1: Backend API (4 days)

**Setup**:
- FastAPI project structure
- SQLAlchemy models (Catalog, CatalogType, CatalogBrand)
- Pydantic schemas (request/response models)

**Services**:
- CatalogService (async CRUD methods)
- ImageService adapter (S3-compatible or local)

**Routes**:
- GET /api/catalog (list with pagination)
- GET /api/catalog/{id} (details)
- POST /api/catalog (create, requires auth)
- PUT /api/catalog/{id} (update, requires auth)
- DELETE /api/catalog/{id} (delete, requires auth)
- POST /api/catalog/images (upload, requires auth)
- GET /api/catalog/types (reference data)
- GET /api/catalog/brands (reference data)

**Auth**:
- JWT middleware
- Token generation endpoint

**Testing**:
- Unit tests (80% coverage target)
- Integration tests (API contract tests)

#### Phase 2: Frontend (3 days)

**Setup**:
- React + TypeScript + Vite
- TanStack Query for server state
- React Hook Form + Zod for forms
- shadcn/ui + Tailwind for styling

**Pages**:
- CatalogListPage (/) - List with pagination
- CatalogDetailPage (/{id}) - Details view
- CatalogCreatePage (/create) - Create form
- CatalogEditPage (/{id}/edit) - Edit form

**Components**:
- CatalogTable (reusable data table)
- CatalogForm (shared create/edit form)
- ImageUpload (file upload with preview)
- DeleteConfirmationDialog (modal)

**Routing**:
- React Router v6
- Protected routes (JWT required)

**Testing**:
- Component tests (Vitest, 75% coverage target)
- E2E tests (Playwright, critical paths)

#### Phase 3: Data Migration (1 day)

**Tasks**:
- Export legacy SQL Server database
- Transform schema (remove HiLo sequences)
- Import to PostgreSQL
- Migrate product images to new storage
- Validate data integrity

#### Phase 4: Deployment (2 days)

**Tasks**:
- Deploy backend to staging
- Deploy frontend to staging
- Run end-to-end parity tests
- Load test API endpoints
- Deploy to production with rollback plan
- Monitor and verify

---

## Inputs for Downstream Agents

### For Requirements Generator (spec-agent)

**Business Rules Extracted**:
1. Default pagination: 10 items per page, starting at page 0
2. Product sorting: Always by ID ascending (deterministic order)
3. Eager loading: Always include brand and type data with products
4. Image handling: Default to "dummy.png" if no image uploaded
5. Authentication: Required for Create/Edit/Delete, not for List/Details
6. Validation rules:
   - Name: Required, max 50 characters (inferred from DB schema)
   - Description: Optional, max length unlimited
   - Price: 0 to 1,000,000, max 2 decimal places, currency format
   - Stock fields: 0 to 10,000,000, integer
   - Brand and Type: Required (foreign keys)
7. Image formats: JPEG, PNG, GIF only
8. Temp image cleanup: Not implemented (orphaned images on failed submissions)
9. Image deletion: Not implemented on product deletion (orphaned images)

**UI Workflows Documented**:
- See ui-behavior.md for complete screen/control/action inventory
- All workflows are server-rendered (WebForms) → migrate to SPA (React)

**Data Access Patterns**:
- Read: Paginated queries with navigation properties
- Write: Single-record CRUD operations
- Transaction: Implicit (Entity Framework SaveChanges)
- Concurrency: None (no optimistic concurrency control)

### For Contract Generator

**Required Fields**:
- See `contracts/required-fields.json` (to be generated)

**Suggested Endpoints**:
1. GET /api/catalog?page={int}&size={int}&type_id={int?}&brand_id={int?}
2. GET /api/catalog/{id}
3. POST /api/catalog (body: CatalogItemCreate)
4. PUT /api/catalog/{id} (body: CatalogItemUpdate)
5. DELETE /api/catalog/{id}
6. POST /api/catalog/images (multipart: file)
7. GET /api/catalog/types
8. GET /api/catalog/brands

**Authentication**:
- Protected endpoints: POST, PUT, DELETE
- Public endpoints: GET
- Auth method: JWT bearer token

### For Implementation

**Platform-Specific Wrappers Needed**: None

**Test Scenarios**:
1. List products with pagination (default and custom page sizes)
2. View product details (existing and non-existent IDs)
3. Create product without image (default image used)
4. Create product with image upload (end-to-end flow)
5. Edit product without changing image (image preserved)
6. Edit product with new image (old image replaced)
7. Delete product (verify DB deletion, note image orphaned)
8. Upload image via AJAX (temp storage)
9. Authentication: Access protected pages (authenticated and unauthenticated)
10. Validation: Invalid form inputs (required fields, range validators)
11. Pagination: First page, middle page, last page, edge cases
12. Reference data: Load brands and types for dropdowns

---

## Stop Condition

**Status**: Discovery complete

**Outputs Generated**:
- ✅ discovery.md (this file)
- ✅ readiness.json (to be written next)
- ✅ evidence-map.json (to be written next)
- ✅ contracts/required-fields.json (to be written next)
- ✅ data/targets.json (to be written next)

**Readiness Status**: GO

**Next Agent**: spec-agent (Phase 2 - Requirements Generation)

---

## References

- Legacy codebase: `C:/Users/pratikp6/codebase/eShopModernizing/eShopModernizedWebFormsSolution`
- Seam proposal: `docs/context-fabric/seam-proposals.json`
- UI inventory: `docs/seams/catalog-management/ui-behavior.md`
- Database schema: `docs/context-fabric/database-schema.json`
- External integrations: `docs/context-fabric/external-integrations.json`
- Dependency graph: `docs/context-fabric/dependency-graph.json`
- CLAUDE.md: `C:/Users/pratikp6/codebase/eshopmigration/CLAUDE.md`
