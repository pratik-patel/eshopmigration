/**
 * DeletePage component.
 *
 * Confirm deletion of catalog item.
 * Matches legacy Delete.aspx.
 */

import { useNavigate, useParams } from "react-router-dom";
import { useCatalogItem, useDeleteCatalogItem } from "@/hooks/useCatalog";
import { ProductImage } from "@/components/catalog/ProductImage";

/**
 * Delete confirmation page.
 *
 * Matches ui-specification.json Delete.aspx:
 * - Title: "Delete"
 * - Confirmation message: "Are you sure you want to delete this?"
 * - Display item details (read-only)
 * - Layout: Image (col-md-4) + Two data columns (col-md-4 each)
 * - Buttons: "[ Cancel ]", "[ Delete ]"
 * - On success: redirect to Default.aspx (home)
 */
export function DeletePage() {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const itemId = Number(id);

  const { data: item, isLoading, isError, error } = useCatalogItem(itemId);
  const deleteMutation = useDeleteCatalogItem();

  const handleDelete = async () => {
    try {
      await deleteMutation.mutateAsync(itemId);
      // Redirect to home page on success (legacy behavior)
      navigate("/");
    } catch (error) {
      alert(
        error instanceof Error
          ? error.message
          : "Failed to delete catalog item"
      );
    }
  };

  const handleCancel = () => {
    navigate("/");
  };

  if (isLoading) {
    return (
      <div className="esh-container py-8">
        <div className="flex justify-center">
          <div className="esh-loader" />
        </div>
      </div>
    );
  }

  if (isError || !item) {
    return (
      <div className="esh-container py-8">
        <div className="bg-secondary-red text-neutral-white p-4 rounded">
          <strong>Error loading catalog item:</strong>{" "}
          {error instanceof Error ? error.message : "Item not found"}
        </div>
        <div className="mt-4">
          <button
            onClick={() => navigate("/")}
            className="btn esh-button esh-button-secondary"
          >
            [ Back to list ]
          </button>
        </div>
      </div>
    );
  }

  return (
    <div>
      {/* Page title */}
      <div className="esh-body-title">
        <h1>Delete</h1>
      </div>

      <div className="container mx-auto py-8">
        {/* Confirmation message */}
        <h3 className="text-xl font-semibold mb-6 text-center">
          Are you sure you want to delete this?
        </h3>

        {/* Item details layout: Image + Two columns */}
        <div className="grid grid-cols-1 md:grid-cols-12 gap-8">
          {/* Left column: Image (col-md-4) */}
          <div className="md:col-span-4">
            <ProductImage
              pictureFileName={item.picture_file_name}
              alt={item.name}
              size="full"
            />
          </div>

          {/* Middle column: Basic info (col-md-4) */}
          <div className="md:col-span-4">
            <dl className="space-y-4">
              <div>
                <dt className="font-semibold">Name</dt>
                <dd className="mt-1">{item.name}</dd>
              </div>
              <div>
                <dt className="font-semibold">Description</dt>
                <dd className="mt-1">{item.description || "-"}</dd>
              </div>
              <div>
                <dt className="font-semibold">Brand</dt>
                <dd className="mt-1">{item.brand.brand}</dd>
              </div>
              <div>
                <dt className="font-semibold">Type</dt>
                <dd className="mt-1">{item.type.type}</dd>
              </div>
              <div>
                <dt className="font-semibold">Price</dt>
                <dd className="mt-1">
                  <span className="esh-price">{item.price}</span>
                </dd>
              </div>
            </dl>
          </div>

          {/* Right column: Stock info + actions (col-md-4) */}
          <div className="md:col-span-4">
            <dl className="space-y-4">
              <div>
                <dt className="font-semibold">Picture name</dt>
                <dd className="mt-1">{item.picture_file_name}</dd>
              </div>
              <div>
                <dt className="font-semibold">Stock</dt>
                <dd className="mt-1">{item.available_stock}</dd>
              </div>
              <div>
                <dt className="font-semibold">Restock</dt>
                <dd className="mt-1">{item.restock_threshold}</dd>
              </div>
              <div>
                <dt className="font-semibold">Max stock</dt>
                <dd className="mt-1">{item.max_stock_threshold}</dd>
              </div>
            </dl>

            {/* Action buttons */}
            <div className="flex gap-4 mt-8">
              <button
                type="button"
                onClick={handleCancel}
                disabled={deleteMutation.isPending}
                className="btn esh-button esh-button-secondary"
              >
                [ Cancel ]
              </button>
              <button
                type="button"
                onClick={handleDelete}
                disabled={deleteMutation.isPending}
                className="btn esh-button esh-button-primary"
              >
                {deleteMutation.isPending ? "Deleting..." : "[ Delete ]"}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
