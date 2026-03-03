# Legacy Application - Workflow Discovery Index

**Base URL**: http://localhost:50586
**Last Discovery**: 2026-03-02 22:40:57
**Total Workflows**: 4 (automated) + 3 (manual)
**Total Screenshots**: 11

## Automated Discovery (Browser Agent)

**Latest Run**: March 2, 2026 22:40:57

### Quick Links
- [README.md](README.md) - Quick start guide
- [BASELINE_INDEX.md](BASELINE_INDEX.md) - Workflow index
- [DISCOVERY_SUMMARY.md](DISCOVERY_SUMMARY.md) - Technical analysis
- [BROWSER_AGENT_REPORT.md](BROWSER_AGENT_REPORT.md) - Executive report
- [workflows.json](workflows.json) - Machine-readable workflows
- [ui-elements.json](ui-elements.json) - Element catalog (111 elements)
- [grid-data.json](grid-data.json) - Table data (10 rows)
- [screenshots/](screenshots/) - 4 screenshots (3.7MB)

### Automated Workflows Discovered
1. **Home/List Page** - Main catalog listing
2. **Create Page** - New item form
3. **Edit Page** - Edit item form
4. **Navigation Flow** - Cancel/back navigation

---

## Manual Workflows (Pre-existing)

### catalog-list

**Description**: View and navigate catalog items list

**Location**: [`catalog-list/`](catalog-list/README.md)

**Screenshots**: 1

**Key Steps**:
- Load catalog list page
- View all catalog items in grid
- Available actions: Edit, Details, Delete, Create

### catalog-crud

**Description**: Create, Read, Update, Delete catalog items

**Location**: [`catalog-crud/`](catalog-crud/README.md)

**Screenshots**: 4

**Key Steps**:
- Fill form to create new catalog item
- Modify existing catalog item
- View catalog item details
- Delete catalog item with confirmation

### static-pages

**Description**: Static and informational pages

**Location**: [`static-pages/`](static-pages/README.md)

**Screenshots**: 2

**Key Steps**:
- Visit 2 static/info pages


## Workflow Details

For detailed information about each workflow, see:

- [catalog-list](catalog-list/README.md)
- [catalog-crud](catalog-crud/README.md)
- [static-pages](static-pages/README.md)
