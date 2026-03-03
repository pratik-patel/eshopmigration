#!/bin/bash
# Browser Agent - Discovery Mode Runner
set -e

# Parse arguments
MODE="discovery"
APP_URL=""
SEAM=""
OUTPUT_DIR=""
MAX_DEPTH=3

while [[ $# -gt 0 ]]; do
  case $1 in
    --url)
      APP_URL="$2"
      shift 2
      ;;
    --seam)
      SEAM="$2"
      shift 2
      ;;
    --output)
      OUTPUT_DIR="$2"
      shift 2
      ;;
    --depth)
      MAX_DEPTH="$2"
      shift 2
      ;;
    *)
      APP_URL="$1"
      shift
      ;;
  esac
done

# Validate inputs
if [ -z "$APP_URL" ]; then
  echo "❌ Error: Application URL required"
  echo "Usage: ./run-discovery.sh <url> [--seam <name>] [--depth <n>]"
  exit 1
fi

# Set output directory
if [ -z "$OUTPUT_DIR" ]; then
  if [ -n "$SEAM" ]; then
    OUTPUT_DIR="./legacy-golden/$SEAM"
  else
    OUTPUT_DIR="./legacy-golden/discovery"
  fi
fi

echo "🚀 Browser Agent - Discovery Mode"
echo "=================================="
echo "URL: $APP_URL"
echo "Output: $OUTPUT_DIR"
echo "Max Depth: $MAX_DEPTH"
echo "=================================="

# Check if playwright is installed
cd "$(dirname "$0")/.."

if [ ! -d "node_modules" ]; then
  echo "📦 Installing dependencies..."
  npm install
fi

if [ ! -d "$HOME/.cache/ms-playwright" ] && [ ! -d "$HOME/Library/Caches/ms-playwright" ]; then
  echo "📦 Installing Playwright browsers..."
  npx playwright install chromium
fi

# Create output directory
mkdir -p "$OUTPUT_DIR/screenshots"

# Run discovery
echo ""
echo "🔍 Starting UI discovery..."
APP_URL="$APP_URL" \
OUTPUT_DIR="$OUTPUT_DIR" \
MAX_DEPTH="$MAX_DEPTH" \
npx playwright test scripts/discover.spec.ts --reporter=list

# Generate baseline index
echo ""
echo "📝 Generating baseline index..."
node scripts/generate-baseline-index.js "$OUTPUT_DIR"

echo ""
echo "✅ Discovery complete!"
echo ""
echo "📂 Results:"
echo "  - Baseline: $OUTPUT_DIR/BASELINE_INDEX.md"
echo "  - Workflows: $OUTPUT_DIR/workflows.json"
echo "  - Screenshots: $OUTPUT_DIR/screenshots/"
echo ""
echo "Next steps:"
echo "  1. Review BASELINE_INDEX.md"
echo "  2. Verify all workflows were captured"
echo "  3. Commit baseline to git"
echo "  4. Run verification: /browser-agent verify"
