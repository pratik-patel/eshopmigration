/**
 * Browser Agent - Verification Mode
 * Parity testing between legacy and modern applications
 */

import { test, expect, Page } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';
import { PNG } from 'pngjs';
import pixelmatch from 'pixelmatch';

interface ParityResult {
  screen: string;
  legacyUrl: string;
  modernUrl: string;
  visualSimilarity: number;
  elementsMatch: boolean;
  dataParity: boolean;
  issues: string[];
  screenshots: {
    legacy: string;
    modern: string;
    diff: string;
  };
}

interface FeatureParityMatrix {
  feature: string;
  legacyPresent: boolean;
  modernPresent: boolean;
  behaviorMatch: boolean;
  notes: string;
}

class ParityVerifier {
  private legacyPage: Page;
  private modernPage: Page;
  private legacyUrl: string;
  private modernUrl: string;
  private outputDir: string;
  private results: ParityResult[] = [];
  private featureMatrix: FeatureParityMatrix[] = [];

  constructor(
    legacyPage: Page,
    modernPage: Page,
    legacyUrl: string,
    modernUrl: string,
    outputDir: string
  ) {
    this.legacyPage = legacyPage;
    this.modernPage = modernPage;
    this.legacyUrl = legacyUrl;
    this.modernUrl = modernUrl;
    this.outputDir = outputDir;
  }

  async verifyParity(workflows: any[]): Promise<ParityResult[]> {
    console.log(`🔍 Starting parity verification`);
    console.log(`  Legacy: ${this.legacyUrl}`);
    console.log(`  Modern: ${this.modernUrl}`);

    // Load baseline workflows
    const baselineDir = process.env.BASELINE_DIR || './legacy-golden';
    const workflowsPath = path.join(baselineDir, 'workflows.json');

    if (!fs.existsSync(workflowsPath)) {
      console.error(`❌ No baseline workflows found at ${workflowsPath}`);
      console.log('   Run discovery mode first: /browser-agent discovery');
      return [];
    }

    const baselineWorkflows = JSON.parse(fs.readFileSync(workflowsPath, 'utf-8'));
    console.log(`📋 Found ${baselineWorkflows.length} baseline workflows`);

    // Verify each workflow
    for (const workflow of baselineWorkflows.slice(0, 10)) { // Limit to avoid timeout
      await this.verifyWorkflow(workflow);
    }

    // Generate parity score
    const score = this.calculateParityScore();
    console.log(`\n📊 Parity Score: ${score.toFixed(1)}%`);

    return this.results;
  }

  async verifyWorkflow(workflow: any): Promise<void> {
    console.log(`\n🔄 Verifying workflow: ${workflow.name}`);

    try {
      // Navigate both apps to starting point
      await this.legacyPage.goto(this.legacyUrl, { waitUntil: 'networkidle' });
      await this.modernPage.goto(this.modernUrl, { waitUntil: 'networkidle' });

      // Execute workflow steps
      for (const step of workflow.steps) {
        if (step.action === 'click') {
          try {
            await this.legacyPage.click(step.target, { timeout: 5000 });
            await this.modernPage.click(step.target, { timeout: 5000 });
            await Promise.all([
              this.legacyPage.waitForTimeout(500),
              this.modernPage.waitForTimeout(500)
            ]);
          } catch (error: any) {
            console.log(`  ⚠️  Could not execute step: ${step.description} - ${error.message}`);
          }
        }
      }

      // Compare final state
      const result = await this.comparePages(
        workflow.name,
        this.legacyPage.url(),
        this.modernPage.url()
      );

      this.results.push(result);

      console.log(`  Visual Similarity: ${result.visualSimilarity.toFixed(1)}%`);
      console.log(`  Elements Match: ${result.elementsMatch ? '✅' : '❌'}`);
      console.log(`  Data Parity: ${result.dataParity ? '✅' : '❌'}`);

      if (result.issues.length > 0) {
        console.log(`  Issues: ${result.issues.length}`);
        result.issues.forEach(issue => console.log(`    - ${issue}`));
      }

    } catch (error: any) {
      console.error(`  ❌ Error verifying workflow: ${error.message}`);
    }
  }

  async comparePages(
    screenName: string,
    legacyUrl: string,
    modernUrl: string
  ): Promise<ParityResult> {
    const result: ParityResult = {
      screen: screenName,
      legacyUrl,
      modernUrl,
      visualSimilarity: 0,
      elementsMatch: false,
      dataParity: false,
      issues: [],
      screenshots: {
        legacy: '',
        modern: '',
        diff: ''
      }
    };

    try {
      // Capture screenshots
      const timestamp = Date.now();
      const legacyScreenshot = path.join(this.outputDir, 'screenshots', `legacy_${screenName}_${timestamp}.png`);
      const modernScreenshot = path.join(this.outputDir, 'screenshots', `modern_${screenName}_${timestamp}.png`);
      const diffScreenshot = path.join(this.outputDir, 'screenshots', `diff_${screenName}_${timestamp}.png`);

      await this.legacyPage.screenshot({ path: legacyScreenshot, fullPage: true });
      await this.modernPage.screenshot({ path: modernScreenshot, fullPage: true });

      result.screenshots = {
        legacy: path.basename(legacyScreenshot),
        modern: path.basename(modernScreenshot),
        diff: path.basename(diffScreenshot)
      };

      // Visual comparison
      try {
        const similarity = await this.compareScreenshots(
          legacyScreenshot,
          modernScreenshot,
          diffScreenshot
        );
        result.visualSimilarity = similarity;

        if (similarity < 85) {
          result.issues.push(`Visual similarity below threshold: ${similarity.toFixed(1)}%`);
        }
      } catch (error: any) {
        result.issues.push(`Visual comparison failed: ${error.message}`);
      }

      // Element comparison
      const elementComparison = await this.compareElements();
      result.elementsMatch = elementComparison.match;
      result.issues.push(...elementComparison.issues);

      // Data comparison (if grids present)
      const dataComparison = await this.compareGridData();
      result.dataParity = dataComparison.match;
      result.issues.push(...dataComparison.issues);

    } catch (error: any) {
      result.issues.push(`Comparison error: ${error.message}`);
    }

    return result;
  }

  async compareScreenshots(
    legacyPath: string,
    modernPath: string,
    diffPath: string
  ): Promise<number> {
    try {
      const img1 = PNG.sync.read(fs.readFileSync(legacyPath));
      const img2 = PNG.sync.read(fs.readFileSync(modernPath));

      // Resize to match dimensions if needed
      const width = Math.min(img1.width, img2.width);
      const height = Math.min(img1.height, img2.height);

      const diff = new PNG({ width, height });

      const mismatchedPixels = pixelmatch(
        img1.data,
        img2.data,
        diff.data,
        width,
        height,
        { threshold: 0.1 }
      );

      // Save diff image
      fs.writeFileSync(diffPath, PNG.sync.write(diff));

      // Calculate similarity percentage
      const totalPixels = width * height;
      const similarity = ((totalPixels - mismatchedPixels) / totalPixels) * 100;

      return similarity;
    } catch (error: any) {
      console.error(`Screenshot comparison error: ${error.message}`);
      return 0;
    }
  }

  async compareElements(): Promise<{ match: boolean; issues: string[] }> {
    const issues: string[] = [];

    try {
      // Get interactive elements from both pages
      const legacyElements = await this.getInteractiveElements(this.legacyPage);
      const modernElements = await this.getInteractiveElements(this.modernPage);

      // Compare button counts
      const legacyButtons = legacyElements.filter(e => e.type === 'button').length;
      const modernButtons = modernElements.filter(e => e.type === 'button').length;

      if (legacyButtons !== modernButtons) {
        issues.push(`Button count mismatch: Legacy=${legacyButtons}, Modern=${modernButtons}`);
      }

      // Compare input counts
      const legacyInputs = legacyElements.filter(e => e.type.startsWith('input')).length;
      const modernInputs = modernElements.filter(e => e.type.startsWith('input')).length;

      if (legacyInputs !== modernInputs) {
        issues.push(`Input count mismatch: Legacy=${legacyInputs}, Modern=${modernInputs}`);
      }

      // Compare table counts
      const legacyTables = legacyElements.filter(e => e.type === 'table').length;
      const modernTables = modernElements.filter(e => e.type === 'table').length;

      if (legacyTables !== modernTables) {
        issues.push(`Table count mismatch: Legacy=${legacyTables}, Modern=${modernTables}`);
      }

      // Check for missing critical buttons
      const legacyButtonTexts = legacyElements
        .filter(e => e.type === 'button')
        .map(e => e.text.toLowerCase().trim());

      const modernButtonTexts = modernElements
        .filter(e => e.type === 'button')
        .map(e => e.text.toLowerCase().trim());

      const missingButtons = legacyButtonTexts.filter(
        text => text && !modernButtonTexts.includes(text)
      );

      if (missingButtons.length > 0) {
        issues.push(`Missing buttons in modern app: ${missingButtons.join(', ')}`);
      }

      // Update feature matrix
      legacyElements.forEach(legacyEl => {
        if (legacyEl.type === 'button' && legacyEl.text) {
          const modernHas = modernElements.some(
            m => m.type === 'button' && m.text.toLowerCase() === legacyEl.text.toLowerCase()
          );

          this.featureMatrix.push({
            feature: `Button: ${legacyEl.text}`,
            legacyPresent: true,
            modernPresent: modernHas,
            behaviorMatch: modernHas, // Simplified assumption
            notes: modernHas ? '' : 'Missing in modern app'
          });
        }
      });

      return {
        match: issues.length === 0,
        issues
      };

    } catch (error: any) {
      return {
        match: false,
        issues: [`Element comparison failed: ${error.message}`]
      };
    }
  }

  async compareGridData(): Promise<{ match: boolean; issues: string[] }> {
    const issues: string[] = [];

    try {
      const legacyGrids = await this.extractAllGridData(this.legacyPage);
      const modernGrids = await this.extractAllGridData(this.modernPage);

      if (legacyGrids.length !== modernGrids.length) {
        issues.push(`Grid count mismatch: Legacy=${legacyGrids.length}, Modern=${modernGrids.length}`);
      }

      // Compare each grid
      for (let i = 0; i < Math.min(legacyGrids.length, modernGrids.length); i++) {
        const legacy = legacyGrids[i];
        const modern = modernGrids[i];

        // Compare column counts
        if (legacy.headers.length !== modern.headers.length) {
          issues.push(`Grid ${i + 1}: Column count mismatch (${legacy.headers.length} vs ${modern.headers.length})`);
        }

        // Compare row counts (with tolerance)
        const rowDiff = Math.abs(legacy.rows.length - modern.rows.length);
        if (rowDiff > 2) { // Allow small differences due to pagination
          issues.push(`Grid ${i + 1}: Row count mismatch (${legacy.rows.length} vs ${modern.rows.length})`);
        }

        // Sample data comparison (first row)
        if (legacy.rows.length > 0 && modern.rows.length > 0) {
          const legacyFirstRow = legacy.rows[0].join('|');
          const modernFirstRow = modern.rows[0].join('|');

          if (legacyFirstRow !== modernFirstRow) {
            issues.push(`Grid ${i + 1}: First row data mismatch`);
          }
        }
      }

      return {
        match: issues.length === 0,
        issues
      };

    } catch (error: any) {
      return {
        match: false,
        issues: [`Grid comparison failed: ${error.message}`]
      };
    }
  }

  async getInteractiveElements(page: Page): Promise<any[]> {
    const elements: any[] = [];

    try {
      // Buttons
      const buttons = await page.$$('button, input[type="submit"], input[type="button"]');
      for (const btn of buttons) {
        if (await btn.isVisible()) {
          const text = await btn.textContent() || await btn.getAttribute('value') || '';
          elements.push({ type: 'button', text: text.trim() });
        }
      }

      // Inputs
      const inputs = await page.$$('input:not([type="submit"]):not([type="button"]), textarea, select');
      for (const input of inputs) {
        if (await input.isVisible()) {
          const type = await input.getAttribute('type') || 'text';
          elements.push({ type: `input_${type}`, text: '' });
        }
      }

      // Tables
      const tables = await page.$$('table, [role="grid"]');
      for (let i = 0; i < tables.length; i++) {
        elements.push({ type: 'table', text: `Table ${i + 1}` });
      }

    } catch (error: any) {
      console.error(`Error getting elements: ${error.message}`);
    }

    return elements;
  }

  async extractAllGridData(page: Page): Promise<any[]> {
    const grids = [];

    try {
      const tables = await page.$$('table, [role="grid"]');

      for (let i = 0; i < tables.length; i++) {
        const data = await page.evaluate((index) => {
          const table = document.querySelectorAll('table, [role="grid"]')[index];
          if (!table) return null;

          const headers: string[] = [];
          const rows: string[][] = [];

          // Extract headers
          table.querySelectorAll('th').forEach(cell =>
            headers.push(cell.textContent?.trim() || '')
          );

          // Extract rows (first 5)
          const dataRows = table.querySelectorAll('tbody tr, tr');
          for (let j = 0; j < Math.min(5, dataRows.length); j++) {
            const row: string[] = [];
            dataRows[j].querySelectorAll('td').forEach(cell =>
              row.push(cell.textContent?.trim() || '')
            );
            if (row.length > 0) rows.push(row);
          }

          return { headers, rows };
        }, i);

        if (data && data.rows.length > 0) {
          grids.push(data);
        }
      }
    } catch (error: any) {
      console.error(`Error extracting grid data: ${error.message}`);
    }

    return grids;
  }

  calculateParityScore(): number {
    if (this.results.length === 0) return 0;

    const weights = {
      visualSimilarity: 0.2,
      elementsMatch: 0.4,
      dataParity: 0.3,
      workflowComplete: 0.1
    };

    let totalScore = 0;

    for (const result of this.results) {
      let score = 0;
      score += result.visualSimilarity * weights.visualSimilarity;
      score += (result.elementsMatch ? 100 : 0) * weights.elementsMatch;
      score += (result.dataParity ? 100 : 0) * weights.dataParity;
      score += (result.issues.length === 0 ? 100 : 50) * weights.workflowComplete;
      totalScore += score;
    }

    return totalScore / this.results.length;
  }

  getResults() {
    return {
      results: this.results,
      featureMatrix: this.featureMatrix,
      parityScore: this.calculateParityScore()
    };
  }
}

// Main test suite
test.describe('Parity Verification', () => {
  test('verify legacy vs modern parity', async ({ browser }) => {
    const legacyUrl = process.env.LEGACY_URL || 'http://localhost:8080';
    const modernUrl = process.env.MODERN_URL || 'http://localhost:5173';
    const outputDir = process.env.OUTPUT_DIR || './tests/parity';

    // Create output directories
    fs.mkdirSync(path.join(outputDir, 'screenshots'), { recursive: true });

    // Create separate pages
    const legacyContext = await browser.newContext({ viewport: { width: 1920, height: 1080 } });
    const modernContext = await browser.newContext({ viewport: { width: 1920, height: 1080 } });

    const legacyPage = await legacyContext.newPage();
    const modernPage = await modernContext.newPage();

    const verifier = new ParityVerifier(legacyPage, modernPage, legacyUrl, modernUrl, outputDir);

    // Run verification
    await verifier.verifyParity([]);

    // Get results
    const results = verifier.getResults();

    // Save results
    const resultsPath = path.join(outputDir, 'parity-results.json');
    fs.writeFileSync(resultsPath, JSON.stringify(results, null, 2));

    // Save feature matrix
    const matrixPath = path.join(outputDir, 'feature-matrix.json');
    fs.writeFileSync(matrixPath, JSON.stringify(results.featureMatrix, null, 2));

    console.log(`\n✅ Parity verification complete`);
    console.log(`   Score: ${results.parityScore.toFixed(1)}%`);
    console.log(`   Results: ${resultsPath}`);

    // Cleanup
    await legacyContext.close();
    await modernContext.close();

    // Assert minimum parity
    expect(results.parityScore).toBeGreaterThan(70);
  });
});
