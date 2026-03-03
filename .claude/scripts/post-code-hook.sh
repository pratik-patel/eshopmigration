#!/bin/bash
#
# Post-Code Hook: Runs after Write/Edit tool execution
# Performs code review and security analysis on modified files
#

set -euo pipefail

FILE_PATH="${1:-}"

if [ -z "$FILE_PATH" ]; then
    echo "Error: No file path provided"
    exit 1
fi

# Determine if file is backend or frontend
if [[ "$FILE_PATH" == *"/backend/"* ]]; then
    STACK="backend"
    LANGUAGE="python"
elif [[ "$FILE_PATH" == *"/frontend/"* ]]; then
    STACK="frontend"
    LANGUAGE="typescript"
else
    echo "Skipping hook: File not in backend or frontend"
    exit 0
fi

echo "🔍 Running post-code quality checks on: $FILE_PATH"
echo "Stack: $STACK | Language: $LANGUAGE"
echo "----------------------------------------"

# Run quality checks
bash .claude/scripts/code-quality-check.sh "$FILE_PATH" "$STACK"

# Run security analysis
bash .claude/scripts/security-analysis.sh "$FILE_PATH" "$STACK"

# Check if fixes are needed
if [ -f "/tmp/claude-code-fixes-needed.flag" ]; then
    echo "⚠️  Issues found - triggering auto-fix..."
    bash .claude/scripts/auto-fix.sh "$FILE_PATH" "$STACK"
    rm -f /tmp/claude-code-fixes-needed.flag
fi

echo "✅ Post-code quality checks completed"
