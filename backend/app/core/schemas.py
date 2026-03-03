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

    Validates according to business rules with EXACT legacy error messages:
    - BR-001: Price validation
    - BR-002: AvailableStock validation
    - BR-003: RestockThreshold validation
    - BR-004: MaxStockThreshold validation
    - BR-005: Name required
    """

    name: str = Field(..., description="Product name (required)")
    description: str | None = Field(None, description="Product description (optional)")
    price: Decimal = Field(..., description="Price (0-1000000, max 2 decimals)")
    catalog_type_id: int = Field(..., description="Catalog type ID (required)")
    catalog_brand_id: int = Field(..., description="Catalog brand ID (required)")
    available_stock: int = Field(default=0, description="Available stock (0-10,000,000)")
    restock_threshold: int = Field(default=0, description="Restock threshold (0-10,000,000)")
    max_stock_threshold: int = Field(default=0, description="Max stock threshold (0-10,000,000)")
    picture_file_name: str = Field(default="dummy.png", description="Picture filename (defaults to 'dummy.png')")

    @field_validator("name")
    @classmethod
    def validate_name_required(cls, v: str) -> str:
        """Validate name is not empty (BR-005)."""
        if not v or not v.strip():
            raise ValueError("The Name field is required.")
        return v

    @field_validator("price")
    @classmethod
    def validate_price_range(cls, v: Decimal) -> Decimal:
        """Validate price range and decimals (BR-001)."""
        # Check range first
        if v < 0 or v > 1_000_000:
            raise ValueError(
                "The Price must be a positive number with maximum two decimals between 0 and 1 million."
            )
        # Check decimal places
        if v.as_tuple().exponent < -2:
            raise ValueError(
                "The Price must be a positive number with maximum two decimals between 0 and 1 million."
            )
        return v

    @field_validator("available_stock")
    @classmethod
    def validate_available_stock_range(cls, v: int) -> int:
        """Validate available stock range (BR-002)."""
        if v < 0 or v > 10_000_000:
            raise ValueError("The field Stock must be between 0 and 10 million.")
        return v

    @field_validator("restock_threshold")
    @classmethod
    def validate_restock_threshold_range(cls, v: int) -> int:
        """Validate restock threshold range (BR-003)."""
        if v < 0 or v > 10_000_000:
            raise ValueError("The field Restock must be between 0 and 10 million.")
        return v

    @field_validator("max_stock_threshold")
    @classmethod
    def validate_max_stock_threshold_range(cls, v: int) -> int:
        """Validate max stock threshold range (BR-004)."""
        if v < 0 or v > 10_000_000:
            raise ValueError("The field Max stock must be between 0 and 10 million.")
        return v


class CatalogItemUpdateDto(BaseModel):
    """
    Catalog item update DTO.

    Similar to CreateDto but for updates. All fields except ID can be modified.
    Same validation rules as CreateDto (BR-001 to BR-005).
    """

    name: str = Field(...)
    description: str | None = None
    price: Decimal = Field(...)
    catalog_type_id: int
    catalog_brand_id: int
    available_stock: int = Field(...)
    restock_threshold: int = Field(...)
    max_stock_threshold: int = Field(...)
    picture_file_name: str  # Read-only in UI but included for completeness

    @field_validator("name")
    @classmethod
    def validate_name_required(cls, v: str) -> str:
        """Validate name is not empty (BR-005)."""
        if not v or not v.strip():
            raise ValueError("The Name field is required.")
        return v

    @field_validator("price")
    @classmethod
    def validate_price_range(cls, v: Decimal) -> Decimal:
        """Validate price range and decimals (BR-001)."""
        # Check range first
        if v < 0 or v > 1_000_000:
            raise ValueError(
                "The Price must be a positive number with maximum two decimals between 0 and 1 million."
            )
        # Check decimal places
        if v.as_tuple().exponent < -2:
            raise ValueError(
                "The Price must be a positive number with maximum two decimals between 0 and 1 million."
            )
        return v

    @field_validator("available_stock")
    @classmethod
    def validate_available_stock_range(cls, v: int) -> int:
        """Validate available stock range (BR-002)."""
        if v < 0 or v > 10_000_000:
            raise ValueError("The field Stock must be between 0 and 10 million.")
        return v

    @field_validator("restock_threshold")
    @classmethod
    def validate_restock_threshold_range(cls, v: int) -> int:
        """Validate restock threshold range (BR-003)."""
        if v < 0 or v > 10_000_000:
            raise ValueError("The field Restock must be between 0 and 10 million.")
        return v

    @field_validator("max_stock_threshold")
    @classmethod
    def validate_max_stock_threshold_range(cls, v: int) -> int:
        """Validate max stock threshold range (BR-004)."""
        if v < 0 or v > 10_000_000:
            raise ValueError("The field Max stock must be between 0 and 10 million.")
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
