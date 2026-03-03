#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Browser Agent - Verification Mode (Python)
Compare legacy vs modern applications for feature parity
"""

import json
import os
import sys
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import difflib

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

try:
    from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext
except ImportError:
    print("Installing Playwright...")
    os.system(f"{sys.executable} -m pip install playwright")
    os.system(f"{sys.executable} -m playwright install chromium")
    from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext

try:
    from PIL import Image, ImageChops, ImageDraw, ImageFont
except ImportError:
    print("Installing Pillow for image comparison...")
    os.system(f"{sys.executable} -m pip install Pillow")
    from PIL import Image, ImageChops, ImageDraw, ImageFont


class ParityVerifier:
    """Compare legacy and modern applications for feature parity"""

    def __init__(self, legacy_url: str, modern_url: str, output_dir: str,
                 workflows: Optional[List[str]] = None, compare_data: bool = True,
                 screenshot_diff: bool = True):
        self.legacy_url = legacy_url.rstrip('/')
        self.modern_url = modern_url.rstrip('/')
        self.output_dir = Path(output_dir)
        self.workflows = workflows or []
        self.compare_data_flag = compare_data
        self.screenshot_diff_flag = screenshot_diff

        # Create output structure
        (self.output_dir / 'screenshots' / 'legacy').mkdir(parents=True, exist_ok=True)
        (self.output_dir / 'screenshots' / 'modern').mkdir(parents=True, exist_ok=True)
        (self.output_dir / 'screenshots' / 'diff').mkdir(parents=True, exist_ok=True)

        self.results = {
            'timestamp': datetime.now().isoformat(),
            'legacy_url': self.legacy_url,
            'modern_url': self.modern_url,
            'workflows': [],
            'feature_comparison': {},
            'data_comparison': {},
            'visual_comparison': {},
            'issues': [],
            'parity_score': 0.0
        }

        self.screenshot_counter = 0

    def verify_all(self):
        """Run complete verification suite"""
        print("🔍 Browser Agent - Verification Mode")
        print("=" * 50)
        print(f"Legacy:  {self.legacy_url}")
        print(f"Modern:  {self.modern_url}")
        print(f"Output:  {self.output_dir}")
        print("=" * 50)
        print()

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)

            try:
                # Create contexts for both apps
                legacy_context = browser.new_context(viewport={'width': 1920, 'height': 1080})
                modern_context = browser.new_context(viewport={'width': 1920, 'height': 1080})

                legacy_page = legacy_context.new_page()
                modern_page = modern_context.new_page()

                # Run verification workflows
                if self.workflows:
                    for workflow in self.workflows:
                        print(f"\n📋 Verifying workflow: {workflow}")
                        self.verify_workflow(legacy_page, modern_page, workflow)
                else:
                    # Default: verify home pages
                    print(f"\n📋 Verifying home pages")
                    self.verify_page_pair(legacy_page, modern_page, "home", "/")

                # Calculate parity score
                self.calculate_parity_score()

                # Generate reports
                self.save_results()
                self.generate_feature_matrix()
                self.generate_html_report()

                print("\n" + "=" * 50)
                print(f"✅ Verification complete!")
                print(f"📊 Parity Score: {self.results['parity_score']:.1f}%")
                self.print_summary()
                print("=" * 50)

            finally:
                browser.close()

    def verify_workflow(self, legacy_page: Page, modern_page: Page, workflow_name: str):
        """Verify a specific workflow"""
        workflow_result = {
            'name': workflow_name,
            'pages': [],
            'passed': True,
            'issues': []
        }

        # Map workflow names to paths
        workflow_paths = {
            'catalog-list': '/catalog',
            'catalog-crud': '/catalog',
            'static-pages': '/',
            'home': '/'
        }

        path = workflow_paths.get(workflow_name, '/')
        page_result = self.verify_page_pair(legacy_page, modern_page, workflow_name, path)
        workflow_result['pages'].append(page_result)

        if page_result.get('issues'):
            workflow_result['passed'] = False
            workflow_result['issues'].extend(page_result['issues'])

        self.results['workflows'].append(workflow_result)

    def verify_page_pair(self, legacy_page: Page, modern_page: Page,
                         page_name: str, path: str) -> Dict[str, Any]:
        """Verify a single page pair"""
        print(f"  📄 Comparing: {page_name} ({path})")

        page_result = {
            'name': page_name,
            'path': path,
            'timestamp': datetime.now().isoformat(),
            'elements': {'legacy': {}, 'modern': {}, 'comparison': {}},
            'data': {'legacy': {}, 'modern': {}, 'comparison': {}},
            'visual': {},
            'issues': []
        }

        try:
            # Load both pages
            legacy_page.goto(f"{self.legacy_url}{path}", wait_until='networkidle', timeout=30000)
            legacy_page.wait_for_timeout(2000)

            modern_page.goto(f"{self.modern_url}{path}", wait_until='networkidle', timeout=30000)
            modern_page.wait_for_timeout(2000)

            # Capture screenshots
            if self.screenshot_diff_flag:
                legacy_ss = self.capture_screenshot(legacy_page, 'legacy', page_name)
                modern_ss = self.capture_screenshot(modern_page, 'modern', page_name)

                # Compare screenshots
                diff_result = self.compare_screenshots(legacy_ss, modern_ss, page_name)
                page_result['visual'] = diff_result

                if diff_result['difference_percentage'] > 20:  # More than 20% different
                    page_result['issues'].append({
                        'type': 'visual',
                        'severity': 'warning',
                        'message': f"Visual difference: {diff_result['difference_percentage']:.1f}%"
                    })

            # Compare elements
            print("    🔍 Discovering elements...")
            legacy_elements = self.discover_elements(legacy_page)
            modern_elements = self.discover_elements(modern_page)

            page_result['elements']['legacy'] = legacy_elements
            page_result['elements']['modern'] = modern_elements
            page_result['elements']['comparison'] = self.compare_elements(
                legacy_elements, modern_elements
            )

            # Add element issues
            if page_result['elements']['comparison'].get('missing_in_modern'):
                for elem in page_result['elements']['comparison']['missing_in_modern']:
                    page_result['issues'].append({
                        'type': 'element',
                        'severity': 'error',
                        'message': f"Missing element: {elem['type']} - {elem['text']}"
                    })

            # Compare data (grids/tables)
            if self.compare_data_flag:
                print("    📊 Comparing data...")
                legacy_data = self.extract_grid_data(legacy_page)
                modern_data = self.extract_grid_data(modern_page)

                page_result['data']['legacy'] = legacy_data
                page_result['data']['modern'] = modern_data
                page_result['data']['comparison'] = self.compare_data(legacy_data, modern_data)

                # Add data issues
                data_comp = page_result['data']['comparison']
                if data_comp.get('row_count_mismatch'):
                    page_result['issues'].append({
                        'type': 'data',
                        'severity': 'error',
                        'message': f"Row count mismatch: {data_comp['legacy_rows']} vs {data_comp['modern_rows']}"
                    })

            print(f"    ✅ Complete - {len(page_result['issues'])} issues found")

        except Exception as e:
            print(f"    ❌ Error: {str(e)}")
            page_result['issues'].append({
                'type': 'error',
                'severity': 'critical',
                'message': f"Page verification failed: {str(e)}"
            })

        return page_result

    def capture_screenshot(self, page: Page, app_type: str, page_name: str) -> str:
        """Capture screenshot"""
        filename = f"{self.screenshot_counter:03d}_{page_name}.png"
        filepath = self.output_dir / 'screenshots' / app_type / filename
        page.screenshot(path=str(filepath), full_page=True)
        self.screenshot_counter += 1
        return str(filepath)

    def compare_screenshots(self, legacy_path: str, modern_path: str,
                           page_name: str) -> Dict[str, Any]:
        """Compare two screenshots pixel by pixel"""
        try:
            legacy_img = Image.open(legacy_path)
            modern_img = Image.open(modern_path)

            # Resize to same dimensions if needed
            if legacy_img.size != modern_img.size:
                width = max(legacy_img.width, modern_img.width)
                height = max(legacy_img.height, modern_img.height)

                legacy_resized = Image.new('RGB', (width, height), (255, 255, 255))
                legacy_resized.paste(legacy_img, (0, 0))

                modern_resized = Image.new('RGB', (width, height), (255, 255, 255))
                modern_resized.paste(modern_img, (0, 0))

                legacy_img = legacy_resized
                modern_img = modern_resized

            # Calculate difference
            diff = ImageChops.difference(legacy_img, modern_img)
            diff_bbox = diff.getbbox()

            if diff_bbox:
                # Create visual diff image
                diff_highlighted = modern_img.copy()
                draw = ImageDraw.Draw(diff_highlighted, 'RGBA')
                draw.rectangle(diff_bbox, outline=(255, 0, 0, 128), width=3)

                diff_path = self.output_dir / 'screenshots' / 'diff' / f"{self.screenshot_counter:03d}_{page_name}_diff.png"
                diff_highlighted.save(str(diff_path))

                # Calculate percentage difference
                diff_pixels = sum(
                    1 for pixel in diff.getdata()
                    if pixel != (0, 0, 0)
                )
                total_pixels = legacy_img.width * legacy_img.height
                diff_percentage = (diff_pixels / total_pixels) * 100

                return {
                    'has_difference': True,
                    'difference_percentage': diff_percentage,
                    'diff_image': str(diff_path),
                    'diff_bbox': diff_bbox
                }
            else:
                return {
                    'has_difference': False,
                    'difference_percentage': 0.0
                }

        except Exception as e:
            print(f"    ⚠️  Screenshot comparison failed: {str(e)}")
            return {
                'has_difference': False,
                'difference_percentage': 0.0,
                'error': str(e)
            }

    def discover_elements(self, page: Page) -> Dict[str, List[Dict]]:
        """Discover interactive elements on a page"""
        elements = {
            'buttons': [],
            'links': [],
            'inputs': [],
            'tables': [],
            'headings': []
        }

        try:
            # Buttons
            buttons = page.query_selector_all('button, input[type="submit"], input[type="button"], a.btn')
            for btn in buttons[:50]:  # Limit to avoid overflow
                text = btn.text_content() or btn.get_attribute('value') or ''
                if text.strip():
                    elements['buttons'].append({
                        'type': 'button',
                        'text': text.strip()[:100],
                        'visible': btn.is_visible()
                    })

            # Links
            links = page.query_selector_all('a[href]')
            for link in links[:50]:
                text = link.text_content() or ''
                href = link.get_attribute('href') or ''
                if text.strip() and not href.startswith('javascript:'):
                    elements['links'].append({
                        'type': 'link',
                        'text': text.strip()[:100],
                        'href': href[:200],
                        'visible': link.is_visible()
                    })

            # Input fields
            inputs = page.query_selector_all('input:not([type="submit"]):not([type="button"]), textarea, select')
            for inp in inputs[:50]:
                name = inp.get_attribute('name') or inp.get_attribute('id') or ''
                input_type = inp.get_attribute('type') or 'text'
                if name or input_type:
                    elements['inputs'].append({
                        'type': f'input_{input_type}',
                        'name': name[:100],
                        'visible': inp.is_visible()
                    })

            # Tables
            tables = page.query_selector_all('table, [role="table"], [class*="grid"], [class*="table"]')
            for i, table in enumerate(tables[:10]):
                if table.is_visible():
                    elements['tables'].append({
                        'type': 'table',
                        'index': i,
                        'visible': True
                    })

            # Headings
            headings = page.query_selector_all('h1, h2, h3, h4, h5, h6')
            for heading in headings[:20]:
                text = heading.text_content() or ''
                if text.strip():
                    elements['headings'].append({
                        'type': heading.evaluate('el => el.tagName.toLowerCase()'),
                        'text': text.strip()[:200],
                        'visible': heading.is_visible()
                    })

        except Exception as e:
            print(f"    ⚠️  Element discovery error: {str(e)}")

        return elements

    def compare_elements(self, legacy: Dict, modern: Dict) -> Dict[str, Any]:
        """Compare element sets"""
        comparison = {
            'total_legacy': sum(len(v) for v in legacy.values()),
            'total_modern': sum(len(v) for v in modern.values()),
            'missing_in_modern': [],
            'new_in_modern': [],
            'matching': 0
        }

        # Compare buttons by text
        legacy_button_texts = {b['text'].lower() for b in legacy.get('buttons', [])}
        modern_button_texts = {b['text'].lower() for b in modern.get('buttons', [])}

        missing_buttons = legacy_button_texts - modern_button_texts
        for text in missing_buttons:
            comparison['missing_in_modern'].append({'type': 'button', 'text': text})

        # Compare headings
        legacy_heading_texts = {h['text'].lower() for h in legacy.get('headings', [])}
        modern_heading_texts = {h['text'].lower() for h in modern.get('headings', [])}

        missing_headings = legacy_heading_texts - modern_heading_texts
        for text in missing_headings:
            comparison['missing_in_modern'].append({'type': 'heading', 'text': text})

        # Calculate matching percentage
        total_legacy_features = len(legacy_button_texts) + len(legacy_heading_texts)
        if total_legacy_features > 0:
            total_missing = len(missing_buttons) + len(missing_headings)
            comparison['matching'] = ((total_legacy_features - total_missing) / total_legacy_features) * 100
        else:
            comparison['matching'] = 100.0

        return comparison

    def extract_grid_data(self, page: Page) -> List[Dict[str, Any]]:
        """Extract data from grids/tables"""
        grids = []

        try:
            tables = page.query_selector_all('table, [role="table"], [class*="grid"]')

            for i, table in enumerate(tables[:5]):  # Limit to first 5 tables
                if not table.is_visible():
                    continue

                grid_data = page.evaluate("""(tableElement) => {
                    const headers = [];
                    const rows = [];

                    // Try standard table structure
                    const headerCells = tableElement.querySelectorAll('th, thead td, [role="columnheader"]');
                    headerCells.forEach(cell => {
                        headers.push(cell.textContent.trim());
                    });

                    // Get data rows
                    const dataRows = tableElement.querySelectorAll('tbody tr, [role="row"]:not(:first-child)');
                    for (let i = 0; i < Math.min(10, dataRows.length); i++) {
                        const row = [];
                        const cells = dataRows[i].querySelectorAll('td, [role="cell"]');
                        cells.forEach(cell => {
                            row.push(cell.textContent.trim());
                        });
                        if (row.length > 0) {
                            rows.push(row);
                        }
                    }

                    return {
                        headers: headers,
                        rows: rows,
                        totalRows: dataRows.length
                    };
                }""", table)

                if grid_data['headers'] or grid_data['rows']:
                    grids.append({
                        'index': i,
                        'headers': grid_data['headers'],
                        'rows': grid_data['rows'],
                        'total_rows': grid_data['totalRows']
                    })

        except Exception as e:
            print(f"    ⚠️  Grid extraction error: {str(e)}")

        return grids

    def compare_data(self, legacy_grids: List[Dict], modern_grids: List[Dict]) -> Dict[str, Any]:
        """Compare grid data"""
        comparison = {
            'legacy_grids': len(legacy_grids),
            'modern_grids': len(modern_grids),
            'row_count_mismatch': False,
            'data_differences': []
        }

        if not legacy_grids or not modern_grids:
            return comparison

        # Compare first grid (most common case)
        if legacy_grids and modern_grids:
            legacy_grid = legacy_grids[0]
            modern_grid = modern_grids[0]

            comparison['legacy_rows'] = legacy_grid['total_rows']
            comparison['modern_rows'] = modern_grid['total_rows']

            if legacy_grid['total_rows'] != modern_grid['total_rows']:
                comparison['row_count_mismatch'] = True

            # Compare headers
            legacy_headers = set(h.lower() for h in legacy_grid['headers'])
            modern_headers = set(h.lower() for h in modern_grid['headers'])

            missing_headers = legacy_headers - modern_headers
            if missing_headers:
                comparison['data_differences'].append(f"Missing columns: {', '.join(missing_headers)}")

            # Sample compare first few rows
            for i in range(min(3, len(legacy_grid['rows']), len(modern_grid['rows']))):
                legacy_row = legacy_grid['rows'][i]
                modern_row = modern_grid['rows'][i]

                if legacy_row != modern_row:
                    comparison['data_differences'].append(f"Row {i+1} differs")

        return comparison

    def calculate_parity_score(self):
        """Calculate overall parity score (0-100%)"""
        scores = {
            'feature_completeness': 0.0,
            'visual_consistency': 0.0,
            'data_accuracy': 0.0,
            'workflow_equivalence': 0.0
        }

        total_pages = 0
        feature_scores = []
        visual_scores = []
        data_scores = []

        for workflow in self.results['workflows']:
            for page in workflow['pages']:
                total_pages += 1

                # Feature score (elements comparison)
                if 'elements' in page and 'comparison' in page['elements']:
                    comp = page['elements']['comparison']
                    feature_scores.append(comp.get('matching', 0))

                # Visual score (screenshot comparison)
                if 'visual' in page:
                    visual = page['visual']
                    if visual.get('has_difference'):
                        visual_score = max(0, 100 - visual.get('difference_percentage', 100))
                        visual_scores.append(visual_score)
                    else:
                        visual_scores.append(100.0)

                # Data score (grid comparison)
                if 'data' in page and 'comparison' in page['data']:
                    comp = page['data']['comparison']
                    if comp.get('row_count_mismatch'):
                        data_scores.append(70.0)  # Partial credit
                    elif comp.get('data_differences'):
                        data_scores.append(80.0)
                    else:
                        data_scores.append(100.0)

        # Calculate weighted average
        if feature_scores:
            scores['feature_completeness'] = sum(feature_scores) / len(feature_scores)

        if visual_scores:
            scores['visual_consistency'] = sum(visual_scores) / len(visual_scores)

        if data_scores:
            scores['data_accuracy'] = sum(data_scores) / len(data_scores)
        else:
            scores['data_accuracy'] = 100.0  # No data to compare

        # Workflow equivalence (did all workflows run?)
        total_workflows = len(self.results['workflows'])
        passed_workflows = sum(1 for w in self.results['workflows'] if w.get('passed', False))
        if total_workflows > 0:
            scores['workflow_equivalence'] = (passed_workflows / total_workflows) * 100

        # Weighted final score
        final_score = (
            scores['feature_completeness'] * 0.40 +
            scores['visual_consistency'] * 0.20 +
            scores['data_accuracy'] * 0.30 +
            scores['workflow_equivalence'] * 0.10
        )

        self.results['parity_score'] = final_score
        self.results['detailed_scores'] = scores

    def save_results(self):
        """Save verification results to JSON"""
        results_file = self.output_dir / 'parity-results.json'
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Results saved: {results_file}")

    def generate_feature_matrix(self):
        """Generate feature parity matrix markdown"""
        matrix_file = self.output_dir / 'feature-matrix.md'

        with open(matrix_file, 'w', encoding='utf-8') as f:
            f.write("# Feature Parity Matrix\n\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Legacy**: {self.legacy_url}\n\n")
            f.write(f"**Modern**: {self.modern_url}\n\n")
            f.write(f"**Parity Score**: {self.results['parity_score']:.1f}%\n\n")

            f.write("---\n\n")
            f.write("## Workflow Results\n\n")
            f.write("| Workflow | Status | Issues | Pages Tested |\n")
            f.write("|----------|--------|--------|-------------|\n")

            for workflow in self.results['workflows']:
                status = "✅ Pass" if workflow.get('passed', False) else "❌ Fail"
                issue_count = len(workflow.get('issues', []))
                page_count = len(workflow.get('pages', []))
                f.write(f"| {workflow['name']} | {status} | {issue_count} | {page_count} |\n")

            f.write("\n---\n\n")
            f.write("## Detailed Issues\n\n")

            for workflow in self.results['workflows']:
                if workflow.get('issues'):
                    f.write(f"### {workflow['name']}\n\n")
                    for issue in workflow['issues']:
                        severity_emoji = {'critical': '🔴', 'error': '⚠️', 'warning': '🟡'}.get(issue.get('severity', 'warning'), '🟡')
                        f.write(f"- {severity_emoji} **{issue.get('type', 'unknown')}**: {issue.get('message', 'No message')}\n")
                    f.write("\n")

        print(f"📊 Feature matrix: {matrix_file}")

    def generate_html_report(self):
        """Generate HTML diff report"""
        report_file = self.output_dir / 'diff-report.html'

        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Parity Report - {datetime.now().strftime('%Y-%m-%d')}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .header {{ background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
        .score {{ font-size: 48px; font-weight: bold; color: {'#4CAF50' if self.results['parity_score'] >= 70 else '#ff9800'}; }}
        .workflow {{ background: white; padding: 15px; margin: 10px 0; border-radius: 8px; }}
        .screenshot-pair {{ display: flex; gap: 20px; margin: 20px 0; }}
        .screenshot-pair img {{ max-width: 45%; border: 1px solid #ddd; }}
        .issue {{ padding: 10px; margin: 5px 0; border-radius: 4px; }}
        .issue.error {{ background: #ffebee; border-left: 4px solid #f44336; }}
        .issue.warning {{ background: #fff3e0; border-left: 4px solid #ff9800; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Feature Parity Report</h1>
        <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>Legacy:</strong> {self.legacy_url}</p>
        <p><strong>Modern:</strong> {self.modern_url}</p>
        <div class="score">{self.results['parity_score']:.1f}%</div>
    </div>
"""

        for workflow in self.results['workflows']:
            html += f"""
    <div class="workflow">
        <h2>{workflow['name']}</h2>
        <p><strong>Status:</strong> {'✅ Passed' if workflow.get('passed') else '❌ Failed'}</p>
"""

            if workflow.get('issues'):
                html += "<h3>Issues</h3>"
                for issue in workflow['issues']:
                    severity = issue.get('severity', 'warning')
                    html += f'<div class="issue {severity}">'
                    html += f"<strong>{issue.get('type', 'unknown').upper()}</strong>: {issue.get('message', 'No message')}"
                    html += '</div>'

            html += "</div>"

        html += """
</body>
</html>
"""

        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(html)

        print(f"📄 HTML report: {report_file}")

    def print_summary(self):
        """Print summary to console"""
        print("\n📋 Summary:")
        print(f"  Workflows tested: {len(self.results['workflows'])}")

        total_issues = sum(len(w.get('issues', [])) for w in self.results['workflows'])
        print(f"  Total issues: {total_issues}")

        if 'detailed_scores' in self.results:
            scores = self.results['detailed_scores']
            print("\n📊 Detailed Scores:")
            print(f"  Feature Completeness: {scores['feature_completeness']:.1f}% (40% weight)")
            print(f"  Visual Consistency:   {scores['visual_consistency']:.1f}% (20% weight)")
            print(f"  Data Accuracy:        {scores['data_accuracy']:.1f}% (30% weight)")
            print(f"  Workflow Equivalence: {scores['workflow_equivalence']:.1f}% (10% weight)")

        print(f"\n📂 Output Files:")
        print(f"  - {self.output_dir}/parity-results.json")
        print(f"  - {self.output_dir}/feature-matrix.md")
        print(f"  - {self.output_dir}/diff-report.html")
        print(f"  - {self.output_dir}/screenshots/")


def main():
    parser = argparse.ArgumentParser(description='Browser Agent - Verification Mode')
    parser.add_argument('--legacy-url', required=True, help='Legacy application URL')
    parser.add_argument('--modern-url', required=True, help='Modern application URL')
    parser.add_argument('--output-dir', default='./parity-results', help='Output directory')
    parser.add_argument('--workflows', help='Comma-separated workflow names')
    parser.add_argument('--compare-data', action='store_true', default=True, help='Compare data grids')
    parser.add_argument('--screenshot-diff', action='store_true', default=True, help='Generate screenshot diffs')

    args = parser.parse_args()

    workflows = []
    if args.workflows:
        workflows = [w.strip() for w in args.workflows.split(',')]

    verifier = ParityVerifier(
        legacy_url=args.legacy_url,
        modern_url=args.modern_url,
        output_dir=args.output_dir,
        workflows=workflows,
        compare_data=args.compare_data,
        screenshot_diff=args.screenshot_diff
    )

    verifier.verify_all()


if __name__ == '__main__':
    main()
