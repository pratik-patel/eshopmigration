"""
Quality Metrics Page
SonarQube analysis, test coverage, and security
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
    page_title="Quality Metrics",
    page_icon="✅",
    layout="wide"
)

# Initialize
init_session_state()
config = get_config()

# Header
st.title("✅ Quality Metrics")
st.markdown("Code Quality, Test Coverage, and Security Analysis")

# Check if data loaded
if not st.session_state.get('data_loaded', False):
    st.warning("⚠️ No metrics available. Please collect metrics first.")
    st.stop()

# Get metrics
legacy_quality = st.session_state.legacy_metrics.get('quality', {})
modern_quality = st.session_state.modern_metrics.get('quality', {})

# Top metrics
st.markdown("## 📊 Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    score = st.session_state.quality_score
    st.metric("Overall Score", f"{score}/100")

with col2:
    coverage = modern_quality.get('coverage', {}).get('total', 0)
    st.metric("Test Coverage", f"{coverage:.1f}%")

with col3:
    sonar = modern_quality.get('sonarqube', {})
    bugs = sonar.get('bugs', 0)
    st.metric("Bugs", bugs)

with col4:
    vulnerabilities = sonar.get('vulnerabilities', 0)
    st.metric("Vulnerabilities", vulnerabilities)

st.markdown("---")

# SonarQube Quality Ratings
st.markdown("## 🎯 SonarQube Ratings")

sonar_modern = modern_quality.get('sonarqube', {})
sonar_legacy = legacy_quality.get('sonarqube', {})

col1, col2 = st.columns([2, 1])

with col1:
    # Ratings comparison
    categories = ['Reliability', 'Security', 'Maintainability']
    legacy_ratings = [
        sonar_legacy.get('reliability_rating', 'C'),
        sonar_legacy.get('security_rating', 'C'),
        sonar_legacy.get('maintainability_rating', 'C')
    ]
    modern_ratings = [
        sonar_modern.get('reliability_rating', 'C'),
        sonar_modern.get('security_rating', 'C'),
        sonar_modern.get('maintainability_rating', 'C')
    ]

    # Convert ratings to numeric for display
    rating_map = {'A': 5, 'B': 4, 'C': 3, 'D': 2, 'E': 1}
    legacy_numeric = [rating_map.get(r, 3) for r in legacy_ratings]
    modern_numeric = [rating_map.get(r, 3) for r in modern_ratings]

    fig = go.Figure(data=[
        go.Bar(name='Legacy', x=categories, y=legacy_numeric, text=legacy_ratings,
               marker_color='#94a3b8'),
        go.Bar(name='Modern', x=categories, y=modern_numeric, text=modern_ratings,
               marker_color='#3b82f6')
    ])

    fig.update_layout(
        barmode='group',
        title="Quality Ratings Comparison",
        yaxis=dict(
            tickmode='array',
            tickvals=[1, 2, 3, 4, 5],
            ticktext=['E', 'D', 'C', 'B', 'A']
        ),
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("### Rating Details")

    def rating_color(rating):
        if rating == 'A':
            return '🟢'
        elif rating == 'B':
            return '🟡'
        elif rating == 'C':
            return '🟠'
        else:
            return '🔴'

    for category, modern_rating in zip(categories, modern_ratings):
        st.markdown(f"{rating_color(modern_rating)} **{category}**: {modern_rating}")

    st.markdown("---")

    # Target ratings
    st.markdown("### Targets")
    st.info(f"Reliability: {config.scoring.thresholds.sonar_reliability}")
    st.info(f"Security: {config.scoring.thresholds.sonar_security}")
    st.info(f"Maintainability: {config.scoring.thresholds.sonar_maintainability}")

st.markdown("---")

# Issues Breakdown
st.markdown("## 🐛 Issues Analysis")

col1, col2, col3 = st.columns(3)

with col1:
    bugs = sonar_modern.get('bugs', 0)
    if bugs == 0:
        st.success("✅ No Bugs")
    elif bugs < 10:
        st.warning(f"⚠️ {bugs} Bugs")
    else:
        st.error(f"🔴 {bugs} Bugs")

with col2:
    vulnerabilities = sonar_modern.get('vulnerabilities', 0)
    if vulnerabilities == 0:
        st.success("✅ No Vulnerabilities")
    elif vulnerabilities < 5:
        st.warning(f"⚠️ {vulnerabilities} Vulnerabilities")
    else:
        st.error(f"🔴 {vulnerabilities} Vulnerabilities")

with col3:
    code_smells = sonar_modern.get('code_smells', 0)
    if code_smells < 50:
        st.success(f"✅ {code_smells} Code Smells")
    elif code_smells < 200:
        st.warning(f"⚠️ {code_smells} Code Smells")
    else:
        st.error(f"🔴 {code_smells} Code Smells")

# Issues by severity
issues_by_severity = sonar_modern.get('issues_by_severity', {})

if issues_by_severity:
    st.markdown("### Issues by Severity")

    severities = ['blocker', 'critical', 'major', 'minor', 'info']
    counts = [issues_by_severity.get(s, 0) for s in severities]

    fig = px.bar(
        x=severities,
        y=counts,
        labels={'x': 'Severity', 'y': 'Count'},
        color=counts,
        color_continuous_scale=['#10b981', '#fbbf24', '#f97316', '#ef4444', '#7f1d1d']
    )

    fig.update_layout(height=300, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Test Coverage
st.markdown("## 🧪 Test Coverage")

coverage_modern = modern_quality.get('coverage', {})
coverage_legacy = legacy_quality.get('coverage', {})

col1, col2 = st.columns([2, 1])

with col1:
    # Coverage comparison
    coverage_types = ['Line', 'Branch', 'Function']
    legacy_cov = [
        coverage_legacy.get('line', 0),
        coverage_legacy.get('branch', 0),
        coverage_legacy.get('function', 0)
    ]
    modern_cov = [
        coverage_modern.get('line', 0),
        coverage_modern.get('branch', 0),
        coverage_modern.get('function', 0)
    ]

    fig = go.Figure(data=[
        go.Bar(name='Legacy', x=coverage_types, y=legacy_cov,
               marker_color='#94a3b8'),
        go.Bar(name='Modern', x=coverage_types, y=modern_cov,
               marker_color='#3b82f6')
    ])

    fig.update_layout(
        barmode='group',
        title="Code Coverage Comparison",
        yaxis_title="Coverage (%)",
        yaxis_range=[0, 100],
        height=400
    )

    # Add threshold line
    threshold = config.scoring.thresholds.test_coverage
    fig.add_hline(y=threshold, line_dash="dash", line_color="red",
                  annotation_text=f"Target: {threshold}%")

    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("### Coverage Details")

    total_coverage = coverage_modern.get('total', 0)
    if total_coverage >= config.scoring.thresholds.test_coverage:
        st.success(f"✅ {total_coverage:.1f}%")
    else:
        st.error(f"🔴 {total_coverage:.1f}%")

    st.metric("Lines Covered",
              f"{coverage_modern.get('lines_covered', 0)} / {coverage_modern.get('lines_total', 0)}")
    st.metric("Branches Covered",
              f"{coverage_modern.get('branches_covered', 0)} / {coverage_modern.get('branches_total', 0)}")
    st.metric("Functions Covered",
              f"{coverage_modern.get('functions_covered', 0)} / {coverage_modern.get('functions_total', 0)}")

st.markdown("---")

# Technical Debt
st.markdown("## 💳 Technical Debt")

tech_debt_mins = sonar_modern.get('technical_debt_minutes', 0)
tech_debt_hours = tech_debt_mins / 60
tech_debt_days = tech_debt_hours / 8

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Debt", f"{tech_debt_days:.1f} days")

with col2:
    loc = sonar_modern.get('lines_of_code', 1)
    debt_ratio = (tech_debt_mins / loc) * 100 if loc > 0 else 0
    st.metric("Debt Ratio", f"{debt_ratio:.2f}%")

with col3:
    complexity = sonar_modern.get('complexity', 0)
    st.metric("Complexity", complexity)

# Duplication
duplication = sonar_modern.get('duplicated_lines_density', 0)

if duplication < config.scoring.thresholds.code_duplication:
    st.success(f"✅ Low Code Duplication: {duplication:.1f}%")
else:
    st.warning(f"⚠️ Code Duplication: {duplication:.1f}% (threshold: {config.scoring.thresholds.code_duplication}%)")

st.markdown("---")

# Security Analysis
st.markdown("## 🔒 Security")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Vulnerabilities")

    vulnerabilities = sonar_modern.get('vulnerabilities', 0)
    security_rating = sonar_modern.get('security_rating', 'C')

    if vulnerabilities == 0 and security_rating == 'A':
        st.success("✅ Excellent Security Posture")
    elif vulnerabilities < 5:
        st.warning(f"⚠️ {vulnerabilities} vulnerabilities found")
    else:
        st.error(f"🔴 {vulnerabilities} vulnerabilities found")

    st.markdown(f"**Security Rating**: {security_rating}")

with col2:
    st.markdown("### Security Issues")

    security_issues = modern_quality.get('security_issues', 0)

    if security_issues == 0:
        st.success("✅ No security issues detected")
    else:
        st.error(f"🔴 {security_issues} security issues")

    st.info("""
    **Security scan** includes:
    - Dependency vulnerabilities
    - Code security hotspots
    - Insecure configurations
    """)

st.markdown("---")

# Recommendations
st.markdown("## 💡 Recommendations")

recommendations = []

# Coverage check
total_coverage = coverage_modern.get('total', 0)
if total_coverage < config.scoring.thresholds.test_coverage:
    recommendations.append({
        'priority': 'High',
        'issue': f'Low Test Coverage ({total_coverage:.1f}%)',
        'recommendation': f'Increase test coverage to at least {config.scoring.thresholds.test_coverage}%. Focus on untested modules first.'
    })

# Bugs check
bugs = sonar_modern.get('bugs', 0)
if bugs > 10:
    recommendations.append({
        'priority': 'Critical',
        'issue': f'{bugs} Bugs Detected',
        'recommendation': 'Address critical and major bugs before deployment. Review SonarQube for details.'
    })

# Vulnerabilities check
if vulnerabilities > 0:
    recommendations.append({
        'priority': 'Critical',
        'issue': f'{vulnerabilities} Security Vulnerabilities',
        'recommendation': 'Fix security vulnerabilities immediately. Update dependencies and review code security hotspots.'
    })

# Code smells check
code_smells = sonar_modern.get('code_smells', 0)
if code_smells > 100:
    recommendations.append({
        'priority': 'Medium',
        'issue': f'{code_smells} Code Smells',
        'recommendation': 'Refactor code to improve maintainability. Start with critical and major smells.'
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
    st.success("✅ No critical quality issues detected!")

# Footer
st.markdown("---")
st.caption("Data collected from SonarQube and test coverage reports")
