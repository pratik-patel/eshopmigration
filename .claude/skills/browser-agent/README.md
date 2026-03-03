# Browser Agent Skill

Automated browser testing skill for Claude Code that discovers UI workflows and verifies parity between legacy and modern applications using Playwright.

## Features

- **🔍 Discovery Mode**: Automatically explore legacy UI and capture workflows
- **✅ Verification Mode**: Compare legacy vs modern UI for feature parity
- **📸 Screenshot Capture**: Full-page screenshots of all UI states
- **📊 Element Discovery**: Identify buttons, forms, grids, navigation
- **💾 Data Extraction**: Capture grid/table data for validation
- **📈 Parity Scoring**: Quantitative assessment of migration completeness

## Installation

```bash
cd .claude/skills/browser-agent
npm install
npx playwright install chromium
```

## Usage

### Discovery Mode

Explore a legacy application and capture UI workflows:

```bash
# Via Claude Code skill
/browser-agent discovery http://localhost:8080

# Direct command
APP_URL="http://localhost:8080" \
OUTPUT_DIR="./legacy-golden/my-seam" \
MAX_DEPTH=3 \
npm run discover

# Generate baseline index
npm run report:baseline ./legacy-golden/my-seam
```

**Output:**
- `legacy-golden/my-seam/BASELINE_INDEX.md` — Human-readable summary
- `legacy-golden/my-seam/workflows.json` — Workflow definitions
- `legacy-golden/my-seam/discovery-summary.json` — Statistics
- `legacy-golden/my-seam/screenshots/` — UI captures
- `legacy-golden/my-seam/elements_*.json` — Element inventories
- `legacy-golden/my-seam/grid-data_*.json` — Extracted data

### Verification Mode

Compare legacy vs modern application:

```bash
# Via Claude Code skill
/browser-agent verify --legacy http://localhost:8080 --modern http://localhost:5173 --seam channels

# Direct command
LEGACY_URL="http://localhost:8080" \
MODERN_URL="http://localhost:5173" \
BASELINE_DIR="./legacy-golden/channels" \
OUTPUT_DIR="./tests/parity/channels" \
npm run verify

# Generate parity report
npm run report:parity ./tests/parity/channels
```

**Output:**
- `tests/parity/channels/feature-matrix.md` — Feature comparison
- `tests/parity/channels/diff-report.html` — Visual diff report
- `tests/parity/channels/parity-results.json` — Detailed results
- `tests/parity/channels/issues.json` — Detected issues
- `tests/parity/channels/screenshots/` — Side-by-side captures

## Configuration

Edit `config.json` to customize behavior:

```json
{
  "discovery": {
    "maxDepth": 5,              // How deep to explore navigation
    "maxDurationMs": 300000,    // Max 5 minutes
    "screenshotFormat": "png",
    "fullPageScreenshots": true,
    "waitForNetworkIdle": true,
    "excludePatterns": [        // URLs to skip
      "*/logout",
      "*/delete/*"
    ]
  },
  "verification": {
    "pixelDiffThreshold": 0.05,  // 5% difference tolerance
    "viewportSizes": [
      { "width": 1920, "height": 1080 }
    ]
  }
}
```

## Integration with Migration Agents

### 1. Golden Baseline Capture Agent

The `golden-baseline-capture` agent uses this skill to capture legacy UI:

```yaml
workflow:
  1. Agent invokes: /browser-agent discovery http://legacy-app:8080
  2. Reviews workflows.json
  3. Generates BASELINE_INDEX.md
  4. Commits to legacy-golden/
```

### 2. Parity Harness Generator Agent

The `parity-harness-generator` agent uses this skill to verify parity:

```yaml
workflow:
  1. Reads legacy-golden/<seam>/workflows.json
  2. Invokes: /browser-agent verify --seam <seam>
  3. Analyzes diff-report.html
  4. Generates test suite
  5. Documents approved differences
```

### 3. UI Inventory Extractor Agent

The `ui-inventory-extractor` agent uses this skill for component discovery:

```yaml
workflow:
  1. Invokes browser-agent for each major screen
  2. Consolidates element inventories
  3. Generates visual-controls-catalog.md
```

## Examples

### Example 1: Capture Channels Seam

```bash
/browser-agent discovery http://localhost:8080/channels --seam channels
```

Result: `legacy-golden/channels/BASELINE_INDEX.md` with 15 workflows captured

### Example 2: Verify Archiver Parity

```bash
/browser-agent verify --legacy http://localhost:8080/archiver --modern http://localhost:5173/archiver --seam archiver
```

Result: Parity score of 87% with 3 minor issues

### Example 3: Extract UI Components

```bash
/browser-agent discovery http://localhost:8080 --mode ui-inventory
```

Result: Complete element catalog for component library generation

## Troubleshooting

### Issue: Screenshots are blank

**Solution**: Increase wait time or disable `waitForNetworkIdle`

```bash
# In config.json
"waitForNetworkIdle": false
```

### Issue: Can't reach authenticated screens

**Solution**: Pass credentials via environment:

```bash
AUTH_USER="admin" AUTH_PASS="password" npm run discover
```

### Issue: Agent stuck in infinite loop

**Solution**: Reduce `maxDepth` or add exclusion patterns:

```json
{
  "discovery": {
    "maxDepth": 3,
    "excludePatterns": ["*/loop/*"]
  }
}
```

### Issue: Legacy app is WinForms (not web)

**Solution**: WinForms requires different capture approach. See WinForms-specific documentation in migration guide.

## Parity Scoring

Verification mode calculates parity score based on:

| Component | Weight | Description |
|-----------|--------|-------------|
| **Feature Completeness** | 40% | All legacy features present in modern |
| **Data Accuracy** | 30% | Grid data matches between apps |
| **Visual Consistency** | 20% | UI looks similar (within tolerance) |
| **Workflow Equivalence** | 10% | Same steps achieve same result |

**Score Interpretation:**
- **90-100%**: ✅ Excellent — Production ready
- **70-89%**: 🟡 Good — Minor gaps to address
- **Below 70%**: 🔴 Significant gaps — More work needed

## Safety

The browser agent is **read-only** by default:
- Never clicks Delete/Logout/Admin buttons
- 500ms delay between actions (rate limiting)
- 5-minute timeout per session
- Isolated browser contexts (no state leak)
- No form submissions (unless explicitly enabled)

## Advanced Usage

### Custom Selectors

Override default selector generation:

```typescript
// In discover.spec.ts
const customSelectors = {
  button: '[data-action="click"]',
  input: '[data-field]',
  grid: '.custom-grid'
};
```

### Authenticated Testing

Handle login flow:

```typescript
// Add to discover.spec.ts before exploration
await page.goto('http://localhost:8080/login');
await page.fill('#username', process.env.AUTH_USER);
await page.fill('#password', process.env.AUTH_PASS);
await page.click('button[type="submit"]');
await page.waitForURL('**/dashboard');
```

### Framework-Specific Adaptations

Detect and adapt to frameworks:

```typescript
// WebForms detection
const isWebForms = await page.evaluate(() => !!window.__doPostBack);

// React detection
const isReact = await page.evaluate(() =>
  !!document.querySelector('[data-reactroot]')
);
```

## Files

```
browser-agent/
├── SKILL.md              # Skill definition
├── README.md             # This file
├── package.json          # Dependencies
├── config.json           # Configuration
├── scripts/
│   ├── discover.spec.ts           # Discovery Playwright test
│   ├── verify.spec.ts             # Verification Playwright test
│   ├── generate-baseline-index.js # Report generator
│   └── generate-parity-report.js  # Parity report generator
```

## Contributing

To extend the browser agent:

1. **Add new element types**: Edit `discoverElements()` in `discover.spec.ts`
2. **Add comparison logic**: Edit `comparePages()` in `verify.spec.ts`
3. **Add report sections**: Edit `generateBaselineIndex()` or `generateParityReport()`
4. **Add config options**: Update `config.json` schema

## License

Part of the Claude Code migration toolkit. See main project license.
