# Migration Tracking Data

This directory contains structured metrics and logs for dashboard visualization.

## Directory Structure

```
docs/tracking/
├── migration-activity.jsonl      # Global event log (all agents)
├── coverage-audit.json           # Agent 101: Module coverage breakdown
├── iteration-history.json        # Agent 101: Discovery iterations
│
└── seams/{seam}/                 # Per-seam metrics
    ├── data-access.json          # Agent 104: Structured data access
    ├── requirements-stats.json   # Agent 105: Req counts/stats
    ├── tasks-status.json         # Agent 105+107+108: Task tracking
    ├── test-results.json         # Agent 107+108: Test results
    ├── code-quality.json         # Agent 107+108: Linting/quality
    ├── security-review.json      # Agent 109: Security scan results
    └── parity-results.json       # Agent 110: Visual parity SSIM scores
```

## Event Log Format

`migration-activity.jsonl` uses JSON Lines format (one JSON object per line):

```jsonl
{"timestamp":"2026-03-03T10:00:00Z","event":"migration_started","mode":"semi-automated"}
{"timestamp":"2026-03-03T10:05:00Z","event":"agent_started","agent":"seam-discovery","description":"..."}
{"timestamp":"2026-03-03T10:35:00Z","event":"agent_completed","agent":"seam-discovery","status":"completed"}
```

## How Events Are Logged

Events are automatically captured via hooks in `.claude/settings.json`:
- **SubagentStart** → logs `agent_started`
- **SubagentStop** → logs `agent_completed`

No code changes needed in agents or orchestrator.

## Dashboard Usage

The migration report dashboard reads these files to generate:
- Overview metrics (health score, progress)
- Phase 0-6 detailed pages
- Real-time agent activity feed
- Analytics & trends

See `.claude/skills/migration-report-dashboard/` for dashboard implementation.
