"""
Unit tests for CatalogService.
"""

import pytest
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.db import Base
from app.core.models import CatalogItem, CatalogBrand, CatalogType
from app.core.service import CatalogService, CatalogServiceMock
from app.core.seed import seed_database


# Test database setup
@pytest.fixture
async def db_session():
    """Create an in-memory SQLite database for testing."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session_maker = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session_maker() as session:
        # Seed test data
        await seed_database(session)
        yield session

    await engine.dispose()


@pytest.fixture
def catalog_service(db_session: AsyncSession):
    """Create CatalogService instance with test database."""
    return CatalogService(db_session)


@pytest.fixture
def catalog_service_mock():
    """Create CatalogServiceMock instance."""
    return CatalogServiceMock()


class TestCatalogService:
    """Tests for real CatalogService (database-backed)."""

    async def test_get_catalog_brands(self, catalog_service: CatalogService):
        """Test getting all catalog brands."""
        brands = await catalog_service.get_catalog_brands()

        assert len(brands) == 5
        assert brands[0].brand == ".NET"  # Sorted by brand name
        assert brands[1].brand == "Azure"

    async def test_get_catalog_types(self, catalog_service: CatalogService):
        """Test getting all catalog types."""
        types = await catalog_service.get_catalog_types()

        assert len(types) == 4
        assert types[0].type == "Mug"  # Sorted by type name
        assert types[1].type == "Sheet"

    async def test_find_catalog_item_existing(self, catalog_service: CatalogService):
        """Test finding an existing catalog item."""
        item = await catalog_service.find_catalog_item(1)

        assert item is not None
        assert item.id == 1
        assert item.name == ".NET Bot Black Hoodie"
        assert item.price == Decimal("19.5")
        # Check relationships loaded
        assert item.catalog_brand is not None
        assert item.catalog_brand.brand == ".NET"
        assert item.catalog_type is not None
        assert item.catalog_type.type == "T-Shirt"

    async def test_find_catalog_item_not_found(self, catalog_service: CatalogService):
        """Test finding a non-existent catalog item."""
        item = await catalog_service.find_catalog_item(99999)

        assert item is None

    async def test_get_catalog_items_paginated_first_page(
        self, catalog_service: CatalogService
    ):
        """Test getting first page of catalog items."""
        result = await catalog_service.get_catalog_items_paginated(
            page_size=5, page_index=0
        )

        assert result.page_index == 0
        assert result.page_size == 5
        assert result.total_items == 12
        assert result.total_pages == 3
        assert len(result.data) == 5

        # Check first item (should be sorted by name)
        first_item = result.data[0]
        assert first_item.catalog_brand is not None
        assert first_item.catalog_type is not None

    async def test_get_catalog_items_paginated_last_page(
        self, catalog_service: CatalogService
    ):
        """Test getting last page of catalog items."""
        result = await catalog_service.get_catalog_items_paginated(
            page_size=5, page_index=2
        )

        assert result.page_index == 2
        assert result.page_size == 5
        assert result.total_items == 12
        assert result.total_pages == 3
        assert len(result.data) == 2  # Only 2 items on last page

    async def test_create_catalog_item(
        self, catalog_service: CatalogService, db_session: AsyncSession
    ):
        """Test creating a new catalog item."""
        new_item = CatalogItem(
            name="Test Product",
            description="Test Description",
            price=Decimal("99.99"),
            picture_file_name="test.png",
            catalog_type_id=1,
            catalog_brand_id=1,
            available_stock=50,
            restock_threshold=10,
            max_stock_threshold=100,
        )

        created = await catalog_service.create_catalog_item(new_item)

        assert created.id is not None
        assert created.id > 0
        assert created.name == "Test Product"
        assert created.price == Decimal("99.99")
        # Check relationships loaded
        assert created.catalog_brand is not None
        assert created.catalog_type is not None

    async def test_update_catalog_item(
        self, catalog_service: CatalogService, db_session: AsyncSession
    ):
        """Test updating an existing catalog item."""
        # Fetch existing item
        item = await catalog_service.find_catalog_item(1)
        assert item is not None

        # Update fields
        item.name = "Updated Name"
        item.price = Decimal("29.99")

        # Save update
        updated = await catalog_service.update_catalog_item(item)

        assert updated.id == 1
        assert updated.name == "Updated Name"
        assert updated.price == Decimal("29.99")

    async def test_remove_catalog_item(
        self, catalog_service: CatalogService, db_session: AsyncSession
    ):
        """Test removing a catalog item."""
        # Fetch existing item
        item = await catalog_service.find_catalog_item(1)
        assert item is not None

        # Remove item
        await catalog_service.remove_catalog_item(item)

        # Verify deleted
        deleted_item = await catalog_service.find_catalog_item(1)
        assert deleted_item is None


class TestCatalogServiceMock:
    """Tests for mock CatalogService (in-memory)."""

    async def test_get_catalog_brands_mock(
        self, catalog_service_mock: CatalogServiceMock
    ):
        """Test getting brands from mock service."""
        brands = await catalog_service_mock.get_catalog_brands()

        assert len(brands) == 3
        assert brands[0].brand == "Azure"

    async def test_get_catalog_types_mock(
        self, catalog_service_mock: CatalogServiceMock
    ):
        """Test getting types from mock service."""
        types = await catalog_service_mock.get_catalog_types()

        assert len(types) == 3
        assert types[0].type == "Mug"

    async def test_find_catalog_item_mock(
        self, catalog_service_mock: CatalogServiceMock
    ):
        """Test finding item in mock service."""
        item = await catalog_service_mock.find_catalog_item(1)

        assert item is not None
        assert item.id == 1
        assert item.name == ".NET Bot Black Hoodie"

    async def test_get_catalog_items_paginated_mock(
        self, catalog_service_mock: CatalogServiceMock
    ):
        """Test pagination in mock service."""
        result = await catalog_service_mock.get_catalog_items_paginated(
            page_size=2, page_index=0
        )

        assert result.page_index == 0
        assert result.page_size == 2
        assert result.total_items == 3
        assert result.total_pages == 2
        assert len(result.data) == 2

    async def test_create_catalog_item_mock(
        self, catalog_service_mock: CatalogServiceMock
    ):
        """Test creating item in mock service."""
        new_item = CatalogItem(
            name="Mock Test Product",
            description="Test",
            price=Decimal("50.00"),
            picture_file_name="test.png",
            catalog_type_id=1,
            catalog_brand_id=1,
            available_stock=10,
        )

        created = await catalog_service_mock.create_catalog_item(new_item)

        assert created.id == 4  # Next ID after initial 3 items
        assert created.name == "Mock Test Product"

    async def test_update_catalog_item_mock(
        self, catalog_service_mock: CatalogServiceMock
    ):
        """Test updating item in mock service."""
        item = await catalog_service_mock.find_catalog_item(1)
        assert item is not None

        item.name = "Updated Mock Name"
        updated = await catalog_service_mock.update_catalog_item(item)

        assert updated.name == "Updated Mock Name"

    async def test_remove_catalog_item_mock(
        self, catalog_service_mock: CatalogServiceMock
    ):
        """Test removing item in mock service."""
        item = await catalog_service_mock.find_catalog_item(1)
        assert item is not None

        await catalog_service_mock.remove_catalog_item(item)

        deleted = await catalog_service_mock.find_catalog_item(1)
        assert deleted is None
