#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Custom Browser Agent - Verification with explicit URL mapping
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from verify import ParityVerifier, sync_playwright
from pathlib import Path

def main():
    """Run custom verification with explicit URL mapping"""

    # Configuration
    legacy_base = "http://localhost:50586"
    modern_base = "http://localhost:5173"
    output_dir = Path("legacy-golden/parity-results/catalog-corrected")

    # Workflow to URL mapping
    workflows = {
        'catalog-list': {
            'legacy': '/',  # Root URL shows catalog list
            'modern': '/catalog'  # Modern app has /catalog route
        },
        'catalog-crud-create': {
            'legacy': '/Catalog/Create',
            'modern': '/catalog/create'
        },
        'catalog-crud-edit': {
            'legacy': '/Catalog/Edit/1',
            'modern': '/catalog/edit/1'
        }
    }

    print("🔍 Custom Browser Agent - Verification Mode")
    print("=" * 60)
    print(f"Legacy:  {legacy_base}")
    print(f"Modern:  {modern_base}")
    print(f"Output:  {output_dir}")
    print("=" * 60)
    print()

    # Create output structure
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / 'screenshots' / 'legacy').mkdir(parents=True, exist_ok=True)
    (output_dir / 'screenshots' / 'modern').mkdir(parents=True, exist_ok=True)
    (output_dir / 'screenshots' / 'diff').mkdir(parents=True, exist_ok=True)

    # Initialize verifier
    verifier = ParityVerifier(
        legacy_url=legacy_base,
        modern_url=modern_base,
        output_dir=str(output_dir),
        workflows=[],
        compare_data=True,
        screenshot_diff=True
    )

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        try:
            # Create contexts
            legacy_context = browser.new_context(viewport={'width': 1920, 'height': 1080})
            modern_context = browser.new_context(viewport={'width': 1920, 'height': 1080})

            legacy_page = legacy_context.new_page()
            modern_page = modern_context.new_page()

            # Verify each workflow with custom paths
            for workflow_name, paths in workflows.items():
                print(f"\n📋 Verifying workflow: {workflow_name}")

                workflow_result = {
                    'name': workflow_name,
                    'pages': [],
                    'passed': True,
                    'issues': []
                }

                # Custom verify_page_pair call with different paths
                legacy_full_url = f"{legacy_base}{paths['legacy']}"
                modern_full_url = f"{modern_base}{paths['modern']}"

                print(f"  Legacy: {legacy_full_url}")
                print(f"  Modern: {modern_full_url}")

                # Load pages
                try:
                    legacy_page.goto(legacy_full_url, wait_until='networkidle', timeout=30000)
                    legacy_page.wait_for_timeout(2000)

                    modern_page.goto(modern_full_url, wait_until='networkidle', timeout=30000)
                    modern_page.wait_for_timeout(2000)

                    # Capture screenshots
                    legacy_ss = verifier.capture_screenshot(legacy_page, 'legacy', workflow_name)
                    modern_ss = verifier.capture_screenshot(modern_page, 'modern', workflow_name)

                    # Compare screenshots
                    diff_result = verifier.compare_screenshots(legacy_ss, modern_ss, workflow_name)

                    # Discover elements
                    print("    🔍 Discovering elements...")
                    legacy_elements = verifier.discover_elements(legacy_page)
                    modern_elements = verifier.discover_elements(modern_page)

                    # Compare elements
                    element_comparison = verifier.compare_elements(legacy_elements, modern_elements)

                    # Compare data
                    print("    📊 Comparing data...")
                    legacy_data = verifier.extract_grid_data(legacy_page)
                    modern_data = verifier.extract_grid_data(modern_page)
                    data_comparison = verifier.compare_data(legacy_data, modern_data)

                    page_result = {
                        'name': workflow_name,
                        'legacy_url': legacy_full_url,
                        'modern_url': modern_full_url,
                        'elements': {
                            'legacy': legacy_elements,
                            'modern': modern_elements,
                            'comparison': element_comparison
                        },
                        'data': {
                            'legacy': legacy_data,
                            'modern': modern_data,
                            'comparison': data_comparison
                        },
                        'visual': diff_result,
                        'issues': []
                    }

                    # Add issues
                    if diff_result['difference_percentage'] > 20:
                        page_result['issues'].append({
                            'type': 'visual',
                            'severity': 'warning',
                            'message': f"Visual difference: {diff_result['difference_percentage']:.1f}%"
                        })

                    if element_comparison.get('missing_in_modern'):
                        for elem in element_comparison['missing_in_modern'][:5]:  # Limit to 5
                            page_result['issues'].append({
                                'type': 'element',
                                'severity': 'error',
                                'message': f"Missing element: {elem['type']} - {elem['text'][:50]}"
                            })

                    workflow_result['pages'].append(page_result)
                    workflow_result['passed'] = len(page_result['issues']) == 0
                    workflow_result['issues'] = page_result['issues']

                    verifier.results['workflows'].append(workflow_result)

                    print(f"    ✅ Complete - {len(page_result['issues'])} issues found")

                except Exception as e:
                    print(f"    ❌ Error: {e}")
                    workflow_result['passed'] = False
                    workflow_result['issues'].append({
                        'type': 'error',
                        'severity': 'critical',
                        'message': str(e)
                    })
                    verifier.results['workflows'].append(workflow_result)

            # Calculate parity score
            verifier.calculate_parity_score()

            # Generate reports
            verifier.save_results()
            verifier.generate_feature_matrix()
            verifier.generate_html_report()

            print("\n" + "=" * 60)
            print(f"✅ Verification complete!")
            print(f"📊 Parity Score: {verifier.results['parity_score']:.1f}%")
            verifier.print_summary()
            print("=" * 60)

        finally:
            browser.close()

if __name__ == '__main__':
    main()
