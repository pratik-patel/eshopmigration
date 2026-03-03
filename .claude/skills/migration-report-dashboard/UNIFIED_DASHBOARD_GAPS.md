# Unified Dashboard Data Gaps Analysis

**Created:** 2026-03-03
**Purpose:** Document all data sources, gaps, and solutions for unified dashboard

---

## 1. Data Availability Matrix

### ✅ FULLY AVAILABLE - Modern System (24 sources - 89%)

| # | Data Source | Location | Type | Status |
|---|-------------|----------|------|--------|
| 1 | Migration activity log | docs/tracking/migration-activity.jsonl | Hook | ✅ |
| 2 | Backend test results | docs/tracking/seams/{seam}/test-results-backend.json | Hook | ✅ |
| 3 | Frontend test results | docs/tracking/seams/{seam}/test-results-frontend.json | Hook | ✅ |
| 4 | Backend coverage | docs/tracking/seams/{seam}/coverage-backend.json | Hook | ✅ |
| 5 | Frontend coverage | docs/tracking/seams/{seam}/coverage-frontend.json | Hook | ✅ |
| 6 | Code quality | docs/tracking/seams/{seam}/code-quality.json | Hook | ✅ |
| 7 | Parity results | docs/tracking/seams/{seam}/parity-results.json | Hook | ✅ |
| 8 | UI behavior | docs/tracking/seams/{seam}/ui-behavior.json | Hook | ✅ |
| 9 | Backend dependencies | docs/tracking/seams/{seam}/dependency-scan-backend.json | Hook | ✅ |
| 10 | Frontend dependencies | docs/tracking/seams/{seam}/dependency-scan-frontend.json | Hook | ✅ |
| 11 | Lighthouse metrics | docs/tracking/seams/{seam}/lighthouse-results.json | Hook | ✅ |
| 12 | Backend file changes | docs/tracking/seams/{seam}/file-changes-backend.json | Hook | ✅ |
| 13 | Frontend file changes | docs/tracking/seams/{seam}/file-changes-frontend.json | Hook | ✅ |
| 14 | Seam proposals | docs/context-fabric/seam-proposals.json | Agent | ✅ |
| 15 | Project facts | docs/context-fabric/project-facts.json | Agent | ✅ |
| 16 | Dependency graph | docs/context-fabric/dependency-graph.json | Agent | ✅ |
| 17 | Database schema | docs/context-fabric/database-schema.json | Agent | ✅ |
| 18 | Design system | docs/context-fabric/design-system.json | Agent | ✅ |
| 19 | Seam discovery | docs/seams/{seam}/discovery.md | Agent | ✅ |
| 20 | Seam readiness | docs/seams/{seam}/readiness.json | Agent | ✅ |
| 21 | Requirements | docs/seams/{seam}/requirements.md | Agent | ✅ |
| 22 | Design specs | docs/seams/{seam}/design.md | Agent | ✅ |
| 23 | Tasks checklist | docs/seams/{seam}/tasks.md | Agent | ✅ |
| 24 | OpenAPI contract | docs/seams/{seam}/contracts/openapi.yaml | Agent | ✅ |

---

### ⚠️ DERIVABLE - Dashboard Logic (2 sources - 7%)

| # | Data Source | Derivation Method | Input Files | Effort |
|---|-------------|-------------------|-------------|--------|
| 25 | Critical path | Longest path algorithm | dependency-graph.json, implementation-roadmap.md | 2 hours |
| 26 | Priority matrix | User input + readiness | readiness.json + user form | 1 hour |

**Implementation:**
```python
# unified-app/lib/derived_data.py

def calculate_critical_path(dependency_graph: dict) -> dict:
    """
    Find longest path through dependency graph (critical path)

    Input: docs/context-fabric/dependency-graph.json
    Output: List of seams in critical path with estimated duration
    """
    # Algorithm: Dynamic programming for longest path in DAG
    pass

def calculate_priority_matrix(readiness_data: dict, business_value: dict) -> dict:
    """
    Create priority matrix (business value vs complexity)

    Input:
    - readiness.json (complexity from score)
    - User input form (business value 1-10)
    Output: Scatter plot data points
    """
    pass
```

---

### ❌ MISSING - Legacy System (5 sources - 18%)

**These require mock data as legacy system metrics aren't captured automatically**

| # | Data Source | Purpose | Mock Location | Format |
|---|-------------|---------|---------------|--------|
| 27 | Legacy metrics | Response times, throughput, error rates | mock-data/legacy/legacy-metrics.xml | XML |
| 28 | Legacy code stats | LOC, complexity, tech debt | mock-data/legacy/legacy-code-stats.xml | XML |
| 29 | Legacy test results | Test coverage %, pass rate | mock-data/legacy/legacy-test-results.xml | XML |
| 30 | Legacy dependencies | Library versions, CVEs | mock-data/legacy/legacy-dependencies.xml | XML |
| 31 | Legacy architecture | Layers, patterns, components | mock-data/legacy/legacy-architecture.xml | XML |

**Why Mock?**
- Legacy system is being replaced (no longer instrumented)
- Historical data may not have been collected
- Focus is on forward progress, not legacy analysis

**Mock Data Structure:**
```xml
<!-- mock-data/legacy/legacy-metrics.xml -->
<metrics>
  <performance>
    <response_time unit="ms" p50="350" p95="1200" p99="2500"/>
    <throughput unit="req/sec" value="45"/>
    <error_rate unit="percent" value="2.3"/>
  </performance>
  <resources>
    <memory unit="MB" avg="512" max="1024"/>
    <cpu unit="percent" avg="65" max="95"/>
  </resources>
</metrics>
```

---

## 2. Feature Comparison

### Features in `progress-app/` (Not in `app/`)

| Feature | Description | Data Source |
|---------|-------------|-------------|
| Phase progress tracker | 7-phase completion % | Derived from seam artifacts |
| Seam status matrix | All seams with readiness | readiness.json |
| Migration health score | 0-100 weighted score | Calculated from multiple sources |
| Agent activity log | Real-time agent execution | migration-activity.jsonl |
| Critical blockers count | Boundary issues | boundary-issues.json |

### Features in `app/` (Not in `progress-app/`)

| Feature | Description | Data Source |
|---------|-------------|-------------|
| Legacy vs Modern comparison | Side-by-side comparison | Legacy XML + Modern JSON |
| Frontend component analysis | React vs legacy UI | UI behavior + design system |
| Backend API comparison | Endpoints, performance | OpenAPI + legacy architecture |
| Comprehensive quality dashboard | Multi-dimensional quality | Test results, coverage, code quality |
| Summary report | Executive summary | Aggregated metrics |

### New Features in Unified Dashboard

| Feature | Description | Data Source | Effort |
|---------|-------------|-------------|--------|
| Discovery page | Context fabric explorer | context-fabric/* | 2 hours |
| Specifications page | Requirements + Tasks Kanban | requirements.md, tasks.md | 3 hours |
| Roadmap page | Implementation waves | Derived from dependencies | 2 hours |
| Database page | Schema comparison | database-schema.json + legacy XML | 2 hours |
| Security page | OWASP Top 10 + CVEs | dependency-scan + security-review | 2 hours |
| Parity page | Screenshot comparison | SSIM scores + screenshots | 2 hours |

---

## 3. Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Unified Dashboard                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ├─────────────────┐
                              │                 │
                    ┌─────────▼──────┐  ┌──────▼──────────┐
                    │ Legacy System  │  │ Modern System   │
                    │   (Mock XML)   │  │  (Real JSON)    │
                    └─────────┬──────┘  └──────┬──────────┘
                              │                 │
        ┌─────────────────────┼─────────────────┼─────────┐
        │                     │                 │         │
        │              ┌──────▼──────┐   ┌──────▼──────┐  │
        │              │ XML Parser  │   │ JSON Loader │  │
        │              └──────┬──────┘   └──────┬──────┘  │
        │                     │                 │         │
        │                     └────────┬────────┘         │
        │                              │                  │
        │                    ┌─────────▼─────────┐        │
        │                    │  Unified Loader   │        │
        │                    └─────────┬─────────┘        │
        │                              │                  │
        │              ┌───────────────┼──────────────┐   │
        │              │               │              │   │
        │       ┌──────▼──────┐ ┌──────▼──────┐ ┌────▼───▼──┐
        │       │  Comparison │ │   Progress  │ │  Quality  │
        │       │   Engine    │ │   Tracker   │ │  Analysis │
        │       └──────┬──────┘ └──────┬──────┘ └────┬──────┘
        │              │               │              │
        │              └───────────────┼──────────────┘
        │                              │
        │                    ┌─────────▼─────────┐
        │                    │   Visualization   │
        │                    │      Pages        │
        │                    └───────────────────┘
        │                              │
        └──────────────────────────────┘
                    11 Pages Total
```

---

## 4. Known Limitations

### L1 - Mock Legacy Data
**Issue:** Legacy system metrics are mocked, not real
**Impact:** Comparison analysis shows estimated legacy baseline, not actual
**Mitigation:** Clearly label as "Estimated" in UI
**Severity:** Low (still valuable for decision-making)

### L2 - No Runtime Metrics
**Issue:** Legacy runtime performance not instrumented
**Impact:** Can't show real-time legacy performance degradation
**Mitigation:** Use Lighthouse for modern system performance
**Severity:** Low (not critical for migration decisions)

### L3 - User Input Required
**Issue:** Business value scoring requires manual input
**Impact:** Priority matrix incomplete without user input
**Mitigation:** Add form for users to score business value (1-10)
**Severity:** Medium (affects roadmap prioritization)

### L4 - Single Seam Focus
**Issue:** Current migration has only 1 seam (catalog-management)
**Impact:** Can't demonstrate multi-seam dependency visualization
**Mitigation:** Works correctly, just less visually impressive
**Severity:** Low (not a technical limitation)

---

## 5. Data Quality Validation

### Validation Rules

```python
# unified-app/lib/validators.py

def validate_modern_data():
    """Validate modern system data completeness"""
    required_files = [
        'docs/context-fabric/seam-proposals.json',
        'docs/tracking/migration-activity.jsonl',
        # ... all 24 files
    ]

    missing = []
    for file in required_files:
        if not Path(file).exists():
            missing.append(file)

    return {
        'valid': len(missing) == 0,
        'missing': missing,
        'coverage': f"{(24 - len(missing)) / 24 * 100:.1f}%"
    }

def validate_mock_data():
    """Validate mock legacy data exists"""
    required_mocks = [
        'mock-data/legacy/legacy-metrics.xml',
        'mock-data/legacy/legacy-code-stats.xml',
        'mock-data/legacy/legacy-test-results.xml',
        'mock-data/legacy/legacy-dependencies.xml',
        'mock-data/legacy/legacy-architecture.xml',
    ]

    missing = []
    for file in required_mocks:
        if not Path(file).exists():
            missing.append(file)

    return {
        'valid': len(missing) == 0,
        'missing': missing
    }
```

---

## 6. Roadmap to 100% Coverage

### Current: 89% (24/27 data sources)

| Step | Action | Effort | Coverage After |
|------|--------|--------|----------------|
| 1 | Implement critical path derivation | 2 hours | 93% (25/27) |
| 2 | Create priority matrix UI form | 1 hour | 96% (26/27) |
| 3 | Create mock legacy XML files | 1 hour | 100% (31/31) |

**Total to 100%: 4 hours**

---

## 7. Recommendations

### Immediate (Do Now)
1. ✅ Create this gap analysis document
2. ⏳ Create mock legacy XML files (1 hour)
3. ⏳ Implement unified data loaders (2 hours)
4. ⏳ Port existing pages to unified structure (4 hours)

### Short-term (This Week)
5. ⏳ Implement critical path calculation (2 hours)
6. ⏳ Create priority matrix UI form (1 hour)
7. ⏳ Add data validation and error handling (2 hours)

### Long-term (Future)
8. Replace mock legacy data with real data if available
9. Add export functionality (PDF reports)
10. Add real-time auto-refresh (file watcher)

---

## 8. Success Criteria

**Dashboard is complete when:**
- ✅ 100% data coverage (31/31 sources)
- ✅ All 11 pages functional
- ✅ Legacy vs Modern comparison working
- ✅ Progress tracking working
- ✅ Quality metrics working
- ✅ No errors with real migration data
- ✅ Gaps clearly documented in UI

---

**Status:** Ready to implement unified dashboard
**Next Step:** Create mock legacy XML files
