#!/bin/bash
# Log when an agent starts
# Triggered by SubagentStart hook

INPUT=$(cat)
AGENT=$(echo "$INPUT" | jq -r '.subagent_type')
DESCRIPTION=$(echo "$INPUT" | jq -r '.description // ""')
TIMESTAMP=$(date -Iseconds)

# Ensure tracking directory exists
mkdir -p docs/tracking

# Append to activity log (JSON Lines format)
echo "{\"timestamp\":\"$TIMESTAMP\",\"event\":\"agent_started\",\"agent\":\"$AGENT\",\"description\":\"$DESCRIPTION\"}" >> docs/tracking/migration-activity.jsonl

# Exit 0 to allow agent to proceed
exit 0
