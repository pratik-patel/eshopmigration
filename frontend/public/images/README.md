# Shared Layout Images

This directory contains shared layout assets used across all pages.

## Required Assets (from static-assets.json)

### Brand Logos
- **brand.png** - Header brand logo (light variant for dark backgrounds)
- **brand_dark.png** - Footer brand logo (dark variant for light backgrounds)
  - Dimensions: Approximately 230x50px
  - Format: PNG with transparency

### Hero Banner
- **main_banner.png** - Hero section background image
  - Format: PNG or JPG
  - Dimensions: Full-width, approximately 1440px wide
  - Usage: CSS `background-image: url('/images/main_banner.png')`

### Footer
- **main_footer_text.png** - Footer text image
  - Dimensions: 335x26px
  - Format: PNG
  - Usage: Footer branding text

### Favicon
- **favicon.ico** - Browser tab icon
  - Format: ICO (multi-size) or PNG
  - Location: `/public/favicon.ico` (root level)

## Legacy Migration Notes

All paths updated from legacy `~/images/` to `/images/` (served from this directory).

## To Populate This Directory

1. Copy assets from legacy application's `images` directory
2. Verify file names match exactly as listed above
3. Optimize images if >500KB
4. Test that assets load correctly in browser
