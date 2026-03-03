# Unified Dashboard Implementation Plan

**Created:** 2026-03-03
**Goal:** Combine `app/` and `progress-app/` into single comprehensive dashboard

---

## Current State Analysis

### Dashboard 1: `progress-app/` (Migration Progress Tracker)
**Pages:** 1 (Overview)
**Focus:** Real-time migration progress tracking

**Features:**
- ✅ Migration health score (0-100)
- ✅ Phase progress (7 phases)
- ✅ Seam status matrix
- ✅ Agent activity tracking
- ✅ Key insights
- ✅ Critical blockers count

**Data Sources:**
- docs/context-fabric/seam-proposals.json
- docs/seams/{seam}/readiness.json
- docs/seams/{seam}/discovery.md
- docs/seams/{seam}/boundary-issues.json
- docs/tracking/migration-activity.jsonl

---

### Dashboard 2: `app/` (Legacy vs Modern Comparison)
**Pages:** 5 (Home, Frontend, Backend, Quality, Summary)
**Focus:** Comparative analysis of legacy and modern systems

**Features:**
- ✅ Overall migration score
- ✅ Frontend comparison (legacy vs modern)
- ✅ Backend comparison (legacy vs modern)
- ✅ Quality metrics (coverage, tests)
- ✅ Comprehensive summary

**Data Sources:**
- Collectors for various metrics
- Configuration files
- External API calls (?)

---

## Data Availability (from DATA_REQUIREMENTS_STATUS.md)

### ✅ Available (24 files - 89%)

**From Hooks:**
1. migration-activity.jsonl ✅
2. test-results-backend.json ✅
3. test-results-frontend.json ✅
4. coverage-backend.json ✅
5. coverage-frontend.json ✅
6. code-quality.json ✅
7. parity-results.json ✅
8. ui-behavior.json ✅
9. dependency-scan-backend.json ✅
10. dependency-scan-frontend.json ✅
11. lighthouse-results.json ✅
12. file-changes-backend.json ✅
13. file-changes-frontend.json ✅

**From Agent Artifacts:**
14. docs/context-fabric/seam-proposals.json ✅
15. docs/context-fabric/project-facts.json ✅
16. docs/context-fabric/dependency-graph.json ✅
17. docs/seams/{seam}/discovery.md ✅
18. docs/seams/{seam}/readiness.json ✅
19. docs/seams/{seam}/requirements.md ✅
20. docs/seams/{seam}/design.md ✅
21. docs/seams/{seam}/tasks.md ✅
22. docs/seams/{seam}/contracts/openapi.yaml ✅
23. docs/seams/{seam}/boundary-issues.json ✅
24. CLAUDE.md ✅

### ⏳ Data Gaps (3 files - 11%)

**P1 High Priority:**
1. **critical-path.json** - Can derive from dependency-graph.json
2. **priority-matrix.json** - Need user input form for business value

**P3 Low Priority:**
3. **runtime-metrics.json** - Skip (use Lighthouse instead)

### ❌ Legacy System Data (MISSING)

**Need Mock XML for Legacy System:**
1. **legacy-metrics.xml** - Legacy app metrics (response times, throughput)
2. **legacy-code-stats.xml** - Legacy codebase statistics (LOC, complexity)
3. **legacy-test-results.xml** - Legacy test coverage and results
4. **legacy-dependencies.xml** - Legacy dependency vulnerabilities
5. **legacy-architecture.xml** - Legacy architecture description

---

## Unified Dashboard Structure

### **Pages (11 total)**

#### **Section 1: Overview (2 pages)**
1. **🏠 Home** - Executive dashboard
   - Migration health score
   - Overall progress
   - Key metrics
   - Quick actions

2. **📊 Progress Tracker** - Real-time migration progress
   - Phase progress (7 phases)
   - Seam status matrix
   - Agent activity log
   - Velocity metrics

#### **Section 2: Migration Deep Dive (3 pages)**
3. **🔍 Discovery** - Seam discovery and analysis
   - Context fabric explorer
   - Dependency graph
   - Coverage heatmap

4. **📝 Specifications** - Requirements and design
   - Per-seam requirements
   - Tasks Kanban board
   - OpenAPI spec viewer

5. **🗺️ Roadmap** - Implementation plan
   - Implementation waves
   - Critical path diagram
   - Priority matrix

#### **Section 3: Comparison Analysis (3 pages)**
6. **🎨 Frontend** - Frontend comparison
   - Legacy vs Modern UI
   - Component mapping
   - Design system comparison

7. **⚙️ Backend** - Backend comparison
   - Legacy vs Modern API
   - Architecture comparison
   - Performance comparison

8. **🗄️ Database** - Data layer comparison
   - Schema comparison
   - Query patterns
   - Migration strategy

#### **Section 4: Quality & Validation (3 pages)**
9. **✅ Quality** - Code quality metrics
   - Test coverage
   - Code quality scores
   - Linting results

10. **🔒 Security** - Security analysis
    - Vulnerability scan
    - OWASP Top 10 checklist
    - Dependency audit

11. **🎯 Parity** - Visual parity validation
    - Screenshot comparison
    - SSIM scores
    - Lighthouse scores

---

## Implementation Strategy

### Phase 1: Create Unified Structure (2 hours)
1. Create new `unified-app/` directory
2. Merge page structures from both apps
3. Create unified navigation
4. Implement shared state management

### Phase 2: Mock Legacy Data (1 hour)
1. Create `mock-data/legacy/` directory
2. Generate XML files for legacy system:
   - `legacy-metrics.xml`
   - `legacy-code-stats.xml`
   - `legacy-test-results.xml`
   - `legacy-dependencies.xml`
   - `legacy-architecture.xml`
3. Create XML parsers

### Phase 3: Unified Data Loaders (3 hours)
1. Create `loaders/legacy_loader.py` (XML parser)
2. Create `loaders/modern_loader.py` (JSON parser)
3. Create `loaders/unified_loader.py` (combines both)
4. Implement caching and error handling

### Phase 4: Migrate Existing Pages (4 hours)
1. Merge Home page (from both apps)
2. Port Progress Tracker (from progress-app)
3. Port Frontend, Backend, Quality, Summary (from app)
4. Add new Discovery, Specifications, Roadmap pages
5. Add new Database, Security, Parity pages

### Phase 5: Derive Missing Data (2 hours)
1. Implement critical path calculation
2. Create priority matrix UI form
3. Generate comparison metrics

### Phase 6: Testing & Polish (2 hours)
1. Test all pages with real data
2. Test with mock legacy data
3. Fix styling and layout issues
4. Add loading states and error handling

**Total Effort: 14 hours (2 days)**

---

## Data Source Mapping

### Legacy System (Mock XML)
```
mock-data/legacy/
├── legacy-metrics.xml          → Response times, throughput, errors
├── legacy-code-stats.xml       → LOC, complexity, tech debt
├── legacy-test-results.xml     → Test count, coverage %, pass rate
├── legacy-dependencies.xml     → Library versions, vulnerabilities
└── legacy-architecture.xml     → Layers, components, patterns
```

### Modern System (Real JSON + Derived)
```
docs/
├── context-fabric/             → Seam proposals, dependency graph
├── seams/{seam}/               → Discovery, requirements, tasks
└── tracking/
    ├── migration-activity.jsonl    → Agent activity
    └── seams/{seam}/
        ├── test-results-*.json     → Test results
        ├── coverage-*.json         → Coverage data
        ├── lighthouse-*.json       → Performance
        └── dependency-scan-*.json  → Vulnerabilities
```

### Derived Data (Dashboard Logic)
```python
# In unified-app/lib/derived_data.py
def calculate_critical_path(dependency_graph, roadmap):
    # Longest path algorithm
    pass

def calculate_priority_matrix(readiness_data, business_value_input):
    # Complexity from readiness, business value from user
    pass

def compare_architectures(legacy_xml, modern_facts):
    # Parse and compare
    pass
```

---

## Gap Analysis Document

Create `UNIFIED_DASHBOARD_GAPS.md` documenting:

1. **Data Gaps:**
   - Where legacy data comes from (mock XML)
   - Where modern data comes from (hooks + artifacts)
   - What data needs derivation (critical path, priority matrix)

2. **Feature Gaps:**
   - What's in app/ but not in progress-app/
   - What's in progress-app/ but not in app/
   - What's new in unified dashboard

3. **Known Limitations:**
   - Mock data vs real data
   - Missing runtime metrics
   - User input required for business value

---

## Next Steps

1. ✅ Read this plan
2. ⏳ Create mock legacy XML files
3. ⏳ Create unified-app/ structure
4. ⏳ Implement data loaders
5. ⏳ Port and merge pages
6. ⏳ Test with real migration data
7. ⏳ Document gaps

---

**Ready to proceed?** I can start implementing the unified dashboard now.
