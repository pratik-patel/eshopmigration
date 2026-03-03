# Static Assets - Catalog CRUD Operations

**Append this section to**: `docs/seams/catalog-crud/ui-behavior.md`

---

## Static Assets

### CSS Stylesheets
**Source**: `Content/Site.css`
**Destination**: `frontend/src/styles/forms.css`

**Bootstrap Form Classes Used**:
- `form-group` - Form field grouping
- `form-control` - Input/select styling
- `btn` - Button base
- `btn-default` - Secondary button
- `btn-primary` - Primary button
- `text-danger` - Validation error text
- `validation-summary-errors` - Error summary list
- `field-validation-error` - Field-level error messages
- `field-validation-valid` - Valid field state
- `control-label` - Form label styling
- `form-horizontal` - Horizontal form layout
- `col-md-*` - Bootstrap grid columns

**Custom eShop Classes**:
- `esh-body-title` - Page heading
- `esh-button` - Button styling
- `esh-button-primary` - Primary action button
- `esh-button-secondary` - Secondary/cancel button
- `esh-button-actions` - Button container
- `esh-form-information` - Informational message styling
- `esh-picture` - Product image display (Edit/Details/Delete pages)

**Migration Action**: **HIGH PRIORITY**
1. Extract form-related CSS from `Content/Site.css`
2. Create `frontend/src/styles/forms.css`
3. Map to React Hook Form error display components
4. Preserve validation message styling exactly

### Validation Scripts
**Source**: `Scripts/WebForms/ValidationScripts.js`
**Action**: DO NOT COPY
**Replacement**: React Hook Form + Zod validation
**Notes**: WebForms validation is framework-specific. Implement with modern validation library.

### Product Images
**Source**: `Pics/*.png` (referenced from Edit/Details/Delete pages)
**Destination**: `frontend/public/pics/`
**Usage**: Image display on Edit, Details, and Delete pages
**Path Template**: `/pics/{pictureFileName}`
**CSS Class**: `esh-picture` for sizing/positioning

**Notes**:
- Same images as catalog-list seam
- Images are displayed but not editable in forms
- PictureFileName field is read-only in Edit page

## Asset Migration Checklist

- [ ] Extract form CSS classes from `Content/Site.css`
- [ ] Create `frontend/src/styles/forms.css`
- [ ] Map validation error classes to React Hook Form error components
- [ ] Preserve button styling (esh-button classes)
- [ ] Extract image display CSS (esh-picture class)
- [ ] Test validation message display matches legacy
- [ ] Verify form field order and layout
- [ ] Test error summary styling
- [ ] Validate dropdown styling matches legacy
- [ ] Test product image display on Edit/Details/Delete pages
- [ ] Verify button spacing and alignment
- [ ] Compare form layout to legacy screenshots

## Validation Rules Preservation

**Critical**: All validation rules, error messages, and field constraints must match legacy exactly.

### Price Field Validation
- **Pattern**: `^\\d+(\\.\\d{0,2})*$` (positive decimal, max 2 decimals)
- **Range**: 0-9999999999999999.99 (legacy shows 0-1,000,000 in UI)
- **Error Message**: "The field Price must be a number."
- **Additional Error**: "Price must have at most 2 decimal places."

### Stock Fields Validation
- **Range**: 0-10000000 (integer)
- **Fields**: AvailableStock, RestockThreshold, MaxStockThreshold
- **Error Message**: "The field {FieldName} must be between 0 and 10000000."

### Required Fields
- Name
- Price (with default "0.00")
- CatalogBrandId (Brand dropdown)
- CatalogTypeId (Type dropdown)

**Error Message**: "The {FieldName} field is required."

### Default Values
- **PictureFileName**: `"dummy.png"` if not provided
- **Price**: `"0.00"`
- **Stock fields**: `"0"`

## Migration Notes

### Zod Schema Example
```typescript
import { z } from 'zod';

const catalogItemSchema = z.object({
  name: z.string().min(1, "The Name field is required."),
  description: z.string().optional(),
  price: z.number()
    .min(0, "The field Price must be a number.")
    .max(9999999999999999.99, "Price exceeds maximum.")
    .refine(val => {
      const str = val.toString();
      const decimalIndex = str.indexOf('.');
      return decimalIndex === -1 || str.length - decimalIndex - 1 <= 2;
    }, "Price must have at most 2 decimal places."),
  catalogBrandId: z.number().min(1, "The Brand field is required."),
  catalogTypeId: z.number().min(1, "The Type field is required."),
  availableStock: z.number()
    .int()
    .min(0)
    .max(10000000, "The field Available Stock must be between 0 and 10000000."),
  restockThreshold: z.number()
    .int()
    .min(0)
    .max(10000000, "The field Restock Threshold must be between 0 and 10000000."),
  maxStockThreshold: z.number()
    .int()
    .min(0)
    .max(10000000, "The field Max Stock Threshold must be between 0 and 10000000."),
  pictureFileName: z.string().default("dummy.png"),
});
```

### React Hook Form Integration
```typescript
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';

const { register, handleSubmit, formState: { errors } } = useForm({
  resolver: zodResolver(catalogItemSchema),
  defaultValues: {
    price: 0.00,
    availableStock: 0,
    restockThreshold: 0,
    maxStockThreshold: 0,
    pictureFileName: "dummy.png",
  }
});
```

### Error Display Component
```typescript
function FieldError({ error }: { error?: FieldError }) {
  if (!error) return null;
  return <span className="text-danger field-validation-error">{error.message}</span>;
}
```

### Form Field Component
```typescript
interface FormFieldProps {
  label: string;
  name: string;
  type?: string;
  register: any;
  error?: FieldError;
  readonly?: boolean;
  defaultValue?: string | number;
}

function FormField({ label, name, type, register, error, readonly, defaultValue }: FormFieldProps) {
  return (
    <div className="form-group">
      <label className="control-label col-md-4">{label}</label>
      <div className="col-md-8">
        <input
          type={type || "text"}
          className="form-control"
          readOnly={readonly}
          defaultValue={defaultValue}
          {...register(name)}
        />
        <FieldError error={error} />
      </div>
    </div>
  );
}
```

## CSS Extraction Requirements

### esh-button Classes
Extract these exact styles from `Content/Site.css`:
```css
.esh-button {
  /* Base button styling */
}

.esh-button-primary {
  /* Primary action button (blue) */
}

.esh-button-secondary {
  /* Secondary/cancel button (gray) */
}

.esh-button-actions {
  /* Button container alignment */
}
```

### esh-picture Class
```css
.esh-picture {
  /* Product image sizing and positioning */
  /* Used on Edit, Details, Delete pages */
}
```

### Form Layout Classes
```css
.esh-body-title {
  /* Page heading styling */
}

.esh-form-information {
  /* Informational message styling */
  /* Used for "Uploading images not allowed" message */
}
```

## Test Scenarios

1. **Create form - required field validation**
   - Leave Name blank, submit
   - Verify error: "The Name field is required."
   - Error styling matches legacy

2. **Create form - price validation**
   - Enter "abc" in Price, submit
   - Verify error: "The field Price must be a number."
   - Enter "123.456", submit
   - Verify error: "Price must have at most 2 decimal places."

3. **Create form - stock validation**
   - Enter "20000000" in Available Stock
   - Verify error: "The field Available Stock must be between 0 and 10000000."

4. **Edit form - populate existing values**
   - Navigate to Edit/{id}
   - Verify all fields pre-populated
   - Verify product image displays on left
   - Verify dropdown selections match existing data
   - Verify PictureFileName is read-only

5. **Edit form - image display**
   - Verify product image loads from `/pics/{pictureFileName}`
   - Verify image uses `.esh-picture` class
   - Verify image positioned correctly (left column)

6. **Details page - read-only display**
   - Navigate to Details/{id}
   - Verify all fields shown as text (no form controls)
   - Verify product image displays
   - Verify Edit and Back to List buttons present

7. **Delete page - confirmation**
   - Navigate to Delete/{id}
   - Verify confirmation message: "Are you sure you want to delete this?"
   - Verify product details and image display
   - Verify Delete and Back to List buttons present

8. **Styling preservation**
   - Compare form layout to legacy screenshot
   - Verify button spacing and alignment
   - Verify error message styling
   - Verify form field widths and labels
   - Verify image display on Edit/Details/Delete pages
   - Verify validation error colors and positioning
