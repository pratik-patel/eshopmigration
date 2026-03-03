/**
 * Generate BASELINE_INDEX.md from discovery results
 */

const fs = require('fs');
const path = require('path');

function generateBaselineIndex(outputDir) {
  console.log(`📝 Generating BASELINE_INDEX.md for ${outputDir}`);

  // Load discovery results
  const summaryPath = path.join(outputDir, 'discovery-summary.json');
  const workflowsPath = path.join(outputDir, 'workflows.json');

  if (!fs.existsSync(summaryPath) || !fs.existsSync(workflowsPath)) {
    console.error('❌ Discovery results not found. Run discovery mode first.');
    process.exit(1);
  }

  const summary = JSON.parse(fs.readFileSync(summaryPath, 'utf-8'));
  const workflows = JSON.parse(fs.readFileSync(workflowsPath, 'utf-8'));

  // Find all element files
  const elementFiles = fs.readdirSync(outputDir)
    .filter(f => f.startsWith('elements_'))
    .map(f => path.join(outputDir, f));

  // Aggregate element stats
  let totalElements = 0;
  let buttonCount = 0;
  let linkCount = 0;
  let inputCount = 0;
  let tableCount = 0;

  elementFiles.forEach(file => {
    const elements = JSON.parse(fs.readFileSync(file, 'utf-8'));
    totalElements += elements.length;
    buttonCount += elements.filter(e => e.type === 'button').length;
    linkCount += elements.filter(e => e.type === 'link').length;
    inputCount += elements.filter(e => e.type.startsWith('input')).length;
    tableCount += elements.filter(e => e.type === 'table').length;
  });

  // Find all grid data files
  const gridFiles = fs.readdirSync(outputDir)
    .filter(f => f.startsWith('grid-data_'));

  let totalGrids = 0;
  let totalRows = 0;

  gridFiles.forEach(file => {
    const grids = JSON.parse(fs.readFileSync(path.join(outputDir, file), 'utf-8'));
    totalGrids += grids.length;
    grids.forEach(grid => totalRows += grid.totalRows);
  });

  // Find all screenshots
  const screenshotsDir = path.join(outputDir, 'screenshots');
  const screenshots = fs.existsSync(screenshotsDir)
    ? fs.readdirSync(screenshotsDir).filter(f => f.endsWith('.png') || f.endsWith('.jpg'))
    : [];

  // Generate markdown
  const markdown = `# Legacy Application Baseline Index

**Generated:** ${new Date().toISOString()}
**Discovery Duration:** ${(summary.duration / 1000).toFixed(1)} seconds
**Status:** ✅ Complete

---

## Summary Statistics

| Metric | Count |
|--------|-------|
| **Workflows Discovered** | ${workflows.length} |
| **Pages Visited** | ${summary.totalPages} |
| **Screenshots Captured** | ${screenshots.length} |
| **Interactive Elements** | ${totalElements} |
| **Data Grids** | ${totalGrids} |

### Element Breakdown

| Element Type | Count |
|--------------|-------|
| Buttons | ${buttonCount} |
| Links | ${linkCount} |
| Input Fields | ${inputCount} |
| Tables/Grids | ${tableCount} |

### Data Capture

| Metric | Count |
|--------|-------|
| Grids with Data | ${totalGrids} |
| Total Rows Captured | ${totalRows} |

---

## Discovered Workflows

${workflows.map((w, i) => `
### ${i + 1}. ${w.name}

**ID:** \`${w.id}\`
**Steps:** ${w.steps.length}
**Start URL:** ${w.startUrl}
**End URL:** ${w.endUrl}

**Navigation Path:**
${w.steps.map((step, j) => `${j + 1}. ${step.description}`).join('\n')}

**Screenshots:** ${w.screenshots.length > 0 ? `\`${w.screenshots[0]}\`` : 'None'}

---
`).join('\n')}

## Pages Visited

${Array.from(summary.visitedUrls).map((url, i) => `${i + 1}. ${url}`).join('\n')}

---

## Screenshots

All screenshots are stored in \`screenshots/\`:

${screenshots.slice(0, 20).map((s, i) => `${i + 1}. \`${s}\``).join('\n')}
${screenshots.length > 20 ? `\n... and ${screenshots.length - 20} more` : ''}

---

## Grid Data Samples

${gridFiles.map(file => {
  const grids = JSON.parse(fs.readFileSync(path.join(outputDir, file), 'utf-8'));
  return grids.map((grid, i) => `
### Grid ${i + 1} (${grid.url})

**Columns:** ${grid.headers.length}
**Rows:** ${grid.totalRows}

**Headers:** ${grid.headers.join(' | ')}

**Sample Data (first 3 rows):**
${grid.rows.slice(0, 3).map(row => row.join(' | ')).join('\n')}
`).join('\n');
}).join('\n')}

---

## Files Generated

- \`workflows.json\` — Machine-readable workflow definitions
- \`discovery-summary.json\` — Overall statistics
- \`elements_*.json\` — Per-page element inventories (${elementFiles.length} files)
- \`grid-data_*.json\` — Extracted grid data (${gridFiles.length} files)
- \`screenshots/*.png\` — UI state captures (${screenshots.length} files)

---

## Next Steps

1. **Review Workflows**: Verify all critical user journeys were captured
2. **Supplement Manual Captures**: Add screenshots for authenticated or hard-to-reach screens
3. **Document Business Rules**: Annotate workflows with business logic details
4. **Share with Team**: Commit baseline to git for team access
5. **Begin Migration**: Use this baseline as reference for UI modernization

---

## Usage with Migration Agents

This baseline is used by:

- **contract-generator** — Infers API contracts from UI workflows
- **ui-inventory-extractor** — Builds component catalog from elements
- **parity-harness-generator** — Generates automated parity tests
- **frontend-migration** — References screens during React component development

---

**Note:** This baseline represents the legacy application's UI and behavior at the time of capture. Any subsequent changes to the legacy app should be captured in a new baseline or documented as known drift.
`;

  // Write BASELINE_INDEX.md
  const indexPath = path.join(outputDir, 'BASELINE_INDEX.md');
  fs.writeFileSync(indexPath, markdown);

  console.log(`✅ Generated ${indexPath}`);
  console.log(`\n📊 Summary:`);
  console.log(`  Workflows: ${workflows.length}`);
  console.log(`  Pages: ${summary.totalPages}`);
  console.log(`  Elements: ${totalElements}`);
  console.log(`  Screenshots: ${screenshots.length}`);
}

// CLI entry point
if (require.main === module) {
  const outputDir = process.argv[2] || './legacy-golden/discovery';

  if (!fs.existsSync(outputDir)) {
    console.error(`❌ Output directory not found: ${outputDir}`);
    process.exit(1);
  }

  generateBaselineIndex(outputDir);
}

module.exports = { generateBaselineIndex };
