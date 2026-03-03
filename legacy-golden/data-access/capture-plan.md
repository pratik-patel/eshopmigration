# Golden Baseline Capture Plan: data-access

**Seam**: data-access
**Date**: 2026-03-02
**Status**: SYNTHETIC (infrastructure seam - no UI workflows)

---

## Overview

**Seam Type**: Infrastructure / Library
**Purpose**: Database access layer (Entity Framework 6 → SQLAlchemy 2.x async)

**Note**: This is NOT a user-facing workflow seam. There are no UI pages or HTTP workflows to capture. Instead, we capture:
1. Database schema and constraints
2. Entity model signatures
3. Service interface contracts
4. Seed data
5. Query patterns

---

## What to Capture

### 1. Database Schema
**Source**: `CatalogDBContext.cs`, model annotations
**Purpose**: Ensure migrated SQLAlchemy models match legacy schema exactly

**Tables**:
- CatalogItems (primary table)
- CatalogBrands (lookup table)
- CatalogTypes (lookup table)

**Constraints**:
- Primary keys (Id columns)
- Foreign keys (CatalogBrandId, CatalogTypeId)
- Column types, nullability, defaults

---

### 2. Entity Model Signatures
**Source**: `Models/CatalogItem.cs`, `Models/CatalogBrand.cs`, `Models/CatalogType.cs`
**Purpose**: Verify field names, types, and relationships preserved

**CatalogItem**:
- 12 properties
- 2 navigation properties

**CatalogBrand**:
- 2 properties
- 1 navigation property (collection)

**CatalogType**:
- 2 properties
- 1 navigation property (collection)

---

### 3. Service Interface Contract
**Source**: `Services/ICatalogService.cs`, `Services/CatalogService.cs`
**Purpose**: Ensure migrated service methods match legacy signatures

**Methods**:
- FindCatalogItem(int id)
- GetCatalogItemsPaginated(int pageSize, int pageIndex)
- GetCatalogBrands()
- GetCatalogTypes()
- CreateCatalogItem(CatalogItem)
- UpdateCatalogItem(CatalogItem)
- RemoveCatalogItem(CatalogItem)

---

### 4. Seed Data
**Source**: `Models/Infrastructure/PreconfiguredData.cs`
**Purpose**: Ensure migrated database has identical initial data

**Data Volumes**:
- 5 CatalogBrands (from seed.py)
- 4 CatalogTypes (from seed.py)
- 12 CatalogItems (from seed.py)

---

### 5. Query Patterns
**Source**: `Services/CatalogService.cs` LINQ queries
**Purpose**: Ensure migrated SQLAlchemy queries return equivalent results

**Patterns**:
- SELECT with JOIN (Include() → selectinload())
- SELECT with pagination (Skip/Take → offset/limit)
- INSERT (Add → session.add)
- UPDATE (EntityState.Modified → direct modification)
- DELETE (Remove → session.delete)

---

## Capture Method

**Source**: Direct code analysis + schema inspection
**Files Analyzed**:
- `src/eShopLegacyWebForms/Models/CatalogItem.cs`
- `src/eShopLegacyWebForms/Models/CatalogBrand.cs`
- `src/eShopLegacyWebForms/Models/CatalogType.cs`
- `src/eShopLegacyWebForms/Models/CatalogDBContext.cs`
- `src/eShopLegacyWebForms/Services/ICatalogService.cs`
- `src/eShopLegacyWebForms/Services/CatalogService.cs`
- `backend/app/core/seed.py` (migrated seed data)

---

## What Was Captured (Synthetic Baselines)

1. ✅ **Schema Definition**: Complete table structure with columns, types, constraints
2. ✅ **Entity Models**: All properties and relationships documented
3. ✅ **Service Interface**: All method signatures documented
4. ✅ **Seed Data**: Complete list of initial data (brands, types, items)
5. ✅ **Query Patterns**: LINQ → SQLAlchemy translation documented

---

## What Was NOT Captured (Not Applicable)

1. ❌ **Screenshots**: No UI (this is infrastructure code)
2. ❌ **User Workflows**: No user interaction (this is library code)
3. ❌ **HTTP Requests/Responses**: No API endpoints (internal service layer)
4. ❌ **Database Snapshots**: Seed data is sufficient (schema is deterministic)

---

## Validation Strategy

### Schema Parity
- Compare legacy EF6 model annotations → SQLAlchemy column definitions
- Verify column names match exactly (case-sensitive)
- Verify data types match (VARCHAR, NUMERIC, INTEGER, BOOLEAN)
- Verify foreign key constraints match

### Query Parity
- Execute same query in both systems
- Compare result sets (row count, field values, ordering)
- Verify JOIN behavior matches (INNER vs LEFT JOIN)
- Verify pagination produces same results

### Service Parity
- Call each service method with identical inputs
- Compare outputs (entity properties, counts, ordering)
- Verify exceptions/errors match

---

## Validation Test Cases

### Entity Model Validation
- [ ] CatalogItem model has all 12 properties with correct types
- [ ] CatalogBrand model has 2 properties
- [ ] CatalogType model has 2 properties
- [ ] Foreign key relationships defined correctly
- [ ] Navigation properties load correctly (no N+1 queries)

### Service Method Validation
- [ ] FindCatalogItem(1) returns product with brand and type loaded
- [ ] GetCatalogItemsPaginated(10, 0) returns first 10 items
- [ ] GetCatalogBrands() returns 5 brands
- [ ] GetCatalogTypes() returns 4 types
- [ ] CreateCatalogItem inserts new row and returns ID
- [ ] UpdateCatalogItem modifies existing row
- [ ] RemoveCatalogItem deletes row

### Seed Data Validation
- [ ] Database contains exactly 5 brands (`.NET`, `Other`, `Azure`, `Visual Studio`, `SQL Server`)
- [ ] Database contains exactly 4 types (`Mug`, `T-Shirt`, `Sheet`, `USB Memory Stick`)
- [ ] Database contains 12 catalog items with correct prices
- [ ] Product 1 is ".NET Bot Black Hoodie" with price $19.50

---

## Files to Export

### Schema Export
**File**: `exports/synthetic_schema.json`
**Content**: Complete schema definition (tables, columns, constraints)

### Entity Models Export
**File**: `exports/synthetic_entity_models.json`
**Content**: All entity properties, types, relationships

### Service Interface Export
**File**: `exports/synthetic_service_interface.json`
**Content**: All method signatures with parameters and return types

### Seed Data Export
**File**: (Already exists) `backend/app/core/seed.py`
**Content**: Initial data for brands, types, items

---

## Limitations

**No Runtime Behavior Capture**: Cannot capture actual database queries, execution plans, or performance metrics without running the legacy app.

**No Connection String Capture**: Connection strings are environment-specific (localhost, credentials).

**No Transaction Behavior Capture**: Cannot verify transaction isolation levels or concurrency behavior without runtime testing.

---

## Notes

- **Complexity**: MEDIUM (infrastructure code, no UI)
- **Risk**: MEDIUM (foundational - errors impact all other seams)
- **Testing**: Unit tests + integration tests required
- **Priority**: HIGH (must complete before other seams can be validated)

---

**Capture Method**: SYNTHETIC (code analysis)
**Capture Date**: 2026-03-02
**Capture Status**: READY TO EXECUTE
