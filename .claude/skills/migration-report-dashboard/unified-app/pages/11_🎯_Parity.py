"""
Parity Page
Screenshot comparison, visual parity, behavioral validation, and feature parity
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

st.set_page_config(page_title="Parity Validation", page_icon="🎯", layout="wide")

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

st.title("🎯 Parity Validation")
st.markdown("### Screenshot comparison, visual parity, and behavioral validation")

if not data_loaded:
    st.error("Data loading failed. Check paths and data sources.")
    st.stop()

try:
    seams = loader.modern.get_all_seams()

    if not seams:
        st.info("No seams discovered yet. Run Phase 0 (Discovery Loop) first.")
        st.stop()

    # Parity summary
    st.subheader("Parity Validation Summary")

    parity_data = []

    for seam in seams:
        # Check for visual parity results
        visual_parity_path = Path(loader.modern.docs_path) / f"parity-validation/{seam}/visual-parity.json"

        if visual_parity_path.exists():
            try:
                parity = json.loads(visual_parity_path.read_text())
                visual_score = parity.get("parity_score", 0)
                visual_status = parity.get("status", "pending")
            except:
                visual_score = 0
                visual_status = "error"
        else:
            visual_score = 0
            visual_status = "pending"

        # Check for behavioral validation
        behavioral_path = Path(loader.modern.docs_path) / f"parity-validation/{seam}/behavioral-validation.json"

        if behavioral_path.exists():
            try:
                behavioral = json.loads(behavioral_path.read_text())
                behavioral_score = behavioral.get("parity_score", 0)
                behavioral_status = behavioral.get("status", "pending")
            except:
                behavioral_score = 0
                behavioral_status = "error"
        else:
            behavioral_score = 0
            behavioral_status = "pending"

        # Overall parity score (average)
        overall_score = (visual_score + behavioral_score) / 2 if (visual_score > 0 or behavioral_score > 0) else 0

        # Status
        if overall_score >= 95:
            status = "✅ Excellent"
        elif overall_score >= 85:
            status = "🟢 Good"
        elif overall_score >= 70:
            status = "🟡 Acceptable"
        elif overall_score > 0:
            status = "🔴 Poor"
        else:
            status = "⏸️ Not Validated"

        parity_data.append({
            "Seam": seam,
            "Visual Parity": f"{visual_score}/100",
            "Behavioral Parity": f"{behavioral_score}/100",
            "Overall Score": f"{overall_score:.1f}/100",
            "Status": status,
        })

    df = pd.DataFrame(parity_data)
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown("---")

    # Tabs for different parity views
    tab1, tab2, tab3, tab4 = st.tabs(["🖼️ Visual Parity", "⚙️ Behavioral Parity", "📋 Feature Checklist", "🔍 Diff Analysis"])

    with tab1:
        st.subheader("Visual Parity Validation")

        selected_seam = st.selectbox("Select seam:", seams, key="visual_seam")

        if selected_seam:
            # Load visual parity results
            visual_parity_path = Path(loader.modern.docs_path) / f"parity-validation/{selected_seam}/visual-parity.json"

            if visual_parity_path.exists():
                try:
                    parity = json.loads(visual_parity_path.read_text())

                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        score = parity.get("parity_score", 0)
                        st.metric("Parity Score", f"{score}/100")

                    with col2:
                        status = parity.get("status", "unknown")
                        if status == "pass":
                            st.success("✅ PASS")
                        elif status == "fail":
                            st.error("❌ FAIL")
                        else:
                            st.warning("⏸️ PENDING")

                    with col3:
                        differences = parity.get("differences_count", 0)
                        st.metric("Differences", differences)

                    with col4:
                        timestamp = parity.get("timestamp", "N/A")
                        st.caption(f"Last validated: {timestamp}")

                    st.progress(score / 100)

                    # Side-by-side screenshot comparison
                    st.markdown("---")
                    st.subheader("Screenshot Comparison")

                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown("### 🏛️ Legacy Screenshot")

                        legacy_screenshot = Path(loader.modern.docs_path) / f"seams/{selected_seam}/evidence/legacy-screenshot.png"

                        if legacy_screenshot.exists():
                            st.image(str(legacy_screenshot), use_container_width=True)
                        else:
                            st.info("Legacy screenshot not available.")

                    with col2:
                        st.markdown("### 🚀 Modern Screenshot")

                        modern_screenshot = Path(loader.modern.docs_path) / f"seams/{selected_seam}/evidence/modern-screenshot.png"

                        if modern_screenshot.exists():
                            st.image(str(modern_screenshot), use_container_width=True)
                        else:
                            st.info("Modern screenshot not available.")

                    # Difference highlights
                    st.markdown("---")
                    st.subheader("Visual Differences")

                    if "differences" in parity and parity["differences"]:
                        for idx, diff in enumerate(parity["differences"], 1):
                            diff_type = diff.get("type", "unknown")
                            description = diff.get("description", "No description")
                            severity = diff.get("severity", "medium")

                            if severity == "critical":
                                st.error(f"**{idx}. {diff_type}** (Critical): {description}")
                            elif severity == "high":
                                st.warning(f"**{idx}. {diff_type}** (High): {description}")
                            else:
                                st.info(f"**{idx}. {diff_type}** (Low): {description}")

                            # Show diff image if available
                            diff_img_path = Path(loader.modern.docs_path) / f"parity-validation/{selected_seam}/diff-{idx}.png"
                            if diff_img_path.exists():
                                with st.expander(f"View difference #{idx}", expanded=False):
                                    st.image(str(diff_img_path), use_container_width=True)
                    else:
                        st.success("✅ No visual differences detected!")

                except Exception as e:
                    st.error(f"Error loading visual parity results: {e}")
            else:
                st.info(f"Visual parity validation not yet performed for `{selected_seam}`.")

    with tab2:
        st.subheader("Behavioral Parity Validation")

        selected_seam = st.selectbox("Select seam:", seams, key="behavioral_seam")

        if selected_seam:
            # Load behavioral validation results
            behavioral_path = Path(loader.modern.docs_path) / f"parity-validation/{selected_seam}/behavioral-validation.json"

            if behavioral_path.exists():
                try:
                    behavioral = json.loads(behavioral_path.read_text())

                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        score = behavioral.get("parity_score", 0)
                        st.metric("Parity Score", f"{score}/100")

                    with col2:
                        status = behavioral.get("status", "unknown")
                        if status == "pass":
                            st.success("✅ PASS")
                        elif status == "fail":
                            st.error("❌ FAIL")
                        else:
                            st.warning("⏸️ PENDING")

                    with col3:
                        test_count = behavioral.get("tests_run", 0)
                        st.metric("Tests Run", test_count)

                    with col4:
                        failures = behavioral.get("failures", 0)
                        st.metric("Failures", failures)

                    st.progress(score / 100)

                    # Test results
                    st.markdown("---")
                    st.subheader("Behavioral Test Results")

                    if "test_results" in behavioral and behavioral["test_results"]:
                        test_data = []

                        for test in behavioral["test_results"]:
                            test_name = test.get("name", "Unknown")
                            test_status = test.get("status", "unknown")
                            expected = test.get("expected", "N/A")
                            actual = test.get("actual", "N/A")

                            if test_status == "pass":
                                status_icon = "✅ PASS"
                            elif test_status == "fail":
                                status_icon = "❌ FAIL"
                            else:
                                status_icon = "⏸️ SKIP"

                            test_data.append({
                                "Test": test_name,
                                "Status": status_icon,
                                "Expected": str(expected),
                                "Actual": str(actual),
                            })

                        df_tests = pd.DataFrame(test_data)
                        st.dataframe(df_tests, use_container_width=True, hide_index=True)

                        # Show failed tests in detail
                        failed_tests = [t for t in behavioral["test_results"] if t.get("status") == "fail"]

                        if failed_tests:
                            st.markdown("---")
                            st.subheader("Failed Tests Details")

                            for test in failed_tests:
                                with st.expander(f"❌ {test.get('name', 'Unknown')}", expanded=False):
                                    st.markdown(f"**Expected:** `{test.get('expected', 'N/A')}`")
                                    st.markdown(f"**Actual:** `{test.get('actual', 'N/A')}`")
                                    st.markdown(f"**Error:** {test.get('error_message', 'No error message')}")

                    else:
                        st.success("✅ All behavioral tests passed!")

                except Exception as e:
                    st.error(f"Error loading behavioral validation results: {e}")
            else:
                st.info(f"Behavioral validation not yet performed for `{selected_seam}`.")

    with tab3:
        st.subheader("Feature Parity Checklist")

        selected_seam = st.selectbox("Select seam:", seams, key="feature_seam")

        if selected_seam:
            # Check for feature checklist
            checklist_path = Path(loader.modern.docs_path) / f"parity-validation/{selected_seam}/feature-checklist.json"

            if checklist_path.exists():
                try:
                    checklist = json.loads(checklist_path.read_text())

                    features = checklist.get("features", [])

                    if features:
                        total_features = len(features)
                        implemented = sum(1 for f in features if f.get("implemented", False))
                        pct = (implemented / total_features) * 100 if total_features > 0 else 0

                        col1, col2, col3 = st.columns(3)

                        with col1:
                            st.metric("Total Features", total_features)

                        with col2:
                            st.metric("Implemented", implemented)

                        with col3:
                            st.metric("Completeness", f"{pct:.0f}%")

                        st.progress(pct / 100)

                        st.markdown("---")

                        # Feature list
                        feature_data = []

                        for feature in features:
                            name = feature.get("name", "Unknown")
                            implemented = feature.get("implemented", False)
                            verified = feature.get("verified", False)

                            if implemented and verified:
                                status = "✅ Verified"
                            elif implemented:
                                status = "🔵 Implemented"
                            else:
                                status = "⏸️ Pending"

                            feature_data.append({
                                "Feature": name,
                                "Implemented": "✅" if implemented else "❌",
                                "Verified": "✅" if verified else "❌",
                                "Status": status,
                            })

                        df_features = pd.DataFrame(feature_data)
                        st.dataframe(df_features, use_container_width=True, hide_index=True)

                    else:
                        st.info("No features in checklist.")

                except Exception as e:
                    st.error(f"Error loading feature checklist: {e}")
            else:
                st.info(f"Feature checklist not available for `{selected_seam}`.")

                # Show manual checklist template
                st.markdown("---")
                st.subheader("Manual Feature Verification")

                st.markdown("""
                **Verify these aspects match legacy behavior:**

                - [ ] **Authentication** — Login/logout flow identical
                - [ ] **Authorization** — Permission checks match
                - [ ] **Data Display** — Same fields, format, sorting
                - [ ] **Forms** — Same validation rules and error messages
                - [ ] **Actions** — Same side effects (DB changes, emails, etc.)
                - [ ] **Navigation** — Same menu structure and links
                - [ ] **Search/Filters** — Same search logic and filters
                - [ ] **Reports** — Same data, calculations, exports
                - [ ] **Styling** — Same colors, fonts, layout
                - [ ] **Responsiveness** — Same behavior on different screens
                - [ ] **Performance** — Response times comparable or better
                - [ ] **Error Handling** — Same error messages and recovery
                """)

    with tab4:
        st.subheader("API Diff Analysis")

        selected_seam = st.selectbox("Select seam:", seams, key="diff_seam")

        if selected_seam:
            # Check for API diff
            diff_path = Path(loader.modern.docs_path) / f"parity-validation/{selected_seam}/api-diff.json"

            if diff_path.exists():
                try:
                    diff = json.loads(diff_path.read_text())

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        added = len(diff.get("added_endpoints", []))
                        st.metric("Added Endpoints", added)

                    with col2:
                        removed = len(diff.get("removed_endpoints", []))
                        st.metric("Removed Endpoints", removed)

                    with col3:
                        modified = len(diff.get("modified_endpoints", []))
                        st.metric("Modified Endpoints", modified)

                    # Show details
                    if added > 0:
                        with st.expander(f"➕ Added Endpoints ({added})", expanded=False):
                            for endpoint in diff.get("added_endpoints", []):
                                st.code(f"{endpoint.get('method')} {endpoint.get('path')}", language="text")

                    if removed > 0:
                        with st.expander(f"➖ Removed Endpoints ({removed})", expanded=False):
                            for endpoint in diff.get("removed_endpoints", []):
                                st.code(f"{endpoint.get('method')} {endpoint.get('path')}", language="text")

                    if modified > 0:
                        with st.expander(f"🔄 Modified Endpoints ({modified})", expanded=False):
                            for endpoint in diff.get("modified_endpoints", []):
                                st.markdown(f"**{endpoint.get('method')} {endpoint.get('path')}**")
                                changes = endpoint.get("changes", [])
                                for change in changes:
                                    st.markdown(f"- {change}")

                except Exception as e:
                    st.error(f"Error loading API diff: {e}")
            else:
                st.info(f"API diff analysis not available for `{selected_seam}`.")

            # Response comparison
            st.markdown("---")
            st.subheader("Response Comparison")

            response_comparison_path = Path(loader.modern.docs_path) / f"parity-validation/{selected_seam}/response-comparison.json"

            if response_comparison_path.exists():
                try:
                    comparison = json.loads(response_comparison_path.read_text())

                    comparisons = comparison.get("comparisons", [])

                    if comparisons:
                        comp_data = []

                        for comp in comparisons:
                            endpoint = comp.get("endpoint", "Unknown")
                            match = comp.get("match", False)
                            differences = comp.get("differences_count", 0)

                            if match:
                                status = "✅ Match"
                            elif differences == 0:
                                status = "✅ Match"
                            else:
                                status = f"❌ {differences} differences"

                            comp_data.append({
                                "Endpoint": endpoint,
                                "Legacy Response Size": comp.get("legacy_size", "N/A"),
                                "Modern Response Size": comp.get("modern_size", "N/A"),
                                "Status": status,
                            })

                        df_comp = pd.DataFrame(comp_data)
                        st.dataframe(df_comp, use_container_width=True, hide_index=True)

                        # Show detailed differences
                        mismatches = [c for c in comparisons if not c.get("match", False)]

                        if mismatches:
                            st.markdown("---")
                            st.subheader("Response Differences")

                            for comp in mismatches:
                                with st.expander(f"❌ {comp.get('endpoint', 'Unknown')}", expanded=False):
                                    if "differences" in comp:
                                        for diff in comp["differences"]:
                                            st.markdown(f"- {diff}")

                    else:
                        st.info("No response comparisons available.")

                except Exception as e:
                    st.error(f"Error loading response comparison: {e}")
            else:
                st.info(f"Response comparison not available for `{selected_seam}`.")

except Exception as e:
    st.error("Error loading parity validation data")
    st.exception(e)
