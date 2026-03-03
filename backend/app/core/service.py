"""
Catalog service implementations.

Provides both real database access (CatalogService) and mock in-memory data (CatalogServiceMock).
"""

import math
from abc import ABC, abstractmethod
from typing import Protocol
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
import structlog

from app.core.models import CatalogItem, CatalogBrand, CatalogType
from app.core.schemas import PaginatedCatalogItemsResponse, CatalogItemDto
from app.core.exceptions import NotFoundException

logger = structlog.get_logger()


class ICatalogService(Protocol):
    """
    Catalog service interface (port).

    Legacy: eShopLegacyWebForms.Services.ICatalogService

    Defines contract for catalog operations.
    """

    async def find_catalog_item(self, item_id: int) -> CatalogItem | None:
        """Find catalog item by ID with Brand and Type loaded."""
        ...

    async def get_catalog_items_paginated(
        self, page_size: int, page_index: int
    ) -> PaginatedCatalogItemsResponse:
        """Get paginated catalog items."""
        ...

    async def get_catalog_brands(self) -> list[CatalogBrand]:
        """Get all catalog brands."""
        ...

    async def get_catalog_types(self) -> list[CatalogType]:
        """Get all catalog types."""
        ...

    async def create_catalog_item(self, item: CatalogItem) -> CatalogItem:
        """Create new catalog item."""
        ...

    async def update_catalog_item(self, item: CatalogItem) -> CatalogItem:
        """Update existing catalog item."""
        ...

    async def remove_catalog_item(self, item: CatalogItem) -> None:
        """Remove catalog item."""
        ...


class CatalogService:
    """
    Real catalog service implementation with database access.

    Legacy: eShopLegacyWebForms.Services.CatalogService

    Uses SQLAlchemy async for all database operations.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize service with database session.

        Args:
            session: SQLAlchemy async session
        """
        self.session = session
        self.logger = logger.bind(service="CatalogService")

    async def find_catalog_item(self, item_id: int) -> CatalogItem | None:
        """
        Find catalog item by ID with Brand and Type eagerly loaded.

        Args:
            item_id: Catalog item ID

        Returns:
            CatalogItem if found, None otherwise
        """
        stmt = (
            select(CatalogItem)
            .options(
                selectinload(CatalogItem.catalog_brand),
                selectinload(CatalogItem.catalog_type),
            )
            .where(CatalogItem.id == item_id)
        )

        result = await self.session.execute(stmt)
        item = result.scalar_one_or_none()

        self.logger.info(
            "catalog.item.find",
            item_id=item_id,
            found=item is not None,
        )

        return item

    async def get_catalog_items_paginated(
        self, page_size: int, page_index: int
    ) -> PaginatedCatalogItemsResponse:
        """
        Get paginated catalog items with Brand and Type eagerly loaded.

        Args:
            page_size: Number of items per page
            page_index: Page index (zero-based)

        Returns:
            Paginated response with items and metadata
        """
        # Count total items
        count_stmt = select(func.count()).select_from(CatalogItem)
        total_count = await self.session.scalar(count_stmt) or 0

        # Calculate total pages
        total_pages = math.ceil(total_count / page_size) if page_size > 0 else 0

        # Fetch page of items
        stmt = (
            select(CatalogItem)
            .options(
                selectinload(CatalogItem.catalog_brand),
                selectinload(CatalogItem.catalog_type),
            )
            .order_by(CatalogItem.name)
            .offset(page_index * page_size)
            .limit(page_size)
        )

        result = await self.session.execute(stmt)
        items = list(result.scalars().all())

        self.logger.info(
            "catalog.items.paginated",
            page_size=page_size,
            page_index=page_index,
            total_items=total_count,
            items_returned=len(items),
        )

        # Convert to DTOs
        item_dtos = [CatalogItemDto.model_validate(item) for item in items]

        return PaginatedCatalogItemsResponse(
            page_index=page_index,
            page_size=page_size,
            total_items=total_count,
            total_pages=total_pages,
            data=item_dtos,
        )

    async def get_catalog_brands(self) -> list[CatalogBrand]:
        """
        Get all catalog brands ordered by brand name.

        Returns:
            List of all catalog brands
        """
        stmt = select(CatalogBrand).order_by(CatalogBrand.brand)
        result = await self.session.execute(stmt)
        brands = list(result.scalars().all())

        self.logger.info("catalog.brands.get_all", count=len(brands))

        return brands

    async def get_catalog_types(self) -> list[CatalogType]:
        """
        Get all catalog types ordered by type name.

        Returns:
            List of all catalog types
        """
        stmt = select(CatalogType).order_by(CatalogType.type)
        result = await self.session.execute(stmt)
        types = list(result.scalars().all())

        self.logger.info("catalog.types.get_all", count=len(types))

        return types

    async def create_catalog_item(self, item: CatalogItem) -> CatalogItem:
        """
        Create new catalog item.

        Args:
            item: Catalog item to create

        Returns:
            Created catalog item with ID assigned
        """
        self.session.add(item)
        await self.session.commit()
        await self.session.refresh(item)

        # Eagerly load relationships
        await self.session.refresh(item, ["catalog_brand", "catalog_type"])

        self.logger.info(
            "catalog.item.create",
            item_id=item.id,
            name=item.name,
            price=float(item.price),
        )

        return item

    async def update_catalog_item(self, item: CatalogItem) -> CatalogItem:
        """
        Update existing catalog item.

        Args:
            item: Catalog item with updated values

        Returns:
            Updated catalog item
        """
        await self.session.commit()
        await self.session.refresh(item)

        # Eagerly load relationships
        await self.session.refresh(item, ["catalog_brand", "catalog_type"])

        self.logger.info(
            "catalog.item.update",
            item_id=item.id,
            name=item.name,
            price=float(item.price),
        )

        return item

    async def remove_catalog_item(self, item: CatalogItem) -> None:
        """
        Remove catalog item.

        Args:
            item: Catalog item to remove
        """
        item_id = item.id
        await self.session.delete(item)
        await self.session.commit()

        self.logger.info("catalog.item.remove", item_id=item_id)


class CatalogServiceMock:
    """
    Mock catalog service implementation with in-memory data.

    Legacy: eShopLegacyWebForms.Services.CatalogServiceMock

    Returns hardcoded sample data without database dependency.
    Used for development and testing.
    """

    def __init__(self):
        """Initialize mock service with sample data."""
        self.logger = logger.bind(service="CatalogServiceMock", mock=True)

        # Initialize mock data
        self._brands = [
            CatalogBrand(id=1, brand="Azure"),
            CatalogBrand(id=2, brand=".NET"),
            CatalogBrand(id=5, brand="Other"),
        ]

        self._types = [
            CatalogType(id=1, type="Mug"),
            CatalogType(id=2, type="T-Shirt"),
            CatalogType(id=3, type="Sheet"),
        ]

        self._items = [
            CatalogItem(
                id=1,
                name=".NET Bot Black Hoodie",
                description=".NET Bot Black Hoodie",
                price=19.50,
                picture_file_name="1.png",
                catalog_type_id=2,
                catalog_brand_id=2,
                available_stock=100,
                restock_threshold=10,
                max_stock_threshold=200,
                on_reorder=False,
            ),
            CatalogItem(
                id=2,
                name=".NET Black & White Mug",
                description=".NET Black & White Mug",
                price=8.50,
                picture_file_name="2.png",
                catalog_type_id=1,
                catalog_brand_id=2,
                available_stock=100,
                restock_threshold=10,
                max_stock_threshold=200,
                on_reorder=False,
            ),
            CatalogItem(
                id=3,
                name="Prism White T-Shirt",
                description="Prism White T-Shirt",
                price=12.00,
                picture_file_name="3.png",
                catalog_type_id=2,
                catalog_brand_id=5,
                available_stock=100,
                restock_threshold=10,
                max_stock_threshold=200,
                on_reorder=False,
            ),
        ]

        # Manually set navigation properties for mock data
        for item in self._items:
            item.catalog_brand = next((b for b in self._brands if b.id == item.catalog_brand_id), self._brands[0])
            item.catalog_type = next((t for t in self._types if t.id == item.catalog_type_id), self._types[0])

    async def find_catalog_item(self, item_id: int) -> CatalogItem | None:
        """Mock implementation of find_catalog_item."""
        item = next((i for i in self._items if i.id == item_id), None)

        self.logger.info(
            "catalog.item.find",
            item_id=item_id,
            found=item is not None,
            mock=True,
        )

        return item

    async def get_catalog_items_paginated(
        self, page_size: int, page_index: int
    ) -> PaginatedCatalogItemsResponse:
        """Mock implementation of get_catalog_items_paginated."""
        total_count = len(self._items)
        total_pages = math.ceil(total_count / page_size) if page_size > 0 else 0

        # Slice items for pagination
        start_idx = page_index * page_size
        end_idx = start_idx + page_size
        page_items = self._items[start_idx:end_idx]

        self.logger.info(
            "catalog.items.paginated",
            page_size=page_size,
            page_index=page_index,
            total_items=total_count,
            items_returned=len(page_items),
            mock=True,
        )

        # Convert to DTOs
        item_dtos = [CatalogItemDto.model_validate(item) for item in page_items]

        return PaginatedCatalogItemsResponse(
            page_index=page_index,
            page_size=page_size,
            total_items=total_count,
            total_pages=total_pages,
            data=item_dtos,
        )

    async def get_catalog_brands(self) -> list[CatalogBrand]:
        """Mock implementation of get_catalog_brands."""
        self.logger.info("catalog.brands.get_all", count=len(self._brands), mock=True)
        return self._brands

    async def get_catalog_types(self) -> list[CatalogType]:
        """Mock implementation of get_catalog_types."""
        self.logger.info("catalog.types.get_all", count=len(self._types), mock=True)
        return self._types

    async def create_catalog_item(self, item: CatalogItem) -> CatalogItem:
        """Mock implementation of create_catalog_item."""
        # Assign next ID
        item.id = max((i.id for i in self._items), default=0) + 1

        # Set navigation properties
        item.catalog_brand = next((b for b in self._brands if b.id == item.catalog_brand_id), self._brands[0])
        item.catalog_type = next((t for t in self._types if t.id == item.catalog_type_id), self._types[0])

        self._items.append(item)

        self.logger.info(
            "catalog.item.create",
            item_id=item.id,
            name=item.name,
            mock=True,
        )

        return item

    async def update_catalog_item(self, item: CatalogItem) -> CatalogItem:
        """Mock implementation of update_catalog_item."""
        # Find and replace existing item
        idx = next((i for i, x in enumerate(self._items) if x.id == item.id), None)
        if idx is not None:
            self._items[idx] = item

        # Refresh navigation properties
        item.catalog_brand = next((b for b in self._brands if b.id == item.catalog_brand_id), self._brands[0])
        item.catalog_type = next((t for t in self._types if t.id == item.catalog_type_id), self._types[0])

        self.logger.info(
            "catalog.item.update",
            item_id=item.id,
            name=item.name,
            mock=True,
        )

        return item

    async def remove_catalog_item(self, item: CatalogItem) -> None:
        """Mock implementation of remove_catalog_item."""
        self._items = [i for i in self._items if i.id != item.id]

        self.logger.info("catalog.item.remove", item_id=item.id, mock=True)
