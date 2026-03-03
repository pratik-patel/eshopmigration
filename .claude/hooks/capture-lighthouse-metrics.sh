#!/bin/bash
# Capture Lighthouse performance metrics
# Triggered by SubagentStop hook for frontend-migration agent

INPUT=$(cat)
AGENT=$(echo "$INPUT" | jq -r '.subagent_type')

# Only run for frontend migration agent
if [[ "$AGENT" != "frontend-migration" ]]; then
  exit 0
fi

echo "⚡ Running Lighthouse performance audit..." >&2

# Extract seam name from current context
SEAM_DIR=$(find docs/seams -type d -maxdepth 1 -name "*" | head -1 | xargs basename 2>/dev/null)

if [ -z "$SEAM_DIR" ]; then
  echo "⚠️ No seam context found, skipping Lighthouse audit" >&2
  exit 0
fi

mkdir -p docs/tracking/seams/$SEAM_DIR

# Check if frontend dev server is running
if ! curl -s http://localhost:3000 > /dev/null 2>&1; then
  echo "⚠️ Frontend dev server not running at http://localhost:3000, skipping Lighthouse" >&2
  echo "  (To enable: run 'npm run dev' in frontend directory)" >&2

  # Create placeholder file
  cat > docs/tracking/seams/$SEAM_DIR/lighthouse-results.json <<EOF
{
  "seam": "$SEAM_DIR",
  "url": "http://localhost:3000/$SEAM_DIR",
  "timestamp": "$(date -Iseconds)",
  "status": "skipped",
  "reason": "Frontend dev server not running",
  "scores": {
    "performance": null,
    "accessibility": null,
    "best-practices": null,
    "seo": null
  }
}
EOF
  exit 0
fi

# Check if lighthouse is installed
if ! command -v lighthouse &> /dev/null; then
  echo "⚠️ Lighthouse not installed, skipping audit" >&2
  echo "  (To install: npm install -g lighthouse)" >&2

  # Create placeholder file
  cat > docs/tracking/seams/$SEAM_DIR/lighthouse-results.json <<EOF
{
  "seam": "$SEAM_DIR",
  "url": "http://localhost:3000/$SEAM_DIR",
  "timestamp": "$(date -Iseconds)",
  "status": "skipped",
  "reason": "Lighthouse not installed",
  "scores": {
    "performance": null,
    "accessibility": null,
    "best-practices": null,
    "seo": null
  }
}
EOF
  exit 0
fi

echo "  → Auditing http://localhost:3000/$SEAM_DIR..." >&2

# Run Lighthouse
lighthouse http://localhost:3000/$SEAM_DIR \
  --output=json \
  --output-path=docs/tracking/seams/$SEAM_DIR/lighthouse-results.json \
  --chrome-flags="--headless --no-sandbox" \
  --quiet \
  2>/dev/null

if [ -f "docs/tracking/seams/$SEAM_DIR/lighthouse-results.json" ]; then
  # Extract key metrics
  PERFORMANCE=$(jq -r '.categories.performance.score * 100' docs/tracking/seams/$SEAM_DIR/lighthouse-results.json 2>/dev/null)
  ACCESSIBILITY=$(jq -r '.categories.accessibility.score * 100' docs/tracking/seams/$SEAM_DIR/lighthouse-results.json 2>/dev/null)

  echo "  ✅ Lighthouse audit complete" >&2
  echo "     Performance: ${PERFORMANCE}%" >&2
  echo "     Accessibility: ${ACCESSIBILITY}%" >&2
else
  echo "  ⚠️ Lighthouse audit failed" >&2
fi

exit 0
