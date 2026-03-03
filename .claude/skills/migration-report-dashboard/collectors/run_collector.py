"""
Collector Runner CLI
Runs individual collectors and saves results
"""

import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import load_config
from collectors.lighthouse_collector import LighthouseCollector
from collectors.api_collector import APICollector
from collectors.sonar_collector import SonarQubeCollector
from collectors.coverage_collector import CoverageCollector
from collectors.database_collector import DatabaseCollector

COLLECTORS = {
    'lighthouse': LighthouseCollector,
    'api': APICollector,
    'sonar': SonarQubeCollector,
    'coverage': CoverageCollector,
    'database': DatabaseCollector,
}

def main():
    """
    Main entry point for collector runner

    Usage:
        python -m collectors.run_collector <collector_name> <app_type>

    Example:
        python -m collectors.run_collector lighthouse modern
        python -m collectors.run_collector api legacy
    """
    if len(sys.argv) < 3:
        print("Usage: python -m collectors.run_collector <collector_name> <app_type>")
        print(f"Available collectors: {', '.join(COLLECTORS.keys())}")
        print("App types: legacy, modern")
        sys.exit(1)

    collector_name = sys.argv[1]
    app_type = sys.argv[2]

    if collector_name not in COLLECTORS:
        print(f"Unknown collector: {collector_name}")
        print(f"Available collectors: {', '.join(COLLECTORS.keys())}")
        sys.exit(1)

    if app_type not in ['legacy', 'modern']:
        print(f"Invalid app type: {app_type}")
        print("App types: legacy, modern")
        sys.exit(1)

    # Load configuration
    try:
        config = load_config()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Create collector
    collector_class = COLLECTORS[collector_name]
    collector = collector_class(config, app_type)

    print(f"Running {collector_name} collector for {app_type} app...")

    # Run collection
    metrics = collector.safe_collect()

    # Check for errors
    if 'error' in metrics:
        print(f"❌ Collection failed: {metrics['error']}")
        sys.exit(1)

    # Save results
    output_dir = Path(__file__).parent.parent / "data" / app_type
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / f"{collector_name}.json"

    with open(output_file, 'w') as f:
        json.dump(metrics, f, indent=2)

    print(f"✅ Saved results to {output_file}")

if __name__ == '__main__':
    main()
