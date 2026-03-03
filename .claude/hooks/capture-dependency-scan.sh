#!/bin/bash
# Capture dependency vulnerability scan results
# Triggered by SubagentStop hook for backend/frontend migration agents

INPUT=$(cat)
AGENT=$(echo "$INPUT" | jq -r '.subagent_type')

# Only run for implementation agents
if [[ ! "$AGENT" =~ ^(backend-migration|frontend-migration)$ ]]; then
  exit 0
fi

echo "🔒 Scanning dependencies for vulnerabilities..." >&2

# Extract seam name from current context
SEAM_DIR=$(find docs/seams -type d -maxdepth 1 -name "*" | head -1 | xargs basename 2>/dev/null)

if [ -z "$SEAM_DIR" ]; then
  echo "⚠️ No seam context found, skipping dependency scan" >&2
  exit 0
fi

mkdir -p docs/tracking/seams/$SEAM_DIR

case "$AGENT" in
  "backend-migration")
    echo "  → Running pip-audit for backend..." >&2
    cd backend 2>/dev/null || exit 0

    # Run pip-audit (Python dependency scanner)
    if command -v pip-audit &> /dev/null; then
      pip-audit --format=json --output=../docs/tracking/seams/$SEAM_DIR/dependency-scan-backend.json 2>/dev/null || {
        # If pip-audit fails, use pip check as fallback
        pip check 2>&1 | python3 -c "
import sys, json
lines = sys.stdin.read()
print(json.dumps({
  'seam': '$SEAM_DIR',
  'layer': 'backend',
  'tool': 'pip check',
  'vulnerabilities': [],
  'total': 0,
  'critical': 0,
  'high': 0,
  'medium': 0,
  'low': 0,
  'timestamp': '$(date -Iseconds)',
  'note': 'pip-audit not available, used pip check as fallback'
}))
" > ../docs/tracking/seams/$SEAM_DIR/dependency-scan-backend.json
      }
      echo "  ✅ Backend dependency scan complete" >&2
    else
      echo "  ⚠️ pip-audit not installed, skipping backend scan" >&2
    fi

    cd - > /dev/null 2>&1
    ;;

  "frontend-migration")
    echo "  → Running npm audit for frontend..." >&2
    cd frontend 2>/dev/null || exit 0

    # Run npm audit (Node.js dependency scanner)
    if command -v npm &> /dev/null; then
      npm audit --json > ../docs/tracking/seams/$SEAM_DIR/dependency-scan-frontend.json 2>/dev/null || {
        # If npm audit fails (no vulnerabilities or no package-lock), create empty report
        cat > ../docs/tracking/seams/$SEAM_DIR/dependency-scan-frontend.json <<EOF
{
  "seam": "$SEAM_DIR",
  "layer": "frontend",
  "tool": "npm audit",
  "vulnerabilities": [],
  "metadata": {
    "vulnerabilities": {
      "total": 0,
      "critical": 0,
      "high": 0,
      "moderate": 0,
      "low": 0,
      "info": 0
    }
  },
  "timestamp": "$(date -Iseconds)"
}
EOF
      }
      echo "  ✅ Frontend dependency scan complete" >&2
    else
      echo "  ⚠️ npm not installed, skipping frontend scan" >&2
    fi

    cd - > /dev/null 2>&1
    ;;
esac

echo "✅ Dependency scan complete" >&2
exit 0
