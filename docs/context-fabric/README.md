# Context Fabric - Discovery Results

This directory contains the complete discovery analysis of the eShop ASP.NET WebForms application.

## Discovery Artifacts

### Core Analysis Files

1. **[project-facts.json](./project-facts.json)**
   - Framework: ASP.NET WebForms 4.6+
   - Language: C#
   - Entry points: 5 ASPX pages
   - Dependencies: Entity Framework, Autofac, OWIN, Azure SDK
   - Architecture: 3-tier (UI → Service → Data)

2. **[manifest.json](./manifest.json)**
   - Solution structure
   - Module breakdown (9 modules)
   - Source file inventory (54 files)
   - Technology stack

3. **[database-schema.json](./database-schema.json)**
   - 3 tables: Catalog, CatalogBrand, CatalogType
   - 3 HiLo sequences for ID generation
   - Foreign key relationships
   - Column definitions and constraints

4. **[seam-proposals.json](./seam-proposals.json)**
   - 5 identified seams
   - Priority and complexity rankings
   - Suggested delivery order
   - Cross-cutting concerns analysis

5. **[discovery-summary.md](./discovery-summary.md)**
   - Comprehensive overview
   - Risk assessment
   - Migration strategy
   - Next steps

## Identified Seams

All seam specifications are in `../seams/{seam-name}/spec.md`:

### Seam 1: catalog-list (Priority 1, Complexity: Low)
- **Purpose**: Display paginated catalog items
- **Type**: Read-only
- **Auth**: Not required
- **Spec**: [../seams/catalog-list/spec.md](../seams/catalog-list/spec.md)

### Seam 2: catalog-details (Priority 3, Complexity: Low)
- **Purpose**: View single item details
- **Type**: Read-only
- **Auth**: Not required
- **Spec**: [../seams/catalog-details/spec.md](../seams/catalog-details/spec.md)

### Seam 3: catalog-create (Priority 2, Complexity: Medium)
- **Purpose**: Create new catalog items
- **Type**: Write (Create)
- **Auth**: Required
- **Spec**: [../seams/catalog-create/spec.md](../seams/catalog-create/spec.md)

### Seam 4: catalog-edit (Priority 2, Complexity: Medium)
- **Purpose**: Update existing catalog items
- **Type**: Write (Update)
- **Auth**: Required
- **Spec**: [../seams/catalog-edit/spec.md](../seams/catalog-edit/spec.md)

### Seam 5: catalog-delete (Priority 3, Complexity: Low)
- **Purpose**: Delete catalog items with confirmation
- **Type**: Write (Delete)
- **Auth**: Required
- **Spec**: [../seams/catalog-delete/spec.md](../seams/catalog-delete/spec.md)

## Recommended Delivery Order

1. **catalog-list** - Foundation, highest priority
2. **catalog-details** - Simplest read operation
3. **catalog-create** - First write operation, validates auth and image upload
4. **catalog-edit** - Builds on create patterns
5. **catalog-delete** - Completes CRUD operations

## Cross-Cutting Concerns

These patterns require special attention during migration:

1. **Authentication**: OpenID Connect → JWT/Session
2. **Image Storage**: Azure Blob Storage → Platform wrapper pattern
3. **ID Generation**: HiLo sequences → Auto-increment or ported logic
4. **Validation**: DataAnnotations → Pydantic + Zod
5. **Pagination**: Server-side OFFSET/FETCH (keep same pattern)
6. **Dependency Injection**: Autofac → FastAPI Depends()

See [discovery-summary.md](./discovery-summary.md) for detailed analysis of each concern.

## Migration Target

- **Backend**: Python 3.12+ with FastAPI (async)
- **Frontend**: React 18 with TypeScript, Vite, TanStack Query
- **Database**: SQL Server (initially, can migrate to PostgreSQL)
- **Auth**: JWT tokens or session-based
- **Storage**: Azure Blob Storage or local filesystem (via wrapper)

## Next Steps

1. Review all seam specs in `../seams/*/spec.md`
2. Set up backend and frontend project structure
3. Implement platform wrappers (auth, image storage)
4. Begin with catalog-list seam (highest priority)
5. Capture golden baseline for parity testing
6. Iterate through remaining seams in order

## Discovery Methodology

This discovery was performed using the seam-discovery phase approach:

- **Phase 0**: Safety checks and directory creation
- **Phase 1**: Located solution file and entry points
- **Phase 2**: Built manifest of all modules and files
- **Phase 2.5**: Extracted database schema from Entity Framework models
- **Phase 5**: Identified and analyzed seams
- **Phase 8**: Generated detailed specs for each seam

All analysis completed on: 2026-03-03

## Legacy Application Location

- **Solution**: `C:\Users\pratikp6\codebase\eShopModernizing\eShopModernizedWebFormsSolution\eShopModernizedWebForms.sln`
- **Main Project**: `src\eShopModernizedWebForms\`
- **Runtime URL**: http://localhost:50586

## Documentation Status

- [x] Project facts captured
- [x] Manifest created
- [x] Database schema documented
- [x] Seams identified and prioritized
- [x] Detailed specs written for all seams
- [x] Cross-cutting concerns analyzed
- [x] Risk assessment completed
- [ ] Golden baselines captured (next step)
- [ ] Implementation started (pending)

---

**For questions or clarifications, see [discovery-summary.md](./discovery-summary.md) or individual seam specs.**
