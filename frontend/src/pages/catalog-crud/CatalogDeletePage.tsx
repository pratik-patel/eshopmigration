/**
 * Catalog Delete Page.
 *
 * Confirmation page for deleting catalog items.
 * Displays product details and requires confirmation before deletion.
 */

import { useParams, Navigate, Link } from 'react-router-dom'
import { useCatalogItem, useDeleteCatalogItem } from '@/hooks/useCatalogCRUD'

export function CatalogDeletePage() {
  const { id } = useParams<{ id: string }>()
  const productId = parseInt(id || '', 10)

  // Fetch product data
  const { data: product, isLoading, error } = useCatalogItem(productId)
  const deleteMutation = useDeleteCatalogItem(productId)

  // Handle invalid ID
  if (isNaN(productId)) {
    return <Navigate to="/" replace />
  }

  // Loading state
  if (isLoading) {
    return (
      <div className="container">
        <h2 className="esh-body-title">Delete</h2>
        <p>Loading product...</p>
      </div>
    )
  }

  // Error state
  if (error || !product) {
    return (
      <div className="container">
        <h2 className="esh-body-title">Delete</h2>
        <p className="text-danger">Product not found.</p>
        <Link to="/" className="btn esh-button esh-button-secondary">
          [ Back to List ]
        </Link>
      </div>
    )
  }

  // Build product image URL
  const productImage = product.picture_uri || `/pics/${product.picture_file_name}`

  const handleDelete = () => {
    deleteMutation.mutate()
  }

  return (
    <div className="container">
      <h2 className="esh-body-title">Delete</h2>

      {/* Confirmation Message */}
      <h3 className="text-danger">Are you sure you want to delete this?</h3>

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
              <button
                onClick={handleDelete}
                disabled={deleteMutation.isPending}
                className="btn esh-button esh-button-primary"
              >
                {deleteMutation.isPending ? 'Deleting...' : '[ Delete ]'}
              </button>
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
