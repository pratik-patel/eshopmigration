#!/bin/bash
# FIXED: Log when an agent starts
# Triggered by SubagentStart hook

# Read stdin input (JSON data from Claude Code)
INPUT=$(cat)

# Extract agent_type from JSON (this is the key field)
AGENT=$(echo "$INPUT" | jq -r '.agent_type // empty' 2>/dev/null)

# Fallback if empty
if [ -z "$AGENT" ] || [ "$AGENT" == "null" ]; then
    AGENT="unknown-agent"
fi

# Get timestamp
TIMESTAMP=$(date -Iseconds)

# Ensure tracking directory exists
mkdir -p docs/tracking

# Append to activity log (JSON Lines format)
echo "{\"timestamp\":\"$TIMESTAMP\",\"event\":\"agent_started\",\"agent\":\"$AGENT\"}" >> docs/tracking/migration-activity.jsonl

# Debug logging (to verify it's working)
echo "=== Agent Start Hook ===" >> docs/tracking/hook-debug.log
echo "Timestamp: $TIMESTAMP" >> docs/tracking/hook-debug.log
echo "Agent extracted: $AGENT" >> docs/tracking/hook-debug.log
echo "Raw JSON input: $INPUT" >> docs/tracking/hook-debug.log
echo "=======================" >> docs/tracking/hook-debug.log
echo "" >> docs/tracking/hook-debug.log

# Exit 0 to allow agent to proceed
exit 0
