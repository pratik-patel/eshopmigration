#!/bin/bash
# Log when an agent stops
# Triggered by SubagentStop hook
# FIXED: No jq dependency - uses pure bash

# Read stdin input (JSON data from Claude Code)
INPUT=$(cat)

# Extract agent_type using pure bash (no jq required)
AGENT=$(echo "$INPUT" | grep -oP '"agent_type"\s*:\s*"\K[^"]+' 2>/dev/null)

# Fallback if empty
if [ -z "$AGENT" ]; then
    AGENT="unknown-agent"
fi

# Get result/status using pure bash
RESULT=$(echo "$INPUT" | grep -oP '"status"\s*:\s*"\K[^"]+' 2>/dev/null)
if [ -z "$RESULT" ]; then
    RESULT="completed"
fi

# Get error if any using pure bash
ERROR=$(echo "$INPUT" | grep -oP '"error"\s*:\s*"\K[^"]+' 2>/dev/null)

# Get timestamp
TIMESTAMP=$(date -Iseconds)

# Ensure tracking directory exists
mkdir -p docs/tracking

# Build log entry
if [ -n "$ERROR" ] && [ "$ERROR" != "null" ]; then
    echo "{\"timestamp\":\"$TIMESTAMP\",\"event\":\"agent_completed\",\"agent\":\"$AGENT\",\"status\":\"$RESULT\",\"error\":\"$ERROR\"}" >> docs/tracking/migration-activity.jsonl
else
    echo "{\"timestamp\":\"$TIMESTAMP\",\"event\":\"agent_completed\",\"agent\":\"$AGENT\",\"status\":\"$RESULT\"}" >> docs/tracking/migration-activity.jsonl
fi

# Also log raw input for debugging (optional, comment out in production)
if [ -n "$INPUT" ]; then
    echo "$INPUT" >> docs/tracking/hook-debug.log 2>/dev/null || true
fi

# Exit 0 (always allow completion)
exit 0
