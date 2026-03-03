#!/usr/bin/env python3
"""
Visual Parity Checker: Compare screenshots for structural similarity
Uses SSIM (Structural Similarity Index) to detect visual differences.
"""

import argparse
import sys
from pathlib import Path

try:
    from PIL import Image, ImageChops, ImageDraw
    from skimage.metrics import structural_similarity as ssim
    import numpy as np
except ImportError:
    print("Error: Required packages not installed.")
    print("Install with: pip install Pillow scikit-image numpy")
    sys.exit(1)


def load_and_resize(image_path: Path, target_size: tuple) -> Image.Image:
    """Load image and resize to target size."""
    img = Image.open(image_path)
    if img.size != target_size:
        print(f"Resizing {image_path.name} from {img.size} to {target_size}")
        img = img.resize(target_size, Image.Resampling.LANCZOS)
    return img


def compare_images(baseline_path: Path, current_path: Path, threshold: float = 85.0, output_path: Path = None) -> bool:
    """
    Compare two screenshots and return similarity percentage.

    Args:
        baseline_path: Path to baseline (legacy) screenshot
        current_path: Path to current (modern) screenshot
        threshold: Minimum similarity threshold (0-100)
        output_path: Optional path to save diff image

    Returns:
        True if similarity >= threshold, False otherwise
    """

    if not baseline_path.exists():
        print(f"Error: Baseline screenshot not found: {baseline_path}")
        sys.exit(1)

    if not current_path.exists():
        print(f"Error: Current screenshot not found: {current_path}")
        sys.exit(1)

    # Load images
    print(f"Loading baseline: {baseline_path}")
    baseline = Image.open(baseline_path).convert("RGB")

    print(f"Loading current: {current_path}")
    current = Image.open(current_path).convert("RGB")

    # Ensure same size
    if baseline.size != current.size:
        print(f"Resizing images to match: {baseline.size}")
        current = current.resize(baseline.size, Image.Resampling.LANCZOS)

    # Convert to numpy arrays
    baseline_array = np.array(baseline)
    current_array = np.array(current)

    # Calculate SSIM
    print("Calculating structural similarity...")
    similarity, diff_image = ssim(baseline_array, current_array, full=True, channel_axis=2)

    # Convert to percentage
    similarity_percent = similarity * 100

    print(f"\n{'='*60}")
    print(f"Visual Similarity: {similarity_percent:.2f}%")
    print(f"Threshold: {threshold:.2f}%")
    print(f"{'='*60}\n")

    # Create diff visualization
    if output_path:
        print(f"Generating diff image: {output_path}")

        # Normalize diff image to 0-255
        diff_image = (diff_image * 255).astype(np.uint8)

        # Create a colored diff (differences in red)
        diff_pil = Image.fromarray(diff_image).convert("L")

        # Threshold the diff to highlight significant differences
        threshold_value = 200  # Adjust to control sensitivity
        diff_binary = diff_pil.point(lambda p: 0 if p > threshold_value else 255)

        # Create RGB image with differences highlighted
        result = current.copy()
        result_array = np.array(result)

        # Apply red tint to differences
        diff_mask = np.array(diff_binary)
        result_array[:, :, 0] = np.where(diff_mask < 128,
                                         np.minimum(result_array[:, :, 0] + 100, 255),
                                         result_array[:, :, 0])

        result_highlighted = Image.fromarray(result_array)
        result_highlighted.save(output_path)
        print(f"✅ Diff image saved: {output_path}")

    # Report result
    if similarity_percent >= threshold:
        print(f"✅ PASS: Visual similarity ({similarity_percent:.2f}%) meets threshold ({threshold:.2f}%)")
        print("\nThe UI implementation matches the baseline screenshot.")
        return True
    else:
        print(f"❌ FAIL: Visual similarity ({similarity_percent:.2f}%) below threshold ({threshold:.2f}%)")
        print(f"\nVisual differences detected:")
        print(f"  - Difference: {100 - similarity_percent:.2f}%")
        print(f"\nPossible issues:")
        print(f"  - Missing layout elements (header, footer, sidebar)")
        print(f"  - Different component structure")
        print(f"  - Missing images or assets")
        print(f"  - Wrong styling (colors, spacing, fonts)")
        print(f"  - Missing content sections")

        if output_path:
            print(f"\nReview diff image for visual comparison: {output_path}")
            print(f"  - Red areas indicate differences")
            print(f"  - Focus on structural differences (layout, missing elements)")
            print(f"  - Minor color/style differences are acceptable if structure matches")

        return False


def main():
    parser = argparse.ArgumentParser(description="Compare screenshots for visual parity")
    parser.add_argument("baseline", type=Path, help="Path to baseline (legacy) screenshot")
    parser.add_argument("current", type=Path, help="Path to current (modern) screenshot")
    parser.add_argument("--threshold", type=float, default=85.0,
                        help="Similarity threshold percentage (default: 85)")
    parser.add_argument("--output", type=Path, help="Path to save diff image")

    args = parser.parse_args()

    passed = compare_images(args.baseline, args.current, args.threshold, args.output)

    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
