"""
Catalog item CRUD service.

Implements all business logic for catalog management:
- List with pagination (default 10 items, page 0)
- Get by ID (with brand and type eager loading)
- Create (with image finalization)
- Update (with optional image change)
- Delete (without image cleanup - legacy behavior)
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from typing import Optional
import structlog

from app.catalog.models import CatalogItem, CatalogBrand, CatalogType
from app.catalog.schemas import (
    CatalogItemResponse,
    CatalogItemListResponse,
    CatalogItemCreate,
    CatalogItemUpdate,
    PaginationMetadata,
)
from app.images.service import ImageService

logger = structlog.get_logger()


class CatalogService:
    """
    Service for catalog item CRUD operations.

    All methods follow like-to-like migration principles:
    - Fixed sort order: Id ascending (legacy default)
    - Default pagination: 10 items per page (legacy default)
    - Eager loading: Brand and Type always loaded
    - No image cleanup on delete (legacy behavior)
    """

    def __init__(self, db: AsyncSession, image_service: ImageService):
        """
        Initialize service with database session and image service.

        Args:
            db: Async database session
            image_service: Image upload/storage service
        """
        self.db = db
        self.image_service = image_service

    async def list_items(
        self,
        page: int = 0,
        limit: int = 10,
    ) -> CatalogItemListResponse:
        """
        List catalog items with pagination.

        Args:
            page: Page number (zero-based, default 0)
            limit: Items per page (1-100, default 10)

        Returns:
            Paginated list of catalog items with metadata

        Raises:
            HTTPException: If database query fails
        """
        logger.info("catalog.list", page=page, limit=limit)

        # Validate pagination parameters
        if page < 0:
            raise HTTPException(status_code=400, detail="Page must be >= 0")
        if limit < 1 or limit > 100:
            raise HTTPException(status_code=400, detail="Limit must be between 1 and 100")

        try:
            # Count total items
            count_stmt = select(func.count()).select_from(CatalogItem)
            total_items_result = await self.db.execute(count_stmt)
            total_items = total_items_result.scalar() or 0

            # Calculate total pages
            total_pages = (total_items + limit - 1) // limit if total_items > 0 else 0

            # Query items with eager loading (brand and type)
            offset = page * limit
            stmt = (
                select(CatalogItem)
                .options(
                    selectinload(CatalogItem.brand),
                    selectinload(CatalogItem.type),
                )
                .order_by(CatalogItem.Id)  # Fixed sort order (legacy behavior)
                .offset(offset)
                .limit(limit)
            )

            result = await self.db.execute(stmt)
            items = result.scalars().all()

            # Convert to response DTOs
            items_response = [
                CatalogItemResponse.from_orm_model(item)
                for item in items
            ]

            pagination = PaginationMetadata(
                page=page,
                limit=limit,
                total_items=total_items,
                total_pages=total_pages,
            )

            logger.info(
                "catalog.list.success",
                page=page,
                limit=limit,
                items_returned=len(items_response),
                total_items=total_items,
            )

            return CatalogItemListResponse(items=items_response, pagination=pagination)

        except HTTPException:
            raise
        except SQLAlchemyError as e:
            logger.error("catalog.list.failed", error=str(e))
            raise HTTPException(status_code=500, detail="Failed to retrieve catalog items")

    async def get_item(self, item_id: int) -> CatalogItemResponse:
        """
        Get catalog item by ID.

        Args:
            item_id: Catalog item ID

        Returns:
            Catalog item with brand and type details

        Raises:
            HTTPException: If item not found or query fails
        """
        logger.info("catalog.get", item_id=item_id)

        try:
            stmt = (
                select(CatalogItem)
                .options(
                    selectinload(CatalogItem.brand),
                    selectinload(CatalogItem.type),
                )
                .where(CatalogItem.Id == item_id)
            )

            result = await self.db.execute(stmt)
            item = result.scalar_one_or_none()

            if not item:
                logger.warning("catalog.get.not_found", item_id=item_id)
                raise HTTPException(status_code=404, detail=f"Catalog item {item_id} not found")

            logger.info("catalog.get.success", item_id=item_id, name=item.Name)
            return CatalogItemResponse.from_orm_model(item)

        except HTTPException:
            raise
        except SQLAlchemyError as e:
            logger.error("catalog.get.failed", item_id=item_id, error=str(e))
            raise HTTPException(status_code=500, detail="Failed to retrieve catalog item")

    async def create_item(self, data: CatalogItemCreate) -> CatalogItemResponse:
        """
        Create new catalog item.

        Args:
            data: Catalog item creation data (includes temp_image_name)

        Returns:
            Created catalog item

        Raises:
            HTTPException: If foreign key invalid, image finalization fails, or insert fails
        """
        logger.info("catalog.create", name=data.name, brand_id=data.catalog_brand_id)

        try:
            # Validate foreign keys exist
            await self._validate_brand_exists(data.catalog_brand_id)
            await self._validate_type_exists(data.catalog_type_id)

            # Finalize image (move from temp to /Pics/)
            final_filename = self.image_service.get_final_filename(data.temp_image_name)
            if data.temp_image_name and data.temp_image_name != "dummy.png":
                try:
                    self.image_service.finalize_image(data.temp_image_name)
                except HTTPException as e:
                    logger.warning("catalog.create.image_finalize_failed", temp_image=data.temp_image_name)
                    # Use dummy.png if temp image not found
                    final_filename = "dummy.png"

            # Create catalog item
            item = CatalogItem(
                Name=data.name,
                Description=data.description,
                Price=data.price,
                PictureFileName=final_filename,
                CatalogBrandId=data.catalog_brand_id,
                CatalogTypeId=data.catalog_type_id,
                AvailableStock=data.available_stock,
                RestockThreshold=data.restock_threshold,
                MaxStockThreshold=data.max_stock_threshold,
                OnReorder=False,  # Default value
            )

            self.db.add(item)
            await self.db.flush()  # Get ID before commit
            await self.db.refresh(item, ["brand", "type"])  # Load relationships

            logger.info("catalog.create.success", item_id=item.Id, name=item.Name)
            return CatalogItemResponse.from_orm_model(item)

        except HTTPException:
            raise
        except SQLAlchemyError as e:
            logger.error("catalog.create.failed", error=str(e))
            raise HTTPException(status_code=500, detail="Failed to create catalog item")

    async def update_item(self, item_id: int, data: CatalogItemUpdate) -> CatalogItemResponse:
        """
        Update existing catalog item.

        Args:
            item_id: Catalog item ID
            data: Updated catalog item data (includes optional temp_image_name)

        Returns:
            Updated catalog item

        Raises:
            HTTPException: If item not found, foreign keys invalid, or update fails
        """
        logger.info("catalog.update", item_id=item_id, name=data.name)

        try:
            # Get existing item
            stmt = select(CatalogItem).where(CatalogItem.Id == item_id)
            result = await self.db.execute(stmt)
            item = result.scalar_one_or_none()

            if not item:
                logger.warning("catalog.update.not_found", item_id=item_id)
                raise HTTPException(status_code=404, detail=f"Catalog item {item_id} not found")

            # Validate foreign keys exist
            await self._validate_brand_exists(data.catalog_brand_id)
            await self._validate_type_exists(data.catalog_type_id)

            # Handle image change
            final_filename = item.PictureFileName  # Keep existing by default
            if data.temp_image_name:
                final_filename = self.image_service.get_final_filename(data.temp_image_name)
                if data.temp_image_name != "dummy.png":
                    try:
                        self.image_service.finalize_image(data.temp_image_name)
                    except HTTPException:
                        logger.warning("catalog.update.image_finalize_failed", temp_image=data.temp_image_name)
                        final_filename = item.PictureFileName  # Keep existing

            # Update fields
            item.Name = data.name
            item.Description = data.description
            item.Price = data.price
            item.PictureFileName = final_filename
            item.CatalogBrandId = data.catalog_brand_id
            item.CatalogTypeId = data.catalog_type_id
            item.AvailableStock = data.available_stock
            item.RestockThreshold = data.restock_threshold
            item.MaxStockThreshold = data.max_stock_threshold

            await self.db.flush()
            await self.db.refresh(item, ["brand", "type"])

            logger.info("catalog.update.success", item_id=item.Id, name=item.Name)
            return CatalogItemResponse.from_orm_model(item)

        except HTTPException:
            raise
        except SQLAlchemyError as e:
            logger.error("catalog.update.failed", item_id=item_id, error=str(e))
            raise HTTPException(status_code=500, detail="Failed to update catalog item")

    async def delete_item(self, item_id: int) -> None:
        """
        Delete catalog item.

        Args:
            item_id: Catalog item ID

        Raises:
            HTTPException: If item not found or delete fails

        Note:
            Image file is NOT deleted (legacy behavior preserved).
            This is documented technical debt.
        """
        logger.info("catalog.delete", item_id=item_id)

        try:
            stmt = select(CatalogItem).where(CatalogItem.Id == item_id)
            result = await self.db.execute(stmt)
            item = result.scalar_one_or_none()

            if not item:
                logger.warning("catalog.delete.not_found", item_id=item_id)
                raise HTTPException(status_code=404, detail=f"Catalog item {item_id} not found")

            # Note: Image file NOT deleted (legacy behavior)
            # image_filename = item.PictureFileName  # Not used
            await self.db.delete(item)

            logger.info("catalog.delete.success", item_id=item_id)

        except HTTPException:
            raise
        except SQLAlchemyError as e:
            logger.error("catalog.delete.failed", item_id=item_id, error=str(e))
            raise HTTPException(status_code=500, detail="Failed to delete catalog item")

    # Helper methods

    async def _validate_brand_exists(self, brand_id: int) -> None:
        """Validate that brand ID exists."""
        stmt = select(CatalogBrand).where(CatalogBrand.Id == brand_id)
        result = await self.db.execute(stmt)
        brand = result.scalar_one_or_none()

        if not brand:
            logger.warning("catalog.validate.brand_not_found", brand_id=brand_id)
            raise HTTPException(status_code=400, detail=f"Brand ID {brand_id} does not exist")

    async def _validate_type_exists(self, type_id: int) -> None:
        """Validate that type ID exists."""
        stmt = select(CatalogType).where(CatalogType.Id == type_id)
        result = await self.db.execute(stmt)
        catalog_type = result.scalar_one_or_none()

        if not catalog_type:
            logger.warning("catalog.validate.type_not_found", type_id=type_id)
            raise HTTPException(status_code=400, detail=f"Type ID {type_id} does not exist")
