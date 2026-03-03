/**
 * Catalog Edit Page.
 *
 * Provides form to edit existing catalog items.
 * Displays product image on left, form on right (2-column layout).
 */

import { useParams, Navigate } from 'react-router-dom'
import { CatalogForm, type CatalogFormData } from '@/components/catalog/CatalogForm'
import { useCatalogItem, useUpdateCatalogItem } from '@/hooks/useCatalogCRUD'
import { ApiError } from '@/api/client'

export function CatalogEditPage() {
  const { id } = useParams<{ id: string }>()
  const productId = parseInt(id || '', 10)

  // Fetch product data
  const { data: product, isLoading, error } = useCatalogItem(productId)
  const updateMutation = useUpdateCatalogItem(productId)

  // Handle invalid ID
  if (isNaN(productId)) {
    return <Navigate to="/" replace />
  }

  // Loading state
  if (isLoading) {
    return (
      <div className="container">
        <h2 className="esh-body-title">Edit</h2>
        <p>Loading product...</p>
      </div>
    )
  }

  // Error state
  if (error || !product) {
    return (
      <div className="container">
        <h2 className="esh-body-title">Edit</h2>
        <p className="text-danger">Product not found.</p>
        <a href="/" className="btn esh-button esh-button-secondary">
          [ Back to List ]
        </a>
      </div>
    )
  }

  // Build product image URL
  const productImage = product.picture_uri || `/pics/${product.picture_file_name}`

  const handleSubmit = (data: CatalogFormData) => {
    updateMutation.mutate(data)
  }

  // Extract server validation errors from 400 response
  const serverErrors = updateMutation.error instanceof ApiError &&
    updateMutation.error.status === 400 &&
    (updateMutation.error.details as { detail?: Record<string, string> })?.detail
      ? (updateMutation.error.details as { detail: Record<string, string> }).detail
      : null

  return (
    <div>
      <CatalogForm
        mode="edit"
        initialData={product}
        productImage={productImage}
        onSubmit={handleSubmit}
        isSubmitting={updateMutation.isPending}
        serverErrors={serverErrors}
      />
    </div>
  )
}
