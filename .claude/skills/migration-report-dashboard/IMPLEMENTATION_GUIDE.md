# 🛠️ Migration Progress Dashboard — Implementation Guide

**Quick Start:** Get the dashboard running in 15 minutes

---

## 📋 Prerequisites

- Python 3.12+
- Migration artifacts in `docs/` directory
- `seam-proposals.json` exists (Phase 0 complete)

---

## 🚀 Installation Steps

### Step 1: Install Dependencies

```bash
cd .claude/skills/migration-report-dashboard

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install Python packages
pip install -r requirements.txt
```

**Required packages** (`requirements.txt`):
```
streamlit==1.31.0
pandas==2.2.0
plotly==5.18.0
pyyaml==6.0.1
markdown==3.5.1
watchdog==4.0.0
Pillow==10.2.0
```

### Step 2: Verify Data Structure

```bash
# Check required files exist
ls docs/context-fabric/seam-proposals.json
ls docs/context-fabric/project-facts.json

# Optional: Run data validator
python scripts/validate_data.py
```

### Step 3: Configure Dashboard

Edit `config.yaml`:

```yaml
dashboard:
  title: "eShop Migration Progress"
  docs_path: "../../docs"  # Relative to dashboard root
  refresh_interval: 5  # seconds
  theme: "light"  # or "dark"
  port: 8501

phases:
  enabled:
    - phase_0
    - phase_1
    - phase_2
    - phase_3
    - phase_4
    - phase_5
    - phase_6

  # Auto-hide phases not started yet
  hide_not_started: false

insights:
  enabled: true
  min_confidence: 0.7  # 0-1 scale
```

### Step 4: Launch Dashboard

```bash
streamlit run app/main.py

# Open browser → http://localhost:8501
```

---

## 📁 Project Structure

```
.claude/skills/migration-report-dashboard/
├── app/
│   ├── main.py                    # 🎯 Entry point
│   ├── pages/
│   │   ├── 01_📊_Overview.py      # Home dashboard
│   │   ├── 02_🔍_Phase_0.py       # Discovery Loop
│   │   ├── 03_🔬_Phase_1.py       # Per-Seam Discovery
│   │   ├── 04_🏗️_Phase_2.py       # Architecture
│   │   ├── 05_📝_Phase_3.py       # Specifications
│   │   ├── 06_🗺️_Phase_4.py       # Roadmap
│   │   ├── 07_🔨_Phase_5.py       # Implementation
│   │   ├── 08_✅_Phase_6.py       # Validation
│   │   ├── 09_📈_Analytics.py     # Trends & Forecasting
│   │   ├── 10_🎨_Artifacts.py     # File Browser
│   │   └── 11_🚨_Issues.py        # Blockers & Warnings
│   ├── lib/
│   │   ├── __init__.py
│   │   ├── data_loader.py         # Load artifacts from docs/
│   │   ├── metrics.py             # Calculate scores
│   │   ├── visualizations.py      # Plotly charts
│   │   ├── insights.py            # Automated insights engine
│   │   └── state.py               # Migration state management
│   ├── components/
│   │   ├── __init__.py
│   │   ├── seam_card.py           # Seam info card
│   │   ├── progress_bar.py        # Custom progress indicator
│   │   ├── status_badge.py        # Status badge component
│   │   └── dependency_graph.py    # Network graph visualization
│   └── utils/
│       ├── __init__.py
│       ├── file_watcher.py        # Real-time updates
│       ├── parsers.py             # Markdown/JSON parsers
│       └── exporters.py           # Export to PDF/Excel/ZIP
├── scripts/
│   ├── validate_data.py           # Check data completeness
│   ├── generate_sample_data.py    # For testing without real migration
│   └── export_report.py           # CLI export tool
├── tests/
│   ├── test_data_loader.py
│   ├── test_metrics.py
│   └── test_visualizations.py
├── static/
│   ├── styles.css                 # Custom CSS
│   └── logo.png                   # Dashboard logo
├── config.yaml                    # Dashboard configuration
├── requirements.txt               # Python dependencies
├── PROGRESS_DASHBOARD_SPEC.md     # Full specification
├── IMPLEMENTATION_GUIDE.md        # This file
└── README.md                      # Quick start guide
```

---

## 🔧 Implementation Roadmap

### Sprint 1: Core Infrastructure (3 days)

**Day 1: Data Loading**
- ✅ Implement `data_loader.py`
  - Load seam-proposals.json
  - Load discovery.md per seam
  - Load readiness.json per seam
  - Load requirements.md, design.md, tasks.md
- ✅ Implement `metrics.py`
  - Calculate migration health score
  - Calculate phase completion %
  - Calculate seam readiness scores
- ✅ Implement `state.py`
  - Migration state management
  - Current phase tracking
  - Agent activity log

**Day 2: Main Page & Navigation**
- ✅ Implement `main.py`
  - Sidebar navigation
  - Header with hero score
  - Page routing
- ✅ Implement `01_Overview.py`
  - Hero section (migration health score)
  - Phase progress cards
  - Seam status matrix
  - Key insights panel

**Day 3: Basic Visualizations**
- ✅ Implement `visualizations.py`
  - Progress bar charts (Plotly)
  - Seam status pie chart
  - Phase timeline
- ✅ Implement reusable components
  - `seam_card.py`
  - `progress_bar.py`
  - `status_badge.py`

**Deliverable:** Basic dashboard showing overview with real data

---

### Sprint 2: Phase Pages (5 days)

**Day 4: Phase 0 & 1**
- ✅ Implement `02_Phase_0.py`
  - Discovery iterations timeline
  - Seam dependency graph (Cytoscape.js)
  - Coverage heatmap
  - Context Fabric Explorer
- ✅ Implement `03_Phase_1.py`
  - Seam selector dropdown
  - Seam overview card
  - Call chain visualizer
  - Data access matrix

**Day 5: Phase 2 & 3**
- ✅ Implement `04_Phase_2.py`
  - Architecture diagram
  - Tech stack comparison table
  - Design patterns library
- ✅ Implement `05_Phase_3.py`
  - Requirements viewer (EARS format)
  - Design components diagram
  - Tasks Kanban board
  - OpenAPI spec viewer (Swagger UI)

**Day 6: Phase 4 & 5**
- ✅ Implement `06_Phase_4.py`
  - Implementation waves timeline
  - Dependency flow diagram
  - Priority matrix (scatter plot)
- ✅ Implement `07_Phase_5.py`
  - Real-time progress tracker
  - Code quality dashboard
  - Agent activity log
  - File changes heatmap

**Day 7: Phase 6**
- ✅ Implement `08_Phase_6.py`
  - Security review dashboard (OWASP checklist)
  - Visual parity results (SSIM scores)
  - Side-by-side screenshot comparison
  - Dependency vulnerability scan

**Day 8: Polish**
- ✅ Styling & responsiveness
- ✅ Error handling for missing data
- ✅ Loading states

**Deliverable:** All phase pages functional

---

### Sprint 3: Advanced Features (4 days)

**Day 9: Analytics**
- ✅ Implement `09_Analytics.py`
  - Migration velocity chart
  - Quality trends over time
  - Effort distribution pie chart
  - Forecast completion date

**Day 10: Artifacts & Issues**
- ✅ Implement `10_Artifacts.py`
  - File browser with search
  - Markdown/JSON viewer
  - Download single file
  - Bulk export (ZIP)
- ✅ Implement `11_Issues.py`
  - Critical blockers table
  - Warnings list
  - Boundary issues aggregator

**Day 11: Insights Engine**
- ✅ Implement `insights.py`
  - Pattern detection (blockers by type)
  - Performance regressions
  - Coverage gaps
  - Automated recommendations
- ✅ Display insights on Overview page

**Day 12: Real-Time Updates**
- ✅ Implement `file_watcher.py`
  - Watch docs/ directory for changes
  - Auto-refresh dashboard
- ✅ Implement polling fallback
- ✅ WebSocket push (optional)

**Deliverable:** Feature-complete dashboard

---

### Sprint 4: Export & Documentation (2 days)

**Day 13: Export Functionality**
- ✅ Implement `exporters.py`
  - Export to PDF (executive summary)
  - Export to Excel (metrics table)
  - Export to ZIP (all artifacts)
- ✅ CLI export tool (`scripts/export_report.py`)

**Day 14: Documentation & Testing**
- ✅ Write README.md
- ✅ Write usage guide
- ✅ Unit tests for data loading
- ✅ Integration tests for metrics
- ✅ User acceptance testing

**Deliverable:** Production-ready dashboard

---

## 💻 Code Examples

### Data Loader Example

```python
# app/lib/data_loader.py
import json
from pathlib import Path
from typing import Dict, List, Optional

class MigrationDataLoader:
    def __init__(self, docs_path: str = "docs/"):
        self.docs_path = Path(docs_path)
        self._cache = {}

    def load_seam_proposals(self) -> Dict:
        """Load all discovered seams."""
        if "seam_proposals" in self._cache:
            return self._cache["seam_proposals"]

        path = self.docs_path / "context-fabric/seam-proposals.json"
        if not path.exists():
            return {"seams": []}

        data = json.loads(path.read_text())
        self._cache["seam_proposals"] = data
        return data

    def get_all_seams(self) -> List[str]:
        """Get list of all seam names."""
        proposals = self.load_seam_proposals()
        return [seam["name"] for seam in proposals.get("seams", [])]

    def load_seam_discovery(self, seam_name: str) -> Optional[str]:
        """Load discovery.md for a seam."""
        path = self.docs_path / f"seams/{seam_name}/discovery.md"
        if not path.exists():
            return None
        return path.read_text()

    def load_seam_readiness(self, seam_name: str) -> Optional[Dict]:
        """Load readiness.json for a seam."""
        path = self.docs_path / f"seams/{seam_name}/readiness.json"
        if not path.exists():
            return None
        return json.loads(path.read_text())

    def get_phase_completion(self) -> Dict[str, float]:
        """Calculate completion % for each phase."""
        seams = self.get_all_seams()
        total_seams = len(seams)

        if total_seams == 0:
            return {f"phase_{i}": 0.0 for i in range(7)}

        # Phase 0: Check coverage
        coverage_report = self.docs_path / "legacy-golden/coverage-report.json"
        phase_0 = 100.0 if coverage_report.exists() and \
                  json.loads(coverage_report.read_text()).get("coverage_percentage") == 100 else 0.0

        # Phase 1: Count seams with discovery.md
        phase_1 = sum(1 for s in seams if (self.docs_path / f"seams/{s}/discovery.md").exists()) / total_seams * 100

        # Phase 2: Check architecture docs
        arch_exists = (self.docs_path / "architecture-design.md").exists()
        phase_2 = 100.0 if arch_exists else 0.0

        # Phase 3: Count seams with requirements.md
        phase_3 = sum(1 for s in seams if (self.docs_path / f"seams/{s}/requirements.md").exists()) / total_seams * 100

        # Phase 4: Check roadmap
        roadmap_exists = (self.docs_path / "implementation-roadmap.md").exists()
        phase_4 = 100.0 if roadmap_exists else 0.0

        # Phase 5: Count seams with implementation-summary.md
        phase_5 = sum(1 for s in seams if (self.docs_path / f"seams/{s}/implementation-summary.md").exists()) / total_seams * 100

        # Phase 6: Count seams with security-review.md
        phase_6 = sum(1 for s in seams if (self.docs_path / f"seams/{s}/security-review.md").exists()) / total_seams * 100

        return {
            "phase_0": phase_0,
            "phase_1": phase_1,
            "phase_2": phase_2,
            "phase_3": phase_3,
            "phase_4": phase_4,
            "phase_5": phase_5,
            "phase_6": phase_6,
        }
```

### Metrics Calculator Example

```python
# app/lib/metrics.py
from typing import Dict, List
from .data_loader import MigrationDataLoader

class MigrationMetrics:
    def __init__(self, loader: MigrationDataLoader):
        self.loader = loader

    def calculate_migration_health_score(self) -> int:
        """Calculate overall migration health (0-100)."""
        phase_completion = self.loader.get_phase_completion()

        # Phase completion (30%)
        phase_score = sum(phase_completion.values()) / 7 * 0.3

        # Seam readiness (40%)
        seams = self.loader.get_all_seams()
        if len(seams) == 0:
            return 0

        readiness_scores = []
        for seam in seams:
            readiness = self.loader.load_seam_readiness(seam)
            if readiness:
                readiness_scores.append(readiness.get("score", 0))

        avg_readiness = sum(readiness_scores) / len(readiness_scores) if readiness_scores else 0
        seam_score = (avg_readiness / 100) * 0.4 * 100

        # Quality gates (20%)
        # TODO: Parse test-results.json for coverage
        quality_score = 0.8 * 20  # Placeholder: 80% quality

        # Blockers penalty (10%)
        num_blockers = self._count_critical_blockers()
        blocker_penalty = min(10, num_blockers * 2)

        total = phase_score + seam_score + quality_score - blocker_penalty
        return round(total)

    def _count_critical_blockers(self) -> int:
        """Count critical blockers across all seams."""
        seams = self.loader.get_all_seams()
        blocker_count = 0

        for seam in seams:
            boundary_issues_path = self.loader.docs_path / f"seams/{seam}/boundary-issues.json"
            if boundary_issues_path.exists():
                issues = json.loads(boundary_issues_path.read_text())
                blocker_count += len([i for i in issues.get("issues", []) if i.get("severity") == "critical"])

        return blocker_count

    def get_seam_status_distribution(self) -> Dict[str, int]:
        """Get distribution of seam statuses."""
        seams = self.loader.get_all_seams()
        statuses = {"complete": 0, "in_progress": 0, "blocked": 0, "not_started": 0}

        for seam in seams:
            readiness = self.loader.load_seam_readiness(seam)
            if not readiness:
                statuses["not_started"] += 1
                continue

            score = readiness.get("score", 0)
            if score >= 95:
                statuses["complete"] += 1
            elif score >= 50:
                statuses["in_progress"] += 1
            else:
                statuses["blocked"] += 1

        return statuses
```

### Streamlit Page Example

```python
# app/pages/01_📊_Overview.py
import streamlit as st
import plotly.graph_objects as go
from lib.data_loader import MigrationDataLoader
from lib.metrics import MigrationMetrics
from components.seam_card import render_seam_card

st.set_page_config(page_title="Migration Overview", page_icon="📊", layout="wide")

# Initialize
loader = MigrationDataLoader(docs_path="../../docs")
metrics = MigrationMetrics(loader)

# Hero Section
st.title("🎯 Migration Command Center")

col1, col2, col3 = st.columns(3)

with col1:
    health_score = metrics.calculate_migration_health_score()
    status = "🟢 Near Ready" if health_score >= 75 else "🟡 In Progress" if health_score >= 50 else "🔴 Not Ready"
    st.metric("Migration Health Score", f"{health_score}/100", status)

with col2:
    phase_completion = loader.get_phase_completion()
    avg_phase = sum(phase_completion.values()) / 7
    st.metric("Overall Progress", f"{avg_phase:.0f}%")

with col3:
    seams = loader.get_all_seams()
    st.metric("Total Seams", len(seams))

# Phase Progress Cards
st.subheader("📈 Phase Progress")

cols = st.columns(7)
phases = [
    ("Phase 0", "Discovery", "🔍"),
    ("Phase 1", "Analysis", "🔬"),
    ("Phase 2", "Architecture", "🏗️"),
    ("Phase 3", "Specifications", "📝"),
    ("Phase 4", "Roadmap", "🗺️"),
    ("Phase 5", "Implementation", "🔨"),
    ("Phase 6", "Validation", "✅"),
]

for idx, (col, phase_info) in enumerate(zip(cols, phases)):
    with col:
        phase_name, phase_desc, icon = phase_info
        completion = phase_completion[f"phase_{idx}"]
        st.metric(f"{icon} {phase_name}", f"{completion:.0f}%", phase_desc)

# Seam Status Matrix
st.subheader("📋 Seam Status Matrix")

seam_data = []
for seam in seams:
    readiness = loader.load_seam_readiness(seam)
    score = readiness.get("score", 0) if readiness else 0
    status = "✅ Complete" if score >= 95 else "🔵 In Progress" if score >= 50 else "🔴 Blocked"
    blockers = "None"  # TODO: Parse boundary-issues.json

    seam_data.append({
        "Seam": seam,
        "Status": status,
        "Readiness": f"{score}/100",
        "Blockers": blockers
    })

import pandas as pd
df = pd.DataFrame(seam_data)
st.dataframe(df, use_container_width=True)

# Key Insights
st.subheader("💡 Key Insights")
st.info(f"🎯 {len(seams)} seams discovered across the application")
st.info(f"📊 Average readiness score: {avg_phase:.0f}%")

# TODO: Add automated insights
```

---

## 🧪 Testing

### Unit Tests

```python
# tests/test_data_loader.py
import pytest
from app.lib.data_loader import MigrationDataLoader

def test_load_seam_proposals():
    loader = MigrationDataLoader(docs_path="tests/fixtures")
    proposals = loader.load_seam_proposals()
    assert "seams" in proposals
    assert len(proposals["seams"]) > 0

def test_get_all_seams():
    loader = MigrationDataLoader(docs_path="tests/fixtures")
    seams = loader.get_all_seams()
    assert isinstance(seams, list)
    assert "catalog-list" in seams
```

### Run Tests

```bash
pytest tests/ -v
```

---

## 🚀 Deployment

### Local Development

```bash
streamlit run app/main.py --server.port 8501
```

### Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY config.yaml .

# Mount docs/ directory as volume
VOLUME /app/docs

EXPOSE 8501

CMD ["streamlit", "run", "app/main.py", "--server.address", "0.0.0.0"]
```

```bash
# Build & run
docker build -t migration-dashboard .
docker run -p 8501:8501 -v $(pwd)/../../docs:/app/docs migration-dashboard
```

### Cloud Deployment (Streamlit Cloud)

1. Push code to GitHub
2. Go to https://share.streamlit.io
3. Deploy from repository
4. Set `docs_path` in config to mounted volume

---

## 🔍 Troubleshooting

### Dashboard shows "No data"

**Solution:** Check that migration artifacts exist:
```bash
ls docs/context-fabric/seam-proposals.json
# If missing, run Phase 0: /run-full-migration
```

### Charts not rendering

**Solution:** Check Plotly version:
```bash
pip install --upgrade plotly
```

### File watcher not working

**Solution:** Increase watchdog timeout:
```python
# app/utils/file_watcher.py
observer.timeout = 10  # Increase from default 1s
```

---

## 📚 Next Steps

1. **Run Phase 0** to generate initial artifacts
2. **Launch dashboard** with `streamlit run app/main.py`
3. **Monitor progress** as agents execute
4. **Export reports** for stakeholders
5. **Iterate** based on insights

---

**Ready to visualize your migration journey! 🚀**
