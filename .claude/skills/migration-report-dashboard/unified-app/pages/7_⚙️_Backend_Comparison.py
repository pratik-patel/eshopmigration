"""
Backend Comparison Page
API endpoints, performance, and architecture comparison
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

st.set_page_config(page_title="Backend Comparison", page_icon="⚙️", layout="wide")

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

st.title("⚙️ Backend Comparison")
st.markdown("### Legacy API vs Modern FastAPI implementation")

if not data_loaded:
    st.error("Data loading failed. Check paths and data sources.")
    st.stop()

try:
    # Get backend comparison data
    backend_comp = loader.get_backend_comparison()

    # High-level comparison
    st.subheader("Technology Stack Comparison")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🏛️ Legacy System")
        st.info(f"**Framework:** {backend_comp['legacy']['framework']}")
        st.info(f"**Pattern:** {backend_comp['legacy']['pattern']}")

        legacy_metrics = loader.legacy.load_metrics()
        if legacy_metrics:
            st.metric("Throughput", f"{legacy_metrics.throughput} req/s")
            st.metric("Error Rate", f"{legacy_metrics.error_rate}%")
        else:
            st.metric("Throughput", "N/A")
            st.metric("Error Rate", "N/A")

    with col2:
        st.markdown("### 🚀 Modern System")
        st.success(f"**Framework:** {backend_comp['modern']['framework']}")
        st.success(f"**Pattern:** {backend_comp['modern']['pattern']}")
        st.info("Performance metrics available after implementation")

    st.markdown("---")

    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["🔌 API Endpoints", "📊 Performance", "🗄️ Data Access", "🏗️ Architecture"])

    with tab1:
        st.subheader("API Endpoint Comparison")

        seams = loader.modern.get_all_seams()

        if not seams:
            st.info("No seams discovered yet. Run Phase 0 (Discovery Loop) first.")
        else:
            selected_seam = st.selectbox("Select seam:", seams, key="api_seam")

            if selected_seam:
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("### 🏛️ Legacy Endpoints")

                    # Check for call chains documentation
                    call_chains_path = Path(loader.modern.docs_path) / f"seams/{selected_seam}/call-chains.md"

                    if call_chains_path.exists():
                        content = call_chains_path.read_text(encoding="utf-8")

                        # Try to extract endpoints
                        import re
                        endpoint_pattern = r'`([A-Z]+)\s+(/[^\s`]+)`'
                        endpoints = re.findall(endpoint_pattern, content)

                        if endpoints:
                            for method, path in endpoints:
                                st.code(f"{method} {path}", language="text")
                        else:
                            st.markdown(content[:500] + "..." if len(content) > 500 else content)
                    else:
                        st.info("Call chains documentation not found.")

                with col2:
                    st.markdown("### 🚀 Modern Endpoints")

                    # Check for OpenAPI contract
                    contract_path = Path(loader.modern.docs_path) / f"seams/{selected_seam}/contracts/openapi.yaml"

                    if contract_path.exists():
                        try:
                            import yaml
                            contract = yaml.safe_load(contract_path.read_text())

                            if "paths" in contract:
                                for path, methods in contract["paths"].items():
                                    for method in methods.keys():
                                        st.code(f"{method.upper()} {path}", language="text")
                            else:
                                st.info("No paths defined in contract yet.")

                        except Exception as e:
                            st.error(f"Error parsing OpenAPI contract: {e}")
                    else:
                        st.info("OpenAPI contract not yet created.")

                # Endpoint mapping
                st.markdown("---")
                st.subheader("Endpoint Mapping")

                mapping_path = Path(loader.modern.docs_path) / f"seams/{selected_seam}/api-mapping.md"

                if mapping_path.exists():
                    content = mapping_path.read_text(encoding="utf-8")
                    st.markdown(content)
                else:
                    st.info("API mapping documentation not available.")

    with tab2:
        st.subheader("Performance Metrics")

        # Legacy performance
        st.markdown("### 🏛️ Legacy Performance")

        legacy_metrics = loader.legacy.load_metrics()

        if legacy_metrics:
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Throughput", f"{legacy_metrics.throughput} req/s")

            with col2:
                st.metric("P95 Response Time", f"{legacy_metrics.response_time_p95}ms")

            with col3:
                st.metric("Error Rate", f"{legacy_metrics.error_rate}%")

            with col4:
                st.metric("Avg Response Time", f"{legacy_metrics.response_time_avg}ms")

            # Show response time distribution
            st.markdown("---")
            st.subheader("Legacy Response Time Distribution")

            dist_data = [
                {"Percentile": "P50", "Time (ms)": legacy_metrics.response_time_p50},
                {"Percentile": "P95", "Time (ms)": legacy_metrics.response_time_p95},
                {"Percentile": "P99", "Time (ms)": legacy_metrics.response_time_p99},
            ]

            df = pd.DataFrame(dist_data)
            st.bar_chart(df.set_index("Percentile"))

        else:
            st.info("Legacy performance metrics not available.")

        # Modern performance
        st.markdown("---")
        st.markdown("### 🚀 Modern Performance")

        seams = loader.modern.get_all_seams()

        if seams:
            selected_seam = st.selectbox("Select seam:", seams, key="perf_seam")

            # Check for performance test results
            perf_path = Path(loader.modern.docs_path) / f"tracking/seams/{selected_seam}/performance-test.json"

            if perf_path.exists():
                try:
                    perf = json.loads(perf_path.read_text())

                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        st.metric("Throughput", f"{perf.get('throughput', 0)} req/s")

                    with col2:
                        st.metric("P95 Response Time", f"{perf.get('response_time_p95', 0)}ms")

                    with col3:
                        st.metric("Error Rate", f"{perf.get('error_rate', 0)}%")

                    with col4:
                        st.metric("Avg Response Time", f"{perf.get('response_time_avg', 0)}ms")

                    # Comparison with legacy
                    if legacy_metrics:
                        st.markdown("---")
                        st.subheader("Performance Improvement")

                        col1, col2, col3 = st.columns(3)

                        with col1:
                            improvement = ((legacy_metrics.response_time_p95 - perf.get('response_time_p95', 0)) / legacy_metrics.response_time_p95) * 100
                            st.metric("Response Time (P95)", f"{improvement:+.1f}%", delta_color="normal" if improvement > 0 else "inverse")

                        with col2:
                            throughput_improvement = ((perf.get('throughput', 0) - legacy_metrics.throughput) / legacy_metrics.throughput) * 100
                            st.metric("Throughput", f"{throughput_improvement:+.1f}%", delta_color="normal" if throughput_improvement > 0 else "inverse")

                        with col3:
                            error_improvement = ((legacy_metrics.error_rate - perf.get('error_rate', 0)) / legacy_metrics.error_rate) * 100 if legacy_metrics.error_rate > 0 else 0
                            st.metric("Error Rate", f"{error_improvement:+.1f}%", delta_color="normal" if error_improvement > 0 else "inverse")

                except Exception as e:
                    st.error(f"Error loading performance results: {e}")
            else:
                st.info("Performance tests not yet run for this seam.")
        else:
            st.info("No seams available.")

    with tab3:
        st.subheader("Data Access Patterns")

        seams = loader.modern.get_all_seams()

        if not seams:
            st.info("No seams discovered yet.")
        else:
            selected_seam = st.selectbox("Select seam:", seams, key="data_seam")

            if selected_seam:
                # Check for data access documentation
                data_access_path = Path(loader.modern.docs_path) / f"seams/{selected_seam}/data-access.md"

                if data_access_path.exists():
                    content = data_access_path.read_text(encoding="utf-8")
                    st.markdown(content)
                else:
                    st.info("Data access documentation not found. Run Phase 1 (Per-Seam Discovery).")

                # Show query examples if available
                st.markdown("---")
                st.subheader("Query Patterns")

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("**Legacy Pattern**")
                    st.code("""
// Entity Framework (sync)
var products = db.Products
    .Where(p => p.CategoryId == categoryId)
    .ToList();
                    """, language="csharp")

                with col2:
                    st.markdown("**Modern Pattern**")
                    st.code("""
# SQLAlchemy async
result = await session.execute(
    select(Product)
    .where(Product.category_id == category_id)
)
products = result.scalars().all()
                    """, language="python")

    with tab4:
        st.subheader("Architecture Comparison")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 🏛️ Legacy Architecture")

            legacy_arch = loader.legacy.load_architecture()

            if legacy_arch:
                st.info(f"**Framework:** {legacy_arch.framework}")
                st.info(f"**Pattern:** {legacy_arch.pattern}")

                if legacy_arch.layers:
                    st.markdown("**Layers:**")
                    for layer in legacy_arch.layers:
                        st.markdown(f"- {layer}")

                if legacy_arch.dependencies:
                    with st.expander("📦 Key Dependencies", expanded=False):
                        for dep in legacy_arch.dependencies[:10]:
                            st.markdown(f"- `{dep}`")
            else:
                st.info("Legacy architecture data not available.")

        with col2:
            st.markdown("### 🚀 Modern Architecture")

            st.success("**Framework:** FastAPI + Python 3.12")
            st.success("**Pattern:** RESTful API with async")

            st.markdown("**Layers:**")
            st.markdown("- API Routes (FastAPI routers)")
            st.markdown("- Business Logic (Service layer)")
            st.markdown("- Data Access (SQLAlchemy async)")
            st.markdown("- Database (PostgreSQL/SQLite)")

            st.markdown("**Key Features:**")
            st.markdown("- ✅ Async/await throughout")
            st.markdown("- ✅ Dependency injection via Depends()")
            st.markdown("- ✅ Type safety with Pydantic v2")
            st.markdown("- ✅ OpenAPI auto-documentation")
            st.markdown("- ✅ WebSocket support for real-time")

        # Architecture diagram if available
        st.markdown("---")
        st.subheader("Architecture Diagram")

        arch_diagram = Path(loader.modern.docs_path) / "architecture-diagram.png"

        if arch_diagram.exists():
            st.image(str(arch_diagram), use_container_width=True)
        else:
            st.info("Architecture diagram not available. Check `docs/architecture-design.md` for details.")

except Exception as e:
    st.error("Error loading backend comparison")
    st.exception(e)
