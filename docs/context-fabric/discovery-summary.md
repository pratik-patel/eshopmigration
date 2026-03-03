# Discovery Summary: eShop Catalog Migration

## Project Overview

**Legacy Application**: ASP.NET WebForms catalog management system
**Target Architecture**: Python/FastAPI backend + React/TypeScript frontend
**Runtime URL**: http://localhost:50586
**Workspace**: `C:\Users\pratikp6\codebase\eShopModernizing\eShopModernizedWebFormsSolution`

## Key Findings

### Application Architecture

The eShop WebForms application follows a traditional 3-tier architecture:
- **Presentation**: ASP.NET WebForms (*.aspx) with server-side controls
- **Business Logic**: Service layer (`ICatalogService`, `IImageService`)
- **Data Access**: Entity Framework 6 with `CatalogDBContext`

### Domain Model

The application manages a product catalog with three core entities:

1. **CatalogItem** (table: `Catalog`)
   - Products with name, description, price, stock levels
   - Links to Brand and Type via foreign keys
   - Image stored as filename reference (Azure or local)

2. **CatalogBrand** (table: `CatalogBrand`)
   - Lookup table for product brands (e.g., "Nike", "Adidas")

3. **CatalogType** (table: `CatalogType`)
   - Lookup table for product categories (e.g., "Shoes", "T-Shirts")

### Technology Stack

**Legacy**:
- ASP.NET WebForms 4.6+
- Entity Framework 6
- Autofac (DI)
- OWIN / OpenID Connect (Auth)
- Azure Storage SDK (optional)
- log4net
- SQL Server

**Target**:
- Python 3.12+ / FastAPI (async)
- SQLAlchemy 2.x async
- FastAPI Depends() (DI)
- JWT or session auth
- Azure SDK / local filesystem (via wrapper)
- structlog
- SQL Server (initially) or PostgreSQL

## Identified Seams

### Seam Delivery Order

Based on priority, complexity, and dependencies:

1. **catalog-list** (Priority 1, Complexity: Low)
   - Main landing page
   - Paginated product display
   - Foundation for all other seams

2. **catalog-details** (Priority 3, Complexity: Low)
   - Read-only item details
   - No authentication required
   - Reuses GET endpoint from edit

3. **catalog-create** (Priority 2, Complexity: Medium)
   - Create new products
   - Image upload
   - Requires authentication

4. **catalog-edit** (Priority 2, Complexity: Medium)
   - Update existing products
   - Image replacement
   - Requires authentication

5. **catalog-delete** (Priority 3, Complexity: Low)
   - Delete confirmation
   - Cleanup logic
   - Requires authentication

### Seam Breakdown Summary

| Seam | Type | Auth Required | Tables Read | Tables Written | Complexity |
|------|------|---------------|-------------|----------------|------------|
| catalog-list | Read | No | Catalog, CatalogBrand, CatalogType | None | Low |
| catalog-details | Read | No | Catalog, CatalogBrand, CatalogType | None | Low |
| catalog-create | Write | Yes | CatalogBrand, CatalogType | Catalog | Medium |
| catalog-edit | Write | Yes | Catalog, CatalogBrand, CatalogType | Catalog | Medium |
| catalog-delete | Write | Yes | Catalog, CatalogBrand, CatalogType | Catalog | Low |

## Cross-Cutting Concerns

These patterns require special attention during migration:

### 1. Authentication

**Legacy**: OpenID Connect via OWIN middleware
```csharp
if (!Request.IsAuthenticated)
{
    Context.GetOwinContext().Authentication.Challenge(...);
}
```

**Target**: JWT tokens or session-based auth via FastAPI dependencies
```python
@router.post("/api/catalog")
async def create_item(
    current_user: User = Depends(get_current_user)
):
    ...
```

**Migration Path**:
- Phase 1: Implement mock auth (always authenticated) for development
- Phase 2: Implement JWT verification matching legacy identity provider
- Phase 3: Optionally migrate to new auth system

### 2. Image Storage

**Legacy**: `IImageService` with two implementations:
- `ImageAzureStorage` - Azure Blob Storage
- `ImageMockStorage` - Local filesystem

**Target**: Platform wrapper pattern (per CLAUDE.md rules)
```python
# backend/app/adapters/image_wrapper.py
class ImageWrapper(ABC):
    @abstractmethod
    async def build_image_url(self, catalog_item) -> str: ...
    @abstractmethod
    async def update_image(self, catalog_item) -> None: ...
    @abstractmethod
    async def delete_image(self, filename: str) -> None: ...

# Mock implementation for dev
class MockImage(ImageWrapper): ...

# Real implementation
class AzureImage(ImageWrapper): ...
```

**Configuration**: `USE_AZURE_STORAGE` flag in settings

### 3. ID Generation

**Legacy**: HiLo sequence pattern via `CatalogItemHiLoGenerator`
- Pre-allocates blocks of IDs from database sequences
- Complex but allows high-concurrency inserts

**Target Options**:
- **Option A**: Port HiLo logic to Python (maintains compatibility, complex)
- **Option B**: Switch to database auto-increment (simple, requires schema change)
- **Option C**: Use UUIDs (avoids coordination, larger IDs)

**Recommendation**: Auto-increment for new system, document ID mapping if migrating data

### 4. Validation

**Legacy**: DataAnnotations attributes on model classes
```csharp
[Range(0, 10000000)]
[Display(Name = "Stock")]
public int AvailableStock { get; set; }
```

**Target**:
- **Backend**: Pydantic models with Field validators
- **Frontend**: Zod schemas mirroring Pydantic rules

```python
class CatalogItemCreate(BaseModel):
    available_stock: int = Field(..., ge=0, le=10000000)
```

```typescript
const CatalogItemSchema = z.object({
  available_stock: z.number().int().min(0).max(10000000),
});
```

### 5. Pagination

**Legacy**: Server-side with OFFSET/FETCH
```csharp
db.CatalogItems
    .OrderBy(c => c.Id)
    .Skip(pageSize * pageIndex)
    .Take(pageSize)
    .ToList();
```

**Target**: Same server-side pattern, but with TanStack Query on frontend for caching
```python
query = (
    select(CatalogItem)
    .order_by(CatalogItem.id)
    .offset(page_size * page_index)
    .limit(page_size)
)
```

### 6. Dependency Injection

**Legacy**: Autofac container registered in `Global.asax`
```csharp
builder.RegisterType<CatalogService>().As<ICatalogService>();
```

**Target**: FastAPI `Depends()` pattern
```python
@lru_cache
def get_catalog_service(
    db: AsyncSession = Depends(get_db),
) -> CatalogService:
    return CatalogService(db)
```

## Data Migration Considerations

### Schema Compatibility

The current schema is straightforward and maps cleanly to SQLAlchemy:

```
Catalog (Table)
├── Id (PK, HiLo generated)
├── Name (nvarchar(50), required)
├── Description (nvarchar(max))
├── Price (decimal(18,2), required)
├── PictureFileName (nvarchar(max), required)
├── CatalogTypeId (FK → CatalogType.Id)
├── CatalogBrandId (FK → CatalogBrand.Id)
├── AvailableStock (int, required)
├── RestockThreshold (int, required)
├── MaxStockThreshold (int, required)
└── OnReorder (bit, required)
```

**No schema changes required** for initial migration. Can run new Python backend against existing database.

### Data Seeding

Legacy uses `CatalogDBInitializer` and `PreconfiguredData` to seed sample data.

For Python, create similar seeding script:
- `backend/app/core/seed_data.py`
- Run on first startup or via management command

### Foreign Key Constraints

Current relationships:
- `Catalog.CatalogBrandId` → `CatalogBrand.Id` (many-to-one)
- `Catalog.CatalogTypeId` → `CatalogType.Id` (many-to-one)

**No cascading deletes configured** - must handle manually when deleting brands/types.

## Testing Strategy

### Parity Testing

For each seam, capture "golden baseline" from legacy system:

1. **Capture Phase**:
   - Run legacy app
   - Exercise each workflow
   - Capture HTTP responses, database state, screenshots
   - Store in `docs/seams/{seam-name}/evidence/`

2. **Verification Phase**:
   - Run new Python/React app
   - Execute same workflows
   - Compare responses field-by-field
   - Flag any deviations

3. **Acceptance Criteria**:
   - All fields present in response
   - Data types match
   - Validation rules behave identically
   - UI displays same information (screenshot comparison)

### Test Coverage Targets

- **Backend**:
  - Unit tests: 100% of service methods
  - Integration tests: All API endpoints (happy path + error cases)
  - Parity tests: All seams

- **Frontend**:
  - Component tests: All pages and reusable components
  - E2E tests: Happy path for each seam
  - Visual regression: Key pages

## Risk Assessment

### High-Risk Areas

1. **Authentication Migration**
   - Risk: Users unable to log in after migration
   - Mitigation: Parallel run with legacy auth, gradual rollout

2. **Image Storage Migration**
   - Risk: Images not accessible or URLs broken
   - Mitigation: Test with mock storage first, verify Azure connection, maintain URL structure

3. **ID Generation**
   - Risk: ID collisions if HiLo not properly migrated
   - Mitigation: Switch to auto-increment or audit HiLo port carefully

### Medium-Risk Areas

4. **Performance Regression**
   - Risk: Slower pagination or image loading
   - Mitigation: Add database indexes, benchmark against legacy

5. **Validation Drift**
   - Risk: Backend/frontend validation out of sync
   - Mitigation: Generate Zod schemas from Pydantic models, shared validation tests

### Low-Risk Areas

6. **Read-Only Seams** (catalog-list, catalog-details)
   - Simple queries, no state changes
   - Easy to verify with parity tests

## Next Steps

1. **Phase 0: Infrastructure Setup**
   - Set up Python/FastAPI project structure
   - Set up React/Vite project structure
   - Configure development database
   - Implement mock authentication and image storage wrappers

2. **Phase 1: catalog-list Seam**
   - Highest priority, foundational
   - Implement backend pagination endpoint
   - Implement frontend list page
   - Capture golden baseline and verify parity

3. **Phase 2: catalog-details Seam**
   - Lowest complexity
   - Reuses backend endpoint
   - Validates UI component patterns

4. **Phase 3: catalog-create Seam**
   - First write operation
   - Validates authentication integration
   - Tests image upload flow

5. **Phase 4: catalog-edit Seam**
   - Similar to create, adds update logic
   - Tests form pre-population

6. **Phase 5: catalog-delete Seam**
   - Validates deletion workflow
   - Completes CRUD operations

7. **Phase 6: Integration & Deployment**
   - End-to-end testing
   - Performance benchmarking
   - Security review
   - Deployment to staging
   - Parallel run with legacy
   - Production cutover

## File Artifacts

All discovery artifacts have been written to:

- `docs/context-fabric/project-facts.json` - Framework, entry points, architecture
- `docs/context-fabric/manifest.json` - Solution structure, modules, file inventory
- `docs/context-fabric/database-schema.json` - Tables, columns, relationships, sequences
- `docs/context-fabric/seam-proposals.json` - Seam analysis, priority, complexity
- `docs/seams/catalog-list/spec.md` - Detailed specification for catalog-list seam
- `docs/seams/catalog-create/spec.md` - Detailed specification for catalog-create seam
- `docs/seams/catalog-edit/spec.md` - Detailed specification for catalog-edit seam
- `docs/seams/catalog-details/spec.md` - Detailed specification for catalog-details seam
- `docs/seams/catalog-delete/spec.md` - Detailed specification for catalog-delete seam

## Conclusion

The eShop catalog application is a well-structured, straightforward CRUD application ideal for seam-based migration. The five identified seams can be migrated incrementally with low risk. The main challenges are:

1. Authentication system transition
2. Image storage abstraction
3. ID generation strategy

All three have clear mitigation paths via platform wrappers and phased rollout.

**Estimated Effort**: 2-3 weeks for full migration (1 developer, including testing)

**Recommended Start Date**: Immediate - all discovery complete, specs ready for implementation.
