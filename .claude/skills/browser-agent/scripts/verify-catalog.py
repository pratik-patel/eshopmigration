#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Browser Agent - Catalog Verification
Compares legacy and modern catalog implementations
"""

import sys
import os
import json
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from verify import ParityVerifier, sync_playwright

def main():
    """Run catalog-specific verification"""

    # Configuration from arguments
    legacy_base = "http://localhost:50586"
    modern_base = "http://localhost:5173"
    output_dir = Path("C:/Users/pratikp6/codebase/eshopmigration/legacy-golden/parity-results/catalog")

    # Workflow to URL mapping for catalog
    workflows = {
        'catalog-list': {
            'legacy': '/',  # Root URL shows catalog list
            'modern': '/catalog',  # Modern app has /catalog route
            'description': 'Product catalog list view'
        },
        'catalog-crud': {
            'legacy': '/Catalog/Create',
            'modern': '/catalog/create',
            'description': 'Create new product form'
        }
    }

    print("=" * 80)
    print("🔍 BROWSER AGENT - CATALOG PARITY VERIFICATION")
    print("=" * 80)
    print(f"Legacy Application:  {legacy_base}")
    print(f"Modern Application:  {modern_base}")
    print(f"Output Directory:    {output_dir}")
    print(f"Workflows:           {', '.join(workflows.keys())}")
    print("=" * 80)
    print()

    # Create output structure
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / 'screenshots' / 'legacy').mkdir(parents=True, exist_ok=True)
    (output_dir / 'screenshots' / 'modern').mkdir(parents=True, exist_ok=True)
    (output_dir / 'screenshots' / 'diff').mkdir(parents=True, exist_ok=True)

    # Results collection
    results = {
        'timestamp': datetime.now().isoformat(),
        'legacy_url': legacy_base,
        'modern_url': modern_base,
        'workflows': {},
        'overall_score': 0,
        'summary': {}
    }

    with sync_playwright() as p:
        print("🌐 Launching browser...")
        browser = p.chromium.launch(headless=False, slow_mo=500)

        try:
            # Create contexts
            legacy_context = browser.new_context(viewport={'width': 1920, 'height': 1080})
            modern_context = browser.new_context(viewport={'width': 1920, 'height': 1080})

            legacy_page = legacy_context.new_page()
            modern_page = modern_context.new_page()

            total_checks = 0
            passed_checks = 0

            # Verify each workflow
            for workflow_name, config in workflows.items():
                print(f"\n{'='*60}")
                print(f"📋 Workflow: {workflow_name}")
                print(f"   {config['description']}")
                print(f"{'='*60}")

                workflow_result = {
                    'name': workflow_name,
                    'description': config['description'],
                    'legacy_url': config['legacy'],
                    'modern_url': config['modern'],
                    'checks': [],
                    'passed': True,
                    'issues': [],
                    'screenshots': {}
                }

                # Full URLs
                legacy_full_url = f"{legacy_base}{config['legacy']}"
                modern_full_url = f"{modern_base}{config['modern']}"

                print(f"\n🔗 URLs:")
                print(f"   Legacy: {legacy_full_url}")
                print(f"   Modern: {modern_full_url}")

                # Load pages
                print(f"\n⏳ Loading pages...")
                try:
                    print(f"   Loading legacy page...")
                    legacy_page.goto(legacy_full_url, wait_until='networkidle', timeout=30000)
                    legacy_page.wait_for_timeout(2000)

                    print(f"   Loading modern page...")
                    modern_page.goto(modern_full_url, wait_until='networkidle', timeout=30000)
                    modern_page.wait_for_timeout(2000)

                    print(f"   ✓ Pages loaded successfully")

                except Exception as e:
                    error_msg = f"Failed to load pages: {str(e)}"
                    print(f"   ✗ {error_msg}")
                    workflow_result['issues'].append(error_msg)
                    workflow_result['passed'] = False
                    results['workflows'][workflow_name] = workflow_result
                    continue

                # Capture screenshots
                print(f"\n📸 Capturing screenshots...")
                legacy_screenshot_path = output_dir / 'screenshots' / 'legacy' / f"{workflow_name}.png"
                modern_screenshot_path = output_dir / 'screenshots' / 'modern' / f"{workflow_name}.png"

                legacy_page.screenshot(path=str(legacy_screenshot_path), full_page=True)
                modern_page.screenshot(path=str(modern_screenshot_path), full_page=True)

                workflow_result['screenshots'] = {
                    'legacy': str(legacy_screenshot_path.relative_to(output_dir)),
                    'modern': str(modern_screenshot_path.relative_to(output_dir))
                }
                print(f"   ✓ Screenshots saved")

                # Check 1: Page title/heading
                print(f"\n🔍 Check 1: Page Title/Heading")
                try:
                    legacy_title = legacy_page.title()
                    modern_title = modern_page.title()

                    check_result = {
                        'check': 'page_title',
                        'passed': bool(modern_title),
                        'legacy_value': legacy_title,
                        'modern_value': modern_title
                    }
                    workflow_result['checks'].append(check_result)
                    total_checks += 1

                    print(f"   Legacy title: '{legacy_title}'")
                    print(f"   Modern title: '{modern_title}'")

                    if check_result['passed']:
                        passed_checks += 1
                        print(f"   ✓ Modern app has title")
                    else:
                        print(f"   ✗ Modern app missing title")
                        workflow_result['issues'].append('Missing page title')

                except Exception as e:
                    print(f"   ⚠ Could not check titles: {e}")

                # Check 2: Main content presence
                print(f"\n🔍 Check 2: Main Content Presence")
                try:
                    # Look for common content containers
                    legacy_has_content = legacy_page.locator('main, .container, .content, body').count() > 0
                    modern_has_content = modern_page.locator('main, .container, .content, [role="main"]').count() > 0

                    check_result = {
                        'check': 'main_content',
                        'passed': modern_has_content,
                        'legacy_value': legacy_has_content,
                        'modern_value': modern_has_content
                    }
                    workflow_result['checks'].append(check_result)
                    total_checks += 1

                    if check_result['passed']:
                        passed_checks += 1
                        print(f"   ✓ Modern app has main content container")
                    else:
                        print(f"   ✗ Modern app missing main content")
                        workflow_result['issues'].append('Missing main content container')

                except Exception as e:
                    print(f"   ⚠ Could not check content: {e}")

                # Check 3: Interactive elements (buttons, links, forms)
                print(f"\n🔍 Check 3: Interactive Elements")
                try:
                    legacy_buttons = legacy_page.locator('button, input[type="submit"], a.btn').count()
                    modern_buttons = modern_page.locator('button, input[type="submit"], a.btn, [role="button"]').count()

                    legacy_links = legacy_page.locator('a[href]').count()
                    modern_links = modern_page.locator('a[href]').count()

                    legacy_inputs = legacy_page.locator('input, textarea, select').count()
                    modern_inputs = modern_page.locator('input, textarea, select').count()

                    print(f"   Legacy: {legacy_buttons} buttons, {legacy_links} links, {legacy_inputs} inputs")
                    print(f"   Modern: {modern_buttons} buttons, {modern_links} links, {modern_inputs} inputs")

                    has_interactive = modern_buttons > 0 or modern_links > 0 or modern_inputs > 0

                    check_result = {
                        'check': 'interactive_elements',
                        'passed': has_interactive,
                        'legacy_value': {
                            'buttons': legacy_buttons,
                            'links': legacy_links,
                            'inputs': legacy_inputs
                        },
                        'modern_value': {
                            'buttons': modern_buttons,
                            'links': modern_links,
                            'inputs': modern_inputs
                        }
                    }
                    workflow_result['checks'].append(check_result)
                    total_checks += 1

                    if check_result['passed']:
                        passed_checks += 1
                        print(f"   ✓ Modern app has interactive elements")
                    else:
                        print(f"   ✗ Modern app missing interactive elements")
                        workflow_result['issues'].append('Missing interactive elements')

                except Exception as e:
                    print(f"   ⚠ Could not check interactive elements: {e}")

                # Check 4: Tables/Grids (for list view)
                if 'list' in workflow_name:
                    print(f"\n🔍 Check 4: Data Table/Grid")
                    try:
                        legacy_tables = legacy_page.locator('table, .grid, .datagrid').count()
                        modern_tables = modern_page.locator('table, .grid, [role="grid"], [role="table"]').count()

                        print(f"   Legacy tables: {legacy_tables}")
                        print(f"   Modern tables: {modern_tables}")

                        check_result = {
                            'check': 'data_table',
                            'passed': modern_tables > 0,
                            'legacy_value': legacy_tables,
                            'modern_value': modern_tables
                        }
                        workflow_result['checks'].append(check_result)
                        total_checks += 1

                        if check_result['passed']:
                            passed_checks += 1
                            print(f"   ✓ Modern app has data table/grid")
                        else:
                            print(f"   ✗ Modern app missing data table")
                            workflow_result['issues'].append('Missing data table/grid')

                    except Exception as e:
                        print(f"   ⚠ Could not check tables: {e}")

                # Check 5: Forms (for CRUD views)
                if 'crud' in workflow_name:
                    print(f"\n🔍 Check 5: Form Presence")
                    try:
                        legacy_forms = legacy_page.locator('form').count()
                        modern_forms = modern_page.locator('form').count()

                        print(f"   Legacy forms: {legacy_forms}")
                        print(f"   Modern forms: {modern_forms}")

                        check_result = {
                            'check': 'form_presence',
                            'passed': modern_forms > 0,
                            'legacy_value': legacy_forms,
                            'modern_value': modern_forms
                        }
                        workflow_result['checks'].append(check_result)
                        total_checks += 1

                        if check_result['passed']:
                            passed_checks += 1
                            print(f"   ✓ Modern app has form")
                        else:
                            print(f"   ✗ Modern app missing form")
                            workflow_result['issues'].append('Missing form')

                    except Exception as e:
                        print(f"   ⚠ Could not check forms: {e}")

                # Determine workflow pass/fail
                workflow_passed = len(workflow_result['issues']) == 0
                workflow_result['passed'] = workflow_passed

                print(f"\n{'='*60}")
                if workflow_passed:
                    print(f"✅ Workflow '{workflow_name}' PASSED")
                else:
                    print(f"❌ Workflow '{workflow_name}' FAILED")
                    print(f"   Issues: {', '.join(workflow_result['issues'])}")
                print(f"{'='*60}")

                results['workflows'][workflow_name] = workflow_result

            # Close browser
            legacy_context.close()
            modern_context.close()

        finally:
            browser.close()

    # Calculate overall score
    if total_checks > 0:
        results['overall_score'] = round((passed_checks / total_checks) * 100, 2)
    else:
        results['overall_score'] = 0

    results['summary'] = {
        'total_workflows': len(workflows),
        'total_checks': total_checks,
        'passed_checks': passed_checks,
        'failed_checks': total_checks - passed_checks,
        'parity_score': results['overall_score']
    }

    # Save results
    results_path = output_dir / 'verification-results.json'
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)

    # Generate summary report
    generate_summary_report(results, output_dir)

    # Print final summary
    print(f"\n{'='*80}")
    print("📊 VERIFICATION COMPLETE")
    print(f"{'='*80}")
    print(f"Total Workflows:     {results['summary']['total_workflows']}")
    print(f"Total Checks:        {results['summary']['total_checks']}")
    print(f"Passed Checks:       {results['summary']['passed_checks']}")
    print(f"Failed Checks:       {results['summary']['failed_checks']}")
    print(f"Parity Score:        {results['summary']['parity_score']}%")
    print(f"{'='*80}")
    print(f"\n📁 Results saved to: {output_dir}")
    print(f"   - verification-results.json")
    print(f"   - parity-report.md")
    print(f"   - screenshots/")
    print()

    return 0 if results['overall_score'] >= 85 else 1


def generate_summary_report(results, output_dir):
    """Generate a markdown summary report"""

    report_path = output_dir / 'parity-report.md'

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# Catalog Parity Verification Report\n\n")
        f.write(f"**Generated:** {results['timestamp']}\n\n")
        f.write(f"**Legacy URL:** {results['legacy_url']}\n\n")
        f.write(f"**Modern URL:** {results['modern_url']}\n\n")

        f.write("## Summary\n\n")
        f.write(f"- **Total Workflows:** {results['summary']['total_workflows']}\n")
        f.write(f"- **Total Checks:** {results['summary']['total_checks']}\n")
        f.write(f"- **Passed Checks:** {results['summary']['passed_checks']}\n")
        f.write(f"- **Failed Checks:** {results['summary']['failed_checks']}\n")
        f.write(f"- **Parity Score:** {results['summary']['parity_score']}%\n\n")

        # Overall status
        if results['overall_score'] >= 85:
            f.write("**Status:** ✅ PASSED (≥85% parity)\n\n")
        else:
            f.write("**Status:** ❌ FAILED (<85% parity)\n\n")

        f.write("---\n\n")

        # Workflow details
        f.write("## Workflow Results\n\n")

        for workflow_name, workflow_result in results['workflows'].items():
            status = "✅ PASSED" if workflow_result['passed'] else "❌ FAILED"
            f.write(f"### {workflow_name} - {status}\n\n")
            f.write(f"**Description:** {workflow_result['description']}\n\n")
            f.write(f"**Legacy URL:** `{workflow_result['legacy_url']}`\n\n")
            f.write(f"**Modern URL:** `{workflow_result['modern_url']}`\n\n")

            # Screenshots
            if 'screenshots' in workflow_result:
                f.write("**Screenshots:**\n\n")
                f.write(f"- Legacy: `{workflow_result['screenshots']['legacy']}`\n")
                f.write(f"- Modern: `{workflow_result['screenshots']['modern']}`\n\n")

            # Checks
            f.write("**Checks:**\n\n")
            for check in workflow_result['checks']:
                check_status = "✅" if check['passed'] else "❌"
                f.write(f"- {check_status} {check['check']}\n")

            f.write("\n")

            # Issues
            if workflow_result['issues']:
                f.write("**Issues:**\n\n")
                for issue in workflow_result['issues']:
                    f.write(f"- {issue}\n")
                f.write("\n")

            f.write("---\n\n")

        # Recommendations
        f.write("## Recommendations\n\n")

        if results['overall_score'] >= 85:
            f.write("The modern application demonstrates good parity with the legacy system. "
                   "Review any remaining issues and proceed with migration.\n\n")
        else:
            f.write("The modern application needs additional work to achieve parity. "
                   "Address the issues identified above before proceeding.\n\n")


if __name__ == '__main__':
    sys.exit(main())
