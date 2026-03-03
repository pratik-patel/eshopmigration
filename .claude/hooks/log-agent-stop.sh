#!/bin/bash
# Log when an agent stops
# Triggered by SubagentStop hook

# Read stdin input
INPUT=$(cat)

# Try to extract agent name from multiple sources
AGENT=""

# Method 1: From JSON input (stdin)
if [ -n "$INPUT" ]; then
    AGENT=$(echo "$INPUT" | jq -r '.subagent_type // .agent // .name // empty' 2>/dev/null)
fi

# Method 2: From environment variables
if [ -z "$AGENT" ]; then
    AGENT="${CLAUDE_AGENT_NAME:-${AGENT_NAME:-${SUBAGENT_TYPE:-}}}"
fi

# Method 3: From command line arguments
if [ -z "$AGENT" ] && [ $# -gt 0 ]; then
    AGENT="$1"
fi

# Method 4: Try to find from recent start log
if [ -z "$AGENT" ] || [ "$AGENT" == "null" ]; then
    if [ -f docs/tracking/migration-activity.jsonl ]; then
        AGENT=$(tail -1 docs/tracking/migration-activity.jsonl | jq -r 'select(.event=="agent_started") | .agent' 2>/dev/null)
    fi
fi

# Fallback
if [ -z "$AGENT" ] || [ "$AGENT" == "null" ]; then
    AGENT="unknown-agent"
fi

# Get result/status
RESULT=$(echo "$INPUT" | jq -r '.result // .status // "completed"' 2>/dev/null)
if [ -z "$RESULT" ] || [ "$RESULT" == "null" ]; then
    RESULT="completed"
fi

# Get error if any
ERROR=$(echo "$INPUT" | jq -r '.error // empty' 2>/dev/null)

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
