#!/usr/bin/env python3
"""
Claude Code Hooks Integration Module

This module provides Python bindings for the Claude Code hook system,
allowing agents to trigger quality gates and security checks programmatically.
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional


class HooksIntegration:
    """Integration class for Claude Code hooks system."""

    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize hooks integration.

        Args:
            project_root: Path to project root (default: auto-detect)
        """
        self.project_root = project_root or Path.cwd()
        self.scripts_dir = self.project_root / ".claude" / "scripts"
        self.settings_file = self.project_root / ".claude" / "settings.json"

        if not self.scripts_dir.exists():
            raise FileNotFoundError(f"Scripts directory not found: {self.scripts_dir}")

    def load_settings(self) -> Dict:
        """Load hook settings from settings.json."""
        if not self.settings_file.exists():
            return {}

        with open(self.settings_file) as f:
            return json.load(f)

    def run_post_code_hook(self, file_path: str) -> bool:
        """
        Run post-code hook (quality check + security analysis).

        Args:
            file_path: Path to file to check

        Returns:
            True if all checks passed, False otherwise
        """
        script = self.scripts_dir / "post-code-hook.sh"

        try:
            result = subprocess.run(
                ["bash", str(script), file_path],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=False,
            )

            print(result.stdout)
            if result.stderr:
                print(result.stderr, file=sys.stderr)

            return result.returncode == 0

        except Exception as e:
            print(f"Error running post-code hook: {e}", file=sys.stderr)
            return False

    def run_post_implementation_hook(self, seam_name: str) -> bool:
        """
        Run post-implementation hook (comprehensive quality gates).

        Args:
            seam_name: Name of the seam

        Returns:
            True if all quality gates passed, False otherwise
        """
        script = self.scripts_dir / "post-implementation-hook.sh"

        try:
            result = subprocess.run(
                ["bash", str(script), seam_name],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=False,
            )

            print(result.stdout)
            if result.stderr:
                print(result.stderr, file=sys.stderr)

            return result.returncode == 0

        except Exception as e:
            print(f"Error running post-implementation hook: {e}", file=sys.stderr)
            return False

    def run_auto_fix(self, file_path: str, stack: str) -> bool:
        """
        Run auto-fix on a file.

        Args:
            file_path: Path to file to fix
            stack: "backend" or "frontend"

        Returns:
            True if auto-fix succeeded, False otherwise
        """
        script = self.scripts_dir / "auto-fix.sh"

        try:
            result = subprocess.run(
                ["bash", str(script), file_path, stack],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=False,
            )

            print(result.stdout)
            if result.stderr:
                print(result.stderr, file=sys.stderr)

            return result.returncode == 0

        except Exception as e:
            print(f"Error running auto-fix: {e}", file=sys.stderr)
            return False

    def run_auto_fix_seam(self, seam_name: str) -> bool:
        """
        Run auto-fix on entire seam.

        Args:
            seam_name: Name of the seam

        Returns:
            True if auto-fix succeeded, False otherwise
        """
        script = self.scripts_dir / "auto-fix-seam.sh"

        try:
            result = subprocess.run(
                ["bash", str(script), seam_name],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=False,
            )

            print(result.stdout)
            if result.stderr:
                print(result.stderr, file=sys.stderr)

            return result.returncode == 0

        except Exception as e:
            print(f"Error running auto-fix-seam: {e}", file=sys.stderr)
            return False

    def check_code_quality(self, file_path: str, stack: str) -> bool:
        """
        Check code quality for a file.

        Args:
            file_path: Path to file to check
            stack: "backend" or "frontend"

        Returns:
            True if quality checks passed, False otherwise
        """
        script = self.scripts_dir / "code-quality-check.sh"

        try:
            result = subprocess.run(
                ["bash", str(script), file_path, stack],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=False,
            )

            print(result.stdout)
            if result.stderr:
                print(result.stderr, file=sys.stderr)

            return result.returncode == 0

        except Exception as e:
            print(f"Error checking code quality: {e}", file=sys.stderr)
            return False

    def check_security(self, file_path: str, stack: str) -> bool:
        """
        Check security for a file.

        Args:
            file_path: Path to file to check
            stack: "backend" or "frontend"

        Returns:
            True if security checks passed, False otherwise
        """
        script = self.scripts_dir / "security-analysis.sh"

        try:
            result = subprocess.run(
                ["bash", str(script), file_path, stack],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=False,
            )

            print(result.stdout)
            if result.stderr:
                print(result.stderr, file=sys.stderr)

            return result.returncode == 0

        except Exception as e:
            print(f"Error checking security: {e}", file=sys.stderr)
            return False

    def get_quality_thresholds(self) -> Dict:
        """
        Get quality gate thresholds from settings.

        Returns:
            Dictionary of thresholds
        """
        settings = self.load_settings()
        return settings.get("quality_gates", {})


def main():
    """CLI interface for hooks integration."""
    if len(sys.argv) < 3:
        print("Usage:")
        print("  python hooks_integration.py post-code <file_path>")
        print("  python hooks_integration.py post-implementation <seam_name>")
        print("  python hooks_integration.py auto-fix <file_path> <stack>")
        print("  python hooks_integration.py auto-fix-seam <seam_name>")
        sys.exit(1)

    command = sys.argv[1]
    hooks = HooksIntegration()

    if command == "post-code":
        file_path = sys.argv[2]
        success = hooks.run_post_code_hook(file_path)
        sys.exit(0 if success else 1)

    elif command == "post-implementation":
        seam_name = sys.argv[2]
        success = hooks.run_post_implementation_hook(seam_name)
        sys.exit(0 if success else 1)

    elif command == "auto-fix":
        file_path = sys.argv[2]
        stack = sys.argv[3]
        success = hooks.run_auto_fix(file_path, stack)
        sys.exit(0 if success else 1)

    elif command == "auto-fix-seam":
        seam_name = sys.argv[2]
        success = hooks.run_auto_fix_seam(seam_name)
        sys.exit(0 if success else 1)

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
