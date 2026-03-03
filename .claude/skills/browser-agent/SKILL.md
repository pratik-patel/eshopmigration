---
name: browser-agent
description: Automated browser agent using Playwright for pixel-level visual comparison, structural element verification, CSS class matching, and workflow parity testing between legacy and modern applications.
disable-model-invocation: false
context: fork
agent: general-purpose
---

# Browser Agent — UI Discovery & Pixel-Level Parity Verification

Automated browser testing agent for:
1. **Discovery mode**: Capture legacy UI workflows and screenshots for golden baseline
2. **Verification mode**: Pixel-level comparison of legacy vs modern UI including:
   - Screenshot pixel diffing with highlighted changes
   - Structural element verification (headers, footers, nav, forms)
   - CSS class matching
   - Interactive element count comparison
   - Data grid content validation
   - Workflow execution parity

**Arguments:** `[discovery|verify] <app-url> [--seam <seam-name>]`

---

## Prerequisites Check

```bash
# Check if Playwright is installed
if ! command -v npx &> /dev/null; then
    echo "❌ STOP: Node.js and npx required"
    exit 1
fi

# Check if browser-agent scripts exist
test -d ".claude/skills/browser-agent/scripts" || mkdir -p ".claude/skills/browser-agent/scripts"

# Install Playwright if needed
if [ ! -d "node_modules/@playwright/test" ]; then
    echo "📦 Installing Playwright..."
    npm install --save-dev @playwright/test
    npx playwright install chromium
fi
```

---

## Mode 1: Discovery (Legacy Golden Baseline)

**Purpose**: Automatically explore the legacy application to:
- Identify all UI screens and workflows
- Capture screenshots of each state
- Document interactive elements (buttons, forms, grids, charts)
- Record user journeys and navigation paths
- Extract data samples from grids/tables

**Usage**: `/browser-agent discovery http://localhost:8080`

**Output**:
- `docs/legacy-golden/<seam>/screenshots/*.png` — UI state captures
- `docs/legacy-golden/<seam>/workflows.json` — Discovered user journeys
- `docs/legacy-golden/<seam>/ui-elements.json` — Interactive element inventory
- `docs/legacy-golden/<seam>/BASELINE_INDEX.md` — Summary index

### Discovery Algorithm

1. **Initial Page Load**
   - Load application root URL
   - Wait for page to be fully loaded (networkidle)
   - Capture initial screenshot
   - Extract page title, URL, visible text

2. **Element Discovery**
   - Find all interactive elements:
     - Buttons (`button`, `input[type=submit]`, `a` with click handlers)
     - Links (`a[href]`)
     - Form fields (`input`, `select`, `textarea`)
     - Data grids/tables (`table`, `.grid`, `.datagrid`)
     - Navigation menus (`nav`, `.menu`, `.sidebar`)
   - Record element properties:
     - Type, ID, class, text content
     - Position (x, y, width, height)
     - Visibility state

3. **Workflow Exploration (Breadth-First)**
   - For each clickable element:
     - Click element
     - Wait for navigation/state change
     - Capture screenshot
     - Extract new elements
     - Record navigation path
     - Go back to parent state
   - Limit depth to avoid infinite loops (max 5 levels)
   - Track visited states to avoid duplicates

4. **Data Capture**
   - For each grid/table:
     - Extract column headers
     - Extract first 10 rows of data
     - Record pagination state
     - Capture filter/sort controls

5. **Form Interaction**
   - For each form:
     - Record field names, types, labels
     - Capture validation rules (if visible)
     - Document submit behavior

---

## Mode 2: Verification (Parity Testing)

**Purpose**: Compare legacy vs modern UI to verify:
- **Pixel-level visual consistency** (layout, colors, spacing)
- **Structural element parity** (headers, footers, nav, forms)
- **CSS class matching** (styling fidelity)
- **Interactive element completeness** (buttons, links, inputs)
- **Data accuracy** (grid contents, API responses)
- **Workflow equivalence** (same steps, same outcome)

**Usage**: `/browser-agent verify http://localhost:8080 --legacy http://old-app:8080 --modern http://localhost:5173`

**Output**:
- `docs/legacy-golden/parity-results/{seam}/VERIFICATION_SUMMARY.md` — Executive summary with parity score
- `docs/legacy-golden/parity-results/{seam}/screenshots/` — Side-by-side comparisons with pixel diffs
- `docs/legacy-golden/parity-results/{seam}/feature-matrix.md` — Element-by-element comparison
- `docs/legacy-golden/parity-results/{seam}/issues.json` — Structured discrepancy data

### Verification Algorithm

1. **Pixel-Level Screenshot Comparison**
   - Capture full-page screenshots at same viewport (1920x1080)
   - Generate pixel diff using image comparison library (Pillow/pixelmatch)
   - Calculate difference percentage
   - Highlight changed regions in red overlay
   - Save three images: `legacy.png`, `modern.png`, `diff.png`
   - **Tolerance:** 5% pixel diff acceptable (for anti-aliasing, minor rendering differences)
   - **Threshold:** >30% diff = major layout issue

2. **Structural Element Verification**
   - Verify presence of key structural elements:
     - **Header/Banner:** `.header`, `header`, `[role="banner"]`, `.navbar`
     - **Navigation:** `nav`, `.nav`, `.menu`, `[role="navigation"]`
     - **Main Content:** `main`, `[role="main"]`, `.content`, `.container`
     - **Footer:** `footer`, `[role="contentinfo"]`, `.footer`
     - **Forms:** `form`, all `input`/`select`/`textarea` elements
     - **Tables/Grids:** `table`, `.grid`, `[role="grid"]`, `.datagrid`
   - For each element type, report:
     - **Found in both:** ✅ PASS
     - **Found in legacy only:** ❌ FAIL - Missing in modern
     - **Found in modern only:** ⚠️  WARN - Extra element added

3. **CSS Class Matching**
   - Extract all CSS classes from legacy elements
   - Check if modern elements have equivalent classes
   - Special handling for legacy class patterns:
     - `.esh-*` classes (eShop legacy CSS)
     - `.btn`, `.button` classes
     - `.table`, `.grid` classes
     - `.form-control`, `.input` classes
   - Report class coverage percentage

4. **Interactive Element Count**
   - Count all interactive elements:
     - Buttons: `button`, `input[type="submit"]`, `.btn`, `[role="button"]`
     - Links: `a[href]`
     - Inputs: `input`, `textarea`, `select`
   - Compare counts (exact match not required, but within 20%)
   - Flag major discrepancies (>50% difference)

5. **Data Grid Comparison**
   - For each table/grid:
     - Extract column headers
     - Extract first 10 rows of data
     - Compare row counts
     - Compare cell values (text content)
     - **Tolerance:** Formatting differences OK (e.g., "19.50" vs "$19.50")
     - **Threshold:** >10% data difference = FAIL

6. **Workflow Parity**
   - Execute same user journey in both apps:
     - Click "Create New" button
     - Fill form fields with test data
     - Submit form
     - Verify success/error state
   - Compare outcomes:
     - Same success message
     - Same error messages
     - Same navigation destination

7. **Scoring Formula**
   ```
   parity_score = (
     feature_completeness * 0.40 +
     visual_consistency * 0.20 +
     data_accuracy * 0.30 +
     workflow_equivalence * 0.10
   ) * 100

   where:
     feature_completeness = elements_present / elements_expected
     visual_consistency = 1 - (pixel_diff_percent / 100)
     data_accuracy = matching_data_rows / total_data_rows
     workflow_equivalence = successful_workflows / total_workflows
   ```

   **Target:** 85%+ overall score

---

## Dynamic Playwright Script Generation

The skill generates framework-specific Playwright scripts based on detected UI patterns.

### Base Script Template

```typescript
// Auto-generated by browser-agent skill
import { test, expect, Page } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

interface UIElement {
  type: string;
  selector: string;
  text: string;
  boundingBox: { x: number; y: number; width: number; height: number } | null;
}

interface Workflow {
  name: string;
  steps: WorkflowStep[];
  screenshots: string[];
}

interface WorkflowStep {
  action: 'navigate' | 'click' | 'fill' | 'wait';
  target?: string;
  value?: string;
  description: string;
}

class BrowserAgent {
  private page: Page;
  private baseUrl: string;
  private outputDir: string;
  private visitedUrls: Set<string> = new Set();
  private workflows: Workflow[] = [];

  constructor(page: Page, baseUrl: string, outputDir: string) {
    this.page = page;
    this.baseUrl = baseUrl;
    this.outputDir = outputDir;
  }

  async discoverWorkflows(maxDepth: number = 5): Promise<Workflow[]> {
    await this.explorePage(this.baseUrl, [], 0, maxDepth);
    return this.workflows;
  }

  private async explorePage(
    url: string,
    path: WorkflowStep[],
    depth: number,
    maxDepth: number
  ): Promise<void> {
    if (depth > maxDepth || this.visitedUrls.has(url)) {
      return;
    }

    this.visitedUrls.add(url);
    console.log(`📍 Exploring: ${url} (depth: ${depth})`);

    await this.page.goto(url, { waitUntil: 'networkidle' });
    await this.page.waitForTimeout(1000);

    // Capture screenshot
    const screenshotName = `screen_${this.workflows.length}_${depth}.png`;
    const screenshotPath = path.join(this.outputDir, 'screenshots', screenshotName);
    await this.page.screenshot({ path: screenshotPath, fullPage: true });

    // Discover interactive elements
    const elements = await this.discoverElements();

    // Save elements
    const elementsPath = path.join(this.outputDir, `elements_${this.workflows.length}.json`);
    fs.writeFileSync(elementsPath, JSON.stringify(elements, null, 2));

    // Explore clickable elements
    for (const element of elements.filter(e => e.type === 'button' || e.type === 'link')) {
      if (depth < maxDepth) {
        try {
          const newPath = [...path, {
            action: 'click',
            target: element.selector,
            description: `Click "${element.text}"`
          }];

          // Click and explore
          await this.page.click(element.selector, { timeout: 2000 });
          await this.page.waitForTimeout(1000);

          const newUrl = this.page.url();
          if (newUrl !== url) {
            await this.explorePage(newUrl, newPath, depth + 1, maxDepth);
            await this.page.goBack();
            await this.page.waitForTimeout(500);
          }
        } catch (error) {
          console.log(`⚠️  Could not click ${element.selector}: ${error.message}`);
        }
      }
    }
  }

  private async discoverElements(): Promise<UIElement[]> {
    const elements: UIElement[] = [];

    // Buttons
    const buttons = await this.page.$$('button, input[type="submit"], input[type="button"]');
    for (const button of buttons) {
      const text = await button.textContent() || await button.getAttribute('value') || '';
      const boundingBox = await button.boundingBox();
      const selector = await this.generateSelector(button);
      elements.push({ type: 'button', selector, text: text.trim(), boundingBox });
    }

    // Links
    const links = await this.page.$$('a[href]');
    for (const link of links) {
      const text = await link.textContent() || '';
      const boundingBox = await link.boundingBox();
      const selector = await this.generateSelector(link);
      elements.push({ type: 'link', selector, text: text.trim(), boundingBox });
    }

    // Form fields
    const inputs = await this.page.$$('input:not([type="submit"]):not([type="button"]), textarea, select');
    for (const input of inputs) {
      const type = await input.getAttribute('type') || 'text';
      const name = await input.getAttribute('name') || '';
      const boundingBox = await input.boundingBox();
      const selector = await this.generateSelector(input);
      elements.push({ type: `input_${type}`, selector, text: name, boundingBox });
    }

    // Tables/Grids
    const tables = await this.page.$$('table, [class*="grid"], [class*="datagrid"]');
    for (let i = 0; i < tables.length; i++) {
      const boundingBox = await tables[i].boundingBox();
      const selector = `table:nth-of-type(${i + 1})`;
      elements.push({ type: 'table', selector, text: `Table ${i + 1}`, boundingBox });
    }

    return elements;
  }

  private async generateSelector(element: any): Promise<string> {
    // Try ID first
    const id = await element.getAttribute('id');
    if (id) return `#${id}`;

    // Try name
    const name = await element.getAttribute('name');
    if (name) return `[name="${name}"]`;

    // Try data-testid
    const testId = await element.getAttribute('data-testid');
    if (testId) return `[data-testid="${testId}"]`;

    // Try aria-label
    const ariaLabel = await element.getAttribute('aria-label');
    if (ariaLabel) return `[aria-label="${ariaLabel}"]`;

    // Fallback to text content for buttons/links
    const text = await element.textContent();
    if (text && text.trim()) {
      const tagName = await element.evaluate(el => el.tagName.toLowerCase());
      return `${tagName}:has-text("${text.trim().substring(0, 30)}")`;
    }

    // Last resort: nth-of-type
    return 'element';
  }

  async captureGridData(tableSelector: string): Promise<any> {
    const data = await this.page.evaluate((selector) => {
      const table = document.querySelector(selector);
      if (!table) return null;

      const headers: string[] = [];
      const rows: string[][] = [];

      // Extract headers
      const headerCells = table.querySelectorAll('th');
      headerCells.forEach(cell => headers.push(cell.textContent?.trim() || ''));

      // Extract rows (limit to 10)
      const dataRows = table.querySelectorAll('tbody tr');
      for (let i = 0; i < Math.min(10, dataRows.length); i++) {
        const row: string[] = [];
        const cells = dataRows[i].querySelectorAll('td');
        cells.forEach(cell => row.push(cell.textContent?.trim() || ''));
        rows.push(row);
      }

      return { headers, rows, totalRows: dataRows.length };
    }, tableSelector);

    return data;
  }
}

// Main test suite
test.describe('UI Discovery', () => {
  test('discover all workflows', async ({ page }) => {
    const baseUrl = process.env.APP_URL || 'http://localhost:8080';
    const outputDir = process.env.OUTPUT_DIR || './legacy-golden';

    // Ensure output directories exist
    fs.mkdirSync(path.join(outputDir, 'screenshots'), { recursive: true });

    const agent = new BrowserAgent(page, baseUrl, outputDir);
    const workflows = await agent.discoverWorkflows(3);

    // Save workflows
    const workflowsPath = path.join(outputDir, 'workflows.json');
    fs.writeFileSync(workflowsPath, JSON.stringify(workflows, null, 2));

    console.log(`✅ Discovered ${workflows.length} workflows`);
    console.log(`📸 Screenshots saved to ${path.join(outputDir, 'screenshots')}`);
  });

  test('capture grid data', async ({ page }) => {
    const baseUrl = process.env.APP_URL || 'http://localhost:8080';
    const outputDir = process.env.OUTPUT_DIR || './legacy-golden';

    await page.goto(baseUrl, { waitUntil: 'networkidle' });

    const agent = new BrowserAgent(page, baseUrl, outputDir);

    // Find all tables
    const tables = await page.$$('table, [class*="grid"]');
    const gridData = [];

    for (let i = 0; i < tables.length; i++) {
      const data = await agent.captureGridData(`table:nth-of-type(${i + 1})`);
      if (data) {
        gridData.push({ tableIndex: i, ...data });
      }
    }

    // Save grid data
    const gridDataPath = path.join(outputDir, 'grid-data.json');
    fs.writeFileSync(gridDataPath, JSON.stringify(gridData, null, 2));

    console.log(`✅ Captured ${gridData.length} grids`);
  });
});
```

---

## Framework-Specific Adaptations

The skill detects the application framework and adapts selectors:

### WinForms → WebForms Detection
```typescript
// Check for ASP.NET WebForms patterns
const isWebForms = await page.evaluate(() => {
  return !!(window.__doPostBack || document.getElementById('__VIEWSTATE'));
});

if (isWebForms) {
  // Use ASP.NET control naming patterns
  // Format: ctl00$ContentPlaceHolder1$ButtonName
}
```

### Modern React/Angular Detection
```typescript
const isReact = await page.evaluate(() => {
  return !!document.querySelector('[data-reactroot], [data-reactid]');
});

if (isReact) {
  // Prefer data-testid selectors
  // Wait for React re-renders
}
```

---

## Execution Flow

### Discovery Mode

1. **Initialize**
   ```bash
   OUTPUT_DIR="./docs/legacy-golden/<seam>" \
   APP_URL="http://localhost:8080" \
   npx playwright test .claude/skills/browser-agent/scripts/discover.spec.ts
   ```

2. **Generate Report**
   ```bash
   node .claude/skills/browser-agent/scripts/generate-baseline-index.js
   ```

3. **Output Structure**
   ```
   docs/legacy-golden/<seam>/
   ├── BASELINE_INDEX.md         # Human-readable summary
   ├── workflows.json            # Discovered journeys
   ├── ui-elements.json          # Element inventory
   ├── grid-data.json            # Extracted table data
   └── screenshots/
       ├── screen_0_0.png        # Root screen
       ├── screen_1_1.png        # First navigation
       └── ...
   ```

### Verification Mode

1. **Initialize**
   ```bash
   LEGACY_URL="http://localhost:8080" \
   MODERN_URL="http://localhost:5173" \
   SEAM="channels" \
   npx playwright test .claude/skills/browser-agent/scripts/verify.spec.ts
   ```

2. **Generate Diff Report**
   ```bash
   node .claude/skills/browser-agent/scripts/generate-parity-report.js
   ```

3. **Output Structure**
   ```
   tests/parity/<seam>/
   ├── diff-report.html          # Visual comparison
   ├── feature-matrix.md         # Parity checklist
   ├── issues.json               # Detected problems
   └── screenshots/
       ├── legacy_screen1.png
       ├── modern_screen1.png
       └── diff_screen1.png      # Highlighted differences
   ```

---

## Integration with Migration Agents

### 1. Golden Baseline Capture Agent
```yaml
agent: golden-baseline-capture
dependencies:
  - browser-agent skill (discovery mode)
workflow:
  1. User ensures legacy app is running
  2. Agent invokes: /browser-agent discovery http://legacy-app:8080
  3. Agent reviews workflows.json
  4. Agent generates BASELINE_INDEX.md
  5. Agent commits to docs/legacy-golden/
```

### 2. Parity Harness Generator Agent
```yaml
agent: parity-harness-generator
dependencies:
  - browser-agent skill (verify mode)
  - golden baselines (from step 1)
workflow:
  1. Agent reads docs/legacy-golden/<seam>/workflows.json
  2. Agent invokes: /browser-agent verify --seam <seam>
  3. Agent analyzes diff-report.html
  4. Agent generates parity test suite
  5. Agent documents approved differences in evidence.md
```

### 3. UI Inventory Extractor Agent
```yaml
agent: ui-inventory-extractor
dependencies:
  - browser-agent skill (discovery mode)
workflow:
  1. Agent invokes browser-agent for each major screen
  2. Agent consolidates ui-elements.json across screens
  3. Agent generates visual-controls-catalog.md
  4. Agent identifies reusable component patterns
```

---

## Configuration

Create `.claude/skills/browser-agent/config.json`:
```json
{
  "discovery": {
    "maxDepth": 5,
    "maxDurationMs": 300000,
    "screenshotFormat": "png",
    "fullPageScreenshots": true,
    "waitForNetworkIdle": true,
    "excludePatterns": [
      "*/logout",
      "*/delete/*",
      "*/admin/*"
    ]
  },
  "verification": {
    "pixelDiffThreshold": 0.05,
    "viewportSizes": [
      { "width": 1920, "height": 1080 },
      { "width": 1366, "height": 768 }
    ],
    "ignoreRegions": [
      ".timestamp",
      ".version-info",
      ".user-avatar"
    ]
  },
  "browser": {
    "headless": true,
    "slowMo": 100,
    "timeout": 30000
  }
}
```

---

## Safety Guardrails

- **Read-only**: Never click destructive actions (Delete, Logout, Admin)
- **Rate limiting**: 500ms delay between actions
- **Timeout**: Max 5 minutes per discovery session
- **State isolation**: Each test runs in isolated browser context
- **Revertibility**: Never modify application state (no form submissions by default)

---

## Success Criteria

### Discovery Mode
- ✅ All major screens captured (at least 1 screenshot per route)
- ✅ All interactive elements documented
- ✅ At least 3 user workflows identified
- ✅ Grid/table data extracted for data-heavy screens
- ✅ BASELINE_INDEX.md generated

### Verification Mode
- ✅ Parity score ≥ 85% for feature completeness
- ✅ All legacy screens have modern equivalent
- ✅ All critical workflows executable in modern app
- ✅ Data grid contents match (within tolerance)
- ✅ All discrepancies documented and approved

---

## Error Handling

```typescript
try {
  await agent.discoverWorkflows();
} catch (error) {
  console.error('❌ Discovery failed:', error);

  // Save partial results
  fs.writeFileSync('partial-results.json', JSON.stringify({
    error: error.message,
    visitedUrls: Array.from(agent.visitedUrls),
    timestamp: new Date().toISOString()
  }));

  throw error;
}
```

---

## Usage Examples

### Example 1: Capture Legacy Golden Baseline
```bash
/browser-agent discovery http://localhost:8080 --seam channels
```

### Example 2: Verify Modern App Parity
```bash
/browser-agent verify --legacy http://localhost:8080 --modern http://localhost:5173 --seam archiver
```

### Example 3: Extract UI Components for Catalog
```bash
/browser-agent discovery http://localhost:8080 --mode ui-inventory --output docs/context-fabric/
```

---

## Next Steps After Running Browser Agent

1. **Review Output**: Check `docs/legacy-golden/<seam>/BASELINE_INDEX.md`
2. **Validate Workflows**: Ensure all critical workflows were discovered
3. **Supplement**: Add manual screenshots for screens the agent couldn't reach
4. **Document Blockers**: Note any screens requiring authentication or special setup
5. **Commit**: Add golden baselines to git for team access

---

## Troubleshooting

**Issue**: Agent can't reach authenticated screens
**Solution**: Pass credentials via environment variables:
```bash
AUTH_USER="admin" AUTH_PASS="password" /browser-agent discovery ...
```

**Issue**: Infinite loop detected
**Solution**: Reduce `maxDepth` or add exclusion patterns in config

**Issue**: Screenshots are blank
**Solution**: Increase `waitForNetworkIdle` timeout or use `waitUntil: 'load'`

**Issue**: Legacy app is WinForms, not web-based
**Solution**: Use alternative capture method (see WinForms golden baseline capture docs)
