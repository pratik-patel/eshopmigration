#!/bin/bash
# Capture quality metrics after agent completes
# Triggered by SubagentStop hook for implementation agents

INPUT=$(cat)
AGENT=$(echo "$INPUT" | jq -r '.subagent_type')
TIMESTAMP=$(date -Iseconds)

# Only run for implementation and parity agents
if [[ ! "$AGENT" =~ ^(backend-migration|frontend-migration|parity-harness-generator)$ ]]; then
  exit 0
fi

echo "📊 Capturing quality metrics for $AGENT..." >&2

# Extract seam name from agent context (if available in working directory)
# This assumes agents work in context of a specific seam
SEAM_DIR=$(find docs/seams -type d -maxdepth 1 -name "*" | head -1 | xargs basename 2>/dev/null)

if [ -z "$SEAM_DIR" ]; then
  echo "⚠️ No seam context found, skipping metrics capture" >&2
  exit 0
fi

mkdir -p docs/tracking/seams/$SEAM_DIR

case "$AGENT" in
  "backend-migration")
    echo "  → Running backend tests and capturing results..." >&2
    cd backend 2>/dev/null || exit 0

    # Run pytest with JSON reporter
    pytest app/$SEAM_DIR/ tests/ -k $SEAM_DIR \
      --json-report \
      --json-report-file=../docs/tracking/seams/$SEAM_DIR/test-results-backend.json \
      --cov=app/$SEAM_DIR \
      --cov-report=json:../docs/tracking/seams/$SEAM_DIR/coverage-backend.json \
      2>/dev/null || echo "⚠️ Tests not found or failed" >&2

    # Run code quality checks
    ruff check app/$SEAM_DIR/ --output-format=json > ../docs/tracking/seams/$SEAM_DIR/ruff-results.json 2>/dev/null || true
    mypy app/$SEAM_DIR/ --json > ../docs/tracking/seams/$SEAM_DIR/mypy-results.json 2>/dev/null || true
    ;;

  "frontend-migration")
    echo "  → Running frontend tests and capturing results..." >&2
    cd frontend 2>/dev/null || exit 0

    # Run vitest with JSON reporter
    npm test -- --reporter=json --outputFile=../docs/tracking/seams/$SEAM_DIR/test-results-frontend.json --run 2>/dev/null || echo "⚠️ Tests not found or failed" >&2

    # Run coverage
    npm test -- --coverage --reporter=json --outputFile=../docs/tracking/seams/$SEAM_DIR/coverage-frontend.json --run 2>/dev/null || true

    # Run lint
    npm run lint -- --format=json > ../docs/tracking/seams/$SEAM_DIR/eslint-results.json 2>/dev/null || true
    ;;

  "parity-harness-generator")
    echo "  → Capturing parity results..." >&2

    # Check if verification-results.json exists
    if [ -f "docs/legacy-golden/parity-results/$SEAM_DIR/verification-results.json" ]; then
      # Copy to tracking directory
      cp docs/legacy-golden/parity-results/$SEAM_DIR/verification-results.json \
         docs/tracking/seams/$SEAM_DIR/parity-results.json

      # Copy diff screenshots if they exist
      if [ -d "docs/legacy-golden/parity-results/$SEAM_DIR/screenshots/diff" ]; then
        mkdir -p docs/tracking/seams/$SEAM_DIR/parity-diff
        cp docs/legacy-golden/parity-results/$SEAM_DIR/screenshots/diff/*.png \
           docs/tracking/seams/$SEAM_DIR/parity-diff/ 2>/dev/null || true
      fi
    fi
    ;;
esac

echo "✅ Metrics captured for $AGENT" >&2
exit 0
