#!/bin/bash
# Browser Agent - Verification Mode Runner
set -e

# Parse arguments
LEGACY_URL=""
MODERN_URL=""
SEAM=""
BASELINE_DIR=""
OUTPUT_DIR=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --legacy)
      LEGACY_URL="$2"
      shift 2
      ;;
    --modern)
      MODERN_URL="$2"
      shift 2
      ;;
    --seam)
      SEAM="$2"
      shift 2
      ;;
    --baseline)
      BASELINE_DIR="$2"
      shift 2
      ;;
    --output)
      OUTPUT_DIR="$2"
      shift 2
      ;;
    *)
      shift
      ;;
  esac
done

# Validate inputs
if [ -z "$LEGACY_URL" ] || [ -z "$MODERN_URL" ]; then
  echo "❌ Error: Both legacy and modern URLs required"
  echo "Usage: ./run-verification.sh --legacy <url> --modern <url> [--seam <name>]"
  exit 1
fi

# Set directories
if [ -z "$BASELINE_DIR" ]; then
  if [ -n "$SEAM" ]; then
    BASELINE_DIR="./legacy-golden/$SEAM"
  else
    BASELINE_DIR="./legacy-golden/discovery"
  fi
fi

if [ -z "$OUTPUT_DIR" ]; then
  if [ -n "$SEAM" ]; then
    OUTPUT_DIR="./tests/parity/$SEAM"
  else
    OUTPUT_DIR="./tests/parity"
  fi
fi

echo "🔍 Browser Agent - Verification Mode"
echo "====================================="
echo "Legacy: $LEGACY_URL"
echo "Modern: $MODERN_URL"
echo "Baseline: $BASELINE_DIR"
echo "Output: $OUTPUT_DIR"
echo "====================================="

# Check if baseline exists
if [ ! -f "$BASELINE_DIR/workflows.json" ]; then
  echo ""
  echo "⚠️  Warning: No baseline workflows found at $BASELINE_DIR/workflows.json"
  echo "Run discovery mode first: /browser-agent discovery $LEGACY_URL --seam $SEAM"
  echo ""
  read -p "Continue anyway? (y/n) " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
  fi
fi

# Check if playwright is installed
cd "$(dirname "$0")/.."

if [ ! -d "node_modules" ]; then
  echo "📦 Installing dependencies..."
  npm install
fi

# Create output directory
mkdir -p "$OUTPUT_DIR/screenshots"

# Run verification
echo ""
echo "🔍 Starting parity verification..."
LEGACY_URL="$LEGACY_URL" \
MODERN_URL="$MODERN_URL" \
BASELINE_DIR="$BASELINE_DIR" \
OUTPUT_DIR="$OUTPUT_DIR" \
npx playwright test scripts/verify.spec.ts --reporter=list

# Generate parity report
echo ""
echo "📝 Generating parity report..."
node scripts/generate-parity-report.js "$OUTPUT_DIR"

# Display results
echo ""
if [ -f "$OUTPUT_DIR/parity-results.json" ]; then
  SCORE=$(node -e "console.log(JSON.parse(require('fs').readFileSync('$OUTPUT_DIR/parity-results.json')).parityScore.toFixed(1))")
  echo "✅ Verification complete!"
  echo ""
  echo "📊 Parity Score: $SCORE%"
  echo ""

  if (( $(echo "$SCORE >= 90" | bc -l) )); then
    echo "✅ Excellent parity - Production ready"
  elif (( $(echo "$SCORE >= 70" | bc -l) )); then
    echo "🟡 Good parity - Minor gaps to address"
  else
    echo "🔴 Significant gaps - More work needed"
  fi
else
  echo "⚠️  Warning: Results file not generated"
fi

echo ""
echo "📂 Results:"
echo "  - Report: $OUTPUT_DIR/diff-report.html"
echo "  - Matrix: $OUTPUT_DIR/feature-matrix.md"
echo "  - Issues: $OUTPUT_DIR/issues.json"
echo "  - Screenshots: $OUTPUT_DIR/screenshots/"
echo ""
echo "Next steps:"
echo "  1. Open diff-report.html in browser"
echo "  2. Review feature-matrix.md"
echo "  3. Address issues in issues.json"
echo "  4. Document approved differences"
echo "  5. Re-run after fixes"
