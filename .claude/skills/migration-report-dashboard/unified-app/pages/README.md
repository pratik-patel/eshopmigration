# Unified Migration Dashboard Pages

This directory contains all Streamlit pages for the unified migration dashboard.

## Pages Created

1. **2_📊_Progress_Tracker.py** (Reference page - already existed)
   - Phase progress tracking
   - Seam status details
   - Agent activity log

2. **3_🔍_Discovery.py** ✅ NEW
   - Seam proposals from discovery
   - Context fabric manifest
   - Coverage reports
   - Dependency visualization

3. **4_📝_Specifications.py** ✅ NEW
   - Requirements documents per seam
   - Design documents
   - Task breakdowns with checklist tracking
   - OpenAPI contract viewer with endpoint summary

4. **5_🗺️_Roadmap.py** ✅ NEW
   - Implementation waves
   - Timeline view with duration extraction
   - Seam dependencies and critical path

5. **6_🎨_Frontend_Comparison.py** ✅ NEW
   - Component mapping (legacy UI vs modern React)
   - Screenshot comparison
   - Lighthouse performance metrics (Core Web Vitals)
   - UI bundle size and component distribution

6. **7_⚙️_Backend_Comparison.py** ✅ NEW
   - API endpoint comparison
   - Performance metrics (throughput, response times)
   - Data access patterns
   - Architecture comparison

7. **8_🗄️_Database_Comparison.py** ✅ NEW
   - Schema comparison
   - Data model comparison (EF vs SQLAlchemy)
   - Migration status and scripts
   - Query pattern examples

8. **9_✅_Quality.py** ✅ NEW
   - Test coverage by seam (backend + frontend)
   - Test results with pass/fail tracking
   - Code quality metrics
   - Linting status and quality gates

9. **10_🔒_Security.py** ✅ NEW
   - Vulnerability scans (dependency scanning)
   - OWASP Top 10 compliance checklist
   - Security score calculation
   - Security review status per seam

10. **11_🎯_Parity.py** ✅ NEW
    - Visual parity validation with screenshots
    - Behavioral parity testing
    - Feature checklist tracking
    - API diff analysis and response comparison

## Common Patterns

All pages follow these conventions:

### Import Pattern
```python
import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.unified_loader import UnifiedDataLoader
```

### Data Loading
```python
@st.cache_resource
def get_data_loader():
    return UnifiedDataLoader(
        docs_path="../../../../docs",
        mock_legacy_path="../../mock-data/legacy"
    )
```

### Page Structure
- **Page config** with emoji and wide layout
- **Error handling** for missing data with helpful messages
- **Tabs** for organizing content
- **Metrics** with columns for key stats
- **Progress bars** for completion tracking
- **Expanders** for detailed information
- **Dataframes** for tabular data
- **Status icons** (✅ 🔵 🟡 🔴 ⏸️) for visual clarity

### Empty State Handling
All pages gracefully handle:
- Missing data files
- Seams not yet discovered
- Features not yet implemented
- Tests not yet run

With helpful messages like:
- "No seams discovered yet. Run Phase 0 (Discovery Loop) first."
- "Feature not yet implemented for this seam."
- "Data not available. Check paths and data sources."

## Data Sources

Pages load data from:
- `docs/context-fabric/` - Discovery outputs
- `docs/seams/{seam}/` - Per-seam documentation
- `docs/tracking/` - Test results, coverage, scans
- `docs/parity-validation/` - Parity validation results
- `mock-data/legacy/` - Legacy system mock data

## Running the Dashboard

From the unified-app directory:
```bash
streamlit run 1_🏠_Home.py
```

Navigate between pages using the sidebar.
