#!/bin/bash
# Log when an agent starts
# Triggered by SubagentStart hook

# Read stdin input
INPUT=$(cat)

# Try to extract agent name from multiple sources
AGENT=""

# Method 1: From JSON input (stdin)
if [ -n "$INPUT" ]; then
    AGENT=$(echo "$INPUT" | jq -r '.subagent_type // .agent // .name // empty' 2>/dev/null)
fi

# Method 2: From environment variables (Claude Code may set these)
if [ -z "$AGENT" ]; then
    AGENT="${CLAUDE_AGENT_NAME:-${AGENT_NAME:-${SUBAGENT_TYPE:-}}}"
fi

# Method 3: From command line arguments
if [ -z "$AGENT" ] && [ $# -gt 0 ]; then
    AGENT="$1"
fi

# Method 4: Extract from description if available
if [ -z "$AGENT" ]; then
    DESCRIPTION=$(echo "$INPUT" | jq -r '.description // .prompt // empty' 2>/dev/null)
    # Try to extract agent name from description like "backend-migration" or "101-legacy-context-fabric"
    AGENT=$(echo "$DESCRIPTION" | grep -oE '[0-9]{3}-[a-z-]+|[a-z]+-[a-z]+' | head -1)
fi

# Fallback: Use "unknown-agent"
if [ -z "$AGENT" ] || [ "$AGENT" == "null" ]; then
    AGENT="unknown-agent"
fi

# Get description
DESCRIPTION=$(echo "$INPUT" | jq -r '.description // .prompt // ""' 2>/dev/null)
if [ -z "$DESCRIPTION" ] || [ "$DESCRIPTION" == "null" ]; then
    DESCRIPTION=""
fi

# Get timestamp
TIMESTAMP=$(date -Iseconds)

# Ensure tracking directory exists
mkdir -p docs/tracking

# Append to activity log (JSON Lines format)
echo "{\"timestamp\":\"$TIMESTAMP\",\"event\":\"agent_started\",\"agent\":\"$AGENT\",\"description\":\"$DESCRIPTION\"}" >> docs/tracking/migration-activity.jsonl

# Also log raw input for debugging (optional, comment out in production)
if [ -n "$INPUT" ]; then
    echo "$INPUT" >> docs/tracking/hook-debug.log 2>/dev/null || true
fi

# Exit 0 to allow agent to proceed
exit 0
