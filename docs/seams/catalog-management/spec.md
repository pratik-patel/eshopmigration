# Seam Specification: Catalog Management

**Seam ID**: `catalog-management`
**Priority**: 1 (only seam - complete application)
**Status**: Proposed
**Last Updated**: 2026-03-03

---

## Purpose

Complete product catalog management system enabling users to browse, view, and manage (CRUD) product listings with associated images, brands, and types.

---

## Business Capability

**Product Catalog Management** - Core e-commerce functionality for maintaining product inventory, pricing, stock levels, and product information.

---

## Delivery Surfaces

### 1. Product List Page
- **Legacy**: `Default.aspx` → `/`
- **Modern**: `GET /api/catalog`
- **Authentication**: None (public)
- **Operations**:
  - List products with pagination
  - Filter by brand/type (future enhancement)
  - Search by name (future enhancement)

### 2. Product Details Page
- **Legacy**: `Catalog/Details.aspx` → `/Catalog/Details/{id}`
- **Modern**: `GET /api/catalog/{id}`
- **Authentication**: None (public)
- **Operations**: View single product details

### 3. Create Product Page
- **Legacy**: `Catalog/Create.aspx` → `/Catalog/Create`
- **Modern**: `POST /api/catalog`
- **Authentication**: Required (JWT)
- **Operations**: Create new product with optional image

### 4. Edit Product Page
- **Legacy**: `Catalog/Edit.aspx` → `/Catalog/Edit/{id}`
- **Modern**: `PUT /api/catalog/{id}`
- **Authentication**: Required (JWT)
- **Operations**: Update existing product and image

### 5. Delete Product Page
- **Legacy**: `Catalog/Delete.aspx` → `/Catalog/Delete/{id}`
- **Modern**: `DELETE /api/catalog/{id}`
- **Authentication**: Required (JWT)
- **Operations**: Delete product (and associated image)

### 6. Image Upload Service
- **Legacy**: `Catalog/PicUploader.asmx` → `/Catalog/PicUploader.asmx`
- **Modern**: `POST /api/catalog/images`
- **Authentication**: Required (JWT) - **MUST ADD** (legacy has none)
- **Operations**: Upload product image to temporary storage

---

## Data Ownership

### Writes (Exclusive)
- **Catalog** table (all CRUD operations)
- Product images in blob storage

### Reads
- **Catalog** table
- **CatalogType** table (reference data)
- **CatalogBrand** table (reference data)

### Foreign Key Relationships (Within Seam)
- `Catalog.CatalogTypeId` → `CatalogType.Id` (required)
- `Catalog.CatalogBrandId` → `CatalogBrand.Id` (required)

### Sequences
- `catalog_hilo` (legacy - replace with auto-increment or UUID)

---

## Database Schema

### Catalog Table
```sql
CREATE TABLE Catalog (
    Id INT PRIMARY KEY,
    Name NVARCHAR(50) NOT NULL,
    Description NVARCHAR(MAX),
    Price DECIMAL(18,2) NOT NULL,
    PictureFileName NVARCHAR(MAX) NOT NULL,
    CatalogTypeId INT NOT NULL,
    CatalogBrandId INT NOT NULL,
    AvailableStock INT NOT NULL,
    RestockThreshold INT NOT NULL,
    MaxStockThreshold INT NOT NULL,
    OnReorder BIT NOT NULL,
    FOREIGN KEY (CatalogTypeId) REFERENCES CatalogType(Id),
    FOREIGN KEY (CatalogBrandId) REFERENCES CatalogBrand(Id)
);
```

### CatalogType Table (Reference Data)
```sql
CREATE TABLE CatalogType (
    Id INT PRIMARY KEY IDENTITY,
    Type NVARCHAR(100) NOT NULL
);
```

### CatalogBrand Table (Reference Data)
```sql
CREATE TABLE CatalogBrand (
    Id INT PRIMARY KEY IDENTITY,
    Brand NVARCHAR(100) NOT NULL
);
```

---

## External Dependencies

### 1. Image Storage
- **Legacy**: Azure Blob Storage OR local mock storage
- **Adapter**: `IImageService` interface
- **Modern**: S3-compatible storage or local filesystem adapter
- **Migration**: Implement `IImageService` adapter for chosen storage

### 2. Authentication
- **Legacy**: Azure AD OpenID Connect (optional)
- **Modern**: JWT bearer tokens
- **Migration**: Replace OpenID Connect with JWT validation middleware

### 3. Database
- **Legacy**: SQL Server with Entity Framework 6
- **Modern**: PostgreSQL with async SQLAlchemy 2.x
- **Migration**:
  - Replace HiLo sequence with auto-increment PRIMARY KEY
  - Port EF6 mappings to SQLAlchemy models

---

## Transaction Boundaries

### Create Product
- **Scope**: Single operation
- **Tables**: `Catalog` (INSERT)
- **External**: Image storage (if image provided)
- **Consistency**: Strong (atomic DB + storage operation)

### Update Product
- **Scope**: Single operation
- **Tables**: `Catalog` (UPDATE)
- **External**: Image storage (if image changed)
- **Consistency**: Strong (atomic DB + storage operation)

### Delete Product
- **Scope**: Single operation
- **Tables**: `Catalog` (DELETE)
- **External**: Image storage (delete old image) - **NOT IMPLEMENTED IN LEGACY**
- **Consistency**: Strong (atomic DB operation)
- **TODO**: Add image cleanup on product deletion

---

## Cross-Seam Dependencies

### Hard Dependencies
**None** - This is the only seam in the application.

### Soft Dependencies
**None** - Self-contained seam.

### Shared Infrastructure
- Authentication middleware (JWT validation)
- Logging (structlog with JSON output)
- Configuration (pydantic-settings)
- Dependency injection (FastAPI `Depends()`)

---

## Blockers

**None** - All dependencies have clear migration paths.

---

## Verification Strategy

### Functional Parity Tests
1. **List Products**
   - Verify pagination works (page size, page index)
   - Verify product data matches legacy (name, price, description, etc.)
   - Verify brand and type relationships load correctly

2. **View Product Details**
   - Verify single product retrieval by ID
   - Verify all fields display correctly
   - Verify image URL is correct

3. **Create Product**
   - Verify product creation with all fields
   - Verify image upload and association
   - Verify validation errors display correctly
   - Verify brand/type dropdown populations

4. **Update Product**
   - Verify product update with all fields
   - Verify image replacement works
   - Verify image retention (no change) works
   - Verify validation errors display correctly

5. **Delete Product**
   - Verify product deletion by ID
   - Verify foreign key constraints (cannot delete types/brands in use)
   - **TODO**: Verify image cleanup (not in legacy)

6. **Image Upload**
   - Verify AJAX image upload to temporary storage
   - Verify uploaded image preview
   - **NEW**: Verify authentication required

### Non-Functional Parity Tests
- Response times ≤ legacy for list operations
- Image upload supports files up to 5MB
- Pagination supports large datasets (10,000+ items)
- API handles concurrent requests safely

### Data Migration Validation
- All `Catalog` records migrated with correct data
- All `CatalogType` records migrated
- All `CatalogBrand` records migrated
- All product images migrated and accessible
- Foreign key relationships intact

---

## Modern API Specification

### Endpoints

#### GET /api/catalog
List products with pagination.

**Query Parameters:**
- `page` (int, default: 0) - Page index
- `size` (int, default: 10) - Items per page
- `type_id` (int, optional) - Filter by catalog type
- `brand_id` (int, optional) - Filter by catalog brand

**Response:**
```json
{
  "items": [...],
  "page_index": 0,
  "page_size": 10,
  "total_items": 100,
  "total_pages": 10
}
```

#### GET /api/catalog/{id}
Get single product by ID.

**Response:**
```json
{
  "id": 1,
  "name": "Product Name",
  "description": "Product description",
  "price": 99.99,
  "picture_filename": "product.png",
  "picture_uri": "https://storage.example.com/products/1/product.png",
  "catalog_type": {
    "id": 1,
    "type": "Electronics"
  },
  "catalog_brand": {
    "id": 2,
    "brand": "Microsoft"
  },
  "available_stock": 100,
  "restock_threshold": 10,
  "max_stock_threshold": 500,
  "on_reorder": false
}
```

#### POST /api/catalog
Create new product (requires authentication).

**Request Body:**
```json
{
  "name": "Product Name",
  "description": "Product description",
  "price": 99.99,
  "catalog_type_id": 1,
  "catalog_brand_id": 2,
  "available_stock": 100,
  "restock_threshold": 10,
  "max_stock_threshold": 500,
  "picture_filename": "product.png"
}
```

#### PUT /api/catalog/{id}
Update existing product (requires authentication).

**Request Body:** Same as POST

#### DELETE /api/catalog/{id}
Delete product (requires authentication).

**Response:** 204 No Content

#### POST /api/catalog/images
Upload product image (requires authentication).

**Request:** multipart/form-data with file field

**Response:**
```json
{
  "temp_image_url": "https://storage.example.com/temp/12345/product.png",
  "filename": "product.png"
}
```

#### GET /api/catalog/types
Get all catalog types.

**Response:**
```json
[
  {"id": 1, "type": "Electronics"},
  {"id": 2, "type": "Clothing"}
]
```

#### GET /api/catalog/brands
Get all catalog brands.

**Response:**
```json
[
  {"id": 1, "brand": "Microsoft"},
  {"id": 2, "brand": "Nike"}
]
```

---

## Backend Implementation Notes

### Python (FastAPI)
- Use `async def` for all route handlers
- Use SQLAlchemy 2.x async with `AsyncSession`
- Use Pydantic v2 for request/response models
- Inject dependencies via `Depends()`
- Use `structlog` for JSON logging

### Key Services
```python
# app/catalog/service.py
class CatalogService:
    async def get_paginated(self, page: int, size: int) -> PaginatedResponse
    async def get_by_id(self, id: int) -> CatalogItem
    async def create(self, item: CatalogItemCreate) -> CatalogItem
    async def update(self, id: int, item: CatalogItemUpdate) -> CatalogItem
    async def delete(self, id: int) -> None
```

### Database Models
```python
# app/catalog/models.py
class CatalogItem(Base):
    __tablename__ = "catalog"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    # ... other fields

    catalog_type = relationship("CatalogType")
    catalog_brand = relationship("CatalogBrand")
```

---

## Frontend Implementation Notes

### React + TypeScript
- Use React Router v6 for routing
- Use TanStack Query for server state
- Use React Hook Form + Zod for forms
- Use shadcn/ui + Tailwind for styling

### Key Components
```typescript
// src/pages/catalog/CatalogListPage.tsx
export function CatalogListPage() {
  const { data, isLoading } = useQuery(['catalog', page, size], fetchCatalog);
  // ...
}

// src/pages/catalog/CatalogFormPage.tsx
export function CatalogFormPage({ mode }: { mode: 'create' | 'edit' }) {
  const form = useForm<CatalogItemForm>({ resolver: zodResolver(schema) });
  // ...
}
```

---

## Migration Checklist

### Phase 1: Backend API
- [ ] Set up FastAPI project structure
- [ ] Define SQLAlchemy models (Catalog, CatalogType, CatalogBrand)
- [ ] Implement Pydantic schemas (request/response models)
- [ ] Implement CatalogService with async methods
- [ ] Implement ImageService adapter
- [ ] Create API route handlers
- [ ] Add JWT authentication middleware
- [ ] Write unit tests (80% coverage target)
- [ ] Generate OpenAPI spec

### Phase 2: Frontend
- [ ] Set up React + TypeScript + Vite project
- [ ] Configure TanStack Query
- [ ] Create API client with type generation
- [ ] Build CatalogListPage with pagination
- [ ] Build CatalogDetailsPage
- [ ] Build CatalogFormPage (create/edit modes)
- [ ] Build CatalogDeleteDialog
- [ ] Implement image upload component
- [ ] Add form validation with Zod
- [ ] Write component tests (75% coverage target)

### Phase 3: Data Migration
- [ ] Export legacy database to SQL dump
- [ ] Transform schema (remove HiLo, adjust types if needed)
- [ ] Import data to PostgreSQL
- [ ] Migrate product images to new storage
- [ ] Validate data integrity (counts, relationships)

### Phase 4: Deployment
- [ ] Deploy backend to staging
- [ ] Deploy frontend to staging
- [ ] Run end-to-end parity tests
- [ ] Load test API endpoints
- [ ] Deploy to production with rollback plan
- [ ] Monitor and verify

---

## Non-Goals

These features are NOT in scope for this seam:

- Shopping cart functionality
- Order management
- Customer management
- Payment processing
- Product search (can be added later)
- Product filtering by brand/type (can be added later)
- Multi-language support
- Product reviews/ratings
- Inventory alerts/notifications
- Bulk product import/export

---

## Success Criteria

### Functional
- All CRUD operations work identically to legacy
- Pagination matches legacy behavior
- Image upload and display work correctly
- Authentication is enforced on write operations

### Non-Functional
- API response times ≤ legacy times
- Zero data loss during migration
- All security scans pass
- 80% backend code coverage
- 75% frontend code coverage
- Lighthouse score > 90

### Quality Gates
- All unit tests pass
- All integration tests pass
- All E2E tests pass
- No critical security vulnerabilities
- No performance regressions

---

## Rollback Plan

If issues occur in production:

1. Switch DNS/load balancer back to legacy application
2. Stop modern API and frontend
3. Investigate and fix issues
4. Re-deploy to staging for validation
5. Retry production deployment

**Smoke Tests** (must pass before traffic switch):
- Product list loads
- Product details load
- Create product works (authenticated)
- Edit product works (authenticated)
- Delete product works (authenticated)
- Image upload works (authenticated)

---

## Open Questions

1. **Image Storage**: Use S3-compatible service (MinIO, AWS S3) or local filesystem?
   - Recommendation: MinIO for production (S3-compatible, self-hosted), local for dev

2. **Authentication Provider**: Built-in JWT or external (Auth0, Keycloak)?
   - Recommendation: Built-in JWT for POC, can switch to external later

3. **Database**: PostgreSQL or SQLite?
   - Recommendation: PostgreSQL for production, SQLite for dev/testing

4. **ID Generation**: Auto-increment or UUID?
   - Recommendation: Auto-increment (simpler, matches legacy pattern)

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| HiLo sequence incompatibility | High | Medium | Use auto-increment PKs |
| Image upload security issue | High | High | Add JWT auth to endpoint |
| Data migration errors | Medium | High | Thorough validation + rollback |
| Performance regression | Low | Medium | Load testing before prod |
| Authentication issues | Low | High | Extensive auth testing |

---

## Timeline Estimate

- **Phase 1 (Backend)**: 4 days
- **Phase 2 (Frontend)**: 3 days
- **Phase 3 (Data Migration)**: 1 day
- **Phase 4 (Deployment)**: 2 days
- **Total**: 10 days (2 weeks with buffer)

---

## References

- Legacy codebase: `C:/Users/pratikp6/codebase/eShopModernizing/eShopModernizedWebFormsSolution`
- Context fabric: `docs/context-fabric/`
- CLAUDE.md: `C:/Users/pratikp6/codebase/eshopmigration/CLAUDE.md`
