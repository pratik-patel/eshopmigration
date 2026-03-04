"""
Lookup service for catalog brands and types.

Provides read-only access to CatalogBrand and CatalogType tables.
These are reference data tables that are rarely modified.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from typing import List
import structlog

from app.catalog.models import CatalogBrand, CatalogType
from app.catalog.schemas import BrandResponse, TypeResponse

logger = structlog.get_logger()


class LookupService:
    """
    Service for retrieving brand and type lookup data.

    Methods:
    - get_all_brands(): List all brands (ordered by Brand name)
    - get_all_types(): List all types (ordered by Type name)
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize service with database session.

        Args:
            db: Async database session (injected via Depends)
        """
        self.db = db

    async def get_all_brands(self) -> List[BrandResponse]:
        """
        Retrieve all catalog brands.

        Returns:
            List of brands ordered by brand name

        Raises:
            Exception: If database query fails
        """
        logger.info("lookup.brands.list")

        try:
            stmt = select(CatalogBrand).order_by(CatalogBrand.Brand)
            result = await self.db.execute(stmt)
            brands = result.scalars().all()

            response = [
                BrandResponse(id=brand.Id, brand=brand.Brand)
                for brand in brands
            ]

            logger.info("lookup.brands.success", count=len(response))
            return response

        except SQLAlchemyError as e:
            logger.error("lookup.brands.failed", error=str(e))
            raise Exception(f"Failed to retrieve brands: {str(e)}")

    async def get_all_types(self) -> List[TypeResponse]:
        """
        Retrieve all catalog types.

        Returns:
            List of types ordered by type name

        Raises:
            Exception: If database query fails
        """
        logger.info("lookup.types.list")

        try:
            stmt = select(CatalogType).order_by(CatalogType.Type)
            result = await self.db.execute(stmt)
            types = result.scalars().all()

            response = [
                TypeResponse(id=type_obj.Id, type=type_obj.Type)
                for type_obj in types
            ]

            logger.info("lookup.types.success", count=len(response))
            return response

        except SQLAlchemyError as e:
            logger.error("lookup.types.failed", error=str(e))
            raise Exception(f"Failed to retrieve types: {str(e)}")
