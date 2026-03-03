#!/bin/bash
#
# Auto-Fix Seam Script
# Automatically fixes all issues in a seam using Claude Code agents
#

set -euo pipefail

SEAM_NAME="${1:-}"

if [ -z "$SEAM_NAME" ]; then
    echo "Usage: $0 <seam-name>"
    exit 1
fi

echo "🔧 Auto-fixing issues for seam: $SEAM_NAME"
echo "==========================================="

# 1. Fix backend code quality
if [ -d "backend/app/${SEAM_NAME}" ]; then
    echo ""
    echo "📦 Fixing backend code..."

    find "backend/app/${SEAM_NAME}" -name "*.py" -type f | while read -r file; do
        echo "  Processing: $file"
        bash .claude/scripts/auto-fix.sh "$file" "backend"
    done
fi

# 2. Fix frontend code quality
if [ -d "frontend/src/pages/${SEAM_NAME}" ] || [ -d "frontend/src/components/${SEAM_NAME}" ]; then
    echo ""
    echo "🎨 Fixing frontend code..."

    find "frontend/src" -path "*/${SEAM_NAME}/*" -name "*.tsx" -o -name "*.ts" -type f | while read -r file; do
        echo "  Processing: $file"
        bash .claude/scripts/auto-fix.sh "$file" "frontend"
    done
fi

# 3. Fix tests
echo ""
echo "🧪 Fixing tests..."

# Backend tests
if [ -d "backend/tests" ]; then
    find "backend/tests" -name "*${SEAM_NAME}*.py" -type f | while read -r file; do
        echo "  Processing: $file"
        bash .claude/scripts/auto-fix.sh "$file" "backend"
    done
fi

# Frontend tests
if [ -d "frontend/tests" ]; then
    find "frontend/tests" -name "*${SEAM_NAME}*" -type f | while read -r file; do
        echo "  Processing: $file"
        bash .claude/scripts/auto-fix.sh "$file" "frontend"
    done
fi

# 4. Re-run quality gates
echo ""
echo "🚀 Re-running quality gates..."
bash .claude/scripts/post-implementation-hook.sh "$SEAM_NAME"

echo ""
echo "✅ Auto-fix completed"
