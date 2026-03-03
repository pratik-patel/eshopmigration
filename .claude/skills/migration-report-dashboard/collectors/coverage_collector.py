"""
Test Coverage Collector
Parses test coverage reports from various formats
"""

import xml.etree.ElementTree as ET
import json
from pathlib import Path
from typing import Dict, Any
from collectors.base_collector import BaseCollector

class CoverageCollector(BaseCollector):
    """
    Collects test coverage metrics from coverage reports
    """

    def __init__(self, config: Any, app_type: str = "modern"):
        super().__init__(config, app_type)

        if app_type == "legacy":
            self.coverage_path = Path(config.collection.coverage.legacy_path)
        else:
            self.coverage_path = Path(config.collection.coverage.modern_path)

        self.format = config.collection.coverage.format

    def collect(self) -> Dict[str, Any]:
        """
        Parse coverage report

        Returns:
            Coverage metrics
        """
        if not self.coverage_path.exists():
            self.logger.warning(f"Coverage path not found: {self.coverage_path}")
            return self.get_empty_metrics()

        try:
            if self.format == 'lcov':
                return self.parse_lcov()
            elif self.format == 'cobertura':
                return self.parse_cobertura()
            elif self.format == 'jacoco':
                return self.parse_jacoco()
            else:
                self.logger.error(f"Unsupported coverage format: {self.format}")
                return self.get_empty_metrics()

        except Exception as e:
            self.logger.error(f"Error parsing coverage report: {e}")
            return self.get_empty_metrics()

    def parse_lcov(self) -> Dict[str, Any]:
        """
        Parse LCOV format coverage report

        Returns:
            Coverage metrics
        """
        lcov_file = self.coverage_path / 'lcov.info'

        if not lcov_file.exists():
            raise FileNotFoundError(f"lcov.info not found at {lcov_file}")

        lines_found = 0
        lines_hit = 0
        branches_found = 0
        branches_hit = 0
        functions_found = 0
        functions_hit = 0

        with open(lcov_file, 'r') as f:
            for line in f:
                line = line.strip()

                if line.startswith('LF:'):
                    lines_found += int(line.split(':')[1])
                elif line.startswith('LH:'):
                    lines_hit += int(line.split(':')[1])
                elif line.startswith('BRF:'):
                    branches_found += int(line.split(':')[1])
                elif line.startswith('BRH:'):
                    branches_hit += int(line.split(':')[1])
                elif line.startswith('FNF:'):
                    functions_found += int(line.split(':')[1])
                elif line.startswith('FNH:'):
                    functions_hit += int(line.split(':')[1])

        line_coverage = (lines_hit / lines_found * 100) if lines_found > 0 else 0
        branch_coverage = (branches_hit / branches_found * 100) if branches_found > 0 else 0
        function_coverage = (functions_hit / functions_found * 100) if functions_found > 0 else 0

        return {
            'total': round((line_coverage + branch_coverage + function_coverage) / 3, 2),
            'line': round(line_coverage, 2),
            'branch': round(branch_coverage, 2),
            'function': round(function_coverage, 2),
            'lines_covered': lines_hit,
            'lines_total': lines_found,
            'branches_covered': branches_hit,
            'branches_total': branches_found,
            'functions_covered': functions_hit,
            'functions_total': functions_found,
        }

    def parse_cobertura(self) -> Dict[str, Any]:
        """
        Parse Cobertura XML format

        Returns:
            Coverage metrics
        """
        xml_file = self.coverage_path / 'coverage.xml'

        if not xml_file.exists():
            raise FileNotFoundError(f"coverage.xml not found at {xml_file}")

        tree = ET.parse(xml_file)
        root = tree.getroot()

        line_rate = float(root.get('line-rate', 0))
        branch_rate = float(root.get('branch-rate', 0))

        lines_covered = int(root.get('lines-covered', 0))
        lines_valid = int(root.get('lines-valid', 0))
        branches_covered = int(root.get('branches-covered', 0))
        branches_valid = int(root.get('branches-valid', 0))

        return {
            'total': round((line_rate * 100 + branch_rate * 100) / 2, 2),
            'line': round(line_rate * 100, 2),
            'branch': round(branch_rate * 100, 2),
            'function': 0,  # Not available in Cobertura
            'lines_covered': lines_covered,
            'lines_total': lines_valid,
            'branches_covered': branches_covered,
            'branches_total': branches_valid,
            'functions_covered': 0,
            'functions_total': 0,
        }

    def parse_jacoco(self) -> Dict[str, Any]:
        """
        Parse JaCoCo XML format (Java)

        Returns:
            Coverage metrics
        """
        xml_file = self.coverage_path / 'jacoco.xml'

        if not xml_file.exists():
            raise FileNotFoundError(f"jacoco.xml not found at {xml_file}")

        tree = ET.parse(xml_file)
        root = tree.getroot()

        # Find counter elements
        line_counter = root.find(".//counter[@type='LINE']")
        branch_counter = root.find(".//counter[@type='BRANCH']")
        method_counter = root.find(".//counter[@type='METHOD']")

        def calc_coverage(counter):
            if counter is None:
                return 0, 0, 0
            covered = int(counter.get('covered', 0))
            missed = int(counter.get('missed', 0))
            total = covered + missed
            percentage = (covered / total * 100) if total > 0 else 0
            return covered, total, percentage

        lines_covered, lines_total, line_pct = calc_coverage(line_counter)
        branches_covered, branches_total, branch_pct = calc_coverage(branch_counter)
        methods_covered, methods_total, method_pct = calc_coverage(method_counter)

        return {
            'total': round((line_pct + branch_pct + method_pct) / 3, 2),
            'line': round(line_pct, 2),
            'branch': round(branch_pct, 2),
            'function': round(method_pct, 2),
            'lines_covered': lines_covered,
            'lines_total': lines_total,
            'branches_covered': branches_covered,
            'branches_total': branches_total,
            'functions_covered': methods_covered,
            'functions_total': methods_total,
        }

    def get_empty_metrics(self) -> Dict[str, Any]:
        """Return empty metrics structure"""
        return {
            'total': 0,
            'line': 0,
            'branch': 0,
            'function': 0,
            'lines_covered': 0,
            'lines_total': 0,
            'branches_covered': 0,
            'branches_total': 0,
            'functions_covered': 0,
            'functions_total': 0,
        }
