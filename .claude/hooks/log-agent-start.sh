#!/bin/bash
# Log when an agent starts
# Triggered by SubagentStart hook
# FIXED: No jq dependency - uses pure bash

# Read stdin input (JSON data from Claude Code)
INPUT=$(cat)

# Extract agent_type using pure bash (no jq required)
AGENT=$(echo "$INPUT" | grep -oP '"agent_type"\s*:\s*"\K[^"]+' 2>/dev/null)

# Fallback if empty
if [ -z "$AGENT" ]; then
    AGENT="unknown-agent"
fi

# Extract description using pure bash
DESCRIPTION=$(echo "$INPUT" | grep -oP '"description"\s*:\s*"\K[^"]+' 2>/dev/null)

# Get timestamp
TIMESTAMP=$(date -Iseconds)

# Ensure tracking directory exists
mkdir -p docs/tracking

# Append to activity log (JSON Lines format)
echo "{\"timestamp\":\"$TIMESTAMP\",\"event\":\"agent_started\",\"agent\":\"$AGENT\",\"description\":\"$DESCRIPTION\"}" >> docs/tracking/migration-activity.jsonl

# Debug logging (optional, comment out in production)
mkdir -p docs/tracking
{
    echo "=== SubagentStart Hook Debug ==="
    echo "Timestamp: $(date -Iseconds)"
    echo "HOOK_EVENT: ${HOOK_EVENT:-<not set>}"
    echo "HOOK_MATCHER: ${HOOK_MATCHER:-<not set>}"
    echo "AGENT (extracted): $AGENT"
    echo "STDIN Input:"
    echo "$INPUT"
    echo "Environment vars:"
    env | grep -E "(HOOK|AGENT|CLAUDE)" || echo "No matching env vars"
    echo "==================================="
    echo ""
} >> docs/tracking/hook-debug.log 2>/dev/null || true

# Exit 0 to allow agent to proceed
exit 0
