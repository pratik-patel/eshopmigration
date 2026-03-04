# Baseline Index: catalog-management
Captured: 2026-03-03T21:20:00Z
Application Type: web
Framework: ASP.NET WebForms (.NET Framework 4.7.2)
Capture Tools: Playwright (Python, Chromium)
Environment: Windows Server 2022, Chromium headless, 1920x1080 viewport
Base URL: http://localhost:50586/

## Screenshots
| File | Step | URL | Notes |
|------|------|-----|-------|
| screenshots/01_product_list.png | Product List | / (Default.aspx) | Home page with paginated product catalog (10 items per page) |
| screenshots/02_create_product.png | Create Product | /Catalog/Create | Create new product form with fields for name, description, price, brand, type, image |
| screenshots/03_product_details.png | Product Details | /Catalog/Details/1 | Read-only product detail view (product ID 1) |
| screenshots/04_edit_product.png | Edit Product | /Catalog/Edit/1 | Edit existing product form (product ID 1) |
| screenshots/05_delete_confirmation.png | Delete Confirmation | /Catalog/Delete/1 | Delete confirmation page (product ID 1) |

## Data Snapshots
| File | Description | Row Count |
|------|-------------|-----------|
| data-snapshots/product_list_snapshot.json | Product list page structure | 12 products total |
| data-snapshots/create_product_form_structure.json | Create form field inventory | 14 fields |
| data-snapshots/product_1_details.json | Product ID 1 details data | 1 record |

## Workflows Captured

### 1. Browse Catalog (Default.aspx)
**Navigation**: Direct URL: /
**Actions**:
- View paginated product list (default: page 0, size 10)
- Pagination controls (Previous/Next)
- Shows "Showing 10 of 12 products - Page 1 - 2"

**Screenshot**: `01_product_list.png`
**Data Snapshot**: `product_list_snapshot.json`

### 2. Create Product (Catalog/Create.aspx)
**Navigation**: Direct URL: /Catalog/Create
**Actions**:
- Fill out product creation form
- Select brand from dropdown (CatalogBrand)
- Select type from dropdown (CatalogType)
- Upload product image (optional)
- Submit form

**Form Fields** (from `create_product_form_structure.json`):
- Name (text input, required)
- Description (textarea, optional)
- Price (number input, required)
- CatalogBrandId (dropdown, required)
- CatalogTypeId (dropdown, required)
- PictureFileName (file upload, optional)
- AvailableStock (number input, required)
- RestockThreshold (number input, required)
- MaxStockThreshold (number input, required)

**Screenshot**: `02_create_product.png`
**Data Snapshot**: `create_product_form_structure.json`

### 3. View Product Details (Catalog/Details/{id})
**Navigation**: Direct URL: /Catalog/Details/1
**Actions**:
- View read-only product information
- See product image
- See brand and type names (FK relationships)

**Screenshot**: `03_product_details.png`
**Data Snapshot**: `product_1_details.json`

### 4. Edit Product (Catalog/Edit/{id})
**Navigation**: Direct URL: /Catalog/Edit/1
**Actions**:
- Pre-populated form with existing product data
- Modify any field
- Submit updated data

**Screenshot**: `04_edit_product.png`

### 5. Delete Product (Catalog/Delete/{id})
**Navigation**: Direct URL: /Catalog/Delete/1
**Actions**:
- View product details to confirm deletion
- Confirm or cancel deletion

**Screenshot**: `05_delete_confirmation.png`

## Coverage
Spec workflows captured: 5/5
- [OK] Product List (Default.aspx)
- [OK] Create Product (Catalog/Create.aspx)
- [OK] Product Details (Catalog/Details.aspx)
- [OK] Edit Product (Catalog/Edit.aspx)
- [OK] Delete Product (Catalog/Delete.aspx)

**Not Captured**:
- Catalog/PicUploader.asmx (ASMX web service - requires interactive upload workflow, not a navigable page)

**Edge Cases Identified**:
- Empty product list (database has 12 products, so not applicable)
- Pagination edge cases (first page, last page)
- Validation errors (requires interactive form submission)

**Synthetic Baselines**: No (real screenshots from running application)

## Database State
**At capture time**:
- CatalogItem table: 12 products
- CatalogBrand table: Multiple brands (reference data)
- CatalogType table: Multiple types (reference data)
- Pagination: 10 items per page, 2 pages total

**Product ID used for captures**: 1 (first product in catalog)

## Technical Notes
- All pages captured at 1920x1080 resolution (full-page screenshots)
- Captured with Chromium (Playwright) in headless mode
- Network idle wait strategy (ensures all AJAX/images loaded)
- Page titles follow pattern: "{Action} - Catalog manager (Web Forms)"
- URL routing: ASP.NET WebForms with friendly URLs (no .aspx extension visible in some URLs)
- Image upload service (PicUploader.asmx) not captured - requires multi-step upload workflow
- No authentication required (public catalog application)

## Known Limitations
- Product extraction script did not correctly parse product list HTML (0 products extracted)
  - Fallback: Manual verification from screenshots shows 12 products present
  - Product IDs 1-10 visible on first page
- Form validation states not captured (would require interactive submission)
- Image upload workflow not captured (ASMX web service requires file upload interaction)

## Parity Testing Requirements
**Visual Comparison**:
- Layout structure (header, navigation, content area, footer)
- Grid/table structure for product list
- Form field layout and labels
- Button placement and styling
- Typography and spacing

**Functional Parity**:
- Pagination logic (page size 10, correct page calculations)
- Form validation (required fields, data types)
- CRUD operations preserve data integrity
- FK relationships maintained (CatalogBrand, CatalogType)

**Data Parity**:
- Product list returns correct data structure
- Form fields match database schema
- Details view shows all required fields
- Edit form pre-populates correctly

## Next Steps for Parity Harness
1. Extract expected data structures from snapshots
2. Define OpenAPI contract matching legacy behavior
3. Create visual regression tests using these screenshots as baselines
4. Implement API contract tests against captured data structures
5. Test pagination logic (page 0 size 10 = items 1-10)
6. Test FK relationships (brand/type dropdowns match reference tables)
