"""
Unit tests for CatalogService.

Tests all CRUD operations with mocked database.
Coverage target: ≥80%
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession

from app.catalog.service import CatalogService
from app.catalog.models import CatalogItem, CatalogBrand, CatalogType
from app.catalog.schemas import CatalogItemCreate, CatalogItemUpdate
from app.images.service import ImageService


@pytest.fixture
def mock_db():
    """Mock database session."""
    db = AsyncMock(spec=AsyncSession)
    db.execute = AsyncMock()
    db.flush = AsyncMock()
    db.refresh = AsyncMock()
    db.delete = AsyncMock()
    db.add = MagicMock()
    return db


@pytest.fixture
def mock_image_service():
    """Mock image service."""
    service = MagicMock(spec=ImageService)
    service.get_final_filename = MagicMock(return_value="test.png")
    service.finalize_image = MagicMock(return_value="test.png")
    return service


@pytest.fixture
def catalog_service(mock_db, mock_image_service):
    """Catalog service with mocked dependencies."""
    return CatalogService(db=mock_db, image_service=mock_image_service)


@pytest.fixture
def sample_brand():
    """Sample brand object."""
    brand = MagicMock(spec=CatalogBrand)
    brand.Id = 1
    brand.Brand = "Azure"
    return brand


@pytest.fixture
def sample_type():
    """Sample type object."""
    catalog_type = MagicMock(spec=CatalogType)
    catalog_type.Id = 1
    catalog_type.Type = "T-Shirt"
    return catalog_type


@pytest.fixture
def sample_item(sample_brand, sample_type):
    """Sample catalog item object."""
    item = MagicMock(spec=CatalogItem)
    item.Id = 1
    item.Name = "Test Product"
    item.Description = "Test Description"
    item.Price = Decimal("19.99")
    item.PictureFileName = "test.png"
    item.picture_uri = "/Pics/test.png"
    item.CatalogBrandId = 1
    item.CatalogTypeId = 1
    item.brand = sample_brand
    item.type = sample_type
    item.AvailableStock = 100
    item.RestockThreshold = 10
    item.MaxStockThreshold = 200
    return item


# ============================================================================
# List Items Tests
# ============================================================================

@pytest.mark.asyncio
async def test_list_items_success(catalog_service, mock_db, sample_item):
    """Test listing items with pagination."""
    # Mock count query
    count_result = AsyncMock()
    count_result.scalar = MagicMock(return_value=25)

    # Mock items query
    items_result = AsyncMock()
    items_result.scalars = MagicMock(return_value=MagicMock(all=MagicMock(return_value=[sample_item] * 10)))

    # Setup execute to return different results for different queries
    mock_db.execute.side_effect = [count_result, items_result]

    # Call service
    result = await catalog_service.list_items(page=0, limit=10)

    # Assertions
    assert len(result.items) == 10
    assert result.pagination.page == 0
    assert result.pagination.limit == 10
    assert result.pagination.total_items == 25
    assert result.pagination.total_pages == 3
    assert result.items[0].id == 1
    assert result.items[0].name == "Test Product"


@pytest.mark.asyncio
async def test_list_items_empty(catalog_service, mock_db):
    """Test listing items when database is empty."""
    # Mock count query
    count_result = AsyncMock()
    count_result.scalar = MagicMock(return_value=0)

    # Mock items query
    items_result = AsyncMock()
    items_result.scalars = MagicMock(return_value=MagicMock(all=MagicMock(return_value=[])))

    mock_db.execute.side_effect = [count_result, items_result]

    result = await catalog_service.list_items(page=0, limit=10)

    assert len(result.items) == 0
    assert result.pagination.total_items == 0
    assert result.pagination.total_pages == 0


@pytest.mark.asyncio
async def test_list_items_invalid_page(catalog_service):
    """Test listing items with invalid page number."""
    with pytest.raises(Exception) as exc_info:
        await catalog_service.list_items(page=-1, limit=10)
    assert "Page must be >= 0" in str(exc_info.value)


@pytest.mark.asyncio
async def test_list_items_invalid_limit(catalog_service):
    """Test listing items with invalid limit."""
    with pytest.raises(Exception) as exc_info:
        await catalog_service.list_items(page=0, limit=0)
    assert "Limit must be between 1 and 100" in str(exc_info.value)


# ============================================================================
# Get Item Tests
# ============================================================================

@pytest.mark.asyncio
async def test_get_item_success(catalog_service, mock_db, sample_item):
    """Test getting item by ID."""
    result = AsyncMock()
    result.scalar_one_or_none = MagicMock(return_value=sample_item)
    mock_db.execute.return_value = result

    item = await catalog_service.get_item(item_id=1)

    assert item.id == 1
    assert item.name == "Test Product"
    assert item.price == Decimal("19.99")


@pytest.mark.asyncio
async def test_get_item_not_found(catalog_service, mock_db):
    """Test getting non-existent item."""
    result = AsyncMock()
    result.scalar_one_or_none = MagicMock(return_value=None)
    mock_db.execute.return_value = result

    with pytest.raises(Exception) as exc_info:
        await catalog_service.get_item(item_id=999)
    assert "not found" in str(exc_info.value).lower()


# ============================================================================
# Create Item Tests
# ============================================================================

@pytest.mark.asyncio
async def test_create_item_success(catalog_service, mock_db, mock_image_service, sample_brand, sample_type):
    """Test creating new item."""
    # Mock FK validation queries
    brand_result = AsyncMock()
    brand_result.scalar_one_or_none = MagicMock(return_value=sample_brand)

    type_result = AsyncMock()
    type_result.scalar_one_or_none = MagicMock(return_value=sample_type)

    mock_db.execute.side_effect = [brand_result, type_result]

    # Mock item after creation
    created_item = MagicMock(spec=CatalogItem)
    created_item.Id = 1
    created_item.Name = "New Product"
    created_item.Description = "New Description"
    created_item.Price = Decimal("29.99")
    created_item.PictureFileName = "test.png"
    created_item.picture_uri = "/Pics/test.png"
    created_item.CatalogBrandId = 1
    created_item.CatalogTypeId = 1
    created_item.brand = sample_brand
    created_item.type = sample_type
    created_item.AvailableStock = 50
    created_item.RestockThreshold = 5
    created_item.MaxStockThreshold = 100

    # Mock refresh to populate relationships
    async def mock_refresh(item, attributes):
        item.brand = sample_brand
        item.type = sample_type

    mock_db.refresh.side_effect = mock_refresh
    mock_db.add.side_effect = lambda item: setattr(item, 'Id', 1)

    # Create item data
    data = CatalogItemCreate(
        name="New Product",
        description="New Description",
        price=Decimal("29.99"),
        catalog_brand_id=1,
        catalog_type_id=1,
        available_stock=50,
        restock_threshold=5,
        max_stock_threshold=100,
        temp_image_name="test.png",
    )

    # Call service
    result = await catalog_service.create_item(data=data)

    # Assertions
    mock_db.add.assert_called_once()
    mock_db.flush.assert_called_once()
    mock_image_service.finalize_image.assert_called_once_with("test.png")


@pytest.mark.asyncio
async def test_create_item_invalid_brand(catalog_service, mock_db):
    """Test creating item with invalid brand ID."""
    # Mock FK validation - brand not found
    brand_result = AsyncMock()
    brand_result.scalar_one_or_none = MagicMock(return_value=None)
    mock_db.execute.return_value = brand_result

    data = CatalogItemCreate(
        name="New Product",
        price=Decimal("29.99"),
        catalog_brand_id=999,
        catalog_type_id=1,
        available_stock=50,
        restock_threshold=5,
        max_stock_threshold=100,
    )

    with pytest.raises(Exception) as exc_info:
        await catalog_service.create_item(data=data)
    assert "Brand ID" in str(exc_info.value) or "does not exist" in str(exc_info.value)


# ============================================================================
# Update Item Tests
# ============================================================================

@pytest.mark.asyncio
async def test_update_item_success(catalog_service, mock_db, mock_image_service, sample_item, sample_brand, sample_type):
    """Test updating existing item."""
    # Mock get item query
    get_result = AsyncMock()
    get_result.scalar_one_or_none = MagicMock(return_value=sample_item)

    # Mock FK validation queries
    brand_result = AsyncMock()
    brand_result.scalar_one_or_none = MagicMock(return_value=sample_brand)

    type_result = AsyncMock()
    type_result.scalar_one_or_none = MagicMock(return_value=sample_type)

    mock_db.execute.side_effect = [get_result, brand_result, type_result]

    # Update data
    data = CatalogItemUpdate(
        name="Updated Product",
        description="Updated Description",
        price=Decimal("39.99"),
        catalog_brand_id=1,
        catalog_type_id=1,
        available_stock=75,
        restock_threshold=8,
        max_stock_threshold=150,
        temp_image_name="new.png",
    )

    # Call service
    result = await catalog_service.update_item(item_id=1, data=data)

    # Assertions
    mock_db.flush.assert_called_once()
    mock_image_service.finalize_image.assert_called_once_with("new.png")


@pytest.mark.asyncio
async def test_update_item_not_found(catalog_service, mock_db):
    """Test updating non-existent item."""
    result = AsyncMock()
    result.scalar_one_or_none = MagicMock(return_value=None)
    mock_db.execute.return_value = result

    data = CatalogItemUpdate(
        name="Updated Product",
        price=Decimal("39.99"),
        catalog_brand_id=1,
        catalog_type_id=1,
        available_stock=75,
        restock_threshold=8,
        max_stock_threshold=150,
    )

    with pytest.raises(Exception) as exc_info:
        await catalog_service.update_item(item_id=999, data=data)
    assert "not found" in str(exc_info.value).lower()


# ============================================================================
# Delete Item Tests
# ============================================================================

@pytest.mark.asyncio
async def test_delete_item_success(catalog_service, mock_db, sample_item):
    """Test deleting item."""
    result = AsyncMock()
    result.scalar_one_or_none = MagicMock(return_value=sample_item)
    mock_db.execute.return_value = result

    await catalog_service.delete_item(item_id=1)

    mock_db.delete.assert_called_once_with(sample_item)


@pytest.mark.asyncio
async def test_delete_item_not_found(catalog_service, mock_db):
    """Test deleting non-existent item."""
    result = AsyncMock()
    result.scalar_one_or_none = MagicMock(return_value=None)
    mock_db.execute.return_value = result

    with pytest.raises(Exception) as exc_info:
        await catalog_service.delete_item(item_id=999)
    assert "not found" in str(exc_info.value).lower()
