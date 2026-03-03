"""
Frontend Comparison Page
Displays UI/UX, performance, and accessibility comparison
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
    page_title="Frontend Comparison",
    page_icon="🎨",
    layout="wide"
)

# Initialize
init_session_state()
config = get_config()

# Header
st.title("🎨 Frontend Comparison")
st.markdown("UI/UX, Performance, and Accessibility Analysis")

# Check if data loaded
if not st.session_state.get('data_loaded', False):
    st.warning("⚠️ No metrics available. Please collect metrics first.")
    st.stop()

# Get metrics
legacy_fe = st.session_state.legacy_metrics.get('frontend', {})
modern_fe = st.session_state.modern_metrics.get('frontend', {})

# Top metrics
st.markdown("## 📊 Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    score = st.session_state.frontend_score
    st.metric("Overall Score", f"{score}/100")

with col2:
    parity = modern_fe.get('feature_parity', 0)
    st.metric("Feature Parity", f"{parity}%")

with col3:
    lighthouse = modern_fe.get('lighthouse', {})
    perf = lighthouse.get('performance', 0)
    st.metric("Performance", f"{perf}/100")

with col4:
    a11y = lighthouse.get('accessibility', 0)
    st.metric("Accessibility", f"{a11y}/100")

st.markdown("---")

# Lighthouse Scores Comparison
st.markdown("## 🚀 Lighthouse Scores")

col1, col2 = st.columns([2, 1])

with col1:
    # Bar chart comparing lighthouse scores
    legacy_lighthouse = legacy_fe.get('lighthouse', {})
    modern_lighthouse = modern_fe.get('lighthouse', {})

    categories = ['Performance', 'Accessibility', 'Best Practices', 'SEO']
    legacy_scores = [
        legacy_lighthouse.get('performance', 0),
        legacy_lighthouse.get('accessibility', 0),
        legacy_lighthouse.get('best_practices', 0),
        legacy_lighthouse.get('seo', 0),
    ]
    modern_scores = [
        modern_lighthouse.get('performance', 0),
        modern_lighthouse.get('accessibility', 0),
        modern_lighthouse.get('best_practices', 0),
        modern_lighthouse.get('seo', 0),
    ]

    fig = go.Figure(data=[
        go.Bar(name='Legacy', x=categories, y=legacy_scores, marker_color='#94a3b8'),
        go.Bar(name='Modern', x=categories, y=modern_scores, marker_color='#3b82f6')
    ])

    fig.update_layout(
        barmode='group',
        title="Lighthouse Score Comparison",
        yaxis_title="Score (0-100)",
        yaxis_range=[0, 100],
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("### Score Details")

    for category, legacy_val, modern_val in zip(categories, legacy_scores, modern_scores):
        delta = modern_val - legacy_val
        if delta > 0:
            st.success(f"**{category}**: {modern_val} (+{delta})")
        elif delta < 0:
            st.error(f"**{category}**: {modern_val} ({delta})")
        else:
            st.info(f"**{category}**: {modern_val} (no change)")

st.markdown("---")

# Feature Parity Matrix
st.markdown("## ✅ Feature Parity")

feature_parity_data = modern_fe.get('feature_parity_details', [])

if feature_parity_data:
    df = pd.DataFrame(feature_parity_data)

    # Show summary
    total = len(df)
    present = len(df[df['modern_present'] == True])
    missing = total - present

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Features", total)
    with col2:
        st.metric("Implemented", present, f"{(present/total*100):.1f}%")
    with col3:
        st.metric("Missing", missing, f"-{(missing/total*100):.1f}%", delta_color="inverse")

    # Show table
    st.dataframe(
        df,
        column_config={
            "screen": "Screen",
            "feature": "Feature",
            "legacy_present": st.column_config.CheckboxColumn("Legacy"),
            "modern_present": st.column_config.CheckboxColumn("Modern"),
            "notes": "Notes"
        },
        hide_index=True,
        use_container_width=True
    )

    # Filter for missing features
    if st.checkbox("Show only missing features"):
        missing_df = df[df['modern_present'] == False]
        st.dataframe(missing_df, hide_index=True, use_container_width=True)

else:
    st.info("Feature parity data not available. Run browser-agent skill first.")

st.markdown("---")

# Bundle Size Comparison
st.markdown("## 📦 Bundle Size")

col1, col2 = st.columns(2)

with col1:
    legacy_bundle = legacy_fe.get('bundle_size_kb', 0)
    st.metric(
        "Legacy Bundle",
        f"{legacy_bundle} KB",
        help="Total JavaScript bundle size"
    )

with col2:
    modern_bundle = modern_fe.get('bundle_size_kb', 0)
    delta = modern_bundle - legacy_bundle
    st.metric(
        "Modern Bundle",
        f"{modern_bundle} KB",
        f"{delta:+d} KB" if delta != 0 else "No change",
        delta_color="inverse"  # Smaller is better
    )

# Bundle breakdown
if modern_fe.get('bundle_breakdown'):
    st.markdown("### Modern Bundle Breakdown")
    breakdown = modern_fe['bundle_breakdown']
    df = pd.DataFrame(list(breakdown.items()), columns=['Package', 'Size (KB)'])
    df = df.sort_values('Size (KB)', ascending=False).head(10)

    fig = px.bar(df, x='Size (KB)', y='Package', orientation='h',
                 title="Top 10 Packages by Size")
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Performance Metrics
st.markdown("## ⚡ Performance Metrics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    legacy_fcp = legacy_fe.get('first_contentful_paint_ms', 0)
    modern_fcp = modern_fe.get('first_contentful_paint_ms', 0)
    delta = modern_fcp - legacy_fcp
    st.metric(
        "First Contentful Paint",
        f"{modern_fcp}ms",
        f"{delta:+d}ms" if delta != 0 else "—",
        delta_color="inverse"
    )

with col2:
    legacy_tti = legacy_fe.get('time_to_interactive_ms', 0)
    modern_tti = modern_fe.get('time_to_interactive_ms', 0)
    delta = modern_tti - legacy_tti
    st.metric(
        "Time to Interactive",
        f"{modern_tti}ms",
        f"{delta:+d}ms" if delta != 0 else "—",
        delta_color="inverse"
    )

with col3:
    legacy_lcp = legacy_fe.get('largest_contentful_paint_ms', 0)
    modern_lcp = modern_fe.get('largest_contentful_paint_ms', 0)
    delta = modern_lcp - legacy_lcp
    st.metric(
        "Largest Contentful Paint",
        f"{modern_lcp}ms",
        f"{delta:+d}ms" if delta != 0 else "—",
        delta_color="inverse"
    )

with col4:
    legacy_cls = legacy_fe.get('cumulative_layout_shift', 0)
    modern_cls = modern_fe.get('cumulative_layout_shift', 0)
    delta = modern_cls - legacy_cls
    st.metric(
        "Cumulative Layout Shift",
        f"{modern_cls:.3f}",
        f"{delta:+.3f}" if delta != 0 else "—",
        delta_color="inverse"
    )

st.markdown("---")

# Accessibility Issues
st.markdown("## ♿ Accessibility")

a11y_issues = modern_fe.get('accessibility_issues', [])

if a11y_issues:
    st.warning(f"⚠️ {len(a11y_issues)} accessibility issues detected")

    # Group by severity
    critical = [i for i in a11y_issues if i['severity'] == 'critical']
    serious = [i for i in a11y_issues if i['severity'] == 'serious']
    moderate = [i for i in a11y_issues if i['severity'] == 'moderate']

    col1, col2, col3 = st.columns(3)
    with col1:
        st.error(f"🔴 Critical: {len(critical)}")
    with col2:
        st.warning(f"🟠 Serious: {len(serious)}")
    with col3:
        st.info(f"🟡 Moderate: {len(moderate)}")

    # Show details
    if st.checkbox("Show accessibility issue details"):
        df = pd.DataFrame(a11y_issues)
        st.dataframe(df, hide_index=True, use_container_width=True)
else:
    st.success("✅ No accessibility issues detected!")

st.markdown("---")

# Browser Compatibility
st.markdown("## 🌐 Browser Compatibility")

compat = modern_fe.get('browser_compatibility', {})

if compat:
    browsers = ['Chrome', 'Firefox', 'Safari', 'Edge']
    support = [compat.get(b.lower(), False) for b in browsers]

    col1, col2, col3, col4 = st.columns(4)
    for col, browser, supported in zip([col1, col2, col3, col4], browsers, support):
        with col:
            if supported:
                st.success(f"✅ {browser}")
            else:
                st.error(f"❌ {browser}")
else:
    st.info("Browser compatibility data not available")

# Footer
st.markdown("---")
st.caption("Data collected from Lighthouse audits and browser-agent skill")
