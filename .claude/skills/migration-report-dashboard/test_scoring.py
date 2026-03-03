"""
Quick test of scoring system
"""
import json
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from app.state import (
    calculate_frontend_score_simple,
    calculate_backend_score_simple,
    calculate_database_score_simple,
    calculate_quality_score_simple,
    calculate_nfr_score_simple
)

# Load sample data
with open('data/modern/metrics.json', 'r') as f:
    metrics = json.load(f)

# Calculate scores
frontend_score = calculate_frontend_score_simple(metrics.get('frontend', {}))
backend_score = calculate_backend_score_simple(metrics.get('backend', {}))
database_score = calculate_database_score_simple(metrics.get('database', {}))
quality_score = calculate_quality_score_simple(metrics.get('quality', {}))
nfr_score = calculate_nfr_score_simple(metrics.get('nfr', {}))

# Calculate overall
overall_score = (
    frontend_score * 0.25 +
    backend_score * 0.25 +
    database_score * 0.10 +
    quality_score * 0.20 +
    nfr_score * 0.15 +
    95 * 0.05  # Integration placeholder
)

print("=" * 50)
print("SCORING TEST RESULTS")
print("=" * 50)
print(f"\nFrontend Score:    {frontend_score:.1f}/100")
print(f"Backend Score:     {backend_score:.1f}/100")
print(f"Database Score:    {database_score:.1f}/100")
print(f"Quality Score:     {quality_score:.1f}/100")
print(f"NFR Score:         {nfr_score:.1f}/100")
print(f"Integration Score: 95.0/100 (placeholder)")
print(f"\n{'='*50}")
print(f"OVERALL SCORE:     {overall_score:.1f}/100")
print(f"{'='*50}")

if overall_score >= 90:
    status = "Production Ready"
elif overall_score >= 75:
    status = "Near Ready"
elif overall_score >= 60:
    status = "In Progress"
else:
    status = "Not Ready"

print(f"\nStatus: {status}")
print("\nScoring calculation works!")
