/**
 * Catalog API client methods.
 */

import { apiGet, apiPost, apiPut, apiDelete } from './client'

/**
 * Catalog brand DTO.
 */
export interface CatalogBrand {
  id: number
  brand: string
}

/**
 * Catalog type DTO.
 */
export interface CatalogType {
  id: number
  type: string
}

/**
 * Catalog item DTO.
 */
export interface CatalogItem {
  id: number
  name: string
  description: string | null
  price: number
  picture_file_name: string
  picture_uri: string | null
  catalog_type_id: number
  catalog_brand_id: number
  available_stock: number
  restock_threshold: number
  max_stock_threshold: number
  on_reorder: boolean
  catalog_type: CatalogType
  catalog_brand: CatalogBrand
}

/**
 * Paginated catalog items response.
 */
export interface PaginatedCatalogItemsResponse {
  page_index: number
  page_size: number
  total_items: number
  total_pages: number
  data: CatalogItem[]
}

/**
 * Catalog item create request.
 */
export interface CatalogItemCreateRequest {
  name: string
  description?: string | null
  price: number
  catalog_type_id: number
  catalog_brand_id: number
  available_stock?: number
  restock_threshold?: number
  max_stock_threshold?: number
  picture_file_name?: string
}

/**
 * Catalog item update request.
 */
export interface CatalogItemUpdateRequest {
  name: string
  description?: string | null
  price: number
  catalog_type_id: number
  catalog_brand_id: number
  available_stock: number
  restock_threshold: number
  max_stock_threshold: number
  picture_file_name: string
}

/**
 * Get paginated catalog items.
 */
export async function getCatalogItems(
  pageSize: number = 10,
  pageIndex: number = 0
): Promise<PaginatedCatalogItemsResponse> {
  return apiGet<PaginatedCatalogItemsResponse>(
    `/catalog/items?page_size=${pageSize}&page_index=${pageIndex}`
  )
}

/**
 * Get single catalog item by ID.
 */
export async function getCatalogItem(id: number): Promise<CatalogItem> {
  return apiGet<CatalogItem>(`/catalog/items/${id}`)
}

/**
 * Create new catalog item.
 */
export async function createCatalogItem(
  data: CatalogItemCreateRequest
): Promise<CatalogItem> {
  return apiPost<CatalogItem>(`/catalog/items`, data)
}

/**
 * Update existing catalog item.
 */
export async function updateCatalogItem(
  id: number,
  data: CatalogItemUpdateRequest
): Promise<CatalogItem> {
  return apiPut<CatalogItem>(`/catalog/items/${id}`, data)
}

/**
 * Delete catalog item.
 */
export async function deleteCatalogItem(id: number): Promise<void> {
  return apiDelete<void>(`/catalog/items/${id}`)
}

/**
 * Get all catalog brands.
 */
export async function getCatalogBrands(): Promise<CatalogBrand[]> {
  return apiGet<CatalogBrand[]>('/catalog/brands')
}

/**
 * Get all catalog types.
 */
export async function getCatalogTypes(): Promise<CatalogType[]> {
  return apiGet<CatalogType[]>('/catalog/types')
}
