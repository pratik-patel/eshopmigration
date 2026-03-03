---
name: migrate
description: Run full migration orchestrator
---

# Migration Orchestrator Skill

Spawns the `migration-orchestrator` agent to execute the full migration workflow.

## Usage

```bash
/migrate                        # Semi-automated mode (default)
/migrate --mode=full-automation # Full automation mode
/migrate --help                 # Show help
```

## Implementation

Spawn the `migration-orchestrator` agent with user arguments:

**Agent Type:** `migration-orchestrator`
**Arguments:** Pass through `$ARGUMENTS` from user
**Description:** "Execute full migration workflow"

The agent will:
1. Detect mode from arguments
2. Validate workspace
3. Execute phases 0-5
4. Generate migration outputs
