# Agent Responsibilities & Execution Flow

---

## Quick Execution Sequence

The complete order in which agents are run, from a cold start to a fully migrated seam:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 STEP 1  legacy-context-fabric          [ONE-TIME]
         Run once per codebase. Self-discovers the .sln,
         inventories every type, proposes seams, writes spec stubs.
         Output: docs/context-fabric/  +  docs/seams/*/spec.md

 STEP 2  ui-behavior-extractor          [ONE-TIME]
         Reads manifest.json, extracts screen layouts from
         Designer.cs / XAML, writes per-seam ui-behavior.md.
         Output: docs/seams/*/ui-behavior.md  +  visual-controls-catalog.md

 STEP 3  architecture-bootstrap         [ONE-TIME]
         Generates backend/ and frontend/ project skeletons.
         Output: backend/  +  frontend/

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 Repeat steps 4–12 for each seam (run-seam-migration
 skill orchestrates them automatically).
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

 STEP 4  golden-baseline-capture        [OPTIONAL, per seam]
         ⚠️ Must run FIRST in per-seam pipeline (capture legacy system
         while still available). Requires Windows machine with legacy app.
         Output: legacy-golden/{seam}/

 STEP 5  runtime-surface-capture        [OPTIONAL, per seam]
         Observes API/network from running system (any environment).
         Helps inform contract design with real API shapes.
         Output: docs/seams/{seam}/runtime/

 STEP 6  discovery                      [per seam]
         Deep-dives the seam boundary — entry points,
         dependencies, business logic, test scenarios.
         Output: docs/seams/{seam}/discovery.md

 STEP 7  contract-generator             [per seam]
         Designs the OpenAPI contract from discovery output.
         Output: docs/seams/{seam}/contracts/openapi.yaml  +  docs/seams/{seam}/dto-mapping.md

 STEP 8  data-strategy                  [ALWAYS, per seam]
         Chooses DB access strategy; generates SQLAlchemy models.
         Output: docs/seams/{seam}/data-strategy.md

 STEP 9  dependency-wrapper-generator   [CONDITIONAL, per seam]
         Only if discovery flagged COM / serial / Windows-API deps.
         Output: backend/app/adapters/  +  docs/seams/{seam}/hard-dependencies.md

 STEP 10 backend-migration  ┐           [per seam, run in parallel]
 STEP 11 frontend-migration ┘
         Backend: FastAPI routes, services, Pydantic models, unit tests.
         Frontend: React pages, components, hooks, component tests.
         Output: backend/app/{seam}/  +  frontend/src/pages/{seam}/

 STEP 12 parity-harness-generator       [OPTIONAL, per seam]
         Only if legacy-golden/{seam}/BASELINE_INDEX.md exists.
         Output: backend/tests/parity/  +  frontend/tests/e2e/parity/

         → Run all tests → write docs/seams/{seam}/evidence/evidence.md
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### What is optional vs mandatory

| Step | Agent | Mandatory? | Condition |
|------|-------|-----------|-----------|
| 1 | legacy-context-fabric | **Yes** | Always (one-time) |
| 2 | ui-behavior-extractor | **Yes** | Always (one-time) — without it, frontend-migration invents UI |
| 3 | architecture-bootstrap | **Yes** | Once, before first seam |
| 4 | golden-baseline-capture | Optional | Requires live running legacy system; run FIRST in per-seam pipeline |
| 5 | runtime-surface-capture | Optional | Requires running system (any environment); helps contract design |
| 6 | discovery | **Yes** | Every seam |
| 7 | contract-generator | **Yes** | Every seam |
| 8 | data-strategy | **Yes** | Every seam |
| 9 | dependency-wrapper-generator | Conditional | Only if External deps found in step 6 |
| 10 | backend-migration | **Yes** | Every seam |
| 11 | frontend-migration | **Yes** | Every seam |
| 12 | parity-harness-generator | Optional | Only if golden baselines captured in step 4 |

---

## Agent Ecosystem Overview

```
Phase 0: UNDERSTAND (Pre-Migration, One-Time)
├── 1. legacy-context-fabric      — Builds KB; proposes seams; generates spec stubs
└── 2. ui-behavior-extractor      — Extracts screen layouts from Designer.cs + XAML

Phase 0.5: BOOTSTRAP (One-Time, Before First Seam)
└── 3. architecture-bootstrap     — Generates backend/ + frontend/ project skeletons

Per-Seam Pipeline (run-seam-migration orchestrates):
├── 4. golden-baseline-capture    — Captures live screenshots/exports/DB snapshots (optional, run FIRST)
├── 5. runtime-surface-capture    — Observes API/network from running system (optional)
├── 6. discovery                  — Maps seam boundaries and dependencies
├── 7. contract-generator         — Creates OpenAPI contract
├── 8. data-strategy              — Documents DB access, generates SQLAlchemy models
├── 9. dependency-wrapper-generator — Abstracts hard deps (conditional)
├── 10. backend-migration         — Implements Python/FastAPI seam
├── 11. frontend-migration        — Implements React/TypeScript seam
└── 12. parity-harness-generator  — Generates parity tests (conditional)

Orchestration:
└── run-seam-migration (skill)    — Drives steps 4–12 with gate enforcement
```

---

## Artifact Flow Diagram

```
legacy-context-fabric
  ├─→ docs/context-fabric/manifest.json ──────────────→ ui-behavior-extractor
  ├─→ docs/context-fabric/project-facts.json ─────────→ architecture-bootstrap
  ├─→ docs/context-fabric/seam-proposals.json ────────→ ui-behavior-extractor
  ├─→ docs/context-fabric/business-rules.json ────────→ contract-generator
  ├─→ docs/context-fabric/index.json ─────────────────→ discovery
  └─→ docs/seams/*/spec.md ───────────────────────────→ golden-baseline-capture, runtime-surface-capture, discovery

ui-behavior-extractor
  ├─→ docs/seams/*/ui-behavior.md ────────────────────→ runtime-surface-capture, frontend-migration
  └─→ docs/context-fabric/visual-controls-catalog.md ─→ frontend-migration

architecture-bootstrap
  └─→ backend/ + frontend/ skeletons ──────────────────→ backend-migration, frontend-migration

golden-baseline-capture (optional, per seam)
  └─→ legacy-golden/{seam}/ ───────────────────────────→ parity-harness-generator

runtime-surface-capture (optional, per seam)
  └─→ docs/seams/{seam}/runtime/ ──────────────────────→ contract-generator

discovery
  └─→ docs/seams/{seam}/discovery.md ───────────────────→ contract-generator
                                                           data-strategy
                                                           dependency-wrapper-generator

contract-generator
  └─→ docs/seams/{seam}/contracts/openapi.yaml ─────────→ backend-migration, frontend-migration
      docs/seams/{seam}/dto-mapping.md

data-strategy
  └─→ docs/seams/{seam}/data-strategy.md ───────────────→ backend-migration

dependency-wrapper-generator (conditional)
  └─→ backend/app/adapters/ ────────────────────────────→ backend-migration

backend-migration + frontend-migration
  └─→ backend/app/{seam}/ + frontend/src/pages/{seam}/ → parity-harness-generator

parity-harness-generator (optional)
  └─→ tests/parity/ → user runs → docs/seams/{seam}/evidence/evidence.md
```

---

## Detailed Agent Responsibilities

### 1. legacy-context-fabric

**Phase:** 0 — UNDERSTAND (one-time per codebase)
**Input:** Nothing — self-discovers by searching for `.sln` files
**Output:**
- `docs/context-fabric/manifest.json` — exhaustive type inventory (ground truth)
- `docs/context-fabric/project-facts.json` — codebase path, DB paths, plugin types, framework
- `docs/context-fabric/seam-proposals.json` — proposed seams with priority order
- `docs/context-fabric/coverage-audit.json` — audit that every type is assigned
- `docs/context-fabric/dependency-graph.json` — directed type dependency graph + SCCs
- `docs/context-fabric/business-rules.json` — 28+ rules with file:line locations
- `docs/context-fabric/call-graphs/*.md` — per-form event → method chains
- `docs/context-fabric/data-flows/*.md` — end-to-end data pipelines
- `docs/context-fabric/database-access.md` — all SQL and DB connection patterns
- `docs/context-fabric/index.json` — searchable master index
- `docs/seams/{seam-name}/spec.md` — auto-generated stub for every proposed seam

**Does NOT:** Capture screenshots · Analyze individual seams in depth · Require any human config

**Key constraint:** Inventory-first + mandatory coverage audit. `coverage-audit.json` must show `audit_passed: true` before seam proposals are written.

---

### 2. ui-behavior-extractor

**Phase:** 0 — UNDERSTAND (one-time per codebase, runs after legacy-context-fabric)
**Input:** `docs/context-fabric/manifest.json` + `docs/context-fabric/seam-proposals.json`
**Output:**
- `docs/seams/{seam}/ui-behavior.md` — per-seam: control inventory, grid columns, button actions, test scenarios
- `docs/context-fabric/visual-controls-catalog.md` — custom SCADA control specs (AnalogTextValue, BinaryColorText)
- `docs/context-fabric/ui-inventory.json` — machine-readable inventory + coverage audit

**Responsibility:**
- For WinForms forms: read `.Designer.cs` (control declarations, event bindings) + code-behind (grid column headers, handler logic)
- For WPF UserControls: read `.xaml` (element hierarchy, data bindings, triggers)
- For VisualControls: document channel binding properties and visual states per ChannelStatus

**Does NOT:** Modify legacy source files · Propose React implementations · Capture screenshots · Analyze business logic

---

### 3. architecture-bootstrap

**Phase:** 0.5 — BOOTSTRAP (one-time, before first seam migration)
**Input:** `docs/context-fabric/project-facts.json`
**Output:**
- `backend/` — FastAPI project scaffold (app/, tests/, pyproject.toml, alembic/)
- `frontend/` — React+Vite scaffold (src/, tests/, package.json, tsconfig.json)
- `docker-compose.yml`
- `.github/workflows/` CI config

**Does NOT:** Implement seam business logic · Generate API contracts

---

### 4. golden-baseline-capture

**Phase:** 0 — UNDERSTAND (optional, per seam, MUST run FIRST in per-seam pipeline)
**Input:** Running legacy application + `docs/seams/{seam}/spec.md`
**Output:**
- `legacy-golden/{seam}/screenshots/*.png`
- `legacy-golden/{seam}/exports/*.csv`
- `legacy-golden/{seam}/db-snapshots/*.json`
- `legacy-golden/{seam}/user-journeys.md`
- `legacy-golden/{seam}/BASELINE_INDEX.md`

**Timing:** Run FIRST in per-seam pipeline (before discovery/implementation) to capture legacy system behavior while it's still available and unmodified.

**Requires:** Windows machine with legacy WinForms app installed and running.

**Does NOT:** Generate tests · Analyze code · Compare new vs old · Run on development machine

---

### 5. runtime-surface-capture

**Phase:** 0 — UNDERSTAND (optional, per seam, runs early to inform contract design)
**Input:** Running system (any environment) + `docs/seams/{seam}/spec.md` + `docs/seams/{seam}/ui-behavior.md`
**Output:**
- `docs/seams/{seam}/runtime/runtime-observed-flows.json`
- `docs/seams/{seam}/runtime/runtime-network-map.json`
- `docs/seams/{seam}/runtime/runtime-ui-observations.md`
- `docs/seams/{seam}/runtime/runtime-deltas.md`

**Purpose:** Observes actual API calls, request/response shapes, network sequences to help contract-generator design accurate OpenAPI specs.

**Requires:** Access to running system (staging, dev, or even partially migrated system) OR HAR files / network traces.

**Does NOT:** Capture golden baselines · Generate contracts · Store secrets

---

### 6. discovery

**Phase:** 1 — DISCOVER (per seam)
**Input:** `docs/seams/{seam}/spec.md` + `docs/context-fabric/` (read-only reference)
**Output:** `docs/seams/{seam}/discovery.md` containing:
- Entry points with event handler chains
- Dependencies: In-Seam / Cross-Seam / External
- Data sources and DB tables accessed
- Business logic methods with C# file:line references
- Test scenarios (minimum 3)
- Cross-seam dependency resolution notes

**Does NOT:** Build codebase KB (already done by legacy-context-fabric) · Generate contracts · Capture screenshots

---

### 7. contract-generator

**Phase:** 2 — CONTRACT (per seam)
**Input:**
- `docs/seams/{seam}/spec.md`
- `docs/seams/{seam}/discovery.md`
- `docs/seams/{seam}/ui-behavior.md`
- `docs/seams/{seam}/runtime/` (optional - runtime evidence if captured)
- `docs/context-fabric/business-rules.json`

**Output:**
- `docs/seams/{seam}/contracts/openapi.yaml`
- `docs/seams/{seam}/dto-mapping.md`

**Does NOT:** Implement code · Bootstrap project · Validate parity

---

### 8. data-strategy

**Phase:** 2.75 — DATA STRATEGY (every seam, always)
**Input:** `docs/seams/{seam}/discovery.md` + existing SQLite database (read-only inspection)
**Output:** `docs/seams/{seam}/data-strategy.md` — strategy choice + SQLAlchemy model signatures

**Strategy options:** Read-Only (default) → Direct Write → New Tables (requires explicit user approval)

**Does NOT:** Migrate the DB · Implement business logic · Generate parity tests

---

### 9. dependency-wrapper-generator

**Phase:** 2.5 — HARD DEPS (conditional per seam)
**Condition:** Only when discovery flags External COM / device / printing / Registry dependencies
**Input:** `docs/seams/{seam}/discovery.md` + legacy C# files that use the dependency
**Output:**
- `backend/app/adapters/{type}_wrapper.py` — abstract base
- `backend/app/adapters/mock_{type}.py` — test mock
- `docs/seams/{seam}/hard-dependencies.md`

**Does NOT:** Implement real Windows drivers · Implement business logic · Run if no hard deps found

---

### 10. backend-migration

**Phase:** 3 — BUILD (per seam, parallel with frontend-migration)
**Input:**
- `docs/seams/{seam}/contracts/openapi.yaml`
- `docs/seams/{seam}/discovery.md`
- `docs/seams/{seam}/data-strategy.md`
- `docs/context-fabric/business-rules.json`
- Legacy C# source files (read-only)

**Output:**
- `backend/app/{seam}/router.py`
- `backend/app/{seam}/schemas.py`
- `backend/app/{seam}/service.py`
- `backend/app/{seam}/models.py` (if DB access)
- `backend/tests/unit/test_{seam}_*.py`

**Does NOT:** Design the API · Bootstrap the project · Generate parity tests · Wrap hard deps

---

### 11. frontend-migration

**Phase:** 3 — BUILD (per seam, parallel with backend-migration)
**Input:**
- `docs/seams/{seam}/contracts/openapi.yaml`
- `docs/seams/{seam}/ui-behavior.md` ← **primary UI reference** (control layout, columns, actions, test scenarios)
- `docs/context-fabric/visual-controls-catalog.md` ← custom SCADA control specs
- `docs/seams/{seam}/discovery.md`
- `legacy-golden/{seam}/screenshots/` (if captured)

**Output:**
- `frontend/src/api/{seam}.ts`
- `frontend/src/hooks/use{Seam}.ts`
- `frontend/src/components/{seam}/*.tsx`
- `frontend/src/pages/{seam}/{Seam}Page.tsx`
- `frontend/src/components/{seam}/*.test.tsx`

**Does NOT:** Design the API · Bootstrap the project · Generate parity tests

---

### 12. parity-harness-generator

**Phase:** 4 — VALIDATE (conditional per seam)
**Condition:** Only if `legacy-golden/{seam}/BASELINE_INDEX.md` exists
**Input:**
- `legacy-golden/{seam}/` (golden baselines captured in step 4)
- `docs/seams/{seam}/contracts/openapi.yaml`
- Implemented backend/frontend code

**Output:**
- `backend/tests/parity/test_{seam}_exports.py`
- `backend/tests/parity/test_{seam}_db_diff.py`
- `frontend/tests/e2e/parity/{seam}_screenshots.spec.ts`
- `frontend/tests/e2e/parity/{seam}_workflows.spec.ts`

**Does NOT:** Capture golden files · Implement seam logic · Run tests (user runs them)

---

### run-seam-migration (skill)

**Invoked as:** `/run-seam-migration {seam-name}`
**Purpose:** Orchestrates steps 4–12 for a single seam with gate enforcement at each step.

**Prerequisites it checks:**
- `docs/context-fabric/project-facts.json` exists (legacy-context-fabric was run)
- `docs/context-fabric/seam-proposals.json` exists
- `backend/` and `frontend/` exist (architecture-bootstrap was run)
- `docs/seams/{seam}/spec.md` exists (generated by legacy-context-fabric)

**Gate at each phase:** No phase starts until its predecessor's outputs pass validation.

---

## Avoiding Overlaps

| Topic | Agent A | Agent B | How they divide it |
|-------|---------|---------|-------------------|
| Codebase inventory | legacy-context-fabric | discovery | context-fabric inventories ALL; discovery deep-dives ONE seam |
| UI layout | ui-behavior-extractor | discovery | extractor: controls/columns/actions from Designer.cs; discovery: business logic dependencies |
| UI reference | ui-behavior-extractor | golden-baseline-capture | extractor: from code (always available); golden: live screenshots (optional) |
| Runtime evidence | runtime-surface-capture | golden-baseline-capture | runtime: API shapes/network for contract design; golden: outputs for parity testing |
| Test scenarios | ui-behavior-extractor | discovery | extractor: UI-level (each button/handler); discovery: business-level workflow scenarios |
| Screenshots | golden-baseline-capture | parity-harness-generator | capture takes them; generator writes tests that compare them |
| DB access | discovery | data-strategy | discovery: which tables; data-strategy: access strategy + SQLAlchemy models |
| Unit tests | backend-migration | parity-harness-generator | backend: unit tests for logic; parity: legacy vs new comparison tests |
| Project skeleton | architecture-bootstrap | backend/frontend-migration | bootstrap: create once; migration: add seam slices |

---

## Agent Status

| # | Agent | Phase | Mandatory | File |
|---|-------|-------|-----------|------|
| 1 | legacy-context-fabric | 0 - UNDERSTAND (one-time) | Yes | `.claude/agents/legacy-context-fabric.md` |
| 2 | ui-behavior-extractor | 0 - UNDERSTAND (one-time) | Yes | `.claude/agents/ui-behavior-extractor.md` |
| 3 | architecture-bootstrap | 0.5 - BOOTSTRAP (one-time) | Yes | `.claude/agents/architecture-bootstrap.md` |
| 4 | golden-baseline-capture | 0 - UNDERSTAND (per seam, FIRST) | Optional | `.claude/agents/golden-baseline-capture.md` |
| 5 | runtime-surface-capture | 0 - UNDERSTAND (per seam) | Optional | `.claude/agents/runtime-surface-capture.md` |
| 6 | discovery | 1 - DISCOVER (per seam) | Yes | `.claude/agents/discovery.md` |
| 7 | contract-generator | 2 - CONTRACT (per seam) | Yes | `.claude/agents/contract-generator.md` |
| 8 | data-strategy | 2.75 - DATA STRATEGY (per seam) | Yes | `.claude/agents/data-strategy.md` |
| 9 | dependency-wrapper-generator | 2.5 - HARD DEPS (conditional) | Conditional | `.claude/agents/dependency-wrapper-generator.md` |
| 10 | backend-migration | 3 - BUILD (per seam) | Yes | `.claude/agents/backend-migration.md` |
| 11 | frontend-migration | 3 - BUILD (per seam) | Yes | `.claude/agents/frontend-migration.md` |
| 12 | parity-harness-generator | 4 - VALIDATE (conditional) | Optional | `.claude/agents/parity-harness-generator.md` |
| — | run-seam-migration | ORCHESTRATE | — | `.claude/skills/run-seam-migration/SKILL.md` |

---

## Key Architectural Decisions

- **Same database:** No DB migration, no dual-write. Backend uses existing SQLite as-is.
- **Fully autonomous setup:** legacy-context-fabric discovers the codebase itself — no `PROJECT_CONTEXT.md` or manual config needed.
- **Inventory-first:** legacy-context-fabric builds a complete manifest before proposing any seam. Coverage audit must pass before proposals are written.
- **ui-behavior.md is the frontend spec:** frontend-migration never invents UI — it replicates from ui-behavior.md.
- **Golden baselines optional but early:** Enable parity testing but the migration can proceed without them. If captured, must run FIRST in per-seam pipeline.
- **Runtime capture informs contract design:** runtime-surface-capture (optional) observes real API shapes to help contract-generator design accurate specs.
- **data-strategy runs for every seam:** Even read-only seams get SQLAlchemy model signatures.
- **No parallel operation:** The migrated system replaces the legacy workflow; they do not run side-by-side.
