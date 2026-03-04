/**
 * CatalogForm component.
 *
 * Form for creating/editing catalog items.
 * Matches legacy Create.aspx and Edit.aspx form layouts.
 */

import { useState, useEffect } from "react";
import { useBrands, useTypes } from "@/hooks/useCatalog";
import { ImageUpload } from "./ImageUpload";
import type { CatalogItemCreate, CatalogItemUpdate, CatalogItemResponse } from "@/types/api";

interface CatalogFormProps {
  /** Mode: create or edit */
  mode: "create" | "edit";
  /** Existing item (for edit mode) */
  initialData?: CatalogItemResponse;
  /** Submit handler */
  onSubmit: (data: CatalogItemCreate | CatalogItemUpdate) => void;
  /** Cancel handler */
  onCancel: () => void;
  /** Submitting state */
  isSubmitting?: boolean;
}

/**
 * Product form with validation.
 *
 * Matches ui-specification.json controls:
 * - Layout: .col-md-4 (image) + .col-md-8 (form fields)
 * - All inputs: .form-control class
 * - Labels match exactly: "Name", "Brand", "Type", "Price", "Stock", "Restock", "Max stock"
 * - Dropdowns: Brand and Type with proper data binding
 * - Buttons: "[ Cancel ]" (secondary), "[ Create ]" or "[ Save ]" (primary)
 */
export function CatalogForm({
  mode,
  initialData,
  onSubmit,
  onCancel,
  isSubmitting,
}: CatalogFormProps) {
  // Form state
  const [name, setName] = useState(initialData?.name || "");
  const [description, setDescription] = useState(initialData?.description || "");
  const [price, setPrice] = useState(initialData?.price || "0.00");
  const [brandId, setBrandId] = useState(initialData?.catalog_brand_id || 0);
  const [typeId, setTypeId] = useState(initialData?.catalog_type_id || 0);
  const [stock, setStock] = useState(initialData?.available_stock || 0);
  const [restock, setRestock] = useState(initialData?.restock_threshold || 0);
  const [maxStock, setMaxStock] = useState(initialData?.max_stock_threshold || 0);
  const [tempImageName, setTempImageName] = useState<string | null>(null);

  // Fetch brands and types for dropdowns
  const { data: brands, isLoading: brandsLoading } = useBrands();
  const { data: types, isLoading: typesLoading } = useTypes();

  // Set default selections when data loads
  useEffect(() => {
    if (brands && brands.length > 0 && brandId === 0) {
      setBrandId(brands[0].id);
    }
  }, [brands, brandId]);

  useEffect(() => {
    if (types && types.length > 0 && typeId === 0) {
      setTypeId(types[0].id);
    }
  }, [types, typeId]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    // Basic validation
    if (!name.trim()) {
      alert("Name is required");
      return;
    }

    if (brandId === 0 || typeId === 0) {
      alert("Please select Brand and Type");
      return;
    }

    const formData = {
      name: name.trim(),
      description: description.trim() || null,
      price,
      catalog_brand_id: brandId,
      catalog_type_id: typeId,
      available_stock: stock,
      restock_threshold: restock,
      max_stock_threshold: maxStock,
      temp_image_name: tempImageName,
    };

    onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="container mx-auto py-8">
      <div className="grid grid-cols-1 md:grid-cols-12 gap-8">
        {/* Left column: Image upload (col-md-4) */}
        <div className="md:col-span-4">
          <ImageUpload
            currentImage={initialData?.picture_file_name}
            onUploadSuccess={setTempImageName}
            productName={name || "Product"}
          />
        </div>

        {/* Right column: Form fields (col-md-8) */}
        <div className="md:col-span-8">
          <div className="space-y-4">
            {/* Name */}
            <div className="form-group">
              <label htmlFor="name" className="block text-sm font-semibold mb-2">
                Name
              </label>
              <input
                type="text"
                id="name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="form-control"
                maxLength={50}
                required
              />
            </div>

            {/* Description */}
            <div className="form-group">
              <label htmlFor="description" className="block text-sm font-semibold mb-2">
                Description
              </label>
              <input
                type="text"
                id="description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className="form-control"
              />
            </div>

            {/* Brand */}
            <div className="form-group">
              <label htmlFor="brand" className="block text-sm font-semibold mb-2">
                Brand
              </label>
              <select
                id="brand"
                value={brandId}
                onChange={(e) => setBrandId(Number(e.target.value))}
                className="form-control"
                disabled={brandsLoading}
                required
              >
                <option value={0}>Select Brand</option>
                {brands?.map((brand) => (
                  <option key={brand.id} value={brand.id}>
                    {brand.brand}
                  </option>
                ))}
              </select>
            </div>

            {/* Type */}
            <div className="form-group">
              <label htmlFor="type" className="block text-sm font-semibold mb-2">
                Type
              </label>
              <select
                id="type"
                value={typeId}
                onChange={(e) => setTypeId(Number(e.target.value))}
                className="form-control"
                disabled={typesLoading}
                required
              >
                <option value={0}>Select Type</option>
                {types?.map((type) => (
                  <option key={type.id} value={type.id}>
                    {type.type}
                  </option>
                ))}
              </select>
            </div>

            {/* Price */}
            <div className="form-group">
              <label htmlFor="price" className="block text-sm font-semibold mb-2">
                Price
              </label>
              <input
                type="number"
                id="price"
                value={price}
                onChange={(e) => setPrice(e.target.value)}
                className="form-control"
                min="0"
                max="999999999.99"
                step="0.01"
                required
              />
            </div>

            {/* Stock */}
            <div className="form-group">
              <label htmlFor="stock" className="block text-sm font-semibold mb-2">
                Stock
              </label>
              <input
                type="number"
                id="stock"
                value={stock}
                onChange={(e) => setStock(Number(e.target.value))}
                className="form-control"
                min="0"
                max="10000000"
                required
              />
            </div>

            {/* Restock */}
            <div className="form-group">
              <label htmlFor="restock" className="block text-sm font-semibold mb-2">
                Restock
              </label>
              <input
                type="number"
                id="restock"
                value={restock}
                onChange={(e) => setRestock(Number(e.target.value))}
                className="form-control"
                min="0"
                max="10000000"
                required
              />
            </div>

            {/* Max stock */}
            <div className="form-group">
              <label htmlFor="maxStock" className="block text-sm font-semibold mb-2">
                Max stock
              </label>
              <input
                type="number"
                id="maxStock"
                value={maxStock}
                onChange={(e) => setMaxStock(Number(e.target.value))}
                className="form-control"
                min="0"
                max="10000000"
                required
              />
            </div>

            {/* Picture name (Edit mode only, read-only) */}
            {mode === "edit" && initialData && (
              <div className="form-group">
                <label htmlFor="pictureName" className="block text-sm font-semibold mb-2">
                  Picture name
                </label>
                <input
                  type="text"
                  id="pictureName"
                  value={initialData.picture_file_name}
                  className="form-control"
                  readOnly
                  title="Not allowed for edition"
                />
              </div>
            )}

            {/* Action buttons */}
            <div className="flex gap-4 mt-8">
              <button
                type="button"
                onClick={onCancel}
                disabled={isSubmitting}
                className="btn esh-button esh-button-secondary"
              >
                [ Cancel ]
              </button>
              <button
                type="submit"
                disabled={isSubmitting}
                className="btn esh-button esh-button-primary"
              >
                {isSubmitting
                  ? "Saving..."
                  : mode === "create"
                  ? "[ Create ]"
                  : "[ Save ]"}
              </button>
            </div>
          </div>
        </div>
      </div>
    </form>
  );
}
