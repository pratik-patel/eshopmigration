"""
Unified Migration Dashboard - Main Entry Point
Combines progress tracking and comparison analysis into single comprehensive dashboard

Pages:
- 1. Home (Overview)
- 2. Progress Tracker
- 3. Discovery
- 4. Specifications
- 5. Roadmap
- 6. Frontend Comparison
- 7. Backend Comparison
- 8. Database Comparison
- 9. Quality
- 10. Security
- 11. Parity
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent and current directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))

from lib.unified_loader import UnifiedDataLoader
from lib.state import init_session_state

# Page configuration
st.set_page_config(
    page_title="Unified Migration Dashboard",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state and data loader
init_session_state()

@st.cache_resource
def get_data_loader():
    """Initialize unified data loader with caching"""
    return UnifiedDataLoader(
        docs_path="../../../docs",
        mock_legacy_path="../mock-data/legacy"
    )

try:
    loader = get_data_loader()
    data_loaded = True
except Exception as e:
    data_loaded = False
    st.error(f"Error loading data: {e}")

# Custom CSS
st.markdown("""
<style>
    /* Main content */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }

    /* Hero sections */
    .hero-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 2rem;
        color: white;
        margin-bottom: 2rem;
        text-align: center;
    }

    .hero-section h1 {
        font-size: 4rem;
        margin: 0;
        font-weight: bold;
    }

    .hero-section p {
        font-size: 1.5rem;
        margin: 0.5rem 0 0 0;
        opacity: 0.95;
    }

    /* Status badges */
    .status-excellent { color: #10b981; font-weight: bold; }
    .status-good { color: #22c55e; font-weight: bold; }
    .status-warning { color: #f59e0b; font-weight: bold; }
    .status-poor { color: #ef4444; font-weight: bold; }

    /* Comparison cards */
    .comparison-card {
        background: white;
        border-radius: 8px;
        padding: 1.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }

    /* Metric cards */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: bold;
    }

    /* Tables */
    .dataframe {
        font-size: 0.9rem;
    }

    /* Progress bars */
    .stProgress > div > div > div > div {
        background-color: #667eea;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 6px 6px 0px 0px;
        padding: 10px 20px;
    }

    /* Info boxes */
    .stInfo {
        background-color: #e0e7ff;
        border-left: 4px solid #667eea;
    }

    /* Warning boxes */
    .stWarning {
        background-color: #fef3c7;
        border-left: 4px solid #f59e0b;
    }

    /* Error boxes */
    .stError {
        background-color: #fee2e2;
        border-left: 4px solid #ef4444;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("🎯 Unified Migration Dashboard")
    st.markdown("---")

    # Data load status
    if data_loaded:
        st.success("✅ Data Loaded")

        # Show quick stats
        try:
            health_score = loader.get_migration_health_score()
            seams = loader.modern.get_all_seams()

            st.metric("Health Score", f"{health_score}/100")
            st.metric("Total Seams", len(seams))

            # Phase completion
            phase_completion = loader.modern.get_phase_completion()
            avg_progress = sum(phase_completion.values()) / len(phase_completion) if phase_completion else 0
            st.metric("Overall Progress", f"{avg_progress:.0f}%")

        except Exception as e:
            st.warning("⚠️ Some metrics unavailable")

    else:
        st.error("⚠️ Data Load Failed")
        st.info("Check data sources and paths")

    st.markdown("---")

    # Navigation
    st.markdown("### 📑 Pages")
    st.markdown("""
    **Overview**
    - 🏠 Home
    - 📊 Progress Tracker

    **Migration Details**
    - 🔍 Discovery
    - 📝 Specifications
    - 🗺️ Roadmap

    **Comparison**
    - 🎨 Frontend
    - ⚙️ Backend
    - 🗄️ Database

    **Quality & Validation**
    - ✅ Quality
    - 🔒 Security
    - 🎯 Parity
    """)

    st.markdown("---")
    st.caption("v1.0.0 | Last updated: 2026-03-03")

# Main content - Home page
st.title("🏠 Migration Command Center")
st.markdown("### Unified view of legacy-to-modern migration progress")

if not data_loaded:
    st.error("### Data Loading Failed")
    st.markdown("""
    **Please check:**
    1. Migration data exists in `docs/` directory
    2. Mock legacy data exists in `mock-data/legacy/`
    3. Paths are configured correctly
    """)
    st.stop()

try:
    # Get comprehensive metrics
    health_score = loader.get_migration_health_score()
    seams = loader.modern.get_all_seams()
    phase_completion = loader.modern.get_phase_completion()

    # Hero Section - Migration Health Score
    if health_score >= 90:
        status = "🟢 Production Ready"
        status_color = "#10b981"
    elif health_score >= 75:
        status = "🟢 Near Ready"
        status_color = "#22c55e"
    elif health_score >= 60:
        status = "🟡 In Progress"
        status_color = "#f59e0b"
    else:
        status = "🔴 Early Stage"
        status_color = "#ef4444"

    st.markdown(f"""
    <div class="hero-section">
        <h1>{health_score}/100</h1>
        <p style="color: {status_color}; font-weight: bold;">{status}</p>
        <p style="font-size: 1rem; opacity: 0.9; margin-top: 1rem;">
            Migration Health Score
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Key Metrics Row
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        avg_progress = sum(phase_completion.values()) / len(phase_completion) if phase_completion else 0
        st.metric("Overall Progress", f"{avg_progress:.0f}%")

    with col2:
        st.metric("Total Seams", len(seams))

    with col3:
        completed = sum(1 for seam in seams
                       if (loader.modern.load_seam_readiness(seam) or {}).get("score", 0) >= 95)
        st.metric("Completed", completed)

    with col4:
        blockers = loader.modern.count_critical_blockers()
        st.metric("Critical Blockers", blockers, delta=None if blockers == 0 else f"-{blockers}", delta_color="inverse")

    st.markdown("---")

    # Two-column layout
    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.subheader("📊 Phase Progress")

        phases = [
            ("Phase 0", "Discovery", "🔍", 0),
            ("Phase 1", "Per-Seam Discovery", "🔬", 1),
            ("Phase 2", "Architecture", "🏗️", 2),
            ("Phase 3", "Specifications", "📝", 3),
            ("Phase 4", "Roadmap", "🗺️", 4),
            ("Phase 5", "Implementation", "🔨", 5),
            ("Phase 6", "Validation", "✅", 6),
        ]

        for phase_name, phase_desc, icon, phase_num in phases:
            completion = phase_completion.get(f"phase_{phase_num}", 0)
            col_label, col_bar, col_pct = st.columns([3, 6, 1])
            with col_label:
                st.markdown(f"**{icon} {phase_name}**")
            with col_bar:
                st.progress(completion / 100)
            with col_pct:
                st.caption(f"{completion:.0f}%")

    with col_right:
        st.subheader("🎯 Quick Stats")

        # Legacy vs Modern comparison
        st.markdown("#### Legacy System (Estimated)")
        st.markdown("- **Framework:** .NET Framework 4.8")
        st.markdown("- **Pattern:** ASP.NET WebForms")
        st.markdown("- **Response Time:** ~1350ms (p95)")
        st.markdown("- **Test Coverage:** 42%")
        st.markdown("- **Vulnerabilities:** 31 CVEs")

        st.markdown("#### Modern System (Target)")
        st.markdown("- **Backend:** Python 3.12 + FastAPI")
        st.markdown("- **Frontend:** React 18 + TypeScript")
        st.markdown("- **Response Time:** <200ms (p95 target)")
        st.markdown("- **Test Coverage:** 80% (backend), 75% (frontend)")
        st.markdown("- **Vulnerabilities:** 0 CVEs")

    st.markdown("---")

    # Seam Status Matrix
    st.subheader("📋 Seam Status Matrix")

    import pandas as pd

    seam_data = []
    for seam in seams:
        readiness = loader.modern.load_seam_readiness(seam)
        score = readiness.get("score", 0) if readiness else 0

        # Status
        if score >= 95:
            status_icon = "✅"
            status_text = "Complete"
        elif score >= 50:
            status_icon = "🔵"
            status_text = "In Progress"
        elif score > 0:
            status_icon = "🟡"
            status_text = "Started"
        else:
            status_icon = "⏸️"
            status_text = "Not Started"

        # Blockers
        boundary_issues_path = Path(loader.modern.docs_path) / f"seams/{seam}/boundary-issues.json"
        blocker_count = 0
        if boundary_issues_path.exists():
            import json
            issues = json.loads(boundary_issues_path.read_text())
            blocker_count = len([i for i in issues.get("issues", [])
                               if i.get("severity") == "critical"])

        seam_data.append({
            "Seam": seam,
            "Status": f"{status_icon} {status_text}",
            "Readiness": f"{score}/100",
            "Blockers": f"{blocker_count} critical" if blocker_count > 0 else "None"
        })

    df = pd.DataFrame(seam_data)
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown("---")

    # Navigation Guide
    st.info("""
    **📍 Explore the dashboard:**
    - **📊 Progress Tracker** - Real-time phase progress and agent activity
    - **🎨 Frontend** - Legacy vs Modern UI comparison
    - **⚙️ Backend** - API endpoint and performance comparison
    - **✅ Quality** - Test coverage and code quality metrics
    - **🔒 Security** - Vulnerability scans and OWASP checklist
    - **🎯 Parity** - Visual parity validation results

    Use the sidebar to navigate between pages.
    """)

except Exception as e:
    st.error(f"### Error Loading Dashboard")
    st.exception(e)
    st.info("Check logs for details")

# Footer
st.markdown("---")
st.caption("🎯 Unified Migration Dashboard | Combines Progress Tracking + Comparison Analysis | v1.0.0")
