/**
 * Generate parity reports from verification results
 */

const fs = require('fs');
const path = require('path');

function generateParityReport(outputDir) {
  console.log(`📝 Generating parity reports for ${outputDir}`);

  // Load verification results
  const resultsPath = path.join(outputDir, 'parity-results.json');
  const matrixPath = path.join(outputDir, 'feature-matrix.json');

  if (!fs.existsSync(resultsPath)) {
    console.error('❌ Parity results not found. Run verification mode first.');
    process.exit(1);
  }

  const data = JSON.parse(fs.readFileSync(resultsPath, 'utf-8'));
  const { results, featureMatrix, parityScore } = data;

  // Generate feature-matrix.md
  generateFeatureMatrixMarkdown(outputDir, featureMatrix, parityScore);

  // Generate diff-report.html
  generateDiffReportHtml(outputDir, results, parityScore);

  // Generate issues.json (extract all issues)
  const allIssues = results.flatMap(r => r.issues.map(issue => ({
    screen: r.screen,
    legacyUrl: r.legacyUrl,
    modernUrl: r.modernUrl,
    issue,
    visualSimilarity: r.visualSimilarity
  })));

  const issuesPath = path.join(outputDir, 'issues.json');
  fs.writeFileSync(issuesPath, JSON.stringify(allIssues, null, 2));

  console.log(`✅ Generated parity reports`);
  console.log(`  Score: ${parityScore.toFixed(1)}%`);
  console.log(`  Issues: ${allIssues.length}`);
}

function generateFeatureMatrixMarkdown(outputDir, featureMatrix, parityScore) {
  const statusEmoji = parityScore >= 90 ? '✅' : parityScore >= 70 ? '🟡' : '🔴';

  const markdown = `# Feature Parity Matrix

**Generated:** ${new Date().toISOString()}
**Parity Score:** ${statusEmoji} ${parityScore.toFixed(1)}%

---

## Overall Assessment

| Status | Criteria |
|--------|----------|
| ${parityScore >= 90 ? '✅' : '❌'} | Feature Completeness ≥ 90% |
| ${parityScore >= 85 ? '✅' : '❌'} | Visual Consistency ≥ 85% |
| ${parityScore >= 85 ? '✅' : '❌'} | Data Accuracy ≥ 85% |
| ${parityScore >= 80 ? '✅' : '❌'} | Workflow Equivalence ≥ 80% |

---

## Feature Comparison

| Feature | Legacy | Modern | Behavior Match | Notes |
|---------|--------|--------|----------------|-------|
${featureMatrix.map(f => `| ${f.feature} | ${f.legacyPresent ? '✅' : '❌'} | ${f.modernPresent ? '✅' : '❌'} | ${f.behaviorMatch ? '✅' : '❌'} | ${f.notes || '-'} |`).join('\n')}

---

## Summary by Category

### Buttons
${generateCategorySummary(featureMatrix, 'Button')}

### Input Fields
${generateCategorySummary(featureMatrix, 'Input')}

### Data Grids
${generateCategorySummary(featureMatrix, 'Grid')}

### Navigation
${generateCategorySummary(featureMatrix, 'Navigation')}

---

## Missing Features

Features present in legacy but missing in modern:

${featureMatrix
  .filter(f => f.legacyPresent && !f.modernPresent)
  .map((f, i) => `${i + 1}. **${f.feature}** — ${f.notes}`)
  .join('\n') || '_None_'}

---

## Behavioral Differences

Features present in both but with behavior mismatch:

${featureMatrix
  .filter(f => f.legacyPresent && f.modernPresent && !f.behaviorMatch)
  .map((f, i) => `${i + 1}. **${f.feature}** — ${f.notes}`)
  .join('\n') || '_None_'}

---

## Recommendations

${parityScore >= 90 ? `
✅ **Excellent parity** — Ready for production deployment
- Continue with user acceptance testing
- Monitor for edge cases in production
` : parityScore >= 70 ? `
🟡 **Good parity with minor gaps** — Address missing features before release
- Review missing features list
- Implement high-priority items
- Document approved differences in evidence.md
` : `
🔴 **Significant gaps** — Not ready for production
- Critical features missing
- Behavioral differences need investigation
- Consider additional development sprints
`}

---

## Approved Differences

Document any intentional differences between legacy and modern (approved by product owner):

_[To be filled by team]_

---

## Files

- \`parity-results.json\` — Detailed verification results
- \`issues.json\` — All detected issues
- \`diff-report.html\` — Visual comparison report
- \`screenshots/\` — Side-by-side screenshots

---

## Next Steps

1. **Review Issues**: Address high-priority gaps
2. **User Testing**: Validate with actual users
3. **Document Decisions**: Record approved differences
4. **Re-verify**: Run parity tests after fixes
5. **Sign-off**: Obtain stakeholder approval for deployment
`;

  const matrixPath = path.join(outputDir, 'feature-matrix.md');
  fs.writeFileSync(matrixPath, markdown);
  console.log(`  ✓ ${matrixPath}`);
}

function generateCategorySummary(featureMatrix, category) {
  const features = featureMatrix.filter(f => f.feature.startsWith(category));

  if (features.length === 0) return '_No features in this category_';

  const total = features.length;
  const present = features.filter(f => f.modernPresent).length;
  const behaviorMatch = features.filter(f => f.behaviorMatch).length;

  return `
- Total: ${total}
- Present in modern: ${present} (${((present / total) * 100).toFixed(0)}%)
- Behavior match: ${behaviorMatch} (${((behaviorMatch / total) * 100).toFixed(0)}%)
`;
}

function generateDiffReportHtml(outputDir, results, parityScore) {
  const html = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Parity Verification Report</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
      background: #f5f5f5;
      padding: 2rem;
    }
    .header {
      background: white;
      padding: 2rem;
      border-radius: 8px;
      margin-bottom: 2rem;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .header h1 { margin-bottom: 1rem; color: #333; }
    .score {
      font-size: 3rem;
      font-weight: bold;
      color: ${parityScore >= 90 ? '#10b981' : parityScore >= 70 ? '#f59e0b' : '#ef4444'};
    }
    .comparison-grid {
      display: grid;
      gap: 2rem;
    }
    .comparison {
      background: white;
      padding: 1.5rem;
      border-radius: 8px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .comparison h2 {
      margin-bottom: 1rem;
      color: #333;
      font-size: 1.25rem;
    }
    .screenshots {
      display: grid;
      grid-template-columns: 1fr 1fr 1fr;
      gap: 1rem;
      margin-top: 1rem;
    }
    .screenshot {
      text-align: center;
    }
    .screenshot img {
      width: 100%;
      border: 1px solid #ddd;
      border-radius: 4px;
    }
    .screenshot-label {
      margin-top: 0.5rem;
      font-size: 0.875rem;
      color: #666;
      font-weight: 600;
    }
    .metrics {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 1rem;
      margin: 1rem 0;
    }
    .metric {
      background: #f9fafb;
      padding: 1rem;
      border-radius: 4px;
      text-align: center;
    }
    .metric-value {
      font-size: 1.5rem;
      font-weight: bold;
      color: #333;
    }
    .metric-label {
      font-size: 0.875rem;
      color: #666;
      margin-top: 0.25rem;
    }
    .issues {
      background: #fef2f2;
      border: 1px solid #fecaca;
      border-radius: 4px;
      padding: 1rem;
      margin-top: 1rem;
    }
    .issues h3 {
      color: #dc2626;
      font-size: 1rem;
      margin-bottom: 0.5rem;
    }
    .issues ul {
      list-style: none;
      padding-left: 0;
    }
    .issues li {
      padding: 0.5rem 0;
      border-bottom: 1px solid #fecaca;
      color: #991b1b;
    }
    .issues li:last-child {
      border-bottom: none;
    }
    .urls {
      font-size: 0.875rem;
      color: #666;
      margin-top: 0.5rem;
    }
    .urls span {
      display: inline-block;
      margin-right: 1rem;
    }
  </style>
</head>
<body>
  <div class="header">
    <h1>🔍 Parity Verification Report</h1>
    <div class="score">${parityScore.toFixed(1)}%</div>
    <p style="margin-top: 0.5rem; color: #666;">
      Generated: ${new Date().toISOString()}
    </p>
  </div>

  <div class="comparison-grid">
    ${results.map((result, index) => `
      <div class="comparison">
        <h2>${index + 1}. ${result.screen}</h2>

        <div class="urls">
          <span><strong>Legacy:</strong> ${result.legacyUrl}</span>
          <span><strong>Modern:</strong> ${result.modernUrl}</span>
        </div>

        <div class="metrics">
          <div class="metric">
            <div class="metric-value">${result.visualSimilarity.toFixed(1)}%</div>
            <div class="metric-label">Visual Match</div>
          </div>
          <div class="metric">
            <div class="metric-value">${result.elementsMatch ? '✅' : '❌'}</div>
            <div class="metric-label">Elements</div>
          </div>
          <div class="metric">
            <div class="metric-value">${result.dataParity ? '✅' : '❌'}</div>
            <div class="metric-label">Data</div>
          </div>
        </div>

        <div class="screenshots">
          <div class="screenshot">
            <img src="screenshots/${result.screenshots.legacy}" alt="Legacy">
            <div class="screenshot-label">Legacy</div>
          </div>
          <div class="screenshot">
            <img src="screenshots/${result.screenshots.modern}" alt="Modern">
            <div class="screenshot-label">Modern</div>
          </div>
          <div class="screenshot">
            <img src="screenshots/${result.screenshots.diff}" alt="Diff">
            <div class="screenshot-label">Difference</div>
          </div>
        </div>

        ${result.issues.length > 0 ? `
          <div class="issues">
            <h3>⚠️ Issues (${result.issues.length})</h3>
            <ul>
              ${result.issues.map(issue => `<li>${issue}</li>`).join('')}
            </ul>
          </div>
        ` : '<div style="color: #10b981; margin-top: 1rem;">✅ No issues detected</div>'}
      </div>
    `).join('')}
  </div>
</body>
</html>`;

  const reportPath = path.join(outputDir, 'diff-report.html');
  fs.writeFileSync(reportPath, html);
  console.log(`  ✓ ${reportPath}`);
}

// CLI entry point
if (require.main === module) {
  const outputDir = process.argv[2] || './tests/parity';

  if (!fs.existsSync(outputDir)) {
    console.error(`❌ Output directory not found: ${outputDir}`);
    process.exit(1);
  }

  generateParityReport(outputDir);
}

module.exports = { generateParityReport };
