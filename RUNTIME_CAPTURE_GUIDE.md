# Runtime Evidence Capture Guide

**Legacy Application URL**: http://localhost:50586/

This guide helps capture runtime evidence from the running legacy eShop application for:
- Visual parity verification
- Golden baseline testing
- Contract validation
- UI behavior documentation

---

## 🎯 Capture Checklist

### Page 1: Catalog List (Home Page)
**URL**: http://localhost:50586/

**Screenshots to capture**:
- [ ] Full page view
- [ ] Product table with all columns visible
- [ ] Pagination controls
- [ ] Empty state (if possible - delete all products temporarily)

**Details to document**:
- [ ] Exact page title
- [ ] Table column headers (order and text)
- [ ] Number of products displayed per page
- [ ] Pagination text format (e.g., "Showing X of Y products - Page N - M")
- [ ] Button text: "Create New" exact text and styling
- [ ] Action link text: "Edit | Details | Delete" exact separators
- [ ] CSS classes on table, buttons, pagination
- [ ] Product image dimensions and styling
- [ ] Price formatting (currency symbol, decimal places)
- [ ] Font sizes, colors, spacing

**Data to export**:
- [ ] Take note of first 3 product names and prices
- [ ] Note brand and type for first product
- [ ] Screenshot of one product image

---

### Page 2: Create Product
**URL**: http://localhost:50586/Catalog/Create

**Screenshots to capture**:
- [ ] Full form view
- [ ] Empty form (initial state)
- [ ] Form with validation errors (submit empty form)
- [ ] Form with one field filled
- [ ] Dropdown lists (Brand and Type) expanded

**Details to document**:
- [ ] Exact page title
- [ ] Form field labels (exact text)
- [ ] Field order (top to bottom)
- [ ] Required field indicators (asterisks, etc.)
- [ ] Validation error messages:
  - Name required: "____"
  - Price invalid: "____"
  - Stock invalid: "____"
- [ ] Dropdown options:
  - Brands: [ ]
  - Types: [ ]
- [ ] Default values (Price: "0.00", Stock: "0")
- [ ] Button text: Cancel and Create exact text
- [ ] Field widths and layout
- [ ] Error message styling (color, position)
- [ ] Picture name field: exact informational message

**Test scenarios**:
1. Submit empty form → capture validation errors
2. Enter invalid price (e.g., "abc") → capture error
3. Enter price with 3 decimals (e.g., "12.999") → capture error
4. Enter stock > 10 million → capture error
5. Successfully create a product → note redirect behavior

---

### Page 3: Edit Product
**URL**: http://localhost:50586/Catalog/Edit/1

**Screenshots to capture**:
- [ ] Full page with product image on left
- [ ] Form pre-filled with product data
- [ ] Validation error when price changed to invalid value
- [ ] Dropdown showing current selection

**Details to document**:
- [ ] Product image position and size
- [ ] Form layout (2-column: image left, form right)
- [ ] Picture filename field: read-only styling
- [ ] Tooltip on picture filename field: "____"
- [ ] Pre-filled values for product ID 1
- [ ] Button text: Cancel and Save exact text
- [ ] Validation messages (same as Create or different?)

**Test scenarios**:
1. Change name and save → note success behavior
2. Change price to invalid → capture error
3. Click Cancel → note navigation

---

### Page 4: Details Product
**URL**: http://localhost:50586/Catalog/Details/1

**Screenshots to capture**:
- [ ] Full page view
- [ ] Product image
- [ ] All fields displayed in read-only format

**Details to document**:
- [ ] Page layout (same 2-column as Edit?)
- [ ] Field display format (labels and values)
- [ ] Button text: "Edit" and "Back to List" exact text
- [ ] Read-only styling differences from Edit page

---

### Page 5: Delete Product
**URL**: http://localhost:50586/Catalog/Delete/1

**Screenshots to capture**:
- [ ] Full page with confirmation message
- [ ] Product details displayed

**Details to document**:
- [ ] Exact confirmation message: "____"
- [ ] Button text: "Delete" and "Back to List" exact text
- [ ] Button styling (is Delete button red/warning style?)
- [ ] Product details displayed (same format as Details page?)

**Test scenarios**:
1. Click Delete → note navigation and product removal
2. Click Back to List → note navigation

---

### Page 6: About
**URL**: http://localhost:50586/About

**Screenshots to capture**:
- [ ] Full page view

**Details to document**:
- [ ] Exact page content (heading and paragraphs)

---

### Page 7: Contact
**URL**: http://localhost:50586/Contact

**Screenshots to capture**:
- [ ] Full page view

**Details to document**:
- [ ] Exact page content (address, phone, email)

---

## 📸 Screenshot Naming Convention

Save screenshots to: `docs/seams/{seam}/runtime/screenshots/`

```
catalog-list-01-full-page.png
catalog-list-02-empty-state.png
catalog-create-01-empty-form.png
catalog-create-02-validation-errors.png
catalog-create-03-brand-dropdown.png
catalog-edit-01-full-page.png
catalog-edit-02-validation-error.png
catalog-details-01-full-page.png
catalog-delete-01-confirmation.png
about-01-full-page.png
contact-01-full-page.png
```

---

## 🎨 CSS Classes to Document

For each page, note all CSS classes used:

**Buttons**:
- [ ] Primary button: `esh-button esh-button-primary` or other?
- [ ] Secondary button: `esh-button esh-button-secondary` or other?

**Table**:
- [ ] Table wrapper: `esh-table` or other?
- [ ] Table header: `esh-table-header` or other?
- [ ] Thumbnail image: `esh-thumbnail` or other?
- [ ] Price: `esh-price` or other?
- [ ] Action links: `esh-table-link` or other?

**Pagination**:
- [ ] Pagination wrapper: `esh-pager` or other?
- [ ] Pagination item: `esh-pager-item` or other?
- [ ] Hidden state: `esh-pager-item--hidden` or other?

**Forms**:
- [ ] Form wrapper: `form-horizontal` or other?
- [ ] Form group: `form-group` or other?
- [ ] Form control: `form-control` or other?
- [ ] Validation error: `text-danger` or other?

---

## 🔍 Browser DevTools Inspection

### Inspect Network Requests

1. Open browser DevTools (F12)
2. Go to Network tab
3. Navigate through pages and capture:

**For Catalog List**:
- [ ] Initial page load: HTTP method, URL, response time
- [ ] Pagination click: any AJAX requests? Or full page reload?

**For Create Product**:
- [ ] Form submission: POST request URL, payload format
- [ ] Response: redirect URL or JSON response?
- [ ] Validation: client-side or server-side?

**For Edit Product**:
- [ ] Page load: how is product data fetched?
- [ ] Form submission: PUT or POST? Payload format?

**For Delete Product**:
- [ ] Delete action: POST or DELETE method?
- [ ] Confirmation: JavaScript confirm() or separate page?

### Inspect HTML Structure

For each page, use "Inspect Element" to capture:
- [ ] Exact HTML structure of key elements
- [ ] CSS classes actually applied
- [ ] Data attributes (data-*)
- [ ] Form field IDs and names

---

## 📊 Data Export

### Export Product Data

Navigate to catalog list and export current product data:

**Create**: `docs/seams/catalog-list/runtime/product-data-export.json`

```json
{
  "exported_at": "2026-03-02T...",
  "total_products": 12,
  "products": [
    {
      "id": 1,
      "name": "...",
      "description": "...",
      "price": 19.50,
      "brand": "...",
      "type": "...",
      "stock": 100,
      "picture": "1.png"
    }
  ]
}
```

### Export Validation Messages

**Create**: `docs/seams/catalog-crud/runtime/validation-messages.json`

```json
{
  "name_required": "exact error message",
  "price_invalid_format": "exact error message",
  "price_out_of_range": "exact error message",
  "stock_out_of_range": "exact error message"
}
```

---

## 🎯 Quick Capture Script (PowerShell)

Save this as `capture-runtime-evidence.ps1`:

```powershell
# Quick screenshot capture script
# Requires: Firefox/Chrome with manual navigation

$baseUrl = "http://localhost:50586"
$outputDir = "docs\seams\catalog-list\runtime\screenshots"

# Create output directory
New-Item -ItemType Directory -Force -Path $outputDir

Write-Host "=== Runtime Evidence Capture ==="
Write-Host ""
Write-Host "Navigate to each URL and take screenshots manually:"
Write-Host ""
Write-Host "1. $baseUrl/"
Write-Host "   Save as: $outputDir\catalog-list-01-full-page.png"
Write-Host ""
Write-Host "2. $baseUrl/Catalog/Create"
Write-Host "   Save as: $outputDir\catalog-create-01-empty-form.png"
Write-Host "   Submit empty form, then save: $outputDir\catalog-create-02-validation-errors.png"
Write-Host ""
Write-Host "3. $baseUrl/Catalog/Edit/1"
Write-Host "   Save as: $outputDir\catalog-edit-01-full-page.png"
Write-Host ""
Write-Host "4. $baseUrl/Catalog/Details/1"
Write-Host "   Save as: $outputDir\catalog-details-01-full-page.png"
Write-Host ""
Write-Host "5. $baseUrl/Catalog/Delete/1"
Write-Host "   Save as: $outputDir\catalog-delete-01-confirmation.png"
Write-Host ""
Write-Host "6. $baseUrl/About"
Write-Host "   Save as: $outputDir\about-01-full-page.png"
Write-Host ""
Write-Host "7. $baseUrl/Contact"
Write-Host "   Save as: $outputDir\contact-01-full-page.png"
Write-Host ""
Write-Host "Press any key when done..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
```

---

## 📝 After Capture

Once you've captured all evidence:

1. **Create runtime observation document**:
   - `docs/seams/catalog-list/runtime/runtime-observations.md`
   - `docs/seams/catalog-crud/runtime/runtime-observations.md`

2. **Compare with static analysis**:
   - Check if discovered UI behavior matches code analysis
   - Note any discrepancies

3. **Update migration specs**:
   - Update `ui-behavior.md` with actual runtime findings
   - Add exact validation messages
   - Add exact button text and labels

4. **Create parity test baselines**:
   - Store screenshots in `legacy-golden/{seam}/screenshots/`
   - Create baseline index: `legacy-golden/{seam}/BASELINE_INDEX.md`

---

## 🚀 Quick Start

**Option 1**: Manual capture (recommended for first time)
1. Open http://localhost:50586/ in browser
2. Follow checklist above
3. Take screenshots of each page
4. Document findings in runtime-observations.md

**Option 2**: Automated capture (requires setup)
1. Install Playwright: `npm install -D @playwright/test`
2. Run: `npx playwright codegen http://localhost:50586/`
3. Generate screenshot script
4. Execute and save to docs/seams/*/runtime/screenshots/

---

## 📞 Questions to Answer

After capturing runtime evidence, answer these:

1. **Pagination**: Full page reload or AJAX?
2. **Validation**: Client-side JavaScript or server-side?
3. **Form submission**: Traditional POST or AJAX?
4. **Navigation**: Do action links use query params or route params?
5. **Images**: Exact dimensions of thumbnails?
6. **Spacing**: Exact padding/margin values?
7. **Colors**: Exact hex codes for primary/secondary colors?
8. **Fonts**: Font family and sizes?

---

**Next Step**: Capture evidence and create `runtime-observations.md` for each seam.
