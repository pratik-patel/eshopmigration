# 🎯 Migration Progress & Insights Dashboard — Complete Specification

**Think like:** Creative Experience Architect + Enterprise Architect
**Principle:** Every pixel tells the migration story using **real data from agent artifacts**

---

## 🌟 Vision

A **living, breathing dashboard** that transforms raw agent outputs into a compelling visual narrative of your migration journey. Not just metrics — a **story of transformation** from legacy to modern, told through data, progress, and insights.

---

## 📊 Dashboard Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    MIGRATION COMMAND CENTER                  │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  🎯 Hero Score        📈 Phase Progress      ⏱️ Timeline    │
│  [87/100]            [████████░░] 75%        [Live Clock]    │
│                                                               │
├─────────────────────────────────────────────────────────────┤
│  Navigation Sidebar                Main Content Area         │
│  ┌─────────────────┐              ┌───────────────────────┐ │
│  │ 🏠 Overview     │              │                       │ │
│  │ 🔍 Phase 0      │              │   Dynamic Content     │ │
│  │ 🔬 Phase 1      │              │   (Phase-specific)    │ │
│  │ 🏗️ Phase 2      │              │                       │ │
│  │ 📝 Phase 3      │              │                       │ │
│  │ 🗺️ Phase 4      │              │                       │ │
│  │ 🔨 Phase 5      │              │                       │ │
│  │ ✅ Phase 6      │              │                       │ │
│  │ 📊 Analytics    │              │                       │ │
│  │ 🎨 Artifacts    │              │                       │ │
│  │ 🚨 Issues       │              │                       │ │
│  └─────────────────┘              └───────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 🗂️ Data Sources (Agent Artifacts)

### Phase 0: Discovery Loop
```
docs/context-fabric/
├── project-facts.json          → Codebase summary, framework detection
├── manifest.json               → All modules/files inventory
├── database-schema.json        → Table relationships, FK constraints
├── seam-proposals.json         → All discovered seams
├── coverage-audit.json         → Coverage metrics
├── business-rules.json         → Extracted business rules
├── static-assets-catalog.json  → All images/icons/resources
├── dependency-graph.json       → Inter-seam dependencies
└── design-system.json          → UI design tokens

docs/legacy-golden/
├── coverage-report.json        → Runtime coverage %
├── {seam}/BASELINE_INDEX.md    → Screenshots catalog per seam
└── {seam}/baselines/           → Actual golden screenshots
```

### Phase 1: Per-Seam Discovery
```
docs/seams/{seam}/
├── spec.md                     → Seam purpose, scope
├── discovery.md                → Technical analysis (call chains, data access)
├── evidence-map.json           → Triggers, flows, boundaries
├── readiness.json              → Readiness score, blockers
├── boundary-issues.json        → Scope issues (if any)
└── ui-behavior.md              → UI structure, controls, grids
```

### Phase 2: Architecture
```
docs/
├── architecture-design.md      → Tech stack (from CLAUDE.md)
└── api-design-patterns.md      → API conventions (from CLAUDE.md)
```

### Phase 3: Specifications
```
docs/seams/{seam}/
├── requirements.md             → EARS functional requirements
├── design.md                   → Components, APIs, data models
├── tasks.md                    → Implementation checklist
└── contracts/openapi.yaml      → API specification
```

### Phase 4: Roadmap
```
docs/
└── implementation-roadmap.md   → Waves, priorities, dependencies
```

### Phase 5: Implementation
```
backend/app/{seam}/             → Backend code
frontend/src/pages/{seam}/      → Frontend code
docs/seams/{seam}/
├── implementation-summary.md   → What was built
└── test-results.json           → Quality gate results
```

### Phase 6: Validation
```
docs/seams/{seam}/
├── security-review.md          → Security scan results
└── parity-results/
    └── VERIFICATION_SUMMARY.md → Visual parity (SSIM scores)
```

---

## 🎨 Page-by-Page Design

### 1. 🏠 **Overview Dashboard** (Home)

**Purpose:** Executive summary — migration health at a glance

#### Hero Section
```
┌─────────────────────────────────────────────────────────────┐
│                   MIGRATION HEALTH SCORE                      │
│                                                               │
│                         ┌─────────┐                          │
│                         │  87/100 │  🟢 Near Ready           │
│                         └─────────┘                          │
│                                                               │
│    Started: Mar 1, 2026  │  Elapsed: 14d 3h  │  ETA: 2 weeks│
└─────────────────────────────────────────────────────────────┘
```

**Data Source:**
- Overall score from `readiness.json` (average across seams)
- Start date from `.claude/migration-state.json`
- ETA calculated from velocity (seams completed / days elapsed)

#### Phase Progress Cards
```
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│ Phase 0          │ │ Phase 1          │ │ Phase 2          │
│ Discovery Loop   │ │ Per-Seam Disc.   │ │ Architecture     │
│ ✅ COMPLETE      │ │ 🔵 IN PROGRESS   │ │ ⏸️ NOT STARTED   │
│ 100% coverage    │ │ 12/15 seams      │ │                  │
└──────────────────┘ └──────────────────┘ └──────────────────┘
```

**Data Source:**
- Phase 0: Check `coverage-report.json` → `coverage_percentage == 100`
- Phase 1: Count seams with `discovery.md` vs. total in `seam-proposals.json`
- Phase 2: Check existence of `architecture-design.md`

#### Seam Status Matrix
```
┌─────────────────────────────────────────────────────────────┐
│  SEAM NAME          │ STATUS      │ READINESS │ BLOCKERS    │
├─────────────────────────────────────────────────────────────┤
│  catalog-list       │ ✅ Complete │ 95/100    │ None        │
│  catalog-crud       │ 🔵 Testing  │ 88/100    │ None        │
│  orders-edit        │ 🟡 Impl.    │ 72/100    │ None        │
│  reports-generator  │ 🔴 Blocked  │ 45/100    │ Data Access │
│  ...                │ ...         │ ...       │ ...         │
└─────────────────────────────────────────────────────────────┘
```

**Data Source:** Combine data from:
- `seam-proposals.json` → Seam names
- `readiness.json` per seam → Readiness score
- `tasks.md` → Status (count completed vs. total)
- `boundary-issues.json` → Blockers

#### Top Insights (Automated Insights Engine)
```
┌─────────────────────────────────────────────────────────────┐
│  💡 KEY INSIGHTS                                             │
│  • 3 seams are blocked by shared data access component      │
│  • Frontend performance scores improved by 23% on average   │
│  • 127 UI screens discovered (12 uncovered after Phase 0)   │
│  • API parity: 95% — 3 endpoints need implementation        │
└─────────────────────────────────────────────────────────────┘
```

**Data Source:** Computed insights:
- Parse `boundary-issues.json` → Group by blocker type
- Compare Lighthouse scores before/after
- Sum screens from `coverage-report.json`
- Compare OpenAPI specs (legacy vs. modern)

---

### 2. 🔍 **Phase 0: Discovery Loop**

**Purpose:** Show how the codebase was explored and seams discovered

#### Discovery Timeline
```
┌─────────────────────────────────────────────────────────────┐
│  DISCOVERY ITERATIONS                                        │
│                                                               │
│  Iteration 1 [Mar 1, 10:00] ━━━━━━━━━━━━━━━━━ 85% coverage │
│    • Discovered 12 seams                                     │
│    • Found 18 uncovered screens                              │
│                                                               │
│  Iteration 2 [Mar 1, 14:30] ━━━━━━━━━━━━━━━━━ 92% coverage │
│    • Added 3 new seams                                       │
│    • Found 9 uncovered screens                               │
│                                                               │
│  Iteration 3 [Mar 2, 09:00] ━━━━━━━━━━━━━━━━━ 100% ✅      │
│    • No new seams                                            │
│    • All screens covered                                     │
└─────────────────────────────────────────────────────────────┘
```

**Data Source:**
- Parse `migration-state.json` → Track iterations
- Each iteration stores: timestamp, seams_discovered, coverage_percentage

#### Seam Map (Visual Graph)
```
┌─────────────────────────────────────────────────────────────┐
│  SEAM DEPENDENCY GRAPH                                       │
│                                                               │
│     [catalog-list] ──────┐                                   │
│           │              ├──→ [data-access]                  │
│           │              │                                    │
│     [catalog-crud] ──────┘                                   │
│                                                               │
│     [orders-list] ───────┬──→ [reports-generator]            │
│                          │                                    │
│     [orders-edit] ───────┘                                   │
│                                                               │
│  🟢 No blockers  🟡 Circular dep  🔴 Missing dependency     │
└─────────────────────────────────────────────────────────────┘
```

**Data Source:**
- `dependency-graph.json` → Parse dependencies
- `seam-proposals.json` → Seam metadata
- Visualize with D3.js or Cytoscape.js

#### Coverage Heatmap
```
┌─────────────────────────────────────────────────────────────┐
│  CODEBASE COVERAGE                                           │
│                                                               │
│  Module              Files  Covered  Uncovered  % Coverage   │
│  ────────────────────────────────────────────────────────────│
│  UI/Forms            45     45       0           100%  ████  │
│  Services            23     22       1           96%   ███░  │
│  Data Access         12     12       0           100%  ████  │
│  Reports             8      5        3           63%   ██░░  │
│  Admin               6      0        6           0%     ░░░░ │
└─────────────────────────────────────────────────────────────┘
```

**Data Source:**
- `coverage-audit.json` → Per-module coverage
- `manifest.json` → File inventory

#### Context Fabric Explorer
Interactive browser for discovered artifacts:
- **Project Facts** (framework, modules, entry points)
- **Database Schema** (tables, FKs, indexes)
- **Business Rules** (extracted validation logic)
- **Static Assets** (all images/icons catalog)
- **Design System** (colors, fonts, spacing)

**Data Source:** All `docs/context-fabric/*.json` files

---

### 3. 🔬 **Phase 1: Per-Seam Discovery**

**Purpose:** Deep dive into each seam's technical analysis

#### Seam Selector
```
┌─────────────────────────────────────────────────────────────┐
│  SELECT SEAM:  [catalog-list ▼]                             │
└─────────────────────────────────────────────────────────────┘
```

#### Seam Overview Card
```
┌─────────────────────────────────────────────────────────────┐
│  CATALOG-LIST                                  Readiness: 95%│
│                                                               │
│  Purpose: Display paginated product catalog with filters     │
│                                                               │
│  Triggers:                                                    │
│    • Page Load → LoadCatalogData()                           │
│    • Filter Button → ApplyFilters()                          │
│    • Sort Column → SortCatalog()                             │
│                                                               │
│  Side Effects:                                                │
│    • Reads: products, categories, prices                     │
│    • Writes: None (read-only)                                │
│                                                               │
│  Dependencies:                                                │
│    → data-access (shared service)                            │
│    → None blocking                                           │
└─────────────────────────────────────────────────────────────┘
```

**Data Source:**
- `spec.md` → Purpose
- `discovery.md` → Triggers, side effects
- `evidence-map.json` → Call chains
- `readiness.json` → Readiness score

#### Call Chain Visualizer
```
┌─────────────────────────────────────────────────────────────┐
│  CALL CHAIN: LoadCatalogData()                              │
│                                                               │
│  UI Layer           Business Layer       Data Layer          │
│  ───────────────────────────────────────────────────────────│
│                                                               │
│  [Button Click]                                              │
│       │                                                       │
│       ├─→ LoadCatalogData()                                  │
│               │                                               │
│               ├─→ CatalogService.GetAll()                    │
│                       │                                       │
│                       ├─→ Repository.Query()                 │
│                               │                               │
│                               └─→ [Database]                 │
│                                                               │
│  🔵 In-Seam  🟡 Cross-Seam  🔴 External                     │
└─────────────────────────────────────────────────────────────┘
```

**Data Source:**
- `evidence-map.json` → flows[].call_path
- Color-code based on seam boundaries

#### Data Access Matrix
```
┌─────────────────────────────────────────────────────────────┐
│  DATA ACCESS PATTERNS                                        │
│                                                               │
│  Table/Entity       Read  Write  Query Patterns              │
│  ────────────────────────────────────────────────────────────│
│  products           ✅    ❌    SELECT * WHERE category_id   │
│  categories         ✅    ❌    SELECT * ORDER BY name       │
│  prices             ✅    ❌    JOIN with products           │
└─────────────────────────────────────────────────────────────┘
```

**Data Source:**
- `discovery.md` → Data access section
- `evidence-map.json` → side_effects[]

#### Boundary Issues Panel (if any)
```
┌─────────────────────────────────────────────────────────────┐
│  ⚠️ BOUNDARY ISSUES DETECTED                                 │
│                                                               │
│  Issue #1: Shared Data Access Component                      │
│    Problem: CatalogService called by 3 seams                 │
│    Recommendation: Extract to shared library                 │
│    Action: Accept / Ignore / Re-run discovery                │
│                                                               │
│  Issue #2: Uncovered Workflow                                │
│    Problem: "Export to Excel" button not in any seam        │
│    Recommendation: Add to catalog-list or create new seam    │
│    Action: Accept / Ignore / Re-run discovery                │
└─────────────────────────────────────────────────────────────┘
```

**Data Source:**
- `boundary-issues.json`

---

### 4. 🏗️ **Phase 2: Architecture**

**Purpose:** Show target architecture and design decisions

#### Architecture Overview
```
┌─────────────────────────────────────────────────────────────┐
│  TARGET ARCHITECTURE                                         │
│                                                               │
│  ┌─────────────┐                                            │
│  │   React UI  │  (TypeScript + Vite + TanStack Query)      │
│  └──────┬──────┘                                            │
│         │ REST/WebSocket                                     │
│  ┌──────▼──────┐                                            │
│  │  FastAPI    │  (Python 3.12 + async)                     │
│  └──────┬──────┘                                            │
│         │ SQLAlchemy                                         │
│  ┌──────▼──────┐                                            │
│  │ PostgreSQL  │  (+ Redis cache)                           │
│  └─────────────┘                                            │
└─────────────────────────────────────────────────────────────┘
```

**Data Source:**
- `architecture-design.md` → Parsed sections

#### Tech Stack Comparison
```
┌─────────────────────────────────────────────────────────────┐
│  LEGACY vs. MODERN STACK                                     │
│                                                               │
│  Layer          Legacy              Modern                   │
│  ────────────────────────────────────────────────────────────│
│  Frontend       WinForms            React 18 + TypeScript    │
│  Backend        .NET Framework      Python 3.12 + FastAPI    │
│  Database       SQL Server          PostgreSQL               │
│  Real-time      WCF Duplex          WebSockets               │
│  ORM            ADO.NET             SQLAlchemy 2.x           │
│  Validation     Manual              Pydantic + Zod           │
└─────────────────────────────────────────────────────────────┘
```

**Data Source:**
- `project-facts.json` → Legacy tech (detected)
- `architecture-design.md` → Modern tech (from CLAUDE.md)

#### Design Patterns Library
Interactive guide showing:
- **Contract-First API** (OpenAPI workflow)
- **Dependency Injection** (FastAPI Depends pattern)
- **Error Handling** (structured error responses)
- **WebSocket Streaming** (real-time updates)
- **Data Fetching** (TanStack Query patterns)

**Data Source:**
- `api-design-patterns.md`

---

### 5. 📝 **Phase 3: Specifications**

**Purpose:** Show requirements, design, tasks, contracts per seam

#### Seam Selector (same as Phase 1)

#### Requirements Viewer
```
┌─────────────────────────────────────────────────────────────┐
│  REQUIREMENTS (EARS Format)                                  │
│                                                               │
│  FR-01: Display Product List                                 │
│    WHEN user navigates to catalog page                       │
│    THEN system SHALL display products in grid format         │
│    WITH pagination (20 items per page)                       │
│                                                               │
│  FR-02: Filter Products                                      │
│    WHEN user selects category filter                         │
│    THEN system SHALL display only products in that category  │
│    WHERE results update within 500ms                         │
│                                                               │
│  [Show More...]                                              │
└─────────────────────────────────────────────────────────────┘
```

**Data Source:**
- `requirements.md` → Parsed EARS patterns

#### Design Components Diagram
```
┌─────────────────────────────────────────────────────────────┐
│  COMPONENT ARCHITECTURE                                      │
│                                                               │
│  Frontend Components:                                         │
│    • CatalogListPage                                         │
│      ├─→ CatalogFilters                                      │
│      ├─→ CatalogGrid                                         │
│      │   └─→ ProductCard (repeating)                         │
│      └─→ Pagination                                          │
│                                                               │
│  Backend Services:                                            │
│    • CatalogRouter                                           │
│      └─→ CatalogService                                      │
│          └─→ ProductRepository                               │
│                                                               │
│  Database:                                                    │
│    • products (table)                                        │
│    • categories (table)                                      │
└─────────────────────────────────────────────────────────────┘
```

**Data Source:**
- `design.md` → Component hierarchy section

#### Tasks Kanban Board
```
┌─────────────────────────────────────────────────────────────┐
│  IMPLEMENTATION TASKS                                        │
│                                                               │
│  TODO          IN PROGRESS        DONE                       │
│  ────────────  ───────────────   ──────────────────────────│
│  │ Task 3    │  │ Task 2      │  │ Task 1              ✅ ││
│  │ Setup DB  │  │ Impl. BE    │  │ Create OpenAPI      ✅ ││
│  │ schema    │  │ endpoints   │  │ spec                ✅ ││
│  └───────────┘  └─────────────┘  └─────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

**Data Source:**
- `tasks.md` → Parse checklist format

#### Contract (OpenAPI) Viewer
Interactive OpenAPI spec viewer:
- Endpoints list
- Request/response schemas
- Example payloads
- Try-it-out functionality

**Data Source:**
- `contracts/openapi.yaml` → Swagger UI component

---

### 6. 🗺️ **Phase 4: Roadmap**

**Purpose:** Show implementation plan, waves, priorities

#### Implementation Waves
```
┌─────────────────────────────────────────────────────────────┐
│  IMPLEMENTATION ROADMAP                                      │
│                                                               │
│  Wave 1 (Parallel - No Dependencies)         ✅ COMPLETE    │
│    • catalog-list                            ✅             │
│    • static-pages                            ✅             │
│    • user-profile                            ✅             │
│                                                               │
│  Wave 2 (Depends on Wave 1)                  🔵 IN PROGRESS │
│    • catalog-crud                            🔵             │
│    • orders-list                             🟡 Queued      │
│                                                               │
│  Wave 3 (Depends on Wave 2)                  ⏸️ NOT STARTED │
│    • orders-edit                             ⏸️             │
│    • reports-generator                       ⏸️             │
└─────────────────────────────────────────────────────────────┘
```

**Data Source:**
- `implementation-roadmap.md` → Parse waves

#### Dependency Flow
```
┌─────────────────────────────────────────────────────────────┐
│  CRITICAL PATH                                               │
│                                                               │
│  [data-access] ──→ [catalog-*] ──→ [orders-*] ──→ [reports]│
│       Day 1-2         Day 3-5         Day 6-8      Day 9-10 │
│                                                               │
│  Bottleneck: data-access (blocks 8 seams)                   │
└─────────────────────────────────────────────────────────────┘
```

**Data Source:**
- `dependency-graph.json` → Critical path analysis
- `implementation-roadmap.md` → Estimated durations

#### Priority Matrix
```
┌─────────────────────────────────────────────────────────────┐
│  PRIORITY: Business Value vs. Complexity                    │
│                                                               │
│  High Value │                                                │
│      │      │  [catalog-list]     [orders-edit]             │
│      │      │                                                │
│      │      │                     [reports-gen]             │
│      └──────┼──────────────────────────────────────────────→│
│  Low Value  │  [admin-config]     [data-export]             │
│             Low Complexity     High Complexity               │
└─────────────────────────────────────────────────────────────┘
```

**Data Source:**
- `seam-proposals.json` → Business value (manual or derived)
- `readiness.json` → Complexity estimate

---

### 7. 🔨 **Phase 5: Implementation**

**Purpose:** Track real-time implementation progress, code quality

#### Real-Time Progress
```
┌─────────────────────────────────────────────────────────────┐
│  CURRENT SPRINT: Wave 2                                      │
│                                                               │
│  Seam: catalog-crud                          Progress: 78%   │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━░░░░░░░     │
│                                                               │
│  Backend:   ✅ Routes  ✅ Service  🔵 Tests                  │
│  Frontend:  ✅ Pages   🔵 Hooks    ⏸️ E2E Tests              │
│                                                               │
│  Last Activity: 2 minutes ago — frontend-migration agent     │
└─────────────────────────────────────────────────────────────┘
```

**Data Source:**
- `tasks.md` → Track completion percentage
- `migration-state.json` → Last agent activity timestamp

#### Code Quality Dashboard
```
┌─────────────────────────────────────────────────────────────┐
│  CODE QUALITY METRICS                                        │
│                                                               │
│  Coverage          Tests Pass       Linting       Security   │
│  ──────────────    ──────────────   ────────────  ──────────│
│  Backend:  87% ✅  45/45 ✅         0 errors ✅   0 high ✅  │
│  Frontend: 82% ✅  38/40 🟡         2 warnings🟡  0 high ✅  │
└─────────────────────────────────────────────────────────────┘
```

**Data Source:**
- `test-results.json` → Parse pytest/vitest output
- Backend: `htmlcov/index.html` → Parse coverage
- Frontend: `coverage/coverage-summary.json`

#### Implementation Log (Live Feed)
```
┌─────────────────────────────────────────────────────────────┐
│  AGENT ACTIVITY LOG                                          │
│                                                               │
│  [14:32] backend-migration → Created CatalogService          │
│  [14:35] backend-migration → Generated CRUD endpoints        │
│  [14:38] backend-migration → Tests passed (12/12) ✅         │
│  [14:40] frontend-migration → Created CatalogCrudPage        │
│  [14:42] frontend-migration → Implemented form validation    │
│  [14:45] simplify → Refactored duplicate code                │
└─────────────────────────────────────────────────────────────┘
```

**Data Source:**
- `migration-state.json` → Agent execution log
- Parse agent output in real-time

#### File Changes Heatmap
```
┌─────────────────────────────────────────────────────────────┐
│  FILES MODIFIED (Last 24h)                                   │
│                                                               │
│  backend/app/catalog/router.py      ████████████ 124 lines  │
│  backend/app/catalog/service.py     ████████░░░░  86 lines  │
│  frontend/src/pages/catalog/...     ██████░░░░░░  62 lines  │
│  frontend/src/hooks/useCatalog.ts   ███░░░░░░░░░  31 lines  │
└─────────────────────────────────────────────────────────────┘
```

**Data Source:**
- Git log: `git log --stat --since="24 hours ago"`

---

### 8. ✅ **Phase 6: Validation**

**Purpose:** Security review + visual parity results

#### Security Review Dashboard
```
┌─────────────────────────────────────────────────────────────┐
│  SECURITY SCAN RESULTS                                       │
│                                                               │
│  Seam: catalog-crud                     Status: ✅ PASSED    │
│                                                               │
│  OWASP Top 10:                                               │
│    ✅ A01: Broken Access Control        No issues            │
│    ✅ A02: Cryptographic Failures       No issues            │
│    ✅ A03: Injection                    No issues            │
│    ✅ A04: Insecure Design              No issues            │
│    ✅ A05: Security Misconfiguration    No issues            │
│    🟡 A06: Vulnerable Components        2 warnings           │
│    ✅ A07: Auth Failures                No issues            │
│    ✅ A08: Software/Data Integrity      No issues            │
│    ✅ A09: Logging Failures             No issues            │
│    ✅ A10: SSRF                         No issues            │
│                                                               │
│  Dependency Scan:                                            │
│    🟡 2 medium vulnerabilities (non-critical)                │
│       • lodash 4.17.19 → Update to 4.17.21                  │
│       • axios 0.21.1 → Update to 1.6.0                      │
└─────────────────────────────────────────────────────────────┘
```

**Data Source:**
- `security-review.md` → OWASP findings
- `npm audit --json` / `pip-audit --json` → Dependency scan

#### Visual Parity Results
```
┌─────────────────────────────────────────────────────────────┐
│  VISUAL PARITY: catalog-crud                SSIM: 92% ✅     │
│                                                               │
│  Screenshot Comparisons:                                     │
│                                                               │
│  Screen              Legacy    Modern    SSIM    Status      │
│  ───────────────────────────────────────────────────────────│
│  List View           [img]    [img]     95%     ✅ Pass     │
│  Create Form         [img]    [img]     90%     ✅ Pass     │
│  Edit Form           [img]    [img]     88%     🟡 Warning  │
│  Delete Confirm      [img]    [img]     94%     ✅ Pass     │
│                                                               │
│  Issues:                                                     │
│    🟡 Edit Form: Button alignment off by 2px                │
└─────────────────────────────────────────────────────────────┘
```

**Data Source:**
- `parity-results/VERIFICATION_SUMMARY.md` → SSIM scores
- `docs/legacy-golden/{seam}/baselines/` → Screenshot thumbnails

#### Side-by-Side Comparison
```
┌─────────────────────────────────────────────────────────────┐
│  LEGACY                          MODERN                      │
│  ┌──────────────────┐           ┌──────────────────┐        │
│  │                  │           │                  │        │
│  │  [Legacy Image]  │           │  [Modern Image]  │        │
│  │                  │           │                  │        │
│  └──────────────────┘           └──────────────────┘        │
│                                                               │
│  Diff Overlay: [Show/Hide]  Zoom: [100%]                    │
└─────────────────────────────────────────────────────────────┘
```

**Data Source:**
- Screenshot files from baselines directories

---

### 9. 📊 **Analytics & Trends**

**Purpose:** Historical trends, velocity, forecasting

#### Migration Velocity
```
┌─────────────────────────────────────────────────────────────┐
│  VELOCITY OVER TIME                                          │
│                                                               │
│  Seams/Week │                                                │
│      4 │                                          ●           │
│      3 │                          ●       ●                  │
│      2 │           ●       ●                                 │
│      1 │    ●                                                │
│      0 └──────────────────────────────────────────────────→ │
│          Week 1   Week 2   Week 3   Week 4   Week 5         │
│                                                               │
│  Avg Velocity: 2.4 seams/week                               │
│  Forecast: 6 seams remaining = 2.5 weeks                    │
└─────────────────────────────────────────────────────────────┘
```

**Data Source:**
- `migration-state.json` → Completed seams with timestamps
- Calculate moving average

#### Quality Trends
```
┌─────────────────────────────────────────────────────────────┐
│  CODE QUALITY TRENDS                                         │
│                                                               │
│  Coverage %│                                                 │
│     90% │                                          ●──●      │
│     80% │                          ●──●──●                   │
│     70% │           ●──●                                     │
│     60% │    ●                                               │
│      0  └──────────────────────────────────────────────────→│
│          Seam 1  Seam 2  Seam 3  Seam 4  Seam 5  Seam 6    │
│                                                               │
│  Trend: Coverage improving (+15% since start) ✅             │
└─────────────────────────────────────────────────────────────┘
```

**Data Source:**
- `test-results.json` per seam → Historical coverage data

#### Effort Distribution
```
┌─────────────────────────────────────────────────────────────┐
│  TIME SPENT BY PHASE                                         │
│                                                               │
│  Phase 0: Discovery      ████░░░░░░ 22%  (3.2 days)         │
│  Phase 1: Per-Seam Disc. ██████████ 35%  (5.1 days)         │
│  Phase 2: Architecture   ██░░░░░░░░  8%  (1.2 days)         │
│  Phase 3: Specifications ████░░░░░░ 15%  (2.2 days)         │
│  Phase 4: Roadmap        █░░░░░░░░░  3%  (0.4 days)         │
│  Phase 5: Implementation ████████░░ 35%  (5.1 days)         │
│  Phase 6: Validation     ███░░░░░░░ 12%  (1.7 days)         │
└─────────────────────────────────────────────────────────────┘
```

**Data Source:**
- `migration-state.json` → Phase start/end timestamps

---

### 10. 🎨 **Artifacts Explorer**

**Purpose:** Browse all generated artifacts, download/export

#### Artifact Browser
```
┌─────────────────────────────────────────────────────────────┐
│  SEARCH ARTIFACTS: [____________] 🔍                         │
│                                                               │
│  Filter by:  [Phase ▼] [Seam ▼] [Type ▼]                   │
│                                                               │
│  📁 docs/                                                    │
│    📁 context-fabric/                                        │
│      📄 project-facts.json                    Download       │
│      📄 seam-proposals.json                   Download       │
│      📄 dependency-graph.json                 Download       │
│    📁 seams/                                                 │
│      📁 catalog-list/                                        │
│        📄 requirements.md                     View | Download│
│        📄 design.md                           View | Download│
│        📄 tasks.md                            View | Download│
│        📄 contracts/openapi.yaml              View | Download│
│      📁 catalog-crud/                                        │
│        ...                                                    │
└─────────────────────────────────────────────────────────────┘
```

**Data Source:**
- Filesystem scan of `docs/` directory

#### Bulk Export
```
┌─────────────────────────────────────────────────────────────┐
│  EXPORT MIGRATION PACKAGE                                    │
│                                                               │
│  ☑ All specifications (requirements, design, tasks)         │
│  ☑ All contracts (OpenAPI specs)                            │
│  ☑ All evidence (screenshots, test results)                 │
│  ☑ Executive summary                                         │
│                                                               │
│  Format: [ZIP ▼]  [Excel ▼]  [PDF ▼]                       │
│                                                               │
│  [Generate Package]                                          │
└─────────────────────────────────────────────────────────────┘
```

---

### 11. 🚨 **Issues & Blockers**

**Purpose:** Centralized issue tracking across all seams

#### Critical Blockers
```
┌─────────────────────────────────────────────────────────────┐
│  🔴 CRITICAL BLOCKERS                                        │
│                                                               │
│  Issue #1: Data Access Abstraction Missing                   │
│    Blocks: 8 seams (orders-*, reports-*, admin-*)           │
│    Owner: backend-migration agent                            │
│    Action: Create shared data-access library                 │
│    ETA: 2 days                                               │
│                                                               │
│  Issue #2: Authentication Service Not Implemented            │
│    Blocks: 5 seams (all user-facing pages)                  │
│    Owner: backend-migration agent                            │
│    Action: Implement JWT auth middleware                     │
│    ETA: 1 day                                                │
└─────────────────────────────────────────────────────────────┘
```

**Data Source:**
- Aggregate `boundary-issues.json` across all seams
- Parse `tasks.md` for blocked items

#### Warnings & Technical Debt
```
┌─────────────────────────────────────────────────────────────┐
│  🟡 WARNINGS                                                 │
│                                                               │
│  • catalog-crud: Test coverage below 80% (currently 72%)    │
│  • orders-list: 3 code smells (SonarQube)                   │
│  • reports-gen: Performance budget exceeded (220KB JS)       │
└─────────────────────────────────────────────────────────────┘
```

**Data Source:**
- `test-results.json` → Coverage warnings
- SonarQube API → Code smells
- Lighthouse results → Performance budget

---

## 🔄 Real-Time Updates

### Dashboard Refresh Strategies

#### Mode 1: File Watcher (Development)
```python
from watchdog.observers import Observer

# Watch docs/ directory for changes
observer = Observer()
observer.schedule(handler, path="docs/", recursive=True)
observer.start()

# On file change → update dashboard
```

#### Mode 2: Polling (Production)
```python
# Poll migration-state.json every 5 seconds
while True:
    state = load_state()
    update_dashboard(state)
    time.sleep(5)
```

#### Mode 3: WebSocket Push (Real-time)
```python
# Agent pushes updates via WebSocket
async def agent_completed(agent_name, seam, output):
    await websocket.send_json({
        "event": "agent_completed",
        "agent": agent_name,
        "seam": seam,
        "output": output
    })
```

---

## 🎯 Success Metrics (Dashboard KPIs)

### Overall Migration Health Score (0-100)

```python
def calculate_migration_health():
    # Phase completion (30%)
    phase_score = (completed_phases / 7) * 30

    # Seam readiness (40%)
    avg_readiness = mean([seam.readiness for seam in seams])
    seam_score = (avg_readiness / 100) * 40

    # Quality gates (20%)
    quality_score = (
        (coverage_pct / 100) * 0.5 +
        (tests_passing / total_tests) * 0.5
    ) * 20

    # Blockers penalty (10%)
    blocker_penalty = min(10, num_critical_blockers * 2)

    total = phase_score + seam_score + quality_score - blocker_penalty
    return round(total, 0)
```

### Key Metrics Tracked

1. **Progress Metrics**
   - Phases completed (0-7)
   - Seams completed vs. total
   - Tasks completed vs. total
   - Coverage percentage (0-100%)

2. **Quality Metrics**
   - Test coverage (backend + frontend)
   - SonarQube ratings (A-E)
   - Security vulnerabilities (critical/high/medium/low)
   - Visual parity SSIM scores (0-100%)

3. **Velocity Metrics**
   - Seams per week
   - Days per seam (average)
   - Forecast completion date

4. **Issue Metrics**
   - Critical blockers count
   - Warnings count
   - Boundary issues count
   - Technical debt estimate

---

## 🛠️ Technical Implementation

### Tech Stack

**Backend (Dashboard Server):**
- **Streamlit** — Dashboard framework
- **Python 3.12** — Backend logic
- **Pandas** — Data manipulation
- **Plotly** — Interactive charts
- **FastAPI** (optional) — REST API for programmatic access

**Frontend Components:**
- **Streamlit native** — UI framework
- **Plotly.js** — Charts
- **Cytoscape.js** — Dependency graphs
- **Swagger UI** — OpenAPI viewer
- **Diff2HTML** — Code diff visualization

**Data Storage:**
- **JSON files** — Primary data source (agent artifacts)
- **SQLite** (optional) — Cache for computed metrics
- **Redis** (optional) — Real-time updates

### File Structure

```
.claude/skills/migration-report-dashboard/
├── app/
│   ├── main.py                    # Streamlit app entry point
│   ├── pages/
│   │   ├── 01_overview.py         # Overview dashboard
│   │   ├── 02_phase_0.py          # Phase 0: Discovery
│   │   ├── 03_phase_1.py          # Phase 1: Per-Seam Discovery
│   │   ├── 04_phase_2.py          # Phase 2: Architecture
│   │   ├── 05_phase_3.py          # Phase 3: Specifications
│   │   ├── 06_phase_4.py          # Phase 4: Roadmap
│   │   ├── 07_phase_5.py          # Phase 5: Implementation
│   │   ├── 08_phase_6.py          # Phase 6: Validation
│   │   ├── 09_analytics.py        # Analytics & Trends
│   │   ├── 10_artifacts.py        # Artifacts Explorer
│   │   └── 11_issues.py           # Issues & Blockers
│   ├── lib/
│   │   ├── data_loader.py         # Load data from docs/
│   │   ├── metrics.py             # Compute metrics
│   │   ├── visualizations.py      # Chart generation
│   │   └── insights.py            # Automated insights engine
│   └── components/
│       ├── seam_card.py           # Reusable seam card component
│       ├── progress_bar.py        # Custom progress bar
│       └── dependency_graph.py    # D3.js dependency graph
├── collectors/                     # (Existing) Metric collectors
├── config.yaml                     # Dashboard configuration
├── requirements.txt                # Python dependencies
└── README.md                       # Usage guide
```

### Data Loading Pattern

```python
# app/lib/data_loader.py
import json
from pathlib import Path

class MigrationDataLoader:
    def __init__(self, docs_path="docs/"):
        self.docs_path = Path(docs_path)

    def load_seam_proposals(self):
        """Load all discovered seams."""
        path = self.docs_path / "context-fabric/seam-proposals.json"
        return json.loads(path.read_text())

    def load_seam_discovery(self, seam_name):
        """Load discovery report for a seam."""
        path = self.docs_path / f"seams/{seam_name}/discovery.md"
        return path.read_text()

    def load_seam_readiness(self, seam_name):
        """Load readiness score for a seam."""
        path = self.docs_path / f"seams/{seam_name}/readiness.json"
        return json.loads(path.read_text())

    # ... more loaders for all artifact types
```

### Real-Time Update Implementation

```python
# app/lib/realtime.py
import streamlit as st
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ArtifactWatcher(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith('.json') or event.src_path.endswith('.md'):
            # Trigger Streamlit rerun
            st.rerun()

# Start watcher
observer = Observer()
observer.schedule(ArtifactWatcher(), path="docs/", recursive=True)
observer.start()
```

---

## 📦 Deliverables

### Phase 1: Core Dashboard (Week 1)
- ✅ Overview dashboard (Home)
- ✅ Phase 0: Discovery Loop
- ✅ Phase 1: Per-Seam Discovery
- ✅ Data loading infrastructure
- ✅ Basic visualizations (charts, tables)

### Phase 2: Deep Dive Pages (Week 2)
- ✅ Phase 2: Architecture
- ✅ Phase 3: Specifications
- ✅ Phase 4: Roadmap
- ✅ Phase 5: Implementation
- ✅ Phase 6: Validation
- ✅ OpenAPI viewer integration

### Phase 3: Analytics & Insights (Week 3)
- ✅ Analytics & Trends page
- ✅ Automated insights engine
- ✅ Velocity forecasting
- ✅ Quality trends
- ✅ Effort distribution

### Phase 4: Polish & Export (Week 4)
- ✅ Artifacts Explorer
- ✅ Issues & Blockers centralized view
- ✅ Real-time updates (file watcher)
- ✅ Export to PDF/Excel/ZIP
- ✅ Mobile-responsive layout
- ✅ Dark mode support

---

## 🚀 Quick Start

### Installation

```bash
cd .claude/skills/migration-report-dashboard

# Install dependencies
pip install -r requirements.txt

# Verify data exists
ls docs/context-fabric/seam-proposals.json

# Launch dashboard
streamlit run app/main.py
```

### Usage

```bash
# Launch interactive dashboard
/migration-report-dashboard dashboard

# Open browser → http://localhost:8501

# Navigate through phases using sidebar
# Explore seams, view artifacts, track progress
```

---

## 🎨 Design Principles

1. **Data-Driven Storytelling:** Every visualization tells part of the migration story
2. **Real Artifacts Only:** No mock data — all visualizations use actual agent outputs
3. **Progressive Disclosure:** High-level overview → Drill down to details
4. **Action-Oriented:** Not just status — actionable insights and next steps
5. **Beautiful & Professional:** Enterprise-grade design, not prototype-quality
6. **Fast & Responsive:** Sub-second load times, smooth interactions

---

## 🎯 Success Criteria

Dashboard is production-ready when:
- ✅ All 11 pages implemented
- ✅ Real-time updates working
- ✅ All data sources integrated
- ✅ Export functionality complete
- ✅ Mobile-responsive
- ✅ No errors on page load
- ✅ Insights engine generates meaningful recommendations
- ✅ Stakeholders can understand migration status without technical knowledge

---

## 🔮 Future Enhancements

### Version 2.0
- **AI-Powered Insights:** Use Claude to analyze artifacts and generate recommendations
- **Predictive Analytics:** ML-based ETA forecasting
- **Collaboration Features:** Comments, approvals, notifications
- **Custom Reports:** Drag-and-drop report builder
- **Integration Plugins:** Jira, Slack, GitHub, GitLab

### Version 3.0
- **Multi-Project Support:** Track multiple migrations
- **Benchmark Library:** Compare against industry benchmarks
- **Cost Estimation:** Effort estimation based on historical data
- **Risk Heatmap:** Predictive risk analysis per seam

---

**END OF SPECIFICATION**

This dashboard transforms migration from a black box into a **transparent, data-driven, visually compelling narrative** that stakeholders can understand and teams can act upon. 🚀
