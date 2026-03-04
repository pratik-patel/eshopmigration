"""Simple synchronous seed script."""
import sqlite3
from decimal import Decimal

# Connect to database
conn = sqlite3.connect('eshop.db')
cursor = conn.cursor()

# Seed brands
brands = ["Azure", ".NET", "Visual Studio", "SQL Server", "Other"]
for brand in brands:
    cursor.execute("INSERT INTO CatalogBrand (Brand) VALUES (?)", (brand,))

# Seed types
types = ["T-Shirt", "Mug", "Sheet", "USB Memory Stick", "Posters"]
for catalog_type in types:
    cursor.execute("INSERT INTO CatalogType (Type) VALUES (?)", (catalog_type,))

# Seed catalog items
items = [
    (".NET Bot Black Hoodie", "A stylish black hoodie", 19.50, "1.png", 2, 1, 100, 10, 200, False),
    (".NET Black & White Mug", "Classic mug", 8.50, "2.png", 2, 2, 89, 10, 150, False),
    ("Prism White T-Shirt", "White t-shirt with Prism logo", 12.00, "3.png", 2, 1, 56, 10, 100, False),
    ("Azure Blue Hoodie", "Azure branded blue hoodie", 22.00, "4.png", 1, 1, 45, 10, 100, False),
    ("Azure Logo Mug", "Coffee mug with Azure logo", 7.99, "5.png", 1, 2, 120, 15, 200, False),
    ("Azure Stickers Sheet", "Sheet of Azure logo stickers", 3.50, "6.png", 1, 3, 200, 20, 300, False),
    ("VS Logo Purple Hoodie", "Purple hoodie with Visual Studio logo", 24.00, "7.png", 3, 1, 30, 5, 80, False),
    ("VS Blue Mug", "Blue mug with Visual Studio branding", 9.50, "8.png", 3, 2, 75, 10, 120, False),
    ("VS USB 32GB", "32GB USB memory stick with VS logo", 15.00, "9.png", 3, 4, 40, 8, 80, False),
    ("SQL Server 2022 Poster", "Promotional poster for SQL Server 2022", 5.00, "10.png", 4, 5, 150, 20, 250, False),
    ("SQL Logo Mug", "White mug with SQL Server logo", 8.00, "11.png", 4, 2, 90, 12, 150, False),
    ("SQL Server T-Shirt", "Black t-shirt with SQL Server branding", 14.00, "12.png", 4, 1, 65, 10, 120, False),
    ("Cup<T> White Mug", "Developer humor mug", 12.00, "13.png", 5, 2, 76, 10, 150, False),
    ("Modern .NET Black & White Mug", "Modern .NET branding", 10.50, "14.png", 2, 2, 88, 10, 140, False),
    ("Code Monkey Poster", "Fun developer poster", 6.50, "15.png", 5, 5, 110, 15, 200, False),
    ("Developer USB 64GB", "64GB USB drive", 20.00, "16.png", 5, 4, 25, 5, 60, False),
    ("Azure Functions Stickers", "Sticker pack for Azure Functions", 4.00, "17.png", 1, 3, 180, 25, 300, False),
    ("Roslyn Red Sheet", "Roslyn compiler stickers sheet", 3.00, "18.png", 2, 3, 140, 18, 250, False),
    ("VS Code Blue Hoodie", "VS Code branded blue hoodie", 21.00, "19.png", 3, 1, 38, 8, 90, False),
    ("GitHub Octocat Poster", "Classic GitHub Octocat poster", 7.50, "20.png", 5, 5, 95, 12, 180, False),
]

for item in items:
    cursor.execute("""
        INSERT INTO Catalog (Name, Description, Price, PictureFileName, CatalogBrandId, CatalogTypeId,
                             AvailableStock, RestockThreshold, MaxStockThreshold, OnReorder)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, item)

conn.commit()

# Verify
cursor.execute("SELECT COUNT(*) FROM CatalogBrand")
print(f"[OK] Brands: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM CatalogType")
print(f"[OK] Types: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM Catalog")
print(f"[OK] Items: {cursor.fetchone()[0]}")

conn.close()
print("[OK] Seed complete!")
