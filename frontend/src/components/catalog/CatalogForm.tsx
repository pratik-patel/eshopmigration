/**
 * Shared Catalog Form Component.
 *
 * Used by both Create and Edit pages.
 * Implements validation rules from legacy application.
 */

import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Link } from 'react-router-dom'
import type { CatalogItem } from '@/api/catalog'
import { useCatalogBrands, useCatalogTypes } from '@/hooks/useCatalogCRUD'

/**
 * Validation schema matching legacy business rules.
 *
 * BR-001: Price validation (positive, max 2 decimals, 0-1000000)
 * BR-002-004: Stock validation (0-10000000)
 */
const catalogItemSchema = z.object({
  name: z.string().min(1, 'The Name field is required.'),
  description: z.string().optional(),
  price: z
    .number()
    .min(0, 'The Price must be a positive number with maximum two decimals between 0 and 1 million.')
    .max(1000000, 'The Price must be a positive number with maximum two decimals between 0 and 1 million.')
    .refine((val) => {
      // Check max 2 decimal places
      const decimalStr = val.toString().split('.')[1]
      return !decimalStr || decimalStr.length <= 2
    }, 'The Price must be a positive number with maximum two decimals between 0 and 1 million.'),
  catalog_brand_id: z.number().min(1, 'Brand is required'),
  catalog_type_id: z.number().min(1, 'Type is required'),
  available_stock: z
    .number()
    .int()
    .min(0, 'The field Stock must be between 0 and 10 million.')
    .max(10000000, 'The field Stock must be between 0 and 10 million.'),
  restock_threshold: z
    .number()
    .int()
    .min(0, 'The field Restock must be between 0 and 10 million.')
    .max(10000000, 'The field Restock must be between 0 and 10 million.'),
  max_stock_threshold: z
    .number()
    .int()
    .min(0, 'The field Max stock must be between 0 and 10 million.')
    .max(10000000, 'The field Max stock must be between 0 and 10 million.'),
  picture_file_name: z.string().default('dummy.png'),
})

export type CatalogFormData = z.infer<typeof catalogItemSchema>

interface CatalogFormProps {
  mode: 'create' | 'edit'
  initialData?: CatalogItem
  productImage?: string | null
  onSubmit: (data: CatalogFormData) => void
  isSubmitting: boolean
}

export function CatalogForm({
  mode,
  initialData,
  productImage,
  onSubmit,
  isSubmitting,
}: CatalogFormProps) {
  // Fetch brands and types for dropdowns
  const { data: brands } = useCatalogBrands()
  const { data: types } = useCatalogTypes()

  // Form setup with validation
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<CatalogFormData>({
    resolver: zodResolver(catalogItemSchema),
    defaultValues: initialData
      ? {
          name: initialData.name,
          description: initialData.description || '',
          price: initialData.price,
          catalog_brand_id: initialData.catalog_brand_id,
          catalog_type_id: initialData.catalog_type_id,
          available_stock: initialData.available_stock,
          restock_threshold: initialData.restock_threshold,
          max_stock_threshold: initialData.max_stock_threshold,
          picture_file_name: initialData.picture_file_name,
        }
      : {
          price: 0.0,
          available_stock: 0,
          restock_threshold: 0,
          max_stock_threshold: 0,
          picture_file_name: 'dummy.png',
        },
  })

  const isEdit = mode === 'edit'
  const pageTitle = isEdit ? 'Edit' : 'Create'
  const submitButtonText = isEdit ? '[ Save ]' : '[ Create ]'

  return (
    <div className={isEdit ? 'container' : ''}>
      <h2 className="esh-body-title">{pageTitle}</h2>

      <div className={isEdit ? 'row' : ''}>
        {/* Product Image (Edit page only) */}
        {isEdit && productImage && (
          <div className="col-md-6">
            <img
              src={productImage}
              alt={initialData?.name}
              className="esh-picture"
            />
          </div>
        )}

        {/* Form */}
        <div className={isEdit ? 'col-md-6 form-horizontal' : 'form-horizontal'}>
          <form onSubmit={handleSubmit(onSubmit)}>
            {/* Name Field */}
            <div className="form-group">
              <label className={`control-label ${isEdit ? 'col-md-4' : 'col-md-2'}`}>
                Name
              </label>
              <div className={isEdit ? 'col-md-8' : 'col-md-3'}>
                <input
                  {...register('name')}
                  type="text"
                  className="form-control"
                />
                {errors.name && (
                  <span className="field-validation-valid text-danger">
                    {errors.name.message}
                  </span>
                )}
              </div>
            </div>

            {/* Description Field */}
            <div className="form-group">
              <label className={`control-label ${isEdit ? 'col-md-4' : 'col-md-2'}`}>
                Description
              </label>
              <div className={isEdit ? 'col-md-8' : 'col-md-3'}>
                <input
                  {...register('description')}
                  type="text"
                  className="form-control"
                />
              </div>
            </div>

            {/* Brand Dropdown */}
            <div className="form-group">
              <label className={`control-label ${isEdit ? 'col-md-4' : 'col-md-2'}`}>
                Brand
              </label>
              <div className={isEdit ? 'col-md-8' : 'col-md-3'}>
                <select
                  {...register('catalog_brand_id', { valueAsNumber: true })}
                  className="form-control"
                >
                  <option value="">Select Brand</option>
                  {brands?.map((brand) => (
                    <option key={brand.id} value={brand.id}>
                      {brand.brand}
                    </option>
                  ))}
                </select>
                {errors.catalog_brand_id && (
                  <span className="field-validation-valid text-danger">
                    {errors.catalog_brand_id.message}
                  </span>
                )}
              </div>
            </div>

            {/* Type Dropdown */}
            <div className="form-group">
              <label className={`control-label ${isEdit ? 'col-md-4' : 'col-md-2'}`}>
                Type
              </label>
              <div className={isEdit ? 'col-md-8' : 'col-md-3'}>
                <select
                  {...register('catalog_type_id', { valueAsNumber: true })}
                  className="form-control"
                >
                  <option value="">Select Type</option>
                  {types?.map((type) => (
                    <option key={type.id} value={type.id}>
                      {type.type}
                    </option>
                  ))}
                </select>
                {errors.catalog_type_id && (
                  <span className="field-validation-valid text-danger">
                    {errors.catalog_type_id.message}
                  </span>
                )}
              </div>
            </div>

            {/* Price Field */}
            <div className="form-group">
              <label className={`control-label ${isEdit ? 'col-md-4' : 'col-md-2'}`}>
                Price
              </label>
              <div className={isEdit ? 'col-md-8' : 'col-md-3'}>
                <input
                  {...register('price', { valueAsNumber: true })}
                  type="number"
                  step="0.01"
                  className="form-control"
                />
                {errors.price && (
                  <span className="field-validation-valid text-danger">
                    {errors.price.message}
                  </span>
                )}
              </div>
            </div>

            {/* Picture Name Field */}
            <div className="form-group">
              <label className={`control-label ${isEdit ? 'col-md-4' : 'col-md-2'}`}>
                Picture name
              </label>
              <div className={isEdit ? 'col-md-8' : 'col-md-4 esh-form-information'}>
                {isEdit ? (
                  <input
                    {...register('picture_file_name')}
                    type="text"
                    className="form-control"
                    readOnly
                    title="Not allowed for edition"
                  />
                ) : (
                  'Uploading images not allowed for this version.'
                )}
              </div>
            </div>

            {/* Stock Field */}
            <div className="form-group">
              <label className={`control-label ${isEdit ? 'col-md-4' : 'col-md-2'}`}>
                Stock
              </label>
              <div className={isEdit ? 'col-md-8' : 'col-md-3'}>
                <input
                  {...register('available_stock', { valueAsNumber: true })}
                  type="number"
                  className="form-control"
                />
                {errors.available_stock && (
                  <span className="field-validation-valid text-danger">
                    {errors.available_stock.message}
                  </span>
                )}
              </div>
            </div>

            {/* Restock Field */}
            <div className="form-group">
              <label className={`control-label ${isEdit ? 'col-md-4' : 'col-md-2'}`}>
                Restock
              </label>
              <div className={isEdit ? 'col-md-8' : 'col-md-3'}>
                <input
                  {...register('restock_threshold', { valueAsNumber: true })}
                  type="number"
                  className="form-control"
                />
                {errors.restock_threshold && (
                  <span className="field-validation-valid text-danger">
                    {errors.restock_threshold.message}
                  </span>
                )}
              </div>
            </div>

            {/* Max Stock Field */}
            <div className="form-group">
              <label className={`control-label ${isEdit ? 'col-md-4' : 'col-md-2'}`}>
                Max stock
              </label>
              <div className={isEdit ? 'col-md-8' : 'col-md-3'}>
                <input
                  {...register('max_stock_threshold', { valueAsNumber: true })}
                  type="number"
                  className="form-control"
                />
                {errors.max_stock_threshold && (
                  <span className="field-validation-valid text-danger">
                    {errors.max_stock_threshold.message}
                  </span>
                )}
              </div>
            </div>

            {/* Form Actions */}
            <div className="form-group">
              <div
                className={`${
                  isEdit ? 'col-md-offset-4 col-md-8' : 'col-md-offset-2 col-md-3'
                } text-right esh-button-actions`}
              >
                <Link to="/" className="btn esh-button esh-button-secondary">
                  [ Cancel ]
                </Link>
                <button
                  type="submit"
                  className="btn esh-button esh-button-primary"
                  disabled={isSubmitting}
                >
                  {isSubmitting ? 'Saving...' : submitButtonText}
                </button>
              </div>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}
