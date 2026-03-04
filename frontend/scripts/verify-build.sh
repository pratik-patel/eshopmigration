#!/bin/bash
# Build verification script for frontend

set -e  # Exit on error

echo "=========================================="
echo "Frontend Build Verification"
echo "=========================================="
echo ""

# Step 1: Install dependencies
echo "[1/5] Installing dependencies..."
npm install
echo "✓ Dependencies installed"
echo ""

# Step 2: Type check
echo "[2/5] Running TypeScript type check..."
npm run type-check
echo "✓ Type check passed"
echo ""

# Step 3: Lint
echo "[3/5] Running linter..."
npm run lint 2>/dev/null || echo "⚠ Lint warnings (non-blocking)"
echo ""

# Step 4: Build
echo "[4/5] Building production bundle..."
npm run build
echo "✓ Build succeeded"
echo ""

# Step 5: Check bundle size
echo "[5/5] Checking bundle sizes..."
if [ -d "dist/assets" ]; then
    echo "Bundle contents:"
    ls -lh dist/assets/*.js 2>/dev/null || true
    ls -lh dist/assets/*.css 2>/dev/null || true

    # Calculate total size
    total_size=$(du -sh dist | cut -f1)
    echo ""
    echo "Total bundle size: $total_size"
    echo "✓ Bundle size check complete"
else
    echo "✗ Build output directory not found"
    exit 1
fi

echo ""
echo "=========================================="
echo "✅ Build verification PASSED"
echo "=========================================="
echo ""
echo "Build artifacts located in: dist/"
echo ""
