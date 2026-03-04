/**
 * TanStack Query hooks for catalog operations.
 *
 * Provides data fetching, caching, and mutations for catalog items.
 * All hooks follow React Query best practices with proper cache invalidation.
 */

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  listCatalogItems,
  getCatalogItem,
  createCatalogItem,
  updateCatalogItem,
  deleteCatalogItem,
  listBrands,
  listTypes,
  uploadProductImage,
} from "@/api/catalog";
import type {
  CatalogItemCreate,
  CatalogItemUpdate,
  CatalogItemResponse,
  CatalogItemListResponse,
} from "@/types/api";

// ============================================================================
// Query Hooks (Data Fetching)
// ============================================================================

/**
 * Fetch paginated list of catalog items.
 *
 * @param page - Page number (zero-based, default 0)
 * @param limit - Items per page (default 10)
 * @returns Query result with items and pagination metadata
 */
export function useCatalogItems(page = 0, limit = 10) {
  return useQuery<CatalogItemListResponse>({
    queryKey: ["catalog", "items", { page, limit }],
    queryFn: () => listCatalogItems(page, limit),
    staleTime: 30000, // 30 seconds
    placeholderData: (previousData) => previousData, // Keep previous data while loading
  });
}

/**
 * Fetch single catalog item by ID.
 *
 * @param id - Catalog item ID
 * @returns Query result with catalog item details
 */
export function useCatalogItem(id: number) {
  return useQuery<CatalogItemResponse>({
    queryKey: ["catalog", "item", id],
    queryFn: () => getCatalogItem(id),
    staleTime: 60000, // 1 minute
    enabled: !!id && id > 0, // Only fetch if ID is valid
  });
}

/**
 * Fetch all catalog brands.
 *
 * Used to populate brand dropdown in forms.
 *
 * @returns Query result with list of brands
 */
export function useBrands() {
  return useQuery({
    queryKey: ["catalog", "brands"],
    queryFn: listBrands,
    staleTime: 300000, // 5 minutes (brands rarely change)
  });
}

/**
 * Fetch all catalog types.
 *
 * Used to populate type dropdown in forms.
 *
 * @returns Query result with list of types
 */
export function useTypes() {
  return useQuery({
    queryKey: ["catalog", "types"],
    queryFn: listTypes,
    staleTime: 300000, // 5 minutes (types rarely change)
  });
}

// ============================================================================
// Mutation Hooks (Data Modification)
// ============================================================================

/**
 * Create new catalog item.
 *
 * Automatically invalidates catalog list cache on success.
 *
 * @returns Mutation with create function
 */
export function useCreateCatalogItem() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CatalogItemCreate) => createCatalogItem(data),
    onSuccess: (newItem) => {
      // Invalidate and refetch catalog list
      queryClient.invalidateQueries({ queryKey: ["catalog", "items"] });

      // Optimistically add to cache
      queryClient.setQueryData(["catalog", "item", newItem.id], newItem);
    },
  });
}

/**
 * Update existing catalog item.
 *
 * Automatically updates cache and invalidates list on success.
 *
 * @returns Mutation with update function
 */
export function useUpdateCatalogItem() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: CatalogItemUpdate }) =>
      updateCatalogItem(id, data),
    onSuccess: (updatedItem, variables) => {
      // Update item cache
      queryClient.setQueryData(
        ["catalog", "item", variables.id],
        updatedItem
      );

      // Invalidate list to reflect changes
      queryClient.invalidateQueries({ queryKey: ["catalog", "items"] });
    },
  });
}

/**
 * Delete catalog item.
 *
 * Automatically removes from cache and invalidates list on success.
 *
 * @returns Mutation with delete function
 */
export function useDeleteCatalogItem() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => deleteCatalogItem(id),
    onSuccess: (_, deletedId) => {
      // Remove from item cache
      queryClient.removeQueries({ queryKey: ["catalog", "item", deletedId] });

      // Invalidate list to reflect deletion
      queryClient.invalidateQueries({ queryKey: ["catalog", "items"] });
    },
  });
}

/**
 * Upload product image.
 *
 * Returns temporary filename to include in catalog item creation/update.
 *
 * @returns Mutation with upload function and progress tracking
 */
export function useUploadImage() {
  return useMutation({
    mutationFn: (file: File) => uploadProductImage(file),
  });
}
