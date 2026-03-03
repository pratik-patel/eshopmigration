# Baseline Index: data-access

**Captured**: 2026-03-02T00:00:00Z
**Application Type**: Infrastructure Layer (Entity Framework 6 → SQLAlchemy 2.x async)
**Framework**: Entity Framework 6 (legacy), SQLAlchemy 2.x (migration)
**Capture Tools**: SYNTHETIC (code analysis)
**Environment**: N/A (infrastructure seam - no UI)
**Status**: ✅ **INFRASTRUCTURE BASELINE** - Code-derived schema and interface definitions

---

## Overview

**Seam Type**: Infrastructure / Library (foundational)

**Purpose**: Database access layer providing ORM models, service interface, and CRUD operations for catalog entities.

**No UI Workflows**: This seam has no user-facing pages. Baselines capture:
1. Database schema structure
2. Entity model signatures
3. Service interface contracts
4. Seed data definitions

---

## Screenshots

**Status**: N/A (no UI for infrastructure layer)

---

## Exports

### Entity Models

| File | Source | Notes |
|------|--------|-------|
| `exports/synthetic_entity_models.json` | Models/*.cs | Complete entity signatures (CatalogItem, CatalogBrand, CatalogType) |

**Contents**:
- CatalogItem: 12 properties + 2 navigation properties
- CatalogBrand: 2 properties
- CatalogType: 2 properties
- Validation rules (Range, RegEx)
- Foreign key relationships

**Data Accuracy**: ✅ Exact match to EF6 model definitions

---

### Service Interface

| File | Source | Notes |
|------|--------|-------|
| `exports/synthetic_service_interface.json` | Services/ICatalogService.cs | Complete method signatures (7 methods) |

**Contents**:
- Method signatures with parameter types
- Return types
- SQL operations performed
- Migration mapping to SQLAlchemy patterns

**Data Accuracy**: ✅ Exact match to ICatalogService interface

---

### Database Schema

| File | Source | Notes |
|------|--------|-------|
| `exports/synthetic_schema.json` | EF6 context + annotations | Complete schema (3 tables, columns, constraints) |

**Contents**:
- Table definitions (CatalogItems, CatalogBrands, CatalogTypes)
- Column types and nullability
- Primary keys and foreign keys
- Indexes
- Type mapping (SQL Server → SQLite)

**Data Accuracy**: ✅ Exact match to EF6-generated schema

---

### Seed Data

| File | Source | Notes |
|------|--------|-------|
| (Reference) `backend/app/core/seed.py` | Migrated seed data | Already implemented |

**Contents**:
- 5 CatalogBrands (`.NET`, `Other`, `Azure`, `Visual Studio`, `SQL Server`)
- 4 CatalogTypes (`Mug`, `T-Shirt`, `Sheet`, `USB Memory Stick`)
- 12 CatalogItems (products with prices, stock levels)

**Data Accuracy**: ✅ Matches legacy PreconfiguredData class

---

## Database Snapshots

**Status**: N/A (seed data definitions sufficient)

No runtime snapshots needed - database structure is deterministic from schema + seed data.

---

## API/HTTP Captures

**Status**: N/A (internal service layer, not exposed as HTTP API)

Service methods are called internally by other seams (catalog-list, catalog-crud).

---

## Coverage

**Spec Components Captured**: 5/5

### Components
1. ✅ Entity models (CatalogItem, CatalogBrand, CatalogType)
2. ✅ Service interface (ICatalogService - 7 methods)
3. ✅ Database schema (3 tables with relationships)
4. ✅ Seed data definitions
5. ✅ Migration mapping (EF6 → SQLAlchemy)

**Edge Cases Captured**: 0 (infrastructure seam - no edge cases)

**Synthetic Baselines**: YES (all baselines are code-derived)

---

## Parity Test Strategy

### What CAN Be Validated

✅ **Entity Model Structure**:
- All properties exist with correct types
- Foreign key relationships defined correctly
- Navigation properties configured

✅ **Service Method Signatures**:
- Method names match exactly
- Parameter types match
- Return types match

✅ **Database Schema**:
- Tables exist with correct names
- Columns have correct types and constraints
- Foreign keys enforced

✅ **Query Results**:
- FindCatalogItem(1) returns same data in both systems
- GetCatalogItemsPaginated(10, 0) returns same items
- GetCatalogBrands() returns same brands in same order
- GetCatalogTypes() returns same types in same order

✅ **CRUD Operations**:
- CreateCatalogItem inserts row correctly
- UpdateCatalogItem modifies row correctly
- RemoveCatalogItem deletes row correctly

### What CANNOT Be Validated (Without Runtime Testing)

❌ **Query Performance**: Cannot compare execution times without load testing
❌ **Transaction Isolation**: Cannot verify concurrency behavior without concurrent requests
❌ **Connection Pooling**: Cannot verify pool behavior without multiple simultaneous connections

---

## Validation Test Cases

### Entity Model Validation
- [ ] CatalogItem model has all 12 properties with correct types
- [ ] Price field uses Numeric(18, 2) type
- [ ] Foreign keys (CatalogTypeId, CatalogBrandId) defined correctly
- [ ] Navigation properties (catalog_type, catalog_brand) load correctly
- [ ] Default values applied (PictureFileName = "dummy.png", AvailableStock = 0)

### Service Method Validation
- [ ] find_catalog_item(1) returns product with brand and type loaded
- [ ] get_catalog_items_paginated(10, 0) returns 10 items with total count
- [ ] get_catalog_brands() returns 5 brands ordered by ID
- [ ] get_catalog_types() returns 4 types ordered by ID
- [ ] create_catalog_item() inserts row and returns with ID assigned
- [ ] update_catalog_item() modifies row in database
- [ ] delete_catalog_item() removes row from database

### Schema Validation
- [ ] CatalogItems table exists with 12 columns
- [ ] CatalogBrands table exists with 2 columns
- [ ] CatalogTypes table exists with 2 columns
- [ ] Foreign key constraints enforced (INSERT with invalid brand_id fails)
- [ ] Primary key auto-increment works

### Seed Data Validation
- [ ] Database contains 5 brands (`.NET`, `Other`, `Azure`, `Visual Studio`, `SQL Server`)
- [ ] Database contains 4 types (`Mug`, `T-Shirt`, `Sheet`, `USB Memory Stick`)
- [ ] Database contains 12 catalog items
- [ ] Product 1 is ".NET Bot Black Hoodie" with price $19.50, brand `.NET`, type `T-Shirt`

---

## Validation Strategy

### Unit Tests
**Location**: `backend/tests/unit/test_catalog_service.py`

Test each service method in isolation with mock database.

### Integration Tests
**Location**: `backend/tests/integration/test_catalog_crud.py`

Test service methods against real SQLite database.

### Parity Tests
**Location**: `backend/tests/parity/test_catalog_data_access.py`

Compare query results between legacy and migrated systems:
1. Fetch item 1 from both systems
2. Compare all properties (name, price, brand, type, etc.)
3. Verify ordering of paginated results matches
4. Verify brand/type lists match exactly

---

## Migration Mapping

### Entity Framework 6 → SQLAlchemy 2.x

| EF6 Pattern | SQLAlchemy Pattern |
|-------------|-------------------|
| `DbSet<CatalogItem>` | `class CatalogItem(Base)` |
| `public int Id { get; set; }` | `id: Mapped[int] = mapped_column(primary_key=True)` |
| `public CatalogType CatalogType { get; set; }` | `catalog_type: Mapped["CatalogType"] = relationship(...)` |
| `db.CatalogItems.Include(c => c.CatalogBrand)` | `selectinload(CatalogItem.catalog_brand)` |
| `db.SaveChanges()` | `await session.commit()` |
| `EntityState.Modified` | Direct property modification + `await session.flush()` |

### Service Interface → Async Service Class

| Legacy Method | Migration Method |
|---------------|------------------|
| `CatalogItem FindCatalogItem(int id)` | `async def find_catalog_item(db: AsyncSession, item_id: int) -> CatalogItem \| None` |
| `IEnumerable<CatalogBrand> GetCatalogBrands()` | `async def get_catalog_brands(db: AsyncSession) -> list[CatalogBrand]` |
| `void CreateCatalogItem(CatalogItem item)` | `async def create_catalog_item(db: AsyncSession, item: CatalogItem) -> CatalogItem` |

---

## Known Limitations

### No Runtime Behavior Capture
Cannot capture actual query execution plans, lock behavior, or performance metrics without running both systems side-by-side.

### No Concurrent Write Testing
Cannot verify transaction isolation or deadlock handling without multi-threaded test harness.

### No Connection String Capture
Connection strings are environment-specific (localhost, credentials) and not captured.

---

## Readiness Assessment

**Ready for Implementation**: ✅ YES

**Confidence**: HIGH
- Complete schema documented
- All entity models defined
- Service interface fully specified
- Seed data preserved
- Migration patterns documented

**Blockers**: NONE

**Dependencies**:
- Used by: catalog-list seam, catalog-crud seam
- Depends on: NONE (foundational layer)

---

## Implementation Status

- ✅ SQLAlchemy models created (`backend/app/catalog/models.py`)
- ✅ Service class implemented (`backend/app/catalog/service.py`)
- ✅ Seed script created (`backend/app/core/seed.py`)
- ✅ Database initialization working
- ⏳ Unit tests (pending)
- ⏳ Integration tests (pending)
- ⏳ Parity tests (pending)

---

## Next Steps

1. ✅ Baseline capture complete (this document)
2. → Run unit tests for service methods
3. → Run integration tests for CRUD operations
4. → Run parity tests comparing legacy vs migrated query results
5. → Manual verification: seed database and verify 5 brands, 4 types, 12 items

**Estimated Testing Time**: 1-2 hours (unit + integration + parity)

---

**Capture Method**: SYNTHETIC (code analysis)
**Capture Date**: 2026-03-02
**Capture Status**: COMPLETE
**Ready for Validation**: YES
