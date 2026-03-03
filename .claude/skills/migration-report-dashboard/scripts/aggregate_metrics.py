"""
Aggregate Metrics Script
Combines individual collector outputs into single metrics.json files
"""

import json
from pathlib import Path
from datetime import datetime

def aggregate_app_metrics(app_type: str):
    """
    Aggregate all metrics for an app (legacy or modern)

    Args:
        app_type: "legacy" or "modern"
    """
    data_dir = Path(__file__).parent.parent / "data" / app_type

    if not data_dir.exists():
        print(f"⚠️  Data directory not found: {data_dir}")
        return None

    aggregated = {
        'timestamp': datetime.now().isoformat(),
        'app_type': app_type,
        'frontend': {},
        'backend': {},
        'database': {},
        'quality': {},
        'nfr': {},
        'integration': {}
    }

    # Frontend metrics (Lighthouse)
    lighthouse_file = data_dir / "lighthouse.json"
    if lighthouse_file.exists():
        with open(lighthouse_file, 'r') as f:
            lighthouse_data = json.load(f)
            aggregated['frontend'] = {
                'lighthouse': {
                    'performance': lighthouse_data.get('performance', 0),
                    'accessibility': lighthouse_data.get('accessibility', 0),
                    'best_practices': lighthouse_data.get('best_practices', 0),
                    'seo': lighthouse_data.get('seo', 0),
                },
                'first_contentful_paint_ms': lighthouse_data.get('first_contentful_paint_ms', 0),
                'largest_contentful_paint_ms': lighthouse_data.get('largest_contentful_paint_ms', 0),
                'time_to_interactive_ms': lighthouse_data.get('time_to_interactive_ms', 0),
                'cumulative_layout_shift': lighthouse_data.get('cumulative_layout_shift', 0),
                'accessibility_issues': lighthouse_data.get('accessibility_issues', []),
                'feature_parity': 95,  # Placeholder - should come from browser-agent
            }

    # Backend metrics (API)
    api_file = data_dir / "api.json"
    if api_file.exists():
        with open(api_file, 'r') as f:
            api_data = json.load(f)
            aggregated['backend'] = {
                'total_endpoints': api_data.get('total_endpoints', 0),
                'accessible_endpoints': api_data.get('accessible_endpoints', 0),
                'api_parity': api_data.get('api_parity', 0),
                'avg_response_time_ms': api_data.get('avg_response_time_ms', 0),
                'p95_response_time_ms': api_data.get('p95_response_time_ms', 0),
                'error_rate': api_data.get('error_rate', 0),
                'endpoints': api_data.get('endpoints', [])
            }

    # Database metrics
    database_file = data_dir / "database.json"
    if database_file.exists():
        with open(database_file, 'r') as f:
            db_data = json.load(f)
            aggregated['database'] = {
                'total_tables': db_data.get('total_tables', 0),
                'total_columns': db_data.get('total_columns', 0),
                'avg_query_time_ms': db_data.get('avg_query_time_ms', 0),
                'schema_parity': 0.98,  # Placeholder - needs comparison logic
                'integrity_score': 100,  # Placeholder
            }

    # Quality metrics (SonarQube + Coverage)
    sonar_file = data_dir / "sonar.json"
    coverage_file = data_dir / "coverage.json"

    quality = {}
    if sonar_file.exists():
        with open(sonar_file, 'r') as f:
            sonar_data = json.load(f)
            quality['sonarqube'] = sonar_data

    if coverage_file.exists():
        with open(coverage_file, 'r') as f:
            coverage_data = json.load(f)
            quality['coverage'] = coverage_data

    quality['security_issues'] = quality.get('sonarqube', {}).get('vulnerabilities', 0)
    aggregated['quality'] = quality

    # NFR metrics (placeholder - would come from load tests)
    aggregated['nfr'] = {
        'response_time_p95_ms': aggregated['backend'].get('p95_response_time_ms', 0),
        'security_posture': 80,  # Placeholder
        'observability_score': 70,  # Placeholder
    }

    # Integration metrics (placeholder)
    aggregated['integration'] = {
        'integration_parity': 1.0,  # Placeholder
    }

    return aggregated

def main():
    """Main entry point"""
    print("🔄 Aggregating metrics...")

    # Aggregate legacy metrics
    print("\n📊 Aggregating legacy metrics...")
    legacy_metrics = aggregate_app_metrics('legacy')

    if legacy_metrics:
        output_file = Path(__file__).parent.parent / "data" / "legacy" / "metrics.json"
        with open(output_file, 'w') as f:
            json.dump(legacy_metrics, f, indent=2)
        print(f"✅ Saved: {output_file}")
    else:
        print("⚠️  No legacy metrics to aggregate")

    # Aggregate modern metrics
    print("\n📊 Aggregating modern metrics...")
    modern_metrics = aggregate_app_metrics('modern')

    if modern_metrics:
        output_file = Path(__file__).parent.parent / "data" / "modern" / "metrics.json"
        with open(output_file, 'w') as f:
            json.dump(modern_metrics, f, indent=2)
        print(f"✅ Saved: {output_file}")
    else:
        print("⚠️  No modern metrics to aggregate")

    if legacy_metrics and modern_metrics:
        print("\n✅ Aggregation complete!")
        print("\nNext steps:")
        print("  1. Launch dashboard: streamlit run app/main.py")
        print("  2. Open browser: http://localhost:8501")
    else:
        print("\n⚠️  Incomplete data. Run collectors first.")

if __name__ == '__main__':
    main()
