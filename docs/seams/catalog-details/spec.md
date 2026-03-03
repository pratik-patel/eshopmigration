# Seam Spec: catalog-details

## Purpose

View detailed read-only information for a single catalog item. Does not require authentication.

## Priority & Complexity

- **Priority**: 3
- **Complexity**: Low
- **Type**: Read-only

## Delivery Surfaces

### Backend API

**Endpoint**: `GET /api/catalog/{id}`

**Authentication**: Not required

**Response Schema**: CatalogItemResponse with all fields including related brand and type

### Frontend UI

**Route**: `/catalog/details/:id`

**Component Structure**:
```
frontend/src/pages/catalog-details/
  ├── CatalogDetailsPage.tsx       # Page component
  ├── CatalogDetailsPage.test.tsx
  └── components/
      └── CatalogDetailCard.tsx     # Display component
```

## Data Access

### Reads
- **Catalog** table - Single item by ID
- **CatalogBrand** table - Via JOIN
- **CatalogType** table - Via JOIN

### Writes
- None

## Dependencies

### Internal Dependencies
- **catalog-list** - Navigates from list
- **catalog-edit** - Optional "Edit" link if authenticated

### External Dependencies
- Image Service (for displaying image URL)

## Legacy Code References

- **UI**: `Catalog/Details.aspx` + `Details.aspx.cs`
- **Service**: `CatalogService.FindCatalogItem(id)`

### Simple Read Pattern
```csharp
protected void Page_Load(object sender, EventArgs e)
{
    var productId = Convert.ToInt32(Page.RouteData.Values["id"]);
    product = CatalogService.FindCatalogItem(productId);
    this.DataBind();
}
```

## Verification Strategy

### Tests
- Unit: Test service find method
- Integration: Test GET endpoint, verify 404 for missing ID
- Component: Test details rendering, image display
- E2E: Navigate from list → details → verify all fields displayed
- Parity: Compare response structure with legacy

## Migration Notes

### Backend
- Reuse same endpoint as catalog-edit GET: `GET /api/catalog/{id}`
- Include all related entities (brand, type) in response
- Return 404 if item not found
- No authentication required

### Frontend
- Simple display component (read-only form or card layout)
- Show large product image
- Display all fields with labels
- Action buttons:
  - "Back to List"
  - "Edit" (if authenticated)
  - "Delete" (if authenticated)
- Handle 404 gracefully (show error message, link back to list)
- Use same TanStack Query hook as edit page: `useCatalogItem(id)`

### UI Layout Options
- Option A: Card layout with image on left, details on right
- Option B: Image on top, details below in labeled sections
- Recommendation: Card layout for desktop, stack on mobile

## OpenAPI Contract

Reuses `GET /api/catalog/{id}` from catalog-edit spec.

## Definition of Done

- [ ] Backend GET endpoint exists (shared with edit)
- [ ] Frontend details page component created
- [ ] Details card component created
- [ ] Image display working
- [ ] All fields displayed with proper labels
- [ ] Action buttons (Back, Edit, Delete) working
- [ ] Authentication-based button visibility working
- [ ] Backend unit test
- [ ] Backend integration test (including 404)
- [ ] Frontend component test
- [ ] E2E test
- [ ] Parity test
- [ ] 404 handling working
- [ ] Responsive layout working
- [ ] Code review completed
- [ ] Evidence documented
