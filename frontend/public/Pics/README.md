# Product Images Directory

This directory contains product catalog images referenced by `CatalogItem.PictureFileName`.

## Required Assets

### Default Placeholder
- **dummy.png** - Default image when no product image is uploaded (max 50KB)
  - Dimensions: 370x370px or similar
  - Format: PNG
  - Should display "No Image Available" or similar placeholder text

### Product Images
Product images are dynamically uploaded and stored here with filenames matching the database records.

- **Format**: JPG or PNG
- **Max size**: 10MB per image
- **Naming**: UUID-based or sequential (e.g., `1.png`, `2.jpg`, `abc123-uuid.jpg`)
- **Optimization**: Compress images >500KB before uploading

## Legacy Migration Notes

From `static-assets.json`:
- Legacy path: `~/Pics/{dynamic-filename}`
- Modern path: `/Pics/{dynamic-filename}` (served from this directory)
- Images used in: List view (thumbnail 120px max), Create/Edit/Details/Delete views (preview 370px max)
- CSS classes: `.esh-thumbnail`, `.esh-picture`

## To Populate This Directory

1. Copy product images from legacy application's `Pics` directory
2. Create `dummy.png` placeholder if not present
3. Optimize images >500KB using compression tools
4. Verify images display correctly in catalog views

## Asset Verification

Run this command to verify assets are accessible:
```bash
curl http://localhost:5173/Pics/dummy.png
```
