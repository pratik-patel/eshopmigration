#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Browser Agent - Workflow-Specific Discovery
Captures specific workflows with detailed interactions
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

try:
    from playwright.sync_api import sync_playwright, Page
except ImportError:
    print("Installing Playwright...")
    os.system(f"{sys.executable} -m pip install playwright")
    os.system(f"{sys.executable} -m playwright install chromium")
    from playwright.sync_api import sync_playwright, Page


class WorkflowDiscovery:
    """Discover specific application workflows"""

    def __init__(self, base_url: str, output_dir: str):
        self.base_url = base_url.rstrip('/')
        self.output_dir = Path(output_dir)
        self.workflows = {}
        self.screenshot_counter = 0

        # Create output structure
        for workflow_name in ['catalog-list', 'catalog-crud', 'static-pages']:
            workflow_dir = self.output_dir / workflow_name
            (workflow_dir / 'screenshots').mkdir(parents=True, exist_ok=True)

    def capture_screenshot(self, page: Page, workflow: str, name: str) -> str:
        """Capture and save a screenshot"""
        filename = f"{self.screenshot_counter:03d}_{name}.png"
        filepath = self.output_dir / workflow / 'screenshots' / filename
        page.screenshot(path=str(filepath), full_page=True)
        self.screenshot_counter += 1
        print(f"      Screenshot: {filename}")
        return filename

    def capture_grid_data(self, page: Page, table_selector: str = 'table'):
        """Capture data from a table"""
        try:
            data = page.evaluate('''(selector) => {
                const table = document.querySelector(selector);
                if (!table) return null;

                const headers = [];
                const rows = [];

                // Extract headers
                const headerCells = table.querySelectorAll('th');
                headerCells.forEach(cell => headers.push(cell.textContent?.trim() || ''));

                // Extract all visible rows
                const dataRows = table.querySelectorAll('tbody tr');
                dataRows.forEach(row => {
                    const rowData = [];
                    const cells = row.querySelectorAll('td');
                    cells.forEach(cell => rowData.push(cell.textContent?.trim() || ''));
                    if (rowData.length > 0) rows.push(rowData);
                });

                return { headers, rows, totalRows: dataRows.length };
            }''', table_selector)

            return data
        except Exception as e:
            print(f"      Warning: Could not capture table data - {e}")
            return None

    def capture_form_fields(self, page: Page):
        """Capture form field information"""
        try:
            fields = page.evaluate('''() => {
                const inputs = document.querySelectorAll('input, select, textarea');
                return Array.from(inputs).map(input => ({
                    name: input.name || input.id || '',
                    type: input.type || input.tagName.toLowerCase(),
                    label: input.previousElementSibling?.textContent?.trim() ||
                           document.querySelector(`label[for="${input.id}"]`)?.textContent?.trim() || '',
                    required: input.required || input.getAttribute('required') !== null,
                    value: input.value || '',
                    visible: input.offsetParent !== null
                })).filter(f => f.visible && f.type !== 'hidden');
            }''')
            return fields
        except Exception:
            return []

    def discover_catalog_list(self, page: Page):
        """Discover catalog list workflow"""
        print("\n=== Catalog List Workflow ===")
        workflow = {
            'name': 'catalog-list',
            'description': 'View and navigate catalog items list',
            'steps': [],
            'screenshots': [],
            'data': {}
        }

        print("   Step 1: Navigate to home page (catalog list)")
        page.goto(self.base_url, wait_until='networkidle')
        page.wait_for_timeout(1000)

        # Capture main list view
        screenshot = self.capture_screenshot(page, 'catalog-list', 'main_list')
        workflow['screenshots'].append(screenshot)

        # Capture grid data
        print("   Step 2: Capture catalog grid data")
        grid_data = self.capture_grid_data(page)
        if grid_data:
            workflow['data']['catalog_items'] = grid_data
            print(f"      Captured {grid_data['totalRows']} catalog items")

        # Check for pagination
        try:
            pagination = page.query_selector('.pagination, [class*="pager"]')
            if pagination:
                workflow['data']['has_pagination'] = True
                print("      Pagination detected")
        except Exception:
            workflow['data']['has_pagination'] = False

        # Identify action links
        print("   Step 3: Identify available actions")
        actions = page.evaluate('''() => {
            const editLinks = document.querySelectorAll('a[href*="/Edit/"]');
            const detailLinks = document.querySelectorAll('a[href*="/Details/"]');
            const deleteLinks = document.querySelectorAll('a[href*="/Delete/"]');
            return {
                edit: editLinks.length,
                details: detailLinks.length,
                delete: deleteLinks.length
            };
        }''')
        workflow['data']['available_actions'] = actions
        print(f"      Found: {actions['edit']} edit, {actions['details']} details, {actions['delete']} delete links")

        # Check for Create button
        create_btn = page.query_selector('a[href*="/Create"], button:has-text("Create")')
        if create_btn:
            workflow['data']['has_create'] = True
            print("      Create button found")

        workflow['steps'] = [
            {'action': 'navigate', 'description': 'Load catalog list page'},
            {'action': 'observe', 'description': 'View all catalog items in grid'},
            {'action': 'identify', 'description': 'Available actions: Edit, Details, Delete, Create'}
        ]

        self.workflows['catalog-list'] = workflow

    def discover_catalog_crud(self, page: Page):
        """Discover catalog CRUD operations workflow"""
        print("\n=== Catalog CRUD Workflow ===")
        workflow = {
            'name': 'catalog-crud',
            'description': 'Create, Read, Update, Delete catalog items',
            'steps': [],
            'screenshots': [],
            'forms': {}
        }

        # Start from home
        page.goto(self.base_url, wait_until='networkidle')

        # 1. CREATE - Navigate to Create page
        print("   Step 1: Navigate to Create page")
        create_link = page.query_selector('a[href*="/Create"]')
        if create_link:
            create_link.click()
            page.wait_for_load_state('networkidle')
            page.wait_for_timeout(1000)

            screenshot = self.capture_screenshot(page, 'catalog-crud', 'create_form')
            workflow['screenshots'].append(screenshot)

            # Capture form fields
            print("   Step 2: Capture create form fields")
            fields = self.capture_form_fields(page)
            workflow['forms']['create'] = {
                'url': page.url,
                'fields': fields,
                'field_count': len(fields)
            }
            print(f"      Captured {len(fields)} form fields")
            for field in fields:
                print(f"         - {field['name']} ({field['type']}) {'*' if field['required'] else ''}")

            # Go back to list
            page.goto(self.base_url, wait_until='networkidle')

        # 2. EDIT - Navigate to Edit page
        print("   Step 3: Navigate to Edit page (first item)")
        edit_link = page.query_selector('a[href*="/Edit/"]')
        if edit_link:
            edit_link.click()
            page.wait_for_load_state('networkidle')
            page.wait_for_timeout(1000)

            screenshot = self.capture_screenshot(page, 'catalog-crud', 'edit_form')
            workflow['screenshots'].append(screenshot)

            # Capture form fields with values
            print("   Step 4: Capture edit form fields")
            fields = self.capture_form_fields(page)
            workflow['forms']['edit'] = {
                'url': page.url,
                'fields': fields,
                'field_count': len(fields)
            }
            print(f"      Captured {len(fields)} form fields with existing values")

            # Go back to list
            page.goto(self.base_url, wait_until='networkidle')

        # 3. DETAILS - Navigate to Details page
        print("   Step 5: Navigate to Details page (first item)")
        details_link = page.query_selector('a[href*="/Details/"]')
        if details_link:
            details_link.click()
            page.wait_for_load_state('networkidle')
            page.wait_for_timeout(1000)

            screenshot = self.capture_screenshot(page, 'catalog-crud', 'details_view')
            workflow['screenshots'].append(screenshot)

            # Capture displayed fields
            print("   Step 6: Capture details view")
            details_data = page.evaluate('''() => {
                const labels = document.querySelectorAll('dt, label, .field-label');
                const values = document.querySelectorAll('dd, .field-value');
                const pairs = [];

                labels.forEach((label, i) => {
                    pairs.push({
                        label: label.textContent?.trim() || '',
                        value: values[i]?.textContent?.trim() || ''
                    });
                });

                return pairs;
            }''')
            workflow['forms']['details'] = {
                'url': page.url,
                'fields': details_data
            }
            print(f"      Captured {len(details_data)} detail fields")

            # Go back to list
            page.goto(self.base_url, wait_until='networkidle')

        # 4. DELETE - Navigate to Delete confirmation
        print("   Step 7: Navigate to Delete confirmation (first item)")
        delete_link = page.query_selector('a[href*="/Delete/"]')
        if delete_link:
            delete_link.click()
            page.wait_for_load_state('networkidle')
            page.wait_for_timeout(1000)

            screenshot = self.capture_screenshot(page, 'catalog-crud', 'delete_confirm')
            workflow['screenshots'].append(screenshot)

            # Capture confirmation message and item details
            print("   Step 8: Capture delete confirmation")
            delete_data = page.evaluate('''() => {
                const heading = document.querySelector('h1, h2, h3')?.textContent || '';
                const confirmBtn = document.querySelector('input[type="submit"], button[type="submit"]');
                return {
                    heading: heading,
                    hasConfirmButton: !!confirmBtn,
                    confirmButtonText: confirmBtn?.value || confirmBtn?.textContent || ''
                };
            }''')
            workflow['forms']['delete'] = {
                'url': page.url,
                'confirmation': delete_data
            }
            print(f"      Delete confirmation page found")

        workflow['steps'] = [
            {'action': 'create', 'description': 'Fill form to create new catalog item'},
            {'action': 'edit', 'description': 'Modify existing catalog item'},
            {'action': 'details', 'description': 'View catalog item details'},
            {'action': 'delete', 'description': 'Delete catalog item with confirmation'}
        ]

        self.workflows['catalog-crud'] = workflow

    def discover_static_pages(self, page: Page):
        """Discover static/informational pages"""
        print("\n=== Static Pages Workflow ===")
        workflow = {
            'name': 'static-pages',
            'description': 'Static and informational pages',
            'pages': [],
            'screenshots': []
        }

        # Check for common static page links
        page.goto(self.base_url, wait_until='networkidle')

        print("   Searching for static page links...")
        static_links = page.evaluate('''() => {
            const links = document.querySelectorAll('a[href]');
            const staticPatterns = ['about', 'help', 'contact', 'privacy', 'terms', 'home', 'index'];
            const found = [];

            links.forEach(link => {
                const href = link.getAttribute('href') || '';
                const text = link.textContent?.trim() || '';
                const lowerHref = href.toLowerCase();
                const lowerText = text.toLowerCase();

                if (staticPatterns.some(p => lowerHref.includes(p) || lowerText.includes(p))) {
                    if (!found.find(f => f.href === href)) {
                        found.push({
                            href: href,
                            text: text,
                            fullUrl: link.href
                        });
                    }
                }
            });

            return found;
        }''')

        print(f"   Found {len(static_links)} potential static pages")

        # Visit each static page
        for idx, link in enumerate(static_links[:5]):  # Limit to 5
            try:
                print(f"   Visiting: {link['text']} ({link['href']})")
                page.goto(link['fullUrl'], wait_until='networkidle')
                page.wait_for_timeout(1000)

                screenshot = self.capture_screenshot(page, 'static-pages', f"page_{idx}_{link['text'].replace(' ', '_')[:20]}")

                page_info = {
                    'title': page.title(),
                    'url': page.url,
                    'href': link['href'],
                    'link_text': link['text'],
                    'screenshot': screenshot
                }
                workflow['pages'].append(page_info)
                workflow['screenshots'].append(screenshot)

            except Exception as e:
                print(f"      Warning: Could not visit {link['href']}: {e}")

        workflow['steps'] = [
            {'action': 'navigate', 'description': f'Visit {len(workflow["pages"])} static/info pages'}
        ]

        self.workflows['static-pages'] = workflow

    def save_results(self):
        """Save all workflow results"""
        print("\n=== Saving Results ===")

        for workflow_name, workflow_data in self.workflows.items():
            workflow_dir = self.output_dir / workflow_name
            workflow_file = workflow_dir / 'workflow.json'

            with open(workflow_file, 'w', encoding='utf-8') as f:
                json.dump(workflow_data, f, indent=2, ensure_ascii=False)
            print(f"   Saved: {workflow_file}")

            # Generate workflow-specific markdown
            self._generate_workflow_markdown(workflow_name, workflow_data)

        # Generate consolidated index
        self._generate_consolidated_index()

    def _generate_workflow_markdown(self, name: str, data: dict):
        """Generate markdown documentation for a workflow"""
        md_file = self.output_dir / name / 'README.md'

        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(f"# {data.get('description', name)}\n\n")
            f.write(f"**Workflow**: `{name}`\n")
            f.write(f"**Discovery Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            # Screenshots
            if data.get('screenshots'):
                f.write(f"## Screenshots\n\n")
                for screenshot in data['screenshots']:
                    f.write(f"- [`{screenshot}`](screenshots/{screenshot})\n")
                f.write("\n")

            # Steps
            if data.get('steps'):
                f.write(f"## Workflow Steps\n\n")
                for idx, step in enumerate(data['steps'], 1):
                    f.write(f"{idx}. **{step.get('action', 'action')}**: {step.get('description', '')}\n")
                f.write("\n")

            # Data/Forms
            if data.get('data'):
                f.write(f"## Captured Data\n\n")
                f.write(f"```json\n{json.dumps(data['data'], indent=2)}\n```\n\n")

            if data.get('forms'):
                f.write(f"## Forms\n\n")
                for form_type, form_data in data['forms'].items():
                    f.write(f"### {form_type.title()} Form\n\n")
                    f.write(f"- **URL**: `{form_data.get('url', 'N/A')}`\n")
                    if 'fields' in form_data:
                        f.write(f"- **Fields**: {len(form_data['fields'])}\n\n")
                        if form_data['fields']:
                            f.write("| Field | Type | Required |\n")
                            f.write("|-------|------|----------|\n")
                            for field in form_data['fields'][:20]:  # Limit display
                                name = field.get('name') or field.get('label', 'N/A')
                                ftype = field.get('type', 'N/A')
                                required = 'Yes' if field.get('required') else 'No'
                                f.write(f"| {name} | {ftype} | {required} |\n")
                    f.write("\n")

            if data.get('pages'):
                f.write(f"## Pages Discovered\n\n")
                for page_info in data['pages']:
                    f.write(f"- **{page_info['title']}** - `{page_info['url']}`\n")
                    f.write(f"  - Screenshot: `{page_info['screenshot']}`\n")
                f.write("\n")

        print(f"   Saved: {md_file}")

    def _generate_consolidated_index(self):
        """Generate consolidated index of all workflows"""
        index_file = self.output_dir / 'INDEX.md'

        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(f"# Legacy Application - Workflow Discovery Index\n\n")
            f.write(f"**Base URL**: {self.base_url}\n")
            f.write(f"**Discovery Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Total Workflows**: {len(self.workflows)}\n")
            f.write(f"**Total Screenshots**: {self.screenshot_counter}\n\n")

            f.write(f"## Discovered Workflows\n\n")

            for workflow_name, workflow_data in self.workflows.items():
                f.write(f"### {workflow_name}\n\n")
                f.write(f"**Description**: {workflow_data.get('description', 'N/A')}\n\n")
                f.write(f"**Location**: [`{workflow_name}/`]({workflow_name}/README.md)\n\n")
                f.write(f"**Screenshots**: {len(workflow_data.get('screenshots', []))}\n\n")

                if workflow_data.get('steps'):
                    f.write(f"**Key Steps**:\n")
                    for step in workflow_data['steps']:
                        f.write(f"- {step.get('description', '')}\n")
                    f.write("\n")

            f.write(f"\n## Workflow Details\n\n")
            f.write(f"For detailed information about each workflow, see:\n\n")
            for workflow_name in self.workflows.keys():
                f.write(f"- [{workflow_name}]({workflow_name}/README.md)\n")

        print(f"   Saved: {index_file}")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Workflow-Specific Browser Discovery')
    parser.add_argument('--url', required=True, help='Base URL of legacy application')
    parser.add_argument('--output', required=True, help='Output directory')
    parser.add_argument('--workflows', nargs='+',
                       default=['catalog-list', 'catalog-crud', 'static-pages'],
                       help='Workflows to discover')

    args = parser.parse_args()

    print(f"\n{'='*60}")
    print(f"  Legacy Application Workflow Discovery")
    print(f"{'='*60}")
    print(f"  URL: {args.url}")
    print(f"  Output: {args.output}")
    print(f"  Workflows: {', '.join(args.workflows)}")
    print(f"{'='*60}\n")

    discovery = WorkflowDiscovery(args.url, args.output)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        try:
            # Discover each requested workflow
            if 'catalog-list' in args.workflows:
                discovery.discover_catalog_list(page)

            if 'catalog-crud' in args.workflows:
                discovery.discover_catalog_crud(page)

            if 'static-pages' in args.workflows:
                discovery.discover_static_pages(page)

            # Save all results
            discovery.save_results()

            print(f"\n{'='*60}")
            print(f"  Discovery Complete!")
            print(f"{'='*60}")
            print(f"  Results: {args.output}")
            print(f"  Index: {args.output}/INDEX.md")
            print(f"{'='*60}\n")

        finally:
            browser.close()


if __name__ == '__main__':
    main()
