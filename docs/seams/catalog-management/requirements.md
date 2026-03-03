# Requirements Document: Catalog Management

## Introduction

The Catalog Management seam provides complete product catalog management functionality for an e-commerce platform. This system enables users to browse products, view detailed product information, and perform administrative operations (create, update, delete) on catalog items. The seam includes product image management, inventory tracking, and categorization by brand and type.

This requirement replaces the legacy ASP.NET WebForms application with a modern Python (FastAPI) backend and React TypeScript frontend, maintaining full functional parity while addressing security issues and technical debt identified in the discovery phase.

**Business Context**: The catalog is the core of the e-commerce platform, serving as the single source of truth for product information, pricing, and inventory levels. It supports both customer-facing browsing operations and administrative content management.

## Glossary

- **CatalogSystem**: The FastAPI backend service responsible for all catalog CRUD operations
- **CatalogUI**: The React frontend application that displays and manages catalog data
- **ImageService**: The storage adapter responsible for product image upload, retrieval, and deletion
- **CatalogItem**: A product entity with name, description, price, stock levels, brand, type, and optional image
- **CatalogBrand**: A reference entity representing product manufacturers (e.g., "Microsoft", "Nike")
- **CatalogType**: A reference entity representing product categories (e.g., "Electronics", "Clothing")
- **PaginatedResponse**: A response containing items, page metadata (page index, size, total items, total pages)
- **AuthenticatedUser**: A user who has provided valid JWT credentials
- **AnonymousUser**: A user accessing public catalog endpoints without authentication

## Requirements

### Requirement 1: List Products with Pagination

**User Story:** As a user (anonymous or authenticated), I want to browse products with pagination, so that I can view the catalog without overwhelming page loads.

**Background:**
The legacy system displays products in a server-rendered table with pagination controls. The modern system must replicate this functionality using a REST API and client-side rendering. The default page size is 10 items (matching legacy behavior), and users can navigate between pages. This is the primary entry point for catalog browsing and must support large datasets (10,000+ products).

**Scope:**
- **In scope**: Product listing, pagination controls, page metadata, eager loading of brand/type relationships
- **Out of scope**: Search, filtering by brand/type (future enhancement), sorting options (future enhancement)

**Business Rules:**
- Default page size is 10 items per page
- Default page index is 0 (first page)
- Products are always sorted by ID in ascending order (deterministic ordering)
- Brand and Type data must be included with each product (eager loading)
- Image URIs are computed at runtime (not stored in database)
- Empty result sets are valid (return empty array, not error)

#### Acceptance Criteria

**Happy Path:**
1. WHEN AnonymousUser requests GET /api/catalog without parameters, THE CatalogSystem SHALL return the first 10 products with page metadata
2. WHEN AnonymousUser requests GET /api/catalog?page=2&size=20, THE CatalogSystem SHALL return products 21-40 with correct pagination metadata
3. WHEN AnonymousUser requests the last page, THE CatalogSystem SHALL return remaining products with total_pages correctly indicating last page
4. WHEN product list is displayed, THE CatalogUI SHALL show "Showing {ItemsPerPage} of {TotalItems} products - Page {ActualPage + 1} - {TotalPages}"

**Validation & Edge Cases:**
5. WHEN AnonymousUser requests page=-1, THE CatalogSystem SHALL return 400 error with message "Page index must be non-negative"
6. WHEN AnonymousUser requests size=0, THE CatalogSystem SHALL return 400 error with message "Page size must be positive"
7. WHEN AnonymousUser requests size=1000, THE CatalogSystem SHALL return 400 error with message "Page size must not exceed 100"
8. WHEN AnonymousUser requests page beyond last page, THE CatalogSystem SHALL return empty items array with correct total_pages metadata

**Business Rule Violations:**
9. IF database has 0 products, THEN THE CatalogSystem SHALL return response with empty items array and total_items=0
10. IF page index exceeds available pages, THEN THE CatalogSystem SHALL return 200 status with empty items array (not 404)

**Error Handling:**
11. IF database connection fails, THEN THE CatalogSystem SHALL return 500 error with correlation ID and log error with structlog
12. IF query timeout occurs (>30 seconds), THEN THE CatalogSystem SHALL return 504 error and log slow query warning

**Assumptions & Notes:**
- Pagination uses offset-based approach (LIMIT/OFFSET in SQL)
- Total count is calculated on every request (can be optimized with caching in future)
- Image URIs are built using ImageService.BuildUrlImage() pattern
- All responses include CORS headers for cross-origin access

---

### Requirement 2: View Product Details

**User Story:** As a user (anonymous or authenticated), I want to view detailed information about a single product, so that I can make informed purchasing decisions or review product data before editing.

**Background:**
The legacy Details page displays all product fields including name, description, price, stock levels, brand, type, and image. The modern system must provide the same data via a REST API endpoint and display it in a React component. This is accessed from the product list via a "Details" link and serves as a pre-edit review screen for administrators.

**Scope:**
- **In scope**: Single product retrieval by ID, full field display including navigation properties
- **Out of scope**: Related products, reviews, ratings (not in legacy)

**Business Rules:**
- Product ID must exist in database (return 404 if not found)
- Brand and Type relationships must be eagerly loaded (single query)
- Image URI is computed at runtime (not stored value)
- All numeric fields display with appropriate formatting (currency for price, integer for stock)

#### Acceptance Criteria

**Happy Path:**
1. WHEN AnonymousUser requests GET /api/catalog/{id} with valid ID, THE CatalogSystem SHALL return product with all fields including brand and type objects
2. WHEN product has image, THE CatalogSystem SHALL return pictureUri computed from pictureFileName via ImageService
3. WHEN product details display, THE CatalogUI SHALL show all fields in readable format (currency for price, integers for stock)

**Validation & Edge Cases:**
4. WHEN AnonymousUser requests GET /api/catalog/{id} with ID=0, THE CatalogSystem SHALL return 400 error with message "Product ID must be positive"
5. WHEN AnonymousUser requests GET /api/catalog/{id} with non-numeric ID, THE CatalogSystem SHALL return 400 error with message "Product ID must be an integer"

**Business Rule Violations:**
6. IF product ID does not exist in database, THEN THE CatalogSystem SHALL return 404 error with message "Product with id '{id}' not found"

**Error Handling:**
7. IF database connection fails during retrieval, THEN THE CatalogSystem SHALL return 500 error with correlation ID
8. IF product has invalid foreign key (orphaned brand/type), THEN THE CatalogSystem SHALL return 500 error and log data integrity issue

**Assumptions & Notes:**
- Product IDs are integers (auto-increment or migrated from HiLo sequence)
- Navigation properties (CatalogBrand, CatalogType) are always present (foreign key constraints enforced)
- Image may be default "dummy.png" if no custom image uploaded

---

### Requirement 3: Create Product

**User Story:** As an authenticated administrator, I want to create new products with all required fields and optional images, so that I can expand the catalog inventory.

**Background:**
The legacy Create page requires authentication (OpenID Connect) and validates all input fields. The modern system must require JWT authentication, validate inputs using Pydantic schemas, and support optional image upload via a separate endpoint. Product creation is a critical write operation that must maintain data integrity and handle image uploads atomically.

**Scope:**
- **In scope**: Product creation with all fields, image upload and association, validation, authentication
- **Out of scope**: Bulk import, CSV upload, image editing after creation (separate update flow)

**Business Rules:**
- Authentication is required (JWT token)
- Name is required, max 50 characters
- Price must be between 0 and 1,000,000 with max 2 decimal places
- Stock fields (availableStock, restockThreshold, maxStockThreshold) must be between 0 and 10,000,000
- CatalogBrandId and CatalogTypeId must reference existing entities
- If no image uploaded, pictureFileName defaults to "dummy.png"
- If image uploaded, it must be moved from temp storage to permanent storage atomically

#### Acceptance Criteria

**Happy Path:**
1. WHEN AuthenticatedUser submits POST /api/catalog with all required fields, THE CatalogSystem SHALL create product and return 201 with created product data
2. WHEN product is created without image, THE CatalogSystem SHALL set pictureFileName to "dummy.png"
3. WHEN product is created with tempImageName, THE CatalogSystem SHALL call ImageService.UpdateImage() to move image from temp to permanent storage
4. WHEN product is successfully created, THE CatalogSystem SHALL return Location header with /api/catalog/{id}

**Validation & Edge Cases:**
5. WHEN AuthenticatedUser submits request without name field, THE CatalogSystem SHALL return 400 error with message "The Name field is required"
6. WHEN AuthenticatedUser submits price=1000001, THE CatalogSystem SHALL return 400 error with message "Price must be between 0 and 1,000,000"
7. WHEN AuthenticatedUser submits price=99.999, THE CatalogSystem SHALL return 400 error with message "Price must have maximum 2 decimal places"
8. WHEN AuthenticatedUser submits availableStock=-1, THE CatalogSystem SHALL return 400 error with message "Stock must be between 0 and 10,000,000"
9. WHEN AuthenticatedUser submits catalogBrandId that does not exist, THE CatalogSystem SHALL return 400 error with message "CatalogBrand with id '{id}' not found"
10. WHEN AuthenticatedUser submits catalogTypeId that does not exist, THE CatalogSystem SHALL return 400 error with message "CatalogType with id '{id}' not found"

**Business Rule Violations:**
11. IF AnonymousUser attempts POST /api/catalog, THEN THE CatalogSystem SHALL return 401 error with message "Authentication required"
12. IF tempImageName references non-existent temp image, THEN THE CatalogSystem SHALL return 400 error with message "Temp image not found"

**Error Handling:**
13. IF database insert fails, THEN THE CatalogSystem SHALL return 500 error, log exception with structlog, and NOT move temp image
14. IF database insert succeeds but image move fails, THEN THE CatalogSystem SHALL log error and set pictureFileName to "dummy.png" (compensating action)
15. IF database constraint violation occurs (e.g., name too long), THEN THE CatalogSystem SHALL return 400 error with specific constraint message

**Assumptions & Notes:**
- Product ID is auto-generated (auto-increment PRIMARY KEY, not HiLo sequence)
- Image upload is a separate operation (POST /api/catalog/images) that returns tempImageName
- Image move operation is NOT in a database transaction (compensating action on failure)
- JWT token validation happens in middleware before route handler

---

### Requirement 4: Upload Product Image

**User Story:** As an authenticated administrator, I want to upload product images to temporary storage during product creation/editing, so that I can preview images before finalizing the product.

**Background:**
The legacy system uses an unauthenticated AJAX endpoint (PicUploader.asmx) to upload images to temp storage. This is a **critical security issue**. The modern system must require JWT authentication, validate file format and size, and return a temporary image URL for preview. This is a prerequisite step for product creation/editing workflows.

**Scope:**
- **In scope**: Image upload to temp storage, format/size validation, authentication, temp URL generation
- **Out of scope**: Image editing, cropping, compression (future enhancement), direct permanent storage upload

**Business Rules:**
- Authentication is required (JWT token) — **MUST FIX security issue from legacy**
- Supported formats: JPEG, PNG, GIF only
- Maximum file size: 5MB (new requirement, not in legacy)
- Temp images stored in `pics/temp/{guid}/` or similar isolated location
- Temp image path returned as tempImageName for use in product create/edit requests
- Temp images are NOT automatically cleaned up (manual cleanup process or TTL-based deletion)

#### Acceptance Criteria

**Happy Path:**
1. WHEN AuthenticatedUser uploads image file via POST /api/catalog/images with valid JPEG/PNG/GIF, THE CatalogSystem SHALL validate format and upload to temp storage
2. WHEN image upload succeeds, THE CatalogSystem SHALL return 200 with JSON containing tempImageUrl and tempImageName
3. WHEN temp image is uploaded, THE ImageService SHALL generate unique path with GUID to prevent collisions

**Validation & Edge Cases:**
4. WHEN AuthenticatedUser uploads file >5MB, THE CatalogSystem SHALL return 400 error with message "File size must not exceed 5MB"
5. WHEN AuthenticatedUser uploads file with invalid format (e.g., PDF, TXT), THE CatalogSystem SHALL return 400 error with message "Image format must be JPEG, PNG, or GIF"
6. WHEN AuthenticatedUser uploads corrupted image file, THE CatalogSystem SHALL return 400 error with message "Invalid image file"
7. WHEN AuthenticatedUser uploads image with no file extension, THE CatalogSystem SHALL return 400 error with message "Filename must have extension"

**Business Rule Violations:**
8. IF AnonymousUser attempts POST /api/catalog/images, THEN THE CatalogSystem SHALL return 401 error with message "Authentication required" — **FIXES LEGACY SECURITY ISSUE**

**Error Handling:**
9. IF temp storage write fails (disk full, permissions), THEN THE CatalogSystem SHALL return 500 error and log storage error with structlog
10. IF ImageService is unavailable, THEN THE CatalogSystem SHALL return 503 error with message "Image service unavailable"

**Assumptions & Notes:**
- Image format validation uses Python Pillow library (Image.open())
- File size check happens before upload to prevent resource exhaustion
- Temp image cleanup is NOT part of this requirement (separate maintenance task)
- Temp images have no TTL in initial implementation (can be added later)

---

### Requirement 5: Update Product

**User Story:** As an authenticated administrator, I want to update existing products including replacing images, so that I can correct errors and keep catalog information current.

**Background:**
The legacy Edit page pre-populates form fields with existing product data and allows replacing the product image. The modern system must support partial updates (only changed fields), preserve existing image if not replaced, and handle image replacement atomically. This is a frequently used operation for inventory and price updates.

**Scope:**
- **In scope**: Product field updates, image replacement, validation, authentication
- **Out of scope**: Partial field updates (PUT requires all fields), PATCH support (future), bulk updates

**Business Rules:**
- Authentication is required (JWT token)
- Same validation rules as Create (name, price, stock ranges)
- Product ID must exist (404 if not found)
- If tempImageName provided, replace existing image (delete old, move new from temp)
- If tempImageName not provided, preserve existing pictureFileName
- PictureFileName field is read-only in legacy UI (not directly editable) — enforce in API

#### Acceptance Criteria

**Happy Path:**
1. WHEN AuthenticatedUser submits PUT /api/catalog/{id} with all fields and no tempImageName, THE CatalogSystem SHALL update product and preserve existing image
2. WHEN AuthenticatedUser submits PUT /api/catalog/{id} with tempImageName, THE CatalogSystem SHALL delete old product images and move temp image to permanent storage
3. WHEN product update succeeds, THE CatalogSystem SHALL return 200 with updated product data

**Validation & Edge Cases:**
4. WHEN AuthenticatedUser submits PUT with missing required field, THE CatalogSystem SHALL return 400 error with message "The {field} field is required"
5. WHEN AuthenticatedUser submits PUT with invalid price/stock values, THE CatalogSystem SHALL return 400 error with validation message (same as Create)
6. WHEN AuthenticatedUser attempts to directly set pictureFileName (not via tempImageName), THE CatalogSystem SHALL ignore pictureFileName field and log warning

**Business Rule Violations:**
7. IF product ID does not exist, THEN THE CatalogSystem SHALL return 404 error with message "Product with id '{id}' not found"
8. IF AnonymousUser attempts PUT /api/catalog/{id}, THEN THE CatalogSystem SHALL return 401 error with message "Authentication required"
9. IF tempImageName references non-existent temp image, THEN THE CatalogSystem SHALL return 400 error with message "Temp image not found"

**Error Handling:**
10. IF old image deletion fails, THEN THE CatalogSystem SHALL log warning and proceed with update (best effort cleanup)
11. IF temp image move succeeds but database update fails, THEN THE CatalogSystem SHALL leave new image in storage and return 500 error (orphaned image)
12. IF database update succeeds but old image deletion fails, THEN THE CatalogSystem SHALL log warning and return 200 (orphaned image)

**Assumptions & Notes:**
- Update operation uses PUT (full resource replacement), not PATCH
- Image replacement is NOT atomic with database update (compensating actions on failure)
- Old images may be orphaned if deletion fails (cleanup task needed)
- Optimistic concurrency control is NOT implemented (last write wins)

---

### Requirement 6: Delete Product

**User Story:** As an authenticated administrator, I want to delete products from the catalog, so that I can remove discontinued or erroneous items.

**Background:**
The legacy Delete page displays product details and requires confirmation before deletion. The modern system must provide a REST DELETE endpoint with authentication, delete the database record, and clean up associated images. **IMPORTANT**: The legacy system does NOT delete images (identified as defect in discovery) — modern system MUST delete images.

**Scope:**
- **In scope**: Product deletion, image cleanup, authentication, confirmation
- **Out of scope**: Soft delete, audit trail (future), cascade delete of related entities (brands/types are shared)

**Business Rules:**
- Authentication is required (JWT token)
- Product ID must exist (404 if not found)
- Database record must be deleted atomically (single transaction)
- Product image must be deleted from storage (NEW REQUIREMENT — not in legacy)
- Foreign key constraints prevent deletion of CatalogBrand or CatalogType if referenced by other products

#### Acceptance Criteria

**Happy Path:**
1. WHEN AuthenticatedUser sends DELETE /api/catalog/{id} with valid ID, THE CatalogSystem SHALL delete product record from database
2. WHEN product is deleted, THE CatalogSystem SHALL call ImageService.DeleteImage() to remove product images from storage — **FIXES LEGACY DEFECT**
3. WHEN deletion succeeds, THE CatalogSystem SHALL return 204 No Content

**Validation & Edge Cases:**
4. WHEN AuthenticatedUser sends DELETE with ID=0 or negative, THE CatalogSystem SHALL return 400 error with message "Product ID must be positive"

**Business Rule Violations:**
5. IF product ID does not exist, THEN THE CatalogSystem SHALL return 404 error with message "Product with id '{id}' not found"
6. IF AnonymousUser attempts DELETE /api/catalog/{id}, THEN THE CatalogSystem SHALL return 401 error with message "Authentication required"

**Error Handling:**
7. IF database delete fails (foreign key violation), THEN THE CatalogSystem SHALL return 409 error with message "Cannot delete product: referenced by other entities"
8. IF database delete succeeds but image deletion fails, THEN THE CatalogSystem SHALL log warning and return 204 (orphaned image)
9. IF database connection fails, THEN THE CatalogSystem SHALL return 500 error and NOT delete images

**Assumptions & Notes:**
- Delete operation is permanent (no soft delete or recycle bin)
- Image deletion is best-effort (not atomic with database delete)
- Orphaned images from failed deletions require separate cleanup process
- No confirmation dialog at API level (confirmation handled in UI)

---

### Requirement 7: List Catalog Brands (Reference Data)

**User Story:** As a user (anonymous or authenticated), I want to retrieve the list of all catalog brands, so that I can populate dropdowns in create/edit forms or filter products by brand (future).

**Background:**
The legacy system loads brands into dropdown lists in Create/Edit pages. The modern system must provide a REST endpoint that returns all brands for populating UI select components. This is reference data that changes infrequently.

**Scope:**
- **In scope**: List all brands (no pagination), simple ID/Name pairs
- **Out of scope**: Brand CRUD operations (separate admin feature), brand filtering, sorting

**Business Rules:**
- No authentication required (public reference data)
- Brands are ordered by ID ascending (deterministic)
- Empty result set is valid (return empty array)

#### Acceptance Criteria

**Happy Path:**
1. WHEN AnonymousUser requests GET /api/catalog/brands, THE CatalogSystem SHALL return array of all brands with id and brand fields
2. WHEN brands list is empty, THE CatalogSystem SHALL return 200 status with empty array

**Error Handling:**
3. IF database connection fails, THEN THE CatalogSystem SHALL return 500 error with correlation ID

**Assumptions & Notes:**
- No pagination (reference data is small, <100 brands expected)
- Can be cached client-side or server-side (future enhancement)
- Brands are ordered by ID ascending for deterministic results

---

### Requirement 8: List Catalog Types (Reference Data)

**User Story:** As a user (anonymous or authenticated), I want to retrieve the list of all catalog types, so that I can populate dropdowns in create/edit forms or filter products by type (future).

**Background:**
The legacy system loads types into dropdown lists in Create/Edit pages. The modern system must provide a REST endpoint that returns all types for populating UI select components. This is reference data that changes infrequently.

**Scope:**
- **In scope**: List all types (no pagination), simple ID/Name pairs
- **Out of scope**: Type CRUD operations (separate admin feature), type filtering, sorting

**Business Rules:**
- No authentication required (public reference data)
- Types are ordered by ID ascending (deterministic)
- Empty result set is valid (return empty array)

#### Acceptance Criteria

**Happy Path:**
1. WHEN AnonymousUser requests GET /api/catalog/types, THE CatalogSystem SHALL return array of all types with id and type fields
2. WHEN types list is empty, THE CatalogSystem SHALL return 200 status with empty array

**Error Handling:**
3. IF database connection fails, THEN THE CatalogSystem SHALL return 500 error with correlation ID

**Assumptions & Notes:**
- No pagination (reference data is small, <50 types expected)
- Can be cached client-side or server-side (future enhancement)
- Types are ordered by ID ascending for deterministic results

---

## Non-Functional Requirements

### Performance
- API P95 latency < 500ms for list operations
- API P95 latency < 200ms for single-item retrieval
- Image upload must complete within 10 seconds for 5MB file
- Database queries must use indexed columns (id, catalogBrandId, catalogTypeId)
- Pagination must support datasets up to 100,000 products without performance degradation

### Security
- JWT authentication required for all write operations (POST, PUT, DELETE)
- JWT authentication required for image upload endpoint
- Input validation using Pydantic (backend) and Zod (frontend)
- SQL injection prevention via SQLAlchemy ORM (no raw SQL)
- File upload size limited to 5MB
- File upload format restricted to JPEG, PNG, GIF
- CORS policy configured for allowed origins only (no wildcard in production)
- Rate limiting on image upload endpoint (10 uploads per minute per user)

### Observability
- All API requests logged with method, path, status, duration, user_id using structlog
- All errors logged with exception details, stack trace, correlation ID
- Request correlation IDs propagated through all log entries
- Metrics tracked: request count, error rate, latency (P50, P95, P99)
- Structured JSON logs for centralized logging (ELK, Splunk, etc.)

### Resilience
- Database query timeout: 30 seconds
- Image upload timeout: 10 seconds
- Connection pooling: 5-10 async connections
- Graceful degradation: Log errors and return 500 with correlation ID (never crash)
- Health check endpoint: GET /health (returns 200 if database accessible)

### Accessibility
- All form fields must have labels or aria-label attributes
- All images must have alt text (alt="" for decorative images)
- Keyboard navigation supported for all interactive elements
- Screen reader compatibility (semantic HTML, ARIA attributes)
- Color contrast ratio ≥ 4.5:1 for text

### Compatibility
- Backend: Python 3.12+, PostgreSQL 13+ (or SQLite for development)
- Frontend: Modern browsers (Chrome, Firefox, Safari, Edge) with ES2020 support
- API: RESTful JSON endpoints (no XML, SOAP, or GraphQL)
- Authentication: JWT tokens with RS256 algorithm

---

## Constraints

### Technical Constraints
- Must use FastAPI framework for backend (per CLAUDE.md)
- Must use React 18 with TypeScript for frontend (per CLAUDE.md)
- Must use async SQLAlchemy 2.x for database access (per CLAUDE.md)
- Must use Pydantic v2 for request/response models (per CLAUDE.md)
- Must replace HiLo sequence with auto-increment PRIMARY KEY (migration constraint)
- Must implement IImageService adapter pattern for storage abstraction (per CLAUDE.md)

### Business Constraints
- Must maintain 100% functional parity with legacy system (no feature loss)
- Must support existing database schema (Catalog, CatalogBrand, CatalogType tables)
- Must migrate all existing product data without loss (zero data loss requirement)
- Must migrate all existing product images (preserve image URLs)

### Regulatory Constraints
- None identified (no PII, GDPR, HIPAA, or PCI-DSS requirements)

### Operational Constraints
- Maximum acceptable downtime during migration: 4 hours
- Rollback plan required before production deployment
- Smoke tests must pass before traffic switch (see spec.md)

---

## Traceability Matrix

| Requirement | Evidence (Legacy) | Evidence (Discovery) | API Endpoint |
|-------------|------------------|---------------------|--------------|
| Req 1: List Products | Default.aspx.cs:31-40, CatalogService.cs:20-29 | discovery.md:46-69 | GET /api/catalog |
| Req 2: View Details | Details.aspx.cs:17-23, CatalogService.cs:36-38 | discovery.md:71-92 | GET /api/catalog/{id} |
| Req 3: Create Product | Create.aspx.cs:50-81, CatalogService.cs:50-54 | discovery.md:94-129 | POST /api/catalog |
| Req 4: Upload Image | PicUploader.asmx.cs:32-62, ImageService | discovery.md:194-224 | POST /api/catalog/images |
| Req 5: Update Product | Edit.aspx.cs:62-88, CatalogService.cs:57-60 | discovery.md:131-165 | PUT /api/catalog/{id} |
| Req 6: Delete Product | Delete.aspx.cs:34-36, CatalogService.cs:63-66 | discovery.md:167-193 | DELETE /api/catalog/{id} |
| Req 7: List Brands | Create.aspx.cs:40-43, CatalogService.cs:44-47 | discovery.md:306-320 | GET /api/catalog/brands |
| Req 8: List Types | Create.aspx.cs:45-47, CatalogService.cs:40-42 | discovery.md:306-320 | GET /api/catalog/types |

---

## Acceptance

This requirements document is complete and ready for design when all acceptance criteria are reviewed and approved by stakeholders.

**Approver**: [To be filled]
**Date**: [To be filled]

---

**Document Version**: 1.0
**Last Updated**: 2026-03-03
**Status**: Ready for Design Phase
