# UI Inventory (Pre-Discovery): catalog-management

> Source: ASPX/WebForms inventory. Business behavior is refined by `docs/seams/catalog-management/discovery.md`.

## Layout & Chrome Elements

**CRITICAL**: Document ALL layout elements that frame the content (headers, footers, navigation, sidebars).

| Element | Type | Content | Location | Confidence |
|---------|------|---------|----------|------------|
| Header | Navbar | Brand logo + Login status/controls | Top | high |
| Hero Section | Banner | "Catalog Manager (WebForms)" title | Below header | high |
| MainContent | ContentPlaceHolder | Page-specific content area | Body | high |
| Footer | Footer | Brand logo + footer text + session info | Bottom | high |

### Header Navigation Details
- **Brand logo**: Image at `/images/brand.png`, links to home page (`~/`)
- **Authentication UI**:
  - Anonymous users: "Sign in" link (triggers OpenID Connect authentication)
  - Authenticated users: "Hello, [username]!" + "Sign out" link
  - Authentication state managed via ASP.NET OWIN middleware

### Hero Banner
- Title: "Catalog Manager"
- Subtitle: "(WebForms)"
- Full-width container with custom styling (`.esh-app-hero`)

### Footer Elements
- Brand logo (dark variant): `/images/brand_dark.png`
- Footer text image: `/images/main_footer_text.png`
- Session info label (dynamic, server-rendered)

---

## Screens

### Default.aspx (Product List Page)

**Framework:** ASP.NET WebForms
**File:** `src/eShopModernizedWebForms/Default.aspx`
**Code-behind:** `src/eShopModernizedWebForms/Default.aspx.cs`
**Route:** `/` (home page) and `/products/{index}/{size}` (pagination)
**Title:** "Home Page"
**Authentication Required:** No

#### Controls

| Name | Type | Text/Label | Confidence |
|------|------|------------|------------|
| CatalogList | ContentPlaceHolder | (content area) | high |
| productList | ListView | Product listing grid | high |
| Create New Button | HyperLink (styled as button) | "Create New" | high |
| PaginationPrevious | HyperLink | "Previous" | high |
| PaginationNext | HyperLink | "Next" | high |

#### Data Grid / Table

- **Library:** ASP.NET ListView control (server-side rendering)
- **Data Source:** `PaginatedItemsViewModel<CatalogItem>` (server-side)
- **Pagination:** Server-side, controlled via route parameters (`index`, `size`)
- **Default page size:** 10 items
- **Default page index:** 0

**Columns:**

| Column | Header | Data Binding | Display Format | Confidence |
|--------|--------|--------------|----------------|------------|
| 1 | (no header) | `Item.PictureUri` | Thumbnail image | high |
| 2 | Name | `Item.Name` | Text | high |
| 3 | Description | `Item.Description` | Text | high |
| 4 | Brand | `Item.CatalogBrand.Brand` | Text (navigation property) | high |
| 5 | Type | `Item.CatalogType.Type` | Text (navigation property) | high |
| 6 | Price | `Item.Price` | Currency (styled with `.esh-price`) | high |
| 7 | Picture name | `Item.PictureFileName` | Text | high |
| 8 | Stock | `Item.AvailableStock` | Integer | high |
| 9 | Restock | `Item.RestockThreshold` | Integer | high |
| 10 | Max stock | `Item.MaxStockThreshold` | Integer | high |
| 11 | (Actions) | (links) | "Edit \| Details \| Delete" links | high |

#### Actions (wired events)

| Control | Event | Handler | Notes (UI-only) | Confidence |
|---------|-------|---------|-----------------|------------|
| Create New Button | Click (navigation) | Route: `CreateProductRoute` | Navigates to Create.aspx | high |
| Edit Link (per row) | Click (navigation) | Route: `EditProductRoute` with `{id}` | Navigates to Edit.aspx | high |
| Details Link (per row) | Click (navigation) | Route: `ProductDetailsRoute` with `{id}` | Navigates to Details.aspx | high |
| Delete Link (per row) | Click (navigation) | Route: `DeleteProductRoute` with `{id}` | Navigates to Delete.aspx | high |
| PaginationPrevious | Click (navigation) | Route: `ProductsByPageRoute` with `{index-1, size}` | Hidden if on first page | high |
| PaginationNext | Click (navigation) | Route: `ProductsByPageRoute` with `{index+1, size}` | Hidden if on last page | high |

#### Pagination Display

- **Format:** "Showing {ItemsPerPage} of {TotalItems} products - Page {ActualPage + 1} - {TotalPages}"
- **Visibility Rules:**
  - "Previous" link hidden with class `esh-pager-item--hidden` when `ActualPage == 0`
  - "Next" link hidden with class `esh-pager-item--hidden` when `ActualPage >= TotalPages - 1`

#### Page Load Logic (Code-behind)

- If route contains `size` and `index` parameters → load paginated results
- Else → load default page (size=10, index=0)
- Image URIs built dynamically via `ImageService.BuildUrlImage(catalogItem)`

#### Empty State

- EmptyDataTemplate: "No data was returned." (table row)

---

### Details.aspx (Product Details Page)

**Framework:** ASP.NET WebForms
**File:** `src/eShopModernizedWebForms/Catalog/Details.aspx`
**Code-behind:** `src/eShopModernizedWebForms/Catalog/Details.aspx.cs`
**Route:** `/Catalog/Details/{id}`
**Title:** "Details"
**Authentication Required:** No

#### Layout Structure

- **Two-column layout:**
  - Left column (col-md-4): Product image
  - Middle column (col-md-4): Name, Description, Brand, Type, Price
  - Right column (col-md-4): Picture name, Stock, Restock, Max stock, Action buttons

#### Controls

| Name | Type | Text/Label | Data Binding | Confidence |
|------|------|------------|--------------|------------|
| Product Image | asp:Image | (image) | `/Pics/{product.PictureFileName}` | high |
| Name Label | asp:Label | "Name" (dt) | `product.Name` | high |
| Description Label | asp:Label | "Description" (dt) | `product.Description` | high |
| Brand Label | asp:Label | "Brand" (dt) | `product.CatalogBrand.Brand` | high |
| Type Label | asp:Label | "Type" (dt) | `product.CatalogType.Type` | high |
| Price Label | asp:Label | "Price" (dt) | `product.Price` (styled `.esh-price`) | high |
| Picture Name Label | asp:Label | "Picture name" (dt) | `product.PictureFileName` | high |
| Stock Label | asp:Label | "Stock" (dt) | `product.AvailableStock` | high |
| Restock Label | asp:Label | "Restock" (dt) | `product.RestockThreshold` | high |
| Max Stock Label | asp:Label | "Max stock" (dt) | `product.MaxStockThreshold` | high |
| Back to List Button | HyperLink (styled as button) | "[ Back to list ]" | Routes to `~/` | high |
| Edit Button | HyperLink (styled as button) | "[ Edit ]" | Route: `EditProductRoute` with `{id}` | high |

#### Actions (wired events)

| Control | Event | Handler | Notes (UI-only) | Confidence |
|---------|-------|---------|-----------------|------------|
| Back to List Button | Click (navigation) | Route: `~/` | Returns to product list | high |
| Edit Button | Click (navigation) | Route: `EditProductRoute` with `{id}` | Navigates to Edit.aspx | high |

#### Page Load Logic (Code-behind)

- Extract `id` from route data (`Page.RouteData.Values["id"]`)
- Load `CatalogItem` via `CatalogService.FindCatalogItem(productId)`
- Bind to page controls via `this.DataBind()`

---

### Create.aspx (Create Product Page)

**Framework:** ASP.NET WebForms
**File:** `src/eShopModernizedWebForms/Catalog/Create.aspx`
**Code-behind:** `src/eShopModernizedWebForms/Catalog/Create.aspx.cs`
**Route:** `/Catalog/Create`
**Title:** "Create"
**Authentication Required:** Yes (OpenID Connect)
**ValidateRequest:** false (to allow file uploads)

#### Layout Structure

- **Two-column layout:**
  - Left column (col-md-4): Image preview + Upload button
  - Right column (col-md-8): Form fields

#### Controls

| Name | Type | Text/Label | Default Value | Validation | Confidence |
|------|------|------------|---------------|------------|------------|
| Product Image Preview | asp:Image | (preview) | Default image from `ImageService.UrlDefaultImage()` | N/A | high |
| Upload Image Button | file input (HTML5) | "Upload image" | N/A | Accepts `image/*` | high |
| TempImageName | asp:HiddenField | (hidden) | Empty string | N/A | high |
| Name | asp:TextBox | "Name" | Empty | RequiredFieldValidator | high |
| Description | asp:TextBox | "Description" | Empty | None | high |
| Brand | asp:DropDownList | "Brand" | (dropdown) | None | high |
| Type | asp:DropDownList | "Type" | (dropdown) | None | high |
| Price | asp:TextBox | "Price" | "0.00" | RangeValidator (0 to 1,000,000, Currency) | high |
| Stock | asp:TextBox | "Stock" | "0" | RangeValidator (0 to 10,000,000, Integer) | high |
| Restock | asp:TextBox | "Restock" | "0" | RangeValidator (0 to 10,000,000, Integer) | high |
| Maxstock | asp:TextBox | "Max stock" | "0" | RangeValidator (0 to 10,000,000, Integer) | high |
| Cancel Button | HyperLink (styled as button) | "[ Cancel ]" | N/A | N/A | high |
| Create Button | asp:Button | "[ Create ]" | N/A | Triggers server postback | high |

#### Dropdowns / Select Lists

**Brand Dropdown:**
- **Data Source:** `GetBrands()` method (returns `IEnumerable<CatalogBrand>`)
- **ItemType:** `eShopModernizedWebForms.Models.CatalogBrand`
- **DataTextField:** `Brand`
- **DataValueField:** `Id`

**Type Dropdown:**
- **Data Source:** `GetTypes()` method (returns `IEnumerable<CatalogType>`)
- **ItemType:** `eShopModernizedWebForms.Models.CatalogType`
- **DataTextField:** `Type`
- **DataValueField:** `Id`

#### Validation Rules

| Field | Validator Type | Rule | Error Message | Confidence |
|-------|---------------|------|---------------|------------|
| Name | RequiredFieldValidator | Cannot be empty | "The Name field is required." | high |
| Price | RangeValidator | 0 to 1,000,000 (Currency) | "The Price must be a positive number with maximum two decimals between 0 and 1 million." | high |
| Stock | RangeValidator | 0 to 10,000,000 (Integer) | "The field Stock must be between 0 and 10 million." | high |
| Restock | RangeValidator | 0 to 10,000,000 (Integer) | "The field Restock must be between 0 and 10 million." | high |
| Maxstock | RangeValidator | 0 to 10,000,000 (Integer) | "The field Max stock must be between 0 and 10 million." | high |

#### Image Upload Flow (Client-side + AJAX)

1. User selects image file via `<input type="file" id="uploadEditorImage">`
2. JavaScript (not in provided files, but referenced) uploads image via AJAX to `/Catalog/PicUploader.asmx`
3. Server validates image format (JPEG, PNG, GIF) and size
4. Server uploads to temporary storage via `ImageService.UploadTempImage()`
5. Server returns temp image URL and name as JSON
6. JavaScript updates `TempImageName` hidden field and preview image
7. On form submit, temp image name is included in POST data

**Upload Button Visibility:**
- Hidden if `CatalogConfiguration.UseAzureStorage == false` (controlled server-side)

#### Actions (wired events)

| Control | Event | Handler | Notes (UI-only) | Confidence |
|---------|-------|---------|-----------------|------------|
| Upload Image Button | Change (file input) | JavaScript → AJAX call to `PicUploader.asmx` | Client-side, updates preview | medium |
| Cancel Button | Click (navigation) | Route: `~/` | Returns to product list | high |
| Create Button | Click (postback) | `Create_Click` server event | Server-side validation, then creates product | high |

#### Page Load Logic (Code-behind)

- Check authentication: If not authenticated, trigger OpenID Connect sign-in
- Check Azure Storage config: If disabled, hide upload button
- Set default image preview via `ImageService.UrlDefaultImage()`
- Bind data to page

#### Create Button Logic (Code-behind)

1. Validate `ModelState.IsValid`
2. Construct `CatalogItem` from form fields
3. If `TempImageName` has value → extract filename, set `PictureFileName`
4. Call `CatalogService.CreateCatalogItem(catalogItem)`
5. If temp image exists → call `ImageService.UpdateImage(catalogItem)` (moves temp to permanent storage)
6. Redirect to `~/` (product list)

---

### Edit.aspx (Edit Product Page)

**Framework:** ASP.NET WebForms
**File:** `src/eShopModernizedWebForms/Catalog/Edit.aspx`
**Code-behind:** `src/eShopModernizedWebForms/Catalog/Edit.aspx.cs`
**Route:** `/Catalog/Edit/{id}`
**Title:** "Edit"
**Authentication Required:** Yes (OpenID Connect)
**ValidateRequest:** false (to allow file uploads)

#### Layout Structure

- **Two-column layout:**
  - Left column (col-md-4): Current product image + Upload button
  - Right column (col-md-8): Form fields (pre-populated with product data)

#### Controls

| Name | Type | Text/Label | Data Binding | Validation | Confidence |
|------|------|------------|--------------|------------|------------|
| Product Image | asp:Image | (image) | `/Pics/{product.PictureFileName}` | N/A | high |
| Upload Image Button | file input (HTML5) | "Upload image" | N/A | Accepts `image/*` | high |
| TempImageName | asp:HiddenField | (hidden) | Empty string | N/A | high |
| Name | asp:TextBox | "Name" | `product.Name` | RequiredFieldValidator | high |
| Description | asp:TextBox | "Description" | `product.Description` | None | high |
| BrandDropDownList | asp:DropDownList | "Brand" | `product.CatalogBrandId` (selected) | None | high |
| TypeDropDownList | asp:DropDownList | "Type" | `product.CatalogTypeId` (selected) | None | high |
| Price | asp:TextBox | "Price" | `product.Price` | RangeValidator (0 to 1,000,000, Currency) | high |
| PictureFileName | asp:TextBox | "Picture name" | `product.PictureFileName` | None (read-only) | high |
| Stock | asp:TextBox | "Stock" | `product.AvailableStock` | RangeValidator (0 to 10,000,000, Integer) | high |
| Restock | asp:TextBox | "Restock" | `product.RestockThreshold` | RangeValidator (0 to 10,000,000, Integer) | high |
| Maxstock | asp:TextBox | "Max stock" | `product.MaxStockThreshold` | RangeValidator (0 to 10,000,000, Integer) | high |
| Cancel Button | HyperLink (styled as button) | "[ Cancel ]" | Route: `~/` | N/A | high |
| Save Button | asp:Button | "[ Save ]" | N/A | Triggers server postback | high |

#### Dropdowns / Select Lists

**Brand Dropdown:**
- **Data Source:** `CatalogService.GetCatalogBrands()` (loaded in `Page_Load`)
- **Selected Value:** Set to `product.CatalogBrandId.ToString()`

**Type Dropdown:**
- **Data Source:** `CatalogService.GetCatalogTypes()` (loaded in `Page_Load`)
- **Selected Value:** Set to `product.CatalogTypeId.ToString()`

#### Validation Rules

(Same as Create.aspx — see above)

#### Read-Only Fields

- **PictureFileName:** Read-only (`ReadOnly="true"`), with tooltip "Not allowed for edition"
- User can upload new image, but cannot directly edit filename field

#### Image Upload Flow

(Same as Create.aspx — AJAX upload to `PicUploader.asmx`)

#### Actions (wired events)

| Control | Event | Handler | Notes (UI-only) | Confidence |
|---------|-------|---------|-----------------|------------|
| Upload Image Button | Change (file input) | JavaScript → AJAX call to `PicUploader.asmx` | Client-side, updates preview | medium |
| Cancel Button | Click (navigation) | Route: `~/` | Returns to product list | high |
| Save Button | Click (postback) | `Save_Click` server event | Server-side validation, then updates product | high |

#### Page Load Logic (Code-behind)

- Check authentication: If not authenticated, trigger OpenID Connect sign-in
- Check Azure Storage config: If disabled, hide upload button
- **Only on first load (not postback):**
  - Extract `id` from route data
  - Load `CatalogItem` via `CatalogService.FindCatalogItem(productId)`
  - Load brands and types into dropdowns
  - Set dropdown selected values to match product
  - Bind data to page

#### Save Button Logic (Code-behind)

1. Validate `ModelState.IsValid`
2. Construct `CatalogItem` from form fields (including product `Id` from route)
3. If `TempImageName` has value:
   - Call `ImageService.UpdateImage(catalogItem)` (moves temp to permanent)
   - Extract filename, set `PictureFileName`
4. Call `CatalogService.UpdateCatalogItem(catalogItem)`
5. Redirect to `~/` (product list)

---

### Delete.aspx (Delete Confirmation Page)

**Framework:** ASP.NET WebForms
**File:** `src/eShopModernizedWebForms/Catalog/Delete.aspx`
**Code-behind:** `src/eShopModernizedWebForms/Catalog/Delete.aspx.cs`
**Route:** `/Catalog/Delete/{id}`
**Title:** "Delete"
**Authentication Required:** Yes (OpenID Connect)

#### Layout Structure

- **Confirmation message:** "Are you sure you want to delete this?"
- **Three-column layout (same as Details.aspx):**
  - Left column (col-md-4): Product image
  - Middle column (col-md-4): Name, Description, Brand, Type, Price
  - Right column (col-md-4): Picture name, Stock, Restock, Max stock, Action buttons

#### Controls

(Same display fields as Details.aspx, but with variable name `productToDelete` instead of `product`)

| Name | Type | Text/Label | Data Binding | Confidence |
|------|------|------------|--------------|------------|
| Product Image | asp:Image | (image) | `/Pics/{productToDelete.PictureFileName}` | high |
| Name Label | asp:Label | "Name" (dt) | `productToDelete.Name` | high |
| Description Label | asp:Label | "Description" (dt) | `productToDelete.Description` | high |
| Brand Label | asp:Label | "Brand" (dt) | `productToDelete.CatalogBrand.Brand` | high |
| Type Label | asp:Label | "Type" (dt) | `productToDelete.CatalogType.Type` | high |
| Price Label | asp:Label | "Price" (dt) | `productToDelete.Price` | high |
| Picture Name Label | asp:Label | "Picture name" (dt) | `productToDelete.PictureFileName` | high |
| Stock Label | asp:Label | "Stock" (dt) | `productToDelete.AvailableStock` | high |
| Restock Label | asp:Label | "Restock" (dt) | `productToDelete.RestockThreshold` | high |
| Max Stock Label | asp:Label | "Max stock" (dt) | `productToDelete.MaxStockThreshold` | high |
| Cancel Button | HyperLink (styled as button) | "[ Cancel ]" | Route: `~/` | high |
| Delete Button | asp:Button | "[ Delete ]" | Triggers server postback | high |

#### Actions (wired events)

| Control | Event | Handler | Notes (UI-only) | Confidence |
|---------|-------|---------|-----------------|------------|
| Cancel Button | Click (navigation) | Route: `~/` | Returns to product list without deleting | high |
| Delete Button | Click (postback) | `Delete_Click` server event | Calls delete service, then redirects | high |

#### Page Load Logic (Code-behind)

- Check authentication: If not authenticated, trigger OpenID Connect sign-in
- Extract `id` from route data
- Load `CatalogItem` via `CatalogService.FindCatalogItem(productId)`
- Bind to page controls

#### Delete Button Logic (Code-behind)

1. Call `CatalogService.RemoveCatalogItem(productToDelete)`
2. Redirect to `~/` (product list)

**Note:** No validation or confirmation dialog beyond the page itself.

---

### PicUploader.asmx (Image Upload Web Service)

**Framework:** ASP.NET Web Service (ASMX) with ScriptService
**File:** `src/eShopModernizedWebForms/Catalog/PicUploader.asmx.cs`
**Route:** `/Catalog/PicUploader.asmx`
**Method:** `UploadImage` (WebMethod)
**Authentication Required:** No (security gap — must add in modern API)
**HTTP Method:** POST (AJAX call)

#### Request Format

- **Content-Type:** `multipart/form-data`
- **Form Fields:**
  - `HelpSectionImages`: Image file (HttpPostedFile)
  - `itemId`: Catalog item ID (optional, for logging/context)

#### Response Format (Success)

- **Content-Type:** `application/json`
- **Body:**
  ```json
  {
    "name": "/temp/{filename}",
    "url": "https://storage.example.com/temp/{filename}"
  }
  ```

#### Response Format (Error)

- **HTTP Status:** 400 Bad Request
- **Status Description:** "image is not valid"

#### Validation Logic

- Checks if file is a valid image (JPEG, PNG, GIF)
- Uses `Image.FromStream()` to validate image format
- Returns 400 if validation fails

#### Server-Side Logic

1. Resolve `IImageService` from Autofac container
2. Extract image file and item ID from request
3. Validate image format
4. Call `ImageService.UploadTempImage(image, catalogItemId)`
5. Return JSON with temp image URL and path

---

## Static Assets

| Asset | Type | Path | Usage | Confidence |
|-------|------|------|-------|------------|
| Brand Logo | Image (PNG) | `/images/brand.png` | Header navigation | high |
| Brand Logo (Dark) | Image (PNG) | `/images/brand_dark.png` | Footer | high |
| Footer Text | Image (PNG) | `/images/main_footer_text.png` | Footer | high |
| Favicon | Icon (ICO) | `/favicon.ico` | Browser tab icon | high |
| Product Images | Images (JPEG/PNG/GIF) | `/Pics/{filename}` | Product thumbnails and details | high |
| Default Product Image | Image (PNG) | `dummy.png` | Placeholder for products without images | high |

**Product Image Handling:**
- Images stored in `/Pics/` directory (local) or Azure Blob Storage
- Image URIs dynamically generated via `ImageService.BuildUrlImage()`
- Default image (`dummy.png`) used when no image uploaded
- Supported formats: JPEG, PNG, GIF (validated in `PicUploader.asmx`)

---

## Unknowns / Runtime-built UI

### Dynamic Pagination Links
- Pagination URLs are constructed server-side using `GetRouteUrl()` with route parameters
- CSS classes for hiding pagination links (`esh-pager-item--hidden`) are conditionally added in code-behind

### Image Upload JavaScript
- AJAX upload logic is referenced but not included in ASPX files
- Likely in separate JavaScript file (not analyzed in this inventory)
- Interacts with `uploadEditorImage` file input and updates `TempImageName` hidden field

### Client-Side Validation
- ASP.NET WebForms validators (RequiredFieldValidator, RangeValidator) generate client-side JavaScript
- Validation scripts loaded via `asp:ScriptManager` in Site.Master
- Specific validation behavior not explicitly coded in ASPX files (auto-generated)

### Authentication Flow
- OpenID Connect authentication triggered via OWIN middleware
- Redirect URIs and challenge logic handled server-side
- User identity display in header (`Context.User.Identity.Name`) is server-rendered

---

## Navigation Map

### Routes (ASP.NET Routing)

| Route Name | Pattern | Page | HTTP Methods | Auth Required |
|------------|---------|------|--------------|---------------|
| (Default) | `/` | Default.aspx | GET | No |
| ProductsByPageRoute | `/products/{index}/{size}` | Default.aspx | GET | No |
| ProductDetailsRoute | `/Catalog/Details/{id}` | Details.aspx | GET | No |
| CreateProductRoute | `/Catalog/Create` | Create.aspx | GET, POST | Yes |
| EditProductRoute | `/Catalog/Edit/{id}` | Edit.aspx | GET, POST | Yes |
| DeleteProductRoute | `/Catalog/Delete/{id}` | Delete.aspx | GET, POST | Yes |

### Navigation Flow

```
Default.aspx (Product List)
  ├─> Create.aspx (via "Create New" button)
  │     └─> Default.aspx (after successful create or cancel)
  │
  ├─> Details.aspx (via "Details" link per product)
  │     ├─> Edit.aspx (via "Edit" button)
  │     └─> Default.aspx (via "Back to list" button)
  │
  ├─> Edit.aspx (via "Edit" link per product)
  │     └─> Default.aspx (after save or cancel)
  │
  └─> Delete.aspx (via "Delete" link per product)
        └─> Default.aspx (after delete or cancel)
```

### AJAX Endpoints

| Endpoint | Purpose | Called From |
|----------|---------|-------------|
| `/Catalog/PicUploader.asmx` | Image upload (temp storage) | Create.aspx, Edit.aspx (JavaScript) |

---

## Interaction Patterns

### Server-Side Postbacks (WebForms Pattern)

All form submissions use ASP.NET postback mechanism:
1. User clicks button (e.g., "Create", "Save", "Delete")
2. Form posts to same page URL
3. Server-side event handler executes (e.g., `Create_Click`, `Save_Click`)
4. Server validates and processes
5. Server redirects to target page (typically `~/` for product list)

**Modern equivalent:** Replace with React forms + REST API calls (POST/PUT/DELETE)

### AJAX Image Upload

1. User selects image file
2. JavaScript captures file input change event
3. AJAX POST to `/Catalog/PicUploader.asmx`
4. Server validates and uploads to temp storage
5. Server returns JSON with temp URL
6. JavaScript updates image preview and hidden field
7. On form submit, temp image path included in postback data
8. Server moves temp image to permanent storage

**Modern equivalent:** Replace with React file upload component + REST API (`POST /api/catalog/images`)

### Data Binding (Server-Side)

- All data binding uses ASP.NET data binding expressions: `<%#: Item.Property %>`
- ListView control uses `ItemType` for strongly-typed binding
- Labels use `Text='<%# product.Property %>'` for server-side binding
- All binding happens on server during `Page_Load` and `DataBind()` calls

**Modern equivalent:** Replace with React state management and TanStack Query

---

## CSS Classes / Styling Patterns

### Custom eShop Styles

| Class | Usage | Element Type |
|-------|-------|--------------|
| `.esh-table` | Table container | div |
| `.esh-table-header` | Table header row | tr |
| `.esh-table-link` | Action links in table | a |
| `.esh-thumbnail` | Product thumbnail image | img |
| `.esh-price` | Price display | span |
| `.esh-button` | Button base class | a, button |
| `.esh-button-primary` | Primary action button | a, button |
| `.esh-button-secondary` | Secondary action button | a, button |
| `.esh-button-upload` | Upload button | label |
| `.esh-button-actions` | Button container | div |
| `.esh-link-wrapper` | Link container | p |
| `.esh-pager` | Pagination container | div |
| `.esh-pager-wrapper` | Pagination inner wrapper | article |
| `.esh-pager-item` | Pagination item | a, span |
| `.esh-pager-item--navigable` | Clickable pagination item | a |
| `.esh-pager-item--hidden` | Hidden pagination item | a |
| `.esh-picture` | Full product image | img |
| `.esh-loader` | Loading spinner | div |
| `.esh-app-hero` | Hero banner section | section |
| `.esh-header` | Header container | div |
| `.esh-header-title` | Header title | h1 |
| `.esh-header-brand` | Header brand area | div |
| `.esh-login-link` | Login/logout link | a |
| `.esh-app-footer` | Footer section | footer |
| `.esh-app-footer-brand` | Footer brand image | img |
| `.esh-app-footer-text` | Footer text image | img |
| `.esh-body-title` | Page title | h2 |

### Bootstrap Classes (Inherited)

- Grid: `.container`, `.row`, `.col-md-*`
- Forms: `.form-horizontal`, `.form-group`, `.control-label`, `.form-control`
- Buttons: `.btn`, `.btn-default`
- Visibility: `.hidden`, `.hidden-xs`
- Text: `.text-danger`, `.text-right`
- Navigation: `.navbar`, `.navbar-nav`, `.navbar-right`, `.navbar-text`
- Tables: `.table`, `.dl-horizontal`

---

## Form Validation Summary

### Client-Side Validators (ASP.NET WebForms)

| Page | Field | Validator | Rule | Display |
|------|-------|-----------|------|---------|
| Create.aspx | Name | RequiredFieldValidator | Not empty | Dynamic |
| Create.aspx | Price | RangeValidator | 0-1M, Currency | Dynamic |
| Create.aspx | Stock | RangeValidator | 0-10M, Integer | Dynamic |
| Create.aspx | Restock | RangeValidator | 0-10M, Integer | Dynamic |
| Create.aspx | Maxstock | RangeValidator | 0-10M, Integer | Dynamic |
| Edit.aspx | Name | RequiredFieldValidator | Not empty | Dynamic |
| Edit.aspx | Price | RangeValidator | 0-1M, Currency | Dynamic |
| Edit.aspx | Stock | RangeValidator | 0-10M, Integer | Dynamic |
| Edit.aspx | Restock | RangeValidator | 0-10M, Integer | Dynamic |
| Edit.aspx | Maxstock | RangeValidator | 0-10M, Integer | Dynamic |

### Server-Side Validation

- All pages check `ModelState.IsValid` in event handlers
- Image upload validates format (JPEG, PNG, GIF) and size
- Price must have max 2 decimal places (regex validation in model: `^\d+(\.\d{0,2})*$`)

---

## Authentication & Authorization Patterns

### Authentication

- **Mechanism:** Azure AD OpenID Connect (OWIN middleware)
- **Trigger:** Unauthenticated users redirected to sign-in when accessing protected pages
- **Protected Pages:** Create.aspx, Edit.aspx, Delete.aspx
- **Public Pages:** Default.aspx, Details.aspx

### Authorization

- **Role-based access:** Not implemented (all authenticated users have full access)
- **Item-level permissions:** Not implemented (any authenticated user can edit/delete any product)

**Security note for modern API:**
- Add proper authorization checks (roles, claims)
- Secure image upload endpoint (currently unauthenticated)
- Implement CSRF protection for write operations

---

## Responsive Design Patterns

### Bootstrap Grid

- All pages use Bootstrap grid system (`.container`, `.row`, `.col-md-*`)
- Mobile-specific layout: Site.Mobile.Master (not analyzed in detail)
- ViewSwitcher.ascx allows switching between desktop and mobile views
- Responsive breakpoints: Bootstrap default (xs, sm, md, lg)

### Adaptive Elements

- Footer text image hidden on extra-small screens (`.hidden-xs`)
- Pagination adapts to screen size via Bootstrap responsive utilities

---

## Data Model (UI Perspective)

### CatalogItem Entity

| Property | Type | Display Format | Validation | Notes |
|----------|------|----------------|------------|-------|
| Id | int | Hidden | N/A | Auto-generated (HiLo sequence) |
| Name | string | Text | Required | - |
| Description | string | Text | Optional | - |
| Price | decimal | Currency | 0-1M, 2 decimals max | Styled with `.esh-price` |
| PictureFileName | string | Text | Optional | Read-only on edit |
| PictureUri | string | Image URL | N/A | Computed dynamically |
| CatalogTypeId | int | Dropdown | Required | Foreign key |
| CatalogType | CatalogType | Text (navigation) | N/A | Display `Type` property |
| CatalogBrandId | int | Dropdown | Required | Foreign key |
| CatalogBrand | CatalogBrand | Text (navigation) | N/A | Display `Brand` property |
| AvailableStock | int | Integer | 0-10M | "Stock" label |
| RestockThreshold | int | Integer | 0-10M | "Restock" label |
| MaxStockThreshold | int | Integer | 0-10M | "Max stock" label |
| OnReorder | bool | (not displayed) | N/A | Internal state |
| TempImageName | string | Hidden field | N/A | Used during create/edit |

### Navigation Properties

- **CatalogBrand** → `Id`, `Brand` (string)
- **CatalogType** → `Id`, `Type` (string)

---

## Modern React Equivalents (Migration Guide)

### Screen Mapping

| Legacy Screen | Modern Route | React Component | Key Features |
|---------------|--------------|-----------------|--------------|
| Default.aspx | `/catalog` or `/` | `CatalogListPage` | Data table, pagination, search/filter |
| Details.aspx | `/catalog/{id}` | `CatalogDetailPage` | Detail view, edit/delete actions |
| Create.aspx | `/catalog/create` | `CatalogCreatePage` | Form with image upload |
| Edit.aspx | `/catalog/{id}/edit` | `CatalogEditPage` | Pre-populated form with image upload |
| Delete.aspx | N/A (modal) | `DeleteConfirmationDialog` | Modal dialog on list or detail page |

### Control Mapping

| WebForms Control | React Equivalent | Library/Pattern |
|------------------|------------------|-----------------|
| ListView | Data table component | TanStack Table or shadcn/ui Table |
| TextBox | Input component | shadcn/ui Input |
| DropDownList | Select component | shadcn/ui Select |
| Button | Button component | shadcn/ui Button |
| HyperLink | Link component | React Router Link |
| Image | img element | Standard HTML with lazy loading |
| RequiredFieldValidator | Zod schema validation | React Hook Form + Zod |
| RangeValidator | Zod schema validation | `.min()`, `.max()` |
| HiddenField | React state | `useState()` |

### Postback → API Call Mapping

| Postback Event | Modern API Call | HTTP Method | Endpoint |
|----------------|-----------------|-------------|----------|
| Create_Click | Create product | POST | `/api/catalog` |
| Save_Click | Update product | PUT | `/api/catalog/{id}` |
| Delete_Click | Delete product | DELETE | `/api/catalog/{id}` |
| Upload image | Upload image | POST | `/api/catalog/images` |
| Page_Load (list) | Get products | GET | `/api/catalog?page={page}&size={size}` |
| Page_Load (details) | Get product | GET | `/api/catalog/{id}` |

### State Management

- **Server state (products, types, brands):** TanStack Query
- **Form state:** React Hook Form
- **UI state (modals, loading):** Zustand or React Context
- **Authentication state:** JWT token + React Context

---

## Summary & Coverage

### Screens Extracted: 5

1. Default.aspx (Product List) — Complete
2. Details.aspx (Product Details) — Complete
3. Create.aspx (Create Product) — Complete
4. Edit.aspx (Edit Product) — Complete
5. Delete.aspx (Delete Confirmation) — Complete

### Layout Elements: 4

1. Header (navigation + auth UI)
2. Hero Banner (page title)
3. MainContent (content area)
4. Footer (branding + session info)

### Web Services: 1

1. PicUploader.asmx (Image upload)

### Total Interactive Controls: 70+

- Buttons: 12
- Text inputs: 32
- Dropdowns: 4
- Links: 12+
- Labels: 20+
- Images: 5
- File inputs: 2
- Hidden fields: 2

### Validation Rules: 10

- Required field: 2 instances
- Range validators: 8 instances

### Navigation Routes: 6

- Default/Home
- Paginated products
- Details
- Create
- Edit
- Delete

### Static Assets: 5+

- Brand logos (2)
- Footer images (2)
- Favicon (1)
- Product images (dynamic count)

---

## Next Steps for Frontend Migration Agent

1. **Set up React project structure:**
   - Create pages: `CatalogListPage`, `CatalogDetailPage`, `CatalogCreatePage`, `CatalogEditPage`
   - Create components: `CatalogTable`, `CatalogForm`, `ImageUpload`, `DeleteDialog`

2. **Implement data fetching:**
   - TanStack Query hooks: `useCatalogList`, `useCatalogDetail`, `useCatalogTypes`, `useCatalogBrands`
   - API client functions matching OpenAPI spec

3. **Build forms:**
   - React Hook Form + Zod validation schemas matching legacy validators
   - Image upload component with drag-and-drop support

4. **Implement routing:**
   - React Router v6 routes matching legacy route patterns
   - Protected routes requiring JWT authentication

5. **Style with Tailwind CSS:**
   - Map `.esh-*` classes to Tailwind utilities
   - Use shadcn/ui components for buttons, inputs, tables
   - Ensure responsive design matching Bootstrap grid behavior

6. **Handle authentication:**
   - Replace OpenID Connect with JWT token authentication
   - Implement protected route wrapper
   - Add login/logout UI in header

7. **Asset migration:**
   - Copy brand logos, footer images, favicon to `public/`
   - Set up product image storage (S3-compatible or local)
   - Implement image lazy loading for product thumbnails

8. **Accessibility:**
   - Add ARIA labels to form fields
   - Ensure keyboard navigation for all interactive elements
   - Add loading states and error messages

---

**End of UI Inventory**
