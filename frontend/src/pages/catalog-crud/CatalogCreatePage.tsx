/**
 * Catalog Create Page.
 *
 * Provides form to create new catalog items.
 * Uses shared CatalogForm component with create mode.
 */

import { CatalogForm, type CatalogFormData } from '@/components/catalog/CatalogForm'
import { useCreateCatalogItem } from '@/hooks/useCatalogCRUD'

export function CatalogCreatePage() {
  const createMutation = useCreateCatalogItem()

  const handleSubmit = (data: CatalogFormData) => {
    createMutation.mutate(data)
  }

  return (
    <div>
      <CatalogForm
        mode="create"
        onSubmit={handleSubmit}
        isSubmitting={createMutation.isPending}
      />
    </div>
  )
}
