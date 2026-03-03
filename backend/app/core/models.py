"""
SQLAlchemy ORM models for eShop catalog.

Migrated from Entity Framework 6 models in legacy ASP.NET WebForms application.
"""

from decimal import Decimal
from sqlalchemy import String, Integer, Boolean, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class CatalogBrand(Base):
    """
    Catalog brand/manufacturer entity.

    Legacy: eShopLegacyWebForms.Models.CatalogBrand
    """

    __tablename__ = "catalog_brands"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    brand: Mapped[str] = mapped_column(String, nullable=False)

    # Relationships
    catalog_items: Mapped[list["CatalogItem"]] = relationship(
        back_populates="catalog_brand",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<CatalogBrand(id={self.id}, brand='{self.brand}')>"


class CatalogType(Base):
    """
    Catalog type/category entity.

    Legacy: eShopLegacyWebForms.Models.CatalogType
    """

    __tablename__ = "catalog_types"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    type: Mapped[str] = mapped_column(String, nullable=False)

    # Relationships
    catalog_items: Mapped[list["CatalogItem"]] = relationship(
        back_populates="catalog_type",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<CatalogType(id={self.id}, type='{self.type}')>"


class CatalogItem(Base):
    """
    Catalog item (product) entity.

    Legacy: eShopLegacyWebForms.Models.CatalogItem

    Business Rules:
    - BR-001: Price must be positive decimal with max 2 decimals, range 0-9999999999999999.99
    - BR-002: AvailableStock must be 0-10,000,000
    - BR-003: RestockThreshold must be 0-10,000,000
    - BR-004: MaxStockThreshold must be 0-10,000,000
    - BR-005: PictureFileName defaults to 'dummy.png'
    - BR-013: Must have valid CatalogType (foreign key)
    - BR-014: Must have valid CatalogBrand (foreign key)
    """

    __tablename__ = "catalog_items"

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Basic fields
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    price: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),  # decimal(18,2) from legacy
        nullable=False,
    )

    # Picture fields
    picture_file_name: Mapped[str] = mapped_column(
        String,
        nullable=False,
        default="dummy.png",
    )
    picture_uri: Mapped[str | None] = mapped_column(String, nullable=True)

    # Foreign keys
    catalog_type_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("catalog_types.id"),
        nullable=False,
    )
    catalog_brand_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("catalog_brands.id"),
        nullable=False,
    )

    # Stock fields
    available_stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    restock_threshold: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_stock_threshold: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Reorder flag
    on_reorder: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Relationships
    catalog_type: Mapped["CatalogType"] = relationship(back_populates="catalog_items")
    catalog_brand: Mapped["CatalogBrand"] = relationship(back_populates="catalog_items")

    def __repr__(self) -> str:
        return f"<CatalogItem(id={self.id}, name='{self.name}', price={self.price})>"
