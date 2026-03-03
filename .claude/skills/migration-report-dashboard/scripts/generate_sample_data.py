"""
Generate Sample Data
Creates realistic sample metrics for demo and testing purposes
"""

import json
import random
from datetime import datetime
from pathlib import Path

def generate_sample_metrics(app_type='modern', quality_level='good'):
    """
    Generate sample metrics

    Args:
        app_type: 'legacy' or 'modern'
        quality_level: 'excellent', 'good', 'fair', 'poor'

    Returns:
        Dictionary of sample metrics
    """
    # Quality multipliers
    multipliers = {
        'excellent': {'score': 1.0, 'issues': 0.2},
        'good': {'score': 0.85, 'issues': 0.5},
        'fair': {'score': 0.70, 'issues': 1.0},
        'poor': {'score': 0.50, 'issues': 2.0}
    }

    mult = multipliers.get(quality_level, multipliers['good'])

    # Frontend metrics (Lighthouse)
    lighthouse = {
        'performance': int(90 * mult['score']),
        'accessibility': int(95 * mult['score']),
        'best_practices': int(92 * mult['score']),
        'seo': int(88 * mult['score']),
    }

    frontend = {
        'lighthouse': lighthouse,
        'first_contentful_paint_ms': int(1200 / mult['score']),
        'largest_contentful_paint_ms': int(2500 / mult['score']),
        'time_to_interactive_ms': int(3200 / mult['score']),
        'cumulative_layout_shift': round(0.1 / mult['score'], 3),
        'bundle_size_kb': int(250 if app_type == 'legacy' else 180),
        'accessibility_issues': [
            {
                'audit': 'color-contrast',
                'title': 'Background and foreground colors do not have sufficient contrast',
                'description': '3 elements found',
                'severity': 'serious'
            },
            {
                'audit': 'image-alt',
                'title': 'Image elements do not have alt attributes',
                'description': '2 elements found',
                'severity': 'critical'
            }
        ] if quality_level in ['fair', 'poor'] else [],
        'feature_parity': int(95 * mult['score']),
        'feature_parity_details': [
            {'screen': 'Home', 'feature': 'Dashboard', 'legacy_present': True, 'modern_present': True, 'notes': ''},
            {'screen': 'Products', 'feature': 'Product List', 'legacy_present': True, 'modern_present': True, 'notes': ''},
            {'screen': 'Products', 'feature': 'Product Details', 'legacy_present': True, 'modern_present': True, 'notes': ''},
            {'screen': 'Products', 'feature': 'Export to Excel', 'legacy_present': True, 'modern_present': quality_level != 'poor', 'notes': 'Missing in modern' if quality_level == 'poor' else ''},
            {'screen': 'Orders', 'feature': 'Order List', 'legacy_present': True, 'modern_present': True, 'notes': ''},
            {'screen': 'Orders', 'feature': 'Order Details', 'legacy_present': True, 'modern_present': True, 'notes': ''},
        ]
    }

    # Backend metrics (API)
    endpoints = [
        {'path': '/api/products', 'method': 'GET', 'summary': 'List products', 'avg_response_time_ms': round(random.uniform(50, 150) / mult['score'], 2), 'median_response_time_ms': 80, 'min_response_time_ms': 45, 'max_response_time_ms': 200, 'success_rate': 1.0 if quality_level != 'poor' else 0.67, 'status_codes': [200, 200, 200], 'errors': [] if quality_level != 'poor' else ['timeout'], 'accessible': quality_level != 'poor'},
        {'path': '/api/products/{id}', 'method': 'GET', 'summary': 'Get product', 'avg_response_time_ms': round(random.uniform(40, 120) / mult['score'], 2), 'median_response_time_ms': 70, 'min_response_time_ms': 35, 'max_response_time_ms': 180, 'success_rate': 1.0, 'status_codes': [200, 200, 200], 'errors': [], 'accessible': True},
        {'path': '/api/orders', 'method': 'GET', 'summary': 'List orders', 'avg_response_time_ms': round(random.uniform(60, 180) / mult['score'], 2), 'median_response_time_ms': 95, 'min_response_time_ms': 50, 'max_response_time_ms': 250, 'success_rate': 1.0, 'status_codes': [200, 200, 200], 'errors': [], 'accessible': True},
        {'path': '/api/orders/{id}', 'method': 'GET', 'summary': 'Get order', 'avg_response_time_ms': round(random.uniform(45, 130) / mult['score'], 2), 'median_response_time_ms': 75, 'min_response_time_ms': 40, 'max_response_time_ms': 190, 'success_rate': 1.0, 'status_codes': [200, 200, 200], 'errors': [], 'accessible': True},
        {'path': '/api/customers', 'method': 'GET', 'summary': 'List customers', 'avg_response_time_ms': round(random.uniform(55, 165) / mult['score'], 2), 'median_response_time_ms': 85, 'min_response_time_ms': 48, 'max_response_time_ms': 220, 'success_rate': 1.0, 'status_codes': [200, 200, 200], 'errors': [], 'accessible': True},
    ]

    response_times = [e['avg_response_time_ms'] for e in endpoints if e['avg_response_time_ms']]
    avg_response = sum(response_times) / len(response_times) if response_times else 0

    backend = {
        'total_endpoints': len(endpoints),
        'accessible_endpoints': len([e for e in endpoints if e['accessible']]),
        'api_parity': mult['score'],
        'avg_response_time_ms': round(avg_response, 2),
        'median_response_time_ms': round(sorted(response_times)[len(response_times)//2], 2) if response_times else 0,
        'p95_response_time_ms': round(sorted(response_times)[int(len(response_times)*0.95)], 2) if response_times else 0,
        'p99_response_time_ms': round(sorted(response_times)[int(len(response_times)*0.99)], 2) if response_times else 0,
        'error_rate': round((1 - mult['score']) * 0.02, 4),
        'fastest_endpoint': '/api/products/{id}',
        'slowest_endpoint': '/api/orders',
        'endpoints': endpoints
    }

    # Database metrics
    database = {
        'total_tables': int(25 if app_type == 'legacy' else 22),
        'total_columns': int(180 if app_type == 'legacy' else 165),
        'total_indexes': 45,
        'total_foreign_keys': 28,
        'avg_query_time_ms': round(85 / mult['score'], 2),
        'connection_test': True,
        'schema_parity': mult['score'],
        'integrity_score': int(100 * mult['score']),
        'tables': [
            {'name': 'Products', 'columns': 12, 'indexes': 3, 'foreign_keys': 1, 'column_names': ['Id', 'Name', 'Price', 'CategoryId']},
            {'name': 'Orders', 'columns': 10, 'indexes': 4, 'foreign_keys': 2, 'column_names': ['Id', 'CustomerId', 'OrderDate', 'Total']},
            {'name': 'Customers', 'columns': 15, 'indexes': 2, 'foreign_keys': 0, 'column_names': ['Id', 'Name', 'Email', 'Phone']},
        ]
    }

    # Quality metrics (SonarQube + Coverage)
    sonarqube = {
        'reliability_rating': 'A' if quality_level == 'excellent' else 'B' if quality_level == 'good' else 'C',
        'security_rating': 'A' if quality_level in ['excellent', 'good'] else 'B' if quality_level == 'fair' else 'C',
        'maintainability_rating': 'A' if quality_level == 'excellent' else 'B' if quality_level in ['good', 'fair'] else 'C',
        'coverage': round(82 * mult['score'], 1),
        'duplicated_lines_density': round(3.2 / mult['score'], 1),
        'bugs': int(5 * mult['issues']),
        'vulnerabilities': int(2 * mult['issues']),
        'code_smells': int(45 * mult['issues']),
        'technical_debt_minutes': int(1200 * mult['issues']),
        'lines_of_code': 15000,
        'complexity': int(850 * mult['issues']),
        'cognitive_complexity': int(420 * mult['issues']),
        'issues_by_severity': {
            'blocker': 0,
            'critical': int(2 * mult['issues']),
            'major': int(8 * mult['issues']),
            'minor': int(15 * mult['issues']),
            'info': int(20 * mult['issues'])
        }
    }

    coverage = {
        'total': round(82 * mult['score'], 1),
        'line': round(85 * mult['score'], 1),
        'branch': round(78 * mult['score'], 1),
        'function': round(83 * mult['score'], 1),
        'lines_covered': int(12750 * mult['score']),
        'lines_total': 15000,
        'branches_covered': int(3900 * mult['score']),
        'branches_total': 5000,
        'functions_covered': int(830 * mult['score']),
        'functions_total': 1000
    }

    quality = {
        'sonarqube': sonarqube,
        'coverage': coverage,
        'security_issues': int(2 * mult['issues'])
    }

    # NFR metrics
    nfr = {
        'response_time_p95_ms': round(450 / mult['score'], 2),
        'security_posture': int(85 * mult['score']),
        'observability_score': int(75 * mult['score'])
    }

    # Integration metrics
    integration = {
        'integration_parity': mult['score']
    }

    # Combine all metrics
    metrics = {
        'timestamp': datetime.now().isoformat(),
        'app_type': app_type,
        'quality_level': quality_level,
        'frontend': frontend,
        'backend': backend,
        'database': database,
        'quality': quality,
        'nfr': nfr,
        'integration': integration
    }

    return metrics

def main():
    """Generate sample data for both legacy and modern apps"""
    print("Generating sample data...")

    # Create data directories
    data_dir = Path(__file__).parent.parent / "data"
    (data_dir / "legacy").mkdir(parents=True, exist_ok=True)
    (data_dir / "modern").mkdir(parents=True, exist_ok=True)

    # Generate legacy metrics (fair quality)
    print("\nGenerating legacy metrics...")
    legacy_metrics = generate_sample_metrics('legacy', 'fair')
    legacy_file = data_dir / "legacy" / "metrics.json"
    with open(legacy_file, 'w') as f:
        json.dump(legacy_metrics, f, indent=2)
    print(f"Saved: {legacy_file}")

    # Generate modern metrics (good quality)
    print("\nGenerating modern metrics...")
    modern_metrics = generate_sample_metrics('modern', 'good')
    modern_file = data_dir / "modern" / "metrics.json"
    with open(modern_file, 'w') as f:
        json.dump(modern_metrics, f, indent=2)
    print(f"Saved: {modern_file}")

    print("\nSample data generation complete!")
    print("\nNext steps:")
    print("  1. Launch dashboard: streamlit run app/main.py")
    print("  2. Open browser: http://localhost:8501")
    print("  3. Explore the demo data")

if __name__ == '__main__':
    main()
