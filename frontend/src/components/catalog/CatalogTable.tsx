/**
 * Catalog table component.
 *
 * Displays catalog items in a table format matching the legacy layout.
 */

import { Link } from 'react-router-dom'
import type { CatalogItem } from '@/api/catalog'
import { formatPrice } from '@/lib/utils'
import { getProductImageUrl } from '@/assets/catalog-list'

interface CatalogTableProps {
  items: CatalogItem[]
}

export function CatalogTable({ items }: CatalogTableProps) {
  if (items.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        No data was returned.
      </div>
    )
  }

  return (
    <div className="esh-table overflow-x-auto">
      <table className="table w-full">
        <thead>
          <tr className="esh-table-header">
            <th></th> {/* Image column */}
            <th>Name</th>
            <th>Description</th>
            <th>Brand</th>
            <th>Type</th>
            <th>Price</th>
            <th>Picture name</th>
            <th>Stock</th>
            <th>Restock</th>
            <th>Max stock</th>
            <th></th> {/* Actions column */}
          </tr>
        </thead>
        <tbody>
          {items.map((item) => (
            <tr key={item.id} className="border-b hover:bg-gray-50">
              {/* Image */}
              <td className="p-2">
                <img
                  src={getProductImageUrl(item.picture_file_name)}
                  alt={item.name}
                  className="esh-thumbnail"
                  loading="lazy"
                />
              </td>

              {/* Name */}
              <td className="p-2">
                <p>{item.name}</p>
              </td>

              {/* Description */}
              <td className="p-2">
                <p>{item.description}</p>
              </td>

              {/* Brand */}
              <td className="p-2">
                <p>{item.catalog_brand.brand}</p>
              </td>

              {/* Type */}
              <td className="p-2">
                <p>{item.catalog_type.type}</p>
              </td>

              {/* Price */}
              <td className="p-2">
                <p>
                  <span className="esh-price">{formatPrice(item.price)}</span>
                </p>
              </td>

              {/* Picture name */}
              <td className="p-2">
                <p>{item.picture_file_name}</p>
              </td>

              {/* Stock */}
              <td className="p-2">
                <p>{item.available_stock}</p>
              </td>

              {/* Restock */}
              <td className="p-2">
                <p>{item.restock_threshold}</p>
              </td>

              {/* Max stock */}
              <td className="p-2">
                <p>{item.max_stock_threshold}</p>
              </td>

              {/* Actions */}
              <td className="p-2">
                <div className="flex space-x-1 text-sm">
                  <Link
                    to={`/catalog/edit/${item.id}`}
                    className="esh-table-link"
                  >
                    Edit
                  </Link>
                  <span>|</span>
                  <Link
                    to={`/catalog/details/${item.id}`}
                    className="esh-table-link"
                  >
                    Details
                  </Link>
                  <span>|</span>
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
  )
}
