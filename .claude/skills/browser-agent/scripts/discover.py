#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Browser Agent - Discovery Mode (Python)
Automated UI workflow discovery and golden baseline capture
"""

import json
import os
import sys
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Set
from urllib.parse import urlparse, urljoin

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

try:
    from playwright.sync_api import sync_playwright, Page, Browser, ElementHandle
except ImportError:
    print("[ERROR] Playwright not installed. Installing...")
    os.system(f"{sys.executable} -m pip install playwright")
    os.system(f"{sys.executable} -m playwright install chromium")
    from playwright.sync_api import sync_playwright, Page, Browser, ElementHandle


@dataclass
class UIElement:
    """Represents a discovered UI element"""
    type: str
    selector: str
    text: str
    tag: str
    attributes: Dict[str, str]
    bounding_box: Optional[Dict[str, float]]
    visible: bool


@dataclass
class WorkflowStep:
    """Represents a step in a workflow"""
    action: str
    target: Optional[str]
    value: Optional[str]
    description: str
    timestamp: str


@dataclass
class Workflow:
    """Represents a discovered workflow"""
    name: str
    url: str
    steps: List[WorkflowStep]
    screenshots: List[str]
    elements: List[UIElement]


class BrowserAgent:
    """Automated browser agent for UI discovery"""

    def __init__(self, base_url: str, output_dir: str, max_depth: int = 3):
        self.base_url = base_url.rstrip('/')
        self.output_dir = Path(output_dir)
        self.max_depth = max_depth
        self.visited_urls: Set[str] = set()
        self.workflows: List[Workflow] = []
        self.screenshot_counter = 0

        # Create output directories
        self.screenshots_dir = self.output_dir / "screenshots"
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)

        print(f"[INIT] Browser Agent initialized")
        print(f"   Base URL: {self.base_url}")
        print(f"   Output: {self.output_dir}")
        print(f"   Max depth: {self.max_depth}")

    def discover(self, page: Page) -> List[Workflow]:
        """Main discovery entry point"""
        print(f"\n[SEARCH] Starting discovery from {self.base_url}")
        self._explore_page(page, self.base_url, [], 0)
        print(f"\n[OK] Discovery complete! Found {len(self.workflows)} workflows")
        return self.workflows

    def _explore_page(self, page: Page, url: str, path: List[WorkflowStep], depth: int):
        """Recursively explore pages"""
        if depth > self.max_depth:
            print(f"   [WARN] Max depth reached at {url}")
            return

        if url in self.visited_urls:
            print(f"   [SKIP] Already visited {url}")
            return

        self.visited_urls.add(url)
        print(f"\n{'  ' * depth}[PAGE] Exploring: {url} (depth: {depth})")

        try:
            # Navigate to page
            page.goto(url, wait_until="networkidle", timeout=30000)
            page.wait_for_timeout(1000)  # Additional wait for dynamic content

            # Capture screenshot
            screenshot_name = f"screen_{self.screenshot_counter:03d}_depth{depth}.png"
            screenshot_path = self.screenshots_dir / screenshot_name
            page.screenshot(path=str(screenshot_path), full_page=True)
            self.screenshot_counter += 1
            print(f"{'  ' * depth}[SCREENSHOT] Screenshot: {screenshot_name}")

            # Discover elements
            elements = self._discover_elements(page)
            print(f"{'  ' * depth}[SEARCH] Found {len(elements)} elements")

            # Create workflow for this page
            workflow = Workflow(
                name=self._get_page_title(page, url),
                url=url,
                steps=path.copy(),
                screenshots=[screenshot_name],
                elements=elements
            )
            self.workflows.append(workflow)

            # Explore clickable elements (limited by depth)
            if depth < self.max_depth:
                clickable = [e for e in elements if e.type in ('button', 'link')]
                print(f"{'  ' * depth}[CLICK] Found {len(clickable)} clickable elements")

                for element in clickable[:10]:  # Limit to 10 per page to avoid explosion
                    self._try_click_and_explore(page, element, path, depth, url)

        except Exception as e:
            print(f"{'  ' * depth}[ERROR] Error exploring {url}: {e}")

    def _try_click_and_explore(self, page: Page, element: UIElement,
                               path: List[WorkflowStep], depth: int, current_url: str):
        """Try clicking an element and exploring the result"""
        if not element.visible or element.selector == 'element':
            return

        try:
            # Create workflow step
            step = WorkflowStep(
                action='click',
                target=element.selector,
                value=None,
                description=f"Click '{element.text[:50]}'",
                timestamp=datetime.now().isoformat()
            )

            # Try to click
            page.click(element.selector, timeout=2000)
            page.wait_for_timeout(1000)

            new_url = page.url

            # If URL changed, explore new page
            if new_url != current_url and not self._is_excluded_url(new_url):
                new_path = path + [step]
                self._explore_page(page, new_url, new_path, depth + 1)

                # Navigate back
                page.go_back(wait_until="networkidle")
                page.wait_for_timeout(500)

        except Exception as e:
            # Silently skip elements that can't be clicked
            pass

    def _discover_elements(self, page: Page) -> List[UIElement]:
        """Discover all interactive elements on the page"""
        elements = []

        # Buttons
        for button in page.query_selector_all('button, input[type="submit"], input[type="button"]'):
            element = self._create_ui_element(button, 'button')
            if element:
                elements.append(element)

        # Links
        for link in page.query_selector_all('a[href]'):
            element = self._create_ui_element(link, 'link')
            if element:
                elements.append(element)

        # Form inputs
        for input_elem in page.query_selector_all('input:not([type="submit"]):not([type="button"]), textarea, select'):
            input_type = input_elem.get_attribute('type') or 'text'
            element = self._create_ui_element(input_elem, f'input_{input_type}')
            if element:
                elements.append(element)

        # Tables/Grids
        for idx, table in enumerate(page.query_selector_all('table, [class*="grid"], [class*="datagrid"]')):
            element = self._create_ui_element(table, 'table')
            if element:
                element.text = f"Table {idx + 1}"
                elements.append(element)

        return elements

    def _create_ui_element(self, handle: ElementHandle, elem_type: str) -> Optional[UIElement]:
        """Create UIElement from element handle"""
        try:
            tag = handle.evaluate('el => el.tagName.toLowerCase()')
            text = handle.text_content() or ''
            visible = handle.is_visible()

            # Get attributes
            attributes = handle.evaluate('''el => {
                const attrs = {};
                for (const attr of el.attributes) {
                    attrs[attr.name] = attr.value;
                }
                return attrs;
            }''')

            # Get bounding box
            bbox = handle.bounding_box()

            # Generate selector
            selector = self._generate_selector(handle, attributes, text)

            return UIElement(
                type=elem_type,
                selector=selector,
                text=text.strip()[:100],
                tag=tag,
                attributes=attributes,
                bounding_box=bbox,
                visible=visible
            )
        except Exception:
            return None

    def _generate_selector(self, handle: ElementHandle, attributes: Dict[str, str], text: str) -> str:
        """Generate a reliable CSS selector"""
        # Try ID
        if 'id' in attributes and attributes['id']:
            return f"#{attributes['id']}"

        # Try name
        if 'name' in attributes and attributes['name']:
            return f"[name='{attributes['name']}']"

        # Try data-testid
        if 'data-testid' in attributes:
            return f"[data-testid='{attributes['data-testid']}']"

        # Try aria-label
        if 'aria-label' in attributes:
            return f"[aria-label='{attributes['aria-label']}']"

        # Try class if unique enough
        if 'class' in attributes and attributes['class']:
            classes = attributes['class'].split()
            if len(classes) <= 3:
                return f".{'.'.join(classes)}"

        # Fallback to text content for buttons/links
        if text and len(text.strip()) > 0 and len(text.strip()) < 30:
            tag = handle.evaluate('el => el.tagName.toLowerCase()')
            escaped_text = text.strip().replace('"', '\\"')
            return f'{tag}:has-text("{escaped_text}")'

        return 'element'

    def _get_page_title(self, page: Page, url: str) -> str:
        """Get a meaningful page title"""
        title = page.title()
        if title and title.strip():
            return title.strip()

        # Extract from URL
        parsed = urlparse(url)
        path = parsed.path.strip('/')
        if path:
            return path.replace('/', '_')

        return 'home'

    def _is_excluded_url(self, url: str) -> bool:
        """Check if URL should be excluded"""
        excluded_patterns = ['logout', 'delete', 'admin', 'signout', 'remove']
        url_lower = url.lower()
        return any(pattern in url_lower for pattern in excluded_patterns)

    def save_results(self):
        """Save discovery results to disk"""
        print(f"\n[SAVE] Saving results to {self.output_dir}")

        # Save workflows
        workflows_data = [
            {
                'name': w.name,
                'url': w.url,
                'steps': [asdict(s) for s in w.steps],
                'screenshots': w.screenshots,
                'element_count': len(w.elements)
            }
            for w in self.workflows
        ]
        workflows_path = self.output_dir / "workflows.json"
        with open(workflows_path, 'w', encoding='utf-8') as f:
            json.dump(workflows_data, f, indent=2, ensure_ascii=False)
        print(f"   [OK] Workflows: {workflows_path}")

        # Save all elements
        all_elements = []
        for workflow in self.workflows:
            for element in workflow.elements:
                all_elements.append({
                    'workflow': workflow.name,
                    'url': workflow.url,
                    **asdict(element)
                })
        elements_path = self.output_dir / "ui-elements.json"
        with open(elements_path, 'w', encoding='utf-8') as f:
            json.dump(all_elements, f, indent=2, ensure_ascii=False)
        print(f"   [OK] Elements: {elements_path}")

        # Generate baseline index
        self._generate_baseline_index()

    def _generate_baseline_index(self):
        """Generate human-readable baseline index"""
        index_path = self.output_dir / "BASELINE_INDEX.md"

        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(f"# Legacy UI Golden Baseline\n\n")
            f.write(f"**Base URL**: {self.base_url}\n")
            f.write(f"**Discovery Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Total Workflows**: {len(self.workflows)}\n")
            f.write(f"**Total Screenshots**: {self.screenshot_counter}\n\n")

            f.write(f"## Discovered Workflows\n\n")

            for idx, workflow in enumerate(self.workflows, 1):
                f.write(f"### {idx}. {workflow.name}\n\n")
                f.write(f"- **URL**: `{workflow.url}`\n")
                f.write(f"- **Screenshots**: {', '.join(workflow.screenshots)}\n")
                f.write(f"- **Elements**: {len(workflow.elements)}\n")

                if workflow.steps:
                    f.write(f"- **Navigation Path**:\n")
                    for step in workflow.steps:
                        f.write(f"  - {step.description}\n")

                # Element summary
                element_types = {}
                for elem in workflow.elements:
                    element_types[elem.type] = element_types.get(elem.type, 0) + 1

                f.write(f"- **Element Breakdown**:\n")
                for elem_type, count in sorted(element_types.items()):
                    f.write(f"  - {elem_type}: {count}\n")

                f.write(f"\n")

            f.write(f"\n## Screenshots Index\n\n")
            f.write(f"All screenshots are saved in `screenshots/` directory.\n\n")
            for workflow in self.workflows:
                for screenshot in workflow.screenshots:
                    f.write(f"- `{screenshot}` - {workflow.name}\n")

        print(f"   [OK] Baseline Index: {index_path}")

    def capture_grid_data(self, page: Page):
        """Capture data from all tables/grids"""
        print(f"\n[DATA] Capturing grid data...")
        grid_data = []

        tables = page.query_selector_all('table, [class*="grid"]')
        for idx, table in enumerate(tables):
            try:
                data = page.evaluate('''(element) => {
                    const headers = [];
                    const rows = [];

                    // Extract headers
                    const headerCells = element.querySelectorAll('th');
                    headerCells.forEach(cell => headers.push(cell.textContent?.trim() || ''));

                    // Extract rows (limit to 10)
                    const dataRows = element.querySelectorAll('tbody tr');
                    for (let i = 0; i < Math.min(10, dataRows.length); i++) {
                        const row = [];
                        const cells = dataRows[i].querySelectorAll('td');
                        cells.forEach(cell => row.push(cell.textContent?.trim() || ''));
                        rows.push(row);
                    }

                    return {
                        headers: headers,
                        rows: rows,
                        totalRows: dataRows.length
                    };
                }''', table)

                if data and (data['headers'] or data['rows']):
                    grid_data.append({
                        'tableIndex': idx,
                        'url': page.url,
                        **data
                    })
                    print(f"   [OK] Table {idx + 1}: {len(data['rows'])} rows")

            except Exception as e:
                print(f"   [WARN] Could not capture table {idx + 1}: {e}")

        if grid_data:
            grid_path = self.output_dir / "grid-data.json"
            with open(grid_path, 'w', encoding='utf-8') as f:
                json.dump(grid_data, f, indent=2, ensure_ascii=False)
            print(f"   [OK] Grid data saved: {grid_path}")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Browser Agent - UI Discovery')
    parser.add_argument('--url', required=True, help='Base URL to explore')
    parser.add_argument('--output', required=True, help='Output directory')
    parser.add_argument('--max-depth', type=int, default=3, help='Maximum exploration depth')
    parser.add_argument('--capture-grids', action='store_true', help='Capture grid/table data')

    args = parser.parse_args()

    agent = BrowserAgent(
        base_url=args.url,
        output_dir=args.output,
        max_depth=args.max_depth
    )

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        try:
            # Run discovery
            agent.discover(page)

            # Capture grid data if requested
            if args.capture_grids:
                page.goto(args.url, wait_until="networkidle")
                agent.capture_grid_data(page)

            # Save results
            agent.save_results()

            print(f"\n[OK] Discovery complete!")
            print(f"[FOLDER] Results saved to: {args.output}")
            print(f"[SCREENSHOT] Screenshots: {args.output}/screenshots/")
            print(f"[PAGE] Index: {args.output}/BASELINE_INDEX.md")

        finally:
            browser.close()


if __name__ == '__main__':
    main()
