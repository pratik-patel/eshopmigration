"""
Executive Summary Page
High-level overview and migration readiness assessment
"""

import streamlit as st
import plotly.graph_objects as go
from pathlib import Path
import sys
from datetime import datetime

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.config import get_config
from app.state import init_session_state

# Page config
st.set_page_config(
    page_title="Executive Summary",
    page_icon="📊",
    layout="wide"
)

# Initialize
init_session_state()
config = get_config()

# Header
st.title("📊 Executive Summary")
st.markdown("Migration Readiness Assessment & Recommendations")

# Check if data loaded
if not st.session_state.get('data_loaded', False):
    st.warning("⚠️ No metrics available. Please collect metrics first.")
    st.stop()

# Overall Assessment
st.markdown("## 🎯 Migration Readiness")

overall_score = st.session_state.overall_score

# Determine status
if overall_score >= 90:
    status = "✅ Production Ready"
    status_color = "green"
    assessment = """
    The modern application has achieved excellent parity with the legacy system across all dimensions.
    All critical features are implemented, quality metrics meet or exceed targets, and the system is
    ready for production deployment.
    """
elif overall_score >= 75:
    status = "🟢 Near Ready"
    status_color = "blue"
    assessment = """
    The modern application is approaching production readiness. Few gaps remain, and the overall risk
    is low. Address the identified gaps below before deployment, but the migration is on track for success.
    """
elif overall_score >= 60:
    status = "🟡 In Progress"
    status_color = "orange"
    assessment = """
    The modern application has made significant progress but substantial work remains. Several critical
    gaps need to be addressed before the application is ready for production. Continue focused development
    on the priority areas identified below.
    """
else:
    status = "🔴 Not Ready"
    status_color = "red"
    assessment = """
    The modern application is in early stages of development with major gaps across multiple dimensions.
    Significant work is required before production readiness. Review the critical gaps and create a
    comprehensive remediation plan.
    """

# Display overall score with large visual
col1, col2 = st.columns([1, 2])

with col1:
    # Gauge chart for overall score
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=overall_score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Overall Score"},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': status_color},
            'steps': [
                {'range': [0, 60], 'color': "#fee2e2"},
                {'range': [60, 75], 'color': "#fef3c7"},
                {'range': [75, 90], 'color': "#dbeafe"},
                {'range': [90, 100], 'color': "#d1fae5"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(f"### {status}")

with col2:
    st.markdown("### Assessment")
    st.markdown(assessment)

    # Timeline
    st.markdown("### Collection Details")
    timestamp = st.session_state.get('collection_timestamp', 'Unknown')
    st.info(f"**Last Updated**: {timestamp}")

    st.markdown(f"""
    **Legacy App**: {config.legacy.name}
    **Modern App**: {config.modern.name}
    """)

st.markdown("---")

# Dimension Breakdown
st.markdown("## 📈 Dimension Scores")

dimensions = {
    'Frontend': st.session_state.frontend_score,
    'Backend': st.session_state.backend_score,
    'Database': st.session_state.database_score,
    'Quality': st.session_state.quality_score,
    'NFR': st.session_state.nfr_score,
    'Integration': st.session_state.integration_score
}

col1, col2, col3 = st.columns(3)

cols = [col1, col2, col3, col1, col2, col3]

for (dimension, score), col in zip(dimensions.items(), cols):
    with col:
        # Determine status emoji
        if score >= 90:
            emoji = "✅"
        elif score >= 75:
            emoji = "🟢"
        elif score >= 60:
            emoji = "🟡"
        else:
            emoji = "🔴"

        st.metric(f"{emoji} {dimension}", f"{score}/100")

st.markdown("---")

# Critical Gaps
st.markdown("## 🚨 Critical Gaps")

gaps = st.session_state.get('critical_gaps', [])

if gaps:
    # Categorize by severity
    critical = [g for g in gaps if g['severity'] == 'critical']
    high = [g for g in gaps if g['severity'] == 'high']
    warning = [g for g in gaps if g['severity'] == 'warning']

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"### 🔴 Critical ({len(critical)})")
        for gap in critical:
            st.error(f"**{gap['title']}**")
            st.caption(gap['description'])

    with col2:
        st.markdown(f"### 🟠 High ({len(high)})")
        for gap in high:
            st.warning(f"**{gap['title']}**")
            st.caption(gap['description'])

    with col3:
        st.markdown(f"### 🟡 Warning ({len(warning)})")
        for gap in warning:
            st.info(f"**{gap['title']}**")
            st.caption(gap['description'])

else:
    st.success("✅ No critical gaps detected!")

st.markdown("---")

# Recommendations
st.markdown("## 💡 Recommendations")

recommendations = st.session_state.get('recommendations', [])

if recommendations:
    # Priority-based display
    for i, rec in enumerate(recommendations, 1):
        if rec['priority'] == 'critical':
            st.error(f"**{i}. {rec['title']}**")
        elif rec['priority'] == 'high':
            st.warning(f"**{i}. {rec['title']}**")
        else:
            st.info(f"**{i}. {rec['title']}**")

        st.markdown(f"{rec['description']}")
        st.markdown(f"*Effort: {rec['effort']}*")
        st.markdown("---")
else:
    # Generate default recommendations based on gaps
    st.markdown("### Priority Actions")

    for gap in gaps[:3]:  # Top 3 gaps
        st.markdown(f"**{gap['title']}**")
        st.markdown(f"- {gap['description']}")
        st.markdown(f"- *Dimension: {gap['dimension']}*")
        st.markdown("---")

# Risk Assessment
st.markdown("## ⚠️ Risk Assessment")

# Calculate risk level based on score and critical gaps
critical_gaps_count = len([g for g in gaps if g['severity'] == 'critical'])

if overall_score >= 85 and critical_gaps_count == 0:
    risk_level = "🟢 Low Risk"
    risk_description = "The migration has low risk. The modern application is feature-complete and meets quality standards."
elif overall_score >= 70 and critical_gaps_count < 3:
    risk_level = "🟡 Medium Risk"
    risk_description = "The migration has moderate risk. Address identified gaps before deployment to reduce risk."
else:
    risk_level = "🔴 High Risk"
    risk_description = "The migration has high risk. Significant gaps exist that could impact production readiness."

col1, col2 = st.columns([1, 2])

with col1:
    st.markdown(f"### {risk_level}")
    st.metric("Critical Gaps", critical_gaps_count)

with col2:
    st.markdown(risk_description)

    st.markdown("""
    **Risk Factors**:
    - Critical functionality gaps
    - Quality metrics below thresholds
    - Security vulnerabilities
    - Performance issues
    - Data integrity concerns
    """)

st.markdown("---")

# Next Steps
st.markdown("## 🎯 Next Steps")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Immediate Actions")
    st.markdown("""
    1. **Address Critical Gaps**: Focus on red items first
    2. **Run Integration Tests**: Verify end-to-end functionality
    3. **Security Review**: Fix any vulnerabilities
    4. **Performance Testing**: Run load tests
    5. **Stakeholder Review**: Present findings to decision makers
    """)

with col2:
    st.markdown("### Before Deployment")
    st.markdown("""
    - ✅ Overall score ≥ 85
    - ✅ No critical gaps remaining
    - ✅ All integration tests passing
    - ✅ Security scan clean
    - ✅ Performance benchmarks met
    - ✅ Stakeholder sign-off obtained
    """)

# Timeline Estimate
st.markdown("---")
st.markdown("## 📅 Estimated Timeline")

# Simple timeline estimation based on gaps
total_gaps = len(gaps)
critical_count = len([g for g in gaps if g['severity'] == 'critical'])
high_count = len([g for g in gaps if g['severity'] == 'high'])

# Rough estimation: critical=3 days, high=2 days, warning=1 day
estimated_days = (critical_count * 3) + (high_count * 2) + ((total_gaps - critical_count - high_count) * 1)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Estimated Effort", f"{estimated_days} days")

with col2:
    st.metric("Gaps to Address", total_gaps)

with col3:
    if overall_score >= 85:
        st.success("Ready for deployment")
    elif overall_score >= 70:
        st.warning("1-2 weeks to ready")
    else:
        st.error("3-4 weeks to ready")

st.info("""
**Note**: This is a rough estimate based on identified gaps. Actual timeline depends on team size,
complexity, and other factors. Review with your development team for accurate planning.
""")

st.markdown("---")

# Report Export
st.markdown("## 📥 Export Report")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("📄 Export PDF", use_container_width=True):
        st.info("PDF export will be available soon")

with col2:
    if st.button("📊 Export Excel", use_container_width=True):
        st.info("Excel export will be available soon")

with col3:
    if st.button("📋 Copy Summary", use_container_width=True):
        summary_text = f"""
Migration Assessment Summary
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

Overall Score: {overall_score}/100 - {status}

Dimension Scores:
- Frontend: {dimensions['Frontend']}/100
- Backend: {dimensions['Backend']}/100
- Database: {dimensions['Database']}/100
- Quality: {dimensions['Quality']}/100
- NFR: {dimensions['NFR']}/100
- Integration: {dimensions['Integration']}/100

Critical Gaps: {critical_gaps_count}
Estimated Effort: {estimated_days} days
"""
        st.code(summary_text, language=None)

with col4:
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.session_state.clear()
        st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #64748b; font-size: 0.875rem;'>
    <p><strong>Migration Assessment Dashboard</strong></p>
    <p>For questions or support, contact your migration team lead</p>
</div>
""", unsafe_allow_html=True)
