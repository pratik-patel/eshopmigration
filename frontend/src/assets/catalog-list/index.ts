/**
 * Typed asset exports for catalog-list seam.
 *
 * Provides centralized, type-safe access to all static assets used by the catalog list page.
 * Prevents hardcoded paths and enables easy refactoring.
 *
 * Asset Sources:
 * - Product images: Legacy Pics/*.png copied to frontend/public/pics/
 * - CSS classes: Extracted from Content/Site.css to src/styles/index.css
 */

/**
 * Product image asset helpers.
 */
export const catalogAssets = {
  /**
   * Get the URL for a product image by ID.
   * @param id - Product ID (1-13)
   * @returns Public URL path to the product image
   */
  productImage: (id: number): string => `/pics/${id}.png`,

  /**
   * Get the URL for a product image by filename.
   * @param filename - Picture filename (e.g., "1.png", "2.png")
   * @returns Public URL path to the product image
   */
  productImageByFilename: (filename: string): string => `/pics/${filename}`,

  /**
   * Placeholder/fallback image for missing product images.
   */
  placeholder: '/pics/dummy.png',
} as const

/**
 * CSS class constants used in catalog list.
 *
 * These match the exact class names from the legacy Content/Site.css.
 * Do not modify - visual parity depends on these exact strings.
 */
export const catalogCssClasses = {
  // Table styles
  table: 'esh-table',
  tableHeader: 'esh-table-header',
  tableLink: 'esh-table-link',
  thumbnail: 'esh-thumbnail',
  price: 'esh-price',

  // Button styles
  button: 'esh-button',
  buttonPrimary: 'esh-button-primary',
  buttonSecondary: 'esh-button-secondary',
  buttonActions: 'esh-button-actions',

  // Pagination styles
  pager: 'esh-pager',
  pagerWrapper: 'esh-pager-wrapper',
  pagerItem: 'esh-pager-item',
  pagerItemNavigable: 'esh-pager-item--navigable',
  pagerItemHidden: 'esh-pager-item--hidden',

  // Link styles
  linkWrapper: 'esh-link-wrapper',
  linkItem: 'esh-link-item',
  linkItemMargin: 'esh-link-item--margin',
  linkList: 'esh-link-list',

  // Form styles
  formInformation: 'esh-form-information',

  // Picture display
  picture: 'esh-picture',

  // Body title
  bodyTitle: 'esh-body-title',
} as const

/**
 * Type guard to check if a filename is valid.
 */
export function isValidProductImageFilename(filename: string): boolean {
  return /^\d+\.png$/.test(filename) || filename === 'dummy.png'
}

/**
 * Get product image URL with fallback to placeholder.
 * @param filename - Picture filename or null
 * @returns Valid product image URL
 */
export function getProductImageUrl(filename: string | null | undefined): string {
  if (!filename) {
    return catalogAssets.placeholder
  }

  if (!isValidProductImageFilename(filename)) {
    console.warn(`Invalid product image filename: ${filename}. Using placeholder.`)
    return catalogAssets.placeholder
  }

  return catalogAssets.productImageByFilename(filename)
}
