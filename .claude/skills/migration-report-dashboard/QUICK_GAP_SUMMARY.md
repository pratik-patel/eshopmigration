# 🎯 Quick Gap Summary — Dashboard Data Requirements

**TL;DR: What we have vs. what we need**

---

## 📊 Overall Status

| Category | Count | Status |
|----------|-------|--------|
| **Total Files Needed** | 30+ | - |
| **✅ Currently Available** | 15 | 50% |
| **❌ Missing Critical (P0)** | 4 | Blocks core features |
| **⚠️ Missing High (P1)** | 5 | Degrades UX |
| **🟡 Missing Medium/Low (P2-P3)** | 4+ | Nice-to-have |

---

## 🔴 Critical Missing Files (P0) — MUST FIX

### 1. `migration-state.json`
**Impact:** No real-time tracking, no timeline, no agent activity log, no velocity
**Blocks:**
- 🏠 Overview (health score, elapsed time, ETA)
- 🔍 Phase 0 (discovery iterations timeline)
- 🔨 Phase 5 (agent activity log)
- 📈 Analytics (velocity, trends)

**Fix:** Create orchestrator-level state manager that tracks:
- Migration start date
- Phase status and timestamps
- Agent activity log (real-time)
- Seam completion history
- Current metrics snapshot

---

### 2. `tasks-status.json`
**Impact:** No Kanban board, no real-time task progress
**Blocks:**
- 📝 Phase 3 (tasks Kanban board)
- 🔨 Phase 5 (real-time progress tracker)

**Fix:**
- Parse tasks.md checklist format
- Track task status (todo/in_progress/done)
- Update during implementation

---

### 3. `test-results.json` (per seam, backend + frontend)
**Impact:** No code quality dashboard
**Blocks:**
- 🔨 Phase 5 (code quality metrics, coverage %)
- 📈 Analytics (quality trends)

**Fix:**
- Backend: `pytest --json-report`
- Frontend: `vitest --reporter=json`

---

### 4. `parity-results.json`
**Impact:** No visual parity validation
**Blocks:**
- ✅ Phase 6 (visual parity results, SSIM scores table)

**Fix:**
- parity-harness-generator outputs structured JSON
- Per-screen: screenshot paths, SSIM scores, discrepancies

---

## 🟡 High-Priority Missing Files (P1)

| File | Impact | Pages Affected |
|------|--------|----------------|
| **coverage-audit.json** | No coverage heatmap | Phase 0 |
| **data-access.json** | No data access matrix | Phase 1 |
| **implementation-roadmap.json** | No waves timeline | Phase 4 |
| **security-review.json** | No security dashboard | Phase 6, Issues |
| **code-quality.json** | No linting metrics | Phase 5, Issues |

**Fix:** Enhance agents to output structured JSON alongside markdown

---

## ✅ What's Already Available

| File | Agent | Phase | Used By |
|------|-------|-------|---------|
| seam-proposals.json | seam-discovery | 0 | Overview, Phase 0, Phase 1 |
| project-facts.json | seam-discovery | 0 | Phase 0, Phase 2 |
| dependency-graph.json | seam-discovery | 0 | Phase 0, Phase 4 |
| database-schema.json | seam-discovery | 0 | Phase 0 |
| coverage-report.json | golden-baseline-capture | 0 | Phase 0 |
| discovery.md | discovery | 1 | Phase 1 |
| evidence-map.json | discovery | 1 | Phase 1 |
| readiness.json | discovery | 1 | Overview, Phase 1 |
| boundary-issues.json | discovery | 1 | Phase 1, Issues |
| requirements.md | spec-agent | 3 | Phase 3 |
| design.md | spec-agent | 3 | Phase 3 |
| tasks.md | spec-agent | 3 | Phase 3, Phase 5 |
| contracts/openapi.yaml | spec-agent | 3 | Phase 3 |
| security-review.md | code-security-reviewer | 6 | Phase 6 |
| VERIFICATION_SUMMARY.md | parity-harness-generator | 6 | Phase 6 |

---

## 🚀 Implementation Priorities

### Week 1: Fix Critical (P0)
1. **migration-state.json** — Orchestrator state manager
2. **test-results.json** — pytest/vitest JSON reporters
3. **tasks-status.json** — Parse tasks.md
4. **parity-results.json** — Enhance parity-harness output

**Outcome:** Core dashboard functional (Overview, Phase 5, Phase 6, Analytics)

---

### Week 2: Fix High-Priority (P1)
1. **coverage-audit.json** — seam-discovery enhancement
2. **data-access.json** — discovery agent enhancement
3. **implementation-roadmap.json** — roadmap generator
4. **security-review.json** — security reviewer enhancement
5. **code-quality.json** — lint/type check results

**Outcome:** All 11 pages fully functional

---

### Week 3: Nice-to-Have (P2-P3)
1. Lighthouse integration
2. SonarQube integration
3. Architecture diagram JSON
4. Component hierarchy JSON

**Outcome:** Enhanced visualizations and metrics

---

## 📋 Quick Reference: Agent Outputs

```
Phase 0: seam-discovery
  ✅ seam-proposals.json
  ✅ project-facts.json
  ✅ dependency-graph.json
  ❌ coverage-audit.json (P1)

Phase 0: golden-baseline-capture
  ✅ coverage-report.json
  ✅ baselines/*.png

Phase 1: discovery (per seam)
  ✅ discovery.md
  ✅ evidence-map.json
  ✅ readiness.json
  ❌ data-access.json (P1)

Phase 2: architecture
  ✅ architecture-design.md
  ❌ architecture-diagram.json (P2)

Phase 3: spec-agent (per seam)
  ✅ requirements.md
  ✅ design.md
  ✅ tasks.md
  ✅ openapi.yaml
  ❌ tasks-status.json (P0)
  ❌ requirements-stats.json (P2)

Phase 4: roadmap
  ✅ implementation-roadmap.md
  ❌ implementation-roadmap.json (P1)

Phase 5: backend/frontend-migration
  ❌ test-results.json (P0)
  ❌ code-quality.json (P1)
  ❌ implementation-log.json (P0 — part of migration-state)

Phase 6: code-security-reviewer
  ✅ security-review.md
  ❌ security-review.json (P1)

Phase 6: parity-harness-generator
  ✅ VERIFICATION_SUMMARY.md
  ❌ parity-results.json (P0)

Global: orchestrator
  ❌ migration-state.json (P0) — CRITICAL
```

---

## 🎯 Action Items for Agent Authors

### Immediate (P0):
- [ ] **orchestrator**: Create migration-state.json manager
- [ ] **backend/frontend-migration**: Run tests with JSON reporter
- [ ] **spec-agent**: Generate tasks-status.json from tasks.md
- [ ] **parity-harness**: Output parity-results.json

### High-Priority (P1):
- [ ] **seam-discovery**: Generate coverage-audit.json
- [ ] **discovery**: Generate data-access.json from analysis
- [ ] **roadmap**: Generate implementation-roadmap.json
- [ ] **security-reviewer**: Output security-review.json
- [ ] **backend/frontend-migration**: Capture lint/type check results

### Nice-to-Have (P2-P3):
- [ ] **Phase 2**: Generate architecture-diagram.json
- [ ] **spec-agent**: Generate requirements-stats.json
- [ ] **frontend-migration**: Run Lighthouse, save results
- [ ] **all agents**: Add SonarQube integration

---

## 💡 Workarounds (Until Gaps Fixed)

### Can Parse from Markdown:
- ✅ **data-access.json** → Parse discovery.md "Data Access" section
- ✅ **architecture-diagram.json** → Parse architecture-design.md
- ✅ **implementation-roadmap.json** → Parse implementation-roadmap.md waves

### Can Mock/Stub:
- ✅ **migration-state.json** → Use file modification timestamps as proxy
- ✅ **tasks-status.json** → All tasks marked "todo" initially

### Must Wait:
- ❌ **test-results.json** → Need real test execution
- ❌ **parity-results.json** → Need real visual comparison
- ❌ **Agent activity log** → Need real-time agent instrumentation

---

## 📊 Dashboard Page Readiness

| Page | Status | Blockers |
|------|--------|----------|
| 🏠 Overview | 🟡 Partial | migration-state.json (ETA/timeline) |
| 🔍 Phase 0 | 🟡 Partial | coverage-audit.json, iteration tracking |
| 🔬 Phase 1 | 🟢 Ready | Can parse data-access from discovery.md |
| 🏗️ Phase 2 | 🟢 Ready | Can parse markdown |
| 📝 Phase 3 | 🟡 Partial | tasks-status.json for Kanban |
| 🗺️ Phase 4 | 🟢 Ready | Can parse roadmap markdown |
| 🔨 Phase 5 | 🔴 Blocked | test-results.json, agent log |
| ✅ Phase 6 | 🟡 Partial | parity-results.json, security JSON |
| 📈 Analytics | 🔴 Blocked | migration-state.json history |
| 🎨 Artifacts | 🟢 Ready | No dependencies |
| 🚨 Issues | 🟡 Partial | Need structured quality/security JSONs |

**Legend:**
- 🟢 Ready: All data available or can be parsed
- 🟡 Partial: Core features work, some missing
- 🔴 Blocked: Critical data missing

---

## 🚦 Go/No-Go for Dashboard v1.0

### ✅ Can Launch MVP With:
- Existing markdown/JSON files
- Markdown parsing for missing JSONs
- Stubbed data for agent activity log

### ⚠️ Limited Functionality:
- No real-time agent activity feed
- No test quality metrics
- No velocity/trend analysis
- No visual parity validation

### ✅ Can Launch Full v1.0 After:
- Week 1 P0 fixes (migration-state.json, test-results, parity-results)
- Week 2 P1 fixes (structured JSON outputs)

---

**Recommendation:** Start dashboard implementation NOW with available data, fix critical gaps in parallel over 2 weeks. 🚀
