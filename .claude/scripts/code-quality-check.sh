#!/bin/bash
#
# Code Quality Check Script
# Runs linting, formatting, and type checking
#

set -euo pipefail

FILE_PATH="$1"
STACK="$2"

ISSUES_FOUND=0

echo "📋 Running code quality checks..."

if [ "$STACK" = "backend" ]; then
    # Python quality checks

    # 1. Ruff linting
    echo "  → Running Ruff linter..."
    if ! ruff check "$FILE_PATH" --quiet 2>/dev/null; then
        echo "    ❌ Ruff linting issues found"
        ISSUES_FOUND=1
        ruff check "$FILE_PATH" --output-format=concise
    else
        echo "    ✅ Ruff linting passed"
    fi

    # 2. Black formatting
    echo "  → Checking Black formatting..."
    if ! black --check "$FILE_PATH" --quiet 2>/dev/null; then
        echo "    ❌ Black formatting issues found"
        ISSUES_FOUND=1
    else
        echo "    ✅ Black formatting passed"
    fi

    # 3. MyPy type checking
    echo "  → Running MyPy type checker..."
    if ! mypy "$FILE_PATH" --no-error-summary 2>/dev/null; then
        echo "    ❌ Type checking issues found"
        ISSUES_FOUND=1
        mypy "$FILE_PATH"
    else
        echo "    ✅ Type checking passed"
    fi

    # 4. Complexity check
    echo "  → Checking code complexity..."
    if ! radon cc "$FILE_PATH" -nc -s 2>/dev/null | grep -q "^$"; then
        COMPLEXITY=$(radon cc "$FILE_PATH" -s -n B 2>/dev/null || echo "")
        if [ -n "$COMPLEXITY" ]; then
            echo "    ⚠️  High complexity detected:"
            echo "$COMPLEXITY"
            ISSUES_FOUND=1
        fi
    fi

elif [ "$STACK" = "frontend" ]; then
    # TypeScript/React quality checks

    # 1. ESLint
    echo "  → Running ESLint..."
    if ! npx eslint "$FILE_PATH" --quiet 2>/dev/null; then
        echo "    ❌ ESLint issues found"
        ISSUES_FOUND=1
        npx eslint "$FILE_PATH" --format=compact
    else
        echo "    ✅ ESLint passed"
    fi

    # 2. Prettier formatting
    echo "  → Checking Prettier formatting..."
    if ! npx prettier --check "$FILE_PATH" 2>/dev/null; then
        echo "    ❌ Prettier formatting issues found"
        ISSUES_FOUND=1
    else
        echo "    ✅ Prettier formatting passed"
    fi

    # 3. TypeScript compilation
    echo "  → Running TypeScript compiler..."
    if ! npx tsc --noEmit --skipLibCheck "$FILE_PATH" 2>/dev/null; then
        echo "    ❌ TypeScript compilation issues found"
        ISSUES_FOUND=1
        npx tsc --noEmit --skipLibCheck "$FILE_PATH"
    else
        echo "    ✅ TypeScript compilation passed"
    fi

    # 4. Check for common anti-patterns
    echo "  → Checking for anti-patterns..."
    if grep -q "any" "$FILE_PATH" 2>/dev/null; then
        echo "    ⚠️  'any' type detected - use proper types"
        ISSUES_FOUND=1
    fi

    if grep -q "dangerouslySetInnerHTML" "$FILE_PATH" 2>/dev/null; then
        echo "    ⚠️  'dangerouslySetInnerHTML' detected - verify sanitization"
        ISSUES_FOUND=1
    fi
fi

if [ $ISSUES_FOUND -eq 1 ]; then
    touch /tmp/claude-code-fixes-needed.flag
    echo "❌ Code quality issues found"
    exit 1
else
    echo "✅ All code quality checks passed"
    exit 0
fi
