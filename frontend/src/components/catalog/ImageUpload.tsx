/**
 * ImageUpload component.
 *
 * Handles product image upload with preview.
 * Matches legacy uploadEditorImage control + ProductImage preview pattern.
 */

import { useRef, useState } from "react";
import { useUploadImage } from "@/hooks/useCatalog";
import { ProductImage } from "./ProductImage";

interface ImageUploadProps {
  /** Current image filename (for preview) */
  currentImage?: string | null;
  /** Callback when upload succeeds with temp filename */
  onUploadSuccess: (tempFilename: string) => void;
  /** Product name for alt text */
  productName?: string;
}

/**
 * Image upload with preview.
 *
 * Matches ui-specification.json:
 * - Hidden file input (input[type=file].hidden)
 * - Custom button trigger
 * - Preview with .esh-picture class
 * - Client-side upload before form submission (legacy behavior)
 */
export function ImageUpload({
  currentImage,
  onUploadSuccess,
  productName = "Product",
}: ImageUploadProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const uploadMutation = useUploadImage();

  const handleButtonClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = async (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validate file type
    const validTypes = ["image/jpeg", "image/jpg", "image/png", "image/gif"];
    if (!validTypes.includes(file.type)) {
      alert("Invalid file type. Please upload .jpg, .jpeg, .png, or .gif");
      return;
    }

    // Validate file size (4MB max)
    const maxSize = 4 * 1024 * 1024;
    if (file.size > maxSize) {
      alert("File too large. Maximum size is 4MB");
      return;
    }

    // Create preview URL
    const objectUrl = URL.createObjectURL(file);
    setPreviewUrl(objectUrl);

    try {
      // Upload to backend
      const response = await uploadMutation.mutateAsync(file);
      onUploadSuccess(response.temp_filename);
    } catch (error) {
      alert(
        error instanceof Error ? error.message : "Failed to upload image"
      );
      setPreviewUrl(null);
    }
  };

  // Determine which image to show: preview (new upload) or current (existing)
  const displayImage = previewUrl ? null : currentImage;

  return (
    <div className="space-y-4">
      {/* Image Preview */}
      <div className="flex justify-center">
        {previewUrl ? (
          <img src={previewUrl} alt={productName} className="esh-picture" />
        ) : (
          <ProductImage
            pictureFileName={displayImage}
            alt={productName}
            size="full"
          />
        )}
      </div>

      {/* Hidden file input (legacy pattern) */}
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        className="hidden"
        onChange={handleFileChange}
        disabled={uploadMutation.isPending}
      />

      {/* Upload button */}
      <div className="flex justify-center">
        <button
          type="button"
          onClick={handleButtonClick}
          disabled={uploadMutation.isPending}
          className="btn esh-button esh-button-primary"
        >
          {uploadMutation.isPending ? "Uploading..." : "Upload image"}
        </button>
      </div>

      {/* Upload status */}
      {uploadMutation.isError && (
        <div className="text-secondary-red text-sm text-center">
          Upload failed. Please try again.
        </div>
      )}
    </div>
  );
}
