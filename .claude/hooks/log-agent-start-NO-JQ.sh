#!/bin/bash
# FIXED: Log when an agent starts (NO jq required - pure bash)
# Triggered by SubagentStart hook

# Read stdin input (JSON data from Claude Code)
INPUT=$(cat)

# Extract agent_type using pure bash (no jq required)
# Look for "agent_type":"value" pattern
AGENT=$(echo "$INPUT" | grep -oP '"agent_type"\s*:\s*"\K[^"]+' 2>/dev/null)

# Fallback if empty
if [ -z "$AGENT" ]; then
    AGENT="unknown-agent"
fi

# Get timestamp
TIMESTAMP=$(date -Iseconds)

# Ensure tracking directory exists
mkdir -p docs/tracking

# Append to activity log (JSON Lines format)
echo "{\"timestamp\":\"$TIMESTAMP\",\"event\":\"agent_started\",\"agent\":\"$AGENT\"}" >> docs/tracking/migration-activity.jsonl

# Debug logging
{
    echo "=== Agent Start Hook (NO-JQ) ==="
    echo "Timestamp: $TIMESTAMP"
    echo "Agent extracted: $AGENT"
    echo "Raw JSON input: $INPUT"
    echo "================================"
    echo ""
} >> docs/tracking/hook-debug.log 2>/dev/null || true

# Exit 0 to allow agent to proceed
exit 0
