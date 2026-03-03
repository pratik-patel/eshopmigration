# User Journeys: catalog-management

**Application Type:** Web Application (ASP.NET WebForms)
**Capture Method:** Browser automation (Playwright, Chromium headless)
**Captured:** 2026-03-03T19:04:39Z

---

## Journey 1: Browse Product Catalog (Anonymous User)

**User Goal:** View available products without signing in

### Steps

1. **Navigate to home page**
   - URL: http://localhost:50586/
   - Screen: `screenshots/01_default_desktop.png`
   - State: Product list loaded with 10 items
   - Data visible:
     - Product images (thumbnails)
     - Product names (e.g., ".NET Bot Black Hoodie")
     - Descriptions, brands, types
     - Prices (formatted as currency with `.esh-price` style)
     - Stock levels (Available, Restock threshold, Max stock)
     - Action links (Edit | Details | Delete)
   - Pagination: "Showing 10 of {total} products - Page 1 - {total_pages}"
   - Navigation: "Previous" link hidden (on page 1), "Next" link visible

2. **View pagination controls**
   - Location: Bottom of product list
   - Controls visible:
     - "Previous" link (hidden with `.esh-pager-item--hidden`)
     - Page info text
     - "Next" link (visible, navigable)

3. **Navigate to page 2**
   - Action: Click "Next" link
   - URL: http://localhost:50586/products/1/10 (page index 1, size 10)
   - Screen: `screenshots/02_paginated_desktop.png`
   - State: Different set of products loaded
   - Pagination: Both "Previous" and "Next" links visible

4. **View product details**
   - Action: Click "Details" link for product ID 1
   - URL: http://localhost:50586/Catalog/Details/1
   - Screen: `screenshots/03_details_desktop.png`
   - State: Product details page displayed
   - Layout:
     - Left column: Product image (large, `/Pics/1.png`)
     - Middle column: Name, Description, Brand, Type, Price
     - Right column: Picture filename, Stock, Restock, Max stock, Action buttons
   - Actions available:
     - "[ Back to list ]" - Returns to home page
     - "[ Edit ]" - Navigate to edit page (requires authentication)

### Expected Behavior

- Anonymous users can browse catalog without signing in
- Pagination works correctly (10 items per page)
- Product images load from `/Pics/{filename}`
- Details page shows full product information
- Edit button visible but may require authentication
- No authentication challenge for read-only operations

### Data Snapshot

**Products visible on page 1 (from `data/product_list_data.json`):**

| ID | Name | Brand | Type | Price | Stock |
|----|------|-------|------|-------|-------|
| 1 | .NET Bot Black Hoodie | .NET | T-Shirt | $19.50 | 100 |
| 2 | .NET Black & White Mug | .NET | Mug | $8.50 | 100 |
| 3 | Prism White T-Shirt | Other | T-Shirt | $12.00 | 100 |
| 4 | .NET Foundation T-shirt | .NET | T-Shirt | $12.00 | 100 |
| 5 | Roslyn Red Sheet | Other | Sheet | $8.50 | 100 |
| 6 | .NET Blue Hoodie | .NET | T-Shirt | $12.00 | 100 |
| 7 | Roslyn Red T-Shirt | Other | T-Shirt | $12.00 | 100 |
| 8 | Kudu Purple Hoodie | Other | T-Shirt | $8.50 | 100 |
| 9 | Cup&lt;T&gt; White Mug | Other | Mug | $12.00 | 100 |
| 10 | .NET Foundation Sheet | .NET | Sheet | $12.00 | 100 |

---

## Journey 2: Create New Product (Authenticated User)

**User Goal:** Add a new product to the catalog

### Prerequisites

- User must be authenticated (Azure AD sign-in)
- OR `UseAzureActiveDirectory=false` in configuration

### Steps

1. **Navigate to home page**
   - URL: http://localhost:50586/
   - State: Authenticated user sees "Hello, {username}!" in header

2. **Initiate product creation**
   - Action: Click "Create New" button (top of product list)
   - URL: http://localhost:50586/Catalog/Create
   - Screen: `screenshots/04_create_desktop.png`
   - State: Empty form displayed
   - Authentication check: If not authenticated, redirect to sign-in page

3. **Review form fields**
   - Layout: Two-column (image preview left, form fields right)
   - Image preview: Default image from `ImageService.UrlDefaultImage()`
   - Form fields visible:
     - Name (TextBox, Required)
     - Description (TextBox)
     - Brand (DropDownList, populated from `GetBrands()`)
     - Type (DropDownList, populated from `GetTypes()`)
     - Price (TextBox, default "0.00", RangeValidator 0-1,000,000)
     - Stock (TextBox, default "0", RangeValidator 0-10,000,000)
     - Restock (TextBox, default "0", RangeValidator 0-10,000,000)
     - Maxstock (TextBox, default "0", RangeValidator 0-10,000,000)
   - Hidden field: TempImageName (empty string)
   - Buttons:
     - "[ Cancel ]" - Hyperlink to home page
     - "[ Create ]" - Submit button (triggers server postback)

4. **Fill in product details**
   - Action: User enters values in form fields
   - Example data:
     - Name: "Test Product"
     - Description: "Test Description"
     - Brand: Select from dropdown (e.g., ".NET")
     - Type: Select from dropdown (e.g., "T-Shirt")
     - Price: "25.00"
     - Stock: "50"
     - Restock: "10"
     - Maxstock: "100"
   - Screen: `screenshots/04_create_desktop_filled.png` (simulated state)
   - Validation: Client-side validators active (RequiredFieldValidator, RangeValidator)

5. **Upload product image (optional)**
   - Action: Click "Upload image" file input
   - File dialog: User selects image file (JPEG, PNG, or GIF)
   - Client-side:
     - JavaScript captures file input change event
     - AJAX POST to `/Catalog/PicUploader.asmx`
     - Request includes: file data, itemId (context)
   - Server-side:
     - Validates image format (JPEG, PNG, GIF)
     - Calls `ImageService.UploadTempImage(image, catalogItemId)`
     - Returns JSON: `{ "name": "/temp/{filename}", "url": "{storage_url}" }`
   - Client-side:
     - Updates image preview (src = returned URL)
     - Sets TempImageName hidden field value
   - Note: Upload button hidden if `UseAzureStorage=false`

6. **Submit form**
   - Action: Click "[ Create ]" button
   - Client-side validation:
     - Name field not empty
     - Price between 0 and 1,000,000 (2 decimal places max)
     - Stock between 0 and 10,000,000
     - Restock between 0 and 10,000,000
     - Maxstock between 0 and 10,000,000
   - Server-side processing (Create_Click event):
     - Validate `ModelState.IsValid`
     - Construct `CatalogItem` from form fields
     - If TempImageName has value:
       - Extract filename
       - Set `PictureFileName`
     - Call `CatalogService.CreateCatalogItem(catalogItem)`
     - If temp image exists:
       - Call `ImageService.UpdateImage(catalogItem)` (move temp to permanent)
     - Redirect to home page (`~/`)

7. **Verify creation**
   - URL: http://localhost:50586/
   - State: Product list reloaded, new product visible in list
   - Expected: New product appears with correct data and image

### Validation Rules

| Field | Rule | Error Message |
|-------|------|---------------|
| Name | Required | "The Name field is required." |
| Price | Range 0-1,000,000 (Currency, 2 decimals) | "The Price must be a positive number with maximum two decimals between 0 and 1 million." |
| Stock | Range 0-10,000,000 (Integer) | "The field Stock must be between 0 and 10 million." |
| Restock | Range 0-10,000,000 (Integer) | "The field Restock must be between 0 and 10 million." |
| Maxstock | Range 0-10,000,000 (Integer) | "The field Max stock must be between 0 and 10 million." |

### Edge Cases

- **Empty Name:** Client-side RequiredFieldValidator prevents submission
- **Invalid Price:** Client-side RangeValidator shows error message
- **No Image:** Default image (dummy.png) used, no error
- **Invalid Image Format:** Server returns 400 error "image is not valid"
- **Server Validation Failure:** ModelState errors displayed, form not submitted
- **Cancel Button:** Returns to home page without creating product

---

## Journey 3: Edit Existing Product (Authenticated User)

**User Goal:** Modify an existing product's details

### Prerequisites

- User must be authenticated (Azure AD sign-in)
- Product must exist in catalog (e.g., product ID 1)

### Steps

1. **Navigate to product list**
   - URL: http://localhost:50586/
   - State: Product list displayed

2. **Select product to edit**
   - Action: Click "Edit" link for product ID 1 (.NET Bot Black Hoodie)
   - URL: http://localhost:50586/Catalog/Edit/1
   - Screen: `screenshots/05_edit_desktop.png`
   - State: Form pre-filled with existing product data
   - Authentication check: If not authenticated, redirect to sign-in page

3. **Review pre-filled form**
   - Layout: Two-column (image preview left, form fields right)
   - Image preview: Current product image (`/Pics/1.png`)
   - Form fields pre-populated:
     - Name: ".NET Bot Black Hoodie"
     - Description: ".NET Bot Black Hoodie"
     - Brand: ".NET" (dropdown selected)
     - Type: "T-Shirt" (dropdown selected)
     - Price: "19.5"
     - PictureFileName: "1.png" (READ-ONLY, tooltip "Not allowed for edition")
     - Stock: "100"
     - Restock: "0"
     - Maxstock: "0"
   - Hidden field: TempImageName (empty string)
   - Buttons:
     - "[ Cancel ]" - Hyperlink to home page
     - "[ Save ]" - Submit button (triggers server postback)

4. **Modify product details**
   - Action: User changes values in editable fields
   - Example modifications:
     - Price: Change from "19.5" to "24.99"
     - Stock: Change from "100" to "75"
     - Restock: Change from "0" to "20"
   - Note: Cannot edit PictureFileName directly (read-only)
   - Validation: Same client-side validators as create form

5. **Upload new product image (optional)**
   - Action: Click "Upload image" file input
   - Process: Same as create form (AJAX upload to PicUploader.asmx)
   - Effect: Image preview updates, TempImageName hidden field set
   - Note: New image will replace existing image on save

6. **Submit changes**
   - Action: Click "[ Save ]" button
   - Client-side validation: Same as create form
   - Server-side processing (Save_Click event):
     - Validate `ModelState.IsValid`
     - Construct `CatalogItem` from form fields (including product ID from route)
     - If TempImageName has value:
       - Call `ImageService.UpdateImage(catalogItem)` (move temp to permanent)
       - Extract filename, set `PictureFileName`
     - Call `CatalogService.UpdateCatalogItem(catalogItem)`
     - Redirect to home page (`~/`)

7. **Verify update**
   - URL: http://localhost:50586/
   - State: Product list reloaded, modified product visible with updated data
   - Expected: Price and stock values changed, new image displayed (if uploaded)

### Key Differences from Create Form

- Form is pre-populated with existing product data
- PictureFileName field is read-only (cannot edit directly)
- Brand/Type dropdowns have pre-selected values
- Product ID is included in form submission (from route)
- UpdateCatalogItem called instead of CreateCatalogItem

### Edge Cases

- **No Changes Made:** Save succeeds, no data changed
- **Image Upload Only:** Only image changes, other fields unchanged
- **Cancel Button:** Returns to home page without saving changes
- **Validation Errors:** Same as create form

---

## Journey 4: Delete Product (Authenticated User)

**User Goal:** Remove a product from the catalog

### Prerequisites

- User must be authenticated (Azure AD sign-in)
- Product must exist in catalog (e.g., product ID 1)

### Steps

1. **Navigate to product list**
   - URL: http://localhost:50586/
   - State: Product list displayed

2. **Select product to delete**
   - Action: Click "Delete" link for product ID 1 (.NET Bot Black Hoodie)
   - URL: http://localhost:50586/Catalog/Delete/1
   - Screen: `screenshots/06_delete_desktop.png`
   - State: Confirmation page displayed
   - Authentication check: If not authenticated, redirect to sign-in page

3. **Review confirmation page**
   - Message: "Are you sure you want to delete this?"
   - Layout: Three-column (same as details page)
     - Left column: Product image
     - Middle column: Name, Description, Brand, Type, Price
     - Right column: Picture filename, Stock, Restock, Max stock, Action buttons
   - All product details visible (read-only)
   - Buttons:
     - "[ Cancel ]" - Hyperlink to home page
     - "[ Delete ]" - Submit button (triggers server postback)

4. **Confirm deletion**
   - Action: Click "[ Delete ]" button
   - Server-side processing (Delete_Click event):
     - Call `CatalogService.RemoveCatalogItem(productToDelete)`
     - Redirect to home page (`~/`)
   - No additional validation or confirmation dialog

5. **Verify deletion**
   - URL: http://localhost:50586/
   - State: Product list reloaded, deleted product no longer visible
   - Expected: Product ID 1 removed from catalog

### Safety Features

- Confirmation page shows full product details before deletion
- No accidental deletion (requires explicit button click)
- Cancel button available to abort operation
- No cascading deletes or side effects documented

### Edge Cases

- **Cancel Button:** Returns to home page without deleting product
- **Product Not Found:** Server error (not handled gracefully in legacy)
- **Image Cleanup:** Legacy does not delete image file from storage (should add in modern version)

---

## Journey 5: Responsive Layout Test (Anonymous User)

**User Goal:** Verify application works on different devices

### Steps

1. **Test desktop layout (1920x1080)**
   - URL: http://localhost:50586/
   - Screen: `screenshots/01_default_desktop.png`
   - State: Full layout with all columns visible
   - Grid: All 10 columns displayed (image, name, description, brand, type, price, picture name, stock, restock, max stock, actions)
   - Navigation: Desktop navigation bar with brand logo and auth UI
   - Footer: All footer elements visible

2. **Test tablet layout (768x1024)**
   - URL: http://localhost:50586/
   - Screen: `screenshots/01_default_tablet.png`
   - State: Bootstrap responsive grid adapts
   - Grid: Columns wrap to fit tablet viewport
   - Navigation: Responsive navbar (may collapse)
   - Footer: Footer text image still visible

3. **Test mobile layout (375x667)**
   - URL: http://localhost:50586/
   - Screen: `screenshots/01_default_mobile.png`
   - State: Single-column layout
   - Grid: Columns stack vertically
   - Navigation: Mobile-friendly navigation
   - Footer: Footer text image hidden (`.hidden-xs`)
   - Buttons: Touch-friendly sizes

### Responsive Breakpoints

- **Desktop:** ≥1200px - Full layout
- **Tablet:** 768px-1199px - Collapsed grid
- **Mobile:** <768px - Stacked columns, hidden elements

### Bootstrap Classes Used

- `.container` - Responsive fixed-width container
- `.row` - Grid row
- `.col-md-*` - Medium device columns
- `.hidden-xs` - Hide on extra-small screens
- `.visible-xs` - Show only on extra-small screens

---

## Journey 6: Authentication Flow (Authenticated User)

**User Goal:** Sign in to access administrative features

### Steps (Not Fully Captured)

1. **Attempt to access protected page**
   - URL: http://localhost:50586/Catalog/Create
   - State: User not authenticated
   - Expected: Redirect to Azure AD sign-in page (not captured)

2. **Sign in via Azure AD**
   - Action: Enter Azure AD credentials
   - Authentication: OpenID Connect via OWIN middleware
   - Expected: Redirect back to requested page after successful sign-in

3. **Access protected page**
   - URL: http://localhost:50586/Catalog/Create
   - State: User authenticated, create form displayed
   - Header: Shows "Hello, {username}!" and "Sign out" link

4. **Sign out**
   - Action: Click "Sign out" link
   - Expected: User logged out, redirect to home page
   - Header: Shows "Sign in" link

### Authentication Notes

- **Baseline capture limitation:** Authentication was disabled (`UseAzureActiveDirectory=false`) during capture
- **Modern API equivalent:** Replace with JWT bearer tokens
- **Security enhancement:** Add role-based access control (not in legacy)

---

## Test Scenarios Summary

| Scenario | Input | Expected Output | Screenshot |
|----------|-------|----------------|------------|
| View product list | Navigate to `/` | 10 products displayed with pagination | 01_default_desktop.png |
| Navigate to page 2 | Click "Next" | Page 2 products displayed | 02_paginated_desktop.png |
| View product details | Click "Details" for ID 1 | Product details displayed | 03_details_desktop.png |
| Create product form | Click "Create New" | Empty form with validation | 04_create_desktop.png |
| Edit product form | Click "Edit" for ID 1 | Pre-filled form with product data | 05_edit_desktop.png |
| Delete confirmation | Click "Delete" for ID 1 | Confirmation page with product details | 06_delete_desktop.png |
| Responsive tablet | Resize to 768x1024 | Layout adapts to tablet viewport | 01_default_tablet.png, 03_details_tablet.png |
| Responsive mobile | Resize to 375x667 | Layout adapts to mobile viewport | 01_default_mobile.png |

---

## Data Validation

### Product List Data (captured from running application)

**Source:** `data/product_list_data.json`
**Row count:** 10 products
**Fields validated:**
- name (string, not empty)
- description (string, not empty)
- brand (string, matches CatalogBrand.Brand)
- type (string, matches CatalogType.Type)
- price (decimal, formatted as currency)
- picture (string, filename)
- stock (integer, >= 0)
- restock (integer, >= 0)
- maxStock (integer, >= 0)

**Sample validation:**
- Product 1: Name = ".NET Bot Black Hoodie", Price = "$19.5", Stock = "100"
- Product 2: Name = ".NET Black & White Mug", Price = "$8.50", Stock = "100"

---

## Parity Test Requirements

### Functional Parity

1. **List products with pagination**
   - API: GET /api/catalog?page=0&size=10
   - Expected: 10 products matching product_list_data.json
   - Validation: Compare JSON response to captured data

2. **View product details**
   - API: GET /api/catalog/1
   - Expected: Product details for ".NET Bot Black Hoodie"
   - Validation: Match fields from screenshot 03_details_desktop.png

3. **Create product**
   - API: POST /api/catalog
   - Input: Test product data (name, description, brand, type, price, stock)
   - Expected: Product created, appears in list
   - Validation: Verify in GET /api/catalog response

4. **Edit product**
   - API: PUT /api/catalog/1
   - Input: Modified product data (e.g., price change)
   - Expected: Product updated with new data
   - Validation: Verify in GET /api/catalog/1 response

5. **Delete product**
   - API: DELETE /api/catalog/1
   - Expected: Product removed from catalog
   - Validation: 404 on GET /api/catalog/1

6. **Upload image**
   - API: POST /api/catalog/images
   - Input: Image file (JPEG, PNG, or GIF)
   - Expected: Image uploaded, URL returned
   - Validation: Image accessible at returned URL

### Non-Functional Parity

1. **Response times**
   - List operations: < 500ms
   - Detail view: < 300ms
   - Create/update: < 1000ms

2. **Image upload**
   - Max file size: 5 MB
   - Supported formats: JPEG, PNG, GIF
   - Validation: Reject invalid formats

3. **Pagination**
   - Page size: 10 items (configurable)
   - Max items: Support up to 10,000 products

---

**Captured By:** golden-baseline-capture agent (103)
**Date:** 2026-03-03T19:04:39Z
**Status:** COMPLETE
