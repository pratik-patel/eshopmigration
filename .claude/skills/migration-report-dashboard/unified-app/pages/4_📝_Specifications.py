"""
Specifications Page
Requirements, design, tasks, and OpenAPI contracts per seam
"""

import streamlit as st
import sys
from pathlib import Path
import json
import yaml

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.unified_loader import UnifiedDataLoader

st.set_page_config(page_title="Specifications", page_icon="📝", layout="wide")

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

st.title("📝 Specifications")
st.markdown("### Phase 3: Requirements, design, tasks, and contracts per seam")

if not data_loaded:
    st.error("Data loading failed. Check paths and data sources.")
    st.stop()

try:
    seams = loader.modern.get_all_seams()

    if not seams:
        st.info("No seams discovered yet. Run Phase 0 (Discovery Loop) first.")
        st.stop()

    # Seam selector
    selected_seam = st.selectbox("Select seam:", seams)

    if not selected_seam:
        st.warning("Please select a seam to view specifications.")
        st.stop()

    # Check phase 3 completion for this seam
    seam_base = Path(loader.modern.docs_path) / f"seams/{selected_seam}"

    has_requirements = (seam_base / "requirements.md").exists()
    has_design = (seam_base / "design.md").exists()
    has_tasks = (seam_base / "tasks.md").exists()
    has_contract = (seam_base / "contracts/openapi.yaml").exists()

    completion_items = sum([has_requirements, has_design, has_tasks, has_contract])
    completion_pct = (completion_items / 4) * 100

    # Status indicator
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        st.subheader(f"Seam: {selected_seam}")

    with col2:
        st.metric("Spec Completion", f"{completion_pct:.0f}%")

    with col3:
        if completion_pct >= 100:
            st.success("✅ Complete")
        elif completion_pct >= 50:
            st.info("🔵 In Progress")
        elif completion_pct > 0:
            st.warning("🟡 Started")
        else:
            st.caption("⏸️ Not Started")

    st.progress(completion_pct / 100)

    st.markdown("---")

    # Tabs for different specification documents
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Requirements", "🎨 Design", "✅ Tasks", "📄 Contract"])

    with tab1:
        st.subheader("Requirements Document")

        requirements_path = seam_base / "requirements.md"

        if not requirements_path.exists():
            st.info("Requirements document not found. Run Phase 3 (Specifications) for this seam.")
        else:
            try:
                content = requirements_path.read_text(encoding="utf-8")
                st.markdown(content)
            except Exception as e:
                st.error(f"Error loading requirements.md: {e}")

    with tab2:
        st.subheader("Design Document")

        design_path = seam_base / "design.md"

        if not design_path.exists():
            st.info("Design document not found. Run Phase 3 (Specifications) for this seam.")
        else:
            try:
                content = design_path.read_text(encoding="utf-8")
                st.markdown(content)
            except Exception as e:
                st.error(f"Error loading design.md: {e}")

    with tab3:
        st.subheader("Task Breakdown")

        tasks_path = seam_base / "tasks.md"

        if not tasks_path.exists():
            st.info("Tasks document not found. Run Phase 3 (Specifications) for this seam.")
        else:
            try:
                content = tasks_path.read_text(encoding="utf-8")
                st.markdown(content)

                # Try to extract task checklist if present
                if "- [ ]" in content or "- [x]" in content:
                    st.markdown("---")
                    st.subheader("Task Checklist Summary")

                    lines = content.split("\n")
                    total_tasks = 0
                    completed_tasks = 0

                    for line in lines:
                        if "- [ ]" in line:
                            total_tasks += 1
                        elif "- [x]" in line or "- [X]" in line:
                            total_tasks += 1
                            completed_tasks += 1

                    if total_tasks > 0:
                        col1, col2, col3 = st.columns(3)

                        with col1:
                            st.metric("Total Tasks", total_tasks)

                        with col2:
                            st.metric("Completed", completed_tasks)

                        with col3:
                            task_pct = (completed_tasks / total_tasks) * 100
                            st.metric("Progress", f"{task_pct:.0f}%")

                        st.progress(task_pct / 100)

            except Exception as e:
                st.error(f"Error loading tasks.md: {e}")

    with tab4:
        st.subheader("OpenAPI Contract")

        contract_path = seam_base / "contracts/openapi.yaml"

        if not contract_path.exists():
            st.info("OpenAPI contract not found. Run Phase 3 (Specifications) for this seam.")
        else:
            try:
                content = contract_path.read_text(encoding="utf-8")

                # Try to parse as YAML
                try:
                    contract = yaml.safe_load(content)

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        endpoints = 0
                        if "paths" in contract:
                            endpoints = len(contract["paths"])
                        st.metric("Endpoints", endpoints)

                    with col2:
                        schemas = 0
                        if "components" in contract and "schemas" in contract["components"]:
                            schemas = len(contract["components"]["schemas"])
                        st.metric("Schemas", schemas)

                    with col3:
                        version = contract.get("info", {}).get("version", "N/A")
                        st.metric("Version", version)

                    st.markdown("---")

                    # Display paths
                    if "paths" in contract:
                        st.subheader("API Endpoints")

                        for path, methods in contract["paths"].items():
                            with st.expander(f"**{path}**"):
                                for method, details in methods.items():
                                    st.markdown(f"**{method.upper()}**")
                                    st.markdown(details.get("summary", "No summary"))

                                    if "parameters" in details:
                                        st.markdown("**Parameters:**")
                                        for param in details["parameters"]:
                                            st.markdown(f"- `{param.get('name')}` ({param.get('in')}): {param.get('description', 'No description')}")

                except yaml.YAMLError:
                    # If YAML parsing fails, just show raw content
                    pass

                # Show raw YAML
                with st.expander("📄 Raw YAML", expanded=False):
                    st.code(content, language="yaml")

            except Exception as e:
                st.error(f"Error loading openapi.yaml: {e}")

except Exception as e:
    st.error("Error loading specifications")
    st.exception(e)
