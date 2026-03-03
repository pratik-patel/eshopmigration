"""
SonarQube Metrics Collector
Fetches code quality metrics from SonarQube server
"""

import requests
from typing import Dict, Any
from collectors.base_collector import BaseCollector

class SonarQubeCollector(BaseCollector):
    """
    Collects quality metrics from SonarQube
    """

    def __init__(self, config: Any, app_type: str = "modern"):
        super().__init__(config, app_type)

        if app_type == "legacy":
            self.project_key = config.legacy.sonarqube_project
        else:
            self.project_key = config.modern.sonarqube_project

        self.sonar_url = config.sonarqube.url
        self.sonar_token = config.sonarqube.token

    def collect(self) -> Dict[str, Any]:
        """
        Fetch SonarQube metrics

        Returns:
            Quality metrics from SonarQube
        """
        if not self.sonar_token or self.sonar_token.startswith('${'):
            self.logger.warning("SonarQube token not configured")
            return self.get_empty_metrics()

        try:
            # Fetch measures
            measures = self.fetch_measures()

            # Fetch issues
            issues = self.fetch_issues()

            # Combine into metrics
            metrics = {
                'reliability_rating': measures.get('reliability_rating', 'C'),
                'security_rating': measures.get('security_rating', 'C'),
                'maintainability_rating': measures.get('sqale_rating', 'C'),
                'coverage': float(measures.get('coverage', 0)),
                'duplicated_lines_density': float(measures.get('duplicated_lines_density', 0)),
                'bugs': int(measures.get('bugs', 0)),
                'vulnerabilities': int(measures.get('vulnerabilities', 0)),
                'code_smells': int(measures.get('code_smells', 0)),
                'technical_debt_minutes': int(measures.get('sqale_index', 0)),
                'lines_of_code': int(measures.get('ncloc', 0)),
                'complexity': int(measures.get('complexity', 0)),
                'cognitive_complexity': int(measures.get('cognitive_complexity', 0)),
                'issues_by_severity': issues,
            }

            return metrics

        except Exception as e:
            self.logger.error(f"Error fetching SonarQube metrics: {e}")
            return self.get_empty_metrics()

    def fetch_measures(self) -> Dict[str, str]:
        """
        Fetch measures from SonarQube API

        Returns:
            Dictionary of metric values
        """
        url = f"{self.sonar_url}/api/measures/component"

        metrics = [
            'reliability_rating', 'security_rating', 'sqale_rating',
            'coverage', 'duplicated_lines_density',
            'bugs', 'vulnerabilities', 'code_smells',
            'sqale_index', 'ncloc', 'complexity', 'cognitive_complexity'
        ]

        params = {
            'component': self.project_key,
            'metricKeys': ','.join(metrics)
        }

        response = requests.get(
            url,
            params=params,
            auth=(self.sonar_token, ''),
            timeout=30
        )

        if response.status_code != 200:
            raise Exception(f"SonarQube API returned {response.status_code}")

        data = response.json()

        measures_dict = {}
        for measure in data.get('component', {}).get('measures', []):
            measures_dict[measure['metric']] = measure.get('value', '0')

        return measures_dict

    def fetch_issues(self) -> Dict[str, int]:
        """
        Fetch issues count by severity

        Returns:
            Dictionary with counts per severity
        """
        url = f"{self.sonar_url}/api/issues/search"

        severities = ['BLOCKER', 'CRITICAL', 'MAJOR', 'MINOR', 'INFO']
        issues_by_severity = {}

        for severity in severities:
            params = {
                'componentKeys': self.project_key,
                'severities': severity,
                'ps': 1  # Just get count
            }

            try:
                response = requests.get(
                    url,
                    params=params,
                    auth=(self.sonar_token, ''),
                    timeout=30
                )

                if response.status_code == 200:
                    data = response.json()
                    issues_by_severity[severity.lower()] = data.get('total', 0)
                else:
                    issues_by_severity[severity.lower()] = 0

            except Exception as e:
                self.logger.warning(f"Error fetching {severity} issues: {e}")
                issues_by_severity[severity.lower()] = 0

        return issues_by_severity

    def get_empty_metrics(self) -> Dict[str, Any]:
        """Return empty metrics structure"""
        return {
            'reliability_rating': 'C',
            'security_rating': 'C',
            'maintainability_rating': 'C',
            'coverage': 0.0,
            'duplicated_lines_density': 0.0,
            'bugs': 0,
            'vulnerabilities': 0,
            'code_smells': 0,
            'technical_debt_minutes': 0,
            'lines_of_code': 0,
            'complexity': 0,
            'cognitive_complexity': 0,
            'issues_by_severity': {
                'blocker': 0,
                'critical': 0,
                'major': 0,
                'minor': 0,
                'info': 0
            }
        }
