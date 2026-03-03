#!/bin/bash
# Verify browser-agent skill installation

echo "🔍 Verifying browser-agent skill installation..."
echo ""

ERRORS=0

# Check directory structure
echo "📁 Checking directory structure..."
REQUIRED_DIRS=(
    "scripts"
)

for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo "  ✅ $dir"
    else
        echo "  ❌ $dir (missing)"
        ERRORS=$((ERRORS + 1))
    fi
done

# Check required files
echo ""
echo "📄 Checking required files..."
REQUIRED_FILES=(
    "SKILL.md"
    "README.md"
    "EXAMPLES.md"
    "package.json"
    "config.json"
    "playwright.config.ts"
    "scripts/discover.spec.ts"
    "scripts/verify.spec.ts"
    "scripts/generate-baseline-index.js"
    "scripts/generate-parity-report.js"
    "scripts/run-discovery.sh"
    "scripts/run-verification.sh"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file (missing)"
        ERRORS=$((ERRORS + 1))
    fi
done

# Check Node.js
echo ""
echo "🟢 Checking Node.js..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo "  ✅ Node.js installed: $NODE_VERSION"
else
    echo "  ❌ Node.js not installed"
    echo "     Install from: https://nodejs.org/"
    ERRORS=$((ERRORS + 1))
fi

# Check npm
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    echo "  ✅ npm installed: $NPM_VERSION"
else
    echo "  ❌ npm not installed"
    ERRORS=$((ERRORS + 1))
fi

# Check dependencies
echo ""
echo "📦 Checking dependencies..."
if [ -d "node_modules" ]; then
    echo "  ✅ node_modules exists"

    if [ -d "node_modules/@playwright/test" ]; then
        echo "  ✅ @playwright/test installed"
    else
        echo "  ⚠️  @playwright/test not installed"
        echo "     Run: npm install"
    fi

    if [ -d "node_modules/pngjs" ]; then
        echo "  ✅ pngjs installed"
    else
        echo "  ⚠️  pngjs not installed"
    fi

    if [ -d "node_modules/pixelmatch" ]; then
        echo "  ✅ pixelmatch installed"
    else
        echo "  ⚠️  pixelmatch not installed"
    fi
else
    echo "  ⚠️  node_modules not found"
    echo "     Run: npm install"
fi

# Check Playwright browsers
echo ""
echo "🌐 Checking Playwright browsers..."
if [ -d "$HOME/.cache/ms-playwright" ] || [ -d "$HOME/Library/Caches/ms-playwright" ]; then
    echo "  ✅ Playwright browsers installed"
else
    echo "  ⚠️  Playwright browsers not installed"
    echo "     Run: npx playwright install chromium"
fi

# Check shell script permissions
echo ""
echo "🔐 Checking script permissions..."
SCRIPTS=(
    "scripts/run-discovery.sh"
    "scripts/run-verification.sh"
    "verify-installation.sh"
)

for script in "${SCRIPTS[@]}"; do
    if [ -x "$script" ]; then
        echo "  ✅ $script (executable)"
    else
        echo "  ⚠️  $script (not executable)"
        echo "     Run: chmod +x $script"
    fi
done

# Summary
echo ""
echo "================================"
if [ $ERRORS -eq 0 ]; then
    echo "✅ Installation verification passed!"
    echo ""
    echo "Ready to use browser-agent skill:"
    echo "  /browser-agent discovery <url>"
    echo "  /browser-agent verify --legacy <url> --modern <url>"
    echo ""
    echo "Or run directly:"
    echo "  ./scripts/run-discovery.sh <url>"
    echo "  ./scripts/run-verification.sh --legacy <url> --modern <url>"
else
    echo "❌ Installation verification failed with $ERRORS error(s)"
    echo ""
    echo "Fix the errors above and re-run: ./verify-installation.sh"
fi
echo "================================"

exit $ERRORS
