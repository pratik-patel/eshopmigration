# Seam Specification: Data Access Layer

**Seam ID**: `data-access`
**Priority**: 3 (High - foundational)
**Complexity**: Medium
**Status**: Pending Discovery

---

## Purpose

Database access layer providing CRUD operations for catalog entities, database initialization, and data seeding.

## Scope

### In-Scope
- Entity models (CatalogItem, CatalogBrand, CatalogType)
- Database context and session management
- Service layer implementations (real and mock)
- Database initialization and seeding
- HiLo ID generation (if preserved)
- Query patterns (pagination, filtering, joins)

### Out-of-Scope
- Database migrations (handled by Alembic)
- Connection pooling configuration (handled at engine level)
- Advanced query optimization (initial migration uses straightforward queries)

## Legacy Implementation

### Entity Models

**Models**:
- `CatalogItem` - main product entity
- `CatalogBrand` - product brand/manufacturer
- `CatalogType` - product category/type

**DbContext**: `CatalogDBContext` (Entity Framework 6)
- DbSet<CatalogItem> CatalogItems
- DbSet<CatalogBrand> CatalogBrands
- DbSet<CatalogType> CatalogTypes

### Service Interface

**Interface**: `ICatalogService` (Services/ICatalogService.cs)

**Methods**:
```csharp
CatalogItem FindCatalogItem(int id);
IEnumerable<CatalogBrand> GetCatalogBrands();
PaginatedItemsViewModel<CatalogItem> GetCatalogItemsPaginated(int pageSize, int pageIndex);
IEnumerable<CatalogType> GetCatalogTypes();
void CreateCatalogItem(CatalogItem catalogItem);
void UpdateCatalogItem(CatalogItem catalogItem);
void RemoveCatalogItem(CatalogItem catalogItem);
```

### Implementations

1. **CatalogService** (Services/CatalogService.cs)
   - Real database access via Entity Framework
   - Uses CatalogDBContext
   - Executes SQL queries

2. **CatalogServiceMock** (Services/CatalogServiceMock.cs)
   - In-memory mock data
   - No database dependency
   - Returns hardcoded sample data

### Database Initialization

**Initializer**: `CatalogDBInitializer` (Models/Infrastructure/)
- Database.SetInitializer pattern (EF6)
- Seeds initial data on first run

**Seed Data**: `PreconfiguredData` (Models/Infrastructure/)
- 10 CatalogTypes
- 10 CatalogBrands
- ~14 CatalogItems

### ID Generation

**HiLoGenerator**: `CatalogItemHiLoGenerator` (Models/)
- Hi/Lo pattern for efficient ID generation
- Avoids database round-trips

## Dependencies

### External
- Entity Framework 6 (legacy)
- SQL Server LocalDB (legacy)
- SQLAlchemy 2.x async (migration target)
- asyncpg or aiosqlite (migration target)

### Cross-Seam
- Used by **catalog-list** seam
- Used by **catalog-crud** seam

## Database Schema

See `docs/context-fabric/database-access.md` for complete schema details.

**Key Relationships**:
- CatalogItem → CatalogBrand (Many-to-One)
- CatalogItem → CatalogType (Many-to-One)

## Migration Strategy

### Entity Models → SQLAlchemy

**Replace**:
- EF6 entity classes → SQLAlchemy ORM models
- Data annotations → SQLAlchemy Column definitions
- Navigation properties → SQLAlchemy relationships

**Example** (CatalogItem):
```python
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Numeric, Integer, Boolean, ForeignKey
from decimal import Decimal

class CatalogItem(Base):
    __tablename__ = "catalog_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(String)
    price: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    picture_file_name: Mapped[str] = mapped_column(String, default="dummy.png")
    picture_uri: Mapped[str | None] = mapped_column(String)
    catalog_type_id: Mapped[int] = mapped_column(ForeignKey("catalog_types.id"))
    catalog_brand_id: Mapped[int] = mapped_column(ForeignKey("catalog_brands.id"))
    available_stock: Mapped[int] = mapped_column(Integer, default=0)
    restock_threshold: Mapped[int] = mapped_column(Integer, default=0)
    max_stock_threshold: Mapped[int] = mapped_column(Integer, default=0)
    on_reorder: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    catalog_type: Mapped["CatalogType"] = relationship(back_populates="catalog_items")
    catalog_brand: Mapped["CatalogBrand"] = relationship(back_populates="catalog_items")
```

### DbContext → AsyncSession

**Replace**:
- CatalogDBContext → AsyncSession from sessionmaker
- Synchronous operations → async operations
- Include() → selectinload(), joinedload()

### Service Layer

**FastAPI service class**:
```python
class CatalogService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_catalog_item(self, item_id: int) -> CatalogItem | None:
        stmt = (
            select(CatalogItem)
            .options(
                selectinload(CatalogItem.catalog_brand),
                selectinload(CatalogItem.catalog_type)
            )
            .where(CatalogItem.id == item_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_catalog_items_paginated(
        self, page_size: int, page_index: int
    ) -> PaginatedItemsViewModel:
        # Count total
        count_stmt = select(func.count()).select_from(CatalogItem)
        total = await self.session.scalar(count_stmt)

        # Fetch page
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
        result = await self.session.execute(stmt)
        items = result.scalars().all()

        return PaginatedItemsViewModel(
            page_index=page_index,
            page_size=page_size,
            total_items=total,
            data=items
        )

    async def create_catalog_item(self, item: CatalogItem) -> CatalogItem:
        self.session.add(item)
        await self.session.commit()
        await self.session.refresh(item)
        return item

    async def update_catalog_item(self, item: CatalogItem) -> CatalogItem:
        await self.session.commit()
        await self.session.refresh(item)
        return item

    async def remove_catalog_item(self, item: CatalogItem) -> None:
        await self.session.delete(item)
        await self.session.commit()

    async def get_catalog_brands(self) -> list[CatalogBrand]:
        result = await self.session.execute(select(CatalogBrand).order_by(CatalogBrand.brand))
        return list(result.scalars().all())

    async def get_catalog_types(self) -> list[CatalogType]:
        result = await self.session.execute(select(CatalogType).order_by(CatalogType.type))
        return list(result.scalars().all())
```

### Mock Service

**CatalogServiceMock**:
- Implement same interface as CatalogService
- Return hardcoded in-memory data
- No database dependency
- Used when `Settings.use_mock_adapters = True`

### Database Initialization

**Alembic migration script**:
- Create tables with proper schema
- Seed initial data from PreconfiguredData equivalent

**Seed script** (backend/app/core/seed.py):
- Populate CatalogBrands
- Populate CatalogTypes
- Populate sample CatalogItems
- Run on first startup or via CLI command

## Configuration

**Settings** (backend/app/config.py):
```python
class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./catalog.db"
    use_mock_adapters: bool = True  # Default to mock for development

    model_config = SettingsConfigDict(env_file=".env")
```

## Dependency Injection

**Factory** (backend/app/dependencies.py):
```python
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

def get_catalog_service(
    session: AsyncSession = Depends(get_db_session)
) -> CatalogService:
    if get_settings().use_mock_adapters:
        return CatalogServiceMock()
    return CatalogService(session)
```

## Business Rules

- **BR-017**: Use SQL Server LocalDB in legacy, migrate to SQLite or PostgreSQL
- **BR-018**: MARS not needed in async Python
- **BR-022**: Service implements IDisposable → async context manager
- **BR-024**: Database seeding with preconfigured data
- **BR-025**: HiLo ID generation (optional in migration - can use auto-increment)

## Success Criteria

- [ ] All entity models defined with SQLAlchemy ORM
- [ ] Relationships configured correctly (foreign keys, back_populates)
- [ ] Service methods implemented for all CRUD operations
- [ ] Pagination query works correctly
- [ ] Mock service returns realistic data
- [ ] Database initialization script seeds sample data
- [ ] All queries use async/await
- [ ] No N+1 query issues (proper eager loading)

## Test Scenarios

1. **Create catalog item**
   - Create new item via service
   - Verify persisted to database
   - Verify ID assigned

2. **Find catalog item**
   - Fetch by ID
   - Verify Brand and Type loaded (no lazy loading)

3. **Paginated query**
   - Fetch page 1, size 10
   - Verify correct items returned
   - Verify total count correct

4. **Update catalog item**
   - Fetch item, modify, update
   - Verify changes persisted

5. **Delete catalog item**
   - Remove item via service
   - Verify no longer in database

6. **Mock service**
   - Set use_mock_adapters=True
   - Verify all operations return mock data
   - Verify no database access

## Notes

- This seam is foundational - must complete before other seams
- Focus on clean SQLAlchemy models and async patterns
- Preserve seed data from legacy for parity testing
- Mock service critical for frontend development without database
