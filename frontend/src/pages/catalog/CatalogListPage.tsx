/**
 * CatalogListPage component.
 *
 * Main catalog listing page with pagination.
 * Matches legacy Default.aspx.
 */

import { useState } from "react";
import { Link } from "react-router-dom";
import { useCatalogItems } from "@/hooks/useCatalog";
import { CatalogTable } from "@/components/catalog/CatalogTable";
import { Pagination } from "@/components/catalog/Pagination";

/**
 * Catalog list page (home page).
 *
 * Matches ui-specification.json Default.aspx:
 * - Title: "Home Page" (handled by layout)
 * - Create New button: .btn .esh-button .esh-button-primary
 * - Table with all columns
 * - Pagination with Previous/Next
 */
export function CatalogListPage() {
  const [page, setPage] = useState(0);
  const limit = 10; // Default items per page (legacy behavior)

  const { data, isLoading, isError, error } = useCatalogItems(page, limit);

  if (isError) {
    return (
      <div className="esh-container py-8">
        <div className="bg-secondary-red text-neutral-white p-4 rounded">
          <strong>Error loading catalog items:</strong>{" "}
          {error instanceof Error ? error.message : "Unknown error"}
        </div>
      </div>
    );
  }

  return (
    <div className="esh-container">
      {/* Page title and Create button */}
      <div className="flex items-center justify-between py-8">
        <h1 className="text-h2 font-semibold">Catalog Items</h1>
        <Link to="/catalog/create" className="btn esh-button esh-button-primary">
          Create New
        </Link>
      </div>

      {/* Catalog table */}
      <CatalogTable items={data?.items || []} isLoading={isLoading} />

      {/* Pagination */}
      {data?.pagination && (
        <Pagination pagination={data.pagination} onPageChange={setPage} />
      )}
    </div>
  );
}
