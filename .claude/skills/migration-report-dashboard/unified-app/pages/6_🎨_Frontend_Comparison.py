"""
Frontend Comparison Page
Compare legacy UI vs modern React implementation
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

st.set_page_config(page_title="Frontend Comparison", page_icon="🎨", layout="wide")

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

st.title("🎨 Frontend Comparison")
st.markdown("### Legacy UI vs Modern React implementation")

if not data_loaded:
    st.error("Data loading failed. Check paths and data sources.")
    st.stop()

try:
    # Get frontend comparison data
    frontend_comp = loader.get_frontend_comparison()

    # High-level comparison
    st.subheader("Technology Stack Comparison")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🏛️ Legacy System")
        st.info(f"**Framework:** {frontend_comp['legacy']['framework']}")
        st.info(f"**Pattern:** {frontend_comp['legacy']['pattern']}")
        st.metric("UI Components", frontend_comp['legacy']['ui_components'])

    with col2:
        st.markdown("### 🚀 Modern System")
        st.success(f"**Framework:** {frontend_comp['modern']['framework']}")
        st.success(f"**Pattern:** {frontend_comp['modern']['pattern']}")
        st.metric("UI Components", frontend_comp['modern']['ui_components'])

    st.markdown("---")

    # Seam-by-seam comparison
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Component Mapping", "🖼️ Screenshots", "⚡ Performance", "📐 UI Metrics"])

    with tab1:
        st.subheader("Component Mapping")

        seams = loader.modern.get_all_seams()

        if not seams:
            st.info("No seams discovered yet. Run Phase 0 (Discovery Loop) first.")
        else:
            selected_seam = st.selectbox("Select seam:", seams, key="comp_seam")

            if selected_seam:
                seam_base = Path(loader.modern.docs_path) / f"seams/{selected_seam}"

                # Check for UI behavior documentation
                ui_behavior_path = seam_base / "ui-behavior.md"

                if ui_behavior_path.exists():
                    content = ui_behavior_path.read_text(encoding="utf-8")
                    st.markdown(content)
                else:
                    st.info(f"No UI behavior documentation found for `{selected_seam}`. Run Phase 1 (Per-Seam Discovery).")

                # Show component structure if available
                component_path = Path(loader.modern.docs_path).parent / f"frontend/src/pages/{selected_seam}"

                if component_path.exists():
                    st.success(f"✅ Modern components implemented at `frontend/src/pages/{selected_seam}`")

                    # List component files
                    tsx_files = list(component_path.glob("*.tsx"))
                    if tsx_files:
                        with st.expander("📁 Component Files", expanded=False):
                            for file in tsx_files:
                                st.code(file.name, language="text")
                else:
                    st.warning(f"⏸️ Modern components not yet implemented for `{selected_seam}`")

    with tab2:
        st.subheader("UI Screenshots")

        seams = loader.modern.get_all_seams()

        if not seams:
            st.info("No seams discovered yet.")
        else:
            selected_seam = st.selectbox("Select seam:", seams, key="screenshot_seam")

            if selected_seam:
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("### 🏛️ Legacy UI")

                    # Check for legacy screenshot
                    legacy_screenshot = Path(loader.modern.docs_path) / f"seams/{selected_seam}/evidence/legacy-screenshot.png"

                    if legacy_screenshot.exists():
                        st.image(str(legacy_screenshot), use_container_width=True)
                    else:
                        st.info("Legacy screenshot not available.")

                with col2:
                    st.markdown("### 🚀 Modern UI")

                    # Check for modern screenshot
                    modern_screenshot = Path(loader.modern.docs_path) / f"seams/{selected_seam}/evidence/modern-screenshot.png"

                    if modern_screenshot.exists():
                        st.image(str(modern_screenshot), use_container_width=True)
                    else:
                        st.info("Modern screenshot not available.")

                # Check for parity validation results
                st.markdown("---")
                st.subheader("Visual Parity Analysis")

                parity_path = Path(loader.modern.docs_path) / f"parity-validation/{selected_seam}/visual-parity.json"

                if parity_path.exists():
                    try:
                        parity = json.loads(parity_path.read_text())

                        col1, col2, col3 = st.columns(3)

                        with col1:
                            score = parity.get("parity_score", 0)
                            st.metric("Parity Score", f"{score}/100")

                        with col2:
                            differences = parity.get("differences_count", 0)
                            st.metric("Differences", differences)

                        with col3:
                            status = parity.get("status", "unknown")
                            if status == "pass":
                                st.success("✅ PASS")
                            elif status == "fail":
                                st.error("❌ FAIL")
                            else:
                                st.warning("⏸️ PENDING")

                        # Show differences if any
                        if "differences" in parity and parity["differences"]:
                            with st.expander("🔍 Visual Differences", expanded=False):
                                for diff in parity["differences"]:
                                    st.markdown(f"- **{diff.get('type', 'unknown')}**: {diff.get('description', 'No description')}")

                    except Exception as e:
                        st.error(f"Error loading parity results: {e}")
                else:
                    st.info("Visual parity validation not yet performed.")

    with tab3:
        st.subheader("Frontend Performance")

        seams = loader.modern.get_all_seams()

        if not seams:
            st.info("No seams discovered yet.")
        else:
            selected_seam = st.selectbox("Select seam:", seams, key="perf_seam")

            if selected_seam:
                # Load Lighthouse results
                lighthouse = loader.modern.load_lighthouse_results(selected_seam)

                if lighthouse:
                    st.success("Lighthouse audit completed")

                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        perf = lighthouse.get("performance", 0)
                        st.metric("Performance", f"{perf}/100")

                    with col2:
                        a11y = lighthouse.get("accessibility", 0)
                        st.metric("Accessibility", f"{a11y}/100")

                    with col3:
                        bp = lighthouse.get("best_practices", 0)
                        st.metric("Best Practices", f"{bp}/100")

                    with col4:
                        seo = lighthouse.get("seo", 0)
                        st.metric("SEO", f"{seo}/100")

                    st.markdown("---")

                    # Core Web Vitals
                    if "metrics" in lighthouse:
                        st.subheader("Core Web Vitals")

                        metrics = lighthouse["metrics"]

                        col1, col2, col3 = st.columns(3)

                        with col1:
                            lcp = metrics.get("largest_contentful_paint", 0)
                            st.metric("LCP", f"{lcp}ms")
                            if lcp < 2500:
                                st.success("✅ Good")
                            elif lcp < 4000:
                                st.warning("🟡 Needs Improvement")
                            else:
                                st.error("❌ Poor")

                        with col2:
                            fid = metrics.get("first_input_delay", 0)
                            st.metric("FID", f"{fid}ms")
                            if fid < 100:
                                st.success("✅ Good")
                            elif fid < 300:
                                st.warning("🟡 Needs Improvement")
                            else:
                                st.error("❌ Poor")

                        with col3:
                            cls = metrics.get("cumulative_layout_shift", 0)
                            st.metric("CLS", f"{cls:.3f}")
                            if cls < 0.1:
                                st.success("✅ Good")
                            elif cls < 0.25:
                                st.warning("🟡 Needs Improvement")
                            else:
                                st.error("❌ Poor")

                else:
                    st.info("Lighthouse audit not yet performed for this seam.")

    with tab4:
        st.subheader("UI Metrics")

        # Show bundle size and component metrics
        st.markdown("### Bundle Size")

        # Check for build output
        build_stats_path = Path(loader.modern.docs_path).parent / "frontend/dist/stats.json"

        if build_stats_path.exists():
            try:
                stats = json.loads(build_stats_path.read_text())

                col1, col2, col3 = st.columns(3)

                with col1:
                    total_size = stats.get("total_size", 0) / 1024  # KB
                    st.metric("Total Bundle Size", f"{total_size:.1f} KB")

                with col2:
                    js_size = stats.get("js_size", 0) / 1024
                    st.metric("JavaScript", f"{js_size:.1f} KB")

                with col3:
                    css_size = stats.get("css_size", 0) / 1024
                    st.metric("CSS", f"{css_size:.1f} KB")

                # Bundle size budget check
                st.markdown("---")
                st.subheader("Bundle Budget")

                budget = 200  # KB
                if js_size <= budget:
                    st.success(f"✅ JavaScript bundle within budget ({budget} KB)")
                else:
                    st.error(f"❌ JavaScript bundle exceeds budget: {js_size:.1f} KB / {budget} KB")

            except Exception as e:
                st.error(f"Error loading build stats: {e}")
        else:
            st.info("Build statistics not available. Run `npm run build` in frontend directory.")

        # Component count by seam
        st.markdown("---")
        st.subheader("Component Distribution")

        seams = loader.modern.get_all_seams()
        comp_data = []

        for seam in seams:
            component_path = Path(loader.modern.docs_path).parent / f"frontend/src/pages/{seam}"

            if component_path.exists():
                tsx_files = list(component_path.glob("*.tsx"))
                comp_data.append({
                    "Seam": seam,
                    "Components": len(tsx_files),
                    "Status": "✅ Implemented"
                })
            else:
                comp_data.append({
                    "Seam": seam,
                    "Components": 0,
                    "Status": "⏸️ Not Started"
                })

        if comp_data:
            df = pd.DataFrame(comp_data)
            st.dataframe(df, use_container_width=True, hide_index=True)

except Exception as e:
    st.error("Error loading frontend comparison")
    st.exception(e)
