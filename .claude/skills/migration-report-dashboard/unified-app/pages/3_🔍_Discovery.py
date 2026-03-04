"""
Discovery Page
Seam proposals, context fabric manifest, and coverage reports
"""

import streamlit as st
import sys
from pathlib import Path
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.unified_loader import UnifiedDataLoader
import pandas as pd

st.set_page_config(page_title="Discovery", page_icon="🔍", layout="wide")

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

st.title("🔍 Discovery Phase")
st.markdown("### Phase 0: Discovery Loop - Coverage heatmap, dependency graph, context fabric")

if not data_loaded:
    st.error("Data loading failed. Check paths and data sources.")
    st.stop()

try:
    # Tabs for different discovery views
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Seam Proposals", "🗺️ Context Fabric", "📊 Coverage Report", "🔗 Dependencies"])

    with tab1:
        st.subheader("Discovered Seams")

        proposals = loader.modern.load_seam_proposals()
        seams = proposals.get("seams", [])

        if not seams:
            st.info("No seam proposals found. Run Phase 0 Discovery Loop to analyze the codebase.")
        else:
            st.success(f"**{len(seams)} seams discovered**")

            # Display seam proposals table
            seam_data = []
            for seam in seams:
                name = seam.get("seam_name") or seam.get("name") or seam.get("seam_id", "Unknown")
                score = seam.get("score", 0)
                complexity = seam.get("complexity", "unknown")
                priority = seam.get("priority", "medium")
                confidence = seam.get("confidence", "medium")

                # Priority icon
                priority_icons = {
                    "high": "🔴",
                    "medium": "🟡",
                    "low": "🟢"
                }
                priority_icon = priority_icons.get(priority.lower(), "⚪")

                seam_data.append({
                    "Seam Name": name,
                    "Score": score,
                    "Complexity": complexity.upper(),
                    "Priority": f"{priority_icon} {priority.upper()}",
                    "Confidence": confidence.upper(),
                    "Entry Points": seam.get("entry_points_count", 0),
                })

            df = pd.DataFrame(seam_data)
            st.dataframe(df, use_container_width=True, hide_index=True)

            # Detailed view of selected seam
            st.markdown("---")
            st.subheader("Seam Details")

            seam_names = [s.get("seam_name") or s.get("name") or s.get("seam_id")
                         for s in seams]
            selected_seam_idx = st.selectbox(
                "Select seam for details:",
                range(len(seams)),
                format_func=lambda i: seam_names[i]
            )

            selected_seam = seams[selected_seam_idx]

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Discovery Score", f"{selected_seam.get('score', 0)}/100")

            with col2:
                st.metric("Entry Points", selected_seam.get("entry_points_count", 0))

            with col3:
                st.metric("Complexity", selected_seam.get("complexity", "unknown").upper())

            with col4:
                st.metric("Priority", selected_seam.get("priority", "medium").upper())

            # Display rationale
            if "rationale" in selected_seam:
                st.info(f"**Rationale:** {selected_seam['rationale']}")

            # Display entry points if available
            if "entry_points" in selected_seam and selected_seam["entry_points"]:
                with st.expander("📍 Entry Points", expanded=False):
                    for ep in selected_seam["entry_points"]:
                        st.code(ep, language="text")

            # Display dependencies if available
            if "dependencies" in selected_seam and selected_seam["dependencies"]:
                with st.expander("🔗 Dependencies", expanded=False):
                    for dep in selected_seam["dependencies"]:
                        st.markdown(f"- `{dep}`")

    with tab2:
        st.subheader("Context Fabric Manifest")

        manifest_path = Path(loader.modern.docs_path) / "context-fabric/manifest.json"

        if not manifest_path.exists():
            st.info("Context fabric manifest not found. Run Phase 0 Discovery Loop.")
        else:
            try:
                manifest = json.loads(manifest_path.read_text())

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Total Files", manifest.get("total_files", 0))

                with col2:
                    st.metric("Analyzed Files", manifest.get("analyzed_files", 0))

                with col3:
                    coverage = manifest.get("coverage_percentage", 0)
                    st.metric("Coverage", f"{coverage}%")

                st.markdown("---")

                # Display file types
                if "file_types" in manifest:
                    st.subheader("File Types Analyzed")

                    type_data = []
                    for file_type, count in manifest["file_types"].items():
                        type_data.append({"Type": file_type, "Count": count})

                    df_types = pd.DataFrame(type_data)
                    st.dataframe(df_types, use_container_width=True, hide_index=True)

                # Display extracted patterns
                if "patterns" in manifest:
                    with st.expander("🔍 Extracted Patterns", expanded=False):
                        st.json(manifest["patterns"])

            except Exception as e:
                st.error(f"Error loading manifest: {e}")

    with tab3:
        st.subheader("Coverage Report")

        coverage_path = Path(loader.modern.docs_path) / "legacy-golden/coverage-report.json"

        if not coverage_path.exists():
            st.info("Coverage report not found. Run Phase 0 Discovery Loop.")
        else:
            try:
                coverage = json.loads(coverage_path.read_text())

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    total = coverage.get("total_files", 0)
                    st.metric("Total Files", total)

                with col2:
                    covered = coverage.get("covered_files", 0)
                    st.metric("Covered Files", covered)

                with col3:
                    uncovered = coverage.get("uncovered_files", 0)
                    st.metric("Uncovered Files", uncovered)

                with col4:
                    pct = coverage.get("coverage_percentage", 0)
                    st.metric("Coverage %", f"{pct}%")

                # Progress bar
                st.progress(pct / 100)

                st.markdown("---")

                # Display coverage by file type
                if "by_file_type" in coverage:
                    st.subheader("Coverage by File Type")

                    type_data = []
                    for file_type, data in coverage["by_file_type"].items():
                        type_data.append({
                            "File Type": file_type,
                            "Covered": data.get("covered", 0),
                            "Total": data.get("total", 0),
                            "Coverage %": f"{data.get('coverage_pct', 0)}%"
                        })

                    df_coverage = pd.DataFrame(type_data)
                    st.dataframe(df_coverage, use_container_width=True, hide_index=True)

                # Display uncovered files
                if "uncovered_file_list" in coverage and coverage["uncovered_file_list"]:
                    with st.expander("📄 Uncovered Files", expanded=False):
                        for file in coverage["uncovered_file_list"]:
                            st.text(file)

            except Exception as e:
                st.error(f"Error loading coverage report: {e}")

    with tab4:
        st.subheader("Dependency Graph")

        st.info("Dependency visualization coming soon. Currently analyzing seam relationships.")

        # Show seam dependencies if available
        proposals = loader.modern.load_seam_proposals()
        seams = proposals.get("seams", [])

        if seams:
            st.markdown("### Seam Dependencies")

            for seam in seams:
                name = seam.get("seam_name") or seam.get("name") or seam.get("seam_id")
                deps = seam.get("dependencies", [])

                if deps:
                    with st.expander(f"**{name}** ({len(deps)} dependencies)"):
                        for dep in deps:
                            st.markdown(f"- `{dep}`")

except Exception as e:
    st.error("Error loading discovery data")
    st.exception(e)
