"""
API Metrics Collector
Discovers and tests API endpoints, measures response times
"""

import requests
import time
from typing import Dict, Any, List
from collections import defaultdict
from statistics import mean, median
from collectors.base_collector import BaseCollector

class APICollector(BaseCollector):
    """
    Collects API metrics from backend applications
    """

    def __init__(self, config: Any, app_type: str = "modern"):
        super().__init__(config, app_type)

        if app_type == "legacy":
            self.base_url = config.legacy.backend_url
        else:
            self.base_url = config.modern.backend_url

        self.timeout = config.collection.api.timeout
        self.retries = config.collection.api.retries
        self.verify_ssl = config.collection.api.verify_ssl

    def collect(self) -> Dict[str, Any]:
        """
        Discover and test API endpoints

        Returns:
            API metrics including endpoints, response times, errors
        """
        # Discover endpoints
        endpoints = self.discover_endpoints()

        if not endpoints:
            self.logger.warning(f"No endpoints discovered for {self.base_url}")
            return self.get_empty_metrics()

        # Test each endpoint
        results = []
        for endpoint in endpoints:
            result = self.test_endpoint(endpoint)
            results.append(result)

        # Aggregate metrics
        metrics = self.aggregate_endpoint_results(results)
        metrics['endpoints'] = results

        return metrics

    def discover_endpoints(self) -> List[Dict[str, str]]:
        """
        Discover API endpoints

        Returns:
            List of endpoint definitions
        """
        endpoints = []

        # Try to fetch OpenAPI/Swagger spec
        swagger_urls = [
            f"{self.base_url}/swagger/v1/swagger.json",
            f"{self.base_url}/swagger.json",
            f"{self.base_url}/api-docs",
            f"{self.base_url}/openapi.json",
        ]

        for url in swagger_urls:
            try:
                response = requests.get(url, timeout=5, verify=self.verify_ssl)
                if response.status_code == 200:
                    spec = response.json()
                    endpoints = self.parse_openapi_spec(spec)
                    self.logger.info(f"Discovered {len(endpoints)} endpoints from {url}")
                    return endpoints
            except Exception as e:
                continue

        # Fallback: common endpoints
        self.logger.warning("Could not find OpenAPI spec, using common endpoints")
        endpoints = self.get_common_endpoints()

        return endpoints

    def parse_openapi_spec(self, spec: Dict) -> List[Dict[str, str]]:
        """
        Parse OpenAPI specification

        Args:
            spec: OpenAPI/Swagger JSON

        Returns:
            List of endpoints
        """
        endpoints = []

        paths = spec.get('paths', {})

        for path, methods in paths.items():
            for method, details in methods.items():
                if method.upper() in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
                    endpoints.append({
                        'path': path,
                        'method': method.upper(),
                        'summary': details.get('summary', ''),
                        'tags': details.get('tags', [])
                    })

        return endpoints

    def get_common_endpoints(self) -> List[Dict[str, str]]:
        """
        Get common API endpoints to test

        Returns:
            List of common endpoints
        """
        return [
            {'path': '/health', 'method': 'GET', 'summary': 'Health check'},
            {'path': '/api/status', 'method': 'GET', 'summary': 'Status check'},
            {'path': '/api/version', 'method': 'GET', 'summary': 'Version info'},
        ]

    def test_endpoint(self, endpoint: Dict[str, str]) -> Dict[str, Any]:
        """
        Test a single endpoint

        Args:
            endpoint: Endpoint definition

        Returns:
            Test results with timing and status
        """
        url = f"{self.base_url}{endpoint['path']}"
        method = endpoint['method']

        response_times = []
        errors = []
        status_codes = []

        # Test multiple times for reliability
        for attempt in range(3):
            try:
                start_time = time.time()

                if method == 'GET':
                    response = requests.get(
                        url,
                        timeout=self.timeout,
                        verify=self.verify_ssl
                    )
                elif method == 'POST':
                    response = requests.post(
                        url,
                        json={},
                        timeout=self.timeout,
                        verify=self.verify_ssl
                    )
                else:
                    # Skip other methods for safety
                    continue

                elapsed = (time.time() - start_time) * 1000  # Convert to ms

                response_times.append(elapsed)
                status_codes.append(response.status_code)

            except requests.exceptions.Timeout:
                errors.append('timeout')
            except requests.exceptions.ConnectionError:
                errors.append('connection_error')
            except Exception as e:
                errors.append(str(e))

        # Calculate statistics
        result = {
            'path': endpoint['path'],
            'method': method,
            'summary': endpoint.get('summary', ''),
            'avg_response_time_ms': round(mean(response_times), 2) if response_times else None,
            'median_response_time_ms': round(median(response_times), 2) if response_times else None,
            'min_response_time_ms': round(min(response_times), 2) if response_times else None,
            'max_response_time_ms': round(max(response_times), 2) if response_times else None,
            'success_rate': len(response_times) / 3,
            'status_codes': status_codes,
            'errors': errors,
            'accessible': len(response_times) > 0
        }

        return result

    def aggregate_endpoint_results(self, results: List[Dict]) -> Dict[str, Any]:
        """
        Aggregate results from all endpoints

        Args:
            results: List of endpoint test results

        Returns:
            Aggregated metrics
        """
        accessible_endpoints = [r for r in results if r['accessible']]

        if not accessible_endpoints:
            return self.get_empty_metrics()

        response_times = [
            r['avg_response_time_ms']
            for r in accessible_endpoints
            if r['avg_response_time_ms'] is not None
        ]

        # Calculate error rate
        total_requests = len(results) * 3  # 3 attempts per endpoint
        failed_requests = sum(len(r['errors']) for r in results)
        error_rate = failed_requests / total_requests if total_requests > 0 else 0

        # Calculate API parity (if we have legacy data to compare)
        # For now, just report what we found
        total_endpoints = len(results)
        accessible_count = len(accessible_endpoints)
        api_parity = accessible_count / total_endpoints if total_endpoints > 0 else 0

        metrics = {
            'total_endpoints': total_endpoints,
            'accessible_endpoints': accessible_count,
            'api_parity': round(api_parity, 3),
            'avg_response_time_ms': round(mean(response_times), 2) if response_times else 0,
            'median_response_time_ms': round(median(response_times), 2) if response_times else 0,
            'p95_response_time_ms': round(sorted(response_times)[int(len(response_times) * 0.95)], 2) if len(response_times) > 0 else 0,
            'p99_response_time_ms': round(sorted(response_times)[int(len(response_times) * 0.99)], 2) if len(response_times) > 0 else 0,
            'error_rate': round(error_rate, 4),
            'fastest_endpoint': min(accessible_endpoints, key=lambda x: x['avg_response_time_ms'] or float('inf'))['path'] if accessible_endpoints else None,
            'slowest_endpoint': max(accessible_endpoints, key=lambda x: x['avg_response_time_ms'] or 0)['path'] if accessible_endpoints else None,
        }

        return metrics

    def get_empty_metrics(self) -> Dict[str, Any]:
        """Return empty metrics structure"""
        return {
            'total_endpoints': 0,
            'accessible_endpoints': 0,
            'api_parity': 0,
            'avg_response_time_ms': 0,
            'median_response_time_ms': 0,
            'p95_response_time_ms': 0,
            'p99_response_time_ms': 0,
            'error_rate': 0,
            'fastest_endpoint': None,
            'slowest_endpoint': None,
            'endpoints': []
        }
