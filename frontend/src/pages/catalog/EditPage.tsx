/**
 * EditPage component.
 *
 * Edit existing catalog item page.
 * Matches legacy Edit.aspx.
 */

import { useNavigate, useParams } from "react-router-dom";
import { useCatalogItem, useUpdateCatalogItem } from "@/hooks/useCatalog";
import { CatalogForm } from "@/components/catalog/CatalogForm";
import type { CatalogItemUpdate } from "@/types/api";

/**
 * Edit catalog item page.
 *
 * Matches ui-specification.json Edit.aspx:
 * - Title: "Edit"
 * - Form pre-populated with existing data
 * - Picture name field read-only
 * - Buttons: "[ Cancel ]", "[ Save ]"
 * - On success: redirect to Default.aspx (home)
 */
export function EditPage() {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const itemId = Number(id);

  const { data: item, isLoading, isError, error } = useCatalogItem(itemId);
  const updateMutation = useUpdateCatalogItem();

  const handleSubmit = async (data: CatalogItemUpdate) => {
    try {
      await updateMutation.mutateAsync({ id: itemId, data });
      // Redirect to home page on success (legacy behavior)
      navigate("/");
    } catch (error) {
      alert(
        error instanceof Error
          ? error.message
          : "Failed to update catalog item"
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
        <h1>Edit</h1>
      </div>

      {/* Form */}
      <CatalogForm
        mode="edit"
        initialData={item}
        onSubmit={handleSubmit}
        onCancel={handleCancel}
        isSubmitting={updateMutation.isPending}
      />
    </div>
  );
}
