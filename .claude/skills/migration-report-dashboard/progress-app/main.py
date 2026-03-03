"""
Migration Progress Dashboard - Real-time Migration Tracking
Entry point for 11-page progress tracking dashboard
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from progress_app.lib.data_loader import MigrationDataLoader
from progress_app.lib.metrics import MigrationMetrics

# Page configuration
st.set_page_config(
    page_title="Migration Progress Dashboard",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize data loader
@st.cache_resource
def get_data_loader():
    """Initialize data loader with caching"""
    return MigrationDataLoader(docs_path="../../docs")

loader = get_data_loader()
metrics = MigrationMetrics(loader)

# Custom CSS
st.markdown("""
<style>
    /* Main content */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }

    /* Hero score */
    .hero-score {
        text-align: center;
        padding: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        color: white;
        margin-bottom: 2rem;
    }

    .hero-score h1 {
        font-size: 4rem;
        margin: 0;
        font-weight: bold;
    }

    .hero-score p {
        font-size: 1.5rem;
        margin: 0.5rem 0 0 0;
    }

    /* Status badges */
    .status-complete { color: #10b981; }
    .status-progress { color: #3b82f6; }
    .status-blocked { color: #ef4444; }
    .status-pending { color: #9ca3af; }

    /* Progress bars */
    .stProgress > div > div > div > div {
        background-color: #667eea;
    }

    /* Metric cards */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar navigation
with st.sidebar:
    st.image("https://via.placeholder.com/150x50?text=Migration", use_column_width=True)
    st.title("🎯 Migration Progress")
    st.markdown("---")

    # Quick stats in sidebar
    try:
        health_score = metrics.calculate_migration_health_score()
        seams = loader.get_all_seams()

        st.metric("Health Score", f"{health_score}/100")
        st.metric("Total Seams", len(seams))

        phase_completion = loader.get_phase_completion()
        avg_progress = sum(phase_completion.values()) / len(phase_completion)
        st.metric("Overall Progress", f"{avg_progress:.0f}%")

    except Exception as e:
        st.warning("⚠️ No migration data found")
        st.info("Run `/migrate` to start migration")

    st.markdown("---")
    st.caption("📊 Real-time migration tracking")

# Main content - Home page (Overview Dashboard)
st.title("🏠 Migration Command Center")

try:
    # Hero Section
    health_score = metrics.calculate_migration_health_score()

    # Determine status
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
    <div class="hero-score">
        <h1>{health_score}/100</h1>
        <p style="color: {status_color}">{status}</p>
        <p style="font-size: 1rem; opacity: 0.9; margin-top: 1rem;">
            Migration Health Score
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Key Metrics Row
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        phase_completion = loader.get_phase_completion()
        avg_progress = sum(phase_completion.values()) / len(phase_completion)
        st.metric(
            "Overall Progress",
            f"{avg_progress:.0f}%",
            delta=None
        )

    with col2:
        seams = loader.get_all_seams()
        st.metric("Total Seams", len(seams))

    with col3:
        # Count completed seams (readiness >= 95)
        completed = 0
        for seam in seams:
            readiness = loader.load_seam_readiness(seam)
            if readiness and readiness.get("score", 0) >= 95:
                completed += 1
        st.metric("Completed Seams", completed)

    with col4:
        # Count blockers
        blockers = 0
        for seam in seams:
            boundary_issues_path = loader.docs_path / f"seams/{seam}/boundary-issues.json"
            if boundary_issues_path.exists():
                import json
                issues = json.loads(boundary_issues_path.read_text())
                blockers += len([i for i in issues.get("issues", [])
                               if i.get("severity") == "critical"])
        st.metric("Critical Blockers", blockers)

    st.markdown("---")

    # Phase Progress Cards
    st.subheader("📈 Phase Progress")

    phases = [
        ("Phase 0", "Discovery Loop", "🔍", 0),
        ("Phase 1", "Per-Seam Analysis", "🔬", 1),
        ("Phase 2", "Architecture", "🏗️", 2),
        ("Phase 3", "Specifications", "📝", 3),
        ("Phase 4", "Roadmap", "🗺️", 4),
        ("Phase 5", "Implementation", "🔨", 5),
        ("Phase 6", "Validation", "✅", 6),
    ]

    cols = st.columns(7)
    for idx, (col, phase_info) in enumerate(zip(cols, phases)):
        phase_name, phase_desc, icon, phase_num = phase_info
        completion = phase_completion[f"phase_{phase_num}"]

        with col:
            st.markdown(f"**{icon} {phase_name}**")
            st.progress(completion / 100)
            st.caption(f"{completion:.0f}%")

    st.markdown("---")

    # Seam Status Matrix
    st.subheader("📋 Seam Status Matrix")

    import pandas as pd

    seam_data = []
    for seam in seams:
        readiness = loader.load_seam_readiness(seam)
        score = readiness.get("score", 0) if readiness else 0

        # Determine status
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

        # Count blockers
        boundary_issues_path = loader.docs_path / f"seams/{seam}/boundary-issues.json"
        blocker_count = 0
        if boundary_issues_path.exists():
            import json
            issues = json.loads(boundary_issues_path.read_text())
            blocker_count = len([i for i in issues.get("issues", [])
                               if i.get("severity") == "critical"])

        blockers = f"{blocker_count} critical" if blocker_count > 0 else "None"

        seam_data.append({
            "Seam": seam,
            "Status": f"{status_icon} {status_text}",
            "Readiness": f"{score}/100",
            "Blockers": blockers
        })

    df = pd.DataFrame(seam_data)
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown("---")

    # Key Insights
    st.subheader("💡 Key Insights")

    insights = []

    # Insight 1: Blockers
    if blockers > 0:
        insights.append(f"🚨 {blockers} critical blockers require attention")
    else:
        insights.append("✅ No critical blockers")

    # Insight 2: Coverage
    insights.append(f"📊 {len(seams)} seams discovered across the application")

    # Insight 3: Progress
    insights.append(f"🎯 Average readiness score: {health_score}/100")

    # Insight 4: Completion forecast
    if completed > 0:
        remaining = len(seams) - completed
        if remaining > 0:
            insights.append(f"📈 {completed}/{len(seams)} seams complete, {remaining} remaining")
        else:
            insights.append("🎉 All seams complete!")

    for insight in insights:
        st.info(insight)

    # Navigation guide
    st.markdown("---")
    st.info("""
    **📍 Navigate using the sidebar to:**
    - 🔍 **Phase 0** — See how seams were discovered
    - 🔬 **Phase 1** — Deep dive into seam technical analysis
    - 🏗️ **Phase 2** — View architecture and tech stack
    - 📝 **Phase 3** — Review requirements and specifications
    - 🗺️ **Phase 4** — See implementation roadmap
    - 🔨 **Phase 5** — Track real-time implementation progress
    - ✅ **Phase 6** — Review security and parity validation
    - 📈 **Analytics** — View trends and forecasts
    - 🎨 **Artifacts** — Browse all generated files
    - 🚨 **Issues** — See all blockers and warnings
    """)

except Exception as e:
    st.error("⚠️ Error loading migration data")
    st.exception(e)
    st.info("""
    **To start migration tracking:**
    1. Run `/migrate` to begin migration
    2. Data will be generated in `docs/` directory
    3. Refresh this dashboard to see progress
    """)

# Footer
st.markdown("---")
st.caption("🎯 Migration Progress Dashboard | Updated in real-time from agent execution")
