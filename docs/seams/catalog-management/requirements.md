# Requirements Document: Catalog Management

## Introduction

The catalog management seam provides complete CRUD (Create, Read, Update, Delete) functionality for product catalog items in the eShop application. This seam enables administrators to manage the product catalog through a web interface, including product information (name, description, pricing, stock levels), categorization (brand and type), and product images. The system supports paginated browsing of catalog items, detailed product views, and image upload capabilities.

**Business Context**: This seam is the core administrative interface for maintaining the eShop product catalog. It replaces the legacy ASP.NET WebForms implementation with a modern Python FastAPI backend and React frontend, maintaining exact functional parity with the original system. The catalog serves as the foundation for the eShop's product data, which is consumed by other systems for order processing and customer-facing displays.

**Migration Scope**: This is a like-to-like migration from ASP.NET WebForms 4.7.2 to Python FastAPI + React. All existing functionality, validation rules, UI layout, and business logic will be preserved exactly as implemented in the legacy system.

## Glossary

- **Catalog_System**: The backend FastAPI service responsible for catalog item CRUD operations, data validation, and business rule enforcement
- **Catalog_UI**: The React frontend application providing the user interface for catalog management
- **Database_Service**: SQLAlchemy async ORM layer managing database connections and queries
- **Image_Service**: Backend service handling product image uploads, storage, and retrieval
- **Auth_Service**: Authentication service managing user sessions and access control (JWT-based)
- **Catalog_Item**: A product entity in the catalog with properties: Id, Name, Description, Price, PictureFileName, Brand, Type, Stock levels
- **Brand**: A product brand/manufacturer category (lookup table)
- **Type**: A product type/category (lookup table)
- **Page_Size**: Number of catalog items displayed per page (default: 10)
- **Page_Index**: Zero-based page number for pagination (default: 0)

## Requirements

### Requirement 1: List Catalog Items with Pagination

**User Story:** As a catalog administrator, I want to view a paginated list of all catalog items with their key details, so that I can browse and manage the product catalog efficiently.

**Background:**
The catalog list is the primary entry point for catalog management. Administrators need to see all products at a glance, with essential information displayed in a table format. The legacy system displays 10 items per page by default, sorted by ID ascending, with pagination controls to navigate between pages. This view includes thumbnail images, product names, descriptions, brand/type categorization, pricing, and stock levels. The list provides quick access to Edit, Details, and Delete actions for each item.

**Scope:**
- **In scope**: Display paginated catalog items, table rendering with all columns, pagination controls (Next/Previous), navigation to CRUD pages, thumbnail image display
- **Out of scope**: Filtering by brand/type, searching by name, sorting by different columns, bulk operations

**Business Rules:**
- Default page size is 10 items (configurable via query parameter)
- Default page index is 0 (first page, zero-based indexing)
- Items are sorted by Id in ascending order (fixed sort order)
- All items include related Brand and Type data (eager loaded)
- Image URIs are constructed with prefix "/Pics/" + PictureFileName
- Price is displayed with "$" prefix (CSS-based formatting)
- Pagination shows "Previous" button only if pageIndex > 0
- Pagination shows "Next" button only if more pages exist
- Each row displays action links: Edit, Details, Delete

#### Acceptance Criteria

**Happy Path:**
1. WHEN the catalog list page loads, THE Catalog_System SHALL retrieve catalog items using default pagination (pageSize=10, pageIndex=0)
2. WHEN catalog items are retrieved, THE Catalog_System SHALL include related CatalogBrand and CatalogType data via eager loading
3. WHEN catalog items are retrieved, THE Catalog_System SHALL order results by Id in ascending order
4. WHEN catalog items are returned, THE Catalog_System SHALL return a paginated response with items array and pagination metadata (page, limit, total_items, total_pages)
5. WHEN the catalog list page renders, THE Catalog_UI SHALL display items in a table with columns: Image (thumbnail), Name, Description, Brand, Type, Price, Picture name, Stock, Restock, Max stock, Actions
6. WHEN displaying catalog items, THE Catalog_UI SHALL render thumbnail images with max-width 120px using PictureUri
7. WHEN displaying prices, THE Catalog_UI SHALL prepend "$" symbol using CSS class "esh-price"
8. WHEN displaying pagination controls, THE Catalog_UI SHALL show "Previous" button only if pageIndex > 0
9. WHEN displaying pagination controls, THE Catalog_UI SHALL show "Next" button only if current page < total_pages - 1
10. WHEN user clicks "Create New" button, THE Catalog_UI SHALL navigate to the create catalog item page

**Pagination:**
11. WHEN user clicks "Next" button, THE Catalog_UI SHALL increment pageIndex by 1 and reload the catalog list
12. WHEN user clicks "Previous" button, THE Catalog_UI SHALL decrement pageIndex by 1 and reload the catalog list
13. WHEN pageIndex changes, THE Catalog_System SHALL apply OFFSET calculation as (pageSize * pageIndex)
14. WHEN pageIndex changes, THE Catalog_System SHALL return the correct page of results using LIMIT and OFFSET

**Validation & Edge Cases:**
15. WHEN pageSize parameter is provided, THE Catalog_System SHALL validate it is between 1 and 100
16. WHEN pageSize parameter is invalid, THE Catalog_System SHALL return 400 error with message "Invalid page size: must be between 1 and 100"
17. WHEN pageIndex parameter is negative, THE Catalog_System SHALL return 400 error with message "Invalid page index: must be >= 0"
18. WHEN no catalog items exist, THE Catalog_System SHALL return empty items array with total_items=0
19. WHEN no catalog items exist, THE Catalog_UI SHALL display message "No catalog items found"

**Error Handling:**
20. IF database connection fails, THEN THE Catalog_System SHALL return 500 error with message "Database connection failed" and log the error with correlation ID
21. IF catalog service is unavailable, THEN THE Catalog_UI SHALL display error message "Failed to load catalog items. Please try again."

**Assumptions & Notes:**
- Pagination state persists in URL query parameters (?pageSize=10&pageIndex=0)
- Images are served from "/Pics/" directory (file system or cloud storage)
- Brand and Type data is always available (FK constraint ensures referential integrity)
- No filtering or sorting UI controls in legacy system (out of scope)

---

### Requirement 2: Create Catalog Item

**User Story:** As a catalog administrator, I want to create new catalog items with all required information and an optional product image, so that I can add new products to the catalog.

**Background:**
The create functionality allows administrators to add new products to the catalog. The form collects all product details including name, description, brand, type, pricing, and stock levels. Image upload is optional and handled asynchronously on the client side with preview. The legacy system uses HiLo ID generation pattern, validates all inputs server-side, and redirects to the catalog list upon successful creation. If no image is uploaded, the system uses a default "dummy.png" placeholder.

**Scope:**
- **In scope**: Form inputs for all catalog item fields, brand/type dropdown lookups, image upload with preview, server-side validation, database insertion, redirect on success
- **Out of scope**: Image editing/cropping, multiple image upload, product variants, inventory management

**Business Rules:**
- Name: Required, MaxLength 50 characters
- Description: Optional (no validation)
- Price: Required, must be between 0 and 999999999.99, displayed with 2 decimal places, currency format
- AvailableStock: Required, must be between 0 and 10000000, integer
- RestockThreshold: Required, must be between 0 and 10000000, integer
- MaxStockThreshold: Required, must be between 0 and 10000000, integer
- Brand: Required (selected from dropdown, FK constraint)
- Type: Required (selected from dropdown, FK constraint)
- Image: Optional, defaults to "dummy.png" if not provided
- ID generation: Auto-increment (replacing legacy HiLo pattern)
- On success: Redirect to catalog list page (/)

#### Acceptance Criteria

**Happy Path:**
1. WHEN the create page loads, THE Catalog_System SHALL retrieve all brands via GET /api/catalog/brands endpoint
2. WHEN the create page loads, THE Catalog_System SHALL retrieve all types via GET /api/catalog/types endpoint
3. WHEN the create page renders, THE Catalog_UI SHALL populate Brand dropdown with brand names and IDs
4. WHEN the create page renders, THE Catalog_UI SHALL populate Type dropdown with type names and IDs
5. WHEN user fills form and clicks Create button, THE Catalog_UI SHALL validate required fields client-side before submission
6. WHEN user submits valid form, THE Catalog_UI SHALL send POST request to /api/catalog/items with form data as JSON
7. WHEN catalog item creation request is received, THE Catalog_System SHALL validate all required fields are present
8. WHEN all validations pass, THE Catalog_System SHALL insert new catalog item into Catalog table
9. WHEN image was uploaded, THE Image_Service SHALL copy image file to storage directory "/Pics/{filename}"
10. WHEN catalog item is created successfully, THE Catalog_System SHALL return 201 Created with catalog item JSON including generated ID
11. WHEN creation succeeds, THE Catalog_UI SHALL navigate to catalog list page (/)

**Input Validation:**
12. WHEN Name is empty, THE Catalog_System SHALL return 400 error with message "Name is required"
13. WHEN Name exceeds 50 characters, THE Catalog_System SHALL return 400 error with message "Name must not exceed 50 characters"
14. WHEN Price is empty, THE Catalog_System SHALL return 400 error with message "Price is required"
15. WHEN Price is negative, THE Catalog_System SHALL return 400 error with message "Price must be greater than or equal to 0"
16. WHEN Price exceeds 999999999.99, THE Catalog_System SHALL return 400 error with message "Price must not exceed 999999999.99"
17. WHEN Price has more than 2 decimal places, THE Catalog_System SHALL return 400 error with message "Price must have at most 2 decimal places"
18. WHEN AvailableStock is negative, THE Catalog_System SHALL return 400 error with message "Available stock must be between 0 and 10000000"
19. WHEN AvailableStock exceeds 10000000, THE Catalog_System SHALL return 400 error with message "Available stock must be between 0 and 10000000"
20. WHEN RestockThreshold is negative, THE Catalog_System SHALL return 400 error with message "Restock threshold must be between 0 and 10000000"
21. WHEN MaxStockThreshold is negative, THE Catalog_System SHALL return 400 error with message "Max stock threshold must be between 0 and 10000000"
22. WHEN Brand is not selected, THE Catalog_System SHALL return 400 error with message "Brand is required"
23. WHEN Type is not selected, THE Catalog_System SHALL return 400 error with message "Type is required"

**Business Rule Violations:**
24. IF Brand ID does not exist in CatalogBrand table, THEN THE Catalog_System SHALL return 400 error with message "Invalid brand ID"
25. IF Type ID does not exist in CatalogType table, THEN THE Catalog_System SHALL return 400 error with message "Invalid type ID"

**Image Upload:**
26. WHEN user selects image file, THE Catalog_UI SHALL upload image to server and store temporary filename in TempImageName field
27. WHEN image upload succeeds, THE Catalog_UI SHALL display image preview in esh-picture container (max-width 370px)
28. WHEN no image is uploaded, THE Catalog_System SHALL set PictureFileName to "dummy.png"
29. WHEN image file exceeds 10MB, THE Image_Service SHALL return 400 error with message "Image file too large: maximum 10MB"
30. WHEN image format is not jpg/png, THE Image_Service SHALL return 400 error with message "Invalid image format: only jpg and png allowed"

**Error Handling:**
31. IF database insert fails due to constraint violation, THEN THE Catalog_System SHALL return 409 error with message "Catalog item could not be created: constraint violation"
32. IF database connection fails, THEN THE Catalog_System SHALL return 500 error with message "Database connection failed" and log error with correlation ID
33. IF image storage fails, THEN THE Image_Service SHALL log error but allow catalog item creation to proceed with "dummy.png"

**Authorization:**
34. WHEN unauthenticated user attempts to access create page, THE Catalog_System SHALL return 401 error with message "Authentication required"
35. WHEN authenticated user accesses create page, THE Catalog_System SHALL verify user has valid JWT token

**Assumptions & Notes:**
- Image upload is asynchronous and completes before form submission
- TempImageName hidden field stores the uploaded image filename
- Legacy HiLo ID generation replaced with database auto-increment
- No transaction scope needed (single database operation)
- Cancel button navigates to catalog list without saving

---

### Requirement 3: Edit Catalog Item

**User Story:** As a catalog administrator, I want to edit existing catalog items to update product information and optionally replace the product image, so that I can keep the catalog up to date.

**Background:**
The edit functionality allows administrators to modify existing catalog items. The form is pre-populated with current values and follows the same validation rules as creation. The PictureFileName field is read-only in the UI (cannot be manually edited), but the image can be replaced via upload. The legacy system uses Entity Framework's change tracking to detect modifications and update only changed fields. On success, the user is redirected to the catalog list.

**Scope:**
- **In scope**: Load existing catalog item, pre-populate form, update all fields except PictureFileName (read-only in UI), optional image replacement, server-side validation, database update, redirect on success
- **Out of scope**: Audit logging of changes, version history, partial updates (PATCH)

**Business Rules:**
- Same validation rules as Create (Requirement 2)
- PictureFileName field is read-only in UI (disabled input, tooltip "Not allowed for edition")
- Image can be replaced by uploading new image (TempImageName field)
- If no new image uploaded, existing PictureFileName is preserved
- ID is read-only (from URL route parameter)
- On success: Redirect to catalog list page (/)

#### Acceptance Criteria

**Happy Path:**
1. WHEN edit page URL is accessed with product ID, THE Catalog_System SHALL retrieve catalog item by ID via GET /api/catalog/items/{id}
2. WHEN catalog item is retrieved, THE Catalog_System SHALL include related Brand and Type data
3. WHEN catalog item is not found, THE Catalog_System SHALL return 404 error with message "Catalog item not found"
4. WHEN edit page renders, THE Catalog_UI SHALL pre-populate form fields with catalog item data
5. WHEN edit page renders, THE Catalog_UI SHALL display PictureFileName field as read-only with tooltip "Not allowed for edition"
6. WHEN edit page renders, THE Catalog_UI SHALL display current product image using PictureFileName
7. WHEN edit page renders, THE Catalog_UI SHALL populate Brand dropdown with current brand selected
8. WHEN edit page renders, THE Catalog_UI SHALL populate Type dropdown with current type selected
9. WHEN user modifies form and clicks Save button, THE Catalog_UI SHALL send PUT request to /api/catalog/items/{id} with updated data
10. WHEN update request is received, THE Catalog_System SHALL validate all fields using same rules as Create
11. WHEN all validations pass, THE Catalog_System SHALL update catalog item in database using ID from URL
12. WHEN new image was uploaded, THE Image_Service SHALL replace existing image file in "/Pics/" directory
13. WHEN update succeeds, THE Catalog_System SHALL return 200 OK with updated catalog item JSON
14. WHEN update succeeds, THE Catalog_UI SHALL navigate to catalog list page (/)

**Input Validation:**
15. WHEN any validation rule fails, THE Catalog_System SHALL return 400 error with same validation messages as Create (Requirement 2.12-23)

**Business Rule Violations:**
16. IF Brand ID does not exist, THEN THE Catalog_System SHALL return 400 error with message "Invalid brand ID"
17. IF Type ID does not exist, THEN THE Catalog_System SHALL return 400 error with message "Invalid type ID"

**Image Replacement:**
18. WHEN user uploads new image, THE Catalog_UI SHALL upload image to server and store temporary filename in TempImageName field
19. WHEN new image upload succeeds, THE Catalog_UI SHALL display new image preview
20. WHEN TempImageName is populated on save, THE Image_Service SHALL copy new image file to "/Pics/{filename}"
21. WHEN TempImageName is empty on save, THE Catalog_System SHALL preserve existing PictureFileName unchanged
22. WHEN new image file exceeds 10MB, THE Image_Service SHALL return 400 error with message "Image file too large: maximum 10MB"

**Error Handling:**
23. IF catalog item ID does not exist, THEN THE Catalog_System SHALL return 404 error with message "Catalog item with ID {id} not found"
24. IF database update fails due to constraint violation, THEN THE Catalog_System SHALL return 409 error with message "Catalog item could not be updated: constraint violation"
25. IF database connection fails, THEN THE Catalog_System SHALL return 500 error with message "Database connection failed" and log error with correlation ID
26. IF image replacement fails, THEN THE Image_Service SHALL log error but allow catalog item update to proceed with existing PictureFileName

**Concurrency:**
27. WHILE two users edit the same catalog item simultaneously, THE Catalog_System SHALL allow last-write-wins behavior (no optimistic concurrency control in legacy)

**Authorization:**
28. WHEN unauthenticated user attempts to access edit page, THE Catalog_System SHALL return 401 error with message "Authentication required"
29. WHEN authenticated user accesses edit page, THE Catalog_System SHALL verify user has valid JWT token

**Assumptions & Notes:**
- No optimistic concurrency control (no version/timestamp checking)
- PictureFileName cannot be directly edited via form input (UI enforces this)
- Legacy system used Entity Framework change tracking; modern system will use explicit UPDATE statement
- Cancel button navigates to catalog list without saving changes

---

### Requirement 4: Delete Catalog Item

**User Story:** As a catalog administrator, I want to delete catalog items with confirmation, so that I can remove discontinued or incorrect products from the catalog.

**Background:**
The delete functionality provides a two-step process: first displaying a confirmation page with full item details, then executing the deletion upon confirmation. The confirmation page shows all catalog item fields in read-only format to ensure the administrator is deleting the correct item. The legacy system does NOT delete the associated image file when deleting a catalog item, leaving orphaned files in storage. This behavior is preserved in the migration (like-to-like).

**Scope:**
- **In scope**: Confirmation page with item details, delete confirmation, database deletion, redirect on success
- **Out of scope**: Cascade delete of related records, image file cleanup, soft delete/archiving, undo functionality

**Business Rules:**
- Confirmation page displays all catalog item fields in read-only format
- Image is displayed on confirmation page
- Delete button executes deletion and redirects to catalog list
- Cancel button returns to catalog list without deleting
- Image file is NOT deleted from storage (legacy behavior - potential file system leak)
- FK constraints are preserved (only the catalog item is deleted, not related Brand/Type records)
- On success: Redirect to catalog list page (/)

#### Acceptance Criteria

**Happy Path:**
1. WHEN delete confirmation page URL is accessed with product ID, THE Catalog_System SHALL retrieve catalog item by ID via GET /api/catalog/items/{id}
2. WHEN catalog item is retrieved, THE Catalog_System SHALL include related Brand and Type data
3. WHEN delete confirmation page renders, THE Catalog_UI SHALL display confirmation message "Are you sure you want to delete this?"
4. WHEN delete confirmation page renders, THE Catalog_UI SHALL display all catalog item fields in read-only format (Name, Description, Brand, Type, Price, Picture name, Stock, Restock, Max stock)
5. WHEN delete confirmation page renders, THE Catalog_UI SHALL display product image using PictureFileName
6. WHEN user clicks Delete button, THE Catalog_UI SHALL send DELETE request to /api/catalog/items/{id}
7. WHEN delete request is received, THE Catalog_System SHALL verify catalog item exists by ID
8. WHEN catalog item exists, THE Catalog_System SHALL delete catalog item from Catalog table using ID
9. WHEN deletion succeeds, THE Catalog_System SHALL return 204 No Content
10. WHEN deletion succeeds, THE Catalog_UI SHALL navigate to catalog list page (/)

**Validation & Edge Cases:**
11. WHEN catalog item ID does not exist, THE Catalog_System SHALL return 404 error with message "Catalog item not found"

**Business Rule Violations:**
12. IF catalog item has dependent records in other tables, THEN THE Catalog_System SHALL return 409 error with message "Cannot delete catalog item: referenced by other records" (if FK constraints exist)

**Error Handling:**
13. IF database delete fails, THEN THE Catalog_System SHALL return 500 error with message "Database operation failed" and log error with correlation ID
14. IF database connection fails, THEN THE Catalog_System SHALL return 500 error with message "Database connection failed" and log error with correlation ID

**Image File Handling:**
15. WHEN catalog item is deleted, THE Catalog_System SHALL NOT delete the associated image file from "/Pics/" directory (legacy behavior preserved)

**Authorization:**
16. WHEN unauthenticated user attempts to access delete page, THE Catalog_System SHALL return 401 error with message "Authentication required"
17. WHEN authenticated user accesses delete page, THE Catalog_System SHALL verify user has valid JWT token

**Assumptions & Notes:**
- No cascade delete logic (FK relationships preserved)
- Image files accumulate as orphans when items are deleted (documented technical debt)
- No soft delete or archiving (hard delete from database)
- Cancel button returns to catalog list without executing deletion
- Confirmation page is a separate route, not a modal dialog

---

### Requirement 5: View Catalog Item Details

**User Story:** As a catalog administrator, I want to view detailed information about a catalog item in read-only format, so that I can review product details without risk of accidental modification.

**Background:**
The details page provides a read-only view of all catalog item information. It serves as a safe way to inspect product data without entering edit mode. The page includes navigation buttons to return to the catalog list or proceed to edit the item. Unlike the Create/Edit pages, the Details page does NOT require authentication in the legacy system (public read access).

**Scope:**
- **In scope**: Display all catalog item fields in read-only format, product image display, navigation to edit page, navigation to catalog list
- **Out of scope**: Inline editing, version history, related product recommendations

**Business Rules:**
- All fields displayed in read-only format (no input controls)
- Image displayed at full preview size (max-width 370px)
- Edit button navigates to edit page for the same item
- Back to List button returns to catalog list
- No authentication required (public read access)

#### Acceptance Criteria

**Happy Path:**
1. WHEN details page URL is accessed with product ID, THE Catalog_System SHALL retrieve catalog item by ID via GET /api/catalog/items/{id}
2. WHEN catalog item is retrieved, THE Catalog_System SHALL include related Brand and Type data (eager loading)
3. WHEN catalog item is not found, THE Catalog_System SHALL return 404 error with message "Catalog item not found"
4. WHEN details page renders, THE Catalog_UI SHALL display all fields in read-only format: Name, Description, Brand (name), Type (name), Price, Picture name, Available Stock, Restock Threshold, Max Stock Threshold
5. WHEN details page renders, THE Catalog_UI SHALL display product image using PictureFileName with max-width 370px
6. WHEN details page renders, THE Catalog_UI SHALL display Price with "$" prefix using CSS class "esh-price"
7. WHEN user clicks "Back to list" button, THE Catalog_UI SHALL navigate to catalog list page (/)
8. WHEN user clicks "Edit" button, THE Catalog_UI SHALL navigate to edit page with current item ID (/catalog/edit/{id})

**Validation & Edge Cases:**
9. WHEN catalog item ID does not exist, THE Catalog_System SHALL return 404 error with message "Catalog item with ID {id} not found"
10. WHEN catalog item has null Description, THE Catalog_UI SHALL display empty string (not "null" or placeholder)
11. WHEN PictureFileName is "dummy.png", THE Catalog_UI SHALL display default placeholder image

**Error Handling:**
12. IF database query fails, THEN THE Catalog_System SHALL return 500 error with message "Database operation failed" and log error with correlation ID
13. IF database connection fails, THEN THE Catalog_System SHALL return 500 error with message "Database connection failed" and log error with correlation ID

**Authorization:**
14. WHEN unauthenticated user accesses details page, THE Catalog_System SHALL allow access without authentication (public read access)
15. WHEN authenticated user accesses details page, THE Catalog_System SHALL display same content as unauthenticated user (no additional data)

**Assumptions & Notes:**
- Details page is publicly accessible (no authentication required per legacy behavior)
- Edit button may require authentication when clicked (enforced on edit page, not details page)
- No audit logging of detail page views
- No related product recommendations or cross-sells

---

### Requirement 6: Brand and Type Lookups

**User Story:** As a catalog administrator, I want to select brands and types from dropdown lists when creating or editing catalog items, so that I can categorize products correctly.

**Background:**
The Brand and Type tables provide lookup data for categorizing catalog items. These tables are read-only from the catalog management seam (populated via seed data). The dropdown lists display all available brands and types, with Brand.Brand and Type.Type as display text and Brand.Id and Type.Id as values. The dropdowns are required fields and enforce referential integrity via foreign key constraints.

**Scope:**
- **In scope**: Retrieve all brands, retrieve all types, populate dropdowns, enforce FK constraints
- **Out of scope**: Adding new brands/types via UI, editing brands/types, deleting brands/types, brand/type hierarchies

**Business Rules:**
- Brand and Type data is read-only (no CRUD operations in this seam)
- All brands and types are retrieved without pagination (small lookup tables)
- Brands are ordered by Brand name ascending
- Types are ordered by Type name ascending
- Foreign key constraints enforce that CatalogBrandId and CatalogTypeId must exist in respective tables

#### Acceptance Criteria

**Happy Path:**
1. WHEN brands are requested, THE Catalog_System SHALL retrieve all records from CatalogBrand table via GET /api/catalog/brands
2. WHEN brands are retrieved, THE Catalog_System SHALL order results by Brand name in ascending order
3. WHEN brands are retrieved, THE Catalog_System SHALL return JSON array with Id and Brand fields for each record
4. WHEN types are requested, THE Catalog_System SHALL retrieve all records from CatalogType table via GET /api/catalog/types
5. WHEN types are retrieved, THE Catalog_System SHALL order results by Type name in ascending order
6. WHEN types are retrieved, THE Catalog_System SHALL return JSON array with Id and Type fields for each record
7. WHEN create/edit page loads, THE Catalog_UI SHALL populate Brand dropdown with brand names and IDs
8. WHEN create/edit page loads, THE Catalog_UI SHALL populate Type dropdown with type names and IDs

**Validation & Edge Cases:**
9. WHEN no brands exist in database, THE Catalog_System SHALL return empty array
10. WHEN no types exist in database, THE Catalog_System SHALL return empty array
11. WHEN no brands exist, THE Catalog_UI SHALL display message "No brands available" in dropdown
12. WHEN no types exist, THE Catalog_UI SHALL display message "No types available" in dropdown

**Error Handling:**
13. IF database query fails, THEN THE Catalog_System SHALL return 500 error with message "Database operation failed" and log error with correlation ID
14. IF lookups fail to load, THEN THE Catalog_UI SHALL display error message "Failed to load brands/types. Please refresh the page."

**Assumptions & Notes:**
- Brand and Type tables are small (< 100 records each)
- No pagination needed for lookup lists
- Brand and Type data is seeded via CSV files during database initialization
- FK constraints prevent invalid Brand/Type IDs from being saved

---

## Summary

This requirements document defines six core requirements for the catalog management seam, covering:
1. List catalog items with pagination (browse)
2. Create catalog item (add new product)
3. Edit catalog item (update existing product)
4. Delete catalog item with confirmation (remove product)
5. View catalog item details (read-only inspection)
6. Brand and Type lookups (categorization dropdowns)

All requirements include comprehensive acceptance criteria covering happy path, validation, business rules, error handling, and edge cases using EARS patterns. The requirements preserve exact legacy functionality while specifying the modern Python FastAPI + React implementation.
