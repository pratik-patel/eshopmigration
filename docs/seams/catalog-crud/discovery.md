# Discovery Report: catalog-crud

**Seam ID**: catalog-crud
**Date**: 2026-03-02
**Status**: Discovery Complete
**Confidence**: High

---

## Executive Summary

**Purpose**: Complete CRUD operations (Create, Read, Update, Delete) for catalog items with form validation and database persistence.

**Complexity**: High
- 4 page lifecycles (Create, Edit, Details, Delete)
- Multiple service method calls
- Database writes (INSERT, UPDATE, DELETE)
- Form validation (client + server)
- Dropdown population from database
- Transaction management

**Readiness**: ✅ GO
- Clear boundaries for all 4 operations
- All data flows mapped
- Database writes documented
- No blockers
- No hard dependencies
- Implementation already complete

---

## Entry Points & Triggers

### Trigger 1: Create Page Load

**File**: `src/eShopLegacyWebForms/Catalog/Create.aspx.cs`
**Symbol**: `Create.Page_Load`
**Lines**: 15-18
**Framework Event**: ASP.NET WebForms Page_Load

**Evidence**:
```csharp
protected void Page_Load(object sender, EventArgs e)
{
    _log.Info($"Now loading... /Catalog/Create.aspx");
}
```

**Trigger Conditions**: User navigates to `/Catalog/Create`

---

### Trigger 2: Create Button Click

**File**: `src/eShopLegacyWebForms/Catalog/Create.aspx.cs`
**Symbol**: `Create.Create_Click`
**Lines**: 30-50
**Framework Event**: Button Click (OnClick)

**Evidence**:
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
        };

        CatalogService.CreateCatalogItem(catalogItem);

        Response.Redirect("~");
    }
}
```

**Trigger Conditions**: User submits Create form

**Input Parameters**:
- All form fields (see Required Fields section)

---

### Trigger 3: Edit Page Load

**File**: `src/eShopLegacyWebForms/Catalog/Edit.aspx.cs`
**Symbol**: `Edit.Page_Load`
**Lines**: 18-35
**Framework Event**: Page_Load

**Evidence**:
```csharp
protected void Page_Load(object sender, EventArgs e)
{
    if (!Page.IsPostBack)
    {
        var productId = Convert.ToInt32(Page.RouteData.Values["id"]);
        _log.Info($"Now loading... /Catalog/Edit.aspx?id={productId}");
        product = CatalogService.FindCatalogItem(productId);

        BrandDropDownList.DataSource = CatalogService.GetCatalogBrands();
        BrandDropDownList.SelectedValue = product.CatalogBrandId.ToString();

        TypeDropDownList.DataSource = CatalogService.GetCatalogTypes();
        TypeDropDownList.SelectedValue = product.CatalogTypeId.ToString();

        this.DataBind();
    }
}
```

**Trigger Conditions**: User navigates to `/Catalog/Edit/{id}`

**Input Parameters**:
- `id` (int, from route)

---

### Trigger 4: Save Button Click (Edit)

**File**: `src/eShopLegacyWebForms/Catalog/Edit.aspx.cs`
**Symbol**: `Edit.Save_Click`
**Lines**: 47-68
**Framework Event**: Button Click

**Evidence**:
```csharp
protected void Save_Click(object sender, EventArgs e)
{
    if (this.ModelState.IsValid)
    {
        var catalogItem = new CatalogItem
        {
            Id = Convert.ToInt32(Page.RouteData.Values["id"]),
            Name = Name.Text,
            Description = Description.Text,
            CatalogBrandId = int.Parse(BrandDropDownList.SelectedValue),
            CatalogTypeId = int.Parse(TypeDropDownList.SelectedValue),
            Price = decimal.Parse(Price.Text),
            PictureFileName = PictureFileName.Text,
            AvailableStock = int.Parse(Stock.Text),
            RestockThreshold = int.Parse(Restock.Text),
            MaxStockThreshold = int.Parse(Maxstock.Text)
        };
        CatalogService.UpdateCatalogItem(catalogItem);

        Response.Redirect("~");
    }
}
```

**Trigger Conditions**: User submits Edit form

---

### Trigger 5: Details Page Load

**File**: `src/eShopLegacyWebForms/Catalog/Details.aspx.cs`
**Symbol**: `Details.Page_Load`
**Lines**: 16-23
**Framework Event**: Page_Load

**Evidence**:
```csharp
protected void Page_Load(object sender, EventArgs e)
{
    var productId = Convert.ToInt32(Page.RouteData.Values["id"]);
    _log.Info($"Now loading... /Catalog/Details.aspx?id={productId}");
    product = CatalogService.FindCatalogItem(productId);

    this.DataBind();
}
```

**Trigger Conditions**: User navigates to `/Catalog/Details/{id}`

---

### Trigger 6: Delete Page Load

**File**: `src/eShopLegacyWebForms/Catalog/Delete.aspx.cs`
**Symbol**: `Delete.Page_Load`
**Lines**: 16-24
**Framework Event**: Page_Load

**Evidence**:
```csharp
protected void Page_Load(object sender, EventArgs e)
{
    var productId = Convert.ToInt32(Page.RouteData.Values["id"]);
    _log.Info($"Now loading... /Catalog/Delete.aspx?id={productId}");
    productToDelete = CatalogService.FindCatalogItem(productId);

    this.DataBind();
}
```

**Trigger Conditions**: User navigates to `/Catalog/Delete/{id}`

---

### Trigger 7: Delete Button Click

**File**: `src/eShopLegacyWebForms/Catalog/Delete.aspx.cs`
**Symbol**: `Delete.Delete_Click`
**Lines**: 26-30
**Framework Event**: Button Click

**Evidence**:
```csharp
protected void Delete_Click(object sender, EventArgs e)
{
    CatalogService.RemoveCatalogItem(productToDelete);

    Response.Redirect("~");
}
```

**Trigger Conditions**: User confirms deletion

---

## Vertical Slice: Call Chains

### Flow 1: Create Product

**Trigger**: Create_Click button
**Start**: `Create.aspx.cs:Create_Click` (line 30)
**End**: Database INSERT + redirect

**Call Path**:
```
1. Create.Create_Click (Create.aspx.cs:30)
   ├─> ModelState.IsValid check (validation)
   ├─> Parse form fields into CatalogItem object
   │
2. CatalogService.CreateCatalogItem (CatalogService.cs:52)
   ├─> indexGenerator.GetNextSequenceValue(db)  [HiLo ID generation]
   ├─> db.CatalogItems.Add(catalogItem)          [EF6 Add]
   ├─> db.SaveChanges()                          [WRITE: INSERT]
   │
3. Response.Redirect("~")                         [Navigate to catalog list]
```

**Boundaries Hit**:
- **Data Access**: Entity Framework 6 INSERT operation
- **Cross-seam navigation**: Redirect to catalog-list seam

**Side Effects**: **INSERT INTO CatalogItems** (new row created)

**Transaction Scope**: Implicit EF6 transaction (SaveChanges())

---

### Flow 2: Edit Product

**Trigger**: Save_Click button
**Start**: `Edit.aspx.cs:Save_Click` (line 47)
**End**: Database UPDATE + redirect

**Call Path**:
```
1. Edit.Page_Load (Edit.aspx.cs:18) - FIRST (on initial load)
   ├─> CatalogService.FindCatalogItem(productId)  [READ: SELECT by ID]
   ├─> CatalogService.GetCatalogBrands()           [READ: brands for dropdown]
   ├─> CatalogService.GetCatalogTypes()            [READ: types for dropdown]
   ├─> DataBind() (populate form)
   │
2. Edit.Save_Click (Edit.aspx.cs:47) - THEN (on form submit)
   ├─> ModelState.IsValid check
   ├─> Parse form fields into CatalogItem object
   │
3. CatalogService.UpdateCatalogItem (CatalogService.cs:59)
   ├─> db.Entry(catalogItem).State = EntityState.Modified  [Mark as modified]
   ├─> db.SaveChanges()                                     [WRITE: UPDATE]
   │
4. Response.Redirect("~")
```

**Boundaries Hit**:
- **Data Access**: EF6 SELECT + UPDATE operations
- **Cross-seam navigation**: Redirect to catalog-list seam

**Side Effects**: **UPDATE CatalogItems SET ... WHERE Id = {id}** (row modified)

**Transaction Scope**: Implicit EF6 transaction (SaveChanges())

---

### Flow 3: View Details (Read-Only)

**Trigger**: Details Page_Load
**Start**: `Details.aspx.cs:Page_Load` (line 16)
**End**: Display product data

**Call Path**:
```
1. Details.Page_Load (Details.aspx.cs:16)
   ├─> CatalogService.FindCatalogItem(productId)  [READ: SELECT by ID]
   ├─> DataBind() (display product)
```

**Boundaries Hit**:
- **Data Access**: EF6 SELECT operation
- **No writes**: Read-only

**Side Effects**: NONE (read-only)

**Transaction Scope**: NONE

---

### Flow 4: Delete Product

**Trigger**: Delete_Click button
**Start**: `Delete.aspx.cs:Delete_Click` (line 26)
**End**: Database DELETE + redirect

**Call Path**:
```
1. Delete.Page_Load (Delete.aspx.cs:16) - FIRST (on initial load)
   ├─> CatalogService.FindCatalogItem(productId)  [READ: SELECT by ID]
   ├─> DataBind() (display product for confirmation)
   │
2. Delete.Delete_Click (Delete.aspx.cs:26) - THEN (on confirm)
   ├─> CatalogService.RemoveCatalogItem(productToDelete)
   │
3. CatalogService.RemoveCatalogItem (CatalogService.cs:65)
   ├─> db.CatalogItems.Remove(catalogItem)        [EF6 Remove]
   ├─> db.SaveChanges()                           [WRITE: DELETE]
   │
4. Response.Redirect("~")
```

**Boundaries Hit**:
- **Data Access**: EF6 SELECT + DELETE operations
- **Cross-seam navigation**: Redirect to catalog-list seam

**Side Effects**: **DELETE FROM CatalogItems WHERE Id = {id}** (row removed)

**Transaction Scope**: Implicit EF6 transaction (SaveChanges())

---

### Flow 5: Populate Dropdowns

**Trigger**: Create/Edit Page_Load or GetBrands/GetTypes methods
**Start**: `Create.aspx.cs:GetBrands/GetTypes` or `Edit.aspx.cs:GetBrands/GetTypes`
**End**: Return lists for dropdown binding

**Call Path (Brands)**:
```
1. Create.GetBrands() or Edit.GetBrands()
   ├─> CatalogService.GetCatalogBrands()
   │
2. CatalogService.GetCatalogBrands() (CatalogService.cs:47)
   ├─> db.CatalogBrands.ToList()  [READ: SELECT * FROM CatalogBrands]
```

**Call Path (Types)**:
```
1. Create.GetTypes() or Edit.GetTypes()
   ├─> CatalogService.GetCatalogTypes()
   │
2. CatalogService.GetCatalogTypes() (CatalogService.cs:42)
   ├─> db.CatalogTypes.ToList()   [READ: SELECT * FROM CatalogTypes]
```

**Boundaries Hit**:
- **Data Access**: EF6 SELECT operations
- **No writes**: Read-only

**Side Effects**: NONE

**Transaction Scope**: NONE

---

## Data Ownership & Targets

### Read Targets

| Table/Entity | Access Pattern | Evidence | Operations |
|--------------|----------------|----------|------------|
| **CatalogItems** | SELECT by ID | CatalogService.cs:39, Edit/Details/Delete Page_Load | FindCatalogItem |
| **CatalogBrands** | SELECT all | CatalogService.cs:47, Create/Edit GetBrands | ToList() |
| **CatalogTypes** | SELECT all | CatalogService.cs:42, Create/Edit GetTypes | ToList() |

### Write Targets

| Table/Entity | Operations | Evidence | Side Effects |
|--------------|-----------|----------|--------------|
| **CatalogItems** | INSERT | CatalogService.cs:52-56, Create_Click | New row added |
| **CatalogItems** | UPDATE | CatalogService.cs:59-62, Save_Click | Existing row modified |
| **CatalogItems** | DELETE | CatalogService.cs:65-68, Delete_Click | Row removed |

**SQL Operations**:

**CREATE**:
```sql
INSERT INTO CatalogItems (
    Id, Name, Description, Price, PictureFileName, PictureUri,
    CatalogTypeId, CatalogBrandId, AvailableStock,
    RestockThreshold, MaxStockThreshold, OnReorder
) VALUES (...)
```

**UPDATE**:
```sql
UPDATE CatalogItems SET
    Name = @name,
    Description = @description,
    Price = @price,
    CatalogTypeId = @typeId,
    CatalogBrandId = @brandId,
    AvailableStock = @stock,
    RestockThreshold = @restock,
    MaxStockThreshold = @maxStock,
    PictureFileName = @pictureFileName
WHERE Id = @id
```

**DELETE**:
```sql
DELETE FROM CatalogItems WHERE Id = @id
```

### Unknown Targets

**NONE** - All data access paths confirmed via code inspection.

### Shared Write Conflicts

**POTENTIAL CONFLICT**:
- **Table**: CatalogItems
- **Conflict Type**: Concurrent writes to same row
- **Scenarios**:
  - User A edits product 1 while User B deletes product 1
  - User A edits product 1 while User B also edits product 1 (last-write-wins)

**Mitigation**:
- EF6 handles concurrency at database level
- No optimistic concurrency checks in legacy code
- Last-write-wins behavior (acceptable for catalog management)

**Cross-Seam Write Sharing**:
- CatalogItems table written by: **catalog-crud** seam only
- CatalogItems table read by: **catalog-list** seam, **catalog-crud** seam
- ✅ **Safe**: Only one seam performs writes

---

## Dependencies

### In-Seam Dependencies

| Type | Symbol | File | Purpose |
|------|--------|------|---------|
| Page | `Create` | Catalog/Create.aspx.cs | Create page class |
| Page | `Edit` | Catalog/Edit.aspx.cs | Edit page class |
| Page | `Details` | Catalog/Details.aspx.cs | Details page class |
| Page | `Delete` | Catalog/Delete.aspx.cs | Delete page class |
| Service Interface | `ICatalogService` | Services/ICatalogService.cs | Catalog operations contract |
| Service Implementation | `CatalogService` | Services/CatalogService.cs | EF6-based implementation |
| Model | `CatalogItem` | Models/CatalogItem.cs | Product entity |
| Model | `CatalogBrand` | Models/CatalogBrand.cs | Brand entity |
| Model | `CatalogType` | Models/CatalogType.cs | Type entity |
| Data Context | `CatalogDBContext` | Models/CatalogDBContext.cs | EF6 DbContext |
| ID Generator | `CatalogItemHiLoGenerator` | Models/CatalogItemHiLoGenerator.cs | HiLo ID generation |

### Cross-Seam Dependencies

| Target Seam | Dependency Type | Evidence | Severity |
|-------------|-----------------|----------|----------|
| **catalog-list** | Navigation (hard) | Response.Redirect("~") after Create/Edit/Delete | Medium |

**Note**: All CRUD operations redirect to catalog-list seam (/) after completion. This is a **hard navigation dependency** but does not affect code coupling.

### External Dependencies

**NONE**

- No COM/ActiveX
- No device I/O
- No Windows Registry
- No file system writes (except database)
- No external HTTP APIs
- No message queues

### Framework Dependencies

| Framework | Version | Usage | Migration Target |
|-----------|---------|-------|------------------|
| ASP.NET WebForms | 4.7.2 | Page lifecycle, data binding, validation | FastAPI |
| Entity Framework 6 | 6.x | ORM, CRUD operations, transactions | SQLAlchemy 2.x async |
| Autofac | 4.x | Dependency injection | FastAPI Depends() |
| log4net | 2.x | Logging | Structlog |

---

## Hard Dependencies & Blockers

### Blockers: NONE ✅

No high-severity blockers identified.

### Refactoring Required: NO ✅

- Clean separation between pages, service, and data layers
- Service interface already defined
- No static/global dependencies
- No reflection or dynamic dispatch
- Well-defined transaction boundaries
- No shared write conflicts (single-writer pattern)

### Dependency Wrapper Needed: NO ✅

No platform-specific dependencies requiring abstraction.

---

## Required Fields for Contract

### Create Product (POST /api/catalog/items)

**Request Body**:

| Field | Type | Required | Default | Validation | Evidence |
|-------|------|----------|---------|------------|----------|
| `name` | string | YES | - | Min 1 char | Create.aspx.cs:36 |
| `description` | string | NO | - | - | Create.aspx.cs:37 |
| `catalog_brand_id` | integer | YES | - | Must exist in CatalogBrands | Create.aspx.cs:38 |
| `catalog_type_id` | integer | YES | - | Must exist in CatalogTypes | Create.aspx.cs:39 |
| `price` | decimal | YES | - | 0-1000000, max 2 decimals | Create.aspx.cs:40 |
| `available_stock` | integer | NO | 0 | 0-10000000 | Create.aspx.cs:41 |
| `restock_threshold` | integer | NO | 0 | 0-10000000 | Create.aspx.cs:42 |
| `max_stock_threshold` | integer | NO | 0 | 0-10000000 | Create.aspx.cs:43 |
| `picture_file_name` | string | NO | "dummy.png" | - | Model default |

**Response**: Created CatalogItem with ID assigned

---

### Update Product (PUT /api/catalog/items/{id})

**Path Parameter**:
- `id` (integer, required): Product ID

**Request Body**: Same as Create, plus:
- `picture_file_name` (string, required): Cannot be changed in UI (read-only display)

**Response**: Updated CatalogItem

---

### Get Product (GET /api/catalog/items/{id})

**Path Parameter**:
- `id` (integer, required): Product ID

**Response**: CatalogItem with CatalogBrand and CatalogType populated

---

### Delete Product (DELETE /api/catalog/items/{id})

**Path Parameter**:
- `id` (integer, required): Product ID

**Response**: 204 No Content

---

### Get Brands (GET /api/catalog/brands)

**Response**: Array of CatalogBrand objects

| Field | Type |
|-------|------|
| `id` | integer |
| `brand` | string |

---

### Get Types (GET /api/catalog/types)

**Response**: Array of CatalogType objects

| Field | Type |
|-------|------|
| `id` | integer |
| `type` | string |

---

## Business Rules

All 28 business rules from `docs/context-fabric/business-rules.json` apply. Key rules:

### BR-001: Price Validation
- Positive decimal
- Maximum 2 decimal places
- Range: 0 to 1,000,000
- Error: "The Price must be a positive number with maximum two decimals between 0 and 1 million."

### BR-002: Available Stock Validation
- Integer
- Range: 0 to 10,000,000
- Error: "The field Stock must be between 0 and 10 million."

### BR-003: Restock Threshold Validation
- Integer
- Range: 0 to 10,000,000
- Error: "The field Restock must be between 0 and 10 million."

### BR-004: Max Stock Threshold Validation
- Integer
- Range: 0 to 10,000,000
- Error: "The field Max stock must be between 0 and 10 million."

### BR-005: Name Required
- Non-empty string
- Error: "The Name field is required."

### BR-006: Picture Filename Default
- Default: "dummy.png"
- Read-only on Edit page

---

## Test Scenarios

### Scenario 1: Create Valid Product
**Input**: All required fields with valid data
**Expected**:
- Validation passes
- INSERT INTO CatalogItems
- Redirect to /
- Product appears in catalog list

### Scenario 2: Create with Validation Errors
**Input**: Empty name, invalid price
**Expected**:
- Validation fails
- Error messages display
- No database write
- Form remains on Create page

### Scenario 3: Edit Product
**Input**: Change name and price of product 1
**Expected**:
- UPDATE CatalogItems WHERE Id = 1
- Redirect to /
- Changes visible in catalog list

### Scenario 4: Edit with Read-Only Picture
**Input**: Attempt to change picture_file_name
**Expected**:
- Field is read-only in UI
- Value not changed in database

### Scenario 5: View Details
**Input**: Navigate to /Catalog/Details/1
**Expected**:
- Product 1 details display
- All fields read-only
- Edit button available

### Scenario 6: Delete Product
**Input**: Confirm delete for product 1
**Expected**:
- DELETE FROM CatalogItems WHERE Id = 1
- Redirect to /
- Product no longer in catalog list

### Scenario 7: Product Not Found
**Input**: Navigate to /Catalog/Edit/99999
**Expected**:
- FindCatalogItem returns null
- 404 or error page (implementation-dependent)

---

## Migration Notes

### Backend Migration
- **Routes**: Already implemented ✅
  - POST /api/catalog/items
  - GET /api/catalog/items/{id}
  - PUT /api/catalog/items/{id}
  - DELETE /api/catalog/items/{id}
  - GET /api/catalog/brands
  - GET /api/catalog/types

- **Service**: CatalogService methods already implemented ✅
- **Validation**: Pydantic schemas with all business rules ✅

### Frontend Migration
- **Routes**: Already implemented ✅
  - /catalog/create
  - /catalog/edit/:id
  - /catalog/details/:id
  - /catalog/delete/:id

- **Components**: Already implemented ✅
  - CatalogForm (shared by Create/Edit)
  - CatalogCreatePage
  - CatalogEditPage
  - CatalogDetailsPage
  - CatalogDeletePage

- **Hooks**: TanStack Query hooks already implemented ✅
- **Validation**: Zod schemas matching Pydantic ✅

---

## Readiness Assessment

### Readiness: ✅ GO

**Confidence**: HIGH

**Confidence Reason**:
- All 4 CRUD operations mapped
- All data writes documented
- Service interface clear and complete
- Transaction boundaries understood
- Backend already implemented ✅
- Frontend already implemented ✅
- No hard dependencies
- No blockers

### Blockers: NONE

### Warnings: NONE

### Requirements Met:
- ✅ Entry points confirmed (7 triggers)
- ✅ Data flows traced (5 flows)
- ✅ Data targets identified (READ: 3 tables, WRITE: 1 table)
- ✅ Write operations confirmed (INSERT, UPDATE, DELETE)
- ✅ Dependencies documented
- ✅ No hard dependencies
- ✅ Business rules documented (28 rules)
- ✅ Test scenarios defined (7 scenarios)

---

## Next Steps

1. ✅ **Discovery complete** - This document
2. → **Contract generation** (STEP 7) - Generate OpenAPI spec for all CRUD endpoints
3. → **Data strategy** (STEP 8) - Document write strategy
4. ✅ **Backend implementation** (STEP 10) - Already complete
5. ✅ **Frontend implementation** (STEP 11) - Already complete
6. → **Parity testing** (STEP 12) - Generate parity tests (optional)

**Estimated implementation time**: Already complete
**Validation time**: 30-45 minutes (manual validation of all 4 workflows)

---

**Discovery completed**: 2026-03-02
**Ready for contract generation**: YES
