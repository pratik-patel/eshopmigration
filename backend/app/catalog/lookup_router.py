"""
Catalog lookup API router.

Endpoints:
- GET /api/v1/catalog/brands - List all brands
- GET /api/v1/catalog/types - List all types
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import structlog

from app.core.db import get_db
from app.catalog.lookup_service import LookupService
from app.catalog.schemas import BrandResponse, TypeResponse, ErrorResponse

logger = structlog.get_logger()

router = APIRouter(prefix="/catalog", tags=["catalog-lookups"])


def get_lookup_service(
    db: AsyncSession = Depends(get_db),
) -> LookupService:
    """Dependency injection for LookupService."""
    return LookupService(db=db)


@router.get(
    "/brands",
    response_model=List[BrandResponse],
    status_code=200,
    responses={
        500: {"model": ErrorResponse, "description": "Database error"},
    },
    summary="List all catalog brands",
    description="""
    Retrieve all available catalog brands.

    Brands are sorted alphabetically by name.
    Used to populate brand dropdown in catalog item forms.
    """,
)
async def list_brands(
    service: LookupService = Depends(get_lookup_service),
) -> List[BrandResponse]:
    """
    List all catalog brands.

    Args:
        service: Lookup service dependency

    Returns:
        List of all brands (sorted by name)
    """
    logger.info("api.catalog.brands.list")
    return await service.get_all_brands()


@router.get(
    "/types",
    response_model=List[TypeResponse],
    status_code=200,
    responses={
        500: {"model": ErrorResponse, "description": "Database error"},
    },
    summary="List all catalog types",
    description="""
    Retrieve all available catalog types.

    Types are sorted alphabetically by name.
    Used to populate type dropdown in catalog item forms.
    """,
)
async def list_types(
    service: LookupService = Depends(get_lookup_service),
) -> List[TypeResponse]:
    """
    List all catalog types.

    Args:
        service: Lookup service dependency

    Returns:
        List of all types (sorted by name)
    """
    logger.info("api.catalog.types.list")
    return await service.get_all_types()
