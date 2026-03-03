# Seam Spec: catalog-create

## Purpose

Create new catalog items with product details, image upload, and comprehensive validation. Requires authentication.

## Priority & Complexity

- **Priority**: 2
- **Complexity**: Medium
- **Type**: Write (Create)

## Delivery Surfaces

### Backend API

**Endpoint**: `POST /api/catalog`

**Authentication**: Required (JWT or session token)

**Request Schema**:
```json
{
  "name": "string",
  "description": "string",
  "catalog_brand_id": 1,
  "catalog_type_id": 1,
  "price": 19.99,
  "available_stock": 100,
  "restock_threshold": 10,
  "max_stock_threshold": 500,
  "picture_file_name": "product.png",
  "temp_image_name": "temp/uuid-image.png"
}
```

**Response Schema**:
```json
{
  "id": 123,
  "name": "string",
  "description": "string",
  "price": 19.99,
  "picture_uri": "https://storage.example.com/product.png",
  "catalog_brand_id": 1,
  "catalog_type_id": 1,
  "available_stock": 100,
  "restock_threshold": 10,
  "max_stock_threshold": 500
}
```

**Additional Endpoints**:
- `GET /api/catalog/brands` - Get all brands for dropdown
- `GET /api/catalog/types` - Get all types for dropdown
- `POST /api/catalog/upload-temp-image` - Upload temporary image, returns temp file name

### Frontend UI

**Route**: `/catalog/create`

**Component Structure**:
```
frontend/src/pages/catalog-create/
  ├── CatalogCreatePage.tsx        # Page component with form
  ├── CatalogCreatePage.test.tsx   # Component tests
  └── components/
      ├── CatalogForm.tsx           # Reusable form (shared with Edit)
      ├── ImageUpload.tsx           # Image upload component
      └── FormValidation.tsx        # Client-side validation
```

## Data Access

### Reads
- **CatalogBrand** table - All brands for dropdown
- **CatalogType** table - All types for dropdown

### Writes
- **Catalog** table - INSERT new record

### Business Logic
1. Generate new ID using HiLo sequence (or auto-increment if migrated)
2. Validate all input fields (Pydantic on backend, Zod on frontend)
3. If image uploaded:
   - Move from temp storage to permanent storage
   - Extract filename from temp path
   - Store filename in `picture_file_name`
4. Insert record with generated ID
5. Return created record with full details

## Dependencies

### Internal Dependencies
- **catalog-list** - Redirects here after successful creation

### External Dependencies
1. **Authentication Service** - Verify user is authenticated
   - Legacy: OpenID Connect via OWIN middleware
   - Python: JWT verification via FastAPI dependency

2. **Image Service** - Handle image upload and storage
   - Legacy: `IImageService.UpdateImage(catalogItem)`
   - Python: `ImageWrapper.update_image(catalog_item)`
   - Supports Azure Blob Storage or local filesystem

3. **ID Generator** - Generate unique IDs
   - Legacy: `CatalogItemHiLoGenerator.GetNextSequenceValue(db)`
   - Python: Either keep HiLo pattern or switch to auto-increment

## Legacy Code References

### ASP.NET WebForms
- **UI**: `Catalog/Create.aspx` + `Catalog/Create.aspx.cs`
- **Service**: `Services/CatalogService.cs::CreateCatalogItem()`
- **ID Gen**: `Models/CatalogItemHiLoGenerator.cs`
- **Image**: `Services/ImageAzureStorage.cs` or `ImageMockStorage.cs`

### Key Legacy Patterns

1. **Form Submission**:
```csharp
protected void Create_Click(object sender, EventArgs e)
{
    if (this.ModelState.IsValid)
    {
        var catalogItem = new CatalogItem { /* map form fields */ };
        CatalogService.CreateCatalogItem(catalogItem);
        Response.Redirect("~");
    }
}
```

2. **Image Upload Flow**:
```csharp
if (!string.IsNullOrEmpty(catalogItem.TempImageName))
{
    var fileName = Path.GetFileName(catalogItem.TempImageName);
    catalogItem.PictureFileName = fileName;
    ImageService.UpdateImage(catalogItem);
}
```

3. **Authentication Check**:
```csharp
if (!Request.IsAuthenticated)
{
    Context.GetOwinContext().Authentication.Challenge(
        new AuthenticationProperties { RedirectUri = "/" },
        OpenIdConnectAuthenticationDefaults.AuthenticationType
    );
}
```

4. **Dropdown Population**:
```csharp
public IEnumerable<CatalogBrand> GetBrands()
{
    return CatalogService.GetCatalogBrands();
}
```

## Verification Strategy

### Unit Tests (Backend)

```python
# backend/tests/unit/test_catalog_service.py

async def test_create_catalog_item():
    # Test successful creation
    # Verify ID generation
    # Test validation failures
    # Test image handling

async def test_create_without_image():
    # Verify default picture used
```

### Integration Tests (Backend)

```python
# backend/tests/integration/test_catalog_create_api.py

async def test_create_catalog_item_authenticated():
    response = await authenticated_client.post("/api/catalog", json={...})
    assert response.status_code == 201
    assert response.json()["id"] > 0

async def test_create_catalog_item_unauthenticated():
    response = await client.post("/api/catalog", json={...})
    assert response.status_code == 401

async def test_create_with_invalid_data():
    response = await authenticated_client.post("/api/catalog", json={
        "name": "",  # Invalid: empty name
        "price": -10  # Invalid: negative price
    })
    assert response.status_code == 422
    assert "validation" in response.json()["detail"].lower()
```

### Component Tests (Frontend)

```typescript
// frontend/src/pages/catalog-create/CatalogCreatePage.test.tsx

test('renders create form', () => {
  render(<CatalogCreatePage />);
  expect(screen.getByLabelText(/name/i)).toBeInTheDocument();
  expect(screen.getByLabelText(/price/i)).toBeInTheDocument();
});

test('validates required fields', async () => {
  render(<CatalogCreatePage />);
  fireEvent.click(screen.getByText(/create/i));
  await waitFor(() => {
    expect(screen.getByText(/name is required/i)).toBeInTheDocument();
  });
});

test('submits form successfully', async () => {
  const mockCreate = jest.fn().mockResolvedValue({ id: 123 });
  render(<CatalogCreatePage createFn={mockCreate} />);

  fireEvent.change(screen.getByLabelText(/name/i), {
    target: { value: 'Test Product' }
  });
  fireEvent.change(screen.getByLabelText(/price/i), {
    target: { value: '19.99' }
  });
  // ... fill other fields

  fireEvent.click(screen.getByText(/create/i));

  await waitFor(() => {
    expect(mockCreate).toHaveBeenCalled();
  });
});
```

### E2E Tests (Playwright)

```typescript
// frontend/tests/e2e/catalog-create.spec.ts

test('create new catalog item', async ({ page }) => {
  await page.goto('/catalog/create');

  // Fill form
  await page.fill('[name="name"]', 'New Product');
  await page.fill('[name="description"]', 'Description');
  await page.selectOption('[name="brand"]', '1');
  await page.selectOption('[name="type"]', '1');
  await page.fill('[name="price"]', '29.99');
  await page.fill('[name="stock"]', '100');
  await page.fill('[name="restock"]', '10');
  await page.fill('[name="maxstock"]', '500');

  // Submit
  await page.click('button:has-text("Create")');

  // Verify redirect to list
  await expect(page).toHaveURL('/catalog');

  // Verify new item appears
  await expect(page.locator('text=New Product')).toBeVisible();
});

test('validates price format', async ({ page }) => {
  await page.goto('/catalog/create');
  await page.fill('[name="price"]', 'invalid');
  await page.blur('[name="price"]');
  await expect(page.locator('text=/price.*number/i')).toBeVisible();
});
```

### Parity Tests

```python
# backend/tests/parity/test_catalog_create_parity.py

async def test_create_matches_legacy_id_generation():
    # Compare ID generation pattern
    # Verify HiLo sequence behavior matches

async def test_create_validates_like_legacy():
    # Test same validation rules
    # Verify error messages match
```

## Migration Notes

### Backend Considerations

1. **ID Generation**:
   - Legacy uses HiLo pattern: `CatalogItemHiLoGenerator`
   - Options:
     - A) Port HiLo logic to Python (complex but maintains compatibility)
     - B) Switch to auto-increment (simpler but requires DB schema change)
   - Recommendation: Auto-increment for new system, document migration path

2. **Image Upload**:
   - Create platform wrapper: `ImageWrapper` (abstract base)
   - Mock implementation for local dev: `MockImage`
   - Real implementation: `AzureImage` (uses Azure SDK)
   - Configuration flag: `USE_AZURE_STORAGE` in settings

3. **Validation**:
   - Pydantic model with validators:
   ```python
   class CatalogItemCreate(BaseModel):
       name: str = Field(..., min_length=1, max_length=50)
       price: Decimal = Field(..., gt=0, decimal_places=2)
       available_stock: int = Field(..., ge=0, le=10000000)
       # ...
   ```

4. **Authentication**:
   - FastAPI dependency: `current_user: User = Depends(get_current_user)`
   - Raises HTTP 401 if not authenticated
   - Replace OpenID Connect with JWT or session-based auth

### Frontend Considerations

1. **Form Management**:
   - Use React Hook Form + Zod validation
   - Client-side validation mirrors backend Pydantic rules
   - Show inline validation errors

2. **Image Upload**:
   - Two-step process:
     1. Upload to temp endpoint, get temp filename
     2. Submit form with temp filename
     3. Backend moves from temp to permanent storage
   - Show image preview after upload
   - Handle upload errors gracefully

3. **Dropdowns**:
   - Fetch brands/types on mount with TanStack Query
   - Cache for 5 minutes (rarely change)
   - Show loading state while fetching

4. **Navigation**:
   - On success: Navigate to `/catalog` with success toast
   - On cancel: Navigate back to `/catalog`
   - Prevent accidental navigation away if form is dirty

5. **Default Values**:
   - Picture: Use default placeholder (`dummy.png`) if no upload
   - Stock fields: Default to 0 or sensible defaults

### Authentication Migration

Legacy OpenID Connect pattern:
```csharp
if (!Request.IsAuthenticated)
{
    Context.GetOwinContext().Authentication.Challenge(...);
}
```

Python equivalent:
```python
from fastapi import Depends, HTTPException
from app.dependencies import get_current_user

@router.post("/api/catalog")
async def create_catalog_item(
    item: CatalogItemCreate,
    current_user: User = Depends(get_current_user),
    service: CatalogService = Depends(get_catalog_service),
):
    # user is authenticated if this executes
    ...
```

Frontend equivalent:
```typescript
// Protected route wrapper
function RequireAuth({ children }) {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) return <LoadingSpinner />;
  if (!isAuthenticated) return <Navigate to="/login" />;

  return children;
}
```

## OpenAPI Contract

```yaml
paths:
  /api/catalog:
    post:
      summary: Create new catalog item
      tags:
        - Catalog
      security:
        - bearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CatalogItemCreate'
      responses:
        '201':
          description: Catalog item created
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/CatalogItemResponse'
        '401':
          description: Unauthorized
        '422':
          description: Validation error
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ValidationError'

  /api/catalog/brands:
    get:
      summary: Get all catalog brands
      tags:
        - Catalog
      responses:
        '200':
          description: List of brands
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/CatalogBrandDto'

  /api/catalog/types:
    get:
      summary: Get all catalog types
      tags:
        - Catalog
      responses:
        '200':
          description: List of types
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/CatalogTypeDto'

  /api/catalog/upload-temp-image:
    post:
      summary: Upload temporary image
      tags:
        - Catalog
      security:
        - bearerAuth: []
      requestBody:
        required: true
        content:
          multipart/form-data:
            schema:
              type: object
              properties:
                file:
                  type: string
                  format: binary
      responses:
        '200':
          description: Temporary file uploaded
          content:
            application/json:
              schema:
                type: object
                properties:
                  temp_file_name:
                    type: string

components:
  schemas:
    CatalogItemCreate:
      type: object
      required:
        - name
        - catalog_brand_id
        - catalog_type_id
        - price
        - available_stock
        - restock_threshold
        - max_stock_threshold
      properties:
        name:
          type: string
          minLength: 1
          maxLength: 50
        description:
          type: string
        catalog_brand_id:
          type: integer
        catalog_type_id:
          type: integer
        price:
          type: number
          format: decimal
          minimum: 0
          maximum: 9999999999999999.99
        available_stock:
          type: integer
          minimum: 0
          maximum: 10000000
        restock_threshold:
          type: integer
          minimum: 0
          maximum: 10000000
        max_stock_threshold:
          type: integer
          minimum: 0
          maximum: 10000000
        picture_file_name:
          type: string
        temp_image_name:
          type: string

    ValidationError:
      type: object
      properties:
        detail:
          type: array
          items:
            type: object
            properties:
              loc:
                type: array
                items:
                  type: string
              msg:
                type: string
              type:
                type: string
```

## Definition of Done

- [ ] OpenAPI contract written
- [ ] Backend create endpoint implemented with authentication
- [ ] Backend brands/types endpoints implemented
- [ ] Image upload endpoint implemented
- [ ] Image wrapper (abstract + mock) implemented
- [ ] Pydantic validation schemas created
- [ ] Frontend create page component created
- [ ] Form with Zod validation implemented
- [ ] Image upload component created
- [ ] TanStack Query mutations configured
- [ ] Backend unit tests passing
- [ ] Backend integration tests passing (authenticated + unauthenticated cases)
- [ ] Frontend component tests passing
- [ ] E2E test passing
- [ ] Parity test passing
- [ ] Error handling tested (validation errors, auth errors, server errors)
- [ ] Default image placeholder working
- [ ] Form dirty state tracking working
- [ ] Success toast/notification working
- [ ] Code review completed
- [ ] Evidence documented
