/**
 * Typed exports for catalog assets
 * All asset paths are managed here for type safety and maintainability
 */

export const catalogAssets = {
  // Product images (dynamic, served from public/Pics/)
  productImagePath: (filename: string) => `/Pics/${filename}`,

  // Default placeholder for missing product images
  dummyImage: '/Pics/dummy.png',

  // Shared layout assets (from public/images/)
  brandLogo: '/images/brand.png',
  brandLogoDark: '/images/brand_dark.png',
  mainBanner: '/images/main_banner.png',
  footerText: '/images/main_footer_text.png',

  // Action icons (if needed, served from src/assets/catalog/icons/)
  // Icons would be imported as modules for optimization
  // saveIcon: new URL('./icons/save.svg', import.meta.url).href,
} as const;

export type CatalogAsset = keyof typeof catalogAssets;

/**
 * Helper to construct full product image URI
 * Matches legacy PictureUri computed property pattern
 */
export function getProductImageUri(pictureFileName: string | null | undefined): string {
  if (!pictureFileName || pictureFileName.trim() === '') {
    return catalogAssets.dummyImage;
  }
  return catalogAssets.productImagePath(pictureFileName);
}

/**
 * Helper to get brand logo based on context (header vs footer)
 */
export function getBrandLogo(variant: 'light' | 'dark' = 'light'): string {
  return variant === 'dark' ? catalogAssets.brandLogoDark : catalogAssets.brandLogo;
}
