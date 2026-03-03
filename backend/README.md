# eShop Catalog API - Backend

FastAPI backend for eShop catalog management (migrated from ASP.NET WebForms).

## Tech Stack

- **Python 3.12+**
- **FastAPI** - async web framework
- **SQLAlchemy 2.x** - async ORM
- **Pydantic v2** - data validation
- **Structlog** - structured logging
- **aiosqlite** - async SQLite driver
- **pytest** - testing framework

## Setup

### 1. Install Dependencies

```bash
# Install Poetry (if not already installed)
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and configure:
# - DATABASE_URL (defaults to SQLite)
# - USE_MOCK_ADAPTERS (true for mock data, false for real database)
```

### 3. Run the Application

```bash
# Development mode (with auto-reload)
poetry run uvicorn app.main:app --reload --port 8000

# Production mode
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Access the API:
- **API Documentation**: http://localhost:8000/api/docs
- **Health Check**: http://localhost:8000/api/health

## Mock vs Real Mode

### Mock Mode (Default)
- Set `USE_MOCK_ADAPTERS=true` in `.env`
- Returns hardcoded sample data
- No database required
- Useful for frontend development

### Real Mode
- Set `USE_MOCK_ADAPTERS=false` in `.env`
- Uses SQLite database
- Database and tables created automatically on startup
- Seed data populated on first run

## Testing

### Run All Tests

```bash
poetry run pytest
```

### Run Unit Tests Only

```bash
poetry run pytest tests/unit/
```

### Run with Coverage

```bash
poetry run pytest --cov=app --cov-report=html
```

View coverage report: `htmlcov/index.html`

### Run Specific Test

```bash
poetry run pytest tests/unit/test_catalog_service.py::TestCatalogService::test_get_catalog_brands
```

## Database

### SQLite (Default)

Database file: `eshop_catalog.db` (created automatically)

### PostgreSQL (Production)

Update `.env`:
```
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/eshop_catalog
```

### Manual Database Initialization

```python
# Python shell
poetry run python

from app.core.db import init_db, async_session_maker
from app.core.seed import seed_database
import asyncio

async def init():
    await init_db()
    async with async_session_maker() as session:
        await seed_database(session)

asyncio.run(init())
```

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Configuration (Pydantic settings)
│   ├── dependencies.py      # DI factories
│   ├── core/
│   │   ├── db.py            # Database engine & session
│   │   ├── models.py        # SQLAlchemy models
│   │   ├── schemas.py       # Pydantic DTOs
│   │   ├── service.py       # CatalogService + Mock
│   │   ├── seed.py          # Database seed script
│   │   ├── logging.py       # Structlog config
│   │   └── exceptions.py    # Custom exceptions
│   └── catalog/             # (To be added - catalog endpoints)
├── tests/
│   ├── unit/                # Unit tests
│   ├── integration/         # Integration tests
│   └── parity/              # Parity tests
├── pyproject.toml           # Poetry dependencies
└── .env                     # Environment variables
```

## API Endpoints (Planned)

### Catalog Items
- `GET /api/catalog/items?page_size={size}&page_index={index}` - List items (paginated)
- `GET /api/catalog/items/{id}` - Get item by ID
- `POST /api/catalog/items` - Create item
- `PUT /api/catalog/items/{id}` - Update item
- `DELETE /api/catalog/items/{id}` - Delete item

### Reference Data
- `GET /api/catalog/brands` - Get all brands
- `GET /api/catalog/types` - Get all types

### Health
- `GET /api/health` - Health check

## Development

### Code Quality

```bash
# Format code
poetry run black app/ tests/

# Lint code
poetry run ruff check app/ tests/

# Type check
poetry run mypy app/
```

### Logging

All logs are structured JSON (in production) or pretty-printed (in development).

Log levels: DEBUG, INFO, WARNING, ERROR

Configure via `LOG_LEVEL` in `.env`.

## Migration Status

✅ **Data Access Layer (Complete)**
- SQLAlchemy models (CatalogItem, CatalogBrand, CatalogType)
- Pydantic schemas (DTOs)
- CatalogService + CatalogServiceMock
- Database seed script
- Unit tests

❌ **Catalog List API (Pending)**
❌ **Catalog CRUD API (Pending)**

See `MIGRATION_STATUS.md` in project root for full migration progress.
