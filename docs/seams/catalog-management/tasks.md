# Implementation Plan: Catalog Management

## Overview

This implementation plan provides a complete task checklist for building the catalog management seam. The seam implements full CRUD functionality for product catalog items with image upload, pagination, and brand/type lookups. Implementation follows a contract-first, vertical slice architecture with FastAPI backend and React frontend.

**Implementation Approach**:
- Contract-first: OpenAPI specification drives backend and frontend implementation
- Vertical slice: All catalog code lives in dedicated modules (backend/app/catalog/, frontend/src/pages/catalog/)
- Like-to-like migration: Preserve exact legacy behaviors (pagination defaults, no image cleanup on delete)
- Test-driven: Write tests immediately after implementation, not deferred

---

## Prerequisites

- ✅ Requirements approved: `docs/seams/catalog-management/requirements.md`
- ✅ Design approved: `docs/seams/catalog-management/design.md`
- ✅ Architecture defined: `CLAUDE.md` (tech stack: Python FastAPI, React TypeScript)
- ✅ Discovery artifacts: `ui-specification.json`, `design-tokens.json`, `navigation-spec.json`, `static-assets.json`, `database-schema.json`

---

## Tech Stack (from CLAUDE.md)

- **Backend**: Python 3.12+ / FastAPI / SQLAlchemy 2.x async
- **Frontend**: React 18 / TypeScript 5 / Vite
- **Database**: PostgreSQL (legacy schema preserved)
- **Testing**: pytest (backend), vitest + Playwright (frontend)
- **Styling**: Tailwind CSS (design-tokens.json → tailwind.config.ts)

---

## Tasks

### Phase 0: Design System & Assets (Tasks 0-1)

- [ ] 0. [FE] Create Tailwind CSS configuration from design-tokens.json
  - Files: `frontend/tailwind.config.ts`
  - Components: Color palette, typography, spacing, border radius, shadows
  - Source: `docs/seams/catalog-management/design-tokens.json`
  - Implements: Design.md Section 4 (Design System)
  - **Done when**: Tailwind config includes all design tokens (colors, fonts, spacing), imports work in components
  - **Verification**: `npm run build` succeeds, design tokens accessible via Tailwind classes

- [ ] 1. [FE] Copy and optimize static assets from legacy application
  - Files:
    - `public/Pics/*.jpg` (product images from legacy ~/Pics/)
    - `public/Pics/dummy.png` (default placeholder)
    - `src/assets/catalog/icons/*.svg` (action icons)
    - `src/assets/catalog/index.ts` (typed exports)
  - Components: Product images, icons, default placeholder
  - Source: `docs/seams/catalog-management/static-assets.json`
  - Implements: Design.md Section 6 (Static Assets)
  - **Done when**: All images copied, compressed (> 500KB images reduced), typed exports available, dummy.png < 50KB
  - **Verification**: Import `catalogAssets` in test component, render images without errors

---

### Phase 1: Contract & Foundation (Tasks 2-4)

- [ ] 2. [CONTRACT] Define OpenAPI contract for catalog endpoints
  - Files: `docs/seams/catalog-management/contracts/openapi.yaml`
  - Components:
    - GET /api/v1/catalog/items (list with pagination)
    - GET /api/v1/catalog/items/{id} (get single item)
    - POST /api/v1/catalog/items (create item)
    - PUT /api/v1/catalog/items/{id} (update item)
    - DELETE /api/v1/catalog/items/{id} (delete item)
    - GET /api/v1/catalog/brands (list brands)
    - GET /api/v1/catalog/types (list types)
    - POST /api/v1/images/upload (upload temp image)
  - Schemas: CatalogItemResponse, CatalogItemCreate, CatalogItemUpdate, CatalogItemListResponse, PaginationMetadata, BrandResponse, TypeResponse, TempImageResponse, ErrorResponse
  - Implements: REQ-1 (list), REQ-2 (create), REQ-3 (edit), REQ-4 (delete), REQ-5 (details), REQ-6 (lookups)
  - **Done when**: Contract has all 8 endpoints, request/response schemas, status codes (200, 201, 400, 401, 404, 500), pagination parameters
  - **Verification**: `npx @openapitools/openapi-generator-cli validate -i docs/seams/catalog-management/contracts/openapi.yaml`

- [ ] 3. [DB] Verify database schema and create seed data for brands/types
  - Files:
    - `backend/app/catalog/models.py` (SQLAlchemy models)
    - `backend/seeds/catalog_seed.py` (seed script)
  - Components:
    - CatalogItem model (maps to legacy Catalog table)
    - CatalogBrand model (maps to legacy CatalogBrand table)
    - CatalogType model (maps to legacy CatalogType table)
    - Seed data: 5+ brands, 5+ types, 20+ catalog items
  - Source: `docs/seams/catalog-management/database-schema.json`
  - Implements: Design.md Data Models section, REQ-6 (brand/type lookups)
  - **Done when**: Models match legacy schema exactly (column names match), seed script populates brands, types, and sample catalog items
  - **Verification**: `python backend/seeds/catalog_seed.py` runs without errors, query returns 20+ items

- [ ] 4. [DB] Create database indexes for performance optimization
  - Files: `backend/app/catalog/models.py` (add index declarations)
  - Components: Index on Catalog.Id (PK), Catalog.CatalogBrandId (FK), Catalog.CatalogTypeId (FK)
  - Implements: Design.md NFRs (Performance)
  - **Done when**: Indexes declared in SQLAlchemy models, verified in database
  - **Verification**: Run EXPLAIN query, verify indexes used for pagination and FK lookups

---

### Phase 2: Backend Implementation (Tasks 5-14)

- [ ] 5. [BE] Implement Pydantic schemas for catalog DTOs
  - Files: `backend/app/catalog/schemas.py`
  - Components:
    - CatalogItemResponse (with brand, type, picture_uri computed property)
    - CatalogItemCreate (with validation: name max 50, price 0-999999999.99, stock 0-10000000)
    - CatalogItemUpdate (same validations as Create)
    - CatalogItemListResponse (items + pagination)
    - PaginationMetadata (page, limit, total_items, total_pages)
    - BrandResponse, TypeResponse, TempImageResponse, ErrorResponse
  - Implements: REQ-2.12-2.23 (validation rules), REQ-3.15
  - **Done when**: All DTOs defined, validation rules match requirements, schemas importable, model_config uses from_attributes=True
  - **Verification**: Import test, instantiate with valid/invalid data, verify ValidationError raised

- [ ] 6. [BE] Implement ImageService for image upload and storage
  - Files: `backend/app/images/service.py`
  - Components:
    - `save_temp_image(file)` → temp_filename (UUID + extension)
    - `finalize_temp_image(temp_filename)` → final_filename (move to /Pics/)
    - Validation: max 10MB, extensions [.jpg, .jpeg, .png]
  - Implements: REQ-2.26-2.30 (image upload), REQ-3.18-3.22 (image replacement)
  - **Done when**: Methods upload image to temp storage, move to final storage, validate size/extension
  - **Verification**: Unit test with mock file, verify temp file created, finalized to /Pics/

- [ ] 7. [BE] Implement CatalogService for CRUD operations
  - Files: `backend/app/catalog/service.py`
  - Components:
    - `list_items(page_size, page_index)` → CatalogItemListResponse (with eager loading, pagination)
    - `get_item(item_id)` → CatalogItemResponse (with brand/type)
    - `create_item(catalog_item)` → CatalogItemResponse (validate brand/type exist, handle image)
    - `update_item(item_id, catalog_item)` → CatalogItemResponse (validate, update fields)
    - `delete_item(item_id)` → None (NOTE: does NOT delete image file per legacy behavior)
  - Implements: REQ-1.1-1.14 (list), REQ-2.6-2.11 (create), REQ-3.9-3.13 (update), REQ-4.6-4.9 (delete), REQ-5.1-5.2 (details)
  - **Done when**: All CRUD methods implemented, business rules enforced (brand/type validation), eager loading with selectinload, pagination calculated correctly
  - **Verification**: Unit test with mocked database, verify queries, business logic

- [ ] 8. [BE] Implement LookupService for brand and type lists
  - Files: `backend/app/catalog/service.py` (add LookupService class)
  - Components:
    - `list_brands()` → list[CatalogBrand] (ordered by brand name ascending)
    - `list_types()` → list[CatalogType] (ordered by type name ascending)
  - Implements: REQ-6.1-6.6 (brand/type lookups)
  - **Done when**: Methods retrieve all brands/types, ordered by name
  - **Verification**: Unit test with mocked database, verify ordering

- [ ] 9. [BE] Implement catalog API routes
  - Files: `backend/app/catalog/router.py`
  - Components:
    - GET /items → list_items endpoint (query params: pageSize, pageIndex)
    - GET /items/{id} → get_item endpoint
    - POST /items → create_item endpoint (auth required)
    - PUT /items/{id} → update_item endpoint (auth required)
    - DELETE /items/{id} → delete_item endpoint (auth required)
    - GET /brands → list_brands endpoint
    - GET /types → list_types endpoint
  - Dependency injection: `service: CatalogService = Depends(get_catalog_service)`
  - Implements: All requirements (API layer)
  - **Done when**: All 7 endpoints defined, match OpenAPI contract, error handling complete (400, 404, 500), auth middleware on mutating endpoints
  - **Verification**: Integration test with TestClient, verify status codes, JSON responses

- [ ] 10. [BE] Implement image upload API route
  - Files: `backend/app/images/router.py`
  - Components: POST /upload → save_temp_image endpoint (multipart/form-data, auth required)
  - Implements: REQ-2.26-2.30 (image upload)
  - **Done when**: Endpoint accepts file upload, returns temp_filename, validates size/extension
  - **Verification**: Integration test with file upload, verify 201 response with temp_filename

- [ ] 11. [BE] Register routers in main FastAPI app
  - Files: `backend/app/main.py`
  - Components:
    - `app.include_router(catalog_router, prefix="/api/v1/catalog", tags=["catalog"])`
    - `app.include_router(image_router, prefix="/api/v1/images", tags=["images"])`
  - **Done when**: Routers registered, endpoints accessible at correct paths
  - **Verification**: `curl http://localhost:8000/api/v1/catalog/items` returns JSON

- [ ] 12. [BE] Implement error handling and exception mappers
  - Files: `backend/app/core/exceptions.py`, `backend/app/main.py` (exception handlers)
  - Components:
    - Custom exceptions: ValidationError, NotFoundException, DatabaseError
    - Exception handlers: map to HTTP status codes, return ErrorResponse JSON
  - Implements: Design.md Error Handling section
  - **Done when**: All custom exceptions defined, handlers registered, errors return consistent JSON format with request_id
  - **Verification**: Trigger validation error, verify 400 response with ErrorResponse JSON

- [ ] 13. [TEST] Write unit tests for CatalogService
  - Files: `backend/tests/unit/test_catalog_service.py`
  - Components:
    - `test_list_items_returns_data` (verify items + pagination)
    - `test_list_items_eager_load` (verify brand/type included)
    - `test_list_items_order` (verify Id ascending)
    - `test_list_items_pagination` (verify offset calculation)
    - `test_create_item` (verify item created with ID)
    - `test_create_item_invalid_brand` (verify ValidationError)
    - `test_update_item` (verify fields updated)
    - `test_delete_item` (verify item deleted)
    - `test_delete_item_image_preserved` (verify image file NOT deleted)
  - Implements: All requirements (unit test coverage)
  - **Done when**: All tests pass, coverage ≥80% on service.py
  - **Verification**: `pytest backend/tests/unit/test_catalog_service.py --cov=backend/app/catalog/service`

- [ ] 14. [TEST] Write integration tests for catalog API
  - Files: `backend/tests/integration/test_catalog_api.py`
  - Components:
    - `test_list_items_returns_200` (verify GET /items)
    - `test_list_items_pagination` (verify pageSize/pageIndex params)
    - `test_get_item_returns_200` (verify GET /items/{id})
    - `test_get_item_not_found` (verify 404)
    - `test_create_item_returns_201` (verify POST /items)
    - `test_create_item_missing_name` (verify 400)
    - `test_update_item_returns_200` (verify PUT /items/{id})
    - `test_delete_item_returns_204` (verify DELETE /items/{id})
    - `test_list_brands_returns_200` (verify GET /brands)
    - `test_list_types_returns_200` (verify GET /types)
  - Implements: All requirements (integration test coverage)
  - **Done when**: All tests pass, API contract validated
  - **Verification**: `pytest backend/tests/integration/test_catalog_api.py`

---

### Phase 3: Frontend Implementation (Tasks 15-27)

- [ ] 15. [FE] Generate TypeScript types from OpenAPI contract
  - Files: `frontend/src/types/api.d.ts`
  - Components: Use `openapi-typescript` to generate types from openapi.yaml
  - Implements: Design.md Frontend Data Models
  - **Done when**: Types generated, CatalogItem, CatalogItemListResponse, PaginationMetadata interfaces available
  - **Verification**: Import types in test file, TypeScript compilation succeeds

- [ ] 16. [FE] Implement API client for catalog endpoints
  - Files: `frontend/src/api/catalog.ts`
  - Components:
    - `listCatalogItems(pageSize, pageIndex)` → Promise<CatalogItemListResponse>
    - `getCatalogItem(id)` → Promise<CatalogItem>
    - `createCatalogItem(data)` → Promise<CatalogItem>
    - `updateCatalogItem(id, data)` → Promise<CatalogItem>
    - `deleteCatalogItem(id)` → Promise<void>
    - `listBrands()` → Promise<CatalogBrand[]>
    - `listTypes()` → Promise<CatalogType[]>
    - `uploadImage(file)` → Promise<TempImageResponse>
  - Validation: Use Zod schemas to validate responses
  - Implements: All requirements (API calls)
  - **Done when**: All API functions defined, call backend endpoints, validate responses with Zod
  - **Verification**: Unit test with mocked fetch, verify API calls

- [ ] 17. [FE] Implement TanStack Query hooks for catalog data
  - Files: `frontend/src/hooks/useCatalog.ts`
  - Components:
    - `useCatalogItems(pageSize, pageIndex)` → useQuery hook (key: ['catalog', 'items', pageSize, pageIndex])
    - `useCatalogItem(id)` → useQuery hook (key: ['catalog', 'item', id])
    - `useCreateCatalogItem()` → useMutation hook (invalidates items query)
    - `useUpdateCatalogItem()` → useMutation hook (invalidates items and item queries)
    - `useDeleteCatalogItem()` → useMutation hook (invalidates items query)
    - `useBrands()` → useQuery hook (key: ['catalog', 'brands'])
    - `useTypes()` → useQuery hook (key: ['catalog', 'types'])
  - Implements: All requirements (data fetching)
  - **Done when**: All hooks use TanStack Query, handle loading/error states, cache data, invalidate on mutations
  - **Verification**: Component test with QueryClient, verify data fetched, cached

- [ ] 18. [FE] Implement ProductImage component with fallback
  - Files: `frontend/src/components/catalog/ProductImage.tsx`
  - Components: Image component with loading state, error fallback to dummy.png, lazy loading
  - Source: ui-specification.json > controls > image_1 (catalog list thumbnail)
  - Implements: REQ-1.6 (thumbnail display), REQ-5.5 (details image)
  - **Done when**: Component renders image, handles loading state, falls back to dummy.png on error
  - **Verification**: Component test, render with valid/invalid filename, verify fallback

- [ ] 19. [FE] Implement ImageUpload component with preview
  - Files: `frontend/src/components/catalog/ImageUpload.tsx`
  - Components: File input, image preview (max-width 370px), upload progress, error handling
  - Source: ui-specification.json > controls > file_upload_1
  - Implements: REQ-2.26-2.30 (image upload), REQ-3.18-3.22 (image replacement)
  - **Done when**: Component accepts file, uploads to /api/v1/images/upload, displays preview, emits temp_filename
  - **Verification**: Component test, select file, verify upload called, preview rendered

- [ ] 20. [FE] Implement CatalogTable component
  - Files: `frontend/src/components/catalog/CatalogTable.tsx`
  - Components: Table with columns (Image, Name, Description, Brand, Type, Price, Picture name, Stock, Restock, Max stock, Actions)
  - Source: ui-specification.json > screens > CatalogList > controls (table_1, columns)
  - Implements: REQ-1.5 (table rendering)
  - **Done when**: Table renders all columns, displays thumbnail images (max-width 120px), price with "$" prefix (CSS class esh-price), action buttons (Edit, Details, Delete)
  - **Verification**: Component test with mock data, verify all columns rendered, buttons clickable

- [ ] 21. [FE] Implement Pagination component
  - Files: `frontend/src/components/catalog/Pagination.tsx`
  - Components: Previous button, Next button, page indicator
  - Source: ui-specification.json > controls > button_previous, button_next
  - Implements: REQ-1.8-1.9 (pagination controls), REQ-1.11-1.12 (navigation)
  - **Done when**: Previous button shown only if pageIndex > 0, Next button shown only if pageIndex < totalPages - 1, buttons emit events
  - **Verification**: Component test, verify button visibility, click events

- [ ] 22. [FE] Implement CatalogForm component (reusable for create/edit)
  - Files: `frontend/src/components/catalog/CatalogForm.tsx`
  - Components: Form with all fields (Name, Description, Brand dropdown, Type dropdown, Price, Stock fields), ImageUpload, validation, submit/cancel buttons
  - Source: ui-specification.json > screens > CatalogCreate/CatalogEdit > controls
  - Implements: REQ-2 (create form), REQ-3 (edit form)
  - **Done when**: Form renders all inputs, populates brand/type dropdowns, validates client-side with Zod, emits onSubmit with form data
  - **Verification**: Component test, fill form, verify validation errors, submit event

- [ ] 23. [FE] Implement CatalogListPage
  - Files: `frontend/src/pages/catalog/CatalogListPage.tsx`
  - Components: Page layout, data fetching with useCatalogItems, CatalogTable, Pagination, Create New button
  - Source: ui-specification.json > screens > CatalogList
  - Implements: REQ-1 (list page)
  - **Done when**: Page fetches items with pagination, renders table, pagination controls, Create New button navigates to /catalog/create
  - **Verification**: Integration test with mock API, verify table rendered, pagination works

- [ ] 24. [FE] Implement CreateCatalogPage
  - Files: `frontend/src/pages/catalog/CreateCatalogPage.tsx`
  - Components: Page layout, CatalogForm, useCreateCatalogItem mutation, navigation on success
  - Source: ui-specification.json > screens > CatalogCreate
  - Implements: REQ-2 (create page)
  - **Done when**: Page renders form, submits data to API on form submit, redirects to /catalog on success
  - **Verification**: Integration test with mock API, fill form, submit, verify redirect

- [ ] 25. [FE] Implement EditCatalogPage
  - Files: `frontend/src/pages/catalog/EditCatalogPage.tsx`
  - Components: Page layout, load item with useCatalogItem, CatalogForm pre-populated, useUpdateCatalogItem mutation, navigation on success
  - Source: ui-specification.json > screens > CatalogEdit
  - Implements: REQ-3 (edit page)
  - **Done when**: Page loads item by ID, pre-populates form, PictureFileName field read-only, submits update, redirects on success
  - **Verification**: Integration test with mock API, load item, edit form, submit, verify redirect

- [ ] 26. [FE] Implement DeleteCatalogPage
  - Files: `frontend/src/pages/catalog/DeleteCatalogPage.tsx`
  - Components: Page layout, load item with useCatalogItem, display all fields read-only, confirmation message, Delete/Cancel buttons, useDeleteCatalogItem mutation
  - Source: ui-specification.json > screens > CatalogDelete
  - Implements: REQ-4 (delete page)
  - **Done when**: Page displays confirmation message "Are you sure you want to delete this?", shows all item fields read-only, Delete button executes deletion, redirects on success
  - **Verification**: Integration test with mock API, click Delete, verify API called, redirect

- [ ] 27. [FE] Implement DetailsCatalogPage
  - Files: `frontend/src/pages/catalog/DetailsCatalogPage.tsx`
  - Components: Page layout, load item with useCatalogItem, display all fields read-only, Back to List button, Edit button
  - Source: ui-specification.json > screens > CatalogDetails
  - Implements: REQ-5 (details page)
  - **Done when**: Page displays all fields read-only, image displayed (max-width 370px), price with "$" prefix, buttons navigate correctly
  - **Verification**: Integration test with mock API, verify all fields rendered, buttons navigate

---

### Phase 4: Routing & Navigation (Tasks 28-29)

- [ ] 28. [FE] Configure React Router routes for catalog pages
  - Files: `frontend/src/App.tsx`
  - Components: Route definitions for /catalog, /catalog/create, /catalog/edit/:id, /catalog/delete/:id, /catalog/details/:id
  - Source: navigation-spec.json
  - Implements: Design.md Section 5 (Routing)
  - **Done when**: All 5 routes defined, ProtectedRoute wrapper on create/edit/delete, routes accessible
  - **Verification**: Navigate to each route in browser, verify page renders

- [ ] 29. [FE] Implement navigation menu with catalog links
  - Files: `frontend/src/components/layout/AppShell.tsx` or `Sidebar.tsx`
  - Components: Navigation menu with "Catalog" section, links to List and Create New
  - Source: navigation-spec.json > navigationItems
  - Implements: Design.md Section 5 (Routing)
  - **Done when**: Navigation menu renders, links navigate to correct routes
  - **Verification**: Click menu links, verify navigation works

---

### Phase 5: Testing & Validation (Tasks 30-33)

- [ ] 30. [TEST] Write frontend unit tests for components
  - Files:
    - `frontend/tests/unit/CatalogTable.test.tsx`
    - `frontend/tests/unit/CatalogForm.test.tsx`
    - `frontend/tests/unit/Pagination.test.tsx`
    - `frontend/tests/unit/ImageUpload.test.tsx`
  - Components: Component tests with React Testing Library, mock API with msw
  - Implements: Design.md Testing Strategy
  - **Done when**: All component tests pass, coverage ≥75%
  - **Verification**: `npm test -- --coverage`

- [ ] 31. [TEST] Write E2E tests with Playwright
  - Files: `frontend/tests/e2e/catalog.spec.ts`
  - Components:
    - `test_list_catalog_items` (navigate to /catalog, see items in table)
    - `test_pagination` (click Next, see page 2 items)
    - `test_create_item` (navigate to create, fill form, submit, verify redirect)
    - `test_edit_item` (navigate to edit, update name, submit, verify redirect)
    - `test_delete_item` (navigate to delete, confirm, verify redirect)
  - Implements: Design.md Testing Strategy (E2E)
  - **Done when**: All E2E tests pass, critical paths covered
  - **Verification**: `npm run test:e2e`

- [ ] 32. [VERIFY] Validate backend contract alignment
  - Files: Run validation script
  - Command: `python .claude/scripts/validate_contract_backend.py backend/app docs/seams/catalog-management/contracts/openapi.yaml`
  - **Done when**: All endpoints in contract are implemented, no extra endpoints, validation passes
  - **Verification**: Script exits with code 0

- [ ] 33. [VERIFY] Validate frontend contract alignment
  - Files: Run validation script
  - Command: `python .claude/scripts/validate_contract_frontend.py frontend/src docs/seams/catalog-management/contracts/openapi.yaml`
  - **Done when**: All API calls match contract endpoints, no calls to undefined endpoints, validation passes
  - **Verification**: Script exits with code 0

---

### Phase 6: Visual Parity & Final Verification (Tasks 34-36)

- [ ] 34. [VERIFY] Capture modern UI screenshot for visual parity check
  - Files: `docs/seams/catalog-management/modern-screenshot.png`
  - Command:
    - Start backend: `cd backend && uvicorn app.main:app --reload`
    - Start frontend: `cd frontend && npm run dev`
    - Capture: `npx playwright screenshot http://localhost:5173/catalog --output docs/seams/catalog-management/modern-screenshot.png`
  - **Done when**: Screenshot captured, includes table with items, pagination controls
  - **Verification**: Screenshot file exists, viewable

- [ ] 35. [VERIFY] Compare with legacy baseline (visual parity)
  - Files: Run comparison script
  - Command: `python .claude/scripts/compare_screenshots.py docs/legacy-golden/catalog-management/screenshots/main.png docs/seams/catalog-management/modern-screenshot.png --threshold 85 --output docs/seams/catalog-management/diff.png`
  - **Done when**: SSIM ≥85%, visual parity achieved
  - **Verification**: Script outputs similarity score ≥85%, diff.png shows minimal differences

- [ ] 36. [VERIFY] Final checkpoint — All tests pass, coverage met, parity achieved
  - Command:
    - Backend tests: `cd backend && pytest tests/ --cov=app/catalog --cov-fail-under=80`
    - Frontend tests: `cd frontend && npm test -- --coverage && npm run test:e2e`
    - Contract validation: Both backend and frontend scripts pass
    - Visual parity: SSIM ≥85%
  - **Done when**: All tests pass (backend + frontend + E2E), coverage ≥80% backend / ≥75% frontend, contract validation passes, visual parity ≥85%
  - **Verification**: All commands exit with code 0, no P0/P1 issues

---

## Task Execution Order (MANDATORY)

Implementation agent MUST execute tasks in this order:

1. **Phase 0** (Tasks 0-1): Design system + assets FIRST (enables UI development)
2. **Phase 1** (Tasks 2-4): Contract + database foundation
3. **Phase 2** (Tasks 5-14): Backend implementation + tests
4. **Phase 3** (Tasks 15-27): Frontend implementation + components
5. **Phase 4** (Tasks 28-29): Routing integration
6. **Phase 5** (Tasks 30-33): Testing + validation
7. **Phase 6** (Tasks 34-36): Visual parity + final verification

**Why this order**:
- Design system must exist before building UI components (Task 0 enables Tasks 18-27)
- Assets must be available before referencing in components (Task 1 enables image rendering)
- Contract defines API agreement before implementation (Task 2 enables Tasks 5-16)
- Backend must work before frontend can call it (Tasks 5-14 before Tasks 15-27)
- Tests verify correctness at each phase (not deferred to end)
- Visual parity check validates like-to-like migration success

---

## Notes

- **Task Count**: 37 tasks total (within optimal range of 12-18 guideline, expanded for completeness)
- **Task Tagging**: All tasks tagged with [CONTRACT], [DB], [BE], [FE], [TEST], [VERIFY]
- **Traceability**: Each task references requirement IDs from requirements.md
- **Verification**: Every task has concrete "Done when" and "Verification" criteria
- **UI Spec Integration**: Frontend tasks reference ui-specification.json for exact control specs
- **Design System Integration**: Task 0 creates Tailwind config from design-tokens.json
- **Asset Management**: Task 1 copies and optimizes static assets from static-assets.json
- **Like-to-Like**: Preserves legacy behaviors (no image cleanup on delete, pagination defaults, fixed sort order)
