"""
Session state management for Migration Report Dashboard
"""

import streamlit as st
import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

def init_session_state():
    """Initialize session state variables"""

    # Scores
    if 'overall_score' not in st.session_state:
        st.session_state.overall_score = 0

    if 'frontend_score' not in st.session_state:
        st.session_state.frontend_score = 0

    if 'backend_score' not in st.session_state:
        st.session_state.backend_score = 0

    if 'database_score' not in st.session_state:
        st.session_state.database_score = 0

    if 'quality_score' not in st.session_state:
        st.session_state.quality_score = 0

    if 'nfr_score' not in st.session_state:
        st.session_state.nfr_score = 0

    if 'integration_score' not in st.session_state:
        st.session_state.integration_score = 0

    # Metrics data
    if 'legacy_metrics' not in st.session_state:
        st.session_state.legacy_metrics = {}

    if 'modern_metrics' not in st.session_state:
        st.session_state.modern_metrics = {}

    # Gaps and recommendations
    if 'critical_gaps' not in st.session_state:
        st.session_state.critical_gaps = []

    if 'recommendations' not in st.session_state:
        st.session_state.recommendations = []

    # Metadata
    if 'collection_timestamp' not in st.session_state:
        st.session_state.collection_timestamp = None

    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False

@st.cache_data(ttl=3600)
def load_metrics_from_disk() -> tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Load collected metrics from disk

    Returns:
        Tuple of (legacy_metrics, modern_metrics)
    """
    data_dir = Path(__file__).parent.parent / "data"

    legacy_metrics = {}
    modern_metrics = {}

    # Load legacy metrics
    legacy_path = data_dir / "legacy" / "metrics.json"
    if legacy_path.exists():
        with open(legacy_path, 'r') as f:
            legacy_metrics = json.load(f)

    # Load modern metrics
    modern_path = data_dir / "modern" / "metrics.json"
    if modern_path.exists():
        with open(modern_path, 'r') as f:
            modern_metrics = json.load(f)

    return legacy_metrics, modern_metrics

def load_metrics() -> bool:
    """
    Load metrics into session state

    Returns:
        True if metrics were loaded successfully
    """
    try:
        legacy_metrics, modern_metrics = load_metrics_from_disk()

        if not legacy_metrics or not modern_metrics:
            st.session_state.data_loaded = False
            return False

        # Store in session state
        st.session_state.legacy_metrics = legacy_metrics
        st.session_state.modern_metrics = modern_metrics

        # Calculate scores
        calculate_scores()

        # Identify gaps
        identify_gaps()

        # Generate recommendations
        generate_recommendations()

        # Set metadata
        st.session_state.collection_timestamp = legacy_metrics.get(
            'timestamp',
            datetime.now().isoformat()
        )
        st.session_state.data_loaded = True

        return True

    except Exception as e:
        st.error(f"Error loading metrics: {e}")
        st.session_state.data_loaded = False
        return False

def calculate_scores():
    """Calculate dimension and overall scores"""

    legacy = st.session_state.legacy_metrics
    modern = st.session_state.modern_metrics

    # Frontend score
    frontend_score = calculate_frontend_score(legacy.get('frontend', {}), modern.get('frontend', {}))
    st.session_state.frontend_score = round(frontend_score, 1)

    # Backend score
    backend_score = calculate_backend_score(legacy.get('backend', {}), modern.get('backend', {}))
    st.session_state.backend_score = round(backend_score, 1)

    # Database score
    database_score = calculate_database_score(legacy.get('database', {}), modern.get('database', {}))
    st.session_state.database_score = round(database_score, 1)

    # Quality score
    quality_score = calculate_quality_score(legacy.get('quality', {}), modern.get('quality', {}))
    st.session_state.quality_score = round(quality_score, 1)

    # NFR score
    nfr_score = calculate_nfr_score(legacy.get('nfr', {}), modern.get('nfr', {}))
    st.session_state.nfr_score = round(nfr_score, 1)

    # Integration score
    integration_score = calculate_integration_score(legacy.get('integration', {}), modern.get('integration', {}))
    st.session_state.integration_score = round(integration_score, 1)

    # Overall score (weighted average)
    overall_score = (
        frontend_score * 0.25 +
        backend_score * 0.25 +
        database_score * 0.10 +
        quality_score * 0.20 +
        nfr_score * 0.15 +
        integration_score * 0.05
    )
    st.session_state.overall_score = round(overall_score, 1)

def calculate_frontend_score(legacy: Dict, modern: Dict) -> float:
    """Calculate frontend dimension score"""

    if not modern:
        return 0

    # Feature parity (60%)
    feature_parity = modern.get('feature_parity', 0)

    # Performance (20%) - based on Lighthouse
    lighthouse = modern.get('lighthouse', {})
    performance = lighthouse.get('performance', 0)

    # Accessibility (20%)
    accessibility = lighthouse.get('accessibility', 0)

    score = (feature_parity * 0.6) + (performance * 0.2) + (accessibility * 0.2)
    return score

def calculate_backend_score(legacy: Dict, modern: Dict) -> float:
    """Calculate backend dimension score"""

    if not modern:
        return 0

    # API parity (50%)
    api_parity = modern.get('api_parity', 0) * 100

    # Performance (30%) - based on response time
    response_time = modern.get('avg_response_time_ms', 200)
    performance = max(0, 100 - (response_time - 200) / 10) if response_time > 200 else 100

    # Error handling (20%)
    error_rate = modern.get('error_rate', 0)
    error_handling = max(0, 100 - error_rate * 1000)

    score = (api_parity * 0.5) + (performance * 0.3) + (error_handling * 0.2)
    return score

def calculate_database_score(legacy: Dict, modern: Dict) -> float:
    """Calculate database dimension score"""

    if not modern:
        return 0

    # Schema parity (40%)
    schema_parity = modern.get('schema_parity', 0) * 100

    # Performance (40%)
    query_time = modern.get('avg_query_time_ms', 100)
    performance = max(0, 100 - (query_time - 100) / 5) if query_time > 100 else 100

    # Integrity (20%)
    integrity = modern.get('integrity_score', 100)

    score = (schema_parity * 0.4) + (performance * 0.4) + (integrity * 0.2)
    return score

def calculate_quality_score(legacy: Dict, modern: Dict) -> float:
    """Calculate quality dimension score"""

    if not modern:
        return 0

    # SonarQube (50%)
    sonar = modern.get('sonarqube', {})
    sonar_score = calculate_sonar_score(sonar)

    # Coverage (30%)
    coverage = modern.get('coverage', {}).get('total', 0)

    # Security (20%)
    security_issues = modern.get('security_issues', 0)
    security_score = max(0, 100 - security_issues * 10)

    score = (sonar_score * 0.5) + (coverage * 0.3) + (security_score * 0.2)
    return score

def calculate_sonar_score(sonar: Dict) -> float:
    """Calculate SonarQube composite score"""

    if not sonar:
        return 0

    # Rating to score mapping
    rating_scores = {'A': 100, 'B': 80, 'C': 60, 'D': 40, 'E': 20}

    reliability = rating_scores.get(sonar.get('reliability_rating', 'C'), 60)
    security = rating_scores.get(sonar.get('security_rating', 'C'), 60)
    maintainability = rating_scores.get(sonar.get('maintainability_rating', 'C'), 60)

    # Bugs and vulnerabilities
    bugs = sonar.get('bugs', 0)
    vulnerabilities = sonar.get('vulnerabilities', 0)
    issues_penalty = min(50, (bugs + vulnerabilities) * 5)

    score = ((reliability + security + maintainability) / 3) - issues_penalty
    return max(0, score)

def calculate_nfr_score(legacy: Dict, modern: Dict) -> float:
    """Calculate NFR dimension score"""

    if not modern:
        return 0

    # Performance (40%)
    p95 = modern.get('response_time_p95_ms', 500)
    performance = max(0, 100 - (p95 - 500) / 10) if p95 > 500 else 100

    # Security (30%)
    security_score = modern.get('security_posture', 80)

    # Observability (30%)
    observability = modern.get('observability_score', 70)

    score = (performance * 0.4) + (security_score * 0.3) + (observability * 0.3)
    return score

def calculate_integration_score(legacy: Dict, modern: Dict) -> float:
    """Calculate integration dimension score"""

    if not modern:
        return 0

    # Integration parity
    parity = modern.get('integration_parity', 0) * 100
    return parity

def identify_gaps():
    """Identify critical gaps between legacy and modern"""

    gaps = []
    modern = st.session_state.modern_metrics

    # Check test coverage
    coverage = modern.get('quality', {}).get('coverage', {}).get('total', 0)
    if coverage < 80:
        gaps.append({
            'title': 'Low Test Coverage',
            'description': f'Test coverage is {coverage}%, below threshold of 80%',
            'severity': 'warning',
            'dimension': 'quality'
        })

    # Check API parity
    api_parity = modern.get('backend', {}).get('api_parity', 1.0)
    if api_parity < 0.95:
        missing_count = int((1 - api_parity) * 100)
        gaps.append({
            'title': 'API Parity Gap',
            'description': f'Approximately {missing_count} API endpoints missing or different',
            'severity': 'critical',
            'dimension': 'backend'
        })

    # Check performance
    lighthouse = modern.get('frontend', {}).get('lighthouse', {})
    performance = lighthouse.get('performance', 100)
    if performance < 90:
        gaps.append({
            'title': 'Performance Below Target',
            'description': f'Lighthouse performance score is {performance}, below threshold of 90',
            'severity': 'high',
            'dimension': 'frontend'
        })

    # Check accessibility
    accessibility = lighthouse.get('accessibility', 100)
    if accessibility < 95:
        gaps.append({
            'title': 'Accessibility Issues',
            'description': f'Accessibility score is {accessibility}, below threshold of 95',
            'severity': 'high',
            'dimension': 'frontend'
        })

    # Check SonarQube
    sonar = modern.get('quality', {}).get('sonarqube', {})
    bugs = sonar.get('bugs', 0)
    vulnerabilities = sonar.get('vulnerabilities', 0)
    if bugs + vulnerabilities > 10:
        gaps.append({
            'title': 'High SonarQube Issues',
            'description': f'{bugs} bugs and {vulnerabilities} vulnerabilities detected',
            'severity': 'high',
            'dimension': 'quality'
        })

    st.session_state.critical_gaps = gaps

def generate_recommendations():
    """Generate recommendations based on gaps"""

    recommendations = []

    gaps = st.session_state.critical_gaps

    for gap in gaps:
        if gap['title'] == 'Low Test Coverage':
            recommendations.append({
                'title': 'Increase Test Coverage',
                'description': 'Add unit and integration tests to reach 80% coverage minimum',
                'effort': 'medium',
                'priority': 'high'
            })

        elif gap['title'] == 'API Parity Gap':
            recommendations.append({
                'title': 'Implement Missing APIs',
                'description': 'Review API comparison report and implement missing endpoints',
                'effort': 'high',
                'priority': 'critical'
            })

        elif gap['title'] == 'Performance Below Target':
            recommendations.append({
                'title': 'Optimize Performance',
                'description': 'Run Lighthouse audits and address performance recommendations',
                'effort': 'medium',
                'priority': 'high'
            })

    st.session_state.recommendations = recommendations
