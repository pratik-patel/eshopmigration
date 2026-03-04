/**
 * Pagination component.
 *
 * Displays page navigation with Previous/Next links.
 * Matches legacy PaginationNext/PaginationPrevious controls.
 */

import type { PaginationMetadata } from "@/types/api";

interface PaginationProps {
  /** Pagination metadata from API */
  pagination: PaginationMetadata;
  /** Callback when page changes */
  onPageChange: (newPage: number) => void;
}

/**
 * Page navigation with Previous/Next buttons.
 *
 * Matches ui-specification.json:
 * - Container: .esh-pager
 * - Items: .esh-pager-item .esh-pager-item--navigable
 * - Text: "Previous" and "Next" (exact match required)
 * - Disabled state: .esh-pager-item--disabled
 */
export function Pagination({ pagination, onPageChange }: PaginationProps) {
  const { page, total_pages } = pagination;

  const hasPrevious = page > 0;
  const hasNext = page < total_pages - 1;

  const handlePrevious = () => {
    if (hasPrevious) {
      onPageChange(page - 1);
    }
  };

  const handleNext = () => {
    if (hasNext) {
      onPageChange(page + 1);
    }
  };

  // Don't show pagination if only one page
  if (total_pages <= 1) {
    return null;
  }

  return (
    <div className="esh-pager">
      {/* Previous button */}
      <button
        onClick={handlePrevious}
        disabled={!hasPrevious}
        className={
          hasPrevious
            ? "esh-pager-item esh-pager-item--navigable"
            : "esh-pager-item esh-pager-item--disabled"
        }
        type="button"
      >
        Previous
      </button>

      {/* Page indicator */}
      <span className="esh-pager-item esh-pager-item--active">
        Page {page + 1} of {total_pages}
      </span>

      {/* Next button */}
      <button
        onClick={handleNext}
        disabled={!hasNext}
        className={
          hasNext
            ? "esh-pager-item esh-pager-item--navigable"
            : "esh-pager-item esh-pager-item--disabled"
        }
        type="button"
      >
        Next
      </button>
    </div>
  );
}
