---
name: run-seam-migration
description: Orchestrates the complete migration of a single seam from legacy application to Python + React.
disable-model-invocation: true
context: fork
agent: general-purpose
---

# Seam Migration Orchestrator

Migrate seam: **$ARGUMENTS**

---

## Framework Detection

**Before starting migration, detect the source framework:**

```bash
# Check for .NET/WinForms
if [ -f "docs/context-fabric/project-facts.json" ]; then
    framework=$(jq -r '.framework' docs/context-fabric/project-facts.json 2>/dev/null || echo "unknown")
    echo "Detected framework: $framework"
else
    echo "⚠️  project-facts.json not found, assuming framework from file extensions"
    [ -f "*.sln" ] && framework="dotnet" || framework="unknown"
fi
```

**Framework-specific agents:**
- **WinForms/WPF** (.NET) → Uses: `ui-behavior-extractor`, `dependency-wrapper-generator` (Windows), `winforms-patterns` skill
- **Spring** (Java) → Would use: `jsp-ui-behavior-extractor` (future), `jvm-dependency-wrapper-generator` (future), `spring-patterns` skill
- **Other** → Generic agents only (discovery, contract-generator, etc.)

---

## 🚨 Phase 0 Check (CRITICAL - NEW)

**Before ANY implementation, verify Phase 0 (UNDERSTAND) completion:**

```bash
# 1. Check legacy-context-fabric output
test -f "docs/context-fabric/project-facts.json"    || echo "❌ BLOCKED: Run legacy-context-fabric first"
test -f "docs/context-fabric/seam-proposals.json"   || echo "❌ BLOCKED: Run legacy-context-fabric first"

# 2. Check ui-behavior extraction
ui_behavior_count=$(find seams -name "ui-behavior.md" 2>/dev/null | wc -l)
test $ui_behavior_count -ge 5 && echo "✅ UI behavior: $ui_behavior_count seams documented" || echo "⚠️  UI behavior: Only $ui_behavior_count seams (run ui-behavior-extractor)"

# 3. Check architecture design (REQUIRED after first seam requirements)
# NOTE: Architecture runs AFTER first seam requirements (to be informed by actual needs)
if [ ! -f "docs/architecture-design.md" ]; then
    echo "⚠️  Architecture design not yet complete"
    echo "   This is normal - architecture will be designed after first seam requirements"
fi

# 4. Check golden baselines (CRITICAL FOR VALIDATION)
if [ -d "legacy-golden" ] && [ -f "docs/legacy-golden/BASELINE_INDEX.md" ]; then
    echo "✅ Golden baselines: captured"
else
    echo "❌ WARNING: No golden baselines found"
    echo "   Impact: Cannot validate parity, cannot compare screenshots"
    echo "   Action: Run golden-baseline-capture agent on Windows machine with legacy app"
    echo "   Workaround: Continue with synthetic baselines (limited validation)"

    # Check if blocker is documented
    if [ ! -f "docs/BASELINE_BLOCKERS.md" ]; then
        echo "❌ STOP: Create docs/BASELINE_BLOCKERS.md to document why baselines cannot be captured"
        echo "   Or run golden-baseline-capture agent if Windows machine is available"
        exit 1
    else
        echo "✅ Baseline blockers documented. Proceeding with limited validation."
    fi
fi

# 4. Check legacy database
if [ ! -f "backend/data/archiver.db" ]; then
    echo "⚠️  Legacy database not found at backend/data/archiver.db"
    echo "   Seed data will be synthetic only"
fi
```

**Decision Point:**
- If golden baselines missing AND blocker not documented → **STOP**
- If blockers documented → proceed with synthetic baselines (reduced confidence)
- If golden baselines present → proceed with full validation capability

## Prerequisites (Check Before Starting)

```bash
test -f CLAUDE.md                                   || echo "STOP: CLAUDE.md missing"
test -d backend                                     || echo "STOP: Run architecture-bootstrap first"
test -d frontend                                    || echo "STOP: Run architecture-bootstrap first"
test -f "docs/seams/$ARGUMENTS/spec.md"                  || echo "WARN: spec.md not found — legacy-context-fabric may not have generated it yet"
```

Stop and report if any required prerequisite is missing. Do not attempt to work around it.

---

## Phase 1 — Discovery (Technical Analysis)

**Agent:** discovery
**Input:** seam name, `docs/seams/$ARGUMENTS/spec.md`, `docs/seams/$ARGUMENTS/ui-behavior.md`, legacy source files
**Output:**
- `docs/seams/$ARGUMENTS/discovery.md` (technical analysis)
- `docs/seams/$ARGUMENTS/readiness.json` (GO/NO-GO)
- `docs/seams/$ARGUMENTS/evidence-map.json` (call chains, flows)
- `docs/seams/$ARGUMENTS/contracts/required-fields.json` (UI fields)
- `docs/seams/$ARGUMENTS/data/targets.json` (read/write targets)

**Gate — do not proceed until:**
- [ ] All dependencies classified (In-Seam / Cross-Seam / External)
- [ ] No unresolved UNKNOWN dependencies
- [ ] At least 3 test scenarios documented
- [ ] Cross-seam dependencies have a resolution note
- [ ] Readiness status is GO (confidence: high/medium)

---

## Phase 2 — Requirements (Functional Specifications)

**Agent:** requirements-generator
**Input:**
- **REQUIRED**: `docs/seams/$ARGUMENTS/discovery.md` (technical analysis)
- **REQUIRED**: `docs/seams/$ARGUMENTS/ui-behavior.md` (UI structure)
- Optional: `docs/context-fabric/business-rules.json`

**Output:**
- `docs/seams/$ARGUMENTS/requirements.md` (EARS-formatted functional requirements)

**Process**:
1. Read discovery.md (extract business rules, workflows, validation rules)
2. Transform technical findings → EARS requirements
3. Generate acceptance criteria (happy path, validation, error handling)
4. Add Requirement 0 (if first seam): Project Scaffolding
5. Add Requirement 0.5 (if UI seam): UI Layout & Navigation
6. **Human review gate**: User MUST approve requirements

**Gate — do not proceed until:**
- [ ] Requirements generated with EARS patterns
- [ ] All business rules from discovery.md captured
- [ ] Scenario coverage complete (happy path, validation, business rules, error handling)
- [ ] **User has explicitly approved requirements** (typed "approved")

---

## Phase 3 — Architecture Design (CRITICAL - First Seam Only)

**Condition**: Only run if `docs/architecture-design.md` does NOT exist (first seam only)

**Agent:** architecture-design
**Input:**
- **REQUIRED**: `docs/seams/$ARGUMENTS/requirements.md` (concrete functional needs)
- **REQUIRED**: `docs/seams/$ARGUMENTS/discovery.md` (technical complexity, dependencies)
- `docs/context-fabric/project-facts.json` (legacy tech stack)

**Output:**
- `docs/architecture-design.md` (comprehensive 15-section design document)

**Process**:
1. Read requirements.md → understand ACTUAL functional needs
2. Read discovery.md → understand technical complexity
3. Ask user for tech preferences (Python/Java? React/Vue? PostgreSQL/MongoDB?)
4. Generate 15-section design document:
   - Executive Summary, Architecture Overview, Component Architecture
   - Data Architecture, Integration Architecture, Security Architecture
   - Infrastructure & Deployment, Observability, DR, Cost, Risks, Decisions
5. **Human review gate**: User MUST approve architecture

**Gate — do not proceed until:**
- [ ] Requirements inform architecture (not assumptions)
- [ ] User has chosen tech stack (Python/FastAPI + React, etc.)
- [ ] 15-section design document complete
- [ ] **User has explicitly approved architecture** (typed "approved")

**Why architecture runs here**:
- ✅ Informed by REAL requirements (not guesses)
- ✅ Based on concrete complexity (from discovery)
- ✅ User sees what's needed BEFORE choosing tech stack
- ✅ Architecture locked in for remaining seams

---

## Phase 4 — Contract

**Agent:** contract-generator
**Input:** `docs/seams/$ARGUMENTS/spec.md`, `docs/seams/$ARGUMENTS/discovery.md`
**Output:** `docs/seams/$ARGUMENTS/contracts/openapi.yaml`, `docs/seams/$ARGUMENTS/dto-mapping.md`

**Gate:**
- [ ] `npx @openapitools/openapi-generator-cli validate -i docs/seams/$ARGUMENTS/contracts/openapi.yaml` exits 0
- [ ] All spec requirements have a corresponding endpoint
- [ ] ChannelId pattern enforced (if applicable)
- [ ] ErrorResponse schema defined

---

## Phase 2.5 — Hard Dependency Wrappers (conditional)

**Condition:** Run only if Phase 1 discovery flagged External platform-specific dependencies.

**Framework-specific dependencies:**
- **WinForms/WPF**: COM/ActiveX, Windows Registry, Serial Ports, Printing → Use `dependency-wrapper-generator` (Windows platform)
- **Spring**: JNI calls, JNDI lookups, Java-specific APIs → Use `jvm-dependency-wrapper-generator` (future, when available)
- **None**: Pure business logic with no platform dependencies → Skip this phase

**Agent:** `dependency-wrapper-generator` (Windows) or framework-specific equivalent
**Input:** `docs/seams/$ARGUMENTS/discovery.md`, legacy source files
**Output:** `backend/app/adapters/`, `docs/seams/$ARGUMENTS/hard-dependencies.md`

**Gate:**
- [ ] Abstract base class exists for each dependency type
- [ ] Mock implementation exists and is importable
- [ ] `use_mock_adapters` setting added to config

---

## Phase 3 — Backend + Frontend (run in parallel)

### 3a Backend Implementation
**Agent:** backend-migration
**Input:** `docs/seams/$ARGUMENTS/contracts/openapi.yaml`, `docs/seams/$ARGUMENTS/discovery.md`, `docs/seams/$ARGUMENTS/requirements.md`
**Output:** `backend/app/$ARGUMENTS/`

**Note**: Backend agent will determine data strategy in Step 1 (read-only vs direct write vs new tables)

**Gate 3a.1 — Quality Gates (enforced by backend-migration agent internally)**:
```bash
cd backend
# Build verification
pytest --collect-only app/$ARGUMENTS/ tests/unit/test_$ARGUMENTS_*
# Tests + Coverage
pytest tests/unit/test_$ARGUMENTS_* -v --cov=app/$ARGUMENTS --cov-report=term-missing --cov-fail-under=80
# Static Analysis
ruff check app/$ARGUMENTS/ --select=ALL
mypy app/$ARGUMENTS/ --strict --ignore-missing-imports
```
- [ ] pytest exits 0, coverage ≥ 80%
- [ ] mypy exits 0
- [ ] ruff exits 0

**Gate 3a.2 — Code & Security Review (MANDATORY)**:
**Agent:** code-security-reviewer
**Input:**
- Changed files: all files in `backend/app/$ARGUMENTS/`
- `docs/seams/$ARGUMENTS/requirements.md` (spec alignment)
- `docs/seams/$ARGUMENTS/discovery.md` (legacy business rules)
- `docs/architecture-design.md` (design patterns + security architecture)

**Action:**
1. Invoke Agent tool with `subagent_type="code-security-reviewer"`
2. Wait for verdict: APPROVED | RECOMMENDATION | BLOCKER
3. **If BLOCKER**: HALT pipeline, report to user, DO NOT PROCEED
4. **If RECOMMENDATION**: Log recommendations in `docs/seams/$ARGUMENTS/review-notes.md`, proceed
5. **If APPROVED**: Proceed to Phase 3b

**DO NOT PROCEED to Phase 3b until code-security-reviewer returns APPROVED or RECOMMENDATION.**

---

### 3b Frontend Implementation
**Agent:** frontend-migration
**Input:** `docs/seams/$ARGUMENTS/contracts/openapi.yaml`, `docs/seams/$ARGUMENTS/ui-behavior.md` (primary UI reference), `docs/seams/$ARGUMENTS/discovery.md`, `docs/context-fabric/visual-controls-catalog.md`
**Output:** `frontend/src/pages/$ARGUMENTS/`, `frontend/src/components/$ARGUMENTS/`

**Gate 3b.1 — Quality Gates (enforced by frontend-migration agent internally)**:
```bash
cd frontend
# Build verification
npx tsc --noEmit --project tsconfig.json
npm run build
# Tests + Coverage
npm run test -- --coverage --coverageThreshold='{"global":{"statements":80,"branches":80,"functions":80,"lines":80}}' --run
# Static Analysis
npm run lint
npm run format:check
```
- [ ] TypeScript compilation exits 0
- [ ] Build exits 0
- [ ] Tests exit 0, coverage ≥ 80% (all metrics)
- [ ] Lint exits 0
- [ ] Format check exits 0

**Gate 3b.2 — Code & Security Review (MANDATORY)**:
**Agent:** code-security-reviewer
**Input:**
- Changed files: all files in `frontend/src/pages/$ARGUMENTS/`, `frontend/src/components/$ARGUMENTS/`, `frontend/src/api/$ARGUMENTS.ts`, `frontend/src/hooks/use$ARGUMENTS*.ts`
- `docs/seams/$ARGUMENTS/requirements.md` (spec alignment)
- `docs/seams/$ARGUMENTS/ui-behavior.md` (UI structure)
- `docs/architecture-design.md` (design patterns + security architecture)

**Action:**
1. Invoke Agent tool with `subagent_type="code-security-reviewer"`
2. Wait for verdict: APPROVED | RECOMMENDATION | BLOCKER
3. **If BLOCKER**: HALT pipeline, report to user, DO NOT PROCEED
4. **If RECOMMENDATION**: Log recommendations, proceed to Phase 4
5. **If APPROVED**: Proceed to Phase 4

**DO NOT PROCEED to Phase 4 until code-security-reviewer returns APPROVED or RECOMMENDATION.**

---

## Phase 4 — Integration Tests

Run with both backend and frontend running:
```bash
cd backend
pytest tests/integration/test_$ARGUMENTS_* -v
```

**Gate:**
- [ ] All integration tests pass
- [ ] All API paths in `docs/seams/$ARGUMENTS/contracts/openapi.yaml` are tested
- [ ] Error cases (404, 400, 422) are tested

---

## Phase 4.5 — Full-Stack Smoke Test (CRITICAL)

**Purpose**: Verify backend and frontend work **together** end-to-end. Integration tests only test backend; this tests the full stack.

### Step 1: Start Services

```bash
# Start backend
cd backend && docker-compose up -d backend
sleep 3

# Start frontend dev server
cd frontend && npm run dev &
sleep 5
```

### Step 2: Health Checks

```bash
# Backend health check
curl -f http://localhost:8000/api/health || {
  echo "❌ Backend not responding"
  exit 1
}

# Frontend health check
curl -f http://localhost:5173/ || {
  echo "❌ Frontend not responding"
  exit 1
}

echo "✅ Services are running"
```

### Step 3: Contract Validation (Automated)

```bash
# Validate backend routes match contract
python .claude/scripts/validate_contract_backend.py \
  backend/app/$ARGUMENTS \
  docs/seams/$ARGUMENTS/contracts/openapi.yaml || {
    echo "❌ Backend contract validation failed"
    exit 1
  }

# Validate frontend API calls match contract
python .claude/scripts/validate_contract_frontend.py \
  frontend/src \
  docs/seams/$ARGUMENTS/contracts/openapi.yaml || {
    echo "❌ Frontend contract validation failed"
    exit 1
  }

echo "✅ Contract validation passed"
```

### Step 4: E2E Smoke Test (Playwright)

```bash
# Run Playwright smoke test
cd frontend && npx playwright test tests/e2e/smoke/$ARGUMENTS.spec.ts --headed || {
  echo "❌ E2E smoke test failed"
  exit 1
}

echo "✅ E2E smoke test passed"
```

### Step 5: Visual Parity Check (If Screenshots Exist)

```bash
# Check if baseline screenshots exist
if [ -d "docs/legacy-golden/$ARGUMENTS/screenshots" ]; then
  echo "📸 Running visual parity check..."

  # Take screenshot of current implementation
  cd frontend && npx playwright screenshot \
    http://localhost:5173/$ARGUMENTS \
    --viewport-size 1920,1080 \
    --output ../current-screenshot.png

  # Compare with baseline
  python .claude/scripts/compare_screenshots.py \
    docs/legacy-golden/$ARGUMENTS/screenshots/main.png \
    current-screenshot.png \
    --threshold 85 \
    --output diff.png || {
      echo "⚠️  Visual parity below 85%"
      echo "   Review diff.png for visual comparison"
      echo "   Continue? (y/n)"
      read -r response
      if [ "$response" != "y" ]; then
        exit 1
      fi
    }

  echo "✅ Visual parity check passed"
else
  echo "⚠️  No baseline screenshots - skipping visual parity check"
fi
```

### Step 6: Cleanup

```bash
# Stop services
cd backend && docker-compose down
kill %1  # Stop frontend dev server
```

**Gate:**
- [ ] Backend responds to health check
- [ ] Frontend loads without console errors
- [ ] Backend routes match contract (automated validation)
- [ ] Frontend API calls match contract (automated validation)
- [ ] E2E smoke test passes (can navigate, view data, submit forms)
- [ ] Visual similarity ≥ 85% (if screenshots available)

**Why this matters**:
- Catches FE/BE contract mismatches **before** code review
- Verifies full stack works together (not just in isolation)
- Validates visual appearance matches legacy
- Much cheaper to fix now than after all code is merged

---

## Phase 5 — Parity Tests (conditional)

**Condition:** Run only if `docs/legacy-golden/$ARGUMENTS/BASELINE_INDEX.md` exists.

**Agent:** parity-harness-generator
**Input:** `docs/legacy-golden/$ARGUMENTS/`, `docs/seams/$ARGUMENTS/contracts/openapi.yaml`
**Output:** `backend/tests/parity/`, `frontend/tests/e2e/parity/`

Then run:
```bash
pytest backend/tests/parity/test_$ARGUMENTS_* -v
npx playwright test tests/e2e/parity/$ARGUMENTS_parity
```

**Gate:**
- [ ] All parity tests pass OR differences are documented and approved in evidence.md

---

## Phase 6 — Evidence

Collect all test results and write `docs/seams/$ARGUMENTS/evidence/evidence.md`:

```markdown
# Evidence: $ARGUMENTS
Date: {today}
Status: ✅ COMPLETE | 🟡 ISSUES | 🔴 BLOCKED

## Results
| Test Suite | Passed | Failed | Coverage |
|-----------|--------|--------|----------|
| Backend unit | | | |
| Backend integration | | | |
| Frontend unit | | | |
| E2E | | | |
| Parity (if run) | | | |

## Parity Differences (if any)
(document and get approval for any approved divergences)

## Blockers Remaining
(none if COMPLETE)
```

**Gate:**
- [ ] evidence.md exists
- [ ] Status is ✅ COMPLETE or all issues are documented

---

## Final Report to User

Summarise:
- Seam name and completion status
- All gate results
- Coverage numbers
- Any business logic that could not be ported
- Next seam recommendation
