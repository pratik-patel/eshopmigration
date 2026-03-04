# User Journey: catalog-management

**Application Type:** web
**Capture Method:** browser automation (Playwright)
**Base URL:** http://localhost:50586/
**Captured:** 2026-03-03T21:20:00Z

---

## Journey 1: Browse Product Catalog

**User Goal:** View available products in the catalog

**Steps:**
1. Navigate to home page: `/` (Default.aspx)
   - Screenshot: `01_product_list.png`
   - Page displays grid/list of products (10 items per page)
   - Pagination controls show "Showing 10 of 12 products - Page 1 - 2"

2. View product details (click on product link)
   - Navigate to: `/Catalog/Details/{id}` (example: id=1)
   - Screenshot: `03_product_details.png`
   - Page displays read-only product information
   - Shows product image, name, description, price, brand, type, stock levels

**Test Scenarios:**
| Scenario | Input | Expected Output | Screenshot |
|----------|-------|-----------------|------------|
| View first page of catalog | Navigate to / | Shows 10 products, page 1 of 2 | 01_product_list.png |
| Click Next pagination | Click "Next" link | Shows products 11-12, page 2 of 2 | (not captured) |
| View product details | Click product link (id=1) | Shows detailed product view | 03_product_details.png |

**Data Access:**
- **Reads:** CatalogItem, CatalogBrand, CatalogType
- **Writes:** None

---

## Journey 2: Create New Product

**User Goal:** Add a new product to the catalog

**Steps:**
1. Navigate to create page: `/Catalog/Create`
   - Screenshot: `02_create_product.png`
   - Empty form with 9+ fields

2. Fill out form fields:
   - Name (text, required)
   - Description (textarea, optional)
   - Price (number, required)
   - Brand (dropdown, required) - populated from CatalogBrand table
   - Type (dropdown, required) - populated from CatalogType table
   - Product Image (file upload, optional)
   - Available Stock (number, required)
   - Restock Threshold (number, required)
   - Max Stock Threshold (number, required)

3. Submit form
   - Data saved to CatalogItem table
   - Image uploaded to Pics/ directory (if provided)
   - Redirect to product list or details page

**Test Scenarios:**
| Scenario | Input | Expected Output | Screenshot |
|----------|-------|-----------------|------------|
| Load create form | Navigate to /Catalog/Create | Empty form with dropdowns populated | 02_create_product.png |
| Submit with all fields | Fill all fields, submit | Product created, redirect | (interactive test) |
| Submit with only required | Fill required fields only | Product created | (interactive test) |
| Submit with validation errors | Leave required fields empty | Error messages shown | (interactive test) |

**Data Access:**
- **Reads:** CatalogBrand (for dropdown), CatalogType (for dropdown)
- **Writes:** CatalogItem, File System (Pics/)

**Form Structure:** See `data-snapshots/create_product_form_structure.json` (14 fields)

---

## Journey 3: Edit Existing Product

**User Goal:** Modify an existing product's details

**Steps:**
1. Navigate from product list or details to edit page: `/Catalog/Edit/{id}` (example: id=1)
   - Screenshot: `04_edit_product.png`
   - Form pre-populated with existing product data

2. Modify any field (same fields as Create)

3. Submit form
   - Data updated in CatalogItem table
   - Image replaced in Pics/ directory (if new image uploaded)
   - Redirect to product list or details page

**Test Scenarios:**
| Scenario | Input | Expected Output | Screenshot |
|----------|-------|-----------------|------------|
| Load edit form | Navigate to /Catalog/Edit/1 | Form pre-filled with product 1 data | 04_edit_product.png |
| Update name and price | Change name, change price, submit | Product updated | (interactive test) |
| Change product image | Upload new image, submit | Image replaced | (interactive test) |

**Data Access:**
- **Reads:** CatalogItem (to pre-populate), CatalogBrand, CatalogType
- **Writes:** CatalogItem, File System (Pics/)

---

## Journey 4: Delete Product

**User Goal:** Remove a product from the catalog

**Steps:**
1. Navigate from product list or details to delete page: `/Catalog/Delete/{id}` (example: id=1)
   - Screenshot: `05_delete_confirmation.png`
   - Page shows product details with confirmation warning

2. Confirm deletion
   - Click "Confirm Delete" button
   - Product removed from CatalogItem table
   - Image file may remain in Pics/ directory (legacy behavior to verify)
   - Redirect to product list

3. Cancel deletion
   - Click "Cancel" or "Back" link
   - No changes made
   - Return to product list or details

**Test Scenarios:**
| Scenario | Input | Expected Output | Screenshot |
|----------|-------|-----------------|------------|
| Load delete confirmation | Navigate to /Catalog/Delete/1 | Shows product 1 with warning | 05_delete_confirmation.png |
| Confirm deletion | Click confirm button | Product deleted, redirect | (interactive test) |
| Cancel deletion | Click cancel link | No changes, redirect | (interactive test) |

**Data Access:**
- **Reads:** CatalogItem (to show details)
- **Writes:** CatalogItem (DELETE)

---

## Edge Cases Captured

None captured (would require interactive testing):
- Validation errors (empty required fields)
- Database constraint violations (FK references)
- File upload errors (invalid file type, size limit)
- Concurrent edit conflicts

---

## Edge Cases NOT Captured (Require Interactive Testing)

1. **Pagination edge cases:**
   - Navigate to last page (page 2)
   - Navigate beyond last page (page 3+) - should show error or empty
   - Navigate to negative page numbers

2. **Validation errors:**
   - Submit create/edit form with empty required fields
   - Submit invalid price (negative, non-numeric)
   - Submit invalid stock values (negative)

3. **Image upload errors:**
   - Upload file too large
   - Upload invalid file type (non-image)
   - Upload image with special characters in filename

4. **Foreign key constraints:**
   - Delete product referenced by other tables (if any)
   - Create product with invalid brand/type ID

5. **Concurrent operations:**
   - Edit product while another user is editing
   - Delete product that was already deleted

---

## Technical Notes

**URL Patterns:**
- List: `/` (Default.aspx with pagination: `/Default/index/{page}/size/{pageSize}`)
- Create: `/Catalog/Create`
- Details: `/Catalog/Details/{id}` (route parameter, not query string)
- Edit: `/Catalog/Edit/{id}` (route parameter)
- Delete: `/Catalog/Delete/{id}` (route parameter)

**Pagination Logic:**
- Default page size: 10
- Default page index: 0
- URL format: `/Default/index/{pageIndex}/size/{pageSize}`
- Example: `/Default/index/1/size/10` = page 2, 10 items per page

**Form Submission:**
- Method: POST
- CSRF protection: ASP.NET ViewState + EventValidation tokens
- File upload: Multipart form data

**Image Handling:**
- Upload directory: `Pics/` (relative to web root)
- File naming convention: (to be verified from code)
- Max file size: (to be verified from web.config)
- Allowed file types: (to be verified from validation code)

---

## Data Snapshots

**Product List Data:** `data-snapshots/product_list_snapshot.json`
- Total products: 12
- Products on page 1: 10
- Pagination: Page 1 of 2

**Create Form Structure:** `data-snapshots/create_product_form_structure.json`
- Total fields: 14
- Required fields: Name, Price, Brand, Type, Stock fields
- Optional fields: Description, Image

**Product Details:** `data-snapshots/product_1_details.json`
- Product ID: 1
- Fields: Name, Price, Description, Brand (FK), Type (FK), Image, Stock levels

---

## Parity Testing Recommendations

**Visual Parity:**
- Compare layout structure (header, main content, footer)
- Compare form field positions and labels
- Compare button placement and styling
- Compare grid/table layout for product list
- Compare pagination controls

**Functional Parity:**
- Test pagination logic (page calculations, item counts)
- Test form validation (required fields, data types)
- Test CRUD operations (Create, Read, Update, Delete)
- Test FK relationships (brand/type dropdowns populated correctly)
- Test image upload (file handling, storage location)

**Data Parity:**
- Verify product list returns correct data structure
- Verify form fields match database schema
- Verify details view includes all required fields
- Verify edit form pre-populates correctly
- Verify delete operation removes record

**API Contract:**
- GET /api/products?page={page}&size={size} → Product list
- GET /api/products/{id} → Product details
- POST /api/products → Create product
- PUT /api/products/{id} → Update product
- DELETE /api/products/{id} → Delete product
- POST /api/products/{id}/image → Upload product image (replaces ASMX)
