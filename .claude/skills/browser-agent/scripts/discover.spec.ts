/**
 * Browser Agent - Discovery Mode
 * Auto-generated Playwright test for UI workflow discovery
 */

import { test, expect, Page, ElementHandle } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

interface UIElement {
  type: string;
  selector: string;
  text: string;
  boundingBox: { x: number; y: number; width: number; height: number } | null;
  attributes?: Record<string, string>;
}

interface WorkflowStep {
  action: 'navigate' | 'click' | 'fill' | 'wait';
  target?: string;
  value?: string;
  description: string;
  url?: string;
  timestamp: string;
}

interface Workflow {
  id: string;
  name: string;
  steps: WorkflowStep[];
  screenshots: string[];
  startUrl: string;
  endUrl: string;
  duration: number;
}

interface DiscoveryConfig {
  maxDepth: number;
  maxDurationMs: number;
  screenshotFormat: 'png' | 'jpeg';
  fullPageScreenshots: boolean;
  waitForNetworkIdle: boolean;
  excludePatterns: string[];
}

class BrowserAgent {
  private page: Page;
  private baseUrl: string;
  private outputDir: string;
  private visitedUrls: Set<string> = new Set();
  private workflows: Workflow[] = [];
  private allElements: Map<string, UIElement[]> = new Map();
  private config: DiscoveryConfig;
  private startTime: number = Date.now();

  constructor(page: Page, baseUrl: string, outputDir: string, config: DiscoveryConfig) {
    this.page = page;
    this.baseUrl = baseUrl;
    this.outputDir = outputDir;
    this.config = config;
  }

  async discoverWorkflows(maxDepth: number = 3): Promise<Workflow[]> {
    console.log(`🚀 Starting UI discovery from: ${this.baseUrl}`);
    console.log(`📊 Max depth: ${maxDepth}, Timeout: ${this.config.maxDurationMs}ms`);

    await this.explorePage(this.baseUrl, [], 0, maxDepth, 'Root');

    console.log(`✅ Discovery complete. Found ${this.workflows.length} workflows`);
    return this.workflows;
  }

  private async explorePage(
    url: string,
    path: WorkflowStep[],
    depth: number,
    maxDepth: number,
    workflowName: string
  ): Promise<void> {
    // Check timeout
    if (Date.now() - this.startTime > this.config.maxDurationMs) {
      console.log('⏱️  Max duration reached, stopping discovery');
      return;
    }

    // Check depth and visited
    if (depth > maxDepth || this.visitedUrls.has(url)) {
      return;
    }

    // Check exclude patterns
    if (this.config.excludePatterns.some(pattern => url.includes(pattern))) {
      console.log(`⏭️  Skipping excluded URL: ${url}`);
      return;
    }

    this.visitedUrls.add(url);
    console.log(`📍 [Depth ${depth}] Exploring: ${url}`);

    try {
      // Navigate to page
      const waitOption = this.config.waitForNetworkIdle ? 'networkidle' : 'load';
      await this.page.goto(url, { waitUntil: waitOption as any, timeout: 30000 });
      await this.page.waitForTimeout(1000); // Additional settle time

      // Capture screenshot
      const screenshotName = `screen_${this.workflows.length}_depth${depth}_${Date.now()}.${this.config.screenshotFormat}`;
      const screenshotPath = path.join(this.outputDir, 'screenshots', screenshotName);
      await this.page.screenshot({
        path: screenshotPath,
        fullPage: this.config.fullPageScreenshots
      });

      // Discover elements
      const elements = await this.discoverElements();
      this.allElements.set(url, elements);

      // Log element counts
      console.log(`  Found: ${elements.filter(e => e.type === 'button').length} buttons, ` +
                  `${elements.filter(e => e.type === 'link').length} links, ` +
                  `${elements.filter(e => e.type.startsWith('input')).length} inputs, ` +
                  `${elements.filter(e => e.type === 'table').length} tables`);

      // Save elements for this page
      const elementsPath = path.join(this.outputDir, `elements_${url.replace(/[^a-z0-9]/gi, '_')}.json`);
      fs.writeFileSync(elementsPath, JSON.stringify(elements, null, 2));

      // Record workflow up to this point
      if (path.length > 0) {
        this.workflows.push({
          id: `workflow_${this.workflows.length}`,
          name: workflowName,
          steps: path,
          screenshots: [screenshotName],
          startUrl: this.baseUrl,
          endUrl: url,
          duration: Date.now() - this.startTime
        });
      }

      // Explore clickable elements (buttons and links)
      const clickableElements = elements.filter(e =>
        e.type === 'button' || e.type === 'link'
      ).slice(0, 10); // Limit to first 10 to avoid explosion

      for (const element of clickableElements) {
        if (depth < maxDepth && Date.now() - this.startTime < this.config.maxDurationMs) {
          try {
            const newPath = [...path, {
              action: 'click' as const,
              target: element.selector,
              description: `Click "${element.text.substring(0, 50)}"`,
              url: url,
              timestamp: new Date().toISOString()
            }];

            const newWorkflowName = `${workflowName} → ${element.text.substring(0, 30)}`;

            // Try to click
            await this.page.click(element.selector, { timeout: 5000 });
            await this.page.waitForTimeout(500);

            // Check if URL changed
            const newUrl = this.page.url();
            if (newUrl !== url) {
              console.log(`  ↳ Navigated to: ${newUrl}`);
              await this.explorePage(newUrl, newPath, depth + 1, maxDepth, newWorkflowName);

              // Go back
              await this.page.goBack({ waitUntil: 'load', timeout: 10000 });
              await this.page.waitForTimeout(500);
            }
          } catch (error: any) {
            console.log(`  ⚠️  Could not click ${element.selector}: ${error.message}`);
          }
        }
      }

      // Capture grid data if tables present
      const tables = elements.filter(e => e.type === 'table');
      if (tables.length > 0) {
        await this.captureAllGridData(url);
      }

    } catch (error: any) {
      console.error(`  ❌ Error exploring ${url}: ${error.message}`);
    }
  }

  private async discoverElements(): Promise<UIElement[]> {
    const elements: UIElement[] = [];

    try {
      // Buttons
      const buttons = await this.page.$$('button, input[type="submit"], input[type="button"], [role="button"]');
      for (const button of buttons) {
        try {
          if (await button.isVisible()) {
            const text = (await button.textContent() || await button.getAttribute('value') || '').trim();
            const boundingBox = await button.boundingBox();
            const selector = await this.generateSelector(button);
            const attributes = await this.getElementAttributes(button);

            elements.push({
              type: 'button',
              selector,
              text: text.substring(0, 100),
              boundingBox,
              attributes
            });
          }
        } catch (err) {
          // Skip elements that cause errors
        }
      }

      // Links
      const links = await this.page.$$('a[href]');
      for (const link of links) {
        try {
          if (await link.isVisible()) {
            const text = (await link.textContent() || '').trim();
            const href = await link.getAttribute('href') || '';
            const boundingBox = await link.boundingBox();
            const selector = await this.generateSelector(link);

            elements.push({
              type: 'link',
              selector,
              text: text.substring(0, 100),
              boundingBox,
              attributes: { href }
            });
          }
        } catch (err) {
          // Skip elements that cause errors
        }
      }

      // Form fields
      const inputs = await this.page.$$('input:not([type="submit"]):not([type="button"]), textarea, select');
      for (const input of inputs) {
        try {
          if (await input.isVisible()) {
            const type = await input.getAttribute('type') || 'text';
            const name = await input.getAttribute('name') || '';
            const id = await input.getAttribute('id') || '';
            const placeholder = await input.getAttribute('placeholder') || '';
            const boundingBox = await input.boundingBox();
            const selector = await this.generateSelector(input);

            elements.push({
              type: `input_${type}`,
              selector,
              text: name || id || placeholder,
              boundingBox,
              attributes: { type, name, id, placeholder }
            });
          }
        } catch (err) {
          // Skip elements that cause errors
        }
      }

      // Tables/Grids
      const tables = await this.page.$$('table, [class*="grid" i], [class*="datagrid" i], [role="grid"]');
      for (let i = 0; i < tables.length; i++) {
        try {
          const boundingBox = await tables[i].boundingBox();
          const selector = `table:nth-of-type(${i + 1})`;
          const rowCount = await tables[i].$$('tr').then(rows => rows.length);

          elements.push({
            type: 'table',
            selector,
            text: `Table ${i + 1} (${rowCount} rows)`,
            boundingBox,
            attributes: { rowCount: rowCount.toString() }
          });
        } catch (err) {
          // Skip elements that cause errors
        }
      }

      // Navigation menus
      const navs = await this.page.$$('nav, [role="navigation"], [class*="menu" i], [class*="navbar" i]');
      for (let i = 0; i < navs.length; i++) {
        try {
          const boundingBox = await navs[i].boundingBox();
          const text = await navs[i].textContent() || '';
          const selector = `nav:nth-of-type(${i + 1})`;

          elements.push({
            type: 'navigation',
            selector,
            text: text.trim().substring(0, 100),
            boundingBox
          });
        } catch (err) {
          // Skip elements that cause errors
        }
      }

    } catch (error: any) {
      console.error(`Error discovering elements: ${error.message}`);
    }

    return elements;
  }

  private async getElementAttributes(element: ElementHandle): Promise<Record<string, string>> {
    return await element.evaluate(el => {
      const attrs: Record<string, string> = {};
      ['id', 'name', 'class', 'type', 'value', 'placeholder', 'aria-label', 'data-testid'].forEach(attr => {
        const value = el.getAttribute(attr);
        if (value) attrs[attr] = value;
      });
      return attrs;
    });
  }

  private async generateSelector(element: ElementHandle): Promise<string> {
    try {
      // Try ID first
      const id = await element.getAttribute('id');
      if (id) return `#${id}`;

      // Try data-testid
      const testId = await element.getAttribute('data-testid');
      if (testId) return `[data-testid="${testId}"]`;

      // Try name
      const name = await element.getAttribute('name');
      if (name) return `[name="${name}"]`;

      // Try aria-label
      const ariaLabel = await element.getAttribute('aria-label');
      if (ariaLabel) return `[aria-label="${ariaLabel}"]`;

      // Try text content for buttons/links
      const text = await element.textContent();
      if (text && text.trim()) {
        const tagName = await element.evaluate(el => el.tagName.toLowerCase());
        const cleanText = text.trim().replace(/"/g, '\\"').substring(0, 30);
        if (cleanText) {
          return `${tagName}:has-text("${cleanText}")`;
        }
      }

      // Last resort: generate a complex selector
      return await element.evaluate(el => {
        const tagName = el.tagName.toLowerCase();
        const classes = el.className ? `.${el.className.split(' ').join('.')}` : '';
        return `${tagName}${classes}`;
      });
    } catch (error) {
      return 'unknown-element';
    }
  }

  private async captureAllGridData(url: string): Promise<void> {
    try {
      const tables = await this.page.$$('table, [role="grid"]');
      const gridData = [];

      for (let i = 0; i < tables.length; i++) {
        const data = await this.captureGridData(`table:nth-of-type(${i + 1})`);
        if (data && data.rows.length > 0) {
          gridData.push({ tableIndex: i, url, ...data });
        }
      }

      if (gridData.length > 0) {
        const gridDataPath = path.join(
          this.outputDir,
          `grid-data_${url.replace(/[^a-z0-9]/gi, '_')}.json`
        );
        fs.writeFileSync(gridDataPath, JSON.stringify(gridData, null, 2));
        console.log(`  💾 Saved data from ${gridData.length} grids`);
      }
    } catch (error: any) {
      console.error(`Error capturing grid data: ${error.message}`);
    }
  }

  async captureGridData(tableSelector: string): Promise<any> {
    try {
      const data = await this.page.evaluate((selector) => {
        const table = document.querySelector(selector);
        if (!table) return null;

        const headers: string[] = [];
        const rows: string[][] = [];

        // Extract headers
        const headerCells = table.querySelectorAll('th');
        headerCells.forEach(cell => headers.push(cell.textContent?.trim() || ''));

        // If no th, try first tr
        if (headers.length === 0) {
          const firstRow = table.querySelector('tr');
          if (firstRow) {
            firstRow.querySelectorAll('td').forEach(cell =>
              headers.push(cell.textContent?.trim() || '')
            );
          }
        }

        // Extract rows (limit to 10)
        const dataRows = table.querySelectorAll('tbody tr, tr');
        const startIdx = headers.length > 0 && table.querySelectorAll('tbody tr').length === 0 ? 1 : 0;

        for (let i = startIdx; i < Math.min(startIdx + 10, dataRows.length); i++) {
          const row: string[] = [];
          const cells = dataRows[i].querySelectorAll('td, th');
          cells.forEach(cell => row.push(cell.textContent?.trim() || ''));
          if (row.length > 0) rows.push(row);
        }

        return {
          headers,
          rows,
          totalRows: dataRows.length - startIdx
        };
      }, tableSelector);

      return data;
    } catch (error: any) {
      console.error(`Error extracting grid data: ${error.message}`);
      return null;
    }
  }

  getDiscoverySummary() {
    return {
      totalWorkflows: this.workflows.length,
      totalPages: this.visitedUrls.size,
      totalElements: Array.from(this.allElements.values()).reduce((sum, els) => sum + els.length, 0),
      duration: Date.now() - this.startTime,
      visitedUrls: Array.from(this.visitedUrls)
    };
  }
}

// Load config
const configPath = path.join(__dirname, '..', 'config.json');
let config: DiscoveryConfig = {
  maxDepth: 3,
  maxDurationMs: 300000,
  screenshotFormat: 'png',
  fullPageScreenshots: true,
  waitForNetworkIdle: true,
  excludePatterns: ['*/logout', '*/delete/*', '*/admin/*']
};

if (fs.existsSync(configPath)) {
  const fileConfig = JSON.parse(fs.readFileSync(configPath, 'utf-8'));
  config = { ...config, ...fileConfig.discovery };
}

// Main test suite
test.describe('UI Discovery', () => {
  test('discover all workflows', async ({ page }) => {
    const baseUrl = process.env.APP_URL || 'http://localhost:8080';
    const outputDir = process.env.OUTPUT_DIR || './legacy-golden/discovery';
    const maxDepth = parseInt(process.env.MAX_DEPTH || '3');

    // Ensure output directories exist
    fs.mkdirSync(path.join(outputDir, 'screenshots'), { recursive: true });

    const agent = new BrowserAgent(page, baseUrl, outputDir, config);
    const workflows = await agent.discoverWorkflows(maxDepth);

    // Save workflows
    const workflowsPath = path.join(outputDir, 'workflows.json');
    fs.writeFileSync(workflowsPath, JSON.stringify(workflows, null, 2));

    // Save summary
    const summary = agent.getDiscoverySummary();
    const summaryPath = path.join(outputDir, 'discovery-summary.json');
    fs.writeFileSync(summaryPath, JSON.stringify(summary, null, 2));

    console.log('\n📊 Discovery Summary:');
    console.log(`  Workflows: ${summary.totalWorkflows}`);
    console.log(`  Pages: ${summary.totalPages}`);
    console.log(`  Elements: ${summary.totalElements}`);
    console.log(`  Duration: ${(summary.duration / 1000).toFixed(1)}s`);
    console.log(`\n✅ Results saved to: ${outputDir}`);

    expect(workflows.length).toBeGreaterThan(0);
  });
});
