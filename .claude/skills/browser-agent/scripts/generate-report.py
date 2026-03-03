#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate parity report from verification results"""

import json
from pathlib import Path

def main():
    results_path = Path("C:/Users/pratikp6/codebase/eshopmigration/legacy-golden/parity-results/catalog/verification-results.json")
    output_dir = results_path.parent

    with open(results_path, 'r') as f:
        results = json.load(f)

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

        # Overall status (using plain text instead of emoji)
        if results['overall_score'] >= 85:
            f.write("**Status:** [PASSED] (>=85% parity)\n\n")
        else:
            f.write("**Status:** [NEEDS WORK] (<85% parity)\n\n")

        f.write("---\n\n")

        # Workflow details
        f.write("## Workflow Results\n\n")

        for workflow_name, workflow_result in results['workflows'].items():
            status = "[PASSED]" if workflow_result['passed'] else "[FAILED]"
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
                check_status = "[PASS]" if check['passed'] else "[FAIL]"
                f.write(f"- {check_status} `{check['check']}`\n")

            f.write("\n")

            # Issues
            if workflow_result['issues']:
                f.write("**Issues Detected:**\n\n")
                for issue in workflow_result['issues']:
                    f.write(f"- {issue}\n")
                f.write("\n")

            # Check details
            f.write("<details>\n<summary>Check Details</summary>\n\n")
            f.write("```json\n")
            f.write(json.dumps(workflow_result['checks'], indent=2))
            f.write("\n```\n\n")
            f.write("</details>\n\n")

            f.write("---\n\n")

        # Recommendations
        f.write("## Key Findings\n\n")

        # Analyze issues
        all_issues = []
        for workflow_result in results['workflows'].values():
            all_issues.extend(workflow_result['issues'])

        if all_issues:
            f.write("### Issues Found\n\n")
            unique_issues = set(all_issues)
            for issue in unique_issues:
                count = all_issues.count(issue)
                f.write(f"- **{issue}** (affects {count} workflow(s))\n")
            f.write("\n")

        # Success areas
        f.write("### Working Well\n\n")
        working_items = []
        for workflow_result in results['workflows'].values():
            for check in workflow_result['checks']:
                if check['passed']:
                    working_items.append(check['check'])

        if working_items:
            unique_working = set(working_items)
            for item in unique_working:
                count = working_items.count(item)
                f.write(f"- {item.replace('_', ' ').title()} ({count}/{len(results['workflows'])} workflows)\n")
            f.write("\n")

        f.write("## Recommendations\n\n")

        if results['overall_score'] >= 85:
            f.write("The modern application demonstrates good parity with the legacy system. "
                   "Review any remaining issues and proceed with migration.\n\n")
        else:
            f.write("The modern application needs additional work to achieve parity. "
                   "Priority recommendations:\n\n")

            if "Missing interactive elements" in all_issues:
                f.write("1. **Add interactive elements** - The modern catalog list page appears to be loading "
                       "but elements are not being detected. This could be:\n")
                f.write("   - A timing issue (elements loading after the check)\n")
                f.write("   - Elements using different selectors than expected\n")
                f.write("   - Page not fully rendering\n\n")

            if "Missing data table/grid" in all_issues:
                f.write("2. **Implement data table/grid** - The catalog list should display products in a table or grid format\n\n")

            if "Missing main content container" in all_issues:
                f.write("3. **Fix main content detection** - Ensure the page has proper semantic HTML structure\n\n")

        f.write("## Next Steps\n\n")
        f.write("1. Review screenshots in `screenshots/` directory\n")
        f.write("2. Address critical issues identified above\n")
        f.write("3. Re-run verification after fixes\n")
        f.write("4. Document any intentional differences in evidence.md\n\n")

    print(f"Report generated: {report_path}")

if __name__ == '__main__':
    main()
