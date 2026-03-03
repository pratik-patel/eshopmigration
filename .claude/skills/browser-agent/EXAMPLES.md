# Browser Agent - Usage Examples

Complete examples for using the browser agent skill in different scenarios.

---

## Example 1: Legacy Application Golden Baseline Capture

**Scenario**: You have a legacy .NET application running and need to capture its UI for modernization.

### Step 1: Start Legacy Application

```bash
# Ensure legacy app is running
# For WebForms: IIS Express or full IIS
# For WinForms: Run the executable
```

### Step 2: Run Discovery via Claude Code

```bash
# In Claude Code CLI
/browser-agent discovery http://localhost:8080
```

**OR** run directly:

```bash
cd .claude/skills/browser-agent
./scripts/run-discovery.sh http://localhost:8080 --seam channels --depth 3
```

### Step 3: Review Results

```bash
# Open the baseline index
code legacy-golden/channels/BASELINE_INDEX.md

# View screenshots
ls -la legacy-golden/channels/screenshots/

# Check workflows
cat legacy-golden/channels/workflows.json | jq '.[] | {name, steps: .steps | length}'
```

### Step 4: Supplement with Manual Captures

If some screens require authentication or special setup:

```bash
# Add manual screenshots to:
# legacy-golden/channels/screenshots/manual_*.png

# Document in BASELINE_INDEX.md:
echo "## Manual Captures" >> legacy-golden/channels/BASELINE_INDEX.md
echo "- Login screen: manual_login.png" >> legacy-golden/channels/BASELINE_INDEX.md
```

### Step 5: Commit Baseline

```bash
git add legacy-golden/channels/
git commit -m "Add golden baseline for channels seam

- Discovered 12 workflows
- Captured 45 screenshots
- Extracted data from 3 grids

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

**Expected Output:**
```
legacy-golden/channels/
├── BASELINE_INDEX.md          # ✅ 12 workflows documented
├── workflows.json             # ✅ Machine-readable definitions
├── discovery-summary.json     # ✅ Statistics
├── elements_*.json            # ✅ 8 files (one per page)
├── grid-data_*.json           # ✅ 3 files (channel grids)
└── screenshots/
    ├── screen_0_0.png         # Root screen
    ├── screen_1_1.png         # First navigation
    └── ... (45 total)
```

---

## Example 2: Parity Verification After Migration

**Scenario**: You've migrated the channels seam to React. Now verify parity.

### Step 1: Ensure Both Apps Running

```bash
# Terminal 1: Legacy app
cd legacy-app
dotnet run  # Runs on http://localhost:8080

# Terminal 2: Modern app
cd frontend
npm run dev  # Runs on http://localhost:5173
```

### Step 2: Run Verification

```bash
# Via Claude Code
/browser-agent verify --legacy http://localhost:8080 --modern http://localhost:5173 --seam channels

# OR directly
cd .claude/skills/browser-agent
./scripts/run-verification.sh \
  --legacy http://localhost:8080 \
  --modern http://localhost:5173 \
  --seam channels
```

### Step 3: Review Parity Report

```bash
# Open HTML report in browser
open tests/parity/channels/diff-report.html

# Review feature matrix
cat tests/parity/channels/feature-matrix.md

# Check issues
cat tests/parity/channels/issues.json | jq '.[] | {screen, issue}'
```

### Step 4: Interpret Score

```
📊 Parity Score: 87.3%
```

**Breakdown:**
- Visual Similarity: 92% ✅
- Elements Match: 85% 🟡 (2 buttons missing)
- Data Parity: 90% ✅
- Workflow Complete: 82% 🟡 (1 workflow has extra step)

**Action Items:**
1. Add missing "Export" button
2. Add missing "Refresh" button
3. Investigate why modern workflow requires extra click

### Step 5: Fix Issues and Re-verify

```bash
# After fixes in frontend
/browser-agent verify --legacy http://localhost:8080 --modern http://localhost:5173 --seam channels

# New score
📊 Parity Score: 94.1%
```

### Step 6: Document Approved Differences

```bash
# Edit feature matrix to note approved differences
echo "## Approved Differences" >> tests/parity/channels/feature-matrix.md
echo "1. Modern uses icon buttons (legacy used text) - Approved by UX" >> tests/parity/channels/feature-matrix.md
```

**Expected Output:**
```
tests/parity/channels/
├── diff-report.html           # ✅ Visual comparison
├── feature-matrix.md          # ✅ 95% feature parity
├── parity-results.json        # ✅ Detailed results
├── issues.json                # ✅ 2 issues remaining
└── screenshots/
    ├── legacy_channels_list.png
    ├── modern_channels_list.png
    ├── diff_channels_list.png  # Diff highlighted
    └── ... (side-by-side for each screen)
```

---

## Example 3: Integration with Golden Baseline Capture Agent

**Scenario**: Automated baseline capture as part of Phase 0.

### In Agent Workflow

The `golden-baseline-capture` agent invokes the browser-agent skill:

```python
# Pseudo-code from agent
agent.invoke_skill("browser-agent", {
    "mode": "discovery",
    "url": legacy_app_url,
    "seam": current_seam,
    "output": f"legacy-golden/{current_seam}"
})

# Agent then reviews output
workflows = agent.read_json(f"legacy-golden/{current_seam}/workflows.json")

if len(workflows) < 3:
    agent.warn("Only {len(workflows)} workflows found. Manual supplement needed.")

# Agent generates final baseline index
agent.generate_baseline_index(current_seam)
```

### Verification

```bash
# Agent validates completeness
test -f legacy-golden/channels/BASELINE_INDEX.md || echo "❌ Missing index"
test -f legacy-golden/channels/workflows.json || echo "❌ Missing workflows"
test -d legacy-golden/channels/screenshots || echo "❌ Missing screenshots"

# Count screenshots
screenshot_count=$(ls legacy-golden/channels/screenshots/*.png | wc -l)
echo "📸 Captured $screenshot_count screenshots"

# Expect at least 10 for a typical seam
if [ $screenshot_count -lt 10 ]; then
    echo "⚠️  Low screenshot count. Verify discovery depth or add manual captures."
fi
```

---

## Example 4: Authenticated Application Discovery

**Scenario**: Legacy app requires login before accessing features.

### Option A: Pre-authenticate in Browser

```bash
# Start browser-agent in headed mode (to see UI)
cd .claude/skills/browser-agent

# Edit playwright.config.ts temporarily:
# use: { headless: false }

# Run discovery
APP_URL="http://localhost:8080/dashboard" npm run discover

# Manually login when browser opens
# Agent will continue after login completes
```

### Option B: Programmatic Login

Create `scripts/discover-authenticated.spec.ts`:

```typescript
import { test } from '@playwright/test';
// ... (copy from discover.spec.ts)

test.describe('Authenticated UI Discovery', () => {
  test.beforeEach(async ({ page }) => {
    // Login first
    await page.goto('http://localhost:8080/login');
    await page.fill('#username', process.env.AUTH_USER || 'admin');
    await page.fill('#password', process.env.AUTH_PASS || 'password');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard');
    console.log('✅ Logged in successfully');
  });

  test('discover authenticated workflows', async ({ page }) => {
    // Now run discovery starting from dashboard
    const agent = new BrowserAgent(page, page.url(), outputDir, config);
    await agent.discoverWorkflows(3);
    // ...
  });
});
```

Run with credentials:

```bash
AUTH_USER="testuser" AUTH_PASS="testpass" \
npx playwright test scripts/discover-authenticated.spec.ts
```

---

## Example 5: Framework-Specific Capture (WebForms)

**Scenario**: Legacy app is ASP.NET WebForms with postback mechanisms.

### Adapt Selectors

Edit `scripts/discover.spec.ts` to handle WebForms patterns:

```typescript
private async generateSelector(element: ElementHandle): Promise<string> {
  // Check if this is a WebForms app
  const isWebForms = await this.page.evaluate(() =>
    !!(window as any).__doPostBack || document.getElementById('__VIEWSTATE')
  );

  if (isWebForms) {
    // Try WebForms control ID first (e.g., ctl00$ContentPlaceHolder1$btnSubmit)
    const id = await element.getAttribute('id');
    if (id && id.includes('$')) {
      return `#${id}`;
    }

    // Try name attribute (often matches server control ID)
    const name = await element.getAttribute('name');
    if (name) {
      return `[name="${name}"]`;
    }
  }

  // Fall back to standard selector logic
  return await this.standardSelectorGeneration(element);
}
```

### Handle Postbacks

```typescript
// After clicking a button that triggers postback
await this.page.click(element.selector);

// Wait for postback to complete
await this.page.waitForFunction(() => {
  const viewState = document.getElementById('__VIEWSTATE') as HTMLInputElement;
  return viewState && viewState.value !== '';
}, { timeout: 5000 });

// Additional wait for DOM updates
await this.page.waitForTimeout(500);
```

---

## Example 6: Data-Heavy Application (Grids Focus)

**Scenario**: Legacy app has many data grids. Focus on capturing grid structures.

### Custom Grid Discovery

```bash
# Run discovery with grid focus
cd .claude/skills/browser-agent

# Add custom script: scripts/discover-grids.spec.ts
```

```typescript
test('discover all grids', async ({ page }) => {
  const baseUrl = process.env.APP_URL || 'http://localhost:8080';
  const outputDir = process.env.OUTPUT_DIR || './legacy-golden/grids';

  await page.goto(baseUrl);

  // Find all pages with grids
  const links = await page.$$('a[href]');
  const gridPages = [];

  for (const link of links) {
    const href = await link.getAttribute('href');
    if (href && (href.includes('list') || href.includes('grid') || href.includes('data'))) {
      gridPages.push(href);
    }
  }

  console.log(`Found ${gridPages.length} potential grid pages`);

  // Visit each and extract grid data
  for (const pageUrl of gridPages) {
    await page.goto(new URL(pageUrl, baseUrl).href);
    await page.waitForTimeout(1000);

    const tables = await page.$$('table, [role="grid"]');

    for (let i = 0; i < tables.length; i++) {
      const data = await extractDetailedGridData(page, i);
      // Save with metadata about sort/filter controls
      fs.writeFileSync(
        path.join(outputDir, `grid_${pageUrl.replace(/\//g, '_')}_${i}.json`),
        JSON.stringify(data, null, 2)
      );
    }
  }
});
```

---

## Example 7: CI/CD Integration

**Scenario**: Run parity verification in CI pipeline after deployment.

### GitHub Actions Workflow

```yaml
# .github/workflows/parity-check.yml
name: Parity Verification

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  parity:
    runs-on: ubuntu-latest

    services:
      legacy-app:
        image: legacy-app:latest
        ports:
          - 8080:80

    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install dependencies
        run: |
          cd .claude/skills/browser-agent
          npm install
          npx playwright install chromium

      - name: Start modern app
        run: |
          cd frontend
          npm install
          npm run build
          npm run preview &
          sleep 5

      - name: Run parity verification
        run: |
          cd .claude/skills/browser-agent
          ./scripts/run-verification.sh \
            --legacy http://localhost:8080 \
            --modern http://localhost:4173 \
            --seam channels

      - name: Check parity score
        run: |
          SCORE=$(node -e "console.log(JSON.parse(require('fs').readFileSync('tests/parity/channels/parity-results.json')).parityScore)")
          echo "Parity Score: $SCORE%"

          if (( $(echo "$SCORE < 85" | bc -l) )); then
            echo "❌ Parity score below threshold (85%)"
            exit 1
          fi

      - name: Upload parity report
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: parity-report
          path: tests/parity/channels/
```

---

## Example 8: Multi-Seam Discovery

**Scenario**: Capture baselines for all seams in one session.

### Batch Script

```bash
#!/bin/bash
# discover-all-seams.sh

SEAMS=("channels" "archiver" "designer" "reports")
BASE_URL="http://localhost:8080"

for seam in "${SEAMS[@]}"; do
    echo ""
    echo "========================================"
    echo "📍 Discovering seam: $seam"
    echo "========================================"

    cd .claude/skills/browser-agent

    ./scripts/run-discovery.sh \
        "$BASE_URL/$seam" \
        --seam "$seam" \
        --depth 3

    if [ $? -eq 0 ]; then
        echo "✅ $seam: Complete"
    else
        echo "❌ $seam: Failed"
    fi
done

echo ""
echo "📊 Summary:"
for seam in "${SEAMS[@]}"; do
    if [ -f "legacy-golden/$seam/BASELINE_INDEX.md" ]; then
        workflow_count=$(grep -c "^### " "legacy-golden/$seam/BASELINE_INDEX.md" || echo 0)
        echo "  $seam: $workflow_count workflows"
    else
        echo "  $seam: ❌ Not captured"
    fi
done
```

---

## Troubleshooting Examples

### Problem: Discovery Times Out

```bash
# Solution: Reduce depth and increase timeout
cd .claude/skills/browser-agent

# Edit config.json
jq '.discovery.maxDepth = 2 | .discovery.maxDurationMs = 600000' config.json > config.tmp.json
mv config.tmp.json config.json

# Re-run
./scripts/run-discovery.sh http://localhost:8080
```

### Problem: Missing Screenshots

```bash
# Solution: Check if pages loaded
# Review playwright report
npx playwright show-report playwright-report

# Check for JavaScript errors
# Add console logging to discover.spec.ts:
page.on('console', msg => console.log('PAGE LOG:', msg.text()));
page.on('pageerror', err => console.error('PAGE ERROR:', err));
```

### Problem: False Parity Failures

```bash
# Solution: Adjust pixel diff threshold
cd .claude/skills/browser-agent

# Edit config.json
jq '.verification.pixelDiffThreshold = 0.1' config.json > config.tmp.json
mv config.tmp.json config.json

# Add regions to ignore (timestamps, etc.)
jq '.verification.ignoreRegions += [".timestamp", ".session-id"]' config.json > config.tmp.json
mv config.tmp.json config.json
```

---

## Best Practices

1. **Run discovery on stable build**: Don't capture baseline from development environment
2. **Version your baselines**: Tag with legacy app version (e.g., `v1.5.2-baseline`)
3. **Supplement automated captures**: Add manual screenshots for edge cases
4. **Document exclusions**: Note why certain screens weren't captured
5. **Re-verify after fixes**: Don't rely on single verification run
6. **Archive old baselines**: Keep historical baselines for regression testing

---

## Integration Checklist

- [ ] Baseline captured for all seams
- [ ] BASELINE_INDEX.md reviewed and approved
- [ ] Screenshots clear and complete
- [ ] Grid data extracted and validated
- [ ] Workflows cover critical user journeys
- [ ] Baselines committed to git
- [ ] Parity verification run for migrated seams
- [ ] Parity score ≥ 85% for all seams
- [ ] Approved differences documented
- [ ] Evidence files generated
