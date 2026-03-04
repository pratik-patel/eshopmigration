/**
 * Catalog API client functions.
 *
 * All functions match OpenAPI contract endpoints and return typed responses.
 */

import { api } from "./client";
import type {
  CatalogItemListResponse,
  CatalogItemResponse,
  CatalogItemCreate,
  CatalogItemUpdate,
  BrandResponse,
  TypeResponse,
  TempImageResponse,
} from "@/types/api";

// ============================================================================
// Catalog Items API
// ============================================================================

/**
 * List catalog items with pagination.
 *
 * @param page - Page number (zero-based, default 0)
 * @param limit - Items per page (1-100, default 10)
 * @returns Paginated list of catalog items
 */
export async function listCatalogItems(
  page = 0,
  limit = 10
): Promise<CatalogItemListResponse> {
  return api.get<CatalogItemListResponse>(
    `/catalog/items?page=${page}&limit=${limit}`
  );
}

/**
 * Get catalog item by ID.
 *
 * @param id - Catalog item ID
 * @returns Catalog item details with brand and type
 */
export async function getCatalogItem(id: number): Promise<CatalogItemResponse> {
  return api.get<CatalogItemResponse>(`/catalog/items/${id}`);
}

/**
 * Create new catalog item.
 *
 * @param data - Catalog item creation data
 * @returns Created catalog item with assigned ID
 */
export async function createCatalogItem(
  data: CatalogItemCreate
): Promise<CatalogItemResponse> {
  return api.post<CatalogItemResponse>("/catalog/items", data);
}

/**
 * Update existing catalog item.
 *
 * @param id - Catalog item ID
 * @param data - Updated catalog item data
 * @returns Updated catalog item
 */
export async function updateCatalogItem(
  id: number,
  data: CatalogItemUpdate
): Promise<CatalogItemResponse> {
  return api.put<CatalogItemResponse>(`/catalog/items/${id}`, data);
}

/**
 * Delete catalog item.
 *
 * @param id - Catalog item ID
 * @returns void (204 No Content)
 */
export async function deleteCatalogItem(id: number): Promise<void> {
  return api.delete<void>(`/catalog/items/${id}`);
}

// ============================================================================
// Lookup APIs
// ============================================================================

/**
 * List all catalog brands.
 *
 * @returns List of all brands (sorted by name)
 */
export async function listBrands(): Promise<BrandResponse[]> {
  return api.get<BrandResponse[]>("/catalog/brands");
}

/**
 * List all catalog types.
 *
 * @returns List of all types (sorted by name)
 */
export async function listTypes(): Promise<TypeResponse[]> {
  return api.get<TypeResponse[]>("/catalog/types");
}

// ============================================================================
// Image Upload API
// ============================================================================

/**
 * Upload temporary product image.
 *
 * @param file - Image file to upload (.jpg, .jpeg, .png, .gif)
 * @returns Temporary filename to use in catalog item creation/update
 */
export async function uploadProductImage(
  file: File
): Promise<TempImageResponse> {
  return api.uploadFile<TempImageResponse>("/images/upload", file);
}
