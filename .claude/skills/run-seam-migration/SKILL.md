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

# 3. Check golden baselines (CRITICAL FOR VALIDATION)
if [ -d "legacy-golden" ] && [ -f "legacy-golden/BASELINE_INDEX.md" ]; then
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

## Phase 1 — Discovery

**Agent:** discovery
**Input:** seam name, legacy codebase path from `docs/context-fabric/project-facts.json`, docs/context-fabric/ (if available)
**Output:** `docs/seams/$ARGUMENTS/discovery.md`

**Gate — do not proceed until:**
- [ ] All dependencies classified (In-Seam / Cross-Seam / External)
- [ ] No unresolved UNKNOWN dependencies
- [ ] At least 3 test scenarios documented
- [ ] Cross-seam dependencies have a resolution note

---

## Phase 2 — Contract

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

## Phase 2.75 — Data Strategy

**Agent:** data-strategy
**Input:** `docs/seams/$ARGUMENTS/discovery.md`
**Output:** `docs/seams/$ARGUMENTS/data-strategy.md`, SQLAlchemy model signatures

**Gate:**
- [ ] Strategy chosen (Read-Only / Direct Write / New Tables)
- [ ] If New Tables: user approval documented
- [ ] SQLAlchemy model signatures match existing DB schema

---

## Phase 3 — Backend + Frontend (run in parallel)

### 3a Backend
**Agent:** backend-migration
**Input:** `docs/seams/$ARGUMENTS/contracts/openapi.yaml`, `docs/seams/$ARGUMENTS/discovery.md`, `docs/seams/$ARGUMENTS/data-strategy.md`
**Output:** `backend/app/$ARGUMENTS/`

**Gate:**
```bash
cd backend
pytest tests/unit/test_$ARGUMENTS_* -v --cov=app/$ARGUMENTS --cov-report=term-missing
mypy app/$ARGUMENTS/
ruff check app/$ARGUMENTS/
```
- [ ] pytest exits 0, coverage ≥ 80%
- [ ] mypy exits 0
- [ ] ruff exits 0

### 3b Frontend
**Agent:** frontend-migration
**Input:** `docs/seams/$ARGUMENTS/contracts/openapi.yaml`, `docs/seams/$ARGUMENTS/ui-behavior.md` (primary UI reference), `docs/seams/$ARGUMENTS/discovery.md`, `docs/context-fabric/visual-controls-catalog.md`
**Output:** `frontend/src/pages/$ARGUMENTS/`, `frontend/src/components/$ARGUMENTS/`

**Gate:**
```bash
cd frontend
npm run type-check
npm run lint
npm test -- $ARGUMENTS
```
- [ ] type-check exits 0
- [ ] lint exits 0
- [ ] tests exit 0, coverage ≥ 70%

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

## Phase 5 — Parity Tests (conditional)

**Condition:** Run only if `legacy-golden/$ARGUMENTS/BASELINE_INDEX.md` exists.

**Agent:** parity-harness-generator
**Input:** `legacy-golden/$ARGUMENTS/`, `docs/seams/$ARGUMENTS/contracts/openapi.yaml`
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
