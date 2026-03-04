"""
Seed data script for catalog management.

Populates:
- CatalogBrand table (5+ brands)
- CatalogType table (5+ types)
- Catalog table (20+ sample items)

Usage:
    python backend/seeds/catalog_seed.py
"""

import sys
from pathlib import Path

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.catalog.models import Base, CatalogBrand, CatalogType, CatalogItem


# Database connection (SQLite for POC, Postgres in production)
DATABASE_URL = "sqlite:///./eshop.db"

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def seed_brands(session):
    """Seed CatalogBrand table."""
    brands = [
        CatalogBrand(Brand="Azure"),
        CatalogBrand(Brand=".NET"),
        CatalogBrand(Brand="Visual Studio"),
        CatalogBrand(Brand="SQL Server"),
        CatalogBrand(Brand="Other"),
    ]

    for brand in brands:
        existing = session.query(CatalogBrand).filter_by(Brand=brand.Brand).first()
        if not existing:
            session.add(brand)
            print(f"Added brand: {brand.Brand}")
        else:
            print(f"Brand already exists: {brand.Brand}")

    session.commit()
    print(f"✓ Seeded {len(brands)} brands")


def seed_types(session):
    """Seed CatalogType table."""
    types = [
        CatalogType(Type="T-Shirt"),
        CatalogType(Type="Mug"),
        CatalogType(Type="Sheet"),
        CatalogType(Type="USB Memory Stick"),
        CatalogType(Type="Posters"),
    ]

    for catalog_type in types:
        existing = session.query(CatalogType).filter_by(Type=catalog_type.Type).first()
        if not existing:
            session.add(catalog_type)
            print(f"Added type: {catalog_type.Type}")
        else:
            print(f"Type already exists: {catalog_type.Type}")

    session.commit()
    print(f"✓ Seeded {len(types)} types")


def seed_catalog_items(session):
    """Seed Catalog table with sample items."""
    # Get brand and type IDs
    azure_brand = session.query(CatalogBrand).filter_by(Brand="Azure").first()
    dotnet_brand = session.query(CatalogBrand).filter_by(Brand=".NET").first()
    vs_brand = session.query(CatalogBrand).filter_by(Brand="Visual Studio").first()
    sql_brand = session.query(CatalogBrand).filter_by(Brand="SQL Server").first()
    other_brand = session.query(CatalogBrand).filter_by(Brand="Other").first()

    tshirt_type = session.query(CatalogType).filter_by(Type="T-Shirt").first()
    mug_type = session.query(CatalogType).filter_by(Type="Mug").first()
    sheet_type = session.query(CatalogType).filter_by(Type="Sheet").first()
    usb_type = session.query(CatalogType).filter_by(Type="USB Memory Stick").first()
    poster_type = session.query(CatalogType).filter_by(Type="Posters").first()

    items = [
        # .NET Bot products
        CatalogItem(
            Name=".NET Bot Black Hoodie",
            Description="A stylish black hoodie with .NET Bot logo",
            Price=19.50,
            PictureFileName="1.png",
            CatalogBrandId=dotnet_brand.Id,
            CatalogTypeId=tshirt_type.Id,
            AvailableStock=100,
            RestockThreshold=10,
            MaxStockThreshold=200,
        ),
        CatalogItem(
            Name=".NET Black & White Mug",
            Description="Classic .NET mug in black and white",
            Price=8.50,
            PictureFileName="2.png",
            CatalogBrandId=dotnet_brand.Id,
            CatalogTypeId=mug_type.Id,
            AvailableStock=89,
            RestockThreshold=10,
            MaxStockThreshold=150,
        ),
        CatalogItem(
            Name="Prism White T-Shirt",
            Description="White t-shirt with Prism logo",
            Price=12.00,
            PictureFileName="3.png",
            CatalogBrandId=dotnet_brand.Id,
            CatalogTypeId=tshirt_type.Id,
            AvailableStock=56,
            RestockThreshold=10,
            MaxStockThreshold=100,
        ),

        # Azure products
        CatalogItem(
            Name="Azure Blue Hoodie",
            Description="Azure branded blue hoodie",
            Price=22.00,
            PictureFileName="4.png",
            CatalogBrandId=azure_brand.Id,
            CatalogTypeId=tshirt_type.Id,
            AvailableStock=45,
            RestockThreshold=10,
            MaxStockThreshold=100,
        ),
        CatalogItem(
            Name="Azure Logo Mug",
            Description="Coffee mug with Azure logo",
            Price=7.99,
            PictureFileName="5.png",
            CatalogBrandId=azure_brand.Id,
            CatalogTypeId=mug_type.Id,
            AvailableStock=120,
            RestockThreshold=15,
            MaxStockThreshold=200,
        ),
        CatalogItem(
            Name="Azure Stickers Sheet",
            Description="Sheet of Azure logo stickers",
            Price=3.50,
            PictureFileName="6.png",
            CatalogBrandId=azure_brand.Id,
            CatalogTypeId=sheet_type.Id,
            AvailableStock=200,
            RestockThreshold=20,
            MaxStockThreshold=300,
        ),

        # Visual Studio products
        CatalogItem(
            Name="VS Logo Purple Hoodie",
            Description="Purple hoodie with Visual Studio logo",
            Price=24.00,
            PictureFileName="7.png",
            CatalogBrandId=vs_brand.Id,
            CatalogTypeId=tshirt_type.Id,
            AvailableStock=30,
            RestockThreshold=5,
            MaxStockThreshold=80,
        ),
        CatalogItem(
            Name="VS Blue Mug",
            Description="Blue mug with Visual Studio branding",
            Price=9.50,
            PictureFileName="8.png",
            CatalogBrandId=vs_brand.Id,
            CatalogTypeId=mug_type.Id,
            AvailableStock=75,
            RestockThreshold=10,
            MaxStockThreshold=120,
        ),
        CatalogItem(
            Name="VS USB 32GB",
            Description="32GB USB memory stick with VS logo",
            Price=15.00,
            PictureFileName="9.png",
            CatalogBrandId=vs_brand.Id,
            CatalogTypeId=usb_type.Id,
            AvailableStock=40,
            RestockThreshold=8,
            MaxStockThreshold=80,
        ),

        # SQL Server products
        CatalogItem(
            Name="SQL Server 2022 Poster",
            Description="Promotional poster for SQL Server 2022",
            Price=5.00,
            PictureFileName="10.png",
            CatalogBrandId=sql_brand.Id,
            CatalogTypeId=poster_type.Id,
            AvailableStock=150,
            RestockThreshold=20,
            MaxStockThreshold=250,
        ),
        CatalogItem(
            Name="SQL Logo Mug",
            Description="White mug with SQL Server logo",
            Price=8.00,
            PictureFileName="11.png",
            CatalogBrandId=sql_brand.Id,
            CatalogTypeId=mug_type.Id,
            AvailableStock=90,
            RestockThreshold=12,
            MaxStockThreshold=150,
        ),
        CatalogItem(
            Name="SQL Server T-Shirt",
            Description="Black t-shirt with SQL Server branding",
            Price=14.00,
            PictureFileName="12.png",
            CatalogBrandId=sql_brand.Id,
            CatalogTypeId=tshirt_type.Id,
            AvailableStock=65,
            RestockThreshold=10,
            MaxStockThreshold=120,
        ),

        # Other brand products
        CatalogItem(
            Name="Cup<T> White Mug",
            Description="Developer humor mug - Cup<T>",
            Price=12.00,
            PictureFileName="13.png",
            CatalogBrandId=other_brand.Id,
            CatalogTypeId=mug_type.Id,
            AvailableStock=76,
            RestockThreshold=10,
            MaxStockThreshold=150,
        ),
        CatalogItem(
            Name="Modern .NET Black & White Mug",
            Description="Modern .NET branding on ceramic mug",
            Price=10.50,
            PictureFileName="14.png",
            CatalogBrandId=dotnet_brand.Id,
            CatalogTypeId=mug_type.Id,
            AvailableStock=88,
            RestockThreshold=10,
            MaxStockThreshold=140,
        ),
        CatalogItem(
            Name="Code Monkey Poster",
            Description="Fun developer poster",
            Price=6.50,
            PictureFileName="15.png",
            CatalogBrandId=other_brand.Id,
            CatalogTypeId=poster_type.Id,
            AvailableStock=110,
            RestockThreshold=15,
            MaxStockThreshold=200,
        ),
        CatalogItem(
            Name="Developer USB 64GB",
            Description="64GB USB drive with developer branding",
            Price=20.00,
            PictureFileName="16.png",
            CatalogBrandId=other_brand.Id,
            CatalogTypeId=usb_type.Id,
            AvailableStock=25,
            RestockThreshold=5,
            MaxStockThreshold=60,
        ),
        CatalogItem(
            Name="Azure Functions Stickers",
            Description="Sticker pack for Azure Functions",
            Price=4.00,
            PictureFileName="17.png",
            CatalogBrandId=azure_brand.Id,
            CatalogTypeId=sheet_type.Id,
            AvailableStock=180,
            RestockThreshold=25,
            MaxStockThreshold=300,
        ),
        CatalogItem(
            Name="Roslyn Red Sheet",
            Description="Roslyn compiler stickers sheet",
            Price=3.00,
            PictureFileName="18.png",
            CatalogBrandId=dotnet_brand.Id,
            CatalogTypeId=sheet_type.Id,
            AvailableStock=140,
            RestockThreshold=18,
            MaxStockThreshold=250,
        ),
        CatalogItem(
            Name="VS Code Blue Hoodie",
            Description="VS Code branded blue hoodie",
            Price=21.00,
            PictureFileName="19.png",
            CatalogBrandId=vs_brand.Id,
            CatalogTypeId=tshirt_type.Id,
            AvailableStock=38,
            RestockThreshold=8,
            MaxStockThreshold=90,
        ),
        CatalogItem(
            Name="GitHub Octocat Poster",
            Description="Classic GitHub Octocat poster",
            Price=7.50,
            PictureFileName="20.png",
            CatalogBrandId=other_brand.Id,
            CatalogTypeId=poster_type.Id,
            AvailableStock=95,
            RestockThreshold=12,
            MaxStockThreshold=180,
        ),
    ]

    for item in items:
        existing = session.query(CatalogItem).filter_by(Name=item.Name).first()
        if not existing:
            session.add(item)
            print(f"Added item: {item.Name} (${item.Price})")
        else:
            print(f"Item already exists: {item.Name}")

    session.commit()
    print(f"✓ Seeded {len(items)} catalog items")


def main():
    """Main seed function."""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created")

    session = SessionLocal()

    try:
        print("\nSeeding CatalogBrand table...")
        seed_brands(session)

        print("\nSeeding CatalogType table...")
        seed_types(session)

        print("\nSeeding Catalog table...")
        seed_catalog_items(session)

        print("\n✅ Seed complete!")
        print(f"  - Brands: {session.query(CatalogBrand).count()}")
        print(f"  - Types: {session.query(CatalogType).count()}")
        print(f"  - Items: {session.query(CatalogItem).count()}")

    except Exception as e:
        print(f"\n❌ Seed failed: {e}")
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
