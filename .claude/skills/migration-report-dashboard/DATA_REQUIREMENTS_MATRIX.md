# 📊 Dashboard Data Requirements & Gap Analysis

**Comprehensive mapping of dashboard needs vs. agent outputs**

---

## 🎯 Overview

This document maps:
1. **What the dashboard needs** to display all 11 pages
2. **What agents currently produce** (available artifacts)
3. **What's missing** (gaps to fill)
4. **When it's needed** (which migration phase)

---

## 📋 Agent-by-Agent Output Inventory

### Agent 101: seam-discovery (Phase 0)

**Purpose:** Discover all seams from codebase + runtime

#### ✅ Currently Produces:
```
docs/context-fabric/
├── project-facts.json          # Framework, modules, entry points
├── manifest.json               # All files/modules inventory
├── database-schema.json        # Tables, FKs
├── seam-proposals.json         # All discovered seams
├── business-rules.json         # Extracted validation logic
├── static-assets-catalog.json  # Images/icons catalog
├── dependency-graph.json       # Inter-seam dependencies
└── design-system.json          # UI design tokens (colors, fonts)
```

#### ❌ Missing (Needed by Dashboard):
- **`coverage-audit.json`** — Per-module coverage breakdown
  - **Need:** Module name, file count, covered count, uncovered count, coverage %
  - **When:** Phase 0 (for coverage heatmap in Phase 0 dashboard page)
  - **✅ DATA SOURCE:** Derive from `manifest.json` + `seam-proposals.json`
    - `manifest.json` has all files per module
    - `seam-proposals.json` has which files are in seams
    - Dashboard calculates: `coverage_pct = (files_in_seams / total_files) * 100`
  - **Fix:** Dashboard parses existing files (no agent change needed)

- **`seam-proposals-history.json`** — Discovery iteration tracking
  - **Need:** Each iteration: timestamp, seams discovered, coverage %, changes
  - **When:** Phase 0 (for discovery timeline visualization)
  - **✅ DATA SOURCE:** Derive from `migration-activity.jsonl`
    - Hook logs `{"event":"agent_completed","agent":"seam-discovery","timestamp":"..."}`
    - Dashboard reads seam-proposals.json at each seam-discovery completion timestamp
    - Tracks iteration progression over time
  - **Fix:** Dashboard parses activity log + seam-proposals snapshots

- **`navigation-map.json`** — Menu structure, routes
  - **Need:** Menu hierarchy, screen names, routes, parent-child relationships
  - **When:** Phase 0 (for Context Fabric Explorer)
  - **Status:** Mentioned in spec but not confirmed in agent output

#### 📊 Dashboard Pages Using This Data:
- 🏠 **Overview:** Seam count, dependency graph summary
- 🔍 **Phase 0:** All outputs (discovery timeline, coverage heatmap, context fabric explorer, seam dependency graph)
- 🔬 **Phase 1:** Seam list, dependencies

---

### Agent 102: ui-inventory-extractor (Phase 0)

**Purpose:** Extract UI structure, controls, grids per seam

#### ✅ Currently Produces:
```
docs/seams/{seam}/
├── ui-behavior.md              # UI structure, controls, grids, actions
└── ui-behavior-assets.md       # Static assets per seam

docs/context-fabric/
├── design-system.json          # Global design tokens
└── navigation-map.json         # Menu structure
```

#### ❌ Missing (Needed by Dashboard):
- **Nothing major** — ui-behavior.md is comprehensive
- **Enhancement:** Structured JSON version of ui-behavior.md
  - **Need:** `ui-behavior.json` with structured screens, controls, actions (easier to parse than markdown)
  - **When:** Phase 1, Phase 3 (for component visualizations)
  - **Fix:** Optional — can parse markdown, but JSON would be faster

#### 📊 Dashboard Pages Using This Data:
- 🔍 **Phase 0:** Design system viewer
- 🔬 **Phase 1:** UI structure display
- 📝 **Phase 3:** Design components diagram

---

### Agent 103: golden-baseline-capture (Phase 0)

**Purpose:** Capture screenshots from running legacy app

#### ✅ Currently Produces:
```
docs/legacy-golden/
├── coverage-report.json        # Coverage %, uncovered screens
├── {seam}/
│   ├── BASELINE_INDEX.md       # Screenshot catalog
│   └── baselines/
│       ├── screen1.png
│       ├── screen2.png
│       └── ...
```

#### ❌ Missing (Needed by Dashboard):
- **`runtime-metrics.json`** — Performance metrics from legacy app
  - **Need:** Load times, response times, memory usage per screen
  - **When:** Phase 6 (for before/after performance comparison)
  - **Fix:** Capture during baseline screenshot process using browser perf API

- **`user-journey-recordings.json`** — User flow recordings
  - **Need:** Step-by-step user actions, timestamps, screenshots per step
  - **When:** Phase 6 (for workflow validation)
  - **Fix:** Optional — record user flows during baseline capture

#### 📊 Dashboard Pages Using This Data:
- 🔍 **Phase 0:** Coverage report, uncovered screens
- ✅ **Phase 6:** Visual parity (side-by-side screenshots)

---

### Agent 104: discovery (Phase 1)

**Purpose:** Per-seam technical analysis (call chains, data access)

#### ✅ Currently Produces:
```
docs/seams/{seam}/
├── discovery.md                # Technical analysis (narrative)
├── evidence-map.json           # Triggers, flows, boundaries
├── readiness.json              # Readiness score, blockers
└── boundary-issues.json        # Scope issues (if any)
```

#### ❌ Missing (Needed by Dashboard):
- **Structured call chain JSON** — Currently in evidence-map.json but needs enhancement
  - **Current:** `flows[].call_path` is array of {file, symbol}
  - **Need:** Add `layer` field: "UI" | "Business" | "Data" | "External"
  - **When:** Phase 1 (for call chain visualizer with color-coded layers)
  - **Fix:** Enhance evidence-map.json structure

- **Data access summary JSON** — Currently prose in discovery.md
  - **Need:** Structured `data-access.json`: table name, operation (read/write), query pattern
  - **When:** Phase 1 (for data access matrix table)
  - **Fix:** Extract from discovery.md into separate JSON

- **Complexity metrics** — Not currently tracked
  - **Need:** Cyclomatic complexity, LOC, file count per seam
  - **When:** Phase 1, Analytics (for complexity trends)
  - **Fix:** Add to readiness.json

#### 📊 Dashboard Pages Using This Data:
- 🏠 **Overview:** Readiness scores, blockers
- 🔬 **Phase 1:** All outputs (seam overview, call chains, data access, boundary issues)
- 🗺️ **Phase 4:** Readiness for prioritization
- 🚨 **Issues:** Boundary issues, blockers

---

### Agent 105: spec-agent (Phase 3)

**Purpose:** Generate requirements → design → tasks → contract

#### ✅ Currently Produces:
```
docs/seams/{seam}/
├── requirements.md             # EARS functional requirements
├── design.md                   # Components, APIs, data models
├── tasks.md                    # Implementation checklist
└── contracts/
    └── openapi.yaml            # API specification
```

#### ❌ Missing (Needed by Dashboard):
- **`requirements-stats.json`** — Requirements metadata
  - **Need:** Total requirements count, EARS pattern distribution, acceptance criteria count
  - **When:** Phase 3, Analytics (for requirements coverage trends)
  - **Fix:** Generate stats file after requirements.md created

- **`design-components.json`** — Structured component hierarchy
  - **Need:** Component tree with parent-child relationships (currently prose in design.md)
  - **When:** Phase 3 (for component architecture diagram)
  - **Fix:** Extract component tree from design.md section

- **`tasks-status.json`** — Task completion tracking (real-time)
  - **Need:** Task ID, title, status (todo/in_progress/done), assignee, timestamp
  - **When:** Phase 5 (for Kanban board with real-time updates)
  - **Fix:** Generate from tasks.md, update during implementation

- **`contract-summary.json`** — OpenAPI summary stats
  - **Need:** Endpoint count, request/response model count, breaking changes vs. legacy
  - **When:** Phase 3, Analytics (for API parity analysis)
  - **Fix:** Parse openapi.yaml and generate summary

#### 📊 Dashboard Pages Using This Data:
- 📝 **Phase 3:** All outputs (requirements viewer, design diagram, tasks Kanban, OpenAPI viewer)
- 🔨 **Phase 5:** Tasks status for Kanban board
- 📈 **Analytics:** Requirements trends

---

### Agent 107: backend-migration (Phase 5)

**Purpose:** Implement backend per seam (reads tasks.md, generates code)

#### ✅ Currently Produces:
```
backend/app/{seam}/
├── router.py
├── schemas.py
├── service.py
└── models.py

docs/seams/{seam}/
└── implementation-summary.md   # What was built
```

#### ❌ Missing (Needed by Dashboard):
- **`test-results.json`** — Test execution results
  - **Need:** Total tests, passed, failed, skipped, coverage %, duration
  - **When:** Phase 5 (for code quality dashboard)
  - **Fix:** Run pytest with JSON reporter, save output

- **`code-quality.json`** — Linting/formatting results
  - **Need:** Ruff errors/warnings, mypy type errors, complexity scores
  - **When:** Phase 5 (for code quality dashboard)
  - **Fix:** Run ruff/mypy, parse output to JSON

- **`implementation-log.json`** — Agent activity log
  - **Need:** Timestamp, action (e.g., "Created router.py"), status, duration
  - **When:** Phase 5 (for real-time agent activity feed)
  - **Fix:** Agent logs each action to structured JSON

- **`file-changes.json`** — Files modified during implementation
  - **Need:** File path, lines added/deleted, timestamp
  - **When:** Phase 5 (for file changes heatmap)
  - **Fix:** Parse git log after implementation

#### 📊 Dashboard Pages Using This Data:
- 🔨 **Phase 5:** All (real-time progress, code quality, activity log, file changes)
- 📈 **Analytics:** Quality trends over time

---

### Agent 108: frontend-migration (Phase 5)

**Purpose:** Implement frontend per seam (reads tasks.md, generates code)

#### ✅ Currently Produces:
```
frontend/src/pages/{seam}/
└── ...component files

docs/seams/{seam}/
└── implementation-summary.md   # What was built
```

#### ❌ Missing (Needed by Dashboard):
- **`test-results.json`** — Vitest results
  - **Need:** Same as backend (tests, coverage, duration)
  - **When:** Phase 5
  - **Fix:** Run vitest with JSON reporter

- **`lighthouse-results.json`** — Performance metrics
  - **Need:** Performance score, accessibility, best practices, SEO, LCP, FID, CLS
  - **When:** Phase 5, Phase 6 (for performance comparison)
  - **Fix:** Run Lighthouse during/after implementation

- **`bundle-analysis.json`** — Bundle size metrics
  - **Need:** Total size, per-route size, largest chunks
  - **When:** Phase 5, Analytics (for bundle size trends)
  - **Fix:** Run webpack-bundle-analyzer or vite-bundle-visualizer

- **`implementation-log.json`** — Same as backend
  - **When:** Phase 5
  - **Fix:** Agent logs actions

#### 📊 Dashboard Pages Using This Data:
- 🔨 **Phase 5:** Real-time progress, code quality
- ✅ **Phase 6:** Performance comparison
- 📈 **Analytics:** Performance trends

---

### Agent 109: code-security-reviewer (Phase 6)

**Purpose:** Security scan before code is pushed

#### ✅ Currently Produces:
```
docs/seams/{seam}/
└── security-review.md          # Security findings
```

#### ❌ Missing (Needed by Dashboard):
- **`security-review.json`** — Structured security scan results
  - **Need:** OWASP category, severity, issue count, vulnerabilities list
  - **When:** Phase 6 (for security dashboard)
  - **Fix:** Generate structured JSON version of security-review.md

- **`dependency-scan.json`** — npm audit / pip-audit results
  - **Need:** Package name, current version, vulnerable version, severity, fix available
  - **When:** Phase 6 (for dependency vulnerability table)
  - **Fix:** Run npm audit --json / pip-audit --json, save output

#### 📊 Dashboard Pages Using This Data:
- ✅ **Phase 6:** Security review dashboard
- 🚨 **Issues:** Security warnings

---

### Agent 110: parity-harness-generator (Phase 6)

**Purpose:** Visual parity verification (pixel-level comparison)

#### ✅ Currently Produces:
```
docs/seams/{seam}/parity-results/
└── VERIFICATION_SUMMARY.md     # SSIM scores, discrepancies
```

#### ❌ Missing (Needed by Dashboard):
- **`parity-results.json`** — Structured parity results
  - **Need:** Per-screen: screen name, legacy screenshot path, modern screenshot path, SSIM score, status (pass/warning/fail), discrepancies
  - **When:** Phase 6 (for visual parity results table)
  - **Fix:** Generate structured JSON alongside VERIFICATION_SUMMARY.md

- **`diff-screenshots/`** — Diff overlay images
  - **Need:** Highlighted difference overlays (red = different, green = same)
  - **When:** Phase 6 (for side-by-side comparison with diff overlay)
  - **Fix:** Generate diff images during parity verification

#### 📊 Dashboard Pages Using This Data:
- ✅ **Phase 6:** Visual parity results, side-by-side comparison

---

### Phase 2: Architecture (ONE-TIME)

**Purpose:** Extract architecture from CLAUDE.md

#### ✅ Currently Produces:
```
docs/
├── architecture-design.md      # Tech stack (from CLAUDE.md)
└── api-design-patterns.md      # API conventions (from CLAUDE.md)
```

#### ❌ Missing (Needed by Dashboard):
- **`architecture-diagram.json`** — Structured architecture data
  - **Need:** Layers (frontend, backend, database), tech stack per layer, connections
  - **When:** Phase 2 (for architecture diagram visualization)
  - **Fix:** Generate from architecture-design.md

- **`tech-stack-comparison.json`** — Legacy vs. Modern
  - **Need:** Layer name, legacy tech, modern tech, reason for change
  - **When:** Phase 2 (for tech stack comparison table)
  - **Fix:** Extract from project-facts.json + architecture-design.md

#### 📊 Dashboard Pages Using This Data:
- 🏗️ **Phase 2:** Architecture diagram, tech stack comparison

---

### Phase 4: Roadmap (ONE-TIME)

**Purpose:** Generate implementation plan, waves, priorities

#### ✅ Currently Produces:
```
docs/
└── implementation-roadmap.md   # Waves, priorities, dependencies
```

#### ❌ Missing (Needed by Dashboard):
- **`implementation-roadmap.json`** — Structured roadmap
  - **Need:** Waves (wave number, seams in wave, dependencies, estimated duration)
  - **When:** Phase 4 (for waves timeline, critical path diagram)
  - **Fix:** Generate structured JSON from markdown

- **`priority-matrix.json`** — Seam prioritization data
  - **Need:** Seam name, business value (1-10), complexity (1-10), risk level
  - **When:** Phase 4 (for priority matrix scatter plot)
  - **Fix:** Calculate from readiness.json + business input

- **`critical-path.json`** — Critical path analysis
  - **Need:** Dependency chain, estimated duration per seam, bottleneck identification
  - **When:** Phase 4 (for critical path visualization)
  - **Fix:** Analyze dependency-graph.json + roadmap

#### 📊 Dashboard Pages Using This Data:
- 🗺️ **Phase 4:** All (waves timeline, critical path, priority matrix)

---

### Global: migration-state.json (Tracked Throughout)

**Purpose:** Track overall migration state, agent execution, timestamps

#### ❌ Currently Missing (Needed by Dashboard):
```
docs/
└── migration-state.json        # CRITICAL: Real-time migration tracking
```

**Structure:**
```json
{
  "migration_id": "eshopmigration-2026-03-03",
  "start_date": "2026-03-01T10:00:00Z",
  "current_phase": 5,
  "current_seam": "catalog-crud",

  "phases": {
    "phase_0": {
      "status": "complete",
      "start_time": "2026-03-01T10:00:00Z",
      "end_time": "2026-03-02T09:00:00Z",
      "iterations": [
        {
          "iteration": 1,
          "timestamp": "2026-03-01T10:00:00Z",
          "seams_discovered": 12,
          "coverage_pct": 85
        },
        {
          "iteration": 2,
          "timestamp": "2026-03-01T14:30:00Z",
          "seams_discovered": 15,
          "coverage_pct": 100
        }
      ]
    },
    "phase_1": {
      "status": "in_progress",
      "start_time": "2026-03-02T09:30:00Z",
      "completed_seams": 12,
      "total_seams": 15
    }
    // ... other phases
  },

  "agent_activity_log": [
    {
      "timestamp": "2026-03-03T14:32:00Z",
      "agent": "backend-migration",
      "seam": "catalog-crud",
      "action": "Created CatalogService",
      "status": "success",
      "duration_ms": 1250
    },
    {
      "timestamp": "2026-03-03T14:35:00Z",
      "agent": "backend-migration",
      "seam": "catalog-crud",
      "action": "Generated CRUD endpoints",
      "status": "success",
      "duration_ms": 2100
    }
    // ... continuous log
  ],

  "seam_completion_history": [
    {
      "seam": "catalog-list",
      "completed_at": "2026-03-02T16:00:00Z",
      "readiness_score": 95,
      "duration_hours": 8.5
    }
    // ... per seam
  ],

  "metrics_snapshot": {
    "migration_health_score": 87,
    "overall_progress_pct": 75,
    "critical_blockers": 1,
    "warnings": 3,
    "last_updated": "2026-03-03T14:45:00Z"
  }
}
```

**When:** ALL PHASES (continuously updated)

**Used By:**
- 🏠 **Overview:** Health score, progress, start date, elapsed time
- 🔍 **Phase 0:** Discovery iterations timeline
- 🔨 **Phase 5:** Agent activity log (real-time feed)
- 📈 **Analytics:** All trend charts (velocity, quality over time)

**Fix:** Create migration-state.json manager:
- Initialize at migration start
- Update after each agent completes
- Append to agent_activity_log in real-time
- Track seam completion timestamps

---

## 📊 Data Requirements by Dashboard Page

### 🏠 Page 1: Overview Dashboard

**Required Data:**

| Data Point | Source File | Status | Missing? |
|------------|-------------|--------|----------|
| Migration health score | Calculated from readiness.json | ✅ Available | Need readiness.json per seam |
| Overall progress % | Calculated from phase completion | ✅ Available | - |
| Start date | **migration-state.json** | ❌ Missing | **Yes** |
| Elapsed time | **migration-state.json** | ❌ Missing | **Yes** |
| ETA forecast | Calculated from velocity | ⚠️ Partial | Need seam_completion_history |
| Phase progress % | Check file existence | ✅ Available | - |
| Seam status matrix | seam-proposals.json + readiness.json | ✅ Available | - |
| Critical blockers count | boundary-issues.json | ✅ Available | - |
| Key insights | Automated analysis | ✅ Can generate | - |

**Critical Missing:**
- **migration-state.json** (entire file)
- **seam_completion_history** (for velocity calculation)

---

### 🔍 Page 2: Phase 0 — Discovery Loop

**Required Data:**

| Data Point | Source File | Status | Missing? |
|------------|-------------|--------|----------|
| Discovery iterations timeline | **migration-state.json → phases.phase_0.iterations** | ❌ Missing | **Yes** |
| Seams discovered per iteration | Same as above | ❌ Missing | **Yes** |
| Coverage % per iteration | Same as above | ❌ Missing | **Yes** |
| Seam dependency graph | dependency-graph.json | ✅ Available | - |
| Coverage heatmap | **coverage-audit.json** | ❌ Missing | **Yes** |
| Project facts | project-facts.json | ✅ Available | - |
| Database schema | database-schema.json | ✅ Available | - |
| Business rules | business-rules.json | ✅ Available | - |
| Static assets | static-assets-catalog.json | ✅ Available | - |
| Design system | design-system.json | ✅ Available | - |

**Critical Missing:**
- **coverage-audit.json** (per-module coverage breakdown)
- **migration-state.json → phases.phase_0.iterations** (iteration tracking)

---

### 🔬 Page 3: Phase 1 — Per-Seam Discovery

**Required Data:**

| Data Point | Source File | Status | Missing? |
|------------|-------------|--------|----------|
| Seam list | seam-proposals.json | ✅ Available | - |
| Seam purpose | spec.md | ✅ Available | - |
| Triggers | discovery.md + evidence-map.json | ✅ Available | - |
| Call chain | evidence-map.json → flows[].call_path | ⚠️ Partial | Need layer annotations |
| Data access matrix | **data-access.json** | ❌ Missing | **Yes** (parse from discovery.md) |
| Readiness score | readiness.json | ✅ Available | - |
| Boundary issues | boundary-issues.json | ✅ Available | - |

**Critical Missing:**
- **data-access.json** (structured data access patterns)
- **Layer annotations** in call_path (UI/Business/Data/External)

---

### 🏗️ Page 4: Phase 2 — Architecture

**Required Data:**

| Data Point | Source File | Status | Missing? |
|------------|-------------|--------|----------|
| Architecture diagram | **architecture-diagram.json** | ❌ Missing | **Yes** (parse from architecture-design.md) |
| Tech stack comparison | **tech-stack-comparison.json** | ❌ Missing | **Yes** |
| Legacy tech | project-facts.json | ✅ Available | - |
| Modern tech | architecture-design.md | ✅ Available | - |
| Design patterns | api-design-patterns.md | ✅ Available | - |

**Critical Missing:**
- **architecture-diagram.json** (structured layers + connections)
- **tech-stack-comparison.json** (legacy vs. modern table)

---

### 📝 Page 5: Phase 3 — Specifications

**Required Data:**

| Data Point | Source File | Status | Missing? |
|------------|-------------|--------|----------|
| Requirements (EARS) | requirements.md | ✅ Available | - |
| Requirements stats | **requirements-stats.json** | ❌ Missing | **Yes** |
| Design components | design.md | ✅ Available | - |
| Component hierarchy | **design-components.json** | ❌ Missing | **Yes** (parse from design.md) |
| Tasks | tasks.md | ✅ Available | - |
| Task status | **tasks-status.json** | ❌ Missing | **Yes** |
| OpenAPI contract | contracts/openapi.yaml | ✅ Available | - |
| Contract summary | **contract-summary.json** | ❌ Missing | **Yes** |

**Critical Missing:**
- **tasks-status.json** (real-time task tracking for Kanban)
- **design-components.json** (component tree for diagram)

---

### 🗺️ Page 6: Phase 4 — Roadmap

**Required Data:**

| Data Point | Source File | Status | Missing? |
|------------|-------------|--------|----------|
| Implementation waves | implementation-roadmap.md | ✅ Available | - |
| Waves timeline | **implementation-roadmap.json** | ❌ Missing | **Yes** |
| Critical path | **critical-path.json** | ❌ Missing | **Yes** |
| Priority matrix | **priority-matrix.json** | ❌ Missing | **Yes** |
| Dependencies | dependency-graph.json | ✅ Available | - |

**Critical Missing:**
- **implementation-roadmap.json** (structured waves)
- **critical-path.json** (dependency chain analysis)
- **priority-matrix.json** (business value vs. complexity)

---

### 🔨 Page 7: Phase 5 — Implementation

**Required Data:**

| Data Point | Source File | Status | Missing? |
|------------|-------------|--------|----------|
| Real-time progress | **tasks-status.json** | ❌ Missing | **Yes** |
| Agent activity log | **migration-state.json → agent_activity_log** | ❌ Missing | **Yes** |
| Test results | **test-results.json** | ❌ Missing | **Yes** |
| Code coverage | test-results.json | ❌ Missing | **Yes** |
| Linting results | **code-quality.json** | ❌ Missing | **Yes** |
| File changes | **file-changes.json** | ❌ Missing | **Yes** |

**Critical Missing:**
- **ALL Phase 5 tracking files** (implementation logs, test results, quality metrics)

---

### ✅ Page 8: Phase 6 — Validation

**Required Data:**

| Data Point | Source File | Status | Missing? |
|------------|-------------|--------|----------|
| Security scan results | security-review.md | ✅ Available | - |
| OWASP checklist | **security-review.json** | ❌ Missing | **Yes** |
| Dependency vulnerabilities | **dependency-scan.json** | ❌ Missing | **Yes** |
| Visual parity results | VERIFICATION_SUMMARY.md | ✅ Available | - |
| SSIM scores per screen | **parity-results.json** | ❌ Missing | **Yes** |
| Legacy screenshots | docs/legacy-golden/{seam}/baselines/ | ✅ Available | - |
| Modern screenshots | (Need to capture after impl) | ⚠️ Runtime | Need capture process |
| Diff overlays | **diff-screenshots/** | ❌ Missing | **Yes** |
| Lighthouse scores | **lighthouse-results.json** | ❌ Missing | **Yes** |

**Critical Missing:**
- **security-review.json** (structured security data)
- **parity-results.json** (structured SSIM scores)
- **lighthouse-results.json** (performance metrics)

---

### 📈 Page 9: Analytics & Trends

**Required Data:**

| Data Point | Source File | Status | Missing? |
|------------|-------------|--------|----------|
| Velocity (seams/week) | **migration-state.json → seam_completion_history** | ❌ Missing | **Yes** |
| Quality trends | Historical test-results.json | ❌ Missing | **Yes** |
| Coverage trends | Historical test-results.json | ❌ Missing | **Yes** |
| Effort distribution | **migration-state.json → phases[].duration** | ❌ Missing | **Yes** |
| Forecast | Calculated from velocity | ⚠️ Depends | Need seam_completion_history |

**Critical Missing:**
- **Historical tracking** in migration-state.json
- **seam_completion_history** array

---

### 🎨 Page 10: Artifacts Explorer

**Required Data:**

| Data Point | Source File | Status | Missing? |
|------------|-------------|--------|----------|
| All docs/ files | File system scan | ✅ Available | - |
| Markdown rendering | Read file content | ✅ Available | - |
| JSON viewing | Read file content | ✅ Available | - |
| Download | File access | ✅ Available | - |

**No Missing Data** — All available via filesystem

---

### 🚨 Page 11: Issues & Blockers

**Required Data:**

| Data Point | Source File | Status | Missing? |
|------------|-------------|--------|----------|
| Critical blockers | boundary-issues.json | ✅ Available | - |
| Warnings | test-results.json, code-quality.json | ❌ Missing | **Yes** |
| Security issues | security-review.json | ❌ Missing | **Yes** |
| Tech debt | SonarQube API (external) | ⚠️ External | Optional |

**Critical Missing:**
- **Structured quality/security JSON files** for warnings aggregation

---

## 🎯 Priority Gap Analysis

### 🔴 Critical Gaps (Block Core Functionality)

| Missing File | Needed By | Impact if Missing | Fix Priority |
|--------------|-----------|-------------------|--------------|
| **migration-state.json** | Overview, Phase 0, Phase 5, Analytics | No real-time tracking, no timeline, no agent log, no velocity | **P0 — CRITICAL** |
| **tasks-status.json** | Phase 3, Phase 5 | No Kanban board, no real-time progress | **P0 — CRITICAL** |
| **test-results.json** | Phase 5, Analytics | No code quality dashboard | **P0 — CRITICAL** |
| **parity-results.json** | Phase 6 | No visual parity validation | **P0 — CRITICAL** |

---

### 🟡 High-Priority Gaps (Degrade UX)

| Missing File | Needed By | Impact if Missing | Fix Priority |
|--------------|-----------|-------------------|--------------|
| **coverage-audit.json** | Phase 0 | No coverage heatmap | **P1 — High** |
| **data-access.json** | Phase 1 | No data access matrix (can parse from markdown) | **P1 — High** |
| **implementation-roadmap.json** | Phase 4 | No waves timeline visualization | **P1 — High** |
| **security-review.json** | Phase 6, Issues | No security dashboard | **P1 — High** |
| **code-quality.json** | Phase 5, Issues | No linting/quality metrics | **P1 — High** |

---

### 🟢 Nice-to-Have Gaps (Enhance Features)

| Missing File | Needed By | Impact if Missing | Fix Priority |
|--------------|-----------|-------------------|--------------|
| **architecture-diagram.json** | Phase 2 | No architecture diagram (can parse from markdown) | **P2 — Medium** |
| **requirements-stats.json** | Phase 3, Analytics | No requirements trends | **P2 — Medium** |
| **design-components.json** | Phase 3 | No component diagram (can parse from markdown) | **P2 — Medium** |
| **lighthouse-results.json** | Phase 6 | No performance comparison | **P2 — Medium** |
| **runtime-metrics.json** | Phase 6 | No legacy performance baseline | **P3 — Low** |

---

## 🛠️ Implementation Recommendations

### Phase 1: Fix Critical Gaps (Week 1)

**1. Create `migration-state.json` Manager**
```python
# New file: .claude/scripts/migration_state_manager.py
class MigrationStateManager:
    def initialize_migration(migration_id, start_date):
        """Create migration-state.json at start"""
        pass

    def log_agent_activity(agent, seam, action, status, duration):
        """Append to agent_activity_log"""
        pass

    def complete_seam(seam, readiness_score, duration_hours):
        """Update seam_completion_history"""
        pass

    def update_phase_status(phase, status):
        """Update phase status"""
        pass
```

**Integration Points:**
- Call `log_agent_activity()` from each agent (backend-migration, frontend-migration, etc.)
- Call `complete_seam()` at end of Phase 6 per seam
- Call `update_phase_status()` at phase transitions

---

**2. Generate `test-results.json`**
```bash
# Backend
pytest --json-report --json-report-file=docs/seams/{seam}/test-results.json

# Frontend
vitest --reporter=json --outputFile=docs/seams/{seam}/test-results.json
```

**Integration:** backend-migration and frontend-migration agents run tests and save JSON output

---

**3. Generate `tasks-status.json`**
```python
# Parse tasks.md checklist
def parse_tasks_md(tasks_md_path):
    """
    Parse tasks.md checklist format:
    - [ ] Task 1
    - [x] Task 2

    Generate tasks-status.json:
    {
      "tasks": [
        {"id": 1, "title": "Task 1", "status": "todo"},
        {"id": 2, "title": "Task 2", "status": "done"}
      ]
    }
    """
    pass
```

**Integration:** spec-agent generates initial tasks-status.json, implementation agents update it

---

**4. Generate `parity-results.json`**
```python
# parity-harness-generator agent output
{
  "seam": "catalog-crud",
  "overall_ssim": 92.3,
  "screens": [
    {
      "screen_name": "list_view",
      "legacy_screenshot": "docs/legacy-golden/catalog-crud/baselines/list_view.png",
      "modern_screenshot": "docs/modern-screenshots/catalog-crud/list_view.png",
      "ssim_score": 95.2,
      "status": "pass",
      "discrepancies": []
    }
  ]
}
```

**Integration:** parity-harness-generator agent writes JSON output alongside VERIFICATION_SUMMARY.md

---

### Phase 2: Fix High-Priority Gaps (Week 2)

**1. Generate `coverage-audit.json`**
```python
# seam-discovery agent enhancement
{
  "modules": [
    {
      "module_name": "UI/Forms",
      "total_files": 45,
      "covered_files": 45,
      "uncovered_files": 0,
      "coverage_pct": 100
    },
    {
      "module_name": "Services",
      "total_files": 23,
      "covered_files": 22,
      "uncovered_files": 1,
      "coverage_pct": 96
    }
  ]
}
```

---

**2. Generate `data-access.json`**
```python
# discovery agent enhancement
{
  "seam": "catalog-list",
  "data_access": [
    {
      "table": "products",
      "operations": ["read"],
      "query_pattern": "SELECT * WHERE category_id = ?",
      "frequency": "high"
    }
  ]
}
```

---

**3. Generate `implementation-roadmap.json`**
```python
# Roadmap generator enhancement
{
  "waves": [
    {
      "wave_number": 1,
      "seams": ["catalog-list", "static-pages"],
      "dependencies": [],
      "estimated_duration_days": 5,
      "status": "complete"
    }
  ]
}
```

---

**4. Generate `security-review.json` & `code-quality.json`**
```python
# code-security-reviewer agent enhancement
# Output structured JSON alongside markdown
```

---

### Phase 3: Nice-to-Have Enhancements (Week 3)

- Parse markdown files to generate JSON versions
- Add Lighthouse integration
- Add SonarQube integration (optional, external)

---

## 📋 Summary Table: All Required Files

| File | Status | Priority | Agent | When Generated |
|------|--------|----------|-------|----------------|
| **migration-state.json** | ❌ Missing | P0 | orchestrator | Throughout |
| **tasks-status.json** | ❌ Missing | P0 | spec-agent + impl agents | Phase 3 + 5 |
| **test-results.json** | ❌ Missing | P0 | backend/frontend-migration | Phase 5 |
| **parity-results.json** | ❌ Missing | P0 | parity-harness-generator | Phase 6 |
| **coverage-audit.json** | ❌ Missing | P1 | seam-discovery | Phase 0 |
| **data-access.json** | ❌ Missing | P1 | discovery | Phase 1 |
| **implementation-roadmap.json** | ❌ Missing | P1 | roadmap generator | Phase 4 |
| **security-review.json** | ❌ Missing | P1 | code-security-reviewer | Phase 6 |
| **code-quality.json** | ❌ Missing | P1 | backend/frontend-migration | Phase 5 |
| **architecture-diagram.json** | ❌ Missing | P2 | Phase 2 generator | Phase 2 |
| **requirements-stats.json** | ❌ Missing | P2 | spec-agent | Phase 3 |
| **design-components.json** | ❌ Missing | P2 | spec-agent | Phase 3 |
| **lighthouse-results.json** | ❌ Missing | P2 | frontend-migration | Phase 5/6 |
| seam-proposals.json | ✅ Available | - | seam-discovery | Phase 0 |
| project-facts.json | ✅ Available | - | seam-discovery | Phase 0 |
| discovery.md | ✅ Available | - | discovery | Phase 1 |
| requirements.md | ✅ Available | - | spec-agent | Phase 3 |
| design.md | ✅ Available | - | spec-agent | Phase 3 |
| tasks.md | ✅ Available | - | spec-agent | Phase 3 |
| contracts/openapi.yaml | ✅ Available | - | spec-agent | Phase 3 |
| security-review.md | ✅ Available | - | code-security-reviewer | Phase 6 |
| VERIFICATION_SUMMARY.md | ✅ Available | - | parity-harness-generator | Phase 6 |

**Total Files Needed:** 30+
**Currently Available:** 15
**Missing Critical (P0):** 4
**Missing High (P1):** 5
**Missing Medium/Low (P2-P3):** 4

---

## 🎯 Action Items

### For Dashboard Implementation:
1. ✅ **Can start NOW:** Pages that only need existing files (Phase 2, Phase 3 base, Artifacts)
2. ⏸️ **Wait for P0 fixes:** Overview, Phase 0 timeline, Phase 5, Analytics
3. 🔄 **Workaround available:** Parse markdown for missing JSON (Phase 1, Phase 4)

### For Agent Enhancement:
1. **Week 1:** Add P0 critical outputs (migration-state.json, tasks-status.json, test-results.json, parity-results.json)
2. **Week 2:** Add P1 high-priority outputs (structured JSON for existing markdown reports)
3. **Week 3:** Add P2 nice-to-have outputs (performance metrics, trends)

---

**Ready to prioritize and implement the missing artifacts!** 🚀

---

## 🗺️ Data Source Reference (For Agent Updates)

**Use this table when updating agent instructions or creating hooks.**

| Data File | Data Source | How Generated | When Available |
|-----------|-------------|---------------|----------------|
| **migration-activity.jsonl** | ✅ **Hooks** (SubagentStart/Stop) | `.claude/hooks/log-agent-*.sh` | Throughout migration |
| **tasks-status.json** | ⚠️ **Parse tasks.md** | Dashboard parses `docs/seams/{seam}/tasks.md` directly | After Phase 3 |
| **test-results-backend.json** | ✅ **Hook** (SubagentStop) | `.claude/hooks/capture-quality-metrics.sh` runs pytest | After backend impl |
| **test-results-frontend.json** | ✅ **Hook** (SubagentStop) | `.claude/hooks/capture-quality-metrics.sh` runs vitest | After frontend impl |
| **coverage-backend.json** | ✅ **Hook** (SubagentStop) | `.claude/hooks/capture-quality-metrics.sh` runs pytest --cov | After backend impl |
| **coverage-frontend.json** | ✅ **Hook** (SubagentStop) | `.claude/hooks/capture-quality-metrics.sh` runs coverage | After frontend impl |
| **parity-results.json** | ⚠️ **Parse VERIFICATION_SUMMARY.md** | Dashboard parses `docs/legacy-golden/parity-results/{seam}/VERIFICATION_SUMMARY.md` | After Phase 6 |
| **requirements-stats.json** | ⚠️ **Parse requirements.md** | Dashboard counts EARS patterns in `docs/seams/{seam}/requirements.md` | After Phase 3 |
| **design-components.json** | ⚠️ **Parse design.md** | Dashboard extracts components from `docs/seams/{seam}/design.md` Section 3 | After Phase 3 |
| **contract-summary.json** | ⚠️ **Parse openapi.yaml** | Dashboard analyzes `docs/seams/{seam}/contracts/openapi.yaml` | After Phase 3 |
| **data-access.json** | ⚠️ **Parse discovery.md** | Dashboard extracts from `docs/seams/{seam}/discovery.md` | After Phase 1 |
| **security-review.json** | ⚠️ **Parse security-review.md** | Dashboard parses `docs/seams/{seam}/security-review.md` | After Phase 6 |
| **code-quality.json** | ✅ **Hook** (SubagentStop) | `.claude/hooks/capture-quality-metrics.sh` runs ruff/mypy | After impl |
| **implementation-roadmap.json** | ⚠️ **Parse implementation-roadmap.md** | Dashboard parses `docs/implementation-roadmap.md` | After Phase 4 |
| **coverage-audit.json** | ⚠️ **Derive from manifest.json + seam-proposals.json** | Dashboard calculates per-module coverage | Phase 0 |
| **architecture-diagram.json** | ⚠️ **Parse CLAUDE.md + architecture-design.md** | Dashboard extracts layers/tech stack | Available always |

---

## 🎯 Implementation Strategy

### ✅ Hooks Capture Real-time Data (Preferred)
**What:** Test results, coverage, code quality (ruff, mypy, eslint)
**How:** SubagentStop hook runs quality tools after agent completes
**Location:** `.claude/hooks/capture-quality-metrics.sh`

### ⚠️ Dashboard Parses Source Files (No Duplication)
**What:** Tasks, requirements, design components, contracts, parity
**Why:** Source markdown/YAML files already exist — don't duplicate
**How:** Dashboard reads and parses on-demand

### ❌ Agent Generates Only When Necessary
**What:** coverage-audit.json (Phase 0 only)
**Why:** No source file to parse, aggregated data needed
**How:** Agent 101 tracks module coverage during discovery

---

## 📋 Dashboard Data Derivation Guide

**How to calculate missing data from existing files:**

### Coverage Audit (Per-Module Coverage)

**Source Files:**
- `docs/context-fabric/manifest.json` - all files per module
- `docs/context-fabric/seam-proposals.json` - files mapped to seams

**Calculation:**
```python
def calculate_coverage_audit(manifest, seams):
    coverage = []
    for module in manifest['modules']:
        total_files = len(module['files'])
        covered_files = 0

        for file in module['files']:
            if file_in_any_seam(file, seams):
                covered_files += 1

        coverage.append({
            "module_name": module['name'],
            "total_files": total_files,
            "covered_files": covered_files,
            "uncovered_files": total_files - covered_files,
            "coverage_pct": (covered_files / total_files) * 100
        })
    return coverage
```

---

### Discovery Iterations Timeline

**Source Files:**
- `docs/tracking/migration-activity.jsonl` - agent completion events
- `docs/context-fabric/seam-proposals.json` - seam list

**Calculation:**
```python
def get_discovery_iterations(activity_log):
    iterations = []
    for event in activity_log:
        if event['agent'] == 'seam-discovery' and event['event'] == 'agent_completed':
            # Read seam-proposals.json state at this timestamp
            seams = load_seams_at_timestamp(event['timestamp'])
            iterations.append({
                "iteration": len(iterations) + 1,
                "timestamp": event['timestamp'],
                "seams_discovered": len(seams),
                "coverage_pct": calculate_coverage(seams)
            })
    return iterations
```

---

### Task Status (Real-time Progress)

**Source Files:**
- `docs/seams/{seam}/tasks.md` - checklist with `- [ ]` and `- [x]`

**Calculation:**
```python
def parse_task_status(tasks_md):
    lines = tasks_md.split('\n')
    tasks = []
    current_phase = None

    for line in lines:
        if line.startswith('## '):
            current_phase = extract_phase(line)  # Backend/Frontend/Testing
        elif line.startswith('- ['):
            status = 'done' if '[x]' in line else 'todo'
            title = line.split(']', 1)[1].strip()
            tasks.append({
                "id": f"T{len(tasks)+1}",
                "title": title,
                "status": status,
                "phase": current_phase
            })

    return {
        "total_tasks": len(tasks),
        "completed": sum(1 for t in tasks if t['status'] == 'done'),
        "todo": sum(1 for t in tasks if t['status'] == 'todo'),
        "tasks": tasks
    }
```

---

### Requirements Stats

**Source Files:**
- `docs/seams/{seam}/requirements.md` - EARS patterns

**Calculation:**
```python
def count_ears_patterns(requirements_md):
    patterns = {
        "ubiquitous": len(re.findall(r'\*\*Ubiquitous\*\*', requirements_md)),
        "event_driven": len(re.findall(r'\*\*Event-Driven\*\*', requirements_md)),
        "unwanted": len(re.findall(r'\*\*Unwanted\*\*', requirements_md)),
        "state_driven": len(re.findall(r'\*\*State-Driven\*\*', requirements_md)),
        "optional": len(re.findall(r'\*\*Optional\*\*', requirements_md)),
        "complex": len(re.findall(r'\*\*Complex\*\*', requirements_md))
    }
    return {
        "total_requirements": sum(patterns.values()),
        "ears_distribution": patterns
    }
```

---

### Design Components Tree

**Source Files:**
- `docs/seams/{seam}/design.md` - Section 3: Component Architecture

**Calculation:**
```python
def extract_component_tree(design_md):
    # Parse markdown section "## 3. Component Architecture"
    section = extract_section(design_md, "3. Component Architecture")

    # Extract component hierarchy from markdown structure
    components = []
    for line in section.split('\n'):
        if line.startswith('### '):
            components.append({
                "name": line.replace('###', '').strip(),
                "type": "page",
                "children": []
            })
        elif line.startswith('- **'):
            component_name = extract_component_name(line)
            components[-1]['children'].append({
                "name": component_name,
                "type": "component"
            })

    return components
```

---

### Contract Summary

**Source Files:**
- `docs/seams/{seam}/contracts/openapi.yaml`

**Calculation:**
```python
import yaml

def summarize_contract(openapi_path):
    spec = yaml.safe_load(open(openapi_path))

    return {
        "endpoint_count": len(spec.get('paths', {})),
        "schema_count": len(spec.get('components', {}).get('schemas', {})),
        "methods": {
            "GET": count_methods(spec, 'get'),
            "POST": count_methods(spec, 'post'),
            "PUT": count_methods(spec, 'put'),
            "DELETE": count_methods(spec, 'delete')
        }
    }
```

---

## 📋 Dashboard Implementation Checklist

When building dashboard pages:

1. **Check if source file exists first**
   - ✅ tasks.md → Parse directly (see derivation guide above)
   - ✅ requirements.md → Count EARS patterns (see guide)
   - ✅ design.md → Extract components (see guide)
   - ✅ openapi.yaml → Count endpoints (see guide)

2. **Use hook-generated data if available**
   - ✅ test-results-*.json (from hooks)
   - ✅ coverage-*.json (from hooks)
   - ✅ code-quality.json (from hooks)

3. **Derive from multiple sources if needed**
   - ✅ coverage-audit (manifest + seams)
   - ✅ discovery iterations (activity log + seams)
   - ✅ task status (parse tasks.md)

---

## 🔄 Update Process for Agents

**If you need to add data capture:**

1. **First:** Can dashboard parse an existing file? → YES: Add parsing logic to dashboard
2. **Second:** Can a hook capture it automatically? → YES: Add to `.claude/hooks/capture-quality-metrics.sh`
3. **Last resort:** Must agent generate it? → Add to agent instructions (avoid duplication)

**Example:**
- ❌ Don't make agent 105 generate tasks-status.json → Dashboard parses tasks.md
- ✅ Let hook capture test results → Hook runs pytest/vitest after agent completes
- ✅ Let agent 101 generate coverage-audit.json → No source file exists, aggregation needed
