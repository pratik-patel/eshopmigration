"""
Catalog API router.

Provides REST endpoints for catalog operations.
"""

from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import Annotated
import structlog

from app.core.service import ICatalogService
from app.core.schemas import (
    PaginatedCatalogItemsResponse,
    CatalogItemDto,
    CatalogItemCreateDto,
    CatalogItemUpdateDto,
    CatalogBrandDto,
    CatalogTypeDto,
)
from app.core.models import CatalogItem
from app.core.exceptions import NotFoundException
from app.dependencies import get_catalog_service
from app.config import get_settings

logger = structlog.get_logger()
router = APIRouter()
settings = get_settings()


@router.get(
    "/items",
    response_model=PaginatedCatalogItemsResponse,
    summary="Get paginated catalog items",
    description="Get a paginated list of catalog items with brand and type information",
)
async def get_catalog_items(
    page_size: Annotated[
        int,
        Query(
            ge=1,
            le=settings.max_page_size,
            description=f"Number of items per page (1-{settings.max_page_size})",
        ),
    ] = settings.default_page_size,
    page_index: Annotated[
        int, Query(ge=0, description="Page index (zero-based)")
    ] = 0,
    catalog_service: ICatalogService = Depends(get_catalog_service),
):
    """
    Get paginated catalog items.

    **Query Parameters:**
    - `page_size`: Number of items per page (default: 10, max: 100)
    - `page_index`: Page index, zero-based (default: 0)

    **Returns:**
    - Paginated response with items and metadata

    **Legacy Endpoint:** Default.aspx (catalog list page)
    """
    logger.info(
        "api.catalog.items.list",
        page_size=page_size,
        page_index=page_index,
    )

    result = await catalog_service.get_catalog_items_paginated(page_size, page_index)

    return result


@router.get(
    "/items/{item_id}",
    response_model=CatalogItemDto,
    summary="Get catalog item by ID",
    description="Get a single catalog item with brand and type information",
)
async def get_catalog_item(
    item_id: int,
    catalog_service: ICatalogService = Depends(get_catalog_service),
):
    """
    Get catalog item by ID.

    **Path Parameters:**
    - `item_id`: Catalog item ID

    **Returns:**
    - Catalog item with brand and type

    **Raises:**
    - 404 if item not found

    **Legacy Endpoint:** Used by Edit.aspx, Details.aspx, Delete.aspx
    """
    logger.info("api.catalog.item.get", item_id=item_id)

    item = await catalog_service.find_catalog_item(item_id)

    if not item:
        raise NotFoundException("Catalog item", item_id)

    return CatalogItemDto.model_validate(item)


@router.post(
    "/items",
    response_model=CatalogItemDto,
    status_code=status.HTTP_201_CREATED,
    summary="Create catalog item",
    description="Create a new catalog item",
)
async def create_catalog_item(
    item_data: CatalogItemCreateDto,
    catalog_service: ICatalogService = Depends(get_catalog_service),
):
    """
    Create new catalog item.

    **Request Body:**
    - Catalog item data (see CatalogItemCreateDto schema)

    **Returns:**
    - Created catalog item with ID assigned

    **Legacy Endpoint:** Create.aspx (Create_Click handler)
    """
    logger.info("api.catalog.item.create", name=item_data.name, price=float(item_data.price))

    # Convert DTO to model
    new_item = CatalogItem(
        name=item_data.name,
        description=item_data.description,
        price=item_data.price,
        picture_file_name=item_data.picture_file_name,
        catalog_type_id=item_data.catalog_type_id,
        catalog_brand_id=item_data.catalog_brand_id,
        available_stock=item_data.available_stock,
        restock_threshold=item_data.restock_threshold,
        max_stock_threshold=item_data.max_stock_threshold,
    )

    # Create in database
    created_item = await catalog_service.create_catalog_item(new_item)

    return CatalogItemDto.model_validate(created_item)


@router.put(
    "/items/{item_id}",
    response_model=CatalogItemDto,
    summary="Update catalog item",
    description="Update an existing catalog item",
)
async def update_catalog_item(
    item_id: int,
    item_data: CatalogItemUpdateDto,
    catalog_service: ICatalogService = Depends(get_catalog_service),
):
    """
    Update existing catalog item.

    **Path Parameters:**
    - `item_id`: Catalog item ID

    **Request Body:**
    - Updated catalog item data

    **Returns:**
    - Updated catalog item

    **Raises:**
    - 404 if item not found

    **Legacy Endpoint:** Edit.aspx (Save_Click handler)
    """
    logger.info("api.catalog.item.update", item_id=item_id, name=item_data.name)

    # Find existing item
    existing_item = await catalog_service.find_catalog_item(item_id)

    if not existing_item:
        raise NotFoundException("Catalog item", item_id)

    # Update fields
    existing_item.name = item_data.name
    existing_item.description = item_data.description
    existing_item.price = item_data.price
    existing_item.catalog_type_id = item_data.catalog_type_id
    existing_item.catalog_brand_id = item_data.catalog_brand_id
    existing_item.available_stock = item_data.available_stock
    existing_item.restock_threshold = item_data.restock_threshold
    existing_item.max_stock_threshold = item_data.max_stock_threshold
    existing_item.picture_file_name = item_data.picture_file_name

    # Save to database
    updated_item = await catalog_service.update_catalog_item(existing_item)

    return CatalogItemDto.model_validate(updated_item)


@router.delete(
    "/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete catalog item",
    description="Delete a catalog item",
)
async def delete_catalog_item(
    item_id: int,
    catalog_service: ICatalogService = Depends(get_catalog_service),
):
    """
    Delete catalog item.

    **Path Parameters:**
    - `item_id`: Catalog item ID

    **Returns:**
    - 204 No Content on success

    **Raises:**
    - 404 if item not found

    **Legacy Endpoint:** Delete.aspx (Delete_Click handler)
    """
    logger.info("api.catalog.item.delete", item_id=item_id)

    # Find existing item
    existing_item = await catalog_service.find_catalog_item(item_id)

    if not existing_item:
        raise NotFoundException("Catalog item", item_id)

    # Delete from database
    await catalog_service.remove_catalog_item(existing_item)

    # Return 204 No Content (no response body)
    return None


@router.get(
    "/brands",
    response_model=list[CatalogBrandDto],
    summary="Get all catalog brands",
    description="Get list of all catalog brands for dropdown",
)
async def get_catalog_brands(
    catalog_service: ICatalogService = Depends(get_catalog_service),
):
    """
    Get all catalog brands.

    **Returns:**
    - List of all brands ordered by name

    **Legacy Endpoint:** Create.aspx GetBrands(), Edit.aspx dropdown population
    """
    logger.info("api.catalog.brands.list")

    brands = await catalog_service.get_catalog_brands()

    return [CatalogBrandDto.model_validate(brand) for brand in brands]


@router.get(
    "/types",
    response_model=list[CatalogTypeDto],
    summary="Get all catalog types",
    description="Get list of all catalog types for dropdown",
)
async def get_catalog_types(
    catalog_service: ICatalogService = Depends(get_catalog_service),
):
    """
    Get all catalog types.

    **Returns:**
    - List of all types ordered by name

    **Legacy Endpoint:** Create.aspx GetTypes(), Edit.aspx dropdown population
    """
    logger.info("api.catalog.types.list")

    types = await catalog_service.get_catalog_types()

    return [CatalogTypeDto.model_validate(catalog_type) for catalog_type in types]
