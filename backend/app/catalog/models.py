"""
SQLAlchemy models for catalog management seam.

Maps to legacy database schema (Catalog, CatalogBrand, CatalogType tables).
Preserves exact column names and relationships from ASP.NET Entity Framework models.
"""

from sqlalchemy import Column, Integer, String, Numeric, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship, DeclarativeBase
from typing import Optional


class Base(DeclarativeBase):
    """Base class for all models."""
    pass


class CatalogBrand(Base):
    """
    CatalogBrand lookup table.
    Maps to legacy CatalogBrand table (read-only in this seam).
    """
    __tablename__ = "CatalogBrand"

    Id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    Brand = Column(String(100), nullable=False)

    # Relationship to catalog items
    catalog_items = relationship("CatalogItem", back_populates="brand")

    def __repr__(self) -> str:
        return f"<CatalogBrand(Id={self.Id}, Brand='{self.Brand}')>"


class CatalogType(Base):
    """
    CatalogType lookup table.
    Maps to legacy CatalogType table (read-only in this seam).
    """
    __tablename__ = "CatalogType"

    Id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    Type = Column(String(100), nullable=False)

    # Relationship to catalog items
    catalog_items = relationship("CatalogItem", back_populates="type")

    def __repr__(self) -> str:
        return f"<CatalogType(Id={self.Id}, Type='{self.Type}')>"


class CatalogItem(Base):
    """
    CatalogItem entity.
    Maps to legacy Catalog table (full CRUD access).

    Column names preserved exactly from legacy Entity Framework model:
    - Id (not id)
    - Name (not name)
    - PictureFileName (not picture_file_name)
    - CatalogBrandId (not catalog_brand_id)
    - CatalogTypeId (not catalog_type_id)

    This ensures SQL queries match legacy schema exactly.
    """
    __tablename__ = "Catalog"

    # Primary key (auto-increment, replaces legacy HiLo pattern)
    Id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Product information
    Name = Column(String(50), nullable=False)
    Description = Column(String, nullable=True)
    Price = Column(Numeric(18, 2), nullable=False)  # Decimal with 2 decimal places
    PictureFileName = Column(String(255), nullable=False, default="dummy.png")

    # Foreign keys (indexed for performance via __table_args__)
    CatalogTypeId = Column(Integer, ForeignKey("CatalogType.Id"), nullable=False)
    CatalogBrandId = Column(Integer, ForeignKey("CatalogBrand.Id"), nullable=False)

    # Stock management
    AvailableStock = Column(Integer, nullable=False, default=0)
    RestockThreshold = Column(Integer, nullable=False, default=0)
    MaxStockThreshold = Column(Integer, nullable=False, default=0)
    OnReorder = Column(Boolean, nullable=False, default=False)

    # Relationships (eager loading with selectinload in queries)
    brand = relationship("CatalogBrand", back_populates="catalog_items")
    type = relationship("CatalogType", back_populates="catalog_items")

    # Indexes for performance (named to match legacy schema)
    __table_args__ = (
        Index("IX_Catalog_CatalogBrandId", "CatalogBrandId"),
        Index("IX_Catalog_CatalogTypeId", "CatalogTypeId"),
    )

    def __repr__(self) -> str:
        return f"<CatalogItem(Id={self.Id}, Name='{self.Name}', Price={self.Price})>"

    @property
    def picture_uri(self) -> str:
        """
        Computed property for full image URI.
        Matches legacy PictureUri computed property pattern.
        Returns: /Pics/{PictureFileName}
        """
        return f"/Pics/{self.PictureFileName}"
