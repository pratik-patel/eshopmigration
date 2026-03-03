#!/bin/bash
# Convert ui-behavior.md to ui-behavior.json
# Triggered by SubagentStop hook for ui-inventory-extractor agent

INPUT=$(cat)
AGENT=$(echo "$INPUT" | jq -r '.subagent_type')

# Only run for ui-inventory-extractor agent
if [[ "$AGENT" != "ui-inventory-extractor" ]]; then
  exit 0
fi

echo "📄 Converting ui-behavior.md to JSON..." >&2

# Find all seams with ui-behavior.md
for seam_dir in docs/seams/*/; do
  seam=$(basename "$seam_dir")
  ui_behavior_md="$seam_dir/ui-behavior.md"

  if [ ! -f "$ui_behavior_md" ]; then
    continue
  fi

  echo "  → Processing $seam..." >&2

  # Use Python parser script
  python3 .claude/scripts/parse-ui-behavior-to-json.py "$seam"

  if [ $? -eq 0 ]; then
    echo "  ✅ Created ui-behavior.json for $seam" >&2
  else
    echo "  ⚠️ Failed to convert for $seam" >&2
  fi
done

echo "✅ UI behavior JSON conversion complete" >&2
exit 0
