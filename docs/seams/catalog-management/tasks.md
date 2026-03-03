# Implementation Plan: Catalog Management

## Overview

This implementation plan breaks down the catalog management seam migration into granular, executable tasks. The tasks follow the design specified in `design.md` and implement all requirements from `requirements.md`. Tasks are organized by implementation layer (scaffolding, backend, frontend, testing) and sequenced by dependencies.

**Implementation Approach**: Contract-first development with vertical slices. Each slice implements a complete user workflow (backend + frontend + tests).

**Estimated Duration**: 10 days (2 weeks with buffer)

---

## Prerequisites

- ✅ Requirements approved: `docs/seams/catalog-management/requirements.md`
- ✅ Design approved: `docs/seams/catalog-management/design.md`
- ✅ Architecture defined: `CLAUDE.md`
- ✅ Python backend rules: `.claude/rules/python-backend.md`
- ✅ React frontend rules: `.claude/rules/react-frontend.md`

---

## Tech Stack (from CLAUDE.md)

- **Backend**: Python 3.12+ / FastAPI / SQLAlchemy 2.x async / Pydantic v2
- **Frontend**: React 18 / TypeScript 5 / Vite / TanStack Query / shadcn/ui
- **Database**: PostgreSQL 13+ (production) / SQLite (development)
- **Storage**: MinIO (S3-compatible) or local filesystem adapter
- **Testing**: pytest + pytest-asyncio (backend), vitest + Playwright (frontend)

---

## Tasks

### Scaffolding (First Seam - Setup Project Structure)

- [ ] 1. [FIRST SEAM ONLY] Create backend project structure
  - Create `backend/app/main.py` (FastAPI app factory with CORS, middleware, router registration)
  - Create `backend/app/config.py` (pydantic-settings for env vars: DATABASE_URL, JWT_SECRET, IMAGE_STORAGE_PATH)
  - Create `backend/app/dependencies.py` (DI functions: get_db, get_current_user, get_image_service)
  - Create `backend/app/core/database.py` (SQLAlchemy async engine, session factory, Base class)
  - Create `backend/app/core/logging.py` (structlog configuration with JSON output, correlation IDs)
  - Create `backend/app/core/exceptions.py` (custom exception classes: NotFoundException, ValidationError)
  - Create `backend/pyproject.toml` (dependencies: fastapi[all], sqlalchemy[asyncio], pydantic, pytest, structlog)
  - **Done when**: Project structure exists, `pip install -e .` succeeds, imports work

- [ ] 2. [FIRST SEAM ONLY] Create frontend project structure
  - Create `frontend/src/main.tsx` (entry point, React render, QueryClientProvider, Router)
  - Create `frontend/src/App.tsx` (React Router v6 root with routes)
  - Create `frontend/src/api/client.ts` (base HTTP client with axios/fetch, JWT token injection)
  - Create `frontend/src/components/layout/AppShell.tsx` (header, sidebar, main content area)
  - Create `frontend/src/lib/auth.ts` (JWT token management, useAuth hook)
  - Create `frontend/package.json` (dependencies: react, react-router-dom, @tanstack/react-query, zod, axios)
  - Create `frontend/vite.config.ts` (Vite config with proxy to backend)
  - Create `frontend/tailwind.config.ts` (Tailwind CSS config with shadcn/ui presets)
  - **Done when**: Project structure exists, `npm install` succeeds, `npm run dev` starts dev server

- [ ] 3. [FIRST SEAM ONLY] Set up database and migrations
  - Create `backend/alembic.ini` (Alembic configuration for database migrations)
  - Create `backend/alembic/env.py` (Alembic environment setup with async support)
  - Create initial migration: `alembic revision --autogenerate -m "Initial catalog schema"`
  - Verify migration creates Catalog, CatalogBrand, CatalogType tables with correct columns
  - **Done when**: `alembic upgrade head` creates tables in SQLite/PostgreSQL

- [ ] 4. [FIRST SEAM ONLY] Set up JWT authentication middleware
  - Create `backend/app/core/auth.py` (JWT token validation, get_current_user dependency)
  - Create `backend/app/auth/router.py` (POST /api/auth/login endpoint for token generation)
  - Create `backend/app/auth/schemas.py` (LoginRequest, TokenResponse Pydantic models)
  - Add authentication dependencies to `backend/app/dependencies.py`
  - **Done when**: Login endpoint returns JWT token, protected endpoints return 401 for invalid tokens

---

### Backend Implementation (Catalog CRUD + Image Upload)

- [ ] 5. Create backend module for catalog
  - File: `backend/app/catalog/__init__.py` (empty)
  - File: `backend/app/catalog/router.py` (empty, will implement endpoints later)
  - File: `backend/app/catalog/schemas.py` (empty, will implement DTOs later)
  - File: `backend/app/catalog/service.py` (empty, will implement business logic later)
  - File: `backend/app/catalog/models.py` (empty, will implement SQLAlchemy models later)
  - **Done when**: Module structure exists, files importable

- [ ] 6. Implement SQLAlchemy models
  - File: `backend/app/catalog/models.py`
  - Implement `CatalogItem` model (all fields from design.md Data Models section)
  - Implement `CatalogBrand` model (id, brand)
  - Implement `CatalogType` model (id, type)
  - Add relationships: `CatalogItem.catalog_brand`, `CatalogItem.catalog_type`
  - Add indexes: `name`, `catalog_brand_id`, `catalog_type_id`
  - _Implements: Database schema from requirements.md, design.md_
  - **Done when**: Models defined, match legacy schema (except HiLo → auto-increment), importable

- [ ] 7. Implement Pydantic schemas
  - File: `backend/app/catalog/schemas.py`
  - Implement `CatalogBrandResponse` (id, brand)
  - Implement `CatalogTypeResponse` (id, type)
  - Implement `CatalogItemResponse` (all fields + computed picture_uri)
  - Implement `CatalogItemCreate` (all fields + validation: name length, price range, stock range, temp_image_name)
  - Implement `CatalogItemUpdate` (same fields as Create)
  - Implement `PaginationMetadata` (page_index, page_size, total_items, total_pages)
  - Implement `CatalogItemListResponse` (items, pagination)
  - Implement `ImageUploadResponse` (temp_image_url, temp_image_name)
  - Add field validators: price max 2 decimals, stock ranges 0-10M, price 0-1M
  - _Implements: Requirements 1-8 validation rules_
  - **Done when**: All DTOs defined, validation rules match requirements.md, schemas importable

- [ ] 8. Implement IImageService adapter (abstract base)
  - File: `backend/app/adapters/image_service.py`
  - Implement `IImageService` ABC with methods: `upload_temp_image()`, `move_temp_image()`, `delete_image()`, `build_image_url()`
  - All methods must be `async def`
  - **Done when**: Abstract interface defined, no implementation yet

- [ ] 9. Implement MockImageService (local filesystem)
  - File: `backend/app/adapters/mock_image_service.py`
  - Implement `MockImageService(IImageService)` with local filesystem operations
  - `upload_temp_image()`: Save to `{IMAGE_STORAGE_PATH}/temp/{guid}/`
  - `move_temp_image()`: Copy from temp to `{IMAGE_STORAGE_PATH}/pics/{item_id}/`
  - `delete_image()`: Delete from `{IMAGE_STORAGE_PATH}/pics/{item_id}/`
  - `build_image_url()`: Return `/static/images/pics/{filename}`
  - Log all operations with structlog
  - **Done when**: Mock implementation complete, no external dependencies (S3, MinIO)

- [ ] 10. Implement CatalogService (business logic)
  - File: `backend/app/catalog/service.py`
  - Implement `CatalogService.__init__(self, db: AsyncSession)`
  - Implement `get_paginated(page, size)` → CatalogItemListResponse
    - Query: `SELECT * FROM catalog ORDER BY id LIMIT {size} OFFSET {page * size}`
    - Include: `selectinload(catalog_brand)`, `selectinload(catalog_type)`
    - Count: `SELECT COUNT(*) FROM catalog`
    - Compute: `picture_uri` via `ImageService.build_image_url()`
    - _Implements: Requirement 1.1, 1.2, 1.3_
  - Implement `get_by_id(item_id)` → Optional[CatalogItemResponse]
    - Query: `SELECT * FROM catalog WHERE id = {item_id}`
    - Include: `selectinload(catalog_brand)`, `selectinload(catalog_type)`
    - Return None if not found
    - _Implements: Requirement 2.1_
  - Implement `create(item_data)` → CatalogItemResponse
    - Validate: brand_id and type_id exist (query CatalogBrand, CatalogType)
    - Default: `picture_filename = "dummy.png"` if no temp_image_name
    - If temp_image_name: call `ImageService.move_temp_image()`, set picture_filename
    - Insert: `INSERT INTO catalog (...) VALUES (...)`
    - Return: created item with `get_by_id()`
    - _Implements: Requirement 3.1, 3.2_
  - Implement `update(item_id, item_data)` → Optional[CatalogItemResponse]
    - Load: existing item by id
    - Validate: brand_id and type_id exist
    - If temp_image_name: delete old images, move temp image, update picture_filename
    - Update: all fields from item_data
    - Return: updated item with `get_by_id()`
    - _Implements: Requirement 5.1, 5.2_
  - Implement `delete(item_id)` → bool
    - Load: item by id
    - Delete: `DELETE FROM catalog WHERE id = {item_id}`
    - Call: `ImageService.delete_image()` (best effort, log errors)
    - Return: True if deleted, False if not found
    - _Implements: Requirement 6.1, 6.2_
  - Implement `upload_temp_image(file)` → ImageUploadResponse
    - Validate: file size ≤5MB, format in [JPEG, PNG, GIF]
    - Call: `ImageService.upload_temp_image()`
    - Return: temp image URL and name
    - _Implements: Requirement 4.1, 4.2_
  - Implement `get_brands()` → list[CatalogBrandResponse]
    - Query: `SELECT * FROM catalog_brand ORDER BY id`
    - _Implements: Requirement 7.1_
  - Implement `get_types()` → list[CatalogTypeResponse]
    - Query: `SELECT * FROM catalog_type ORDER BY id`
    - _Implements: Requirement 8.1_
  - **Done when**: All service methods implemented, no DB calls yet (will add in next task)

- [ ] 11. Implement API endpoints (router)
  - File: `backend/app/catalog/router.py`
  - Create router: `router = APIRouter(prefix="/api/catalog", tags=["Catalog"])`
  - Implement `GET /` → list_catalog_items(page, size, db: AsyncSession)
    - Validate: page ≥0, 0 < size ≤100
    - Call: `CatalogService(db).get_paginated(page, size)`
    - _Implements: Requirement 1.1, 1.2_
  - Implement `GET /{item_id}` → get_catalog_item(item_id, db: AsyncSession)
    - Validate: item_id > 0
    - Call: `CatalogService(db).get_by_id(item_id)`
    - Return: 404 if None
    - _Implements: Requirement 2.1_
  - Implement `POST /` → create_catalog_item(item_data, db, current_user: Depends(get_current_user))
    - Auth: JWT required
    - Call: `CatalogService(db).create(item_data)`
    - Return: 201 Created + Location header
    - _Implements: Requirement 3.1_
  - Implement `PUT /{item_id}` → update_catalog_item(item_id, item_data, db, current_user: Depends(get_current_user))
    - Auth: JWT required
    - Call: `CatalogService(db).update(item_id, item_data)`
    - Return: 404 if None
    - _Implements: Requirement 5.1_
  - Implement `DELETE /{item_id}` → delete_catalog_item(item_id, db, current_user: Depends(get_current_user))
    - Auth: JWT required
    - Call: `CatalogService(db).delete(item_id)`
    - Return: 204 No Content
    - _Implements: Requirement 6.1_
  - Implement `POST /images` → upload_catalog_image(file, db, current_user: Depends(get_current_user))
    - Auth: JWT required
    - Call: `CatalogService(db).upload_temp_image(file)`
    - _Implements: Requirement 4.1_
  - Implement `GET /brands` → list_catalog_brands(db: AsyncSession)
    - No auth
    - Call: `CatalogService(db).get_brands()`
    - _Implements: Requirement 7.1_
  - Implement `GET /types` → list_catalog_types(db: AsyncSession)
    - No auth
    - Call: `CatalogService(db).get_types()`
    - _Implements: Requirement 8.1_
  - **Done when**: All endpoints defined, match OpenAPI contract, error handling complete

- [ ] 12. Register router in main app
  - File: `backend/app/main.py`
  - Import: `from app.catalog.router import router as catalog_router`
  - Register: `app.include_router(catalog_router)`
  - **Done when**: All endpoints accessible (test with curl or Postman)

- [ ] 13. Write unit tests for service layer
  - File: `backend/tests/unit/test_catalog_service.py`
  - Test: `test_get_paginated()` → returns items with pagination metadata _(Requirement 1.1)_
  - Test: `test_get_paginated_page_2()` → returns correct offset _(Requirement 1.2)_
  - Test: `test_get_paginated_empty()` → returns empty array if no items _(Requirement 1.9)_
  - Test: `test_get_by_id()` → returns single item _(Requirement 2.1)_
  - Test: `test_get_by_id_not_found()` → returns None _(Requirement 2.6)_
  - Test: `test_create()` → creates item with all fields _(Requirement 3.1)_
  - Test: `test_create_with_temp_image()` → moves temp image to permanent _(Requirement 3.2)_
  - Test: `test_create_invalid_brand()` → raises HTTPException(400) _(Requirement 3.9)_
  - Test: `test_update()` → updates item _(Requirement 5.1)_
  - Test: `test_update_with_image()` → replaces image _(Requirement 5.2)_
  - Test: `test_delete()` → deletes item and image _(Requirement 6.1, 6.2)_
  - Test: `test_upload_temp_image()` → validates and uploads _(Requirement 4.1)_
  - Test: `test_upload_temp_image_too_large()` → raises HTTPException(400) _(Requirement 4.4)_
  - Test: `test_get_brands()` → returns all brands _(Requirement 7.1)_
  - Test: `test_get_types()` → returns all types _(Requirement 8.1)_
  - **Done when**: All tests pass, coverage ≥80% on `service.py`

- [ ] 14. Write integration tests for API endpoints
  - File: `backend/tests/integration/test_catalog_api.py`
  - Use `httpx.AsyncClient` with `TestClient(app)`
  - Test: `test_list_catalog_items()` → GET /api/catalog returns 200 + JSON _(Requirement 1.1)_
  - Test: `test_list_catalog_items_pagination()` → pagination query params work _(Requirement 1.2)_
  - Test: `test_list_catalog_items_invalid_page()` → returns 400 _(Requirement 1.5)_
  - Test: `test_get_catalog_item()` → GET /api/catalog/{id} returns 200 _(Requirement 2.1)_
  - Test: `test_get_catalog_item_not_found()` → returns 404 _(Requirement 2.6)_
  - Test: `test_create_catalog_item()` → POST /api/catalog returns 201 _(Requirement 3.1)_
  - Test: `test_create_catalog_item_unauthenticated()` → returns 401 _(Requirement 3.11)_
  - Test: `test_create_catalog_item_invalid_price()` → returns 400 _(Requirement 3.6)_
  - Test: `test_update_catalog_item()` → PUT /api/catalog/{id} returns 200 _(Requirement 5.1)_
  - Test: `test_delete_catalog_item()` → DELETE /api/catalog/{id} returns 204 _(Requirement 6.1)_
  - Test: `test_upload_image()` → POST /api/catalog/images returns 200 _(Requirement 4.1)_
  - Test: `test_upload_image_unauthenticated()` → returns 401 _(Requirement 4.8)_
  - Test: `test_list_brands()` → GET /api/catalog/brands returns 200 _(Requirement 7.1)_
  - Test: `test_list_types()` → GET /api/catalog/types returns 200 _(Requirement 8.1)_
  - **Done when**: All integration tests pass, API contract validated

- [ ] 15. ✅ Checkpoint — Backend complete
  - Run: `pytest backend/tests/ && pytest --cov=backend/app/catalog`
  - Verify: All tests pass, coverage ≥80% on `catalog` module
  - Verify: All API endpoints accessible, match OpenAPI contract

---

### Frontend Implementation (React + TypeScript)

- [ ] 16. Create frontend module for catalog
  - File: `frontend/src/pages/catalog/CatalogListPage.tsx` (empty component)
  - File: `frontend/src/pages/catalog/CatalogDetailPage.tsx` (empty component)
  - File: `frontend/src/pages/catalog/CatalogCreatePage.tsx` (empty component)
  - File: `frontend/src/pages/catalog/CatalogEditPage.tsx` (empty component)
  - File: `frontend/src/api/catalog.ts` (empty API client)
  - File: `frontend/src/hooks/useCatalog.ts` (empty TanStack Query hook)
  - **Done when**: Module structure exists, files importable

- [ ] 17. Generate TypeScript types from OpenAPI contract
  - Run: `npx openapi-typescript docs/seams/catalog-management/contracts/openapi.yaml -o frontend/src/api/types.ts`
  - Verify: Types match Pydantic schemas (CatalogItemResponse, CatalogItemCreate, etc.)
  - **Done when**: Types generated, no compilation errors

- [ ] 18. Implement API client
  - File: `frontend/src/api/catalog.ts`
  - Implement `catalogApi.listItems(page, size)` → Promise<CatalogItemListResponse>
  - Implement `catalogApi.getItem(id)` → Promise<CatalogItemResponse>
  - Implement `catalogApi.createItem(data)` → Promise<CatalogItemResponse>
  - Implement `catalogApi.updateItem(id, data)` → Promise<CatalogItemResponse>
  - Implement `catalogApi.deleteItem(id)` → Promise<void>
  - Implement `catalogApi.uploadImage(file)` → Promise<ImageUploadResponse>
  - Implement `catalogApi.getBrands()` → Promise<CatalogBrandResponse[]>
  - Implement `catalogApi.getTypes()` → Promise<CatalogTypeResponse[]>
  - Use base client from `client.ts` (includes JWT token injection)
  - _Implements: Requirements 1-8 (API calls)_
  - **Done when**: API client calls backend endpoints, types match OpenAPI contract

- [ ] 19. Implement TanStack Query hooks
  - File: `frontend/src/hooks/useCatalog.ts`
  - Implement `useCatalogList(page, size)` → useQuery hook for list
  - Implement `useCatalogItem(id)` → useQuery hook for single item
  - Implement `useCatalogBrands()` → useQuery hook for brands (cached)
  - Implement `useCatalogTypes()` → useQuery hook for types (cached)
  - Implement `useCreateCatalogItem()` → useMutation hook for create
  - Implement `useUpdateCatalogItem()` → useMutation hook for update
  - Implement `useDeleteCatalogItem()` → useMutation hook for delete
  - Implement `useUploadImage()` → useMutation hook for image upload
  - Auto-invalidate queries on mutations (e.g., invalidate list after create)
  - _Implements: Requirements 1-8 (data fetching)_
  - **Done when**: Hooks fetch data, handle loading/error states, refetch on mutations

- [ ] 20. Implement UI components (shared)
  - File: `frontend/src/pages/catalog/components/CatalogTable.tsx` (table with all columns)
  - File: `frontend/src/pages/catalog/components/CatalogForm.tsx` (shared create/edit form)
  - File: `frontend/src/pages/catalog/components/ImageUpload.tsx` (file upload with preview)
  - File: `frontend/src/pages/catalog/components/DeleteConfirmationDialog.tsx` (modal)
  - File: `frontend/src/components/ui/Pagination.tsx` (prev/next buttons, page indicator)
  - Map columns from ui-behavior.md: image, name, description, brand, type, price, stock, actions
  - Map form fields from ui-behavior.md: name, description, price, brand dropdown, type dropdown, stock fields
  - _Implements: Requirements 1.1 (display), 3.1 (form), 6.1 (delete dialog)_
  - **Done when**: Components render, columns match ui-behavior.md, form fields match requirements

- [ ] 21. Implement CatalogListPage
  - File: `frontend/src/pages/catalog/CatalogListPage.tsx`
  - Compose: `<CatalogTable>`, `<Pagination>`, "Create New" button (if authenticated)
  - Use hook: `useCatalogList(page, size)`
  - Handle loading state: `<LoadingSpinner>`
  - Handle error state: `<ErrorDisplay>`
  - Display pagination info: "Showing {ItemsPerPage} of {TotalItems} products - Page {ActualPage + 1} - {TotalPages}"
  - _Implements: Requirements 1.1, 1.2, 1.3_
  - **Done when**: Page renders, displays products, pagination works

- [ ] 22. Implement CatalogDetailPage
  - File: `frontend/src/pages/catalog/CatalogDetailPage.tsx`
  - Use hook: `useCatalogItem(id)` (get id from route params)
  - Display: all product fields in two-column layout (image left, fields right)
  - Actions: "Back to list" button, "Edit" button (if authenticated)
  - _Implements: Requirement 2.1_
  - **Done when**: Page renders, displays product details, navigation works

- [ ] 23. Implement CatalogCreatePage
  - File: `frontend/src/pages/catalog/CatalogCreatePage.tsx`
  - Use hook: `useCatalogBrands()`, `useCatalogTypes()` (for dropdowns)
  - Use hook: `useCreateCatalogItem()` (for form submission)
  - Use component: `<CatalogForm mode="create">`
  - Handle image upload: `<ImageUpload>` → set tempImageName on success
  - On success: navigate to product list
  - _Implements: Requirements 3.1, 3.2, 4.1_
  - **Done when**: Form submits, creates product, redirects to list

- [ ] 24. Implement CatalogEditPage
  - File: `frontend/src/pages/catalog/CatalogEditPage.tsx`
  - Use hook: `useCatalogItem(id)` (pre-populate form)
  - Use hook: `useCatalogBrands()`, `useCatalogTypes()` (for dropdowns)
  - Use hook: `useUpdateCatalogItem()` (for form submission)
  - Use component: `<CatalogForm mode="edit" initialData={product}>`
  - Handle image replacement: `<ImageUpload>` → set tempImageName on success
  - On success: navigate to product list
  - _Implements: Requirements 5.1, 5.2_
  - **Done when**: Form pre-populated, submits updates, redirects to list

- [ ] 25. Implement delete functionality
  - File: `frontend/src/pages/catalog/CatalogListPage.tsx` (modify)
  - Add "Delete" button in table actions
  - On click: open `<DeleteConfirmationDialog>` with product data
  - On confirm: call `useDeleteCatalogItem()`, invalidate list query
  - _Implements: Requirement 6.1_
  - **Done when**: Delete button opens dialog, confirm deletes product, list refreshes

- [ ] 26. Add routes to application
  - File: `frontend/src/App.tsx`
  - Import: `CatalogListPage`, `CatalogDetailPage`, `CatalogCreatePage`, `CatalogEditPage`
  - Add routes:
    - `/catalog` → `<CatalogListPage />`
    - `/catalog/:id` → `<CatalogDetailPage />`
    - `/catalog/create` → `<CatalogCreatePage />` (protected route)
    - `/catalog/:id/edit` → `<CatalogEditPage />` (protected route)
  - Add nav link in AppShell: "Catalog" → `/catalog`
  - **Done when**: Routes accessible, navigation works, protected routes require JWT

- [ ] 27. Copy static assets (if applicable)
  - Create: `frontend/src/assets/catalog/index.ts` (typed asset exports)
  - Copy: brand logos, default product image (`dummy.png`) from legacy app
  - Compress: images >500KB (use `sharp` or online tool)
  - _Implements: Asset management from ui-behavior.md_
  - **Done when**: Assets copied, typed exports available, images optimized

- [ ] 28. Write unit tests for components
  - File: `frontend/src/pages/catalog/CatalogListPage.test.tsx`
  - Mock: API with `msw` (Mock Service Worker)
  - Test: Page renders with data _(Requirement 1.1)_
  - Test: Pagination updates query _(Requirement 1.2)_
  - Test: Loading state displays _(NFR: observability)_
  - Test: Error state displays _(NFR: error handling)_
  - Test: "Create New" button visible if authenticated _(Requirement 3.1)_
  - File: `frontend/src/pages/catalog/CatalogCreatePage.test.tsx`
  - Test: Form validation (name required, price range) _(Requirement 3.5, 3.6)_
  - Test: Image upload updates preview _(Requirement 4.1)_
  - **Done when**: All tests pass, coverage ≥75% on pages/hooks

- [ ] 29. Write E2E tests with Playwright
  - File: `frontend/tests/e2e/catalog.spec.ts`
  - Test: Navigate to `/catalog`, see products in table _(Requirement 1.1)_
  - Test: Click pagination "Next", see page 2 products _(Requirement 1.2)_
  - Test: Click "Details" link, see product details _(Requirement 2.1)_
  - Test: Click "Create New" (authenticated), fill form, submit, see new product in list _(Requirement 3.1)_
  - Test: Click "Edit" (authenticated), change name, save, see updated name _(Requirement 5.1)_
  - Test: Click "Delete" (authenticated), confirm, see product removed _(Requirement 6.1)_
  - **Done when**: All E2E tests pass, happy paths verified

- [ ] 30. ✅ Checkpoint — Frontend complete
  - Run: `npm test && npm run test:e2e`
  - Verify: All tests pass, coverage ≥75% on pages/hooks
  - Verify: E2E tests pass, UI matches ui-behavior.md

---

### Contract Validation

- [ ] 31. Validate backend contract alignment
  - Run: `python .claude/scripts/validate_contract_backend.py backend/app docs/seams/catalog-management/contracts/openapi.yaml`
  - Verify: All endpoints defined in contract are implemented
  - Verify: No extra endpoints (not in contract)
  - **Done when**: Validation passes, backend matches contract

- [ ] 32. Validate frontend contract alignment
  - Run: `python .claude/scripts/validate_contract_frontend.py frontend/src docs/seams/catalog-management/contracts/openapi.yaml`
  - Verify: All API calls match contract endpoints
  - Verify: No API calls to undefined endpoints
  - **Done when**: Validation passes, frontend matches contract

---

### Data Migration

- [ ] 33. Export legacy database
  - Run: `sqlcmd -S {server} -d {database} -Q "SELECT * FROM Catalog" -o catalog.csv`
  - Run: `sqlcmd -S {server} -d {database} -Q "SELECT * FROM CatalogBrand" -o brands.csv`
  - Run: `sqlcmd -S {server} -d {database} -Q "SELECT * FROM CatalogType" -o types.csv`
  - **Done when**: CSV files exported with all rows

- [ ] 34. Transform data (remove HiLo sequence)
  - Script: `python scripts/transform_catalog_data.py`
  - Remove: HiLo sequence references (catalog_hilo table not migrated)
  - Adjust: ID generation (keep existing IDs, use auto-increment for new items)
  - Validate: No NULL values in required fields
  - **Done when**: Transformed CSVs ready for import

- [ ] 35. Import data to PostgreSQL
  - Run: `psql -U {user} -d {database} -c "\COPY catalog FROM 'catalog.csv' CSV HEADER"`
  - Run: `psql -U {user} -d {database} -c "\COPY catalog_brand FROM 'brands.csv' CSV HEADER"`
  - Run: `psql -U {user} -d {database} -c "\COPY catalog_type FROM 'types.csv' CSV HEADER"`
  - Verify: Row counts match legacy database
  - **Done when**: All data imported, no errors

- [ ] 36. Migrate product images
  - Script: `python scripts/migrate_images.py`
  - Copy: All images from Azure Blob Storage (or legacy path) to MinIO/S3
  - Path: `pics/{item_id}/{filename}`
  - Verify: All images accessible via `ImageService.build_image_url()`
  - **Done when**: All images migrated, no 404 errors

- [ ] 37. Validate data integrity
  - Run: `python scripts/validate_migration.py`
  - Check: Row counts (Catalog, CatalogBrand, CatalogType)
  - Check: Foreign key integrity (all brand_id and type_id references valid)
  - Check: Image URLs (all products have valid picture_uri)
  - **Done when**: All validation checks pass

---

### Visual Parity Check

- [ ] 38. Capture modern screenshot
  - Run backend: `cd backend && uvicorn app.main:app --reload`
  - Run frontend: `cd frontend && npm run dev`
  - Capture: `npx playwright screenshot http://localhost:5173/catalog --output docs/seams/catalog-management/modern-screenshot.png`
  - **Done when**: Screenshot captured

- [ ] 39. Compare with legacy baseline
  - Run: `python .claude/scripts/compare_screenshots.py docs/legacy-golden/catalog-management/screenshots/main.png docs/seams/catalog-management/modern-screenshot.png --threshold 85 --output docs/seams/catalog-management/diff.png`
  - Verify: SSIM ≥85%
  - If fails: Review diff.png, identify missing elements, update frontend
  - **Done when**: SSIM ≥85%, visual parity achieved

---

### Final Checkpoint

- [ ] 40. ✅ Final Checkpoint — All tasks complete
  - Run: `pytest backend/tests/ && npm test && npm run test:e2e`
  - Verify: All tests pass (backend + frontend + E2E)
  - Verify: Coverage ≥80% (backend), ≥75% (frontend)
  - Verify: Contract validation passes (backend + frontend)
  - Verify: Visual parity ≥85% SSIM
  - Verify: Data migration complete (all products, brands, types, images)
  - Verify: No P0/P1 issues from code review
  - **Done when**: All gates pass, seam ready for staging deployment

---

## Notes

- Tasks reference files from design.md (full paths, class names, method signatures)
- Each task includes requirement IDs from requirements.md
- Checkpoints ensure incremental validation
- All tasks are coding tasks (no manual testing, no deployments)
- Scaffolding tasks (1-4) only run for first seam (project setup)
- Backend tasks (5-15) implement all API endpoints and business logic
- Frontend tasks (16-30) implement all UI pages and components
- Contract validation (31-32) ensures backend and frontend align with OpenAPI spec
- Data migration (33-37) moves legacy data to modern database and storage
- Visual parity (38-39) ensures UI matches legacy screenshots
- Final checkpoint (40) gates deployment to staging

---

## Execution Order

**Phase 1: Scaffolding (Tasks 1-4)** — Set up project structure (backend + frontend)
**Phase 2: Backend API (Tasks 5-15)** — Implement all API endpoints, business logic, tests
**Phase 3: Frontend UI (Tasks 16-30)** — Implement all pages, components, tests
**Phase 4: Contract Validation (Tasks 31-32)** — Ensure backend/frontend align with OpenAPI contract
**Phase 5: Data Migration (Tasks 33-37)** — Migrate legacy data to modern system
**Phase 6: Visual Parity (Tasks 38-39)** — Verify UI matches legacy screenshots
**Phase 7: Final Checkpoint (Task 40)** — Gate deployment to staging

---

**Document Version**: 1.0
**Last Updated**: 2026-03-03
**Status**: Ready for Implementation
