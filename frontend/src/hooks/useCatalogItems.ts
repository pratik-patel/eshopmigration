/**
 * TanStack Query hook for catalog items.
 */

import { useQuery } from '@tanstack/react-query'
import { getCatalogItems, type PaginatedCatalogItemsResponse } from '@/api/catalog'

/**
 * Hook for fetching paginated catalog items.
 *
 * @param pageSize - Number of items per page (default: 10)
 * @param pageIndex - Page index, zero-based (default: 0)
 * @returns Query result with catalog items data
 */
export function useCatalogItems(pageSize: number = 10, pageIndex: number = 0) {
  return useQuery<PaginatedCatalogItemsResponse>({
    queryKey: ['catalog-items', pageSize, pageIndex],
    queryFn: () => getCatalogItems(pageSize, pageIndex),
    staleTime: 1000 * 60, // 1 minute
    keepPreviousData: true, // Keep previous page data while loading next page
  })
}
