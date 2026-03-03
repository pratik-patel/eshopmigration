"""
Get Overall Migration Score
Outputs the current migration readiness score
"""

import json
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.state import calculate_scores

def main():
    """Get overall score from metrics"""
    metrics_file = Path(__file__).parent.parent / "data" / "modern" / "metrics.json"

    if not metrics_file.exists():
        print("0", file=sys.stderr)
        print("Error: No metrics found. Run collection first.", file=sys.stderr)
        sys.exit(1)

    try:
        with open(metrics_file, 'r') as f:
            modern_metrics = json.load(f)

        # Calculate scores (simplified version without session state)
        frontend_score = calculate_frontend_score_simple(modern_metrics.get('frontend', {}))
        backend_score = calculate_backend_score_simple(modern_metrics.get('backend', {}))
        database_score = calculate_database_score_simple(modern_metrics.get('database', {}))
        quality_score = calculate_quality_score_simple(modern_metrics.get('quality', {}))
        nfr_score = calculate_nfr_score_simple(modern_metrics.get('nfr', {}))
        integration_score = 95  # Placeholder

        overall_score = (
            frontend_score * 0.25 +
            backend_score * 0.25 +
            database_score * 0.10 +
            quality_score * 0.20 +
            nfr_score * 0.15 +
            integration_score * 0.05
        )

        print(f"{overall_score:.1f}")
        return 0

    except Exception as e:
        print("0", file=sys.stderr)
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def calculate_frontend_score_simple(frontend: dict) -> float:
    """Calculate frontend score"""
    if not frontend:
        return 0

    lighthouse = frontend.get('lighthouse', {})
    performance = lighthouse.get('performance', 0)
    accessibility = lighthouse.get('accessibility', 0)
    feature_parity = frontend.get('feature_parity', 0)

    return (feature_parity * 0.6) + (performance * 0.2) + (accessibility * 0.2)

def calculate_backend_score_simple(backend: dict) -> float:
    """Calculate backend score"""
    if not backend:
        return 0

    api_parity = backend.get('api_parity', 0) * 100
    response_time = backend.get('avg_response_time_ms', 200)
    performance = max(0, 100 - (response_time - 200) / 10) if response_time > 200 else 100
    error_rate = backend.get('error_rate', 0)
    error_handling = max(0, 100 - error_rate * 1000)

    return (api_parity * 0.5) + (performance * 0.3) + (error_handling * 0.2)

def calculate_database_score_simple(database: dict) -> float:
    """Calculate database score"""
    if not database:
        return 0

    schema_parity = database.get('schema_parity', 0) * 100
    query_time = database.get('avg_query_time_ms', 100)
    performance = max(0, 100 - (query_time - 100) / 5) if query_time > 100 else 100
    integrity = database.get('integrity_score', 100)

    return (schema_parity * 0.4) + (performance * 0.4) + (integrity * 0.2)

def calculate_quality_score_simple(quality: dict) -> float:
    """Calculate quality score"""
    if not quality:
        return 0

    sonar = quality.get('sonarqube', {})
    coverage = quality.get('coverage', {}).get('total', 0)
    security_issues = quality.get('security_issues', 0)

    # Simple sonar score
    rating_scores = {'A': 100, 'B': 80, 'C': 60, 'D': 40, 'E': 20}
    reliability = rating_scores.get(sonar.get('reliability_rating', 'C'), 60)
    security = rating_scores.get(sonar.get('security_rating', 'C'), 60)
    sonar_score = (reliability + security) / 2

    security_score = max(0, 100 - security_issues * 10)

    return (sonar_score * 0.5) + (coverage * 0.3) + (security_score * 0.2)

def calculate_nfr_score_simple(nfr: dict) -> float:
    """Calculate NFR score"""
    if not nfr:
        return 0

    p95 = nfr.get('response_time_p95_ms', 500)
    performance = max(0, 100 - (p95 - 500) / 10) if p95 > 500 else 100
    security_score = nfr.get('security_posture', 80)
    observability = nfr.get('observability_score', 70)

    return (performance * 0.4) + (security_score * 0.3) + (observability * 0.3)

if __name__ == '__main__':
    sys.exit(main())
