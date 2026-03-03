# Golden Baseline Capture Plan: catalog-crud

**Date**: 2026-03-02
**Application Type**: Web Application
**Framework**: ASP.NET WebForms 4.7.2
**Application URL**: http://localhost:50586/

---

## Application Detection

**Source**: `docs/context-fabric/project-facts.json`
- Framework: ASP.NET WebForms
- .NET Version: 4.7.2
- Type: Web application (e-commerce catalog CRUD)

**Capture Approach**: Browser automation (Playwright/Selenium)

---

## Workflows to Capture (from spec.md)

### Workflow 1: Create New Product
**Entry point**: Default.aspx → Create New button → /Catalog/Create
**Steps**:
1. Navigate to Create page
2. View empty form with default values
3. Click Brand dropdown → capture options
4. Click Type dropdown → capture options
5. Submit empty form → capture validation errors
6. Fill valid data → submit → verify redirect

**Screenshots needed**:
- `catalog-crud_create_01_empty_form.png`
- `catalog-crud_create_02_brand_dropdown.png`
- `catalog-crud_create_03_type_dropdown.png`
- `catalog-crud_create_04_validation_errors.png`
- `catalog-crud_create_05_filled_form.png`

### Workflow 2: Edit Existing Product
**Entry point**: Default.aspx → Edit link → /Catalog/Edit/1
**Steps**:
1. Navigate to Edit page for product ID 1
2. View pre-filled form with product data
3. View product image on left side
4. Attempt to edit picture filename (read-only)
5. Change name and price
6. Submit → verify redirect

**Screenshots needed**:
- `catalog-crud_edit_01_full_page.png`
- `catalog-crud_edit_02_prefilled_form.png`
- `catalog-crud_edit_03_readonly_picture.png`
- `catalog-crud_edit_04_modified_fields.png`

### Workflow 3: View Product Details
**Entry point**: Default.aspx → Details link → /Catalog/Details/1
**Steps**:
1. Navigate to Details page for product ID 1
2. View read-only product information
3. View product image
4. Click Edit button
5. Click Back to List button

**Screenshots needed**:
- `catalog-crud_details_01_full_page.png`
- `catalog-crud_details_02_readonly_fields.png`

### Workflow 4: Delete Product
**Entry point**: Default.aspx → Delete link → /Catalog/Delete/1
**Steps**:
1. Navigate to Delete page for product ID 1
2. View confirmation message
3. View product details
4. Click Delete button
5. Verify redirect to catalog list
6. Verify product removed from list

**Screenshots needed**:
- `catalog-crud_delete_01_confirmation.png`
- `catalog-crud_delete_02_product_details.png`
- `catalog-crud_delete_03_after_delete.png`

---

## Data Exports

### Brands Dropdown Data
**File**: `exports/brands.json`
**Content**: All brands from database (for dropdown population)

### Types Dropdown Data
**File**: `exports/types.json`
**Content**: All types from database (for dropdown population)

### Single Product Data
**File**: `exports/product_1.json`
**Content**: Complete data for product ID 1 (for Edit/Details/Delete)

### Validation Errors
**File**: `exports/validation_errors.json`
**Content**: All validation error messages captured from form submission

---

## Database Snapshots

### Before Create
**File**: `db-snapshots/before_create.json`
**Tables**: CatalogItems (count: 12)

### After Create
**File**: `db-snapshots/after_create.json`
**Tables**: CatalogItems (count: 13, new product added)
**Diff**: `db-snapshots/diff_create.json`

### Before Edit
**File**: `db-snapshots/before_edit.json`
**Tables**: CatalogItems where Id = 1

### After Edit
**File**: `db-snapshots/after_edit.json`
**Tables**: CatalogItems where Id = 1 (Name and Price changed)
**Diff**: `db-snapshots/diff_edit.json`

### Before Delete
**File**: `db-snapshots/before_delete.json`
**Tables**: CatalogItems where Id = 13 (the created product)

### After Delete
**File**: `db-snapshots/after_delete.json`
**Tables**: CatalogItems (count: 12, product removed)
**Diff**: `db-snapshots/diff_delete.json`

---

## HTTP Captures

### GET /Catalog/Create
**File**: `exports/http_get_create.har`
**Expected**: HTML form with empty fields

### POST /Catalog/Create (empty form)
**File**: `exports/http_post_create_invalid.har`
**Expected**: Validation errors

### POST /Catalog/Create (valid data)
**File**: `exports/http_post_create_valid.har`
**Expected**: 302 Redirect to /

### GET /Catalog/Edit/1
**File**: `exports/http_get_edit.har`
**Expected**: HTML form with pre-filled data

### POST /Catalog/Edit/1 (valid data)
**File**: `exports/http_post_edit.har`
**Expected**: 302 Redirect to /

### GET /Catalog/Details/1
**File**: `exports/http_get_details.har`
**Expected**: HTML with read-only product data

### GET /Catalog/Delete/1
**File**: `exports/http_get_delete.har`
**Expected**: HTML with confirmation message

### POST /Catalog/Delete/1
**File**: `exports/http_post_delete.har`
**Expected**: 302 Redirect to /

---

## Coverage

**Spec workflows**: 4 (Create, Edit, Details, Delete)
**Edge cases**:
- Empty form submission (validation)
- Invalid price (validation)
- Invalid stock values (validation)
- Read-only picture filename on Edit
- Product not found (404)

---

## Capture Method

**Tool**: Playwright (Node.js or Python)
**Browser**: Chromium
**Viewport**: 1920x1080 (desktop)
**Wait Strategy**: Wait for network idle after navigation

---

## Blockers

See: `docs/BASELINE_BLOCKERS.md` - same blockers as catalog-list (browser automation not available)
