# Seam Spec: catalog-edit

## Purpose

Edit existing catalog items with pre-populated form, image replacement, and validation. Requires authentication.

## Priority & Complexity

- **Priority**: 2
- **Complexity**: Medium
- **Type**: Write (Update)

## Delivery Surfaces

### Backend API

**Endpoint**: `PUT /api/catalog/{id}`

**Authentication**: Required

**Request Schema**: Same as catalog-create (CatalogItemUpdate)

**Response Schema**: Updated CatalogItemResponse with all fields

### Frontend UI

**Route**: `/catalog/edit/:id`

**Component Structure**:
```
frontend/src/pages/catalog-edit/
  ├── CatalogEditPage.tsx          # Page component
  ├── CatalogEditPage.test.tsx
  └── components/
      └── (Reuses CatalogForm from catalog-create)
```

## Data Access

### Reads
- **Catalog** table - Fetch existing item by ID
- **CatalogBrand** table - For dropdown
- **CatalogType** table - For dropdown

### Writes
- **Catalog** table - UPDATE existing record

### Business Logic
1. Fetch existing item by ID (404 if not found)
2. Pre-populate form with current values
3. Validate changes (same rules as create)
4. If new image uploaded:
   - Delete old image (optional, based on config)
   - Move new image from temp to permanent
   - Update picture_file_name
5. Update record (Entity Framework Modified state → SQLAlchemy update)

## Dependencies

### Internal Dependencies
- **catalog-list** - Returns here after save

### External Dependencies
- Authentication Service
- Image Service (for upload/replace)

## Legacy Code References

- **UI**: `Catalog/Edit.aspx` + `Edit.aspx.cs`
- **Service**: `CatalogService.UpdateCatalogItem()`

### Key Differences from Create
```csharp
// Legacy Edit pattern
db.Entry(catalogItem).State = EntityState.Modified;
db.SaveChanges();

// Python equivalent
stmt = update(CatalogItem).where(CatalogItem.id == id).values(**item_dict)
await db.execute(stmt)
await db.commit()
```

## Verification Strategy

### Tests
- Unit: Test update logic, handle non-existent IDs
- Integration: Test PUT endpoint (authenticated, 404 for missing ID)
- Component: Test form pre-population, submission
- E2E: Navigate from list → edit → save → verify changes
- Parity: Compare update behavior with legacy

## Migration Notes

### Backend
- Use route parameter for ID: `@router.put("/api/catalog/{id}")`
- Return 404 if item not found
- Verify user owns item (if implementing ownership)
- Handle partial updates (PATCH) or require full object (PUT)

### Frontend
- Fetch item on mount with `useCatalogItem(id)` hook
- Show loading skeleton while fetching
- Pre-populate form fields once data loaded
- Disable form submission until data loaded
- Handle "item not found" gracefully (404 → redirect with error)
- Track form changes (show "unsaved changes" warning)

### Image Handling
- Display current image
- Allow replacement (upload new)
- Keep old image as backup or delete based on config
- Update `picture_file_name` only if new image uploaded

## OpenAPI Contract

```yaml
paths:
  /api/catalog/{id}:
    get:
      summary: Get catalog item by ID
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: integer
      responses:
        '200':
          description: Catalog item details
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/CatalogItemResponse'
        '404':
          description: Item not found

    put:
      summary: Update catalog item
      security:
        - bearerAuth: []
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: integer
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CatalogItemUpdate'
      responses:
        '200':
          description: Catalog item updated
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/CatalogItemResponse'
        '401':
          description: Unauthorized
        '404':
          description: Item not found
        '422':
          description: Validation error

components:
  schemas:
    CatalogItemUpdate:
      allOf:
        - $ref: '#/components/schemas/CatalogItemCreate'
        - type: object
          properties:
            picture_file_name:
              type: string
              description: Current picture filename (updated only if new image uploaded)
```

## Definition of Done

- [ ] OpenAPI contract written
- [ ] Backend GET /api/catalog/{id} endpoint implemented
- [ ] Backend PUT /api/catalog/{id} endpoint implemented with auth
- [ ] 404 handling for non-existent items
- [ ] Image replacement logic implemented
- [ ] Frontend edit page component created
- [ ] Form pre-population working
- [ ] TanStack Query fetch + mutation configured
- [ ] Backend unit tests (including 404 cases)
- [ ] Backend integration tests
- [ ] Frontend component tests (pre-population, submission)
- [ ] E2E test (full edit flow)
- [ ] Parity test
- [ ] Unsaved changes warning working
- [ ] Code review completed
- [ ] Evidence documented
