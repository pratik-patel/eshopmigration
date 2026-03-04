/**
 * CatalogTable component.
 *
 * Displays catalog items in a table with action links.
 * Matches legacy asp:ListView structure and column layout.
 */

import { Link } from "react-router-dom";
import { ProductImage } from "./ProductImage";
import type { CatalogItemResponse } from "@/types/api";

interface CatalogTableProps {
  /** Array of catalog items to display */
  items: CatalogItemResponse[];
  /** Loading state */
  isLoading?: boolean;
}

/**
 * Product catalog table.
 *
 * Matches ui-specification.json table_columns:
 * - Image (thumbnail)
 * - Name
 * - Description
 * - Brand
 * - Type
 * - Price (.esh-price)
 * - Picture name
 * - Stock
 * - Restock
 * - Max stock
 * - Actions (Edit, Details, Delete with .esh-table-link)
 */
export function CatalogTable({ items, isLoading }: CatalogTableProps) {
  if (isLoading) {
    return (
      <div className="esh-table">
        <div className="flex items-center justify-center py-12">
          <div className="esh-loader" />
        </div>
      </div>
    );
  }

  if (items.length === 0) {
    return (
      <div className="esh-table">
        <div className="text-center py-12 text-neutral-gray-medium">
          No catalog items found
        </div>
      </div>
    );
  }

  return (
    <div className="esh-table">
      <table className="table">
        <thead>
          <tr>
            <th></th>
            <th>Name</th>
            <th>Description</th>
            <th>Brand</th>
            <th>Type</th>
            <th>Price</th>
            <th>Picture name</th>
            <th>Stock</th>
            <th>Restock</th>
            <th>Max stock</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {items.map((item) => (
            <tr key={item.id}>
              {/* Image thumbnail */}
              <td>
                <ProductImage
                  pictureFileName={item.picture_file_name}
                  alt={item.name}
                  size="thumbnail"
                />
              </td>

              {/* Name */}
              <td>{item.name}</td>

              {/* Description */}
              <td>{item.description || "-"}</td>

              {/* Brand */}
              <td>{item.brand.brand}</td>

              {/* Type */}
              <td>{item.type.type}</td>

              {/* Price with .esh-price class */}
              <td>
                <span className="esh-price">{item.price}</span>
              </td>

              {/* Picture filename */}
              <td>{item.picture_file_name}</td>

              {/* Available Stock */}
              <td>{item.available_stock}</td>

              {/* Restock Threshold */}
              <td>{item.restock_threshold}</td>

              {/* Max Stock Threshold */}
              <td>{item.max_stock_threshold}</td>

              {/* Action links */}
              <td>
                <div className="flex gap-2">
                  <Link
                    to={`/catalog/edit/${item.id}`}
                    className="esh-table-link"
                  >
                    Edit
                  </Link>
                  <span className="text-neutral-gray-medium">|</span>
                  <Link
                    to={`/catalog/details/${item.id}`}
                    className="esh-table-link"
                  >
                    Details
                  </Link>
                  <span className="text-neutral-gray-medium">|</span>
                  <Link
                    to={`/catalog/delete/${item.id}`}
                    className="esh-table-link"
                  >
                    Delete
                  </Link>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
