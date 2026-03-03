# DTO Mapping: Catalog CRUD

**Seam**: catalog-crud
**Date**: 2026-03-02
**Evidence Source**: Runtime verification via browser agent

---

## Request DTOs

### CreateCatalogItemRequest / UpdateCatalogItemRequest

Maps Create and Edit form fields to REST API request body.

| Legacy Field (Create) | Legacy Field (Edit) | Type | OpenAPI Field | Notes | Evidence |
|----------------------|---------------------|------|---------------|-------|----------|
| `ctl00$MainContent$Name` | `ctl00$MainContent$Name` | text | `name` | Required, max 50 chars | workflow.json:33-38 |
| `ctl00$MainContent$Description` | `ctl00$MainContent$Description` | text | `description` | Optional, max 255 chars | workflow.json:40-46 |
| `ctl00$MainContent$Brand` | `ctl00$MainContent$BrandDropDownList` | select-one | `catalogBrandId` | Required, foreign key to brands | workflow.json:48-55, 127-133 |
| `ctl00$MainContent$Type` | `ctl00$MainContent$TypeDropDownList` | select-one | `catalogTypeId` | Required, foreign key to types | workflow.json:56-63, 134-141 |
| `ctl00$MainContent$Price` | `ctl00$MainContent$Price` | text | `price` | Decimal, 0-1M, max 2 decimals | workflow.json:64-71, 142-149 |
| N/A (auto-generated on create) | `ctl00$MainContent$PictureFileName` | text | `pictureFileName` | Optional, picture filename | workflow.json:150-157 |
| `ctl00$MainContent$Stock` | `ctl00$MainContent$Stock` | text | `availableStock` | Integer, 0-10M | workflow.json:73-79, 158-166 |
| `ctl00$MainContent$Restock` | `ctl00$MainContent$Restock` | text | `restockThreshold` | Integer, 0-10M | workflow.json:80-87, 167-174 |
| `ctl00$MainContent$Maxstock` | `ctl00$MainContent$Maxstock` | text | `maxStockThreshold` | Integer, 0-10M | workflow.json:88-95, 175-181 |

**Field Naming Differences**:
- Legacy uses `Stock`, `Restock`, `Maxstock` (abbreviated)
- OpenAPI uses `availableStock`, `restockThreshold`, `maxStockThreshold` (explicit)
- Legacy uses `Brand`/`BrandDropDownList`, `Type`/`TypeDropDownList` (inconsistent)
- OpenAPI uses `catalogBrandId`, `catalogTypeId` (consistent foreign key naming)

**Default Values** (Create form):
- `price`: `"0.00"`
- `availableStock`: `0`
- `restockThreshold`: `0`
- `maxStockThreshold`: `0`

---

## Response DTOs

### CatalogItemResponse

Maps database fields and Details view to REST API response.

| Legacy DB Field (inferred) | Details View Label | Type | OpenAPI Field | Notes | Evidence |
|---------------------------|-------------------|------|---------------|-------|----------|
| `id` | N/A (not displayed) | int | `id` | Primary key | synthetic_product_1.json:6 |
| `name` | Name | string | `name` | Product name | workflow.json:197-198, synthetic_product_1.json:7 |
| `description` | Description | string | `description` | Product description | workflow.json:200-202, synthetic_product_1.json:8 |
| `price` | Price | decimal | `price` | Product price | workflow.json:212-214, synthetic_product_1.json:9 |
| `picture_file_name` | Picture name | string | `pictureFileName` | Filename only | workflow.json:216-218, synthetic_product_1.json:10 |
| `picture_uri` | N/A | string | `pictureUri` | Full URI (computed, nullable) | synthetic_product_1.json:11 |
| `catalog_type_id` | N/A | int | `catalogTypeId` | Foreign key to types | synthetic_product_1.json:12 |
| `catalog_brand_id` | N/A | int | `catalogBrandId` | Foreign key to brands | synthetic_product_1.json:13 |
| `available_stock` | Stock | int | `availableStock` | Available stock | workflow.json:220-222, synthetic_product_1.json:14 |
| `restock_threshold` | Restock | int | `restockThreshold` | Restock threshold | workflow.json:224-226, synthetic_product_1.json:15 |
| `max_stock_threshold` | Max stock | int | `maxStockThreshold` | Max stock threshold | workflow.json:228-230, synthetic_product_1.json:16 |
| `on_reorder` | N/A (not displayed) | bool | `onReorder` | Reorder flag | synthetic_product_1.json:17 |

**Nested Objects**:

#### `catalogType` (nested in response)

| Legacy DB Field | Details View Label | Type | OpenAPI Field | Notes | Evidence |
|----------------|-------------------|------|---------------|-------|----------|
| `id` | N/A | int | `id` | Type ID | synthetic_product_1.json:19 |
| `type` | Type | string | `type` | Type name | workflow.json:208-210, synthetic_product_1.json:20 |

#### `catalogBrand` (nested in response)

| Legacy DB Field | Details View Label | Type | OpenAPI Field | Notes | Evidence |
|----------------|-------------------|------|---------------|-------|----------|
| `id` | N/A | int | `id` | Brand ID | synthetic_product_1.json:23 |
| `brand` | Brand | string | `brand` | Brand name | workflow.json:204-206, synthetic_product_1.json:24 |

**Naming Convention**:
- Legacy DB uses `snake_case` (e.g., `picture_file_name`, `catalog_type_id`)
- OpenAPI uses `camelCase` (e.g., `pictureFileName`, `catalogTypeId`)
- Nested objects use `camelCase` for consistency

---

## Metadata DTOs

### CatalogBrand

Maps brand dropdown options.

| Legacy Dropdown | Type | OpenAPI Field | Notes | Evidence |
|----------------|------|---------------|-------|----------|
| Option value | int | `id` | Brand ID | synthetic_brands.json:7-25 |
| Option text | string | `brand` | Brand name | synthetic_brands.json:7-25 |

**Available Brands** (runtime-verified):
1. `.NET` (id: 1)
2. `Other` (id: 2)
3. `Azure` (id: 3)
4. `Visual Studio` (id: 4)
5. `SQL Server` (id: 5)

**Legacy Fields**:
- Create: `ctl00$MainContent$Brand` (default value: `"1"`)
- Edit: `ctl00$MainContent$BrandDropDownList`

---

### CatalogType

Maps type dropdown options.

| Legacy Dropdown | Type | OpenAPI Field | Notes | Evidence |
|----------------|------|---------------|-------|----------|
| Option value | int | `id` | Type ID | synthetic_types.json:7-22 |
| Option text | string | `type` | Type name | synthetic_types.json:7-22 |

**Available Types** (runtime-verified):
1. `Mug` (id: 1)
2. `T-Shirt` (id: 2)
3. `Sheet` (id: 3)
4. `USB Memory Stick` (id: 4)

**Legacy Fields**:
- Create: `ctl00$MainContent$Type` (default value: `"1"`)
- Edit: `ctl00$MainContent$TypeDropDownList`

---

## Validation Error Mapping

### ValidationErrorResponse

Maps ASP.NET validation messages to REST API error format.

| Legacy Error Display | OpenAPI Field | Notes | Evidence |
|---------------------|---------------|-------|----------|
| Inline below field with CSS class `field-validation-valid text-danger` | `errors[].field` | Field name (e.g., `"name"`) | synthetic_validation_errors.json:7-77 |
| Error message text | `errors[].message` | Exact error text from legacy | synthetic_validation_errors.json:10-76 |

**Validation Rules** (runtime-verified):

#### Name Field
- **Rule**: Required
- **Trigger**: Empty string
- **Error**: `"The Name field is required."`
- **Evidence**: synthetic_validation_errors.json:7-14

#### Price Field
- **Rule**: Range (0 to 1,000,000)
- **Trigger**: `< 0` or `> 1000000`
- **Error**: `"The Price must be a positive number with maximum two decimals between 0 and 1 million."`
- **Evidence**: synthetic_validation_errors.json:16-23

- **Rule**: Decimal places (max 2)
- **Trigger**: More than 2 decimal places (e.g., `12.999`)
- **Error**: `"The Price must be a positive number with maximum two decimals between 0 and 1 million."`
- **Evidence**: synthetic_validation_errors.json:24-32

#### Available Stock Field
- **Rule**: Range (0 to 10,000,000)
- **Trigger**: `< 0` or `> 10000000`
- **Error**: `"The field Stock must be between 0 and 10 million."`
- **Evidence**: synthetic_validation_errors.json:33-41

#### Restock Threshold Field
- **Rule**: Range (0 to 10,000,000)
- **Trigger**: `< 0` or `> 10000000`
- **Error**: `"The field Restock must be between 0 and 10 million."`
- **Evidence**: synthetic_validation_errors.json:42-50

#### Max Stock Threshold Field
- **Rule**: Range (0 to 10,000,000)
- **Trigger**: `< 0` or `> 10000000`
- **Error**: `"The field Max stock must be between 0 and 10 million."`
- **Evidence**: synthetic_validation_errors.json:51-59

#### Catalog Brand ID Field
- **Rule**: Required
- **Trigger**: Not selected (empty dropdown)
- **Error**: `"Brand is required"`
- **Evidence**: synthetic_validation_errors.json:60-68

#### Catalog Type ID Field
- **Rule**: Required
- **Trigger**: Not selected (empty dropdown)
- **Error**: `"Type is required"`
- **Evidence**: synthetic_validation_errors.json:69-77

**Error Response Structure**:
```json
{
  "code": "VALIDATION_ERROR",
  "message": "Validation failed",
  "errors": [
    {
      "field": "name",
      "message": "The Name field is required."
    }
  ]
}
```

---

## NOT FOUND Error Mapping

### ErrorResponse (404)

| Legacy Behavior | OpenAPI Field | Notes |
|----------------|---------------|-------|
| Page not found or record not found | `code` | `"NOT_FOUND"` |
| Error message describing what wasn't found | `message` | e.g., `"Catalog item with id '999' not found"` |

---

## Test Data Summary

### Product ID 1 (.NET Bot Black Hoodie)

**Source**: synthetic_product_1.json, grid-data.json row 0

| Field | Value | Evidence |
|-------|-------|----------|
| id | 1 | synthetic_product_1.json:6 |
| name | `.NET Bot Black Hoodie` | synthetic_product_1.json:7, grid-data.json:20 |
| description | `.NET Bot Black Hoodie, and more` | synthetic_product_1.json:8 |
| price | 19.50 | synthetic_product_1.json:9, grid-data.json:24 |
| pictureFileName | `1.png` | synthetic_product_1.json:10, grid-data.json:25 |
| catalogTypeId | 2 (T-Shirt) | synthetic_product_1.json:12, grid-data.json:23 |
| catalogBrandId | 1 (.NET) | synthetic_product_1.json:13, grid-data.json:22 |
| availableStock | 100 | synthetic_product_1.json:14, grid-data.json:26 |
| restockThreshold | 0 | synthetic_product_1.json:15, grid-data.json:27 |
| maxStockThreshold | 0 | synthetic_product_1.json:16, grid-data.json:28 |
| onReorder | false | synthetic_product_1.json:17 |

---

## Unmapped Fields

**None**. All legacy form fields and database fields have been mapped to OpenAPI schemas.

**Notes**:
- `pictureUri` is computed field (not stored in DB, not in form)
- `onReorder` is in DB but not displayed in Details view or editable in forms
- ASP.NET Web Forms hidden fields (`__VIEWSTATE`, `__EVENTTARGET`, etc.) are implementation details and not mapped to REST API

---

## Evidence Priority

1. **Runtime Capture** (highest priority):
   - workflow.json — actual form fields with IDs, types, and values
   - synthetic_product_1.json — actual database record structure
   - synthetic_validation_errors.json — actual validation error messages
   - synthetic_brands.json, synthetic_types.json — actual dropdown options
   - grid-data.json — actual grid row data

2. **Code Discovery**:
   - Not used (no discovery.md available for this seam yet)

3. **Specification**:
   - Not used (spec.md not referenced for this contract)

---

## Validation Strategy

All validation rules in OpenAPI contract are traceable to:
1. Exact error messages from synthetic_validation_errors.json
2. Business rule constraints (BR-001 through BR-005)
3. Field types and constraints observed in runtime forms

**No invented validations**. Every constraint has evidence.
