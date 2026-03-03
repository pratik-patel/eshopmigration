# Catalog CRUD API Contract

**Seam**: catalog-crud
**Version**: v1
**Status**: ✓ Complete - Ready for Implementation
**Generated**: 2026-03-02

---

## Files

### [openapi.yaml](openapi.yaml)
**OpenAPI 3.1 specification** for catalog item CRUD operations.

**Endpoints**:
- `POST /api/catalog/items` — Create catalog item
- `GET /api/catalog/items/{id}` — Get catalog item by ID
- `PUT /api/catalog/items/{id}` — Update catalog item
- `DELETE /api/catalog/items/{id}` — Delete catalog item
- `GET /api/catalog/brands` — List all brands (dropdown data)
- `GET /api/catalog/types` — List all types (dropdown data)

**Validation**: YAML syntax validated ✓

---

### [dto-mapping.md](dto-mapping.md)
**Field-by-field mapping** from legacy Web Forms to OpenAPI schemas.

**Maps**:
- Legacy form field IDs (`ctl00$MainContent$Name`) → OpenAPI fields (`name`)
- Legacy database fields (`available_stock`) → OpenAPI fields (`availableStock`)
- Legacy validation errors → OpenAPI error responses
- Legacy dropdown options → OpenAPI reference data

**Evidence**: Every mapping links to runtime capture files (workflow.json, synthetic_*.json)

---

### [contract-notes.md](contract-notes.md)
**Design decisions and rationale** for contract choices.

**Explains**:
- Why REST resource modeling was chosen
- Field naming conventions (camelCase vs snake_case)
- Required vs optional field decisions
- Validation error format design
- Nested object strategy
- Test strategy and parity approach

**References**: All decisions traceable to runtime evidence or REST best practices

---

## Evidence Sources

All contract elements derived from **runtime-verified data**:

1. **workflow.json** — Real form fields captured from legacy application
   - Form field IDs: `ctl00$MainContent$Name`, `ctl00$MainContent$Brand`, etc.
   - Field types, default values, button labels

2. **synthetic_product_1.json** — Real database record for Product ID 1
   - Complete record structure with nested relationships
   - Field names, types, and values

3. **synthetic_validation_errors.json** — Real validation rules and error messages
   - Exact error text: `"The Name field is required."`, etc.
   - Validation triggers and business rule references (BR-001 through BR-005)

4. **synthetic_brands.json** — Real brand dropdown options
   - 5 brands: `.NET`, `Other`, `Azure`, `Visual Studio`, `SQL Server`

5. **synthetic_types.json** — Real type dropdown options
   - 4 types: `Mug`, `T-Shirt`, `Sheet`, `USB Memory Stick`

6. **grid-data.json** — Real grid data with 10 products
   - Test data for response examples

**No Invented Data**. Every endpoint, field, validation rule, and error message has traceable evidence.

---

## Quick Start

### Generate TypeScript Types (Frontend)

```bash
# Install openapi-typescript
npm install -D openapi-typescript

# Generate types
npx openapi-typescript catalog-crud/contracts/openapi.yaml -o src/types/catalog-api.d.ts
```

### Use in React Component

```typescript
import type { components } from '@/types/catalog-api';

type CatalogItem = components['schemas']['CatalogItemResponse'];
type CreateRequest = components['schemas']['CreateCatalogItemRequest'];

// Type-safe API call
const createItem = async (data: CreateRequest): Promise<CatalogItem> => {
  const response = await fetch('/api/catalog/items', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return response.json();
};
```

### Generate Pydantic Models (Backend)

```bash
# Install datamodel-code-generator
pip install datamodel-code-generator

# Generate Pydantic models
datamodel-codegen \
  --input catalog-crud/contracts/openapi.yaml \
  --output backend/app/catalog/schemas.py \
  --input-file-type openapi
```

### Use in FastAPI Route

```python
from fastapi import APIRouter, HTTPException, status
from app.catalog.schemas import (
    CreateCatalogItemRequest,
    CatalogItemResponse,
    ValidationErrorResponse
)

router = APIRouter(prefix="/api/catalog", tags=["catalog-items"])

@router.post(
    "/items",
    response_model=CatalogItemResponse,
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": ValidationErrorResponse}}
)
async def create_catalog_item(data: CreateCatalogItemRequest):
    # Validation happens automatically via Pydantic
    # Business logic here
    ...
```

---

## Test Examples

### Valid Create Request

```json
POST /api/catalog/items
{
  "name": ".NET Bot Black Hoodie",
  "description": ".NET Bot Black Hoodie, and more",
  "catalogBrandId": 1,
  "catalogTypeId": 2,
  "price": 19.50,
  "pictureFileName": "1.png",
  "availableStock": 100,
  "restockThreshold": 0,
  "maxStockThreshold": 0
}
```

**Expected Response**: `201 Created`
```json
{
  "id": 1,
  "name": ".NET Bot Black Hoodie",
  "description": ".NET Bot Black Hoodie, and more",
  "price": 19.50,
  "pictureFileName": "1.png",
  "pictureUri": null,
  "catalogTypeId": 2,
  "catalogBrandId": 1,
  "availableStock": 100,
  "restockThreshold": 0,
  "maxStockThreshold": 0,
  "onReorder": false,
  "catalogType": {
    "id": 2,
    "type": "T-Shirt"
  },
  "catalogBrand": {
    "id": 1,
    "brand": ".NET"
  }
}
```

### Validation Error (Empty Name)

```json
POST /api/catalog/items
{
  "name": "",
  "description": "",
  "price": null
}
```

**Expected Response**: `400 Bad Request`
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

### Get Item (Success)

```
GET /api/catalog/items/1
```

**Expected Response**: `200 OK`
```json
{
  "id": 1,
  "name": ".NET Bot Black Hoodie",
  "catalogBrand": {
    "id": 1,
    "brand": ".NET"
  },
  "catalogType": {
    "id": 2,
    "type": "T-Shirt"
  },
  ...
}
```

### Get Item (Not Found)

```
GET /api/catalog/items/999
```

**Expected Response**: `404 Not Found`
```json
{
  "code": "NOT_FOUND",
  "message": "Catalog item with id '999' not found"
}
```

---

## Validation Rules Summary

### Required Fields
- `name` — Must not be empty

### Price Validation
- Must be >= 0 and <= 1,000,000
- Must have maximum 2 decimal places
- Error: `"The Price must be a positive number with maximum two decimals between 0 and 1 million."`

### Stock Validation
- `availableStock`, `restockThreshold`, `maxStockThreshold` must be >= 0 and <= 10,000,000
- Each field has its own error message:
  - `"The field Stock must be between 0 and 10 million."`
  - `"The field Restock must be between 0 and 10 million."`
  - `"The field Max stock must be between 0 and 10 million."`

### Foreign Key Validation
- `catalogBrandId` must reference existing brand (1-5)
- `catalogTypeId` must reference existing type (1-4)
- Errors: `"Brand is required"`, `"Type is required"`

---

## Reference Data

### Brands (GET /api/catalog/brands)
```json
[
  { "id": 1, "brand": ".NET" },
  { "id": 2, "brand": "Other" },
  { "id": 3, "brand": "Azure" },
  { "id": 4, "brand": "Visual Studio" },
  { "id": 5, "brand": "SQL Server" }
]
```

### Types (GET /api/catalog/types)
```json
[
  { "id": 1, "type": "Mug" },
  { "id": 2, "type": "T-Shirt" },
  { "id": 3, "type": "Sheet" },
  { "id": 4, "type": "USB Memory Stick" }
]
```

---

## Implementation Checklist

### Backend (Python + FastAPI)
- [ ] Generate Pydantic models from OpenAPI spec
- [ ] Create SQLAlchemy models with `snake_case` fields
- [ ] Implement CRUD route handlers
- [ ] Add custom validators for price decimals and stock ranges
- [ ] Map validation error messages to match legacy text
- [ ] Eager load `catalogBrand` and `catalogType` relationships
- [ ] Add exception handlers for 404 and validation errors
- [ ] Write unit tests for all validation rules
- [ ] Write integration tests for all endpoints
- [ ] Run parity tests against synthetic data

### Frontend (React + TypeScript)
- [ ] Generate TypeScript types from OpenAPI spec
- [ ] Create API client functions (fetchBrands, fetchTypes, etc.)
- [ ] Build Create form with React Hook Form + Zod
- [ ] Build Edit form (similar to Create, with pictureFileName)
- [ ] Build Details view (read-only display)
- [ ] Build Delete confirmation modal
- [ ] Add TanStack Query hooks for all operations
- [ ] Map API validation errors to form field errors
- [ ] Display error messages inline below fields
- [ ] Test all workflows end-to-end with Playwright

---

## Contract Validation

**YAML Syntax**: ✓ Validated with Python YAML parser

**OpenAPI 3.1 Compliance**: ✓ All required fields present
- `openapi: 3.1.0`
- `info.title`, `info.version`
- `paths` with operationId for all endpoints
- `components.schemas` for all DTOs
- Request/response examples provided

**Evidence Traceability**: ✓ All elements traceable to runtime data
- No invented endpoints
- No invented fields
- No invented validation rules
- No invented error messages

**DTO Mapping**: ✓ Complete field-by-field mapping with evidence links

**Design Rationale**: ✓ All decisions documented in contract-notes.md

---

## Next Steps

1. **Backend Implementation**: Use openapi.yaml as source of truth for route handlers and Pydantic models
2. **Frontend Implementation**: Generate TypeScript types and build React components
3. **Contract Tests**: Validate all request/response examples
4. **Parity Tests**: Compare API behavior with legacy page behavior
5. **Integration**: Connect React frontend to FastAPI backend

**Status**: Contract is complete and ready for implementation. No blockers.
