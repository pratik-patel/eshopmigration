# Seam Spec: catalog-list

## Purpose

Display paginated catalog items with product details including name, description, price, brand, type, stock levels, and thumbnail images. This is the main landing page of the application.

## Priority & Complexity

- **Priority**: 1 (Highest - main entry point)
- **Complexity**: Low
- **Type**: Read-only

## Delivery Surfaces

### Backend API

**Endpoint**: `GET /api/catalog`

**Query Parameters**:
- `page_size` (int, default: 10) - Number of items per page
- `page_index` (int, default: 0) - Zero-based page index

**Response Schema** (OpenAPI):
```json
{
  "items": [
    {
      "id": 1,
      "name": "string",
      "description": "string",
      "price": 19.99,
      "picture_uri": "string",
      "catalog_brand": {
        "id": 1,
        "brand": "string"
      },
      "catalog_type": {
        "id": 1,
        "type": "string"
      },
      "available_stock": 100,
      "restock_threshold": 10,
      "max_stock_threshold": 500
    }
  ],
  "page_index": 0,
  "page_size": 10,
  "total_items": 100,
  "total_pages": 10
}
```

**Backend Implementation**:
- **Route**: `backend/app/catalog/router.py`
- **Service**: `backend/app/catalog/service.py` - `CatalogService.get_catalog_items_paginated()`
- **Schemas**: `backend/app/catalog/schemas.py` - `CatalogItemResponse`, `PaginatedCatalogResponse`
- **Models**: `backend/app/catalog/models.py` - SQLAlchemy models for Catalog, CatalogBrand, CatalogType

### Frontend UI

**Route**: `/catalog` (main page, also accessible at `/`)

**Component Structure**:
```
frontend/src/pages/catalog-list/
  ├── CatalogListPage.tsx          # Page component with TanStack Query
  ├── CatalogListPage.test.tsx     # Component tests
  └── components/
      ├── CatalogTable.tsx          # Table display
      ├── CatalogItem.tsx           # Individual row component
      └── Pagination.tsx            # Pagination controls
```

**Data Fetching**:
- **Hook**: `frontend/src/hooks/useCatalogList.ts`
- Uses TanStack Query for server state management
- Polling disabled (not real-time data)
- Cache invalidation on mutations from other seams

**UI Features**:
1. Product table with sortable columns
2. Thumbnail images with fallback to placeholder
3. Pagination controls (Previous/Next + page indicator)
4. Action buttons per row: Edit | Details | Delete
5. "Create New" button (top-right)
6. Responsive design with Tailwind CSS

## Data Access

### Reads
- **Catalog** table - All fields
- **CatalogBrand** table - Id, Brand (via JOIN)
- **CatalogType** table - Id, Type (via JOIN)

### Writes
- None (read-only seam)

### SQL Pattern
```sql
SELECT c.*, cb.Brand, ct.Type
FROM Catalog c
INNER JOIN CatalogBrand cb ON c.CatalogBrandId = cb.Id
INNER JOIN CatalogType ct ON c.CatalogTypeId = ct.Id
ORDER BY c.Id
OFFSET @pageSize * @pageIndex ROWS
FETCH NEXT @pageSize ROWS ONLY;
```

**SQLAlchemy equivalent**:
```python
query = (
    db.query(CatalogItem)
    .join(CatalogBrand)
    .join(CatalogType)
    .order_by(CatalogItem.id)
    .offset(page_size * page_index)
    .limit(page_size)
)
total_count = db.query(func.count(CatalogItem.id)).scalar()
```

## Dependencies

### Internal Dependencies
- None (this is the root entry point)

### External Dependencies
1. **Image Service** - Builds URLs for product images
   - Legacy: `IImageService.BuildUrlImage(catalogItem)`
   - Python: `ImageWrapper.build_image_url(catalog_item)`
   - Returns URL to Azure Blob Storage or local filesystem
   - Mock implementation returns placeholder URL

2. **Database Connection**
   - SQLAlchemy async session
   - Connection string from config/env vars

## Legacy Code References

### ASP.NET WebForms
- **UI**: `Default.aspx` + `Default.aspx.cs`
- **Service**: `Services/CatalogService.cs::GetCatalogItemsPaginated()`
- **Model**: `Models/CatalogItem.cs`, `Models/CatalogBrand.cs`, `Models/CatalogType.cs`
- **ViewModel**: `ViewModel/PaginatedItemsViewModel.cs`

### Key Legacy Patterns
1. **ListView Data Binding**:
   ```csharp
   productList.DataSource = Model.Data;
   productList.DataBind();
   ```
   → Convert to React component iteration

2. **Image URL Construction**:
   ```csharp
   foreach (var catalogItem in items)
   {
       catalogItem.PictureUri = ImageService.BuildUrlImage(catalogItem);
   }
   ```
   → Backend constructs URLs, frontend displays them

3. **Pagination Links**:
   ```csharp
   PaginationNext.NavigateUrl = GetRouteUrl("ProductsByPageRoute",
       new { index = Model.ActualPage + 1, size = Model.ItemsPerPage });
   ```
   → Convert to React Router query params

## Verification Strategy

### Unit Tests (Backend)
```python
# backend/tests/unit/test_catalog_service.py

async def test_get_catalog_items_paginated():
    # Test pagination logic
    # Verify page boundaries
    # Test empty results
    # Test total count calculation
```

### Integration Tests (Backend)
```python
# backend/tests/integration/test_catalog_api.py

async def test_catalog_list_endpoint():
    response = await client.get("/api/catalog?page_size=10&page_index=0")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total_items" in data
    assert len(data["items"]) <= 10
```

### Component Tests (Frontend)
```typescript
// frontend/src/pages/catalog-list/CatalogListPage.test.tsx

test('renders catalog items', async () => {
  render(<CatalogListPage />);
  await waitFor(() => {
    expect(screen.getByText('Product Name')).toBeInTheDocument();
  });
});

test('pagination controls work', async () => {
  // Test Next/Previous buttons
  // Verify page indicator updates
});
```

### E2E Tests (Playwright)
```typescript
// frontend/tests/e2e/catalog-list.spec.ts

test('catalog list page displays products', async ({ page }) => {
  await page.goto('/catalog');
  await expect(page.locator('table tbody tr')).toHaveCount(10);

  // Test pagination
  await page.click('text=Next');
  await expect(page).toHaveURL(/page_index=1/);
});
```

### Parity Tests

**Golden Baseline Capture**:
1. Run legacy app at http://localhost:50586
2. Capture HTTP response from Default.aspx
3. Extract data structure and field values
4. Store as `docs/seams/catalog-list/evidence/golden-baseline.json`

**Parity Verification**:
```python
# backend/tests/parity/test_catalog_list_parity.py

async def test_catalog_list_matches_legacy():
    # Compare new API response to golden baseline
    # Verify all fields present
    # Check data type consistency
    # Validate pagination metadata
```

## Migration Notes

### Backend Considerations
1. **Pagination**: Legacy uses OFFSET/FETCH, Python should use same pattern with SQLAlchemy
2. **Image URLs**: Must maintain same URL structure or update all existing image references
3. **Performance**: Add index on `Catalog.Id` for sorting if not present
4. **Caching**: Consider caching brand/type lookups (rarely change)

### Frontend Considerations
1. **Default Route**: Root `/` should redirect to `/catalog`
2. **Page Size**: Keep default of 10 items per page to match legacy
3. **Image Fallback**: Use placeholder image if `picture_uri` is null or load fails
4. **Responsive Design**: Table should be scrollable on mobile, consider card layout alternative
5. **Loading States**: Show skeleton loaders while fetching data
6. **Error Handling**: Display user-friendly error if API fails

### Data Migration
- No data migration needed (read-only)
- Verify image files accessible at expected URLs
- Check database indexes for performance

### Authentication
- This seam does NOT require authentication
- However, action buttons (Edit/Delete) should be hidden if user not authenticated
- Create button should be visible but redirect to login if clicked when not authenticated

## OpenAPI Contract

```yaml
paths:
  /api/catalog:
    get:
      summary: Get paginated catalog items
      tags:
        - Catalog
      parameters:
        - name: page_size
          in: query
          schema:
            type: integer
            default: 10
            minimum: 1
            maximum: 100
        - name: page_index
          in: query
          schema:
            type: integer
            default: 0
            minimum: 0
      responses:
        '200':
          description: Paginated catalog items
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/PaginatedCatalogResponse'
        '500':
          description: Server error
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'

components:
  schemas:
    CatalogItemResponse:
      type: object
      required:
        - id
        - name
        - price
        - picture_uri
        - catalog_brand
        - catalog_type
      properties:
        id:
          type: integer
        name:
          type: string
          maxLength: 50
        description:
          type: string
          nullable: true
        price:
          type: number
          format: decimal
        picture_uri:
          type: string
          format: uri
        catalog_brand:
          $ref: '#/components/schemas/CatalogBrandDto'
        catalog_type:
          $ref: '#/components/schemas/CatalogTypeDto'
        available_stock:
          type: integer
        restock_threshold:
          type: integer
        max_stock_threshold:
          type: integer

    CatalogBrandDto:
      type: object
      properties:
        id:
          type: integer
        brand:
          type: string

    CatalogTypeDto:
      type: object
      properties:
        id:
          type: integer
        type:
          type: string

    PaginatedCatalogResponse:
      type: object
      required:
        - items
        - page_index
        - page_size
        - total_items
        - total_pages
      properties:
        items:
          type: array
          items:
            $ref: '#/components/schemas/CatalogItemResponse'
        page_index:
          type: integer
        page_size:
          type: integer
        total_items:
          type: integer
        total_pages:
          type: integer
```

## Definition of Done

- [ ] OpenAPI contract written and committed
- [ ] Backend route handler implemented
- [ ] Backend service method implemented
- [ ] SQLAlchemy models created
- [ ] Pydantic schemas created
- [ ] Frontend page component created
- [ ] TanStack Query hook created
- [ ] Pagination component created
- [ ] Backend unit tests passing (100% coverage)
- [ ] Backend integration tests passing
- [ ] Frontend component tests passing
- [ ] E2E test passing
- [ ] Parity test passing (matches legacy golden baseline)
- [ ] Image URLs displaying correctly
- [ ] Responsive design verified on mobile/tablet/desktop
- [ ] Error states handled gracefully
- [ ] Loading states implemented
- [ ] Code review completed
- [ ] Evidence documented in `docs/seams/catalog-list/evidence/evidence.md`
