#!/bin/bash
# Copy all assets from legacy application to modern frontend
# Preserves original formats, resolutions, and file names

LEGACY_PATH="C:/Users/pratikp6/codebase/eShopModernizing/eShopModernizedWebFormsSolution/src/eShopModernizedWebForms"
MODERN_PATH="frontend/public"

echo "🎨 Copying legacy assets to modern frontend..."
echo ""

# Create directories
mkdir -p "$MODERN_PATH/images"
mkdir -p "$MODERN_PATH/images/pics"
mkdir -p "docs/legacy-reference"

# Copy brand assets
echo "📦 Copying brand assets..."
if [ -f "$LEGACY_PATH/images/brand.png" ]; then
    cp "$LEGACY_PATH/images/brand.png" "$MODERN_PATH/images/"
    echo "  ✅ brand.png"
else
    echo "  ⚠️  brand.png not found"
fi

if [ -f "$LEGACY_PATH/images/brand_dark.png" ]; then
    cp "$LEGACY_PATH/images/brand_dark.png" "$MODERN_PATH/images/"
    echo "  ✅ brand_dark.png"
else
    echo "  ⚠️  brand_dark.png not found"
fi

if [ -f "$LEGACY_PATH/images/main_footer_text.png" ]; then
    cp "$LEGACY_PATH/images/main_footer_text.png" "$MODERN_PATH/images/"
    echo "  ✅ main_footer_text.png"
else
    echo "  ⚠️  main_footer_text.png not found"
fi

# Copy product images
echo ""
echo "🖼️  Copying product images..."
if [ -d "$LEGACY_PATH/Pics" ]; then
    cp -r "$LEGACY_PATH/Pics/"* "$MODERN_PATH/images/pics/" 2>/dev/null
    pic_count=$(ls "$MODERN_PATH/images/pics" | wc -l)
    echo "  ✅ Copied $pic_count product images"
else
    echo "  ⚠️  Pics directory not found"
fi

# Copy CSS for reference
echo ""
echo "📄 Copying CSS for reference..."
if [ -f "$LEGACY_PATH/Content/Site.css" ]; then
    cp "$LEGACY_PATH/Content/Site.css" "docs/legacy-reference/Site.css"
    echo "  ✅ Site.css → docs/legacy-reference/"
else
    echo "  ⚠️  Site.css not found"
fi

# Create asset inventory
echo ""
echo "📋 Creating asset inventory..."
cat > "docs/asset-inventory.json" << INVENTORY
{
  "generated": "$(date -Iseconds)",
  "source": "$LEGACY_PATH",
  "destination": "$MODERN_PATH",
  "assets": {
    "brand_logo": {
      "legacy_path": "images/brand.png",
      "modern_path": "frontend/public/images/brand.png",
      "format": "PNG",
      "copied": $([ -f "$MODERN_PATH/images/brand.png" ] && echo "true" || echo "false")
    },
    "brand_logo_dark": {
      "legacy_path": "images/brand_dark.png",
      "modern_path": "frontend/public/images/brand_dark.png",
      "format": "PNG",
      "copied": $([ -f "$MODERN_PATH/images/brand_dark.png" ] && echo "true" || echo "false")
    },
    "footer_text": {
      "legacy_path": "images/main_footer_text.png",
      "modern_path": "frontend/public/images/main_footer_text.png",
      "format": "PNG",
      "copied": $([ -f "$MODERN_PATH/images/main_footer_text.png" ] && echo "true" || echo "false")
    }
  }
}
INVENTORY
echo "  ✅ Created docs/asset-inventory.json"

echo ""
echo "✅ Asset copy complete!"
echo ""
echo "📊 Summary:"
echo "  - Brand assets: $MODERN_PATH/images/"
echo "  - Product images: $MODERN_PATH/images/pics/"
echo "  - CSS reference: docs/legacy-reference/Site.css"
echo "  - Inventory: docs/asset-inventory.json"
