# Parity Verification Architecture

## Overview

The parity verification system uses a **skill + agent** architecture:

- **browser-agent** = SKILL (tool for verification)
- **parity-harness-generator** = AGENT (orchestrator that uses the skill)

---

## Browser-Agent SKILL

**Purpose:** Perform pixel-level visual comparison and structural verification

**Location:** `.claude/skills/browser-agent/SKILL.md`

**Capabilities:**
- ✅ **Pixel-level screenshot comparison** — Generate diff images showing exact visual differences
- ✅ **Structural element verification** — Check presence of headers, footers, nav, forms, tables
- ✅ **CSS class matching** — Verify styling fidelity (e.g., `.esh-button`, `.esh-table`)
- ✅ **Interactive element count** — Compare buttons, links, inputs between legacy/modern
- ✅ **Data grid validation** — Compare table contents cell-by-cell
- ✅ **Workflow execution parity** — Verify same user journey produces same outcome

**Invocation:**
```bash
Skill: browser-agent --legacy http://localhost:50586 --modern http://localhost:5173 --mode verify --workflows catalog-list,catalog-crud
```

**Output:**
```
legacy-golden/parity-results/{seam}/
├── VERIFICATION_SUMMARY.md          # Executive summary with parity score
├── verification-results.json        # Machine-readable results
├── parity-report.md                 # Detailed report
├── feature-matrix.md                # Element comparison matrix
├── issues.json                      # Discrepancy data (for routing)
└── screenshots/
    ├── legacy/{workflow}.png        # Legacy screenshots
    ├── modern/{workflow}.png        # Modern screenshots
    └── diff/{workflow}.png          # Pixel diff with red highlights
```

**Scoring Formula:**
```
parity_score = (
  feature_completeness * 40% +
  visual_consistency * 20% +
  data_accuracy * 30% +
  workflow_equivalence * 10%
) * 100

Target: 85%+ overall score
```

---

## Parity-Harness-Generator AGENT

**Purpose:** Orchestrate iterative parity verification and fixing

**Location:** `.claude/agents/parity-harness-generator.md`

**Responsibilities:**
1. Run browser-agent verification
2. Analyze discrepancies in `issues.json`
3. Route to appropriate fix agents based on root cause
4. Wait for fix completion
5. Re-verify using browser-agent
6. Iterate until 85%+ parity achieved (max 5 iterations)

**Orchestration Loop:**
```
LOOP until parity_score >= 85% OR iteration > 5:
  1. Skill: browser-agent --mode verify
  2. Read: issues.json
  3. Analyze: categorize discrepancies
  4. Route: invoke fix agent
  5. Wait: for agent completion
  6. Re-verify: browser-agent again
END LOOP
```

**Discrepancy Routing Table:**

| Discrepancy Type | Root Cause | Fix Agent |
|------------------|------------|-----------|
| API 404/500 error | Backend endpoint missing/broken | `backend-migration` |
| Wrong API response | Backend logic wrong | `backend-migration` |
| Missing header/footer | Frontend layout incomplete | `frontend-migration` |
| Wrong CSS classes | Frontend styling wrong | `frontend-migration` |
| Empty data table | API integration broken | `frontend-migration` |
| Wrong validation messages | Backend validation wrong | `backend-migration` |
| Misunderstood requirements | Discovery incomplete | `discovery` |
| Missing API in contract | Contract out of sync | `contract-generator` |

**Iteration Log:**

Agent documents each iteration in `iteration-log.md`:

```markdown
## Iteration 1
**Parity Score:** 55.7%
**Issues:** Frontend calling /api/catalog (404)
**Fix:** Updated vite.config.ts proxy port
**Result:** 72.3% (improved)

## Iteration 2
**Parity Score:** 72.3%
**Issues:** Missing header banner, wrong CSS spacing
**Fix:** Invoked frontend-migration to add header
**Result:** 89.1% (PASSED)
```

**Success Criteria:**
- ✅ Parity score >= 85%
- ✅ All critical elements present
- ✅ All workflows functional
- ✅ Iteration log complete
- ✅ Final report in `docs/seams/{seam}/PARITY_EVIDENCE.md`

---

## Example: Catalog Seam Parity Verification

### Current Status (Iteration 1 Complete)

**Parity Score:** 100% (functional checks only)

**What Was Verified:**
- ✅ Elements present (buttons, links, tables)
- ✅ Forms functional
- ✅ API returning data

**What Was NOT Verified:**
- ❌ Pixel-level screenshot comparison
- ❌ Header/banner/footer structure
- ❌ CSS class matching
- ❌ Visual layout similarity

### Next Steps

Run parity-harness-generator agent to:
1. Execute browser-agent with pixel-level comparison
2. Find missing visual elements (header, footer, banner)
3. Route to frontend-migration to add missing elements
4. Re-verify until 85%+ parity (including visual checks)

**Command:**
```bash
Agent: parity-harness-generator
Prompt: "Verify parity for catalog-list and catalog-crud seams. Legacy app: http://localhost:50586, Modern app: http://localhost:5173. Iterate until 85%+ parity achieved including pixel-level visual comparison."
```

---

## Key Architectural Principles

1. **Separation of Concerns:**
   - SKILL = verification tool (no decision making)
   - AGENT = orchestrator (analyzes, routes, iterates)

2. **Iterative Improvement:**
   - Don't expect 85% parity in one shot
   - Use iteration loop to incrementally fix issues
   - Maximum 5 iterations to prevent infinite loops

3. **Root Cause Analysis:**
   - Don't just report "UI different"
   - Categorize: backend vs frontend vs contract vs discovery
   - Route to appropriate fix agent

4. **Evidence-Based:**
   - Screenshots prove parity
   - Pixel diffs highlight exact differences
   - Iteration log shows convergence

5. **Autonomous Operation:**
   - Agent iterates without asking user
   - Only escalates if stuck (5 iterations without convergence)
   - Generates final evidence report automatically

---

## Integration with Migration Flow

```
AGENT_RESPONSIBILITIES_AND_FLOW.md:

STEP 10: backend-migration agent
  ↓
STEP 11: frontend-migration agent
  ↓
STEP 12: parity-harness-generator agent    ← YOU ARE HERE
  │
  ├─→ Skill: browser-agent (verify)
  │     ↓
  │   Analyze issues.json
  │     ↓
  │   Route to fix agent:
  │   ├─→ backend-migration (if API wrong)
  │   ├─→ frontend-migration (if UI wrong)
  │   ├─→ contract-generator (if contract wrong)
  │   └─→ discovery (if requirements wrong)
  │     ↓
  │   Wait for fix
  │     ↓
  │   Re-verify (browser-agent)
  │     ↓
  └─── LOOP until 85%+ parity
         ↓
       DONE: Write PARITY_EVIDENCE.md
```

---

## Updated Agent Descriptions

### browser-agent (SKILL)
```yaml
description: >
  Automated browser agent using Playwright for pixel-level visual comparison,
  structural element verification, CSS class matching, and workflow parity
  testing between legacy and modern applications.
```

### parity-harness-generator (AGENT)
```yaml
description: >
  Orchestrates parity verification using browser-agent skill to compare
  legacy vs modern UIs pixel-by-pixel. When discrepancies found, routes to
  appropriate agents (discovery/contract/backend/frontend) to fix issues.
  Iterates verification loop until 85%+ parity achieved.
```

---

## Summary

This architecture ensures:
- **Comprehensive verification** — Not just functional, but pixel-level visual parity
- **Autonomous fixing** — Agent iterates without user intervention
- **Root cause routing** — Correct fix agent invoked based on issue type
- **Convergence guarantee** — Maximum 5 iterations prevents infinite loops
- **Evidence-based approval** — Screenshots + parity score prove migration readiness

**Current Limitation:** Browser-agent script needs pixel diff implementation (currently only counts elements). This will be added to `.claude/skills/browser-agent/scripts/verify-catalog.py` using Pillow library for image comparison.
