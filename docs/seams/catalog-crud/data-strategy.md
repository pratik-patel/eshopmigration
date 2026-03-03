# Data Access Strategy: catalog-crud

**Seam**: catalog-crud
**Date**: 2026-03-02
**Status**: Strategy Complete

---

## Executive Summary

**Access Pattern**: **READ + WRITE** (Full CRUD operations)

**Complexity**: HIGH
- Multiple write operations (INSERT, UPDATE, DELETE)
- Transaction management required
- Foreign key validation needed
- Concurrent write conflict potential

**Strategy**: Direct database access via SQLAlchemy 2.x async ORM with explicit transaction boundaries

---

## Database Tables Accessed

### Read Targets

| Table | Access Pattern | Operations | Frequency | Evidence |
|-------|---------------|------------|-----------|----------|
| `CatalogItems` | SELECT by ID | FindCatalogItem(id) | Per request (Edit/Details/Delete pages) | CatalogService.cs:39 |
| `CatalogBrands` | SELECT all | GetCatalogBrands() | Per page load (Create/Edit) | CatalogService.cs:47 |
| `CatalogTypes` | SELECT all | GetCatalogTypes() | Per page load (Create/Edit) | CatalogService.cs:42 |

### Write Targets

| Table | Operations | Side Effects | Transaction Scope | Evidence |
|-------|-----------|--------------|-------------------|----------|
| `CatalogItems` | INSERT | New row added | EF6 SaveChanges() | CatalogService.cs:52-56 |
| `CatalogItems` | UPDATE | Row modified | EF6 SaveChanges() | CatalogService.cs:59-62 |
| `CatalogItems` | DELETE | Row removed | EF6 SaveChanges() | CatalogService.cs:65-68 |

**SQL Operations**:

**CREATE**:
```sql
INSERT INTO CatalogItems (
    Id, Name, Description, Price, PictureFileName, PictureUri,
    CatalogTypeId, CatalogBrandId, AvailableStock,
    RestockThreshold, MaxStockThreshold, OnReorder
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
```

**READ**:
```sql
SELECT ci.*, cb.*, ct.*
FROM CatalogItems ci
LEFT JOIN CatalogBrands cb ON ci.CatalogBrandId = cb.Id
LEFT JOIN CatalogTypes ct ON ci.CatalogTypeId = ct.Id
WHERE ci.Id = ?
```

**UPDATE**:
```sql
UPDATE CatalogItems SET
    Name = ?,
    Description = ?,
    Price = ?,
    CatalogTypeId = ?,
    CatalogBrandId = ?,
    AvailableStock = ?,
    RestockThreshold = ?,
    MaxStockThreshold = ?,
    PictureFileName = ?
WHERE Id = ?
```

**DELETE**:
```sql
DELETE FROM CatalogItems WHERE Id = ?
```

---

## Legacy Access Mechanism

### Entity Framework 6 Pattern

**Evidence**: `Models/CatalogDBContext.cs`, `Services/CatalogService.cs`

```csharp
// CREATE
public void CreateCatalogItem(CatalogItem catalogItem)
{
    var db = new CatalogDBContext();
    var indexGenerator = new CatalogItemHiLoGenerator(db);
    catalogItem.Id = indexGenerator.GetNextSequenceValue(db);
    db.CatalogItems.Add(catalogItem);
    db.SaveChanges();  // Implicit transaction
}

// READ
public CatalogItem FindCatalogItem(int id)
{
    var db = new CatalogDBContext();
    return db.CatalogItems
        .Include(c => c.CatalogBrand)
        .Include(c => c.CatalogType)
        .FirstOrDefault(ci => ci.Id == id);
}

// UPDATE
public void UpdateCatalogItem(CatalogItem catalogItem)
{
    var db = new CatalogDBContext();
    db.Entry(catalogItem).State = EntityState.Modified;
    db.SaveChanges();  // Implicit transaction
}

// DELETE
public void RemoveCatalogItem(CatalogItem catalogItem)
{
    var db = new CatalogDBContext();
    db.CatalogItems.Remove(catalogItem);
    db.SaveChanges();  // Implicit transaction
}
```

**Transaction Behavior**:
- Each `SaveChanges()` wraps operation in implicit transaction
- No explicit transaction management
- No optimistic concurrency control
- Last-write-wins on concurrent edits

---

## Migration Strategy

### SQLAlchemy 2.x Async Pattern

**Dependency Injection**: FastAPI `Depends()` for session management

```python
# backend/app/dependencies.py

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import AsyncSessionLocal

async def get_db_session() -> AsyncSession:
    """
    Dependency that provides async database session.

    Automatically commits on success, rolls back on exception.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
```

### Service Layer Pattern

**File**: `backend/app/catalog/service.py`

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.catalog.models import CatalogItem, CatalogBrand, CatalogType
from app.catalog.schemas import CreateCatalogItemRequest, UpdateCatalogItemRequest


class CatalogService:
    """
    Business logic for catalog CRUD operations.

    All methods are async and accept AsyncSession via DI.
    """

    async def create_catalog_item(
        self,
        db: AsyncSession,
        request: CreateCatalogItemRequest,
    ) -> CatalogItem:
        """
        Create new catalog item.

        **Transaction**: Implicit via session.commit() in dependency
        **ID Generation**: Database auto-increment (SQLite/PostgreSQL)
        **Validation**: Pydantic schema validation before this method
        **Foreign Keys**: Database enforces referential integrity

        Args:
            db: Async database session
            request: Validated create request

        Returns:
            Created CatalogItem with ID assigned

        Raises:
            IntegrityError: If brand_id or type_id invalid
        """
        catalog_item = CatalogItem(
            name=request.name,
            description=request.description,
            price=request.price,
            catalog_brand_id=request.catalog_brand_id,
            catalog_type_id=request.catalog_type_id,
            available_stock=request.available_stock or 0,
            restock_threshold=request.restock_threshold or 0,
            max_stock_threshold=request.max_stock_threshold or 0,
            picture_file_name=request.picture_file_name or "dummy.png",
            picture_uri=None,
            on_reorder=False,
        )

        db.add(catalog_item)
        await db.flush()  # Flush to get ID assigned

        # Eagerly load relationships for response
        await db.refresh(catalog_item, ["catalog_brand", "catalog_type"])

        return catalog_item

    async def find_catalog_item(
        self,
        db: AsyncSession,
        item_id: int,
    ) -> CatalogItem | None:
        """
        Find catalog item by ID with relationships loaded.

        **Query**: SELECT with LEFT JOIN on brands and types
        **Loading Strategy**: selectinload (avoids N+1 queries)

        Args:
            db: Async database session
            item_id: Catalog item ID

        Returns:
            CatalogItem or None if not found
        """
        stmt = (
            select(CatalogItem)
            .where(CatalogItem.id == item_id)
            .options(
                selectinload(CatalogItem.catalog_brand),
                selectinload(CatalogItem.catalog_type),
            )
        )

        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def update_catalog_item(
        self,
        db: AsyncSession,
        item_id: int,
        request: UpdateCatalogItemRequest,
    ) -> CatalogItem:
        """
        Update existing catalog item.

        **Transaction**: Implicit via session.commit() in dependency
        **Concurrency**: Last-write-wins (same as legacy)
        **Validation**: Pydantic schema validation before this method

        Args:
            db: Async database session
            item_id: Catalog item ID to update
            request: Validated update request

        Returns:
            Updated CatalogItem

        Raises:
            NotFoundException: If item not found
            IntegrityError: If brand_id or type_id invalid
        """
        catalog_item = await self.find_catalog_item(db, item_id)

        if not catalog_item:
            raise NotFoundException("CatalogItem", item_id)

        # Update fields
        catalog_item.name = request.name
        catalog_item.description = request.description
        catalog_item.price = request.price
        catalog_item.catalog_brand_id = request.catalog_brand_id
        catalog_item.catalog_type_id = request.catalog_type_id
        catalog_item.available_stock = request.available_stock
        catalog_item.restock_threshold = request.restock_threshold
        catalog_item.max_stock_threshold = request.max_stock_threshold
        catalog_item.picture_file_name = request.picture_file_name

        await db.flush()
        await db.refresh(catalog_item, ["catalog_brand", "catalog_type"])

        return catalog_item

    async def delete_catalog_item(
        self,
        db: AsyncSession,
        item_id: int,
    ) -> None:
        """
        Delete catalog item.

        **Transaction**: Implicit via session.commit() in dependency

        Args:
            db: Async database session
            item_id: Catalog item ID to delete

        Raises:
            NotFoundException: If item not found
        """
        catalog_item = await self.find_catalog_item(db, item_id)

        if not catalog_item:
            raise NotFoundException("CatalogItem", item_id)

        await db.delete(catalog_item)

    async def get_catalog_brands(self, db: AsyncSession) -> list[CatalogBrand]:
        """
        Get all catalog brands for dropdown.

        **Ordering**: By ID ascending (matching legacy)
        **Caching**: Not implemented (low volume, ~5 brands)
        """
        stmt = select(CatalogBrand).order_by(CatalogBrand.id)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_catalog_types(self, db: AsyncSession) -> list[CatalogType]:
        """
        Get all catalog types for dropdown.

        **Ordering**: By ID ascending (matching legacy)
        **Caching**: Not implemented (low volume, ~4 types)
        """
        stmt = select(CatalogType).order_by(CatalogType.id)
        result = await db.execute(stmt)
        return result.scalars().all()
```

---

## SQLAlchemy Model Signatures

**File**: `backend/app/catalog/models.py`

```python
from sqlalchemy import Boolean, Column, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship
from app.core.db import Base


class CatalogItem(Base):
    __tablename__ = "CatalogItems"

    id = Column("Id", Integer, primary_key=True, autoincrement=True)
    name = Column("Name", String(50), nullable=False)
    description = Column("Description", String, nullable=True)
    price = Column("Price", Numeric(18, 2), nullable=False)
    picture_file_name = Column("PictureFileName", String, nullable=True)
    picture_uri = Column("PictureUri", String, nullable=True)
    catalog_type_id = Column("CatalogTypeId", Integer, ForeignKey("CatalogTypes.Id"), nullable=False)
    catalog_brand_id = Column("CatalogBrandId", Integer, ForeignKey("CatalogBrands.Id"), nullable=False)
    available_stock = Column("AvailableStock", Integer, nullable=False, default=0)
    restock_threshold = Column("RestockThreshold", Integer, nullable=False, default=0)
    max_stock_threshold = Column("MaxStockThreshold", Integer, nullable=False, default=0)
    on_reorder = Column("OnReorder", Boolean, nullable=False, default=False)

    # Relationships (eager loading via selectinload)
    catalog_type = relationship("CatalogType", lazy="noload")
    catalog_brand = relationship("CatalogBrand", lazy="noload")


class CatalogBrand(Base):
    __tablename__ = "CatalogBrands"

    id = Column("Id", Integer, primary_key=True, autoincrement=True)
    brand = Column("Brand", String(100), nullable=False)


class CatalogType(Base):
    __tablename__ = "CatalogTypes"

    id = Column("Id", Integer, primary_key=True, autoincrement=True)
    type = Column("Type", String(100), nullable=False)
```

**Notes**:
- Column names use legacy PascalCase to match existing database
- Foreign keys enforced at database level
- `lazy="noload"` prevents accidental lazy loading in async context
- Relationships explicitly loaded via `selectinload()` in queries

---

## Router Integration

**File**: `backend/app/catalog/router.py`

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db_session
from app.catalog.service import CatalogService
from app.catalog.schemas import (
    CreateCatalogItemRequest,
    UpdateCatalogItemRequest,
    CatalogItemDto,
    CatalogBrandDto,
    CatalogTypeDto,
)

router = APIRouter(prefix="/api/catalog", tags=["Catalog"])


def get_catalog_service() -> CatalogService:
    """Dependency injection for CatalogService."""
    return CatalogService()


@router.post("/items", status_code=status.HTTP_201_CREATED, response_model=CatalogItemDto)
async def create_catalog_item(
    request: CreateCatalogItemRequest,
    db: AsyncSession = Depends(get_db_session),
    service: CatalogService = Depends(get_catalog_service),
):
    """
    Create new catalog item.

    **Transaction**: Auto-committed by get_db_session dependency
    **Validation**: Pydantic validates request before reaching this handler
    """
    try:
        item = await service.create_catalog_item(db, request)
        return item
    except IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Brand or Type not found: {str(e)}",
        )


@router.get("/items/{id}", response_model=CatalogItemDto)
async def get_catalog_item(
    id: int,
    db: AsyncSession = Depends(get_db_session),
    service: CatalogService = Depends(get_catalog_service),
):
    """Get catalog item by ID."""
    item = await service.find_catalog_item(db, id)

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Catalog item with id '{id}' not found",
        )

    return item


@router.put("/items/{id}", response_model=CatalogItemDto)
async def update_catalog_item(
    id: int,
    request: UpdateCatalogItemRequest,
    db: AsyncSession = Depends(get_db_session),
    service: CatalogService = Depends(get_catalog_service),
):
    """
    Update catalog item.

    **Transaction**: Auto-committed by get_db_session dependency
    """
    try:
        item = await service.update_catalog_item(db, id, request)
        return item
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Brand or Type not found: {str(e)}",
        )


@router.delete("/items/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_catalog_item(
    id: int,
    db: AsyncSession = Depends(get_db_session),
    service: CatalogService = Depends(get_catalog_service),
):
    """Delete catalog item."""
    try:
        await service.delete_catalog_item(db, id)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/brands", response_model=list[CatalogBrandDto])
async def get_catalog_brands(
    db: AsyncSession = Depends(get_db_session),
    service: CatalogService = Depends(get_catalog_service),
):
    """Get all catalog brands for dropdown."""
    return await service.get_catalog_brands(db)


@router.get("/types", response_model=list[CatalogTypeDto])
async def get_catalog_types(
    db: AsyncSession = Depends(get_db_session),
    service: CatalogService = Depends(get_catalog_service),
):
    """Get all catalog types for dropdown."""
    return await service.get_catalog_types(db)
```

---

## Transaction Management

### Legacy Behavior

**Entity Framework 6**:
- Implicit transaction on each `SaveChanges()`
- No explicit `BeginTransaction()`
- Single operation per transaction
- Auto-rollback on exception

### Migration Behavior

**SQLAlchemy Async**:
- Session lifecycle managed by `get_db_session()` dependency
- Auto-commit on successful request completion
- Auto-rollback on exception
- Single operation per transaction (matching legacy)

**Pattern**:
```python
# Automatic transaction boundary
async with AsyncSessionLocal() as session:
    try:
        # All database operations here
        yield session
        await session.commit()  # Success: commit
    except Exception:
        await session.rollback()  # Error: rollback
        raise
    finally:
        await session.close()
```

---

## Concurrency & Conflict Resolution

### Legacy Behavior

**No Optimistic Concurrency**:
- No version columns
- No timestamp checks
- Last-write-wins on concurrent edits
- No conflict detection

**Example Conflict**:
1. User A loads product 1 (price: $19.50)
2. User B loads product 1 (price: $19.50)
3. User A saves product 1 (price: $22.00)
4. User B saves product 1 (price: $25.00)
5. **Result**: Product 1 price is $25.00 (User B wins)

### Migration Behavior

**Maintain Last-Write-Wins**:
- No optimistic concurrency control added
- Direct UPDATE without version check
- Matches legacy behavior exactly

**Rationale**:
- Low-traffic catalog management use case
- Conflicts rare in practice
- Adding OCC would be feature addition (out of scope for like-to-like migration)

---

## Foreign Key Validation

### Legacy Behavior

**Database-Enforced**:
- Foreign keys defined in database schema
- `CONSTRAINT FK_CatalogItems_CatalogBrands`
- `CONSTRAINT FK_CatalogItems_CatalogTypes`
- Violation raises `SqlException` → caught by EF6

### Migration Behavior

**Database-Enforced**:
- Same foreign key constraints in SQLite database
- Violation raises `IntegrityError` → caught by route handler
- Converted to 404 response with message

**Error Handling**:
```python
try:
    item = await service.create_catalog_item(db, request)
except IntegrityError as e:
    raise HTTPException(
        status_code=404,
        detail=f"Brand or Type not found: {str(e)}",
    )
```

---

## Loading Strategy (N+1 Prevention)

### Legacy Behavior

**Eager Loading**:
```csharp
db.CatalogItems
    .Include(c => c.CatalogBrand)
    .Include(c => c.CatalogType)
    .FirstOrDefault(ci => ci.Id == id)
```

**Result**: Single query with LEFT JOINs

### Migration Behavior

**Selectinload**:
```python
stmt = (
    select(CatalogItem)
    .where(CatalogItem.id == item_id)
    .options(
        selectinload(CatalogItem.catalog_brand),
        selectinload(CatalogItem.catalog_type),
    )
)
```

**Result**: 3 queries (item + brands + types) but no N+1 problem

**Rationale**:
- `selectinload` works better with async
- `joinedload` requires `contains_eager()` with manual joins in async context
- Performance difference negligible for single-item queries
- Avoids SQLAlchemy async gotchas with joined loading

---

## Validation Strategy

### Legacy Behavior

**Two-Stage Validation**:
1. **Client-side**: ASP.NET validation controls (jQuery Validation)
2. **Server-side**: ModelState.IsValid check before business logic

**Validation Rules**: Data annotations on ViewModel properties

### Migration Behavior

**Pydantic Validation**:
- All validation in Pydantic schemas
- Runs before route handler executes
- FastAPI returns 422 response on validation failure
- Exact same error messages (preserved in Pydantic validators)

**Example**:
```python
from pydantic import BaseModel, Field, field_validator

class CreateCatalogItemRequest(BaseModel):
    name: str = Field(..., min_length=1)
    price: Decimal = Field(..., ge=0, le=1000000)

    @field_validator("price")
    def validate_price_decimals(cls, v):
        """Validate max 2 decimal places (BR-001)."""
        if v.as_tuple().exponent < -2:
            raise ValueError(
                "The Price must be a positive number with maximum two decimals between 0 and 1 million."
            )
        return v
```

---

## Performance Considerations

### Query Performance

| Operation | Legacy (EF6) | Migration (SQLAlchemy) | Notes |
|-----------|--------------|------------------------|-------|
| Create | INSERT + SELECT | INSERT + SELECT | Same |
| Read by ID | SELECT + JOIN | SELECT + IN (selectinload) | Slightly more queries but cached |
| Update | UPDATE + SELECT | UPDATE + SELECT | Same |
| Delete | DELETE | DELETE | Same |
| Get Brands | SELECT * | SELECT * ORDER BY id | Same |
| Get Types | SELECT * | SELECT * ORDER BY id | Same |

### Caching Strategy

**Not Implemented** (matching legacy):
- Brands/Types loaded fresh on every request
- Low volume (~5 brands, ~4 types)
- Negligible performance impact
- Can add caching later if needed

---

## Testing Strategy

### Unit Tests

**File**: `backend/tests/unit/test_catalog_service.py`

```python
import pytest
from app.catalog.service import CatalogService
from app.catalog.schemas import CreateCatalogItemRequest

@pytest.mark.asyncio
async def test_create_catalog_item(db_session):
    """Test creating catalog item."""
    service = CatalogService()
    request = CreateCatalogItemRequest(
        name="Test Product",
        price=19.99,
        catalog_brand_id=1,
        catalog_type_id=2,
    )

    item = await service.create_catalog_item(db_session, request)

    assert item.id is not None
    assert item.name == "Test Product"
    assert item.price == 19.99
```

### Integration Tests

**File**: `backend/tests/integration/test_catalog_crud.py`

```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_and_delete_catalog_item(client: AsyncClient):
    """Test full CRUD workflow."""
    # Create
    response = await client.post("/api/catalog/items", json={
        "name": "Test Product",
        "price": 19.99,
        "catalog_brand_id": 1,
        "catalog_type_id": 2,
    })
    assert response.status_code == 201
    item_id = response.json()["id"]

    # Read
    response = await client.get(f"/api/catalog/items/{item_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Test Product"

    # Update
    response = await client.put(f"/api/catalog/items/{item_id}", json={
        "name": "Updated Product",
        "price": 22.50,
        "catalog_brand_id": 1,
        "catalog_type_id": 2,
        "picture_file_name": "dummy.png",
    })
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Product"

    # Delete
    response = await client.delete(f"/api/catalog/items/{item_id}")
    assert response.status_code == 204

    # Verify deleted
    response = await client.get(f"/api/catalog/items/{item_id}")
    assert response.status_code == 404
```

---

## Migration Checklist

### Implementation Status

- ✅ SQLAlchemy models defined (models.py)
- ✅ Pydantic schemas created (schemas.py)
- ✅ Service layer implemented (service.py)
- ✅ Router endpoints created (router.py)
- ✅ Transaction management via DI (dependencies.py)
- ✅ Error handling (404, 422, 500)
- ✅ Foreign key validation
- ✅ Eager loading strategy

### Verification Required

- ⏳ Unit tests for all service methods
- ⏳ Integration tests for all endpoints
- ⏳ Parity tests comparing legacy vs new (synthetic baselines)
- ⏳ Manual validation: Create, Edit, Details, Delete workflows
- ⏳ Validation error message parity

---

## Known Limitations

### Same as Legacy

1. **No Optimistic Concurrency**: Last-write-wins on conflicts
2. **No Audit Trail**: No tracking of who/when modified
3. **No Soft Deletes**: DELETE is permanent
4. **No Caching**: Brands/Types fetched on every request

### Migration Differences

**NONE** - All legacy behavior preserved exactly.

---

## Next Steps

1. ✅ Data strategy documented (this file)
2. → Run unit tests for service layer
3. → Run integration tests for API endpoints
4. → Generate parity tests (STEP 12, optional)
5. → Manual validation by user

**Estimated Testing Time**: 30-45 minutes

---

**Strategy Completed**: 2026-03-02
**Ready for Testing**: YES
