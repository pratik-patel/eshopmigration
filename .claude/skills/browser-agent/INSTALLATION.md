# Browser Agent Skill - Installation Guide

## What Was Created

A complete Claude Code skill for automated browser testing using Playwright. This skill enables:

1. **Discovery Mode**: Automatically explore legacy applications and capture UI workflows
2. **Verification Mode**: Compare legacy vs modern applications for feature parity

## File Structure

```
.claude/skills/browser-agent/
├── SKILL.md                          # Skill definition (loaded by Claude Code)
├── README.md                         # Comprehensive documentation
├── EXAMPLES.md                       # Usage examples for common scenarios
├── INSTALLATION.md                   # This file
├── package.json                      # Node.js dependencies
├── config.json                       # Configuration options
├── playwright.config.ts              # Playwright test configuration
├── verify-installation.sh            # Installation verification script
│
└── scripts/
    ├── discover.spec.ts              # Discovery mode Playwright test
    ├── verify.spec.ts                # Verification mode Playwright test
    ├── generate-baseline-index.js    # Baseline report generator
    ├── generate-parity-report.js     # Parity report generator
    ├── run-discovery.sh              # Discovery mode runner script
    └── run-verification.sh           # Verification mode runner script
```

## Prerequisites

Before using this skill, ensure you have:

1. **Node.js** (v18 or higher)
   - Download from: https://nodejs.org/
   - Verify: `node --version`

2. **npm** (comes with Node.js)
   - Verify: `npm --version`

3. **Git** (for version control)
   - Verify: `git --version`

## Installation Steps

### Step 1: Navigate to Skill Directory

```bash
cd .claude/skills/browser-agent
```

### Step 2: Install Dependencies

```bash
npm install
```

This installs:
- `@playwright/test` - Browser automation framework
- `pngjs` - PNG image processing
- `pixelmatch` - Pixel-level image comparison

### Step 3: Install Playwright Browsers

```bash
npx playwright install chromium
```

This downloads the Chromium browser for automated testing.

### Step 4: Verify Installation

```bash
./verify-installation.sh
```

Expected output:
```
✅ Installation verification passed!

Ready to use browser-agent skill:
  /browser-agent discovery <url>
  /browser-agent verify --legacy <url> --modern <url>
```

## Quick Start

### Option 1: Via Claude Code CLI

```bash
# Discovery mode
/browser-agent discovery http://localhost:8080

# Verification mode
/browser-agent verify --legacy http://localhost:8080 --modern http://localhost:5173 --seam channels
```

### Option 2: Direct Script Execution

```bash
# Discovery
cd .claude/skills/browser-agent
./scripts/run-discovery.sh http://localhost:8080 --seam channels

# Verification
./scripts/run-verification.sh \
  --legacy http://localhost:8080 \
  --modern http://localhost:5173 \
  --seam channels
```

## Configuration

Edit `config.json` to customize behavior:

```json
{
  "discovery": {
    "maxDepth": 5,              // Navigation depth
    "maxDurationMs": 300000,    // 5-minute timeout
    "screenshotFormat": "png",
    "fullPageScreenshots": true,
    "excludePatterns": [        // URLs to skip
      "*/logout",
      "*/delete/*"
    ]
  },
  "verification": {
    "pixelDiffThreshold": 0.05, // 5% tolerance
    "viewportSizes": [
      { "width": 1920, "height": 1080 }
    ]
  }
}
```

## Output Locations

### Discovery Mode Output

```
legacy-golden/<seam>/
├── BASELINE_INDEX.md          # Human-readable summary
├── workflows.json             # Machine-readable workflows
├── discovery-summary.json     # Statistics
├── elements_*.json            # Per-page element inventory
├── grid-data_*.json           # Extracted grid data
└── screenshots/
    ├── screen_0_0.png
    └── ...
```

### Verification Mode Output

```
tests/parity/<seam>/
├── diff-report.html           # Visual comparison report
├── feature-matrix.md          # Feature parity checklist
├── parity-results.json        # Detailed results
├── issues.json                # Detected discrepancies
└── screenshots/
    ├── legacy_*.png
    ├── modern_*.png
    └── diff_*.png
```

## Usage with Migration Agents

This skill integrates with Claude Code migration agents:

### 1. Golden Baseline Capture Agent

```yaml
Phase: 0 (UNDERSTAND)
Agent: golden-baseline-capture
Uses: /browser-agent discovery
Output: legacy-golden/<seam>/BASELINE_INDEX.md
```

### 2. Parity Harness Generator Agent

```yaml
Phase: 5 (VERIFY)
Agent: parity-harness-generator
Uses: /browser-agent verify
Output: tests/parity/<seam>/diff-report.html
```

### 3. UI Inventory Extractor Agent

```yaml
Phase: 0 (UNDERSTAND)
Agent: ui-inventory-extractor
Uses: /browser-agent discovery --mode ui-inventory
Output: docs/context-fabric/visual-controls-catalog.md
```

## Troubleshooting

### Issue: `command not found: node`

**Solution**: Install Node.js from https://nodejs.org/

```bash
# Verify installation
node --version
npm --version
```

### Issue: `Error: Cannot find module '@playwright/test'`

**Solution**: Install dependencies

```bash
cd .claude/skills/browser-agent
npm install
```

### Issue: `browserType.launch: Executable doesn't exist`

**Solution**: Install Playwright browsers

```bash
npx playwright install chromium
```

### Issue: Screenshots are blank

**Solution**: Increase wait time in `config.json`

```json
{
  "discovery": {
    "waitForNetworkIdle": true
  }
}
```

Or add delays in the test scripts.

### Issue: Can't access authenticated pages

**Solution**: Set up authentication in discovery script

See `EXAMPLES.md` → "Example 4: Authenticated Application Discovery"

## Advanced Configuration

### Custom Selectors

Edit `scripts/discover.spec.ts` to customize element detection:

```typescript
// Add custom selector strategies
private async generateSelector(element: ElementHandle): Promise<string> {
  // Your custom logic here
}
```

### Framework-Specific Adaptations

Detect and adapt to specific frameworks (WebForms, React, Angular):

```typescript
const isWebForms = await page.evaluate(() => !!window.__doPostBack);
const isReact = await page.evaluate(() => !!document.querySelector('[data-reactroot]'));
```

See `EXAMPLES.md` for detailed framework-specific examples.

## Testing the Installation

### Test Discovery Mode

```bash
# Using a public demo site
cd .claude/skills/browser-agent
APP_URL="https://demo.playwright.dev/todomvc" \
OUTPUT_DIR="./test-output" \
npm run discover

# Check results
ls -la test-output/
cat test-output/BASELINE_INDEX.md
```

### Test Verification Mode

```bash
# Compare demo site against itself (should be 100% parity)
LEGACY_URL="https://demo.playwright.dev/todomvc" \
MODERN_URL="https://demo.playwright.dev/todomvc" \
OUTPUT_DIR="./test-parity" \
npm run verify

# Check results
open test-parity/diff-report.html
```

## Integration Checklist

Before using in production:

- [ ] Node.js v18+ installed
- [ ] npm dependencies installed (`npm install`)
- [ ] Playwright browsers installed (`npx playwright install chromium`)
- [ ] Configuration reviewed and customized (`config.json`)
- [ ] Verification script passes (`./verify-installation.sh`)
- [ ] Test discovery run successful
- [ ] Test verification run successful
- [ ] Output directories created (`legacy-golden/`, `tests/parity/`)
- [ ] Legacy application accessible at specified URL
- [ ] Modern application accessible (for verification mode)

## Next Steps

1. **Read Documentation**: Review `README.md` for detailed usage
2. **Review Examples**: Check `EXAMPLES.md` for common scenarios
3. **Customize Config**: Edit `config.json` for your application
4. **Run Discovery**: Capture legacy UI baseline
5. **Review Output**: Verify workflows and screenshots
6. **Run Verification**: Compare legacy vs modern (after migration)

## Support

For issues or questions:
- Check `EXAMPLES.md` for troubleshooting examples
- Review Playwright documentation: https://playwright.dev/
- Check Claude Code documentation for skill usage
- Review migration agent documentation in `docs/`

## Version

**Version**: 1.0.0
**Created**: 2026-03-02
**Playwright**: ^1.40.0
**Node.js**: >=18.0.0
