"""
Pydantic schemas (DTOs) for catalog entities.

These schemas are used for API request/response validation and serialization.
"""

from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Generic, TypeVar

# Generic type for paginated responses
T = TypeVar("T")


class CatalogBrandDto(BaseModel):
    """Catalog brand DTO."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    brand: str


class CatalogTypeDto(BaseModel):
    """Catalog type DTO."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    type: str


class CatalogItemDto(BaseModel):
    """
    Catalog item DTO with navigation properties populated.

    Used for GET responses that include brand and type information.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None = None
    price: Decimal
    picture_file_name: str
    picture_uri: str | None = None
    catalog_type_id: int
    catalog_brand_id: int
    available_stock: int
    restock_threshold: int
    max_stock_threshold: int
    on_reorder: bool

    # Navigation properties
    catalog_type: CatalogTypeDto
    catalog_brand: CatalogBrandDto


class CatalogItemCreateDto(BaseModel):
    """
    Catalog item creation DTO.

    Validates according to business rules:
    - BR-001: Price validation
    - BR-002: AvailableStock validation
    - BR-003: RestockThreshold validation
    - BR-004: MaxStockThreshold validation
    """

    name: str = Field(..., min_length=1, description="Product name (required)")
    description: str | None = Field(None, description="Product description (optional)")
    price: Decimal = Field(
        ...,
        ge=0,
        le=Decimal("9999999999999999.99"),
        decimal_places=2,
        description="Price (0-9999999999999999.99, max 2 decimals)",
    )
    catalog_type_id: int = Field(..., description="Catalog type ID (required)")
    catalog_brand_id: int = Field(..., description="Catalog brand ID (required)")
    available_stock: int = Field(
        default=0,
        ge=0,
        le=10_000_000,
        description="Available stock (0-10,000,000)",
    )
    restock_threshold: int = Field(
        default=0,
        ge=0,
        le=10_000_000,
        description="Restock threshold (0-10,000,000)",
    )
    max_stock_threshold: int = Field(
        default=0,
        ge=0,
        le=10_000_000,
        description="Max stock threshold (0-10,000,000)",
    )
    picture_file_name: str = Field(
        default="dummy.png",
        description="Picture filename (defaults to 'dummy.png')",
    )

    @field_validator("price")
    @classmethod
    def validate_price_decimals(cls, v: Decimal) -> Decimal:
        """Validate price has maximum 2 decimal places (BR-001)."""
        if v.as_tuple().exponent < -2:
            raise ValueError("Price must have maximum 2 decimal places")
        return v


class CatalogItemUpdateDto(BaseModel):
    """
    Catalog item update DTO.

    Similar to CreateDto but for updates. All fields except ID can be modified.
    """

    name: str = Field(..., min_length=1)
    description: str | None = None
    price: Decimal = Field(..., ge=0, le=Decimal("9999999999999999.99"), decimal_places=2)
    catalog_type_id: int
    catalog_brand_id: int
    available_stock: int = Field(..., ge=0, le=10_000_000)
    restock_threshold: int = Field(..., ge=0, le=10_000_000)
    max_stock_threshold: int = Field(..., ge=0, le=10_000_000)
    picture_file_name: str  # Read-only in UI but included for completeness

    @field_validator("price")
    @classmethod
    def validate_price_decimals(cls, v: Decimal) -> Decimal:
        """Validate price has maximum 2 decimal places."""
        if v.as_tuple().exponent < -2:
            raise ValueError("Price must have maximum 2 decimal places")
        return v


class PaginatedItemsViewModel(BaseModel, Generic[T]):
    """
    Paginated items view model.

    Legacy: eShopLegacyWebForms.ViewModel.PaginatedItemsViewModel<T>

    Used for paginated list responses.
    """

    page_index: int = Field(..., description="Current page index (zero-based)")
    page_size: int = Field(..., description="Number of items per page")
    total_items: int = Field(..., description="Total count of all items")
    total_pages: int = Field(..., description="Total number of pages")
    data: list[T] = Field(..., description="Items for current page")

    @property
    def actual_page(self) -> int:
        """Actual page number (zero-based, for legacy compatibility)."""
        return self.page_index

    @property
    def items_per_page(self) -> int:
        """Items per page (alias for legacy compatibility)."""
        return self.page_size


class PaginatedCatalogItemsResponse(PaginatedItemsViewModel[CatalogItemDto]):
    """
    Paginated catalog items response.

    Concrete type for catalog item pagination.
    """

    pass
