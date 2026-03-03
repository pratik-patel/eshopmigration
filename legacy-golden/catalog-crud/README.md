# Create, Read, Update, Delete catalog items

**Workflow**: `catalog-crud`
**Discovery Date**: 2026-03-02 22:30:08

## Screenshots

- [`001_create_form.png`](screenshots/001_create_form.png)
- [`002_edit_form.png`](screenshots/002_edit_form.png)
- [`003_details_view.png`](screenshots/003_details_view.png)
- [`004_delete_confirm.png`](screenshots/004_delete_confirm.png)

## Workflow Steps

1. **create**: Fill form to create new catalog item
2. **edit**: Modify existing catalog item
3. **details**: View catalog item details
4. **delete**: Delete catalog item with confirmation

## Forms

### Create Form

- **URL**: `http://localhost:50586/Catalog/Create`
- **Fields**: 9

| Field | Type | Required |
|-------|------|----------|
| ctl00$MainContent$Name | text | No |
| ctl00$MainContent$Description | text | No |
| ctl00$MainContent$Brand | select-one | No |
| ctl00$MainContent$Type | select-one | No |
| ctl00$MainContent$Price | text | No |
| ctl00$MainContent$Stock | text | No |
| ctl00$MainContent$Restock | text | No |
| ctl00$MainContent$Maxstock | text | No |
| ctl00$MainContent$ctl06 | submit | No |

### Edit Form

- **URL**: `http://localhost:50586/Catalog/Edit/1`
- **Fields**: 10

| Field | Type | Required |
|-------|------|----------|
| ctl00$MainContent$Name | text | No |
| ctl00$MainContent$Description | text | No |
| ctl00$MainContent$BrandDropDownList | select-one | No |
| ctl00$MainContent$TypeDropDownList | select-one | No |
| ctl00$MainContent$Price | text | No |
| ctl00$MainContent$PictureFileName | text | No |
| ctl00$MainContent$Stock | text | No |
| ctl00$MainContent$Restock | text | No |
| ctl00$MainContent$Maxstock | text | No |
| ctl00$MainContent$ctl07 | submit | No |

### Details Form

- **URL**: `http://localhost:50586/Catalog/Details/1`
- **Fields**: 9

| Field | Type | Required |
|-------|------|----------|
| Name | N/A | No |
| Description | N/A | No |
| Brand | N/A | No |
| Type | N/A | No |
| Price | N/A | No |
| Picture name | N/A | No |
| Stock | N/A | No |
| Restock | N/A | No |
| Max stock | N/A | No |

### Delete Form

- **URL**: `http://localhost:50586/Catalog/Delete/1`

