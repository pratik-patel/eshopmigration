# Quick Start Guide: eShop Migration

**Project**: eShop Legacy to Modern Web Migration
**Date**: 2026-03-02

---

## Prerequisites

- Python 3.12+
- Node.js 18+ and npm
- Poetry (Python package manager)
- Git

---

## Quick Start (5 minutes)

### 1. Start Backend (Terminal 1)

```bash
# Navigate to backend
cd C:\Users\pratikp6\codebase\eshopmigration\backend

# Install dependencies (first time only)
poetry install

# Start FastAPI server
poetry run uvicorn app.main:app --reload --port 8000
```

**Expected Output**:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

**Verify Backend**:
Open in browser: http://localhost:8000/docs (Swagger UI)

---

### 2. Start Frontend (Terminal 2)

```bash
# Navigate to frontend
cd C:\Users\pratikp6\codebase\eshopmigration\frontend

# Install dependencies (first time only)
npm install

# Start Vite dev server
npm run dev
```

**Expected Output**:
```
VITE v5.0.12  ready in XXX ms
➜  Local:   http://localhost:5173/
```

**Open Application**:
Navigate to: http://localhost:5173/

---

## What You Should See

### Home Page (Catalog List)
- Green "Create New" button at top
- Table with 10 products (or however many are in the database)
- Product images, names, descriptions, brands, types, prices
- Edit | Details | Delete links for each product
- Pagination controls (hidden if only 1 page)

### Create New Page
- Form with fields: Name, Description, Brand, Type, Price, Stock, etc.
- Green "[ Create ]" button
- Red "[ Cancel ]" button

---

## Troubleshooting

### Backend won't start
**Error**: `No module named 'app'`
**Fix**: Ensure you're in the `backend/` directory and Poetry environment is active

**Error**: `Address already in use`
**Fix**: Kill process on port 8000 or use different port:
```bash
poetry run uvicorn app.main:app --reload --port 8001
```

### Frontend won't start
**Error**: `npm: command not found`
**Fix**: Install Node.js and npm

**Error**: `Cannot find module`
**Fix**: Run `npm install` first

### API calls fail (Network Error)
**Check**:
1. Backend is running on port 8000
2. No firewall blocking localhost:8000
3. Check browser console for errors

### Images don't load (404)
**Check**:
1. Images exist in `frontend/public/pics/`
2. Backend is NOT serving `/pics` (should be frontend static files)
3. Vite proxy NOT configured for `/pics`

---

## Running Tests

### Backend Tests
```bash
cd backend
poetry run pytest
```

### Frontend Unit Tests
```bash
cd frontend
npm run test
```

### Frontend E2E Tests
```bash
cd frontend
npx playwright test
```

**Note**: Backend must be running for E2E tests to pass.

---

## Database

### Location
- Development: `backend/eshop.db` (SQLite)
- Contains seed data with 10 products

### View Data
```bash
cd backend
sqlite3 eshop.db
sqlite> SELECT id, name, price FROM catalog_items;
sqlite> .quit
```

### Reset Database
```bash
cd backend
rm eshop.db
poetry run python -m app.core.seed
```

---

## Project Structure

```
eshopmigration/
├── backend/                 # Python FastAPI backend
│   ├── app/
│   │   ├── catalog/        # Catalog seam (router, schemas, service)
│   │   ├── core/           # DB, config, exceptions
│   │   └── main.py         # FastAPI app entry point
│   ├── tests/              # Backend tests
│   ├── eshop.db            # SQLite database
│   └── pyproject.toml      # Poetry dependencies
│
├── frontend/               # React + TypeScript frontend
│   ├── src/
│   │   ├── api/            # API client methods
│   │   ├── components/     # React components
│   │   ├── hooks/          # TanStack Query hooks
│   │   ├── pages/          # Page components (one per seam)
│   │   ├── styles/         # CSS (including legacy esh-* classes)
│   │   └── assets/         # Typed asset exports
│   ├── public/
│   │   └── pics/           # Product images (1.png - 13.png, dummy.png)
│   ├── tests/              # E2E tests (Playwright)
│   └── package.json        # npm dependencies
│
└── docs/                   # Documentation
    ├── seams/              # Per-seam documentation
    │   └── catalog-list/
    │       ├── contracts/openapi.yaml
    │       ├── ui-behavior.md
    │       ├── discovery.md
    │       ├── FRONTEND_IMPLEMENTATION_SUMMARY.md
    │       └── VALIDATION_CHECKLIST.md
    └── context-fabric/     # Cross-cutting concerns
```

---

## Seam Status

| Seam | Backend | Frontend | Tests | Status |
|------|---------|----------|-------|--------|
| catalog-list | ✅ | ✅ | ✅ | Complete |
| catalog-crud | ✅ | ✅ | ✅ | Complete |
| static-pages | 🟡 | 🟡 | ⚪ | In Progress |

**Legend**:
- ✅ Complete
- 🟡 Partial
- ⚪ Not Started

---

## API Endpoints

### Catalog List
```
GET /api/catalog/items?page_size=10&page_index=0
```

**Response**:
```json
{
  "page_index": 0,
  "page_size": 10,
  "total_items": 10,
  "total_pages": 1,
  "data": [
    {
      "id": 1,
      "name": ".NET Bot Black Hoodie",
      "price": 19.5,
      "picture_file_name": "1.png",
      "catalog_brand": { "id": 2, "brand": ".NET" },
      "catalog_type": { "id": 2, "type": "T-Shirt" },
      ...
    }
  ]
}
```

### Catalog CRUD
```
GET    /api/catalog/items/{id}         # Get single item
POST   /api/catalog/items              # Create item
PUT    /api/catalog/items/{id}         # Update item
DELETE /api/catalog/items/{id}         # Delete item
GET    /api/catalog/brands             # Get all brands
GET    /api/catalog/types              # Get all types
```

---

## Frontend Routes

| Route | Component | Purpose |
|-------|-----------|---------|
| `/` | CatalogListPage | Home page, product list |
| `/catalog/create` | CatalogCreatePage | Create new product |
| `/catalog/edit/:id` | CatalogEditPage | Edit existing product |
| `/catalog/details/:id` | CatalogDetailsPage | View product details |
| `/catalog/delete/:id` | CatalogDeletePage | Delete product confirmation |
| `/about` | AboutPage | About page (static) |
| `/contact` | ContactPage | Contact page (static) |

---

## Tech Stack

### Backend
- **Framework**: FastAPI (async)
- **Database**: SQLite (development), PostgreSQL-compatible
- **ORM**: SQLAlchemy 2.x (async)
- **Validation**: Pydantic v2
- **Testing**: pytest + pytest-asyncio
- **Logging**: structlog

### Frontend
- **Framework**: React 18
- **Language**: TypeScript (strict mode)
- **Build Tool**: Vite
- **Routing**: React Router v6
- **State Management**: TanStack Query v5 (server state), Zustand (UI state)
- **Styling**: Tailwind CSS + legacy CSS classes
- **Validation**: Zod + React Hook Form
- **Testing**: Vitest (unit), Playwright (E2E)

---

## Environment Variables

### Backend (.env)
```env
# Database
DATABASE_URL=sqlite+aiosqlite:///./eshop.db

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=True

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### Frontend (.env)
```env
# API Base URL (optional, defaults to /api)
VITE_API_BASE_URL=/api
```

---

## Development Workflow

### 1. Make Changes
- Backend: Edit files in `backend/app/`
- Frontend: Edit files in `frontend/src/`
- Both servers hot-reload automatically

### 2. Run Tests
```bash
# Backend
cd backend
poetry run pytest

# Frontend
cd frontend
npm run test
```

### 3. Type Check & Lint
```bash
# Backend
cd backend
poetry run mypy app

# Frontend
cd frontend
npm run build  # Runs TypeScript compiler
npm run lint   # Runs ESLint
```

### 4. Commit Changes
```bash
git add .
git commit -m "feat(catalog-list): implement frontend with asset migration"
git push origin main
```

---

## Next Steps

### For Developers
1. Read `docs/seams/catalog-list/ui-behavior.md` for UI specifications
2. Check `docs/seams/catalog-list/contracts/openapi.yaml` for API contract
3. Run validation checklist: `docs/seams/catalog-list/VALIDATION_CHECKLIST.md`

### For Testers
1. Follow validation checklist
2. Compare visual output to legacy screenshots in `legacy-golden/screenshots/`
3. Run E2E tests and report failures

### For Stakeholders
1. Review implementation summary: `docs/seams/catalog-list/FRONTEND_IMPLEMENTATION_SUMMARY.md`
2. View live application at http://localhost:5173/
3. Test user workflows: Create, Edit, View, Delete products

---

## Support & Documentation

- **Full Documentation**: `docs/` directory
- **API Docs**: http://localhost:8000/docs (Swagger UI)
- **Contract Specs**: `docs/seams/{seam}/contracts/openapi.yaml`
- **UI Behavior**: `docs/seams/{seam}/ui-behavior.md`
- **Discovery Reports**: `docs/seams/{seam}/discovery.md`

---

## Common Commands Cheat Sheet

```bash
# Backend
cd backend
poetry install              # Install dependencies
poetry run uvicorn app.main:app --reload  # Start server
poetry run pytest           # Run tests
poetry run mypy app         # Type check

# Frontend
cd frontend
npm install                 # Install dependencies
npm run dev                 # Start dev server
npm run build               # Build for production
npm run test                # Run unit tests
npm run lint                # Lint code
npx playwright test         # Run E2E tests

# Database
cd backend
sqlite3 eshop.db            # Open database
rm eshop.db && poetry run python -m app.core.seed  # Reset DB
```

---

**Last Updated**: 2026-03-02
**Maintained By**: Migration Team
