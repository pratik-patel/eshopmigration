"""
Unit tests for catalog item validation.

Tests validation error messages match legacy behavior exactly.
Evidence: legacy-golden/catalog-crud/exports/synthetic_validation_errors.json
"""

import pytest
from decimal import Decimal
from pydantic import ValidationError

from app.core.schemas import CatalogItemCreateDto, CatalogItemUpdateDto


class TestCreateCatalogItemValidation:
    """Test validation rules for CatalogItemCreateDto."""

    def test_valid_item_minimal(self):
        """Test creating item with minimal required fields."""
        dto = CatalogItemCreateDto(
            name="Test Product",
            price=Decimal("19.99"),
            catalog_brand_id=1,
            catalog_type_id=2,
        )

        assert dto.name == "Test Product"
        assert dto.price == Decimal("19.99")
        assert dto.available_stock == 0  # Default
        assert dto.picture_file_name == "dummy.png"  # Default

    def test_valid_item_complete(self):
        """Test creating item with all fields."""
        dto = CatalogItemCreateDto(
            name=".NET Bot Black Hoodie",
            description=".NET Bot Black Hoodie, and more",
            price=Decimal("19.50"),
            catalog_brand_id=1,
            catalog_type_id=2,
            available_stock=100,
            restock_threshold=10,
            max_stock_threshold=200,
            picture_file_name="1.png",
        )

        assert dto.name == ".NET Bot Black Hoodie"
        assert dto.price == Decimal("19.50")
        assert dto.available_stock == 100

    def test_name_required_empty_string(self):
        """Test BR-005: Name field is required."""
        with pytest.raises(ValidationError) as exc_info:
            CatalogItemCreateDto(
                name="",
                price=Decimal("19.99"),
                catalog_brand_id=1,
                catalog_type_id=2,
            )

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("name",)
        assert "The Name field is required." in str(errors[0]["msg"])

    def test_name_required_whitespace(self):
        """Test BR-005: Name with only whitespace is invalid."""
        with pytest.raises(ValidationError) as exc_info:
            CatalogItemCreateDto(
                name="   ",
                price=Decimal("19.99"),
                catalog_brand_id=1,
                catalog_type_id=2,
            )

        errors = exc_info.value.errors()
        assert "The Name field is required." in str(errors[0]["msg"])

    def test_price_negative(self):
        """Test BR-001: Price cannot be negative."""
        with pytest.raises(ValidationError) as exc_info:
            CatalogItemCreateDto(
                name="Test Product",
                price=Decimal("-5.00"),
                catalog_brand_id=1,
                catalog_type_id=2,
            )

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("price",)
        assert (
            "The Price must be a positive number with maximum two decimals between 0 and 1 million."
            in str(errors[0]["msg"])
        )

    def test_price_too_many_decimals(self):
        """Test BR-001: Price cannot have more than 2 decimal places."""
        with pytest.raises(ValidationError) as exc_info:
            CatalogItemCreateDto(
                name="Test Product",
                price=Decimal("12.999"),
                catalog_brand_id=1,
                catalog_type_id=2,
            )

        errors = exc_info.value.errors()
        assert "The Price must be a positive number with maximum two decimals between 0 and 1 million." in str(
            errors[0]["msg"]
        )

    def test_price_exceeds_maximum(self):
        """Test BR-001: Price cannot exceed 1 million."""
        with pytest.raises(ValidationError) as exc_info:
            CatalogItemCreateDto(
                name="Test Product",
                price=Decimal("2000000"),
                catalog_brand_id=1,
                catalog_type_id=2,
            )

        errors = exc_info.value.errors()
        assert "The Price must be a positive number with maximum two decimals between 0 and 1 million." in str(
            errors[0]["msg"]
        )

    def test_price_valid_zero(self):
        """Test BR-001: Price can be zero."""
        dto = CatalogItemCreateDto(
            name="Test Product",
            price=Decimal("0.00"),
            catalog_brand_id=1,
            catalog_type_id=2,
        )

        assert dto.price == Decimal("0.00")

    def test_price_valid_maximum(self):
        """Test BR-001: Price can be exactly 1 million."""
        dto = CatalogItemCreateDto(
            name="Test Product",
            price=Decimal("1000000"),
            catalog_brand_id=1,
            catalog_type_id=2,
        )

        assert dto.price == Decimal("1000000")

    def test_available_stock_negative(self):
        """Test BR-002: Available stock cannot be negative."""
        with pytest.raises(ValidationError) as exc_info:
            CatalogItemCreateDto(
                name="Test Product",
                price=Decimal("19.99"),
                catalog_brand_id=1,
                catalog_type_id=2,
                available_stock=-1,
            )

        errors = exc_info.value.errors()
        assert "The field Stock must be between 0 and 10 million." in str(errors[0]["msg"])

    def test_available_stock_exceeds_maximum(self):
        """Test BR-002: Available stock cannot exceed 10 million."""
        with pytest.raises(ValidationError) as exc_info:
            CatalogItemCreateDto(
                name="Test Product",
                price=Decimal("19.99"),
                catalog_brand_id=1,
                catalog_type_id=2,
                available_stock=99999999,
            )

        errors = exc_info.value.errors()
        assert "The field Stock must be between 0 and 10 million." in str(errors[0]["msg"])

    def test_available_stock_valid_maximum(self):
        """Test BR-002: Available stock can be exactly 10 million."""
        dto = CatalogItemCreateDto(
            name="Test Product",
            price=Decimal("19.99"),
            catalog_brand_id=1,
            catalog_type_id=2,
            available_stock=10_000_000,
        )

        assert dto.available_stock == 10_000_000

    def test_restock_threshold_negative(self):
        """Test BR-003: Restock threshold cannot be negative."""
        with pytest.raises(ValidationError) as exc_info:
            CatalogItemCreateDto(
                name="Test Product",
                price=Decimal("19.99"),
                catalog_brand_id=1,
                catalog_type_id=2,
                restock_threshold=-1,
            )

        errors = exc_info.value.errors()
        assert "The field Restock must be between 0 and 10 million." in str(errors[0]["msg"])

    def test_restock_threshold_exceeds_maximum(self):
        """Test BR-003: Restock threshold cannot exceed 10 million."""
        with pytest.raises(ValidationError) as exc_info:
            CatalogItemCreateDto(
                name="Test Product",
                price=Decimal("19.99"),
                catalog_brand_id=1,
                catalog_type_id=2,
                restock_threshold=99999999,
            )

        errors = exc_info.value.errors()
        assert "The field Restock must be between 0 and 10 million." in str(errors[0]["msg"])

    def test_max_stock_threshold_negative(self):
        """Test BR-004: Max stock threshold cannot be negative."""
        with pytest.raises(ValidationError) as exc_info:
            CatalogItemCreateDto(
                name="Test Product",
                price=Decimal("19.99"),
                catalog_brand_id=1,
                catalog_type_id=2,
                max_stock_threshold=-1,
            )

        errors = exc_info.value.errors()
        assert "The field Max stock must be between 0 and 10 million." in str(errors[0]["msg"])

    def test_max_stock_threshold_exceeds_maximum(self):
        """Test BR-004: Max stock threshold cannot exceed 10 million."""
        with pytest.raises(ValidationError) as exc_info:
            CatalogItemCreateDto(
                name="Test Product",
                price=Decimal("19.99"),
                catalog_brand_id=1,
                catalog_type_id=2,
                max_stock_threshold=99999999,
            )

        errors = exc_info.value.errors()
        assert "The field Max stock must be between 0 and 10 million." in str(errors[0]["msg"])


class TestUpdateCatalogItemValidation:
    """Test validation rules for CatalogItemUpdateDto (same as Create)."""

    def test_valid_update(self):
        """Test updating item with valid data."""
        dto = CatalogItemUpdateDto(
            name=".NET Bot Black Hoodie (Updated)",
            description="Updated description",
            price=Decimal("22.50"),
            catalog_brand_id=1,
            catalog_type_id=2,
            available_stock=150,
            restock_threshold=20,
            max_stock_threshold=300,
            picture_file_name="1.png",
        )

        assert dto.name == ".NET Bot Black Hoodie (Updated)"
        assert dto.price == Decimal("22.50")
        assert dto.available_stock == 150

    def test_name_required(self):
        """Test BR-005: Name is required on update."""
        with pytest.raises(ValidationError) as exc_info:
            CatalogItemUpdateDto(
                name="",
                price=Decimal("19.99"),
                catalog_brand_id=1,
                catalog_type_id=2,
                available_stock=100,
                restock_threshold=10,
                max_stock_threshold=200,
                picture_file_name="1.png",
            )

        errors = exc_info.value.errors()
        assert "The Name field is required." in str(errors[0]["msg"])

    def test_price_validation_same_as_create(self):
        """Test BR-001: Price validation is same as create."""
        with pytest.raises(ValidationError) as exc_info:
            CatalogItemUpdateDto(
                name="Test Product",
                price=Decimal("-5.00"),
                catalog_brand_id=1,
                catalog_type_id=2,
                available_stock=100,
                restock_threshold=10,
                max_stock_threshold=200,
                picture_file_name="1.png",
            )

        errors = exc_info.value.errors()
        assert (
            "The Price must be a positive number with maximum two decimals between 0 and 1 million."
            in str(errors[0]["msg"])
        )


class TestValidationErrorMessages:
    """Test exact validation error messages match legacy behavior."""

    def test_all_validation_scenarios_from_synthetic_data(self):
        """Test all validation scenarios from synthetic_validation_errors.json."""
        # Scenario 1: Empty name
        with pytest.raises(ValidationError) as exc_info:
            CatalogItemCreateDto(
                name="",
                price=Decimal("19.99"),
                catalog_brand_id=1,
                catalog_type_id=2,
            )
        assert "The Name field is required." in str(exc_info.value.errors()[0]["msg"])

        # Scenario 2: Negative price
        with pytest.raises(ValidationError) as exc_info:
            CatalogItemCreateDto(
                name="Test Product",
                price=Decimal("-5.00"),
                catalog_brand_id=1,
                catalog_type_id=2,
            )
        assert "The Price must be a positive number with maximum two decimals between 0 and 1 million." in str(
            exc_info.value.errors()[0]["msg"]
        )

        # Scenario 3: Too many decimal places
        with pytest.raises(ValidationError) as exc_info:
            CatalogItemCreateDto(
                name="Test Product",
                price=Decimal("12.999"),
                catalog_brand_id=1,
                catalog_type_id=2,
            )
        assert "The Price must be a positive number with maximum two decimals between 0 and 1 million." in str(
            exc_info.value.errors()[0]["msg"]
        )

        # Scenario 4: Price exceeds max
        with pytest.raises(ValidationError) as exc_info:
            CatalogItemCreateDto(
                name="Test Product",
                price=Decimal("2000000"),
                catalog_brand_id=1,
                catalog_type_id=2,
            )
        assert "The Price must be a positive number with maximum two decimals between 0 and 1 million." in str(
            exc_info.value.errors()[0]["msg"]
        )

        # Scenario 5: Stock exceeds max
        with pytest.raises(ValidationError) as exc_info:
            CatalogItemCreateDto(
                name="Test Product",
                price=Decimal("19.99"),
                catalog_brand_id=1,
                catalog_type_id=2,
                available_stock=99999999,
            )
        assert "The field Stock must be between 0 and 10 million." in str(exc_info.value.errors()[0]["msg"])
