"""
Lighthouse Metrics Collector
Runs Lighthouse audits and collects performance, accessibility, and SEO metrics
"""

import subprocess
import json
import tempfile
from pathlib import Path
from typing import Dict, Any
from collectors.base_collector import BaseCollector

class LighthouseCollector(BaseCollector):
    """
    Collects Lighthouse audit metrics for web applications
    """

    def __init__(self, config: Any, app_type: str = "modern"):
        super().__init__(config, app_type)

        if app_type == "legacy":
            self.url = config.legacy.frontend_url
        else:
            self.url = config.modern.frontend_url

        self.runs = config.collection.lighthouse.runs
        self.throttling = config.collection.lighthouse.throttling
        self.categories = config.collection.lighthouse.categories

    def collect(self) -> Dict[str, Any]:
        """
        Run Lighthouse audits and aggregate results

        Returns:
            Aggregated Lighthouse metrics
        """
        all_results = []

        for i in range(self.runs):
            self.logger.info(f"Running Lighthouse audit {i+1}/{self.runs} for {self.url}")
            result = self.run_lighthouse()
            if result:
                all_results.append(result)

        if not all_results:
            raise Exception(f"All Lighthouse runs failed for {self.url}")

        # Average the results
        aggregated = self.aggregate_results(all_results)
        return aggregated

    def run_lighthouse(self) -> Dict[str, Any]:
        """
        Run single Lighthouse audit

        Returns:
            Lighthouse audit results
        """
        try:
            # Create temporary file for output
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
                output_path = tmp.name

            # Build Lighthouse command
            cmd = [
                'npx', 'lighthouse',
                self.url,
                f'--throttling-method={self.throttling}',
                '--output=json',
                f'--output-path={output_path}',
                '--quiet',
                '--chrome-flags="--headless --no-sandbox"'
            ]

            # Add categories
            for category in self.categories:
                cmd.append(f'--only-categories={category}')

            # Run Lighthouse
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode != 0:
                self.logger.error(f"Lighthouse failed: {result.stderr}")
                return {}

            # Read results
            with open(output_path, 'r') as f:
                lighthouse_data = json.load(f)

            # Clean up
            Path(output_path).unlink()

            return self.parse_lighthouse_output(lighthouse_data)

        except subprocess.TimeoutExpired:
            self.logger.error("Lighthouse timed out")
            return {}
        except Exception as e:
            self.logger.error(f"Error running Lighthouse: {e}")
            return {}

    def parse_lighthouse_output(self, data: Dict) -> Dict[str, Any]:
        """
        Parse Lighthouse JSON output

        Args:
            data: Raw Lighthouse output

        Returns:
            Parsed metrics
        """
        categories = data.get('categories', {})
        audits = data.get('audits', {})

        metrics = {
            # Category scores (0-100)
            'performance': int(categories.get('performance', {}).get('score', 0) * 100),
            'accessibility': int(categories.get('accessibility', {}).get('score', 0) * 100),
            'best_practices': int(categories.get('best-practices', {}).get('score', 0) * 100),
            'seo': int(categories.get('seo', {}).get('score', 0) * 100),

            # Performance metrics
            'first_contentful_paint_ms': int(audits.get('first-contentful-paint', {}).get('numericValue', 0)),
            'largest_contentful_paint_ms': int(audits.get('largest-contentful-paint', {}).get('numericValue', 0)),
            'time_to_interactive_ms': int(audits.get('interactive', {}).get('numericValue', 0)),
            'speed_index_ms': int(audits.get('speed-index', {}).get('numericValue', 0)),
            'total_blocking_time_ms': int(audits.get('total-blocking-time', {}).get('numericValue', 0)),
            'cumulative_layout_shift': float(audits.get('cumulative-layout-shift', {}).get('numericValue', 0)),

            # Resource metrics
            'total_byte_weight': audits.get('total-byte-weight', {}).get('numericValue', 0),
            'dom_size': audits.get('dom-size', {}).get('numericValue', 0),

            # Accessibility issues
            'accessibility_issues': self.extract_accessibility_issues(audits),

            # Best practices issues
            'best_practices_issues': self.extract_best_practices_issues(audits),
        }

        return metrics

    def extract_accessibility_issues(self, audits: Dict) -> list:
        """Extract accessibility violations from audits"""
        issues = []

        a11y_audits = {
            'aria-allowed-attr': 'critical',
            'aria-required-attr': 'critical',
            'button-name': 'serious',
            'color-contrast': 'serious',
            'image-alt': 'serious',
            'label': 'serious',
            'link-name': 'serious',
            'document-title': 'moderate',
            'html-has-lang': 'moderate',
            'valid-lang': 'moderate',
        }

        for audit_id, severity in a11y_audits.items():
            audit = audits.get(audit_id, {})
            if audit.get('score', 1) < 1:
                issues.append({
                    'audit': audit_id,
                    'title': audit.get('title', ''),
                    'description': audit.get('description', ''),
                    'severity': severity
                })

        return issues

    def extract_best_practices_issues(self, audits: Dict) -> list:
        """Extract best practices violations from audits"""
        issues = []

        bp_audits = [
            'errors-in-console',
            'is-on-https',
            'uses-http2',
            'uses-passive-event-listeners',
            'no-document-write',
            'geolocation-on-start',
            'notification-on-start',
        ]

        for audit_id in bp_audits:
            audit = audits.get(audit_id, {})
            if audit.get('score', 1) < 1:
                issues.append({
                    'audit': audit_id,
                    'title': audit.get('title', ''),
                    'description': audit.get('description', '')
                })

        return issues

    def aggregate_results(self, results: list) -> Dict[str, Any]:
        """
        Aggregate multiple Lighthouse runs

        Args:
            results: List of Lighthouse run results

        Returns:
            Aggregated metrics (median/average)
        """
        if len(results) == 1:
            return results[0]

        # Take median for scores
        aggregated = {}

        numeric_keys = [
            'performance', 'accessibility', 'best_practices', 'seo',
            'first_contentful_paint_ms', 'largest_contentful_paint_ms',
            'time_to_interactive_ms', 'speed_index_ms', 'total_blocking_time_ms',
            'cumulative_layout_shift', 'total_byte_weight', 'dom_size'
        ]

        for key in numeric_keys:
            values = [r[key] for r in results if key in r]
            if values:
                # Use median
                values.sort()
                mid = len(values) // 2
                aggregated[key] = values[mid]

        # Merge issues (take from first run)
        aggregated['accessibility_issues'] = results[0].get('accessibility_issues', [])
        aggregated['best_practices_issues'] = results[0].get('best_practices_issues', [])

        return aggregated
