/**
 * Catalog Details Page.
 *
 * Read-only view of catalog item with product image.
 * Displays all product details without edit capability.
 */

import { useParams, Navigate, Link } from 'react-router-dom'
import { useCatalogItem } from '@/hooks/useCatalogCRUD'

export function CatalogDetailsPage() {
  const { id } = useParams<{ id: string }>()
  const productId = parseInt(id || '', 10)

  // Fetch product data
  const { data: product, isLoading, error } = useCatalogItem(productId)

  // Handle invalid ID
  if (isNaN(productId)) {
    return <Navigate to="/" replace />
  }

  // Loading state
  if (isLoading) {
    return (
      <div className="container">
        <h2 className="esh-body-title">Details</h2>
        <p>Loading product...</p>
      </div>
    )
  }

  // Error state
  if (error || !product) {
    return (
      <div className="container">
        <h2 className="esh-body-title">Details</h2>
        <p className="text-danger">Product not found.</p>
        <Link to="/" className="btn esh-button esh-button-secondary">
          [ Back to List ]
        </Link>
      </div>
    )
  }

  // Build product image URL
  const productImage = product.picture_uri || `/pics/${product.picture_file_name}`

  return (
    <div className="container">
      <h2 className="esh-body-title">Details</h2>

      <div className="row">
        {/* Product Image */}
        <div className="col-md-6">
          <img
            src={productImage}
            alt={product.name}
            className="esh-picture"
          />
        </div>

        {/* Product Details (Read-only) */}
        <div className="col-md-6 form-horizontal">
          {/* Name */}
          <div className="form-group">
            <label className="control-label col-md-4">Name</label>
            <div className="col-md-8">
              <p className="form-control-static">{product.name}</p>
            </div>
          </div>

          {/* Description */}
          <div className="form-group">
            <label className="control-label col-md-4">Description</label>
            <div className="col-md-8">
              <p className="form-control-static">
                {product.description || '(none)'}
              </p>
            </div>
          </div>

          {/* Brand */}
          <div className="form-group">
            <label className="control-label col-md-4">Brand</label>
            <div className="col-md-8">
              <p className="form-control-static">
                {product.catalog_brand.brand}
              </p>
            </div>
          </div>

          {/* Type */}
          <div className="form-group">
            <label className="control-label col-md-4">Type</label>
            <div className="col-md-8">
              <p className="form-control-static">
                {product.catalog_type.type}
              </p>
            </div>
          </div>

          {/* Price */}
          <div className="form-group">
            <label className="control-label col-md-4">Price</label>
            <div className="col-md-8">
              <p className="form-control-static esh-price">
                ${product.price.toFixed(2)}
              </p>
            </div>
          </div>

          {/* Picture Name */}
          <div className="form-group">
            <label className="control-label col-md-4">Picture name</label>
            <div className="col-md-8">
              <p className="form-control-static">
                {product.picture_file_name}
              </p>
            </div>
          </div>

          {/* Stock */}
          <div className="form-group">
            <label className="control-label col-md-4">Stock</label>
            <div className="col-md-8">
              <p className="form-control-static">
                {product.available_stock}
              </p>
            </div>
          </div>

          {/* Restock */}
          <div className="form-group">
            <label className="control-label col-md-4">Restock</label>
            <div className="col-md-8">
              <p className="form-control-static">
                {product.restock_threshold}
              </p>
            </div>
          </div>

          {/* Max Stock */}
          <div className="form-group">
            <label className="control-label col-md-4">Max stock</label>
            <div className="col-md-8">
              <p className="form-control-static">
                {product.max_stock_threshold}
              </p>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="form-group">
            <div className="col-md-offset-4 col-md-8 text-right esh-button-actions">
              <Link
                to={`/catalog/edit/${product.id}`}
                className="btn esh-button esh-button-primary"
              >
                [ Edit ]
              </Link>
              <Link to="/" className="btn esh-button esh-button-secondary">
                [ Back to List ]
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
