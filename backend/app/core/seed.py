"""
Database seed script.

Populates database with initial catalog data from legacy PreconfiguredData.
"""

from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import structlog

from app.core.models import CatalogItem, CatalogBrand, CatalogType

logger = structlog.get_logger()


async def seed_database(session: AsyncSession) -> None:
    """
    Seed database with initial catalog data.

    Data source: eShopLegacyWebForms.Models.Infrastructure.PreconfiguredData

    Args:
        session: Database session
    """
    logger.info("database.seed.start")

    # Check if data already exists
    existing_brands = await session.scalar(select(CatalogBrand).limit(1))
    if existing_brands:
        logger.info("database.seed.skip", reason="Data already exists")
        return

    # Seed Catalog Brands
    brands = [
        CatalogBrand(id=1, brand="Azure"),
        CatalogBrand(id=2, brand=".NET"),
        CatalogBrand(id=3, brand="Visual Studio"),
        CatalogBrand(id=4, brand="SQL Server"),
        CatalogBrand(id=5, brand="Other"),
    ]
    session.add_all(brands)
    await session.flush()
    logger.info("database.seed.brands", count=len(brands))

    # Seed Catalog Types
    types = [
        CatalogType(id=1, type="Mug"),
        CatalogType(id=2, type="T-Shirt"),
        CatalogType(id=3, type="Sheet"),
        CatalogType(id=4, type="USB Memory Stick"),
    ]
    session.add_all(types)
    await session.flush()
    logger.info("database.seed.types", count=len(types))

    # Seed Catalog Items
    items = [
        CatalogItem(
            id=1,
            catalog_type_id=2,
            catalog_brand_id=2,
            available_stock=100,
            description=".NET Bot Black Hoodie",
            name=".NET Bot Black Hoodie",
            price=Decimal("19.5"),
            picture_file_name="1.png",
        ),
        CatalogItem(
            id=2,
            catalog_type_id=1,
            catalog_brand_id=2,
            available_stock=100,
            description=".NET Black & White Mug",
            name=".NET Black & White Mug",
            price=Decimal("8.50"),
            picture_file_name="2.png",
        ),
        CatalogItem(
            id=3,
            catalog_type_id=2,
            catalog_brand_id=5,
            available_stock=100,
            description="Prism White T-Shirt",
            name="Prism White T-Shirt",
            price=Decimal("12"),
            picture_file_name="3.png",
        ),
        CatalogItem(
            id=4,
            catalog_type_id=2,
            catalog_brand_id=2,
            available_stock=100,
            description=".NET Foundation T-shirt",
            name=".NET Foundation T-shirt",
            price=Decimal("12"),
            picture_file_name="4.png",
        ),
        CatalogItem(
            id=5,
            catalog_type_id=3,
            catalog_brand_id=5,
            available_stock=100,
            description="Roslyn Red Sheet",
            name="Roslyn Red Sheet",
            price=Decimal("8.5"),
            picture_file_name="5.png",
        ),
        CatalogItem(
            id=6,
            catalog_type_id=2,
            catalog_brand_id=2,
            available_stock=100,
            description=".NET Blue Hoodie",
            name=".NET Blue Hoodie",
            price=Decimal("12"),
            picture_file_name="6.png",
        ),
        CatalogItem(
            id=7,
            catalog_type_id=2,
            catalog_brand_id=5,
            available_stock=100,
            description="Roslyn Red T-Shirt",
            name="Roslyn Red T-Shirt",
            price=Decimal("12"),
            picture_file_name="7.png",
        ),
        CatalogItem(
            id=8,
            catalog_type_id=2,
            catalog_brand_id=5,
            available_stock=100,
            description="Kudu Purple Hoodie",
            name="Kudu Purple Hoodie",
            price=Decimal("8.5"),
            picture_file_name="8.png",
        ),
        CatalogItem(
            id=9,
            catalog_type_id=1,
            catalog_brand_id=5,
            available_stock=100,
            description="Cup<T> White Mug",
            name="Cup<T> White Mug",
            price=Decimal("12"),
            picture_file_name="9.png",
        ),
        CatalogItem(
            id=10,
            catalog_type_id=3,
            catalog_brand_id=2,
            available_stock=100,
            description=".NET Foundation Sheet",
            name=".NET Foundation Sheet",
            price=Decimal("12"),
            picture_file_name="10.png",
        ),
        CatalogItem(
            id=11,
            catalog_type_id=3,
            catalog_brand_id=2,
            available_stock=100,
            description="Cup<T> Sheet",
            name="Cup<T> Sheet",
            price=Decimal("8.5"),
            picture_file_name="11.png",
        ),
        CatalogItem(
            id=12,
            catalog_type_id=2,
            catalog_brand_id=5,
            available_stock=100,
            description="Prism White TShirt",
            name="Prism White TShirt",
            price=Decimal("12"),
            picture_file_name="12.png",
        ),
    ]
    session.add_all(items)
    await session.commit()
    logger.info("database.seed.items", count=len(items))

    logger.info(
        "database.seed.complete",
        brands=len(brands),
        types=len(types),
        items=len(items),
    )
