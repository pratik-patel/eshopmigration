/**
 * Pagination component.
 *
 * Displays pagination controls matching the legacy layout.
 */

import { Link } from 'react-router-dom'
import { cn } from '@/lib/utils'

interface PaginationProps {
  pageIndex: number
  pageSize: number
  totalItems: number
  totalPages: number
  onPageChange: (newPageIndex: number) => void
}

export function Pagination({
  pageIndex,
  pageSize,
  totalItems,
  totalPages,
  onPageChange,
}: PaginationProps) {
  const hasPrevious = pageIndex > 0
  const hasNext = pageIndex < totalPages - 1
  const currentPage = pageIndex + 1 // Display as 1-based

  // Calculate the range of items being shown
  const startItem = pageIndex * pageSize + 1
  const endItem = Math.min((pageIndex + 1) * pageSize, totalItems)

  return (
    <div className="esh-pager">
      <div className="container">
        <article className="esh-pager-wrapper row">
          <nav className="flex items-center justify-center space-x-4">
            {/* Previous button */}
            <button
              onClick={() => onPageChange(pageIndex - 1)}
              disabled={!hasPrevious}
              className={cn(
                'esh-pager-item esh-pager-item--navigable',
                !hasPrevious && 'esh-pager-item--hidden'
              )}
            >
              Previous
            </button>

            {/* Page info - matches legacy format: "Showing X to Y of Z products - Page N - M" */}
            <span className="esh-pager-item">
              Showing {startItem} to {endItem} of {totalItems} products - Page {currentPage} - {totalPages}
            </span>

            {/* Next button */}
            <button
              onClick={() => onPageChange(pageIndex + 1)}
              disabled={!hasNext}
              className={cn(
                'esh-pager-item esh-pager-item--navigable',
                !hasNext && 'esh-pager-item--hidden'
              )}
            >
              Next
            </button>
          </nav>
        </article>
      </div>
    </div>
  )
}
