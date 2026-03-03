/**
 * Catalog List Page.
 *
 * Displays paginated catalog items with product images, details, and actions.
 * Legacy: Default.aspx
 */

import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useCatalogItems } from '@/hooks/useCatalogItems'
import { CatalogTable } from '@/components/catalog/CatalogTable'
import { Pagination } from '@/components/catalog/Pagination'

export function CatalogListPage() {
  const [pageIndex, setPageIndex] = useState(0)
  const pageSize = 10 // Default page size from legacy

  const { data, isLoading, isError, error } = useCatalogItems(pageSize, pageIndex)

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-gray-500">Loading catalog items...</div>
      </div>
    )
  }

  if (isError) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-red-600">
          Error loading catalog items: {error instanceof Error ? error.message : 'Unknown error'}
        </div>
      </div>
    )
  }

  if (!data) {
    return null
  }

  return (
    <div>
      {/* Create New button */}
      <p className="esh-link-wrapper mb-4">
        <Link
          to="/catalog/create"
          className="btn esh-button esh-button-primary"
        >
          Create New
        </Link>
      </p>

      {/* Product table */}
      <CatalogTable items={data.data} />

      {/* Pagination */}
      {data.total_pages > 1 && (
        <Pagination
          pageIndex={data.page_index}
          pageSize={data.page_size}
          totalItems={data.total_items}
          totalPages={data.total_pages}
          onPageChange={setPageIndex}
        />
      )}
    </div>
  )
}
