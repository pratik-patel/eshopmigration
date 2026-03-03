# Apply Practical Gap Fixes

This document contains the EXACT text to add to each agent file.

---

## FIX 1-3: Legacy Context Fabric (101)

**Location**: `.claude/agents/101-legacy-context-fabric.md`
**Add after**: `## Phase 2 — Build ground-truth manifest`

```markdown
---

## Phase 2.5 — Extract Database Schema

Goal: Document tables, columns, foreign keys for migration planning.

Process:
1) Search for `*.sql` files (CREATE TABLE scripts)
2) Search for EF mappings (`[Table]` attributes, DbContext classes)
3) Search for SQL queries in code (extract table/column names)

Write: `docs/context-fabric/database-schema.json`

Example:
```json
{
  "tables": [
    {
      "name": "catalog_items",
      "columns": [
        {"name": "id", "type": "int", "nullable": false, "primary_key": true},
        {"name": "name", "type": "nvarchar(255)", "nullable": false}
      ],
      "foreign_keys": [
        {"column": "category_id", "references": "categories.id"}
      ]
    }
  ]
}
```

Stop condition: All tables documented with columns and FK relationships.

---

## Phase 2.6 — Catalog External Integrations

Goal: Document external API calls, file I/O, email, FTP.

Process:
1) Search: `HttpClient`, `WebRequest` (REST API calls)
2) Search: `File.ReadAllText`, `Directory.GetFiles` (file imports/exports)
3) Search: `SmtpClient` (email)

Write: `docs/context-fabric/external-integrations.json`

Example:
```json
{
  "integrations": [
    {
      "type": "HTTP_REST_API",
      "endpoint": "https://api.crm-system.com/v1",
      "authentication": "API_Key",
      "used_by_seams": ["customer-details"],
      "migration_strategy": "keep_as_is"
    }
  ]
}
```

Stop condition: All HTTP calls, file I/O, email documented.

---

## Phase 2.7 — Catalog User Roles & Permissions

Goal: Document RBAC for secure migration.

Process:
1) Search: `[Authorize(Roles="Admin")]`, `User.IsInRole()`
2) Search database: `Users`, `Roles`, `UserRoles` tables
3) Build permission matrix

Write: `docs/context-fabric/roles-and-permissions.json`

Example:
```json
{
  "roles": [
    {"name": "Admin", "permissions": ["catalog:write", "orders:approve"]},
    {"name": "User", "permissions": ["catalog:read", "orders:create"]}
  ],
  "permission_matrix": [
    {
      "resource": "catalog_items",
      "actions": {
        "view": ["Admin", "User"],
        "edit": ["Admin"]
      }
    }
  ]
}
```

Stop condition: All roles and permissions documented.
```

---

## FIX 4-5: UI Inventory Extractor (102)

**Location**: `.claude/agents/102-ui-inventory-extractor.md`
**Add after**: `## 3.5 Per-Seam Asset Assignment`

```markdown
---

# Phase 3.5 — Extract Design System

Purpose: Capture colors, fonts, spacing for consistent styling.

Process:
1) Search code: `Color.FromArgb()`, `Brushes.*`, hex values
2) Search XAML/CSS: color definitions
3) Search: `Font()` constructors
4) Search: `Margin`, `Padding` patterns

Write:
- `docs/context-fabric/design-system.json`
- `docs/context-fabric/tailwind.config.js` (Tailwind mapping)

Example (design-system.json):
```json
{
  "colors": {
    "primary": "#0078D4",
    "success": "#107C10",
    "error": "#E81123"
  },
  "typography": {
    "fontFamily": "Segoe UI",
    "fontSize": {"base": "14px", "lg": "16px"}
  },
  "spacing": {
    "1": "4px",
    "2": "8px",
    "4": "16px"
  }
}
```

Stop condition: Colors, fonts, spacing extracted.
```

**Add after**: `# Phase 4 — Map screens to seams`

```markdown
---

# Phase 4.5 — Generate Navigation Map

Purpose: Document menu structure, screen-to-screen flows, routes.

Process:
1) Search: `MenuStrip`, `ToolStripMenuItem` (WinForms) or `<Menu>` (WPF)
2) Build navigation tree (which screen opens which)
3) Extract keyboard shortcuts
4) Map to React routes

Write: `docs/context-fabric/navigation-map.json`

Example:
```json
{
  "main_menu": {
    "items": [
      {"label": "Catalog", "children": [
        {"label": "View Catalog", "action": "open_catalog_list_form", "seam": "catalog-list"}
      ]}
    ]
  },
  "navigation_tree": {
    "CatalogListForm": {
      "navigates_to": [
        {"target": "CatalogEditForm", "trigger": "Edit button", "modal": true}
      ]
    }
  },
  "route_mapping": [
    {"legacy_screen": "CatalogListForm", "modern_route": "/catalog"}
  ]
}
```

Stop condition: Menus, navigation flows, routes documented.
```

---

## FIX 6-8: Discovery Agent (301)

**Location**: `.claude/agents/301-discovery.md`
**Add after**: `### Step 4: Data Ownership & Writes`

```markdown
### Step 4.5: Pagination, Filtering, Sorting & Format Rules

Goal: Capture grid defaults and display formats.

**Pagination/Filtering/Sorting**:
1) Search grid code: `PageSize = 50`, default page size
2) Search: default filter values (e.g., `Status = "Active"`)
3) Search: default sort column/direction

Add to `discovery.md`:
```markdown
## Grid Defaults
- Page size: 50 rows
- Default filter: Status = "Active"
- Default sort: Name ascending
```

**Display Format Rules**:
1) Search: `.ToString("C")`, `.ToString("N2")` (number formats)
2) Search: `.ToString("yyyy-MM-dd")` (date formats)
3) Search: `if (value) "Yes" else "No"` (boolean displays)

Add to `discovery.md`:
```markdown
## Display Rules
- Dates: MM/DD/YYYY format
- Currency: USD ($1,234.56)
- Numbers: 2 decimal places
- Booleans: "Yes" / "No"
```

Stop condition: Grid defaults and format rules documented.
```

**Add after**: `### Step 3: Trace Vertical Slice`

```markdown
### Step 3.5: Document Multi-Step Backend Workflows

Goal: Capture orchestrated workflows (order approval, batch import, scheduled jobs).

Process:
1) Search: transaction scopes spanning multiple service calls
2) Search: workflow engines, state machines
3) Search: scheduled jobs (Quartz.NET, Hangfire, Windows Task Scheduler)

Add to `discovery.md`:
```markdown
## Multi-Step Workflows

### Order Approval Workflow:
1. User clicks "Submit for Approval"
2. Backend: Create approval request record
3. Backend: Send email to manager
4. Backend: Update order status to "Pending Approval"
5. Manager clicks "Approve" in email link
6. Backend: Update order status to "Approved"
7. Backend: Trigger fulfillment process
```

Stop condition: All multi-step workflows documented.
```

---

## FIX 9: Spec Agent (302)

**Location**: `.claude/agents/302-spec-agent.md`
**Add at START of Phase 1**: Before "## Step 1: Read Discovery Inputs"

```markdown
### Step 0: Validate Input Completeness (PRE-FLIGHT CHECK)

**Before generating requirements**, validate ALL inputs complete:

Checklist:
- ✅ `discovery.md` has verified UI triggers, flows, data ownership
- ✅ `discovery.md` has grid defaults (page size, filters, sort)
- ✅ `discovery.md` has display rules (date/currency/number formats)
- ✅ `discovery.md` has multi-step workflows (if applicable)
- ✅ `ui-behavior.md` has layout elements, screens, controls, grids, actions, assets
- ✅ `design-system.json` exists (colors, fonts, spacing)
- ✅ `navigation-map.json` exists (menu structure, routes)
- ✅ `architecture-design.md` exists (tech stack)

**If ANY missing**: STOP and report "Input incomplete - missing {item}"

**If complete**: Proceed to Step 1.
```

---

## FIX 10: Frontend Migration (402)

**Location**: `.claude/agents/402-frontend-migration.md`
**Add after**: `#### Gate 10: Linting`

```markdown
#### Gate 11: Manual UI Checklist (Interactive Elements)

Purpose: Verify interactive elements visual parity can't detect.

Process:
1) Start dev server: `npm run dev`
2) User manually checks:

**User Checklist**:
- □ Tooltips: Hover over buttons - tooltips appear with correct text?
- □ Context menus: Right-click grid row - context menu appears with correct options?
- □ Breadcrumbs: Breadcrumb trail shows correct hierarchy?
- □ Keyboard shortcuts: Ctrl+N, F5, Escape work correctly?
- □ Loading states: Spinner shows during data load?
- □ Empty states: "No items found" message shows when grid empty?
- □ Error messages: Validation errors show inline with correct wording?

Must pass: User confirms all items checked.

If fails: Update components to add missing elements.
```

---

## Implementation Order

1. Update `101-legacy-context-fabric.md` (Fixes 1-3)
2. Update `102-ui-inventory-extractor.md` (Fixes 4-5)
3. Update `301-discovery.md` (Fixes 6-8)
4. Update `302-spec-agent.md` (Fix 9)
5. Update `402-frontend-migration.md` (Fix 10)

---

## Total Lines Added: ~220 lines (practical, concise)

**Result**: Zero requirements slip through, including smallest details.
