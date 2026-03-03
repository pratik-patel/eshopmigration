# Database Access Patterns

## Overview

The legacy eShop application uses **Entity Framework 6** with SQL Server LocalDB for data persistence.

## Database Configuration

**Connection String** (Web.config:12):
```
Data Source=(localdb)\MSSQLLocalDB;
Initial Catalog=Microsoft.eShopOnContainers.Services.CatalogDb;
Integrated Security=True;
MultipleActiveResultSets=True;
```

**Database Name**: `Microsoft.eShopOnContainers.Services.CatalogDb`

**Provider**: System.Data.SqlClient (SQL Server)

## DbContext

**Class**: `CatalogDBContext`
**Location**: `Models/CatalogDBContext.cs`

**DbSets**:
- `CatalogItems` → CatalogItem entity
- `CatalogBrands` → CatalogBrand entity
- `CatalogTypes` → CatalogType entity

## Entity Models

### 1. CatalogItem

**Table**: CatalogItems

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| Id | int | PRIMARY KEY, IDENTITY | Generated via HiLo pattern |
| Name | nvarchar(max) | NOT NULL | |
| Description | nvarchar(max) | | |
| Price | decimal(18,2) | NOT NULL | Range: 0-9999999999999999.99 |
| PictureFileName | nvarchar(max) | Default: 'dummy.png' | |
| PictureUri | nvarchar(max) | | |
| CatalogTypeId | int | FOREIGN KEY → CatalogTypes(Id) | |
| CatalogBrandId | int | FOREIGN KEY → CatalogBrands(Id) | |
| AvailableStock | int | NOT NULL | Range: 0-10000000 |
| RestockThreshold | int | NOT NULL | Range: 0-10000000 |
| MaxStockThreshold | int | NOT NULL | Range: 0-10000000 |
| OnReorder | bit | NOT NULL | Default: FALSE |

**Relationships**:
- Many-to-One with CatalogType (via CatalogTypeId)
- Many-to-One with CatalogBrand (via CatalogBrandId)

### 2. CatalogBrand

**Table**: CatalogBrands

| Column | Type | Constraints |
|--------|------|-------------|
| Id | int | PRIMARY KEY, IDENTITY |
| Brand | nvarchar(max) | NOT NULL |

### 3. CatalogType

**Table**: CatalogTypes

| Column | Type | Constraints |
|--------|------|-------------|
| Id | int | PRIMARY KEY, IDENTITY |
| Type | nvarchar(max) | NOT NULL |

## Service Layer Data Access

**Interface**: `ICatalogService`
**Implementations**:
- `CatalogService` (real DB access via EF)
- `CatalogServiceMock` (in-memory mock data)

### Data Access Methods

1. **FindCatalogItem(int id)**
   - Operation: SELECT with JOIN
   - Returns: Single CatalogItem with navigation properties (Brand, Type)
   - Usage: Details, Edit, Delete pages

2. **GetCatalogItemsPaginated(int pageSize, int pageIndex)**
   - Operation: SELECT with JOIN, SKIP/TAKE (pagination)
   - Returns: PaginatedItemsViewModel<CatalogItem>
   - Usage: Default.aspx list page
   - Default pageSize: 10

3. **GetCatalogBrands()**
   - Operation: SELECT all from CatalogBrands
   - Returns: IEnumerable<CatalogBrand>
   - Usage: Populate dropdown in Create/Edit forms

4. **GetCatalogTypes()**
   - Operation: SELECT all from CatalogTypes
   - Returns: IEnumerable<CatalogType>
   - Usage: Populate dropdown in Create/Edit forms

5. **CreateCatalogItem(CatalogItem)**
   - Operation: INSERT into CatalogItems
   - ID Generation: HiLo pattern via CatalogItemHiLoGenerator
   - Usage: Create.aspx

6. **UpdateCatalogItem(CatalogItem)**
   - Operation: UPDATE CatalogItems WHERE Id = {id}
   - Usage: Edit.aspx

7. **RemoveCatalogItem(CatalogItem)**
   - Operation: DELETE FROM CatalogItems WHERE Id = {id}
   - Usage: Delete.aspx

## Query Patterns

### List Query (with pagination)
```csharp
// Simplified pseudo-code from CatalogService
var items = dbContext.CatalogItems
    .Include(c => c.CatalogBrand)
    .Include(c => c.CatalogType)
    .OrderBy(c => c.Name)
    .Skip(pageIndex * pageSize)
    .Take(pageSize)
    .ToList();
```

**Migration Target** (Python/SQLAlchemy):
```python
async def get_catalog_items_paginated(
    session: AsyncSession,
    page_size: int,
    page_index: int
) -> PaginatedItemsViewModel:
    stmt = (
        select(CatalogItem)
        .options(
            selectinload(CatalogItem.catalog_brand),
            selectinload(CatalogItem.catalog_type)
        )
        .order_by(CatalogItem.name)
        .offset(page_index * page_size)
        .limit(page_size)
    )
    result = await session.execute(stmt)
    items = result.scalars().all()
    # ...
```

### Single Item Query
```csharp
var item = dbContext.CatalogItems
    .Include(c => c.CatalogBrand)
    .Include(c => c.CatalogType)
    .FirstOrDefault(c => c.Id == id);
```

**Migration Target**:
```python
async def find_catalog_item(
    session: AsyncSession,
    item_id: int
) -> CatalogItem | None:
    stmt = (
        select(CatalogItem)
        .options(
            selectinload(CatalogItem.catalog_brand),
            selectinload(CatalogItem.catalog_type)
        )
        .where(CatalogItem.id == item_id)
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()
```

## Database Initialization & Seeding

**Initializer**: `CatalogDBInitializer` (Database.SetInitializer pattern)
**Seed Data**: `PreconfiguredData` class

**Seed Data Includes**:
- 10 CatalogTypes (.NET, Java, Node, SQL, NoSQL, etc.)
- 10 CatalogBrands (Microsoft, Xamarin, Azure, etc.)
- ~14 CatalogItems (courses/products for an e-learning catalog)

**Migration Strategy**:
- Use Alembic migrations for schema
- Create seed data script or migration to populate initial data
- Preserve same seed data from PreconfiguredData.cs

## HiLo ID Generation

**Class**: `CatalogItemHiLoGenerator`
**Pattern**: Hi/Lo algorithm for efficient ID generation

**Purpose**: Avoid database round-trips for ID generation by using a "high" value from DB and "low" value generated in-memory.

**Migration Consideration**:
- Modern databases (including SQLite) have auto-increment
- Can simplify to auto-increment in migration unless high-throughput ID generation is needed
- If preserving HiLo, implement Python equivalent

## Transaction Patterns

Entity Framework 6 uses **implicit transactions** for SaveChanges().

**Migration Target**:
- Use SQLAlchemy `async with session.begin()` for explicit transactions
- FastAPI route handlers get scoped session via Depends()

## Mock Data Mode

**Configuration**: `UseMockData=true` in Web.config

When enabled, application uses `CatalogServiceMock` which returns hardcoded in-memory data instead of database queries.

**Migration Target**:
- Create mock service implementation following same interface
- Use DI factory pattern to switch between real and mock based on config
- Defined in `backend/app/dependencies.py` get_catalog_service()

## Migration Summary

| Legacy (EF6) | Target (SQLAlchemy 2.x) |
|--------------|-------------------------|
| DbContext | AsyncSession |
| Include() | selectinload(), joinedload() |
| FirstOrDefault() | scalar_one_or_none() |
| ToList() | scalars().all() |
| SaveChanges() | session.commit() |
| IDisposable | async context manager |
| Skip/Take | offset/limit |
| LINQ queries | SQLAlchemy select() API |

**Key Differences**:
- All operations are `async` in Python
- No lazy loading - use explicit eager loading with selectinload()
- Transaction management via `async with session.begin()`
- Connection pooling configured at engine level
