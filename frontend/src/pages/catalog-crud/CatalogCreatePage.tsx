/**
 * Catalog Create Page.
 *
 * Provides form to create new catalog items.
 * Uses shared CatalogForm component with create mode.
 */

import { CatalogForm, type CatalogFormData } from '@/components/catalog/CatalogForm'
import { useCreateCatalogItem } from '@/hooks/useCatalogCRUD'
import { ApiError } from '@/api/client'

export function CatalogCreatePage() {
  const createMutation = useCreateCatalogItem()

  const handleSubmit = (data: CatalogFormData) => {
    createMutation.mutate(data)
  }

  // Extract server validation errors from 400 response
  const serverErrors = createMutation.error instanceof ApiError &&
    createMutation.error.status === 400 &&
    (createMutation.error.details as { detail?: Record<string, string> })?.detail
      ? (createMutation.error.details as { detail: Record<string, string> }).detail
      : null

  return (
    <div>
      <CatalogForm
        mode="create"
        onSubmit={handleSubmit}
        isSubmitting={createMutation.isPending}
        serverErrors={serverErrors}
      />
    </div>
  )
}
