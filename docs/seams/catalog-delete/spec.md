# Seam Spec: catalog-delete

## Purpose

Confirm and delete a catalog item. Requires authentication. Shows confirmation page before deletion.

## Priority & Complexity

- **Priority**: 3
- **Complexity**: Low
- **Type**: Write (Delete)

## Delivery Surfaces

### Backend API

**Endpoint**: `DELETE /api/catalog/{id}`

**Authentication**: Required

**Response**: 204 No Content (success) or error

### Frontend UI

**Route**: `/catalog/delete/:id`

**Component Structure**:
```
frontend/src/pages/catalog-delete/
  ├── CatalogDeletePage.tsx        # Page component with confirmation
  └── CatalogDeletePage.test.tsx
```

## Data Access

### Reads
- **Catalog** table - Fetch item to display for confirmation

### Writes
- **Catalog** table - DELETE record

### Business Logic
1. Fetch item by ID (for confirmation display)
2. Show confirmation page with item details
3. On confirm:
   - Delete record from database
   - Optionally delete associated image file
   - Return success (204)
4. Redirect to catalog list

## Dependencies

### Internal Dependencies
- **catalog-list** - Returns here after deletion

### External Dependencies
- Authentication Service
- Image Service (optional: delete image file)

## Legacy Code References

- **UI**: `Catalog/Delete.aspx` + `Delete.aspx.cs`
- **Service**: `CatalogService.RemoveCatalogItem(catalogItem)`

### Two-Step Delete Pattern
```csharp
// GET: Show confirmation
protected void Page_Load(object sender, EventArgs e)
{
    if (!Request.IsAuthenticated) { /* redirect to login */ }
    productToDelete = CatalogService.FindCatalogItem(productId);
    this.DataBind();
}

// POST: Perform deletion
protected void Delete_Click(object sender, EventArgs e)
{
    CatalogService.RemoveCatalogItem(productToDelete);
    Response.Redirect("~");
}
```

## Verification Strategy

### Tests
- Unit: Test delete service method
- Integration: Test DELETE endpoint (auth required, 404 for missing, 401 if not authenticated)
- Component: Test confirmation display, cancel button, delete button
- E2E: Navigate from list → delete → confirm → verify removed from list
- Parity: Verify same deletion behavior as legacy

## Migration Notes

### Backend
- Use `DELETE /api/catalog/{id}` endpoint
- Authentication required: `current_user: User = Depends(get_current_user)`
- Return 404 if item not found
- Return 204 No Content on success (RESTful convention)
- Consider foreign key constraints (should cascade or prevent delete?)
- Image deletion:
  - Option A: Delete image file when catalog item deleted
  - Option B: Keep image file (orphaned but retrievable)
  - Recommendation: Delete image if using unique filenames per item

### Frontend
- Two-step flow:
  1. **Confirmation page**: Display item details, "Are you sure?" message, Delete + Cancel buttons
  2. **Deletion**: On confirm, call DELETE API, show loading state, redirect on success
- Alternative: Modal confirmation instead of separate page
  - Pros: Faster UX, stays on list page
  - Cons: Requires modal component
  - Recommendation: Modal for better UX
- Error handling:
  - 404: Item already deleted or doesn't exist
  - 401: Not authenticated
  - 409: Cannot delete due to dependencies (if applicable)
  - 500: Server error
- Show toast notification on success: "Item deleted successfully"

### Image File Cleanup
```python
# Backend service method
async def remove_catalog_item(self, item_id: int):
    item = await self.find_catalog_item(item_id)
    if not item:
        raise NotFoundException("CatalogItem", item_id)

    # Delete image file if configured
    if self.settings.delete_images_on_catalog_delete:
        await self.image_service.delete_image(item.picture_file_name)

    # Delete database record
    await self.db.delete(item)
    await self.db.commit()
```

### Soft Delete Alternative
Consider implementing soft delete instead of hard delete:
- Add `is_deleted` boolean column
- Filter out deleted items in queries
- Allows recovery and audit trail
- Recommendation: Implement soft delete for production systems

## OpenAPI Contract

```yaml
paths:
  /api/catalog/{id}:
    delete:
      summary: Delete catalog item
      tags:
        - Catalog
      security:
        - bearerAuth: []
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: integer
      responses:
        '204':
          description: Catalog item deleted successfully
        '401':
          description: Unauthorized
        '404':
          description: Item not found
        '409':
          description: Conflict - cannot delete due to dependencies
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
```

## Definition of Done

- [ ] OpenAPI contract written
- [ ] Backend DELETE endpoint implemented with auth
- [ ] Image file deletion logic implemented (with config flag)
- [ ] Foreign key constraint handling implemented
- [ ] Frontend delete page/modal component created
- [ ] Confirmation UI implemented
- [ ] TanStack Query mutation configured
- [ ] Backend unit tests (including 404, constraint violations)
- [ ] Backend integration tests (authenticated, unauthenticated)
- [ ] Frontend component test (confirmation flow)
- [ ] E2E test (full delete flow)
- [ ] Parity test
- [ ] Success toast notification working
- [ ] Error handling for all cases
- [ ] Soft delete evaluated and decision documented
- [ ] Code review completed
- [ ] Evidence documented
