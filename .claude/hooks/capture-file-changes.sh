#!/bin/bash
# Capture file changes from git log
# Triggered by SubagentStop hook for backend/frontend migration agents

INPUT=$(cat)
AGENT=$(echo "$INPUT" | jq -r '.subagent_type')

# Only run for implementation agents
if [[ ! "$AGENT" =~ ^(backend-migration|frontend-migration)$ ]]; then
  exit 0
fi

echo "📝 Capturing file changes..." >&2

# Extract seam name from current context
SEAM_DIR=$(find docs/seams -type d -maxdepth 1 -name "*" | head -1 | xargs basename 2>/dev/null)

if [ -z "$SEAM_DIR" ]; then
  echo "⚠️ No seam context found, skipping file changes capture" >&2
  exit 0
fi

mkdir -p docs/tracking/seams/$SEAM_DIR

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
  echo "⚠️ Not a git repository, skipping file changes capture" >&2
  exit 0
fi

echo "  → Analyzing git log for recent changes..." >&2

# Get changes from the last 2 hours (implementation timeframe)
SINCE_TIME=$(date -d '2 hours ago' -Iseconds 2>/dev/null || date -v-2H -Iseconds 2>/dev/null)

# Capture file changes with stats
git log --since="$SINCE_TIME" \
  --numstat \
  --pretty=format:'{"commit":"%H","author":"%an","date":"%aI","message":"%s"}' \
  | python3 -c "
import sys
import json
from datetime import datetime

commits = []
current_commit = None
files = []

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue

    # Try to parse as commit JSON
    if line.startswith('{'):
        if current_commit and files:
            current_commit['files'] = files
            commits.append(current_commit)
            files = []

        try:
            current_commit = json.loads(line)
        except:
            pass

    # Parse numstat (added, deleted, filename)
    elif '\t' in line:
        parts = line.split('\t')
        if len(parts) == 3:
            added, deleted, filename = parts
            files.append({
                'filename': filename,
                'lines_added': int(added) if added.isdigit() else 0,
                'lines_deleted': int(deleted) if deleted.isdigit() else 0
            })

# Add last commit
if current_commit and files:
    current_commit['files'] = files
    commits.append(current_commit)

# Calculate totals
total_files = set()
total_lines_added = 0
total_lines_deleted = 0

for commit in commits:
    for f in commit.get('files', []):
        total_files.add(f['filename'])
        total_lines_added += f['lines_added']
        total_lines_deleted += f['lines_deleted']

output = {
    'seam': '$SEAM_DIR',
    'layer': '$AGENT'.replace('-migration', ''),
    'timestamp': '$(date -Iseconds)',
    'timeframe': '2 hours',
    'summary': {
        'total_commits': len(commits),
        'total_files': len(total_files),
        'total_lines_added': total_lines_added,
        'total_lines_deleted': total_lines_deleted,
        'net_lines': total_lines_added - total_lines_deleted
    },
    'commits': commits
}

print(json.dumps(output, indent=2))
" > docs/tracking/seams/$SEAM_DIR/file-changes-${AGENT//-migration/}.json 2>/dev/null

if [ -f "docs/tracking/seams/$SEAM_DIR/file-changes-${AGENT//-migration/}.json" ]; then
  COMMITS=$(jq -r '.summary.total_commits' docs/tracking/seams/$SEAM_DIR/file-changes-${AGENT//-migration/}.json 2>/dev/null)
  FILES=$(jq -r '.summary.total_files' docs/tracking/seams/$SEAM_DIR/file-changes-${AGENT//-migration/}.json 2>/dev/null)

  echo "  ✅ Captured $COMMITS commits affecting $FILES files" >&2
else
  echo "  ⚠️ No recent changes found" >&2

  # Create empty report
  cat > docs/tracking/seams/$SEAM_DIR/file-changes-${AGENT//-migration/}.json <<EOF
{
  "seam": "$SEAM_DIR",
  "layer": "${AGENT//-migration/}",
  "timestamp": "$(date -Iseconds)",
  "timeframe": "2 hours",
  "summary": {
    "total_commits": 0,
    "total_files": 0,
    "total_lines_added": 0,
    "total_lines_deleted": 0,
    "net_lines": 0
  },
  "commits": []
}
EOF
fi

exit 0
