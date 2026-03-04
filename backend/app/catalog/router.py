"""
Catalog management API router.

Endpoints:
- GET /api/v1/catalog/items - List catalog items (paginated)
- GET /api/v1/catalog/items/{id} - Get catalog item details
- POST /api/v1/catalog/items - Create catalog item
- PUT /api/v1/catalog/items/{id} - Update catalog item
- DELETE /api/v1/catalog/items/{id} - Delete catalog item
"""

from fastapi import APIRouter, Depends, Query, Path, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
import structlog

from app.core.db import get_db
from app.catalog.service import CatalogService
from app.catalog.schemas import (
    CatalogItemListResponse,
    CatalogItemResponse,
    CatalogItemCreate,
    CatalogItemUpdate,
    ErrorResponse,
)
from app.images.service import ImageService

logger = structlog.get_logger()

router = APIRouter(prefix="/catalog", tags=["catalog"])


def get_catalog_service(
    db: AsyncSession = Depends(get_db),
) -> CatalogService:
    """Dependency injection for CatalogService."""
    image_service = ImageService()
    return CatalogService(db=db, image_service=image_service)


@router.get(
    "/items",
    response_model=CatalogItemListResponse,
    status_code=200,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid pagination parameters"},
        500: {"model": ErrorResponse, "description": "Database error"},
    },
    summary="List catalog items",
    description="""
    Retrieve paginated list of catalog items.

    Items are sorted by ID in ascending order (matches legacy behavior).
    Each item includes brand and type details.

    **Default pagination:** 10 items per page, starting at page 0.
    """,
)
async def list_catalog_items(
    page: Annotated[int, Query(ge=0, description="Page number (zero-based)")] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="Items per page")] = 10,
    service: CatalogService = Depends(get_catalog_service),
) -> CatalogItemListResponse:
    """
    List catalog items with pagination.

    Args:
        page: Page number (zero-based, default 0)
        limit: Items per page (1-100, default 10)
        service: Catalog service dependency

    Returns:
        Paginated list of catalog items
    """
    logger.info("api.catalog.list", page=page, limit=limit)
    return await service.list_items(page=page, limit=limit)


@router.get(
    "/items/{item_id}",
    response_model=CatalogItemResponse,
    status_code=200,
    responses={
        404: {"model": ErrorResponse, "description": "Catalog item not found"},
        500: {"model": ErrorResponse, "description": "Database error"},
    },
    summary="Get catalog item details",
    description="Retrieve detailed information for a specific catalog item.",
)
async def get_catalog_item(
    item_id: Annotated[int, Path(ge=1, description="Catalog item ID")],
    service: CatalogService = Depends(get_catalog_service),
) -> CatalogItemResponse:
    """
    Get catalog item by ID.

    Args:
        item_id: Catalog item ID
        service: Catalog service dependency

    Returns:
        Catalog item details with brand and type
    """
    logger.info("api.catalog.get", item_id=item_id)
    return await service.get_item(item_id=item_id)


@router.post(
    "/items",
    response_model=CatalogItemResponse,
    status_code=201,
    responses={
        400: {"model": ErrorResponse, "description": "Validation error or invalid foreign key"},
        500: {"model": ErrorResponse, "description": "Database error"},
    },
    summary="Create catalog item",
    description="""
    Create a new catalog item.

    **Image upload workflow:**
    1. Upload image via `POST /api/v1/images/upload` to get `temp_filename`
    2. Include `temp_filename` in `temp_image_name` field
    3. Image will be moved to permanent storage upon successful creation

    **Validation rules:**
    - Name: 1-50 characters (required)
    - Price: 0-999999999.99 with max 2 decimal places (required)
    - Brand/Type: Must exist in respective tables (required)
    - Stock fields: 0-10000000 (required)
    """,
)
async def create_catalog_item(
    data: CatalogItemCreate,
    service: CatalogService = Depends(get_catalog_service),
) -> CatalogItemResponse:
    """
    Create new catalog item.

    Args:
        data: Catalog item creation data
        service: Catalog service dependency

    Returns:
        Created catalog item with assigned ID
    """
    logger.info("api.catalog.create", name=data.name)
    return await service.create_item(data=data)


@router.put(
    "/items/{item_id}",
    response_model=CatalogItemResponse,
    status_code=200,
    responses={
        400: {"model": ErrorResponse, "description": "Validation error or invalid foreign key"},
        404: {"model": ErrorResponse, "description": "Catalog item not found"},
        500: {"model": ErrorResponse, "description": "Database error"},
    },
    summary="Update catalog item",
    description="""
    Update an existing catalog item.

    **Image handling:**
    - If `temp_image_name` is provided, replaces existing image
    - If `temp_image_name` is null/empty, keeps existing image
    - Old image file is NOT deleted (legacy behavior)

    **Validation rules:** Same as create endpoint.
    """,
)
async def update_catalog_item(
    item_id: Annotated[int, Path(ge=1, description="Catalog item ID")],
    data: CatalogItemUpdate,
    service: CatalogService = Depends(get_catalog_service),
) -> CatalogItemResponse:
    """
    Update existing catalog item.

    Args:
        item_id: Catalog item ID
        data: Updated catalog item data
        service: Catalog service dependency

    Returns:
        Updated catalog item
    """
    logger.info("api.catalog.update", item_id=item_id, name=data.name)
    return await service.update_item(item_id=item_id, data=data)


@router.delete(
    "/items/{item_id}",
    status_code=204,
    responses={
        404: {"model": ErrorResponse, "description": "Catalog item not found"},
        500: {"model": ErrorResponse, "description": "Database error"},
    },
    summary="Delete catalog item",
    description="""
    Delete a catalog item.

    **Note:** Image file is NOT deleted from storage (legacy behavior).
    This is documented technical debt for future cleanup.
    """,
)
async def delete_catalog_item(
    item_id: Annotated[int, Path(ge=1, description="Catalog item ID")],
    service: CatalogService = Depends(get_catalog_service),
) -> None:
    """
    Delete catalog item.

    Args:
        item_id: Catalog item ID
        service: Catalog service dependency

    Returns:
        None (204 No Content)
    """
    logger.info("api.catalog.delete", item_id=item_id)
    await service.delete_item(item_id=item_id)
