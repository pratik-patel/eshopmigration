# Hook Troubleshooting Guide

## Issue: Agent Name Missing in Logs

### Symptom
Activity logs show empty agent names:
```json
{"timestamp":"2026-03-03T13:31:06-05:00","event":"agent_started","agent":"","description":""}
```

### Root Cause
The hook scripts were expecting JSON input on stdin with a `subagent_type` field, but Claude Code's hook system may provide agent information through different channels:
- Environment variables
- Command-line arguments
- Different JSON field names
- Or no input at all

### Solution Implemented

The hook scripts now try **4 methods** to capture the agent name (in order):

#### Method 1: JSON stdin (multiple field names)
```bash
AGENT=$(echo "$INPUT" | jq -r '.subagent_type // .agent // .name // empty' 2>/dev/null)
```
Checks for: `subagent_type`, `agent`, or `name` fields

#### Method 2: Environment variables
```bash
AGENT="${CLAUDE_AGENT_NAME:-${AGENT_NAME:-${SUBAGENT_TYPE:-}}}"
```
Checks for: `CLAUDE_AGENT_NAME`, `AGENT_NAME`, or `SUBAGENT_TYPE`

#### Method 3: Command-line arguments
```bash
if [ $# -gt 0 ]; then
    AGENT="$1"
fi
```
Uses first argument passed to the script

#### Method 4: Extract from recent logs
```bash
AGENT=$(tail -1 docs/tracking/migration-activity.jsonl | jq -r 'select(.event=="agent_started") | .agent')
```
For `agent_stopped` events, looks up the most recent `agent_started` entry

#### Fallback
```bash
if [ -z "$AGENT" ] || [ "$AGENT" == "null" ]; then
    AGENT="unknown-agent"
fi
```

### Debugging

The updated hooks write raw input to `docs/tracking/hook-debug.log`:
```bash
echo "$INPUT" >> docs/tracking/hook-debug.log 2>/dev/null || true
```

To see what Claude Code is actually sending:
```bash
tail -f docs/tracking/hook-debug.log
```

### Testing the Fix

1. **Check if hooks are executable**:
```bash
chmod +x .claude/hooks/*.sh
```

2. **Test agent name capture manually**:
```bash
# Simulate SubagentStart hook
echo '{"subagent_type":"backend-migration","description":"Test"}' | .claude/hooks/log-agent-start.sh

# Check the log
tail -1 docs/tracking/migration-activity.jsonl
```

Expected output:
```json
{"timestamp":"...","event":"agent_started","agent":"backend-migration","description":"Test"}
```

3. **Test with environment variable**:
```bash
CLAUDE_AGENT_NAME="test-agent" .claude/hooks/log-agent-start.sh < /dev/null
tail -1 docs/tracking/migration-activity.jsonl
```

Expected output:
```json
{"timestamp":"...","event":"agent_started","agent":"test-agent","description":""}
```

### Alternative: Pass Agent Name Explicitly

If hooks still don't capture the name, you can modify `.claude/settings.json` to pass the agent name as an argument:

```json
{
  "hooks": {
    "SubagentStart": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": ".claude/hooks/log-agent-start.sh {{subagent_type}}"
          }
        ]
      }
    ]
  }
}
```

**Note**: The `{{subagent_type}}` template syntax depends on Claude Code's hook system capabilities.

### Verifying the Fix

After running a migration:
```bash
# Check for any empty agent names
grep '"agent":""' docs/tracking/migration-activity.jsonl

# Should return nothing (or only old entries before the fix)
```

All new entries should have agent names populated:
```bash
# View recent activity
tail -5 docs/tracking/migration-activity.jsonl | jq .
```

### If Still Not Working

1. **Check Claude Code documentation** for the exact format of hook inputs
2. **Review hook-debug.log** to see what's actually being sent
3. **Add more logging** to the hook scripts to trace execution
4. **Contact Claude Code support** for official hook API documentation

## Common Issues

### Issue: "jq: command not found"

**Solution**: Install jq:
```bash
# On Ubuntu/Debian
sudo apt-get install jq

# On macOS
brew install jq

# On Windows (Git Bash)
# Download from https://stedolan.github.io/jq/download/
```

### Issue: Permission denied

**Solution**: Make hooks executable:
```bash
chmod +x .claude/hooks/*.sh
```

### Issue: Logs not created

**Solution**: Ensure directory exists:
```bash
mkdir -p docs/tracking
```

### Issue: Hooks not triggering

**Solution**: Verify `.claude/settings.json` syntax:
```bash
jq . .claude/settings.json
```

If syntax is invalid, the hooks won't load.

## Best Practices

1. **Always test hooks locally** before committing
2. **Keep debug logging enabled** during migration setup
3. **Disable debug logging in production** to avoid log bloat
4. **Monitor hook-debug.log size** (rotate if it gets too large)
5. **Validate activity log format** with `jq` regularly

## Related Files

- `.claude/hooks/log-agent-start.sh` - Agent start logging
- `.claude/hooks/log-agent-stop.sh` - Agent completion logging
- `.claude/settings.json` - Hook configuration
- `docs/tracking/migration-activity.jsonl` - Activity log output
- `docs/tracking/hook-debug.log` - Raw hook input for debugging
