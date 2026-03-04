/**
 * ProductImage component.
 *
 * Displays product images with proper sizing and loading states.
 * Matches legacy asp:Image control behavior.
 */

import { useState } from "react";
import { getProductImageUri } from "@/assets/catalog";

interface ProductImageProps {
  /** Product picture filename (e.g., "1.png") */
  pictureFileName: string | null | undefined;
  /** Product name for alt text */
  alt: string;
  /** Size variant: thumbnail (120px) or full (370px) */
  size: "thumbnail" | "full";
  /** Optional custom CSS class */
  className?: string;
}

/**
 * Display product image with fallback to dummy.png.
 *
 * Matches ui-specification.json:
 * - Thumbnail: .esh-thumbnail (max-width: 120px)
 * - Full: .esh-picture (max-width: 370px)
 */
export function ProductImage({
  pictureFileName,
  alt,
  size,
  className,
}: ProductImageProps) {
  const [isLoading, setIsLoading] = useState(true);
  const [hasError, setHasError] = useState(false);

  // Get image URI (handles null/empty, returns dummy.png as fallback)
  const imageUri = getProductImageUri(pictureFileName);

  // Determine CSS class based on size
  const sizeClass = size === "thumbnail" ? "esh-thumbnail" : "esh-picture";

  return (
    <div className={`relative ${className || ""}`}>
      {/* Loading placeholder */}
      {isLoading && (
        <div className={`${sizeClass} bg-neutral-gray-light animate-pulse`} />
      )}

      {/* Actual image */}
      <img
        src={imageUri}
        alt={alt}
        className={`${sizeClass} ${isLoading ? "hidden" : ""}`}
        onLoad={() => setIsLoading(false)}
        onError={() => {
          setIsLoading(false);
          setHasError(true);
        }}
      />

      {/* Error state */}
      {hasError && (
        <div
          className={`${sizeClass} bg-neutral-gray-light flex items-center justify-center text-neutral-gray-medium text-sm`}
        >
          Image not available
        </div>
      )}
    </div>
  );
}
