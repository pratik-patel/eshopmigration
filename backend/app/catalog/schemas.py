"""
Pydantic schemas for catalog management API.
All DTOs match OpenAPI contract exactly.
"""

from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional
from decimal import Decimal


# ============================================================================
# Response DTOs
# ============================================================================

class BrandResponse(BaseModel):
    """Brand lookup response."""
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Brand ID")
    brand: str = Field(..., max_length=100, description="Brand name")


class TypeResponse(BaseModel):
    """Type lookup response."""
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Type ID")
    type: str = Field(..., max_length=100, description="Type name")


class CatalogItemResponse(BaseModel):
    """
    Catalog item response with full details.
    Includes nested brand and type objects.
    """
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Catalog item ID")
    name: str = Field(..., max_length=50, description="Product name")
    description: Optional[str] = Field(None, description="Product description")
    price: Decimal = Field(..., description="Product price")
    picture_file_name: str = Field(..., description="Image filename")
    picture_uri: str = Field(..., description="Full image URI (/Pics/{filename})")
    catalog_brand_id: int = Field(..., description="Brand foreign key")
    catalog_type_id: int = Field(..., description="Type foreign key")
    brand: BrandResponse = Field(..., description="Brand details")
    type: TypeResponse = Field(..., description="Type details")
    available_stock: int = Field(..., description="Current stock level")
    restock_threshold: int = Field(..., description="Restock alert threshold")
    max_stock_threshold: int = Field(..., description="Maximum stock capacity")

    @classmethod
    def from_orm_model(cls, db_model):
        """
        Convert SQLAlchemy model to Pydantic schema.
        Handles attribute name mapping (Id → id, Name → name, etc.)
        """
        return cls(
            id=db_model.Id,
            name=db_model.Name,
            description=db_model.Description,
            price=db_model.Price,
            picture_file_name=db_model.PictureFileName,
            picture_uri=db_model.picture_uri,  # Computed property
            catalog_brand_id=db_model.CatalogBrandId,
            catalog_type_id=db_model.CatalogTypeId,
            brand=BrandResponse(id=db_model.brand.Id, brand=db_model.brand.Brand),
            type=TypeResponse(id=db_model.type.Id, type=db_model.type.Type),
            available_stock=db_model.AvailableStock,
            restock_threshold=db_model.RestockThreshold,
            max_stock_threshold=db_model.MaxStockThreshold,
        )


class PaginationMetadata(BaseModel):
    """Pagination metadata for list responses."""

    page: int = Field(..., ge=0, description="Current page (zero-based)")
    limit: int = Field(..., ge=1, le=100, description="Items per page")
    total_items: int = Field(..., ge=0, description="Total items across all pages")
    total_pages: int = Field(..., ge=0, description="Total pages")


class CatalogItemListResponse(BaseModel):
    """Paginated list of catalog items."""

    items: list[CatalogItemResponse] = Field(..., description="Catalog items")
    pagination: PaginationMetadata = Field(..., description="Pagination details")


# ============================================================================
# Request DTOs (Create/Update)
# ============================================================================

class CatalogItemCreate(BaseModel):
    """
    Request body for creating a catalog item.
    Validation rules match requirements.md REQ-2.12-2.23.
    """

    name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Product name (required)",
    )

    description: Optional[str] = Field(
        None,
        description="Product description (optional)",
    )

    price: Decimal = Field(
        ...,
        ge=0,
        le=Decimal("999999999.99"),
        decimal_places=2,
        description="Product price (must have at most 2 decimal places)",
    )

    catalog_brand_id: int = Field(
        ...,
        ge=1,
        description="Brand foreign key (required)",
    )

    catalog_type_id: int = Field(
        ...,
        ge=1,
        description="Type foreign key (required)",
    )

    available_stock: int = Field(
        ...,
        ge=0,
        le=10000000,
        description="Initial stock level",
    )

    restock_threshold: int = Field(
        ...,
        ge=0,
        le=10000000,
        description="Restock alert threshold",
    )

    max_stock_threshold: int = Field(
        ...,
        ge=0,
        le=10000000,
        description="Maximum stock capacity",
    )

    temp_image_name: Optional[str] = Field(
        None,
        description="Temporary image filename from upload (optional, defaults to dummy.png)",
    )

    @field_validator("price")
    @classmethod
    def validate_price_decimal_places(cls, v: Decimal) -> Decimal:
        """Ensure price has at most 2 decimal places."""
        if v.as_tuple().exponent < -2:
            raise ValueError("Price must have at most 2 decimal places")
        return v


class CatalogItemUpdate(BaseModel):
    """
    Request body for updating a catalog item.
    Same validation rules as Create.
    """

    name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Product name (required)",
    )

    description: Optional[str] = Field(
        None,
        description="Product description (optional)",
    )

    price: Decimal = Field(
        ...,
        ge=0,
        le=Decimal("999999999.99"),
        decimal_places=2,
        description="Product price",
    )

    catalog_brand_id: int = Field(
        ...,
        ge=1,
        description="Brand foreign key",
    )

    catalog_type_id: int = Field(
        ...,
        ge=1,
        description="Type foreign key",
    )

    available_stock: int = Field(
        ...,
        ge=0,
        le=10000000,
        description="Stock level",
    )

    restock_threshold: int = Field(
        ...,
        ge=0,
        le=10000000,
        description="Restock threshold",
    )

    max_stock_threshold: int = Field(
        ...,
        ge=0,
        le=10000000,
        description="Maximum stock",
    )

    temp_image_name: Optional[str] = Field(
        None,
        description="New image filename (optional, preserves existing if null)",
    )

    @field_validator("price")
    @classmethod
    def validate_price_decimal_places(cls, v: Decimal) -> Decimal:
        """Ensure price has at most 2 decimal places."""
        if v.as_tuple().exponent < -2:
            raise ValueError("Price must have at most 2 decimal places")
        return v


# ============================================================================
# Image Upload DTOs
# ============================================================================

class TempImageResponse(BaseModel):
    """Response after temporary image upload."""

    temp_filename: str = Field(..., description="Temporary filename (UUID + extension)")


# ============================================================================
# Error DTOs
# ============================================================================

class ErrorDetail(BaseModel):
    """Error detail structure."""

    code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[dict] = Field(None, description="Additional error context")
    request_id: Optional[str] = Field(None, description="Correlation ID for error tracking")


class ErrorResponse(BaseModel):
    """Standard error response envelope."""

    error: ErrorDetail = Field(..., description="Error details")
