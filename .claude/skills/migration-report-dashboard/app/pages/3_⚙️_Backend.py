"""
Backend Comparison Page
API endpoints, response times, and error rates
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from pathlib import Path
import sys

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.config import get_config
from app.state import init_session_state

# Page config
st.set_page_config(
    page_title="Backend Comparison",
    page_icon="⚙️",
    layout="wide"
)

# Initialize
init_session_state()
config = get_config()

# Header
st.title("⚙️ Backend Comparison")
st.markdown("API Endpoints, Performance, and Reliability")

# Check if data loaded
if not st.session_state.get('data_loaded', False):
    st.warning("⚠️ No metrics available. Please collect metrics first.")
    st.stop()

# Get metrics
legacy_be = st.session_state.legacy_metrics.get('backend', {})
modern_be = st.session_state.modern_metrics.get('backend', {})

# Top metrics
st.markdown("## 📊 Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    score = st.session_state.backend_score
    st.metric("Overall Score", f"{score}/100")

with col2:
    parity = modern_be.get('api_parity', 0) * 100
    st.metric("API Parity", f"{parity:.1f}%")

with col3:
    response_time = modern_be.get('avg_response_time_ms', 0)
    st.metric("Avg Response Time", f"{response_time:.0f}ms")

with col4:
    error_rate = modern_be.get('error_rate', 0) * 100
    st.metric("Error Rate", f"{error_rate:.2f}%")

st.markdown("---")

# API Endpoints Comparison
st.markdown("## 🔗 API Endpoints")

col1, col2 = st.columns([2, 1])

with col1:
    # Endpoints comparison table
    modern_endpoints = modern_be.get('endpoints', [])

    if modern_endpoints:
        # Create dataframe
        df = pd.DataFrame(modern_endpoints)
        df = df[['path', 'method', 'avg_response_time_ms', 'success_rate', 'accessible']]
        df.columns = ['Endpoint', 'Method', 'Avg Response (ms)', 'Success Rate', 'Accessible']

        # Color code based on performance
        def color_response_time(val):
            if val is None or val == 0:
                return 'background-color: #fee2e2'  # Red
            elif val < 100:
                return 'background-color: #d1fae5'  # Green
            elif val < 200:
                return 'background-color: #fef3c7'  # Yellow
            else:
                return 'background-color: #fed7aa'  # Orange

        st.dataframe(
            df.style.applymap(color_response_time, subset=['Avg Response (ms)']),
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info("No API endpoints discovered. Configure OpenAPI/Swagger URL.")

with col2:
    st.markdown("### Endpoint Statistics")

    total = modern_be.get('total_endpoints', 0)
    accessible = modern_be.get('accessible_endpoints', 0)
    inaccessible = total - accessible

    if total > 0:
        # Pie chart
        fig = go.Figure(data=[go.Pie(
            labels=['Accessible', 'Inaccessible'],
            values=[accessible, inaccessible],
            marker=dict(colors=['#10b981', '#ef4444'])
        )])
        fig.update_layout(height=300, showlegend=True)
        st.plotly_chart(fig, use_container_width=True)

        st.metric("Total Endpoints", total)
        st.metric("Accessible", accessible, f"{(accessible/total*100):.1f}%")
    else:
        st.info("No endpoints data available")

st.markdown("---")

# Response Time Distribution
st.markdown("## ⚡ Response Time Analysis")

if modern_endpoints:
    # Box plot of response times
    response_times = [e['avg_response_time_ms'] for e in modern_endpoints if e['avg_response_time_ms'] is not None]

    if response_times:
        col1, col2 = st.columns([2, 1])

        with col1:
            fig = go.Figure()
            fig.add_trace(go.Box(
                y=response_times,
                name='Modern App',
                marker_color='#3b82f6'
            ))

            fig.update_layout(
                title="Response Time Distribution",
                yaxis_title="Response Time (ms)",
                height=400
            )

            # Add threshold line
            threshold = config.scoring.thresholds.api_response_time_ms
            fig.add_hline(y=threshold, line_dash="dash", line_color="red",
                          annotation_text=f"Threshold: {threshold}ms")

            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("### Statistics")

            st.metric("Mean", f"{modern_be.get('avg_response_time_ms', 0):.1f}ms")
            st.metric("Median", f"{modern_be.get('median_response_time_ms', 0):.1f}ms")
            st.metric("P95", f"{modern_be.get('p95_response_time_ms', 0):.1f}ms")
            st.metric("P99", f"{modern_be.get('p99_response_time_ms', 0):.1f}ms")

            # Fastest and slowest
            fastest = modern_be.get('fastest_endpoint')
            slowest = modern_be.get('slowest_endpoint')

            if fastest:
                st.success(f"⚡ Fastest: `{fastest}`")
            if slowest:
                st.warning(f"🐌 Slowest: `{slowest}`")

st.markdown("---")

# Error Handling
st.markdown("## 🚨 Error Handling")

col1, col2, col3 = st.columns(3)

with col1:
    error_rate = modern_be.get('error_rate', 0) * 100
    if error_rate < 1:
        st.success(f"✅ Low Error Rate: {error_rate:.2f}%")
    elif error_rate < 5:
        st.warning(f"⚠️ Moderate Error Rate: {error_rate:.2f}%")
    else:
        st.error(f"🔴 High Error Rate: {error_rate:.2f}%")

with col2:
    # Count failed endpoints
    failed = len([e for e in modern_endpoints if not e['accessible']])
    if failed == 0:
        st.success(f"✅ All endpoints accessible")
    else:
        st.error(f"🔴 {failed} endpoints failed")

with col3:
    # Success rate
    success_rates = [e['success_rate'] for e in modern_endpoints]
    avg_success = sum(success_rates) / len(success_rates) * 100 if success_rates else 0
    st.metric("Avg Success Rate", f"{avg_success:.1f}%")

# Failed endpoints list
failed_endpoints = [e for e in modern_endpoints if not e['accessible']]
if failed_endpoints:
    st.markdown("### Failed Endpoints")
    failed_df = pd.DataFrame(failed_endpoints)
    failed_df = failed_df[['path', 'method', 'errors']]
    st.dataframe(failed_df, hide_index=True, use_container_width=True)

st.markdown("---")

# API Parity Analysis
st.markdown("## 🔄 API Parity")

legacy_total = legacy_be.get('total_endpoints', 0)
modern_total = modern_be.get('total_endpoints', 0)

col1, col2 = st.columns(2)

with col1:
    st.metric("Legacy Endpoints", legacy_total)
    st.metric("Modern Endpoints", modern_total)

    delta = modern_total - legacy_total
    if delta >= 0:
        st.success(f"✅ {delta} additional endpoints in modern app")
    else:
        st.error(f"🔴 {abs(delta)} endpoints missing in modern app")

with col2:
    parity_score = modern_be.get('api_parity', 0) * 100

    if parity_score >= 95:
        st.success(f"✅ Excellent API Parity: {parity_score:.1f}%")
    elif parity_score >= 80:
        st.warning(f"⚠️ Good API Parity: {parity_score:.1f}%")
    else:
        st.error(f"🔴 Low API Parity: {parity_score:.1f}%")

    st.info("""
    **API Parity Score** measures the percentage of legacy endpoints
    that have been implemented in the modern application.
    """)

# Recommendations
st.markdown("---")
st.markdown("## 💡 Recommendations")

recommendations = []

# Check response time
if modern_be.get('avg_response_time_ms', 0) > config.scoring.thresholds.api_response_time_ms:
    recommendations.append({
        'priority': 'High',
        'issue': 'High Response Times',
        'recommendation': 'Optimize slow endpoints. Consider caching, database indexing, or async processing.'
    })

# Check error rate
if modern_be.get('error_rate', 0) > config.scoring.thresholds.api_error_rate:
    recommendations.append({
        'priority': 'Critical',
        'issue': 'High Error Rate',
        'recommendation': 'Investigate and fix failing endpoints. Add proper error handling and logging.'
    })

# Check API parity
if modern_be.get('api_parity', 1.0) < config.scoring.thresholds.api_parity:
    recommendations.append({
        'priority': 'Critical',
        'issue': 'Missing API Endpoints',
        'recommendation': 'Implement missing endpoints to reach feature parity with legacy application.'
    })

if recommendations:
    for rec in recommendations:
        if rec['priority'] == 'Critical':
            st.error(f"🔴 **{rec['priority']}**: {rec['issue']}")
        elif rec['priority'] == 'High':
            st.warning(f"🟠 **{rec['priority']}**: {rec['issue']}")
        else:
            st.info(f"🟡 **{rec['priority']}**: {rec['issue']}")

        st.markdown(f"*Recommendation: {rec['recommendation']}*")
else:
    st.success("✅ No critical backend issues detected!")

# Footer
st.markdown("---")
st.caption("Data collected from API discovery and performance testing")
