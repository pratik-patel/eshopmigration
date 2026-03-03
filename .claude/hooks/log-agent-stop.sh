#!/bin/bash
# Log when an agent completes
# Triggered by SubagentStop hook

INPUT=$(cat)
AGENT=$(echo "$INPUT" | jq -r '.subagent_type')
TIMESTAMP=$(date -Iseconds)

# Check if agent succeeded or failed
# SubagentStop doesn't include result status, so we infer from the fact it completed
STATUS="completed"

# Ensure tracking directory exists
mkdir -p docs/tracking

# Append to activity log (JSON Lines format)
echo "{\"timestamp\":\"$TIMESTAMP\",\"event\":\"agent_completed\",\"agent\":\"$AGENT\",\"status\":\"$STATUS\"}" >> docs/tracking/migration-activity.jsonl

# Exit 0 (always allow completion)
exit 0
