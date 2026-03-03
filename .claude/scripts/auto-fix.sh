#!/bin/bash
#
# Auto-Fix Script
# Automatically fixes code quality and security issues
#

set -euo pipefail

FILE_PATH="$1"
STACK="$2"
MAX_ITERATIONS=3
ITERATION=0

echo "🔧 Running auto-fix..."

# Load settings
SETTINGS_FILE=".claude/settings.json"
if [ ! -f "$SETTINGS_FILE" ]; then
    echo "Error: settings.json not found"
    exit 1
fi

while [ $ITERATION -lt $MAX_ITERATIONS ]; do
    ITERATION=$((ITERATION + 1))
    echo "  Iteration $ITERATION/$MAX_ITERATIONS..."

    if [ "$STACK" = "backend" ]; then
        # Python auto-fixes

        # 1. Ruff auto-fix
        echo "    → Running Ruff auto-fix..."
        ruff check "$FILE_PATH" --fix --quiet 2>/dev/null || true

        # 2. Black formatting
        echo "    → Running Black formatter..."
        black "$FILE_PATH" --quiet 2>/dev/null || true

        # 3. isort imports
        echo "    → Sorting imports with isort..."
        isort "$FILE_PATH" --quiet 2>/dev/null || true

        # 4. Remove unused imports (using autoflake)
        echo "    → Removing unused imports..."
        autoflake --in-place --remove-unused-variables --remove-all-unused-imports "$FILE_PATH" 2>/dev/null || true

    elif [ "$STACK" = "frontend" ]; then
        # TypeScript/React auto-fixes

        # 1. ESLint auto-fix
        echo "    → Running ESLint auto-fix..."
        npx eslint "$FILE_PATH" --fix --quiet 2>/dev/null || true

        # 2. Prettier formatting
        echo "    → Running Prettier formatter..."
        npx prettier --write "$FILE_PATH" --log-level=error 2>/dev/null || true

        # 3. Fix common issues
        echo "    → Fixing common issues..."

        # Remove console.log statements in production code
        if [[ "$FILE_PATH" != *".test."* ]] && [[ "$FILE_PATH" != *".spec."* ]]; then
            sed -i 's/^\s*console\.log(.*);*$//g' "$FILE_PATH" 2>/dev/null || true
        fi
    fi

    # Re-run quality checks
    echo "    → Re-checking code quality..."
    if bash .claude/scripts/code-quality-check.sh "$FILE_PATH" "$STACK" 2>/dev/null; then
        echo "✅ Auto-fix completed successfully"
        exit 0
    fi
done

echo "⚠️  Auto-fix completed with partial success after $MAX_ITERATIONS iterations"
echo "Manual review may be required"
exit 0
