"""
Progress Tracker Page
Real-time migration progress with phase tracking and agent activity
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.unified_loader import UnifiedDataLoader
import pandas as pd

st.set_page_config(page_title="Progress Tracker", page_icon="📊", layout="wide")

# Load data
@st.cache_resource
def get_data_loader():
    return UnifiedDataLoader(
        docs_path="../../../../docs",
        mock_legacy_path="../../mock-data/legacy"
    )

try:
    loader = get_data_loader()
    data_loaded = True
except Exception as e:
    st.error(f"Error loading data: {e}")
    data_loaded = False

st.title("📊 Migration Progress Tracker")
st.markdown("### Real-time phase progress and agent activity")

if not data_loaded:
    st.error("Data loading failed. Check paths and data sources.")
    st.stop()

try:
    # Get data
    seams = loader.modern.get_all_seams()
    phase_completion = loader.modern.get_phase_completion()
    health_score = loader.get_migration_health_score()

    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["📈 Phase Progress", "🎯 Seam Details", "📋 Agent Activity"])

    with tab1:
        st.subheader("7-Phase Migration Progress")

        phases = [
            ("Phase 0", "Discovery Loop", "🔍", 0, "Coverage heatmap, dependency graph, context fabric"),
            ("Phase 1", "Per-Seam Discovery", "🔬", 1, "Technical analysis, call chains, data access"),
            ("Phase 2", "Architecture", "🏗️", 2, "Architecture design, tech stack comparison"),
            ("Phase 3", "Specifications", "📝", 3, "Requirements, design, tasks, contracts"),
            ("Phase 4", "Roadmap", "🗺️", 4, "Implementation waves, critical path, priorities"),
            ("Phase 5", "Implementation", "🔨", 5, "Backend + frontend development, testing"),
            ("Phase 6", "Validation", "✅", 6, "Security scan, parity validation, performance"),
        ]

        for phase_name, phase_desc, icon, phase_num, details in phases:
            completion = phase_completion.get(f"phase_{phase_num}", 0)

            with st.expander(f"{icon} **{phase_name}: {phase_desc}** ({completion:.0f}% complete)", expanded=(completion < 100 and completion > 0)):
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.progress(completion / 100)
                    st.caption(details)

                with col2:
                    if completion >= 100:
                        st.success("✅ Complete")
                    elif completion >= 50:
                        st.info("🔵 In Progress")
                    elif completion > 0:
                        st.warning("🟡 Started")
                    else:
                        st.caption("⏸️ Not Started")

        # Overall progress
        st.markdown("---")
        avg_progress = sum(phase_completion.values()) / 7
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Overall Completion", f"{avg_progress:.1f}%")

        with col2:
            st.metric("Health Score", f"{health_score}/100")

        with col3:
            completed_phases = sum(1 for v in phase_completion.values() if v >= 100)
            st.metric("Completed Phases", f"{completed_phases}/7")

    with tab2:
        st.subheader("Seam Status Details")

        if not seams:
            st.info("No seams discovered yet. Run Phase 0 (Discovery Loop).")
        else:
            seam_data = []
            for seam in seams:
                readiness = loader.modern.load_seam_readiness(seam)
                score = readiness.get("score", 0) if readiness else 0

                # Determine status
                if score >= 95:
                    status_icon = "✅"
                    status_text = "Complete"
                    status_color = "green"
                elif score >= 75:
                    status_icon = "🔵"
                    status_text = "Near Complete"
                    status_color = "blue"
                elif score >= 50:
                    status_icon = "🟡"
                    status_text = "In Progress"
                    status_color = "orange"
                else:
                    status_icon = "⏸️"
                    status_text = "Early Stage"
                    status_color = "gray"

                # Count blockers
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
                    "Readiness Score": f"{score}/100",
                    "Blockers": blocker_count,
                    "Phase 1": "✅" if (Path(loader.modern.docs_path) / f"seams/{seam}/discovery.md").exists() else "⏸️",
                    "Phase 3": "✅" if (Path(loader.modern.docs_path) / f"seams/{seam}/requirements.md").exists() else "⏸️",
                    "Phase 5": "✅" if (Path(loader.modern.docs_path) / f"seams/{seam}/implementation-summary.md").exists() else "⏸️",
                    "Phase 6": "✅" if (Path(loader.modern.docs_path) / f"seams/{seam}/security-review.md").exists() else "⏸️",
                })

            df = pd.DataFrame(seam_data)
            st.dataframe(df, use_container_width=True, hide_index=True)

            # Seam details
            st.markdown("---")
            st.subheader("Seam Details")

            selected_seam = st.selectbox("Select seam for details:", seams)

            if selected_seam:
                readiness = loader.modern.load_seam_readiness(selected_seam)

                if readiness:
                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        st.metric("Readiness Score", f"{readiness.get('score', 0)}/100")

                    with col2:
                        status = readiness.get("status", "unknown")
                        st.metric("Status", status.upper())

                    with col3:
                        blockers = readiness.get("blockers", [])
                        st.metric("Blockers", len(blockers))

                    with col4:
                        confidence = readiness.get("confidence", "unknown")
                        st.metric("Confidence", confidence.upper())

                    # Show blockers if any
                    if blockers:
                        st.warning(f"**⚠️ {len(blockers)} Blockers Found:**")
                        for blocker in blockers:
                            st.markdown(f"- {blocker}")

                else:
                    st.info("No readiness data available for this seam.")

    with tab3:
        st.subheader("Agent Activity Log")

        activities = loader.modern.load_activity_log()

        if not activities:
            st.info("No agent activity logged yet.")
        else:
            # Show recent activity
            st.caption(f"**Total events:** {len(activities)}")

            # Filter by event type
            event_types = ["All"] + list(set(a.get("event") for a in activities))
            selected_event = st.selectbox("Filter by event type:", event_types)

            if selected_event != "All":
                filtered_activities = [a for a in activities if a.get("event") == selected_event]
            else:
                filtered_activities = activities

            # Show last 50 activities
            recent_activities = filtered_activities[-50:]

            activity_data = []
            for activity in reversed(recent_activities):
                activity_data.append({
                    "Timestamp": activity.get("timestamp", "N/A"),
                    "Event": activity.get("event", "N/A"),
                    "Agent": activity.get("agent", "unknown"),
                    "Status": activity.get("status", "N/A"),
                })

            df_activity = pd.DataFrame(activity_data)
            st.dataframe(df_activity, use_container_width=True, hide_index=True, height=400)

            # Activity stats
            st.markdown("---")
            col1, col2, col3 = st.columns(3)

            with col1:
                agent_starts = len([a for a in activities if a.get("event") == "agent_started"])
                st.metric("Agent Starts", agent_starts)

            with col2:
                agent_completions = len([a for a in activities if a.get("event") == "agent_completed"])
                st.metric("Agent Completions", agent_completions)

            with col3:
                unique_agents = len(set(a.get("agent") for a in activities if a.get("agent") != "unknown-agent"))
                st.metric("Unique Agents", unique_agents)

except Exception as e:
    st.error("Error loading progress data")
    st.exception(e)
