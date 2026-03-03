# Migration Activity Logging Hooks

Automatic event logging for agent lifecycle tracking.

## Overview

These hooks capture agent start/stop events automatically without requiring code changes to agents or orchestrator.

## Hook Scripts

### log-agent-start.sh
- **Trigger:** `SubagentStart` event
- **Logs:** Agent name, description, timestamp
- **Output:** `docs/tracking/migration-activity.jsonl`

### log-agent-stop.sh
- **Trigger:** `SubagentStop` event
- **Logs:** Agent name, status, timestamp
- **Output:** `docs/tracking/migration-activity.jsonl`

## Configuration

Hooks are configured in `.claude/settings.json`:

```json
{
  "hooks": {
    "SubagentStart": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": ".claude/hooks/log-agent-start.sh"
          }
        ]
      }
    ],
    "SubagentStop": [...]
  }
}
```

## Event Log Format

Events are logged in JSON Lines format (one JSON per line):

```jsonl
{"timestamp":"2026-03-03T10:00:00Z","event":"agent_started","agent":"seam-discovery","description":"Analyze codebase"}
{"timestamp":"2026-03-03T10:30:00Z","event":"agent_completed","agent":"seam-discovery","status":"completed"}
```

## Testing

To verify hooks are working:

```bash
# Check hook scripts are executable
ls -la .claude/hooks/*.sh

# Check settings.json has hooks configured
cat .claude/settings.json | jq '.hooks.SubagentStart'

# Run a test agent and check log
# (spawn any agent via orchestrator)
tail docs/tracking/migration-activity.jsonl
```

## Troubleshooting

**Hooks not firing?**
1. Check scripts are executable: `chmod +x .claude/hooks/*.sh`
2. Check settings.json syntax is valid JSON
3. Check `jq` is installed: `which jq`

**Log file not created?**
1. Check `docs/tracking/` directory exists
2. Check write permissions on `docs/tracking/`
3. Hooks create the directory automatically if missing
