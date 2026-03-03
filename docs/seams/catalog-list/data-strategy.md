# Data Strategy: catalog-list

**Seam ID**: catalog-list
**Date**: 2026-03-02
**Strategy**: READ-ONLY
**Status**: Approved

---

## Strategy Selection

**Chosen Strategy**: **Read-Only**

**Rationale**:
- This seam performs only SELECT queries
- No INSERT, UPDATE, or DELETE operations
- No transaction management needed
- No data modification side effects
- Lowest risk strategy

**Alternative Strategies Considered**:
- ❌ Direct Write: Not applicable (no writes)
- ❌ New Tables: Not applicable (uses existing tables)

---

## Database Access Pattern

### Tables Accessed

| Table | Operations | Access Pattern | Evidence |
|-------|-----------|----------------|----------|
| **CatalogItems** | SELECT, COUNT | Direct query with OFFSET/LIMIT | CatalogService.cs:24-32 |
| **CatalogBrands** | SELECT | INNER JOIN via navigation property | CatalogService.cs:27 |
| **CatalogTypes** | SELECT | INNER JOIN via navigation property | CatalogService.cs:28 |

### Query Strategy

**Primary Query**:
```sql
-- Count total items
SELECT COUNT(*) FROM CatalogItems;

-- Fetch paginated items with joins
SELECT
    CatalogItems.*,
    CatalogBrands.Id AS Brand_Id,
    CatalogBrands.Brand AS Brand_Name,
    CatalogTypes.Id AS Type_Id,
    CatalogTypes.Type AS Type_Name
FROM CatalogItems
INNER JOIN CatalogBrands ON CatalogItems.CatalogBrandId = CatalogBrands.Id
INNER JOIN CatalogTypes ON CatalogItems.CatalogTypeId = CatalogTypes.Id
ORDER BY CatalogItems.Id ASC
OFFSET (@page_size * @page_index) ROWS
FETCH NEXT @page_size ROWS ONLY;
```

**Ordering**: Always ORDER BY Id ASC (hardcoded, no user control)

**Pagination**: OFFSET/LIMIT pattern

---

## SQLAlchemy Implementation

### Model Definitions

**Already Implemented**: `backend/app/core/models.py`

```python
class CatalogItem(Base):
    __tablename__ = "catalog_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    price: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    picture_file_name: Mapped[str] = mapped_column(String, nullable=False, default="dummy.png")
    picture_uri: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    catalog_type_id: Mapped[int] = mapped_column(Integer, ForeignKey("catalog_types.id"))
    catalog_brand_id: Mapped[int] = mapped_column(Integer, ForeignKey("catalog_brands.id"))
    available_stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    restock_threshold: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_stock_threshold: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    on_reorder: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Navigation properties (relationships)
    catalog_type: Mapped["CatalogType"] = relationship(back_populates="catalog_items")
    catalog_brand: Mapped["CatalogBrand"] = relationship(back_populates="catalog_items")


class CatalogBrand(Base):
    __tablename__ = "catalog_brands"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    brand: Mapped[str] = mapped_column(String, nullable=False)

    catalog_items: Mapped[List["CatalogItem"]] = relationship(back_populates="catalog_brand")


class CatalogType(Base):
    __tablename__ = "catalog_types"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type: Mapped[str] = mapped_column(String, nullable=False)

    catalog_items: Mapped[List["CatalogItem"]] = relationship(back_populates="catalog_type")
```

---

## Service Layer Signature

**Already Implemented**: `backend/app/core/service.py`

```python
class ICatalogService(ABC):
    """Catalog service interface."""

    @abstractmethod
    async def get_catalog_items_paginated(
        self,
        page_size: int,
        page_index: int
    ) -> PaginatedItemsViewModel:
        """Get paginated catalog items with brand and type."""
        pass


class CatalogService(ICatalogService):
    """Real database implementation."""

    async def get_catalog_items_paginated(
        self,
        page_size: int,
        page_index: int
    ) -> PaginatedItemsViewModel:
        """
        Get paginated catalog items.

        Eager loads:
        - CatalogBrand (navigation property)
        - CatalogType (navigation property)

        Orders by: Id ASC

        Returns:
        - PaginatedItemsViewModel with metadata and data
        """
        # Count total items
        total_items = await self.session.scalar(
            select(func.count(CatalogItem.id))
        )

        # Fetch paginated items with eager loading
        query = (
            select(CatalogItem)
            .options(
                joinedload(CatalogItem.catalog_brand),
                joinedload(CatalogItem.catalog_type)
            )
            .order_by(CatalogItem.id.asc())
            .offset(page_size * page_index)
            .limit(page_size)
        )

        result = await self.session.execute(query)
        items = result.scalars().all()

        return PaginatedItemsViewModel(
            page_index=page_index,
            page_size=page_size,
            total_items=total_items,
            data=items
        )
```

---

## Eager Loading Strategy

**Required**: Navigation properties MUST be eager-loaded to avoid N+1 queries.

**Legacy Behavior** (Entity Framework 6):
```csharp
db.CatalogItems
    .Include(c => c.CatalogBrand)  // Eager load
    .Include(c => c.CatalogType)   // Eager load
    .OrderBy(c => c.Id)
    .Skip(pageSize * pageIndex)
    .Take(pageSize)
    .ToList();
```

**SQLAlchemy Equivalent**:
```python
select(CatalogItem)
    .options(
        joinedload(CatalogItem.catalog_brand),  # Eager load
        joinedload(CatalogItem.catalog_type)    # Eager load
    )
    .order_by(CatalogItem.id.asc())
    .offset(page_size * page_index)
    .limit(page_size)
```

**Why Eager Loading?**:
- Frontend needs brand name and type name in every row
- Without eager loading: N additional queries (N = number of items per page)
- With eager loading: 1 query with JOINs (optimal)

---

## Transaction Scope

**None Required**

- All operations are read-only
- No BEGIN TRANSACTION / COMMIT needed
- No rollback scenarios
- No data consistency concerns

---

## Concurrency Handling

**Read Committed Isolation** (default)

- Read operations do not block writes
- Writes do not block reads
- No explicit locking needed
- Eventual consistency acceptable (catalog list can show slightly stale data)

**Note**: Since this seam is read-only, there are no write conflicts or race conditions to handle.

---

## Error Handling

### Database Connection Errors

```python
try:
    result = await self.get_catalog_items_paginated(page_size, page_index)
except OperationalError as e:
    logger.error("database.connection_failed", error=str(e))
    raise HTTPException(
        status_code=503,
        detail="Database unavailable"
    )
```

### Query Errors

```python
try:
    result = await session.execute(query)
except DatabaseError as e:
    logger.error("database.query_failed", error=str(e))
    raise HTTPException(
        status_code=500,
        detail="Query execution failed"
    )
```

### Empty Results

```python
# Not an error - return empty data array
if total_items == 0:
    return PaginatedItemsViewModel(
        page_index=0,
        page_size=page_size,
        total_items=0,
        data=[]
    )
```

---

## Performance Considerations

### Indexing

**Required Indexes**:
- `CatalogItems.Id` (primary key, already indexed)
- `CatalogItems.CatalogBrandId` (foreign key, should be indexed)
- `CatalogItems.CatalogTypeId` (foreign key, should be indexed)

**Query Plan**:
```sql
-- Efficient query plan with indexes
1. Index Seek on CatalogItems (Id) with OFFSET/FETCH
2. Nested Loop Join to CatalogBrands (Index Seek on Id)
3. Nested Loop Join to CatalogTypes (Index Seek on Id)
```

### Caching Strategy

**Not Implemented** (not needed for POC)

**Future Optimization**:
- Cache catalog list for 30-60 seconds (reduces DB load)
- Invalidate cache on any catalog item write (from catalog-crud seam)
- Use Redis or in-memory cache

### Query Performance

**Expected Performance**:
- Count query: < 10ms
- Paginated query with JOINs: < 50ms
- Total endpoint latency: < 100ms

**Measurement**:
```python
start = time.time()
result = await service.get_catalog_items_paginated(10, 0)
logger.info("query.performance", duration_ms=(time.time() - start) * 1000)
```

---

## Migration from EF6 to SQLAlchemy

### Compatibility Matrix

| Feature | EF6 | SQLAlchemy 2.x | Status |
|---------|-----|----------------|--------|
| Eager Loading | `.Include()` | `.options(joinedload())` | ✅ Equivalent |
| Ordering | `.OrderBy()` | `.order_by()` | ✅ Equivalent |
| Pagination | `.Skip().Take()` | `.offset().limit()` | ✅ Equivalent |
| Count | `.LongCount()` | `func.count()` | ✅ Equivalent |
| Async | ❌ Not supported | ✅ Async/await native | ✅ Better |

### Key Differences

**EF6 (Synchronous)**:
```csharp
var items = db.CatalogItems
    .Include(c => c.CatalogBrand)
    .ToList();  // Synchronous
```

**SQLAlchemy (Asynchronous)**:
```python
result = await session.execute(
    select(CatalogItem)
        .options(joinedload(CatalogItem.catalog_brand))
)
items = result.scalars().all()  # Async
```

**Benefits of SQLAlchemy Async**:
- Non-blocking I/O (better concurrency)
- FastAPI native async support
- Better performance under load

---

## Data Integrity

**Read-Only Guarantees**:
- This seam CANNOT modify data
- No INSERT, UPDATE, DELETE statements possible
- No data corruption risk
- Safe to run in production without writes

**Foreign Key Integrity**:
- CatalogItems.CatalogBrandId → CatalogBrands.Id
- CatalogItems.CatalogTypeId → CatalogTypes.Id
- Database enforces referential integrity
- JOINs will never fail due to missing foreign keys (if DB constraints are in place)

---

## Testing Strategy

### Unit Tests

**Test Data Access**:
```python
@pytest.mark.asyncio
async def test_get_catalog_items_paginated():
    """Test paginated query with mocked session."""
    service = CatalogService(mock_session)
    result = await service.get_catalog_items_paginated(10, 0)

    assert result.page_size == 10
    assert result.page_index == 0
    assert len(result.data) <= 10
    assert all(item.catalog_brand is not None for item in result.data)
    assert all(item.catalog_type is not None for item in result.data)
```

### Integration Tests

**Test Real Database**:
```python
@pytest.mark.asyncio
async def test_catalog_items_api_pagination(client):
    """Test API endpoint with real database."""
    response = await client.get("/api/catalog/items?page_size=10&page_index=0")

    assert response.status_code == 200
    data = response.json()
    assert "page_index" in data
    assert "total_items" in data
    assert "data" in data
    assert len(data["data"]) <= 10
```

### Performance Tests

**Test Query Speed**:
```python
@pytest.mark.asyncio
async def test_query_performance(service):
    """Ensure query completes within 100ms."""
    start = time.time()
    result = await service.get_catalog_items_paginated(10, 0)
    duration = (time.time() - start) * 1000

    assert duration < 100, f"Query took {duration}ms (expected < 100ms)"
```

---

## Rollback Strategy

**Not Applicable** - Read-only seam has no rollback concerns.

**If Migration Fails**:
- Old system continues to work (no data modified)
- New system can be taken offline
- No data migration or rollback needed

---

## Approval

**Strategy Approved**: READ-ONLY

**Approved By**: Discovery Agent (automated)
**Date**: 2026-03-02
**Confidence**: High

**Constraints**:
- ✅ No writes
- ✅ No transactions
- ✅ No external dependencies
- ✅ No data migration needed

**Next Steps**:
- ✅ Backend implementation complete (already exists)
- ✅ Frontend implementation complete (already exists)
- → Manual validation by user
- → Generate parity tests (STEP 12, optional)

---

**Status**: ✅ APPROVED AND IMPLEMENTED
