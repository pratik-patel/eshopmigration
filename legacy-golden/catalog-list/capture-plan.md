# Golden Baseline Capture Plan: catalog-list

**Date**: 2026-03-02
**Application Type**: Web Application
**Framework**: ASP.NET WebForms 4.7.2
**Application URL**: http://localhost:50586/

---

## Application Detection

**Source**: `docs/context-fabric/project-facts.json`
- Framework: ASP.NET WebForms
- .NET Version: 4.7.2
- Type: Web application (e-commerce catalog)

**Capture Approach**: Browser automation (Playwright/Selenium)

---

## Capture Requirements

### Pre-Execution Checklist
- [?] Is application URL accessible? → http://localhost:50586/
- [?] Do test credentials/authentication work? → No auth required
- [?] Is browser automation tool available? → **BLOCKED**
- [?] Can access application backend/database? → Yes (SQLite copy available)
- [?] Is application in stable test environment? → Yes (user confirmed)

---

## Workflows to Capture (from spec.md)

### Workflow 1: View Catalog List
**Entry point**: Default.aspx (/)
**Steps**:
1. Navigate to homepage
2. View product table with 10 items
3. Observe pagination controls
4. Click "Next" button (if more than 10 items)
5. Verify page 2 displays correctly
6. Click "Previous" button
7. Return to page 1

**Screenshots needed**:
- `catalog-list_step_01_initial_load.png` - First page of products
- `catalog-list_step_02_full_table.png` - Complete 10-item table
- `catalog-list_step_03_pagination_controls.png` - Close-up of pagination
- `catalog-list_step_04_page_2.png` - Second page after clicking Next
- `catalog-list_step_05_page_1_return.png` - Back to first page

### Workflow 2: Navigate to Create
**Entry point**: Default.aspx → Create New button
**Steps**:
1. From catalog list
2. Click "Create New" button
3. Navigate to Create.aspx

**Screenshots needed**:
- `catalog-list_step_06_create_button.png` - Highlighted Create New button
- `catalog-list_step_07_navigate_create.png` - Create page loads (transition)

### Workflow 3: Navigate to Edit/Details/Delete
**Entry point**: Default.aspx → Action links
**Steps**:
1. From catalog list
2. Click "Edit" link for first product
3. Verify Edit page loads
4. Return to list
5. Click "Details" link for first product
6. Verify Details page loads
7. Return to list
8. Click "Delete" link for first product
9. Verify Delete page loads

**Screenshots needed**:
- `catalog-list_step_08_edit_link_hover.png` - Edit link highlighted
- `catalog-list_step_09_details_link_hover.png` - Details link highlighted
- `catalog-list_step_10_delete_link_hover.png` - Delete link highlighted

---

## Data Exports

### Catalog Items List (Page 1)
**File**: `exports/catalog_items_page_1.json`
**Content**: First 10 products as displayed in table

```json
{
  "page_index": 0,
  "page_size": 10,
  "total_items": 12,
  "items": [
    {
      "id": 1,
      "name": ".NET Bot Black Hoodie",
      "description": "...",
      "brand": ".NET",
      "type": "T-Shirt",
      "price": 19.50,
      "picture_file_name": "1.png",
      "available_stock": 100,
      "restock_threshold": 10,
      "max_stock_threshold": 200
    }
  ]
}
```

### Catalog Items List (Page 2)
**File**: `exports/catalog_items_page_2.json`
**Content**: Remaining 2 products

---

## Database Snapshots

### Before Navigation
**File**: `db-snapshots/before_view_list.json`
**Tables**: CatalogItems, CatalogBrands, CatalogTypes
**Action**: Read-only, no changes expected

### After Navigation
**File**: `db-snapshots/after_view_list.json`
**Expected**: No changes (read-only workflow)

---

## HTTP Captures

### GET /Default.aspx
**File**: `exports/http_get_default.har`
**Expected**: HTML response with embedded product data

### GET /Default.aspx?page=2
**File**: `exports/http_get_page_2.har`
**Expected**: HTML response with page 2 products

---

## Coverage

**Spec workflows**: 3 (View list, Navigate to Create, Navigate to Edit/Details/Delete)
**Edge cases**:
- Empty catalog (no products)
- Single page (≤10 products, no pagination)
- Multiple pages (>10 products)

---

## Capture Method

**Tool**: Playwright (Node.js or Python)
**Browser**: Chromium
**Viewport**: 1920x1080 (desktop)
**Wait Strategy**: Wait for network idle after navigation

---

## Blockers

See: `docs/BASELINE_BLOCKERS.md` if capture cannot proceed.
