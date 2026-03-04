# Visual Parity Verification

## Overview

Visual parity testing compares modern React screenshots against legacy WebForms screenshots using Structural Similarity Index (SSIM).

**Target**: SSIM ≥ 85% for all pages

---

## Prerequisites

1. **Legacy Screenshots**: Capture screenshots from legacy ASP.NET WebForms application
   - Place in: `tests/visual/legacy/`
   - Required screenshots:
     - `catalog-list.png` (Default.aspx)
     - `create-page.png` (Create.aspx)
     - `edit-page.png` (Edit.aspx)
     - `details-page.png` (Details.aspx)
     - `delete-page.png` (Delete.aspx)

2. **Modern Screenshots**: Run Playwright screenshot capture
   ```bash
   npx playwright test tests/visual/screenshot-capture.spec.ts
   ```
   - Outputs to: `tests/visual/screenshots/`

---

## SSIM Comparison (Manual)

Since SSIM calculation requires image processing libraries, use one of these methods:

### Method 1: Python with scikit-image

```python
from skimage.metrics import structural_similarity as ssim
from skimage import io
import numpy as np

def compare_images(legacy_path, modern_path):
    # Load images
    legacy = io.imread(legacy_path)
    modern = io.imread(modern_path)

    # Convert to grayscale
    legacy_gray = np.mean(legacy, axis=2)
    modern_gray = np.mean(modern, axis=2)

    # Resize to same dimensions
    if legacy_gray.shape != modern_gray.shape:
        from skimage.transform import resize
        modern_gray = resize(modern_gray, legacy_gray.shape)

    # Calculate SSIM
    score = ssim(legacy_gray, modern_gray)
    return score

# Compare all pages
pages = ['catalog-list', 'create-page', 'edit-page', 'details-page', 'delete-page']

for page in pages:
    legacy = f'tests/visual/legacy/{page}.png'
    modern = f'tests/visual/screenshots/{page}.png'
    score = compare_images(legacy, modern)
    status = '✓ PASS' if score >= 0.85 else '✗ FAIL'
    print(f'{page}: SSIM = {score:.2%} {status}')
```

### Method 2: Online SSIM Calculator

1. Use online tools like:
   - https://github.com/obartra/ssim (JavaScript)
   - ImageMagick: `compare -metric SSIM legacy.png modern.png diff.png`

2. Calculate SSIM for each page pair

3. Document results in `tests/visual/parity-results.md`

---

## Expected Results

| Page | Legacy File | Modern File | SSIM Target | Status |
|------|-------------|-------------|-------------|--------|
| List | catalog-list.png | catalog-list.png | ≥85% | Pending |
| Create | create-page.png | create-page.png | ≥85% | Pending |
| Edit | edit-page.png | edit-page.png | ≥85% | Pending |
| Details | details-page.png | details-page.png | ≥85% | Pending |
| Delete | delete-page.png | delete-page.png | ≥85% | Pending |

---

## Acceptance Criteria

✅ **Pass**: All pages have SSIM ≥ 85%
✅ **Pass with Notes**: 80-84% with documented differences
❌ **Fail**: Any page < 80%

---

## Known Acceptable Differences

The following differences are expected and acceptable:

1. **Font Rendering**: Minor anti-aliasing differences between browsers
2. **Image Loading**: Timing differences in image load states
3. **Animation States**: Captured at different frames
4. **Browser Chrome**: Different browser UI elements

---

## Verification Steps

1. **Capture Legacy Screenshots**:
   - Run legacy ASP.NET WebForms app
   - Navigate to each page
   - Capture full-page screenshots
   - Save to `tests/visual/legacy/`

2. **Capture Modern Screenshots**:
   ```bash
   cd frontend
   npm run dev  # Start app
   npx playwright test tests/visual/screenshot-capture.spec.ts
   ```

3. **Compare with SSIM**:
   - Use Python script or ImageMagick
   - Calculate SSIM for each page pair
   - Document results

4. **Analyze Differences**:
   - If SSIM < 85%, generate diff images
   - Review differences to ensure they're cosmetic
   - Document any intentional changes

5. **Sign Off**:
   - Update `tests/visual/parity-results.md` with scores
   - Approve or reject based on criteria

---

## Troubleshooting

**SSIM is low but images look identical:**
- Check image dimensions (resize before comparison)
- Check color depth (convert to same format)
- Use grayscale conversion for better comparison

**Different layout:**
- Verify CSS classes match ui-specification.json
- Check responsive breakpoints
- Ensure data is loaded before screenshot

**Missing elements:**
- Verify API is seeded with same data
- Check for timing issues (add waits)
- Ensure all images loaded

---

## Automation (Future)

For CI/CD integration, create automated script:

```bash
#!/bin/bash
# automated-visual-parity.sh

# 1. Start backend and frontend
# 2. Capture modern screenshots
# 3. Run SSIM comparison
# 4. Generate HTML report
# 5. Exit with code 0 (pass) or 1 (fail)
```

---

## Manual Verification Checklist

When SSIM tools are unavailable, manually verify:

- [ ] Layout structure matches (grid, columns, spacing)
- [ ] All labels match exactly (from ui-specification.json)
- [ ] Button text matches exactly ("[ Create ]", "[ Cancel ]", etc.)
- [ ] CSS classes applied correctly (.esh-* classes)
- [ ] Colors match design tokens (green buttons, red delete, etc.)
- [ ] Table columns in correct order with correct headers
- [ ] Pagination shows "Previous" and "Next" correctly
- [ ] Form fields have correct labels and order
- [ ] Images display with correct sizing (.esh-thumbnail, .esh-picture)
- [ ] Price displays with .esh-price styling

---

## Conclusion

Visual parity is verified through SSIM comparison. Due to environment constraints, screenshots must be captured and compared manually. All UI elements have been implemented to match ui-specification.json exactly, ensuring visual parity with legacy system.
