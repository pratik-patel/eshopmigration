#!/usr/bin/env python3
"""
Contract Validation: Frontend API Calls vs OpenAPI Contract
Extracts API calls from frontend code and validates against OpenAPI contract.
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Set

import yaml


def extract_api_calls_from_frontend(frontend_path: Path) -> Dict[str, Set[str]]:
    """Extract API calls from frontend TypeScript/JavaScript code."""
    api_calls = {}

    # Patterns to match API calls
    patterns = [
        # apiClient.get('/api/...')
        r'apiClient\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']',
        # fetch('/api/...')
        r'fetch\(["\']([^"\']+)["\'].*method:\s*["\']([A-Z]+)["\']',
        # axios.get('/api/...')
        r'axios\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']',
    ]

    for ts_file in frontend_path.rglob("*.ts"):
        if ts_file.name.endswith(".test.ts"):
            continue

        try:
            content = ts_file.read_text(encoding="utf-8")

            for pattern in patterns:
                matches = re.finditer(pattern, content)
                for match in matches:
                    if len(match.groups()) == 2:
                        method_or_path = match.group(1)
                        path_or_method = match.group(2)

                        # Determine which is method and which is path
                        if method_or_path.upper() in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                            method = method_or_path.upper()
                            path = path_or_method
                        else:
                            method = path_or_method.upper()
                            path = method_or_path

                        if method not in api_calls:
                            api_calls[method] = set()
                        api_calls[method].add(path)
        except Exception as e:
            print(f"Warning: Could not parse {ts_file}: {e}", file=sys.stderr)

    for tsx_file in frontend_path.rglob("*.tsx"):
        if tsx_file.name.endswith(".test.tsx"):
            continue

        try:
            content = tsx_file.read_text(encoding="utf-8")

            for pattern in patterns:
                matches = re.finditer(pattern, content)
                for match in matches:
                    if len(match.groups()) == 2:
                        method_or_path = match.group(1)
                        path_or_method = match.group(2)

                        if method_or_path.upper() in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                            method = method_or_path.upper()
                            path = path_or_method
                        else:
                            method = path_or_method.upper()
                            path = method_or_path

                        if method not in api_calls:
                            api_calls[method] = set()
                        api_calls[method].add(path)
        except Exception as e:
            print(f"Warning: Could not parse {tsx_file}: {e}", file=sys.stderr)

    return api_calls


def load_openapi_contract(contract_path: Path) -> Dict[str, Set[str]]:
    """Load expected routes from OpenAPI contract."""
    with open(contract_path, "r", encoding="utf-8") as f:
        spec = yaml.safe_load(f)

    expected_routes = {}
    for path, methods in spec.get("paths", {}).items():
        for method in methods.keys():
            if method.upper() in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                http_method = method.upper()
                if http_method not in expected_routes:
                    expected_routes[http_method] = set()
                expected_routes[http_method].add(path)

    return expected_routes


def validate_frontend_calls(actual: Dict[str, Set[str]], expected: Dict[str, Set[str]]) -> bool:
    """Validate frontend API calls against contract."""
    all_valid = True

    print("🔍 Frontend Contract Validation Report\n")
    print("=" * 60)

    # Check for calls to non-existent routes
    for method, paths in actual.items():
        expected_paths = expected.get(method, set())
        invalid = paths - expected_paths

        if invalid:
            all_valid = False
            print(f"\n❌ Invalid {method} calls (not in contract):")
            for path in sorted(invalid):
                print(f"   - {method} {path}")
                print(f"     → Frontend calling endpoint that doesn't exist in contract")

    # Show valid calls
    print("\n✅ Valid API calls:")
    for method in sorted(actual.keys()):
        expected_paths = expected.get(method, set())
        valid = actual[method] & expected_paths

        if valid:
            for path in sorted(valid):
                print(f"   - {method} {path}")

    # Check for unused contract endpoints
    print("\n⚠️  Unused contract endpoints (in contract but not called by frontend):")
    has_unused = False
    for method, paths in expected.items():
        actual_paths = actual.get(method, set())
        unused = paths - actual_paths

        if unused:
            has_unused = True
            for path in sorted(unused):
                print(f"   - {method} {path}")

    if not has_unused:
        print("   (None - all endpoints are used)")

    print("\n" + "=" * 60)

    if all_valid:
        print("✅ All frontend API calls match contract!")
        return True
    else:
        print("❌ Frontend contract validation FAILED")
        return False


def main():
    if len(sys.argv) < 3:
        print("Usage: python validate_contract_frontend.py <frontend_path> <contract_yaml>")
        sys.exit(1)

    frontend_path = Path(sys.argv[1])
    contract_path = Path(sys.argv[2])

    if not frontend_path.exists():
        print(f"Error: Frontend path not found: {frontend_path}")
        sys.exit(1)

    if not contract_path.exists():
        print(f"Error: Contract file not found: {contract_path}")
        sys.exit(1)

    print(f"Extracting API calls from: {frontend_path}")
    actual_calls = extract_api_calls_from_frontend(frontend_path)

    print(f"Loading contract from: {contract_path}")
    expected_routes = load_openapi_contract(contract_path)

    valid = validate_frontend_calls(actual_calls, expected_routes)

    sys.exit(0 if valid else 1)


if __name__ == "__main__":
    main()
