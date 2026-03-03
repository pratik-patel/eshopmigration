# UI Behavior: Catalog CRUD Operations

**Seam**: catalog-crud
**Legacy Pages**: Catalog/Create.aspx, Catalog/Edit.aspx, Catalog/Details.aspx, Catalog/Delete.aspx
**Routes**: `/Catalog/Create`, `/Catalog/Edit/{id}`, `/Catalog/Details/{id}`, `/Catalog/Delete/{id}`

---

## Overview

This seam encompasses all CRUD (Create, Read, Update, Delete) operations for catalog items through dedicated form pages.

---

## 1. CREATE PAGE

### Page: Catalog/Create.aspx

**Route**: `/Catalog/Create`
**Master Page**: Site.Master
**Title**: "Create"

### Layout

```
┌───────────────────────────────────────────┐
│ Create                                    │
├───────────────────────────────────────────┤
│ Name:         [___________________]       │
│                                           │
│ Description:  [___________________]       │
│                                           │
│ Brand:        [Dropdown ▼]                │
│                                           │
│ Type:         [Dropdown ▼]                │
│                                           │
│ Price:        [___________________]       │
│                                           │
│ Picture name: Uploading images not        │
│               allowed for this version.   │
│                                           │
│ Stock:        [___________________]       │
│                                           │
│ Restock:      [___________________]       │
│                                           │
│ Max stock:    [___________________]       │
│                                           │
│               [[ Cancel ]] [[ Create ]]   │
└───────────────────────────────────────────┘
```

### Form Controls

#### 1. Name Field
- **Control**: `<asp:TextBox ID="Name">`
- **CSS Class**: `form-control`
- **Required**: Yes
- **Validator**: RequiredFieldValidator
- **Error Message**: "The Name field is required."
- **Error CSS**: `field-validation-valid text-danger`
- **Display**: Dynamic (appears inline when validation fails)

#### 2. Description Field
- **Control**: `<asp:TextBox ID="Description">`
- **CSS Class**: `form-control`
- **Required**: No
- **Validator**: None

#### 3. Brand Dropdown
- **Control**: `<asp:DropDownList ID="Brand">`
- **CSS Class**: `form-control`
- **Data Source**: `GetBrands()` method
- **Data Binding**:
  - ItemType: `CatalogBrand`
  - DataTextField: `Brand`
  - DataValueField: `Id`
- **Population**: Calls `CatalogService.GetCatalogBrands()` on page load

#### 4. Type Dropdown
- **Control**: `<asp:DropDownList ID="Type">`
- **CSS Class**: `form-control`
- **Data Source**: `GetTypes()` method
- **Data Binding**:
  - ItemType: `CatalogType`
  - DataTextField: `Type`
  - DataValueField: `Id`
- **Population**: Calls `CatalogService.GetCatalogTypes()` on page load

#### 5. Price Field
- **Control**: `<asp:TextBox ID="Price">`
- **CSS Class**: `form-control`
- **Default Value**: "0.00"
- **Validator**: RangeValidator
  - Type: Currency
  - MinimumValue: 0
  - MaximumValue: 1,000,000
  - ErrorMessage: "The Price must be a positive number with maximum two decimals between 0 and 1 million."
  - CSS Class: `text-danger`
  - Display: Dynamic

#### 6. Picture Name Field
- **Display**: Informational message only
- **CSS Class**: `esh-form-information`
- **Message**: "Uploading images not allowed for this version."
- **Note**: No actual input control - image upload not implemented

#### 7. Stock Field
- **Control**: `<asp:TextBox ID="Stock">`
- **CSS Class**: `form-control`
- **Default Value**: "0"
- **Validator**: RangeValidator
  - Type: Integer
  - MinimumValue: 0
  - MaximumValue: 10,000,000
  - ErrorMessage: "The field Stock must be between 0 and 10 million."
  - CSS Class: `text-danger`
  - Display: Dynamic

#### 8. Restock Field
- **Control**: `<asp:TextBox ID="Restock">`
- **CSS Class**: `form-control`
- **Default Value**: "0"
- **Validator**: RangeValidator (same as Stock)

#### 9. Max Stock Field
- **Control**: `<asp:TextBox ID="Maxstock">`
- **CSS Class**: `form-control`
- **Default Value**: "0"
- **Validator**: RangeValidator (same as Stock)

### Form Actions

#### Cancel Button
- **Control**: `<a runat="server" href="~">`
- **CSS Classes**: `btn esh-button esh-button-secondary`
- **Text**: "[ Cancel ]"
- **Action**: Navigate back to home page (catalog list)

#### Create Button
- **Control**: `<asp:Button>`
- **CSS Classes**: `btn esh-button esh-button-primary`
- **Text**: "[ Create ]"
- **OnClick Event**: `Create_Click`
- **Container CSS**: `col-md-offset-2 col-md-3 text-right esh-button-actions`

### Code-Behind Logic (Create.aspx.cs)

#### Page Load
```csharp
protected void Page_Load(object sender, EventArgs e)
{
    _log.Info($"Now loading... /Catalog/Create.aspx");
    // Dropdowns auto-populate via SelectMethod
}
```

#### GetBrands Method
```csharp
public IEnumerable<CatalogBrand> GetBrands()
{
    return CatalogService.GetCatalogBrands();
}
```

#### GetTypes Method
```csharp
public IEnumerable<CatalogType> GetTypes()
{
    return CatalogService.GetCatalogTypes();
}
```

#### Create_Click Event
```csharp
protected void Create_Click(object sender, EventArgs e)
{
    if (this.ModelState.IsValid)
    {
        var catalogItem = new CatalogItem
        {
            Name = Name.Text,
            Description = Description.Text,
            CatalogBrandId = int.Parse(Brand.SelectedValue),
            CatalogTypeId = int.Parse(Type.SelectedValue),
            Price = decimal.Parse(Price.Text),
            AvailableStock = int.Parse(Stock.Text),
            RestockThreshold = int.Parse(Restock.Text),
            MaxStockThreshold = int.Parse(Maxstock.Text)
            // PictureFileName defaults to "dummy.png" (model default)
        };

        CatalogService.CreateCatalogItem(catalogItem);
        Response.Redirect("~"); // Redirect to catalog list
    }
}
```

**Flow**:
1. Check if ModelState.IsValid (all validators passed)
2. Create new CatalogItem from form fields
3. Parse dropdown selected values (IDs)
4. Call `CatalogService.CreateCatalogItem()`
5. Redirect to catalog list page

### User Interactions

1. **Navigate to Create page**
   - Click "Create New" button from catalog list
   - Brand and Type dropdowns auto-populate

2. **Fill form**
   - Enter Name (required)
   - Enter Description (optional)
   - Select Brand from dropdown
   - Select Type from dropdown
   - Enter Price (validates on submit)
   - Enter Stock values (validates on submit)

3. **Submit form**
   - Click Create button
   - Validators run:
     - Name: required
     - Price: range 0-1,000,000, currency
     - Stock fields: range 0-10,000,000, integer
   - If validation fails: error messages display inline
   - If validation passes: save to database and redirect to catalog list

4. **Cancel**
   - Click Cancel button
   - Navigate back to catalog list without saving

---

## 2. EDIT PAGE

### Page: Catalog/Edit.aspx

**Route**: `/Catalog/Edit/{id}`
**Master Page**: Site.Master
**Title**: "Edit"

### Layout

```
┌─────────────────────────────────────────────┐
│ Edit                                        │
├─────────────────────────────────────────────┤
│ [Product Image]  │ Name:       [_______]    │
│                  │                          │
│                  │ Description:[_______]    │
│                  │                          │
│                  │ Brand:      [Dropdown▼]  │
│                  │                          │
│                  │ Type:       [Dropdown▼]  │
│                  │                          │
│                  │ Price:      [_______]    │
│                  │                          │
│                  │ Picture:    [_______]    │
│                  │             (readonly)   │
│                  │                          │
│                  │ Stock:      [_______]    │
│                  │                          │
│                  │ Restock:    [_______]    │
│                  │                          │
│                  │ Max stock:  [_______]    │
│                  │                          │
│                  │ [[ Cancel ]] [[ Save ]]  │
└─────────────────────────────────────────────┘
```

### Key Differences from Create

#### 1. Product Image Display
- **Control**: `<asp:Image runat="server">`
- **CSS Class**: `col-md-6 esh-picture`
- **ImageUrl**: `<%#"/Pics/" + product.PictureFileName%>`
- **Position**: Left side of form (col-md-6)

#### 2. Form Pre-population
- All fields pre-filled with existing product data
- Data bound using `<%#product.PropertyName%>` syntax
- Example: `<asp:TextBox Text='<%#product.Name%>'>`

#### 3. Picture Name Field
- **Control**: `<asp:TextBox ID="PictureFileName">`
- **ReadOnly**: true
- **ToolTip**: "Not allowed for edition"
- **Note**: Can view but not edit picture filename

#### 4. Save Button
- **Text**: "[ Save ]" (instead of "[ Create ]")
- **OnClick Event**: `Save_Click`

### Form Layout (Edit)

- **Container**: `<div class="container">` → `<div class="row">`
- **Left Column**: Product image (`col-md-6`)
- **Right Column**: Form fields (`col-md-6 form-horizontal`)
- **Label Width**: `col-md-4` (wider than Create page)
- **Input Width**: `col-md-8`

### Code-Behind Logic (Edit.aspx.cs)

#### Page Load
```csharp
protected void Page_Load(object sender, EventArgs e)
{
    var productId = Convert.ToInt32(RouteData.Values["id"]);
    product = CatalogService.FindCatalogItem(productId);

    if (!IsPostBack)
    {
        DataBind(); // Bind product data to form controls
        PopulateDropDowns();
        SetSelectedBrand();
        SetSelectedType();
    }
}
```

#### Save_Click Event
```csharp
protected void Save_Click(object sender, EventArgs e)
{
    if (this.ModelState.IsValid)
    {
        product.Name = Name.Text;
        product.Description = Description.Text;
        product.CatalogBrandId = int.Parse(BrandDropDownList.SelectedValue);
        product.CatalogTypeId = int.Parse(TypeDropDownList.SelectedValue);
        product.Price = decimal.Parse(Price.Text);
        product.AvailableStock = int.Parse(Stock.Text);
        product.RestockThreshold = int.Parse(Restock.Text);
        product.MaxStockThreshold = int.Parse(Maxstock.Text);
        // PictureFileName is readonly, not updated

        CatalogService.UpdateCatalogItem(product);
        Response.Redirect("~");
    }
}
```

### User Interactions

1. **Navigate to Edit page**
   - Click "Edit" link from catalog list
   - Page loads with product data pre-filled
   - Product image displays on left
   - Dropdowns show current Brand/Type selected

2. **Edit fields**
   - Modify Name, Description, Price, Stock values
   - Change Brand/Type via dropdowns
   - Picture filename is read-only

3. **Save changes**
   - Click Save button
   - Validation runs (same as Create)
   - If valid: update database and redirect to catalog list
   - If invalid: show error messages

4. **Cancel**
   - Click Cancel button
   - Navigate back to catalog list without saving changes

---

## 3. DETAILS PAGE

### Page: Catalog/Details.aspx

**Route**: `/Catalog/Details/{id}`
**Master Page**: Site.Master
**Title**: "Details"

### Layout

```
┌─────────────────────────────────────────────┐
│ Details                                     │
├─────────────────────────────────────────────┤
│ [Product Image]  │ Name:       <value>      │
│                  │                          │
│                  │ Description:<value>      │
│                  │                          │
│                  │ Brand:      <value>      │
│                  │                          │
│                  │ Type:       <value>      │
│                  │                          │
│                  │ Price:      <value>      │
│                  │                          │
│                  │ Picture:    <value>      │
│                  │                          │
│                  │ Stock:      <value>      │
│                  │                          │
│                  │ Restock:    <value>      │
│                  │                          │
│                  │ Max stock:  <value>      │
│                  │                          │
│                  │ [[ Edit ]] [[ Back to List ]] │
└─────────────────────────────────────────────┘
```

### Key Characteristics

- **Read-only**: All fields displayed as labels/text, no form controls
- **Image**: Product image displayed on left (same as Edit page)
- **Layout**: Similar to Edit page but without input controls
- **Data Binding**: Uses label controls or literals to display values

### Actions

#### Edit Button
- **CSS Classes**: `btn esh-button esh-button-primary`
- **Text**: "[ Edit ]"
- **Action**: Navigate to `/Catalog/Edit/{id}`

#### Back to List Link
- **CSS Classes**: `btn esh-button esh-button-secondary`
- **Text**: "[ Back to List ]"
- **Action**: Navigate to catalog list page (/)

---

## 4. DELETE PAGE

### Page: Catalog/Delete.aspx

**Route**: `/Catalog/Delete/{id}`
**Master Page**: Site.Master
**Title**: "Delete"

### Layout

```
┌─────────────────────────────────────────────┐
│ Delete                                      │
├─────────────────────────────────────────────┤
│ Are you sure you want to delete this?      │
│                                             │
│ [Product Image]  │ Name:       <value>      │
│                  │ Description:<value>      │
│                  │ Brand:      <value>      │
│                  │ Type:       <value>      │
│                  │ Price:      <value>      │
│                  │ Picture:    <value>      │
│                  │ Stock:      <value>      │
│                  │ Restock:    <value>      │
│                  │ Max stock:  <value>      │
│                  │                          │
│                  │ [[ Delete ]] [[ Back to List ]] │
└─────────────────────────────────────────────┘
```

### Key Characteristics

- **Confirmation Message**: "Are you sure you want to delete this?"
- **Read-only Display**: All product details shown (same as Details page)
- **Warning Styling**: May use warning colors (CSS dependent)

### Actions

#### Delete Button
- **CSS Classes**: `btn esh-button esh-button-primary` (or `esh-button-danger`)
- **Text**: "[ Delete ]"
- **OnClick Event**: `Delete_Click`
- **Action**: Permanently delete product from database

#### Back to List Link
- **CSS Classes**: `btn esh-button esh-button-secondary`
- **Text**: "[ Back to List ]"
- **Action**: Navigate to catalog list without deleting

### Code-Behind Logic (Delete.aspx.cs)

#### Delete_Click Event
```csharp
protected void Delete_Click(object sender, EventArgs e)
{
    var productId = Convert.ToInt32(RouteData.Values["id"]);
    var product = CatalogService.FindCatalogItem(productId);

    if (product != null)
    {
        CatalogService.RemoveCatalogItem(product);
    }

    Response.Redirect("~");
}
```

### User Interactions

1. **Navigate to Delete page**
   - Click "Delete" link from catalog list
   - Page loads with product details and confirmation message

2. **Confirm deletion**
   - Review product details
   - Click Delete button
   - Product removed from database
   - Redirect to catalog list

3. **Cancel deletion**
   - Click Back to List link
   - Return to catalog list without deleting

---

## Styling Classes (Common Across All Pages)

| Class | Applied To | Purpose |
|-------|------------|---------|
| `esh-body-title` | H2 heading | Page title styling |
| `form-horizontal` | Div | Bootstrap horizontal form layout |
| `form-group` | Div | Bootstrap form group wrapper |
| `control-label` | Label | Form label styling |
| `col-md-2`, `col-md-3`, `col-md-4`, `col-md-8` | Div | Bootstrap grid columns |
| `form-control` | TextBox, DropDownList | Bootstrap form control styling |
| `text-danger` | Validator | Red error text |
| `field-validation-valid` | Validator | Validation message styling |
| `esh-form-information` | Div | Informational message styling |
| `esh-button` | Button, Link | Button base styling |
| `esh-button-primary` | Button, Link | Primary action button (blue) |
| `esh-button-secondary` | Link | Secondary action button (gray) |
| `esh-button-actions` | Div | Button container (right-aligned) |
| `esh-picture` | Image | Product image styling (Edit/Details/Delete) |

---

## Validation Rules (All Forms)

### Client-Side Validators (ASP.NET)

1. **RequiredFieldValidator**
   - Field: Name
   - Display: Dynamic
   - CSS: `field-validation-valid text-danger`

2. **RangeValidator** (Price)
   - Type: Currency
   - Min: 0, Max: 1,000,000
   - Display: Dynamic
   - CSS: `text-danger`

3. **RangeValidator** (Stock, Restock, Max Stock)
   - Type: Integer
   - Min: 0, Max: 10,000,000
   - Display: Dynamic
   - CSS: `text-danger`

### Server-Side Validation

- `ModelState.IsValid` check before save
- If invalid, form redisplays with error messages
- If valid, proceed with database operation

---

## Migration Notes for React

### Component Structure

```
CatalogCRUD/
├── CatalogCreatePage.tsx
├── CatalogEditPage.tsx
├── CatalogDetailsPage.tsx
├── CatalogDeletePage.tsx
├── components/
│   ├── CatalogForm.tsx (shared by Create/Edit)
│   ├── FormField.tsx
│   ├── FormDropdown.tsx
│   ├── ProductImageDisplay.tsx
│   ├── ProductDetailsReadOnly.tsx
│   └── FormActions.tsx (Cancel/Submit buttons)
```

### Shared CatalogForm Component

- **Used by**: Create and Edit pages
- **Props**:
  - `initialValues` (for Edit) or `undefined` (for Create)
  - `onSubmit` callback
  - `onCancel` callback
  - `mode`: 'create' | 'edit'
- **Features**:
  - Zod schema validation (matching Pydantic)
  - React Hook Form for form state
  - Inline error display
  - Dropdown population from API

### Validation with Zod

```typescript
const catalogItemSchema = z.object({
  name: z.string().min(1, "The Name field is required."),
  description: z.string().optional(),
  catalogBrandId: z.number(),
  catalogTypeId: z.number(),
  price: z.number()
    .min(0, "The Price must be positive.")
    .max(1000000, "The Price must be between 0 and 1 million.")
    .refine(val => /^\d+(\.\d{0,2})?$/.test(val.toString()),
      "The Price must have maximum two decimals."),
  availableStock: z.number()
    .int()
    .min(0, "The field Stock must be between 0 and 10 million.")
    .max(10000000),
  restockThreshold: z.number()
    .int()
    .min(0)
    .max(10000000),
  maxStockThreshold: z.number()
    .int()
    .min(0)
    .max(10000000),
});
```

### React Router Routes

- `/catalog/create` → `<CatalogCreatePage />`
- `/catalog/edit/:id` → `<CatalogEditPage />`
- `/catalog/details/:id` → `<CatalogDetailsPage />`
- `/catalog/delete/:id` → `<CatalogDeletePage />`

### TanStack Query Hooks

```typescript
// Fetch single item (Edit, Details, Delete)
useCatalogItem(id: number)

// Fetch brands for dropdown
useCatalogBrands()

// Fetch types for dropdown
useCatalogTypes()

// Create mutation
useCreateCatalogItem() → POST /api/catalog/items

// Update mutation
useUpdateCatalogItem() → PUT /api/catalog/items/{id}

// Delete mutation
useDeleteCatalogItem() → DELETE /api/catalog/items/{id}
```

### Form State Management

- **React Hook Form** for form state and validation
- **Zod resolver** for schema validation
- **TanStack Query** for server data (dropdowns, pre-filled values)
- **React Router** `useNavigate` for redirects after save/cancel

### Image Display (Edit, Details, Delete)

```tsx
<ProductImageDisplay
  pictureFileName={product.pictureFileName}
  altText={product.name}
  className="col-md-6 esh-picture"
/>

// Renders:
<img src={`/pics/${pictureFileName}`} alt={altText} />
```

---

## Test Scenarios (UI Behavior)

### Create Page

1. **Load create page**
   - Verify all form fields render
   - Verify Brand/Type dropdowns populate
   - Verify default values (Price: 0.00, Stock fields: 0)

2. **Submit empty form**
   - Click Create without filling fields
   - Verify "Name required" error displays

3. **Submit with invalid price**
   - Enter price: "abc", "-5", "999.999"
   - Verify price validation error

4. **Submit with invalid stock**
   - Enter stock: "20000000" (exceeds max)
   - Verify stock validation error

5. **Successful create**
   - Fill all required fields with valid data
   - Click Create
   - Verify redirects to catalog list
   - Verify new product appears in list

6. **Cancel create**
   - Fill form partially
   - Click Cancel
   - Verify navigates to catalog list without saving

### Edit Page

1. **Load edit page**
   - Navigate to /catalog/edit/1
   - Verify form pre-populated with product data
   - Verify product image displays
   - Verify dropdowns show current selections

2. **Edit and save**
   - Change Name and Price
   - Click Save
   - Verify redirects to catalog list
   - Verify changes persisted

3. **Picture filename read-only**
   - Verify PictureFileName field is disabled/readonly
   - Verify cannot edit value

4. **Cancel edit**
   - Modify fields
   - Click Cancel
   - Verify navigates back without saving

### Details Page

1. **View details**
   - Navigate to /catalog/details/1
   - Verify all fields display as read-only text
   - Verify product image displays

2. **Navigate to Edit**
   - Click Edit button
   - Verify navigates to /catalog/edit/1

3. **Back to List**
   - Click Back to List
   - Verify navigates to catalog list

### Delete Page

1. **Load delete confirmation**
   - Navigate to /catalog/delete/1
   - Verify confirmation message displays
   - Verify product details display
   - Verify product image displays

2. **Confirm delete**
   - Click Delete button
   - Verify redirects to catalog list
   - Verify product no longer in list
   - Verify product removed from database

3. **Cancel delete**
   - Click Back to List
   - Verify navigates to catalog list
   - Verify product still exists

4. **Delete non-existent product**
   - Navigate to /catalog/delete/99999
   - Verify 404 or "Not Found" error
