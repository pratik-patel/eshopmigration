# Runtime Observations: Catalog CRUD Operations

**Captured From**: http://localhost:50586/
**Date**: 2026-03-02
**Browser**: [Chrome/Firefox/Edge]

---

## CREATE PAGE

**URL**: http://localhost:50586/Catalog/Create

### Page Layout
- **Page Title**: [exact title]
- **Heading**: [H2 text]
- **Form Layout**: [1-column / 2-column / other]

### Form Fields (in order)

**1. Name Field**
- Label: [exact text]
- Input Type: [text / textarea]
- CSS Class: [e.g., "form-control"]
- Placeholder: [if any]
- Default Value: [empty or pre-filled]
- Required Indicator: [asterisk / text / none]

**2. Description Field**
- Label: [exact text]
- Input Type: [text / textarea]
- Required: [yes/no]

**3. Brand Dropdown**
- Label: [exact text]
- CSS Class: [e.g., "form-control"]
- Options (in order):
  1. [option 1, e.g., "Azure"]
  2. [option 2, e.g., ".NET"]
  3. [etc.]
- Default Selection: [first item / none / placeholder]

**4. Type Dropdown**
- Label: [exact text]
- Options (in order):
  1. [option 1, e.g., "Mug"]
  2. [option 2]
  3. [etc.]

**5. Price Field**
- Label: [exact text]
- Input Type: [text / number]
- Default Value: [e.g., "0.00"]
- Step: [if number input]

**6. Picture Name Field**
- Label: [exact text]
- Display: [input field / informational text / disabled]
- Text: [e.g., "Uploading images not allowed for this version."]
- CSS Class: [e.g., "esh-form-information"]

**7. Stock Field**
- Label: [exact text, e.g., "Stock" or "Available Stock"]
- Default Value: [e.g., "0"]

**8. Restock Field**
- Label: [exact text, e.g., "Restock" or "Restock Threshold"]
- Default Value: [e.g., "0"]

**9. Max Stock Field**
- Label: [exact text, e.g., "Max stock" or "Max Stock Threshold"]
- Default Value: [e.g., "0"]

### Form Buttons

**Cancel Button**:
- Text: [e.g., "[ Cancel ]" or "Cancel"]
- CSS Classes: [e.g., "btn esh-button esh-button-secondary"]
- Position: [left / right]
- Action: [navigates to / or stays]

**Create Button**:
- Text: [e.g., "[ Create ]" or "Create"]
- CSS Classes: [e.g., "btn esh-button esh-button-primary"]
- Position: [left / right]

**Button Container**:
- Alignment: [left / center / right]
- CSS Class: [e.g., "esh-button-actions text-right"]

### Validation Testing

**Test 1: Submit Empty Form**
- Click Create with all fields empty
- Error messages displayed:
  - Name: [exact message, e.g., "The Name field is required."]
  - (Other fields if required)
- Error position: [inline below field / at top / other]
- Error styling: [red text / red border / both]
- Error CSS class: [e.g., "text-danger field-validation-valid"]

**Test 2: Invalid Price**
- Enter "abc" in price field
- Error message: [exact text]

**Test 3: Price with 3 Decimals**
- Enter "12.999" in price field
- Error message: [exact text or accepted]

**Test 4: Price Out of Range**
- Enter "99999999999999999" in price field
- Error message: [exact text]

**Test 5: Stock Out of Range**
- Enter "99999999" in stock field
- Error message: [exact text]

**Test 6: Successful Creation**
- Fill all required fields with valid data
- Click Create
- Result: [redirects to catalog list / shows success message / other]

### Styling Details

- **Label Width**: [e.g., "col-md-2"]
- **Input Width**: [e.g., "col-md-3"]
- **Form Horizontal**: [yes/no, CSS class]
- **Form Group**: [CSS class, e.g., "form-group"]

---

## EDIT PAGE

**URL**: http://localhost:50586/Catalog/Edit/1

### Page Layout

**2-Column Layout**:
- Left Column: [Product image]
  - Width: [e.g., "col-md-6"]
  - CSS Class: [e.g., "esh-picture"]
  - Image Size: [width x height]
- Right Column: [Form]
  - Width: [e.g., "col-md-6"]

### Form Differences from Create

**Pre-filled Values** (for product ID 1):
- Name: [value]
- Description: [value]
- Brand: [selected option]
- Type: [selected option]
- Price: [value]
- Picture Name: [value]
- Stock: [value]
- Restock: [value]
- Max Stock: [value]

**Picture Name Field**:
- Input Type: [text / disabled]
- ReadOnly: [yes/no]
- Tooltip: [exact text, e.g., "Not allowed for edition"]

**Save Button**:
- Text: [e.g., "[ Save ]" or "Save"]
- (Same styling as Create button?)

### Validation Testing

**Test 1: Change Name and Save**
- Change name to "Updated Name"
- Click Save
- Result: [redirects to catalog list / shows success / other]

**Test 2: Invalid Price**
- Change price to "abc"
- Click Save
- Error message: [exact text - same as Create or different?]

---

## DETAILS PAGE

**URL**: http://localhost:50586/Catalog/Details/1

### Page Layout

**2-Column Layout** (same as Edit?):
- Left: Product image
- Right: Product details (read-only)

### Display Format

For each field, document:
- Label: [exact text]
- Value Display: [format]
- Styling: [different from editable fields?]

**Example**:
- Name:
  - Label: [e.g., "Name:"]
  - Value: [e.g., ".NET Bot Black Hoodie"]
  - Format: [label on left, value on right / vertical / other]

### Action Buttons

**Edit Button**:
- Text: [exact text]
- CSS Classes: [e.g., "btn esh-button esh-button-primary"]
- Action: [navigates to Edit page]

**Back to List**:
- Text: [exact text]
- Type: [button / link]
- CSS Classes: [e.g., "btn esh-button esh-button-secondary"]

---

## DELETE PAGE

**URL**: http://localhost:50586/Catalog/Delete/1

### Confirmation Message

- **Heading**: [exact text, e.g., "Delete"]
- **Message**: [exact text, e.g., "Are you sure you want to delete this?"]
- **Message Position**: [top / above product details / other]
- **Message Styling**: [warning color / bold / other]

### Product Display

- **Layout**: [same as Details page or different?]
- **Fields Shown**: [all fields or subset?]

### Action Buttons

**Delete Button**:
- Text: [exact text]
- CSS Classes: [e.g., "btn esh-button esh-button-primary" or different for danger?]
- Color: [red / blue / other]

**Back to List**:
- Text: [exact text]
- CSS Classes: [same as Details page]

### Delete Action

**Test: Click Delete**
- Click Delete button
- Confirmation: [JavaScript confirm() dialog / no additional confirmation / other]
- Result: [redirects to catalog list]
- Product removed: [verify product no longer in list]

---

## Validation Error Styling

### Error Display Format

- **Position**: [below field / above field / at top of form]
- **CSS Class**: [e.g., "field-validation-valid text-danger"]
- **Color**: [hex code]
- **Font Size**: [relative to field text]
- **Display Property**: [inline / block / inline-block]
- **Visibility**: [hidden initially, shown on validation / always visible]

### Error Messages (Complete List)

| Field | Invalid Input | Exact Error Message |
|-------|---------------|---------------------|
| Name | (empty) | [e.g., "The Name field is required."] |
| Price | "abc" | [exact message] |
| Price | "12.999" | [exact message or accepted] |
| Price | "-5" | [exact message] |
| Price | "2000000" | [exact message] |
| Stock | "-1" | [exact message] |
| Stock | "99999999" | [exact message] |
| Restock | "99999999" | [exact message] |
| Max Stock | "99999999" | [exact message] |

---

## Dropdown Population

### Brands Dropdown

**Complete list of options (in order)**:
1. [option 1]
2. [option 2]
3. [etc.]

**Total count**: [e.g., 5 brands]

### Types Dropdown

**Complete list of options (in order)**:
1. [option 1]
2. [option 2]
3. [etc.]

**Total count**: [e.g., 4 types]

---

## Form Styling Details

### Layout Classes

- **Form Wrapper**: [e.g., "form-horizontal"]
- **Form Group**: [e.g., "form-group"]
- **Label**: [e.g., "control-label col-md-2" or different for Edit "col-md-4"]
- **Input Container**: [e.g., "col-md-3" or different for Edit "col-md-8"]

### Input Styling

- **Background**: [white / gray]
- **Border**: [1px solid #ccc / other]
- **Border Radius**: [rounded corners?]
- **Padding**: [approximate]
- **Focus State**: [border color change / shadow / other]

---

## Screenshots Captured

**Create Page**:
- [ ] `catalog-create-01-empty-form.png`
- [ ] `catalog-create-02-validation-errors.png`
- [ ] `catalog-create-03-brand-dropdown-expanded.png`
- [ ] `catalog-create-04-type-dropdown-expanded.png`
- [ ] `catalog-create-05-one-field-filled.png`

**Edit Page**:
- [ ] `catalog-edit-01-full-page-with-image.png`
- [ ] `catalog-edit-02-validation-error.png`
- [ ] `catalog-edit-03-readonly-picture-field.png`

**Details Page**:
- [ ] `catalog-details-01-full-page.png`

**Delete Page**:
- [ ] `catalog-delete-01-confirmation.png`
- [ ] `catalog-delete-02-after-delete.png`

---

## Comparison with Static Analysis

### Matches ✅
- [ ] Field order matches code
- [ ] Field labels match code
- [ ] Validation messages match code
- [ ] Default values match code
- [ ] Button text matches code

### Differences ⚠️
[List any differences]

---

## Additional Observations

[Any other findings]

---

**Capture Status**: [In Progress / Complete]
**Next Steps**: [e.g., "Begin implementing Create page component"]
