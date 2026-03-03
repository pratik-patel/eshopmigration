/**
 * TanStack Query hooks for catalog CRUD operations.
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import {
  getCatalogItem,
  createCatalogItem,
  updateCatalogItem,
  deleteCatalogItem,
  getCatalogBrands,
  getCatalogTypes,
  type CatalogItem,
  type CatalogItemCreateRequest,
  type CatalogItemUpdateRequest,
  type CatalogBrand,
  type CatalogType,
} from '@/api/catalog'

/**
 * Hook for fetching single catalog item by ID.
 */
export function useCatalogItem(id: number) {
  return useQuery<CatalogItem>({
    queryKey: ['catalog-item', id],
    queryFn: () => getCatalogItem(id),
    staleTime: 1000 * 30, // 30 seconds
  })
}

/**
 * Hook for fetching all catalog brands.
 */
export function useCatalogBrands() {
  return useQuery<CatalogBrand[]>({
    queryKey: ['catalog-brands'],
    queryFn: getCatalogBrands,
    staleTime: 1000 * 60 * 5, // 5 minutes (brands rarely change)
  })
}

/**
 * Hook for fetching all catalog types.
 */
export function useCatalogTypes() {
  return useQuery<CatalogType[]>({
    queryKey: ['catalog-types'],
    queryFn: getCatalogTypes,
    staleTime: 1000 * 60 * 5, // 5 minutes (types rarely change)
  })
}

/**
 * Hook for creating catalog item.
 */
export function useCreateCatalogItem() {
  const queryClient = useQueryClient()
  const navigate = useNavigate()

  return useMutation({
    mutationFn: (data: CatalogItemCreateRequest) => createCatalogItem(data),
    onSuccess: () => {
      // Invalidate catalog items list
      queryClient.invalidateQueries({ queryKey: ['catalog-items'] })

      // Navigate back to catalog list
      navigate('/')
    },
    onError: (error) => {
      // Error handled in component layer
      console.error('Failed to create catalog item:', error)
    },
  })
}

/**
 * Hook for updating catalog item.
 */
export function useUpdateCatalogItem(id: number) {
  const queryClient = useQueryClient()
  const navigate = useNavigate()

  return useMutation({
    mutationFn: (data: CatalogItemUpdateRequest) => updateCatalogItem(id, data),
    onSuccess: () => {
      // Invalidate catalog items list
      queryClient.invalidateQueries({ queryKey: ['catalog-items'] })

      // Invalidate specific item
      queryClient.invalidateQueries({ queryKey: ['catalog-item', id] })

      // Navigate back to catalog list
      navigate('/')
    },
    onError: (error) => {
      // Error handled in component layer
      console.error('Failed to update catalog item:', error)
    },
  })
}

/**
 * Hook for deleting catalog item.
 */
export function useDeleteCatalogItem(id: number) {
  const queryClient = useQueryClient()
  const navigate = useNavigate()

  return useMutation({
    mutationFn: () => deleteCatalogItem(id),
    onSuccess: () => {
      // Invalidate catalog items list
      queryClient.invalidateQueries({ queryKey: ['catalog-items'] })

      // Remove item from cache
      queryClient.removeQueries({ queryKey: ['catalog-item', id] })

      // Navigate back to catalog list
      navigate('/')
    },
  })
}
