#!/usr/bin/env python3
"""
Contract Validation: Backend Routes vs OpenAPI Contract
Extracts actual routes from FastAPI code and validates against OpenAPI contract.
"""

import ast
import json
import sys
from pathlib import Path
from typing import Dict, List, Set

import yaml


def extract_routes_from_code(backend_path: Path) -> Dict[str, List[str]]:
    """Extract routes from FastAPI router files."""
    routes = {}

    for py_file in backend_path.rglob("*.py"):
        if py_file.name.startswith("test_"):
            continue

        try:
            content = py_file.read_text(encoding="utf-8")
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Look for @router.get, @router.post, etc.
                    for decorator in node.decorator_list:
                        if isinstance(decorator, ast.Call):
                            if isinstance(decorator.func, ast.Attribute):
                                method = decorator.func.attr  # get, post, put, delete
                                # Get the path argument
                                if decorator.args:
                                    if isinstance(decorator.args[0], ast.Constant):
                                        path = decorator.args[0].value
                                        http_method = method.upper()
                                        if http_method not in routes:
                                            routes[http_method] = []
                                        routes[http_method].append(path)
        except Exception as e:
            print(f"Warning: Could not parse {py_file}: {e}", file=sys.stderr)

    return routes


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


def validate_contract(actual: Dict[str, List[str]], expected: Dict[str, Set[str]]) -> bool:
    """Compare actual routes with expected routes from contract."""
    all_valid = True

    print("🔍 Contract Validation Report\n")
    print("=" * 60)

    # Check for missing routes (in contract but not implemented)
    for method, paths in expected.items():
        actual_paths = set(actual.get(method, []))
        missing = paths - actual_paths

        if missing:
            all_valid = False
            print(f"\n❌ Missing {method} routes (in contract but not implemented):")
            for path in sorted(missing):
                print(f"   - {method} {path}")

    # Check for extra routes (implemented but not in contract)
    for method, paths in actual.items():
        expected_paths = expected.get(method, set())
        extra = set(paths) - expected_paths

        if extra:
            all_valid = False
            print(f"\n⚠️  Extra {method} routes (implemented but not in contract):")
            for path in sorted(extra):
                print(f"   - {method} {path}")

    # Show matching routes
    print("\n✅ Matching routes:")
    for method in sorted(set(actual.keys()) | set(expected.keys())):
        actual_paths = set(actual.get(method, []))
        expected_paths = expected.get(method, set())
        matching = actual_paths & expected_paths

        if matching:
            for path in sorted(matching):
                print(f"   - {method} {path}")

    print("\n" + "=" * 60)

    if all_valid:
        print("✅ All routes match contract!")
        return True
    else:
        print("❌ Contract validation FAILED")
        return False


def main():
    if len(sys.argv) < 3:
        print("Usage: python validate_contract_backend.py <backend_path> <contract_yaml>")
        sys.exit(1)

    backend_path = Path(sys.argv[1])
    contract_path = Path(sys.argv[2])

    if not backend_path.exists():
        print(f"Error: Backend path not found: {backend_path}")
        sys.exit(1)

    if not contract_path.exists():
        print(f"Error: Contract file not found: {contract_path}")
        sys.exit(1)

    print(f"Extracting routes from: {backend_path}")
    actual_routes = extract_routes_from_code(backend_path)

    print(f"Loading contract from: {contract_path}")
    expected_routes = load_openapi_contract(contract_path)

    valid = validate_contract(actual_routes, expected_routes)

    sys.exit(0 if valid else 1)


if __name__ == "__main__":
    main()
