"""
Migration Report Dashboard - Main Entry Point
Multi-page Streamlit application for comprehensive migration comparison
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import load_config, AppConfig
from app.state import init_session_state, load_metrics

# Page configuration
st.set_page_config(
    page_title="Migration Assessment Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load configuration
config = load_config()

# Initialize session state
init_session_state()

# Custom CSS
st.markdown("""
<style>
    /* Main content */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* Metrics */
    .metric-card {
        background: white;
        border-radius: 8px;
        padding: 1.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }

    /* Score badge */
    .score-excellent { color: #10b981; font-weight: bold; }
    .score-good { color: #22c55e; font-weight: bold; }
    .score-warning { color: #f59e0b; font-weight: bold; }
    .score-poor { color: #ef4444; font-weight: bold; }

    /* Headers */
    h1 { color: #1e293b; }
    h2 { color: #334155; margin-top: 2rem; }
    h3 { color: #475569; }

    /* Sidebar */
    .css-1d391kg { padding-top: 3rem; }

    /* Tables */
    .dataframe { font-size: 0.9rem; }

    /* Buttons */
    .stButton>button {
        border-radius: 6px;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("📊 Migration Dashboard")
    st.markdown("---")

    # Load data status
    metrics_loaded = load_metrics()

    if metrics_loaded:
        st.success("✅ Data Loaded")

        # Show summary stats
        if 'overall_score' in st.session_state:
            score = st.session_state.overall_score
            if score >= 90:
                st.metric("Overall Score", f"{score}/100", "Production Ready", delta_color="normal")
            elif score >= 75:
                st.metric("Overall Score", f"{score}/100", "Near Ready", delta_color="normal")
            elif score >= 60:
                st.metric("Overall Score", f"{score}/100", "In Progress", delta_color="normal")
            else:
                st.metric("Overall Score", f"{score}/100", "Not Ready", delta_color="inverse")
    else:
        st.warning("⚠️ No Data Available")
        st.markdown("""
        **Data not collected yet.**

        Run collection first:
        ```bash
        ./scripts/collect-all-metrics.sh
        ```
        """)

    st.markdown("---")

    # Data freshness
    if 'collection_timestamp' in st.session_state:
        st.caption(f"Last updated: {st.session_state.collection_timestamp}")

    # Refresh button
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.session_state.clear()
        st.rerun()

    st.markdown("---")

    # Configuration info
    with st.expander("⚙️ Configuration"):
        st.write("**Legacy App:**")
        st.caption(config.legacy.name)
        st.caption(config.legacy.frontend_url)

        st.write("**Modern App:**")
        st.caption(config.modern.name)
        st.caption(config.modern.frontend_url)

    # Export options
    with st.expander("📥 Export"):
        export_format = st.selectbox(
            "Format",
            ["PDF", "Excel", "JSON", "HTML"],
            key="export_format"
        )

        if st.button("Export Report", use_container_width=True):
            st.info("Export functionality will be available soon")

    st.markdown("---")
    st.caption("Migration Report Dashboard v1.0")
    st.caption("© 2026 Enterprise Architecture")

# Main content
st.title("🏠 Migration Assessment Dashboard")
st.markdown("Comprehensive comparison between legacy and modern applications")

# Check if data is loaded
if not metrics_loaded:
    st.error("### ⚠️ No Metrics Available")
    st.markdown("""
    Before using the dashboard, you need to collect metrics from both legacy and modern applications.

    ### Quick Start:

    1. **Configure URLs** in `config.yaml`
    2. **Run Collection**:
       ```bash
       cd .claude/skills/migration-report-dashboard
       ./scripts/collect-all-metrics.sh
       ```
    3. **Refresh Dashboard** (use button in sidebar)

    ### What Will Be Collected:

    - 🎨 **Frontend**: Lighthouse scores, feature parity, bundle size
    - ⚙️ **Backend**: API endpoints, response times, error rates
    - 💾 **Database**: Schema comparison, query performance
    - ✅ **Quality**: SonarQube metrics, test coverage
    - ⚡ **Performance**: Load test results, NFR metrics
    - 🔌 **Integrations**: External system compatibility

    For detailed instructions, see [README.md](README.md)
    """)

    st.info("""
    **First Time Setup:**

    ```bash
    # Install dependencies
    pip install -r requirements.txt
    npm install

    # Configure
    cp config.yaml.example config.yaml
    vim config.yaml

    # Collect metrics
    ./scripts/collect-all-metrics.sh

    # Launch dashboard
    streamlit run app/main.py
    ```
    """)

else:
    # Overview metrics
    st.markdown("## 📈 Migration Overview")

    # Top-level metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        score = st.session_state.get('overall_score', 0)
        st.metric(
            "Overall Score",
            f"{score}/100",
            help="Weighted average across all dimensions"
        )

    with col2:
        fe_score = st.session_state.get('frontend_score', 0)
        st.metric(
            "Frontend",
            f"{fe_score}/100",
            help="UI/UX, Performance, Accessibility"
        )

    with col3:
        be_score = st.session_state.get('backend_score', 0)
        st.metric(
            "Backend",
            f"{be_score}/100",
            help="API parity, Performance, Reliability"
        )

    with col4:
        quality_score = st.session_state.get('quality_score', 0)
        st.metric(
            "Quality",
            f"{quality_score}/100",
            help="SonarQube, Coverage, Security"
        )

    st.markdown("---")

    # Dimension scores (radar chart would go here via plotly)
    st.markdown("## 🎯 Dimension Scores")

    col1, col2 = st.columns([2, 1])

    with col1:
        # Placeholder for radar chart
        import plotly.graph_objects as go

        dimensions = ['Frontend', 'Backend', 'Database', 'Quality', 'NFR', 'Integration']
        scores = [
            st.session_state.get('frontend_score', 0),
            st.session_state.get('backend_score', 0),
            st.session_state.get('database_score', 0),
            st.session_state.get('quality_score', 0),
            st.session_state.get('nfr_score', 0),
            st.session_state.get('integration_score', 0),
        ]

        fig = go.Figure(data=go.Scatterpolar(
            r=scores + [scores[0]],  # Close the polygon
            theta=dimensions + [dimensions[0]],
            fill='toself',
            name='Modern vs Target',
            line=dict(color='#3b82f6')
        ))

        fig.add_trace(go.Scatterpolar(
            r=[100] * (len(dimensions) + 1),
            theta=dimensions + [dimensions[0]],
            fill='toself',
            name='Target (100)',
            line=dict(color='#d1d5db', dash='dash'),
            opacity=0.3
        ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )),
            showlegend=True,
            title="Migration Readiness by Dimension",
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("### Score Interpretation")

        for dim, score in zip(dimensions, scores):
            if score >= 90:
                emoji = "✅"
                status = "Excellent"
            elif score >= 75:
                emoji = "🟢"
                status = "Good"
            elif score >= 60:
                emoji = "🟡"
                status = "Fair"
            else:
                emoji = "🔴"
                status = "Needs Work"

            st.markdown(f"{emoji} **{dim}**: {score}/100 — {status}")

    st.markdown("---")

    # Critical gaps
    st.markdown("## 🚨 Critical Gaps")

    gaps = st.session_state.get('critical_gaps', [])

    if gaps:
        for gap in gaps[:5]:  # Show top 5
            severity = gap.get('severity', 'medium')
            if severity == 'critical':
                st.error(f"🔴 **{gap['title']}** — {gap['description']}")
            elif severity == 'high':
                st.warning(f"🟠 **{gap['title']}** — {gap['description']}")
            else:
                st.info(f"🟡 **{gap['title']}** — {gap['description']}")
    else:
        st.success("✅ No critical gaps detected!")

    # Navigation hint
    st.markdown("---")
    st.info("""
    👈 **Use the sidebar** to navigate to detailed pages:
    - 🎨 Frontend — UI/UX comparison
    - ⚙️ Backend — API analysis
    - 💾 Database — Schema & performance
    - ✅ Quality — SonarQube & coverage
    - ⚡ Performance — NFR metrics
    - 📊 Summary — Executive report
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #64748b; font-size: 0.875rem;'>
    <p>Migration Assessment Dashboard | Enterprise Architecture</p>
    <p>For issues or questions, see <a href='README.md'>README.md</a></p>
</div>
""", unsafe_allow_html=True)
