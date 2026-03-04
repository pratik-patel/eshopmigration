/**
 * CreatePage component.
 *
 * Create new catalog item page.
 * Matches legacy Create.aspx.
 */

import { useNavigate } from "react-router-dom";
import { useCreateCatalogItem } from "@/hooks/useCatalog";
import { CatalogForm } from "@/components/catalog/CatalogForm";
import type { CatalogItemCreate } from "@/types/api";

/**
 * Create catalog item page.
 *
 * Matches ui-specification.json Create.aspx:
 * - Title: "Create"
 * - Form with image upload + fields
 * - Buttons: "[ Cancel ]", "[ Create ]"
 * - On success: redirect to Default.aspx (home)
 */
export function CreatePage() {
  const navigate = useNavigate();
  const createMutation = useCreateCatalogItem();

  const handleSubmit = async (data: CatalogItemCreate) => {
    try {
      await createMutation.mutateAsync(data);
      // Redirect to home page on success (legacy behavior)
      navigate("/");
    } catch (error) {
      alert(
        error instanceof Error
          ? error.message
          : "Failed to create catalog item"
      );
    }
  };

  const handleCancel = () => {
    navigate("/");
  };

  return (
    <div>
      {/* Page title */}
      <div className="esh-body-title">
        <h1>Create</h1>
      </div>

      {/* Form */}
      <CatalogForm
        mode="create"
        onSubmit={handleSubmit}
        onCancel={handleCancel}
        isSubmitting={createMutation.isPending}
      />
    </div>
  );
}
