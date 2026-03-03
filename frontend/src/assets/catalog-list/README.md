# Catalog List Assets

Typed asset exports for the catalog-list seam.

## Usage

### Product Images

```typescript
import { catalogAssets, getProductImageUrl } from '@/assets/catalog-list'

// Using product ID
const imageUrl = catalogAssets.productImage(1) // "/pics/1.png"

// Using filename from API
const item = { picture_file_name: "5.png" }
const imageUrl2 = catalogAssets.productImageByFilename(item.picture_file_name) // "/pics/5.png"

// Smart helper with fallback
const imageUrl3 = getProductImageUrl(item.picture_file_name) // "/pics/5.png"
const imageUrl4 = getProductImageUrl(null) // "/pics/dummy.png" (fallback)
const imageUrl5 = getProductImageUrl("invalid.jpg") // "/pics/dummy.png" (fallback with console warning)
```

### CSS Classes

```typescript
import { catalogCssClasses } from '@/assets/catalog-list'
import { cn } from '@/lib/utils'

// Use typed class names
<button className={catalogCssClasses.buttonPrimary}>
  Create New
</button>

// Combine with conditional classes
<button className={cn(
  catalogCssClasses.pagerItem,
  catalogCssClasses.pagerItemNavigable,
  !hasNext && catalogCssClasses.pagerItemHidden
)}>
  Next
</button>
```

## Asset Inventory

### Images (frontend/public/pics/)
- `1.png` - .NET Bot Black Hoodie
- `2.png` - .NET Black & White Mug
- `3.png` - Prism White T-Shirt
- `4.png` - .NET Foundation T-shirt
- `5.png` - Roslyn Red Sheet
- `6.png` - .NET Blue Hoodie
- `7.png` - Roslyn Red T-Shirt
- `8.png` - Kudu Purple Hoodie
- `9.png` - Cup<T> White Mug
- `10.png` - .NET Foundation Sheet
- `11.png` - (Additional product)
- `12.png` - (Additional product)
- `13.png` - (Additional product)
- `dummy.png` - Placeholder/fallback image

### CSS Classes (frontend/src/styles/index.css)
All classes prefixed with `esh-` (eShop) for namespace isolation:

#### Table
- `esh-table` - Table container
- `esh-table-header` - Header row
- `esh-table-link` - Action links (Edit, Details, Delete)
- `esh-thumbnail` - Product image thumbnail
- `esh-price` - Price display ($ added via CSS :before)

#### Buttons
- `esh-button` - Button base
- `esh-button-primary` - Primary button (green)
- `esh-button-secondary` - Secondary button (red)
- `esh-button-actions` - Button group container

#### Pagination
- `esh-pager` - Pagination container
- `esh-pager-wrapper` - Pagination wrapper
- `esh-pager-item` - Individual pager element
- `esh-pager-item--navigable` - Clickable pager
- `esh-pager-item--hidden` - Hidden pager (opacity: 0)

#### Links
- `esh-link-wrapper` - Link wrapper
- `esh-link-item` - Link item
- `esh-link-item--margin` - Link with margin
- `esh-link-list` - Link list

#### Forms
- `esh-form-information` - Form info text

#### Misc
- `esh-picture` - Picture display (full size)
- `esh-body-title` - Page title

## Best Practices

### DO
✅ Use typed helpers from this module
✅ Import constants instead of hardcoding strings
✅ Use `getProductImageUrl()` for image paths
✅ Use `catalogCssClasses` for CSS class names
✅ Handle null/undefined picture filenames

### DON'T
❌ Hardcode image paths like "/pics/1.png"
❌ Hardcode CSS class names like "esh-button-primary"
❌ Assume picture_file_name is always valid
❌ Skip fallback handling for missing images

## Migration from Legacy

| Legacy Code | React Code |
|-------------|------------|
| `/Pics/<%#:Item.PictureFileName%>` | `getProductImageUrl(item.picture_file_name)` |
| `<asp:Image CssClass="esh-thumbnail" ... />` | `<img className={catalogCssClasses.thumbnail} ... />` |
| `CssClass="btn esh-button esh-button-primary"` | `className={catalogCssClasses.buttonPrimary}` |

## Type Safety

All exports are fully typed:

```typescript
// ✅ Type-safe
const imageUrl: string = catalogAssets.productImage(1)

// ✅ Autocomplete works
const className: string = catalogCssClasses.thumbnail

// ✅ Compile-time error if property doesn't exist
const invalid = catalogCssClasses.nonExistent // Error: Property 'nonExistent' does not exist
```

## Source Attribution

- **Images**: Copied from legacy `Pics/*.png`
- **CSS Classes**: Extracted from legacy `Content/Site.css`
- **Structure**: Defined in `docs/seams/catalog-list/ui-behavior.md`
- **Runtime Data**: Verified against `legacy-golden/grid-data.json`
