# Data Capture Architecture

**Hook-based, source-of-truth pattern for dashboard data**

---

## 🎯 Design Principles

1. **Hooks capture real-time data** (test results, coverage, quality metrics)
2. **Dashboard parses source files** (tasks.md, requirements.md, design.md)
3. **Agents generate only unavoidable aggregations** (coverage-audit.json)
4. **No duplication** (one source of truth per data type)

---

## 📁 Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│ AGENT EXECUTION                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Agent 101: seam-discovery                                  │
│   └─> docs/context-fabric/seam-proposals.json              │
│   └─> docs/context-fabric/dependency-graph.json            │
│                                                             │
│  Agent 105: spec-agent                                      │
│   └─> docs/seams/{seam}/requirements.md   ◄──┐             │
│   └─> docs/seams/{seam}/design.md         ◄──┤ Dashboard   │
│   └─> docs/seams/{seam}/tasks.md          ◄──┤ parses      │
│   └─> docs/seams/{seam}/contracts/openapi.yaml  ◄─┘         │
│                                                             │
│  Agent 107: backend-migration                               │
│   └─> backend/app/{seam}/*.py                              │
│   └─> backend/tests/                                       │
│         │                                                   │
│         └─> [Hook captures] ───┐                           │
│                                 │                           │
│  Agent 108: frontend-migration  │                           │
│   └─> frontend/src/pages/{seam}/                           │
│   └─> frontend/tests/           │                           │
│         │                        │                           │
│         └─> [Hook captures] ───┤                           │
│                                 │                           │
│  Agent 110: parity-harness      │                           │
│   └─> docs/legacy-golden/parity-results/{seam}/            │
│         VERIFICATION_SUMMARY.md ◄──── Dashboard parses      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────┐
│ HOOKS (AUTOMATIC DATA CAPTURE)                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  SubagentStart hook (.claude/hooks/log-agent-start.sh)     │
│   └─> docs/tracking/migration-activity.jsonl               │
│       {"event":"agent_started","agent":"...","timestamp":"..."}  │
│                                                             │
│  SubagentStop hook (.claude/hooks/log-agent-stop.sh)       │
│   └─> docs/tracking/migration-activity.jsonl               │
│       {"event":"agent_completed","agent":"...","status":"..."}   │
│                                                             │
│  SubagentStop hook (.claude/hooks/capture-quality-metrics.sh)  │
│   └─> IF agent=backend-migration:                          │
│       ├─> pytest --json-report                             │
│       │   └─> docs/tracking/seams/{seam}/test-results-backend.json  │
│       ├─> pytest --cov                                     │
│       │   └─> docs/tracking/seams/{seam}/coverage-backend.json     │
│       └─> ruff + mypy                                      │
│           └─> docs/tracking/seams/{seam}/ruff-results.json        │
│           └─> docs/tracking/seams/{seam}/mypy-results.json        │
│                                                             │
│   └─> IF agent=frontend-migration:                         │
│       ├─> vitest --reporter=json                           │
│       │   └─> docs/tracking/seams/{seam}/test-results-frontend.json  │
│       ├─> npm test --coverage                              │
│       │   └─> docs/tracking/seams/{seam}/coverage-frontend.json     │
│       └─> npm run lint                                     │
│           └─> docs/tracking/seams/{seam}/eslint-results.json       │
│                                                             │
│   └─> IF agent=parity-harness-generator:                   │
│       └─> Copy verification-results.json + diff images     │
│           └─> docs/tracking/seams/{seam}/parity-results.json      │
│           └─> docs/tracking/seams/{seam}/parity-diff/*.png        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────┐
│ DASHBOARD (READS DATA)                                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Data Source Priority:                                      │
│                                                             │
│  1. Parse source markdown/YAML files                        │
│     ✅ tasks.md         → extract checkboxes               │
│     ✅ requirements.md  → count EARS patterns              │
│     ✅ design.md        → extract components               │
│     ✅ openapi.yaml     → count endpoints                  │
│                                                             │
│  2. Read hook-generated JSON files                          │
│     ✅ test-results-*.json    → test metrics               │
│     ✅ coverage-*.json        → coverage reports           │
│     ✅ *-results.json         → quality metrics            │
│     ✅ migration-activity.jsonl → event timeline           │
│                                                             │
│  3. Parse agent-generated reports                           │
│     ✅ VERIFICATION_SUMMARY.md → parity scores             │
│     ✅ security-review.md      → security findings         │
│                                                             │
│  4. Agent-generated aggregations (only if necessary)        │
│     ⚠️ coverage-audit.json → per-module coverage (Phase 0) │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🗂️ File Structure

```
docs/
├── context-fabric/               # Phase 0: Discovery outputs
│   ├── seam-proposals.json
│   ├── dependency-graph.json
│   └── ...
│
├── seams/{seam}/                 # Per-seam specifications
│   ├── requirements.md           ← Dashboard parses
│   ├── design.md                 ← Dashboard parses
│   ├── tasks.md                  ← Dashboard parses
│   ├── discovery.md              ← Dashboard parses
│   ├── security-review.md        ← Dashboard parses
│   └── contracts/
│       └── openapi.yaml          ← Dashboard parses
│
├── legacy-golden/                # Baseline screenshots
│   └── parity-results/{seam}/
│       └── VERIFICATION_SUMMARY.md  ← Dashboard parses
│
└── tracking/                     # Metrics (hook-generated)
    ├── migration-activity.jsonl  ← Hooks append
    │
    └── seams/{seam}/
        ├── test-results-backend.json   ← Hook captures
        ├── test-results-frontend.json  ← Hook captures
        ├── coverage-backend.json       ← Hook captures
        ├── coverage-frontend.json      ← Hook captures
        ├── ruff-results.json           ← Hook captures
        ├── mypy-results.json           ← Hook captures
        ├── eslint-results.json         ← Hook captures
        ├── parity-results.json         ← Hook captures
        └── parity-diff/*.png           ← Hook captures
```

---

## 🔧 Hook Configuration

**`.claude/settings.json`:**

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
    "SubagentStop": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": ".claude/hooks/log-agent-stop.sh"
          },
          {
            "type": "command",
            "command": ".claude/hooks/capture-quality-metrics.sh"
          }
        ]
      }
    ]
  }
}
```

**When agent completes:**
1. `log-agent-stop.sh` logs completion event
2. `capture-quality-metrics.sh` captures quality data (if implementation/parity agent)

---

## ✅ Benefits

1. **No agent code changes** - agents focus on their primary job
2. **Automatic data capture** - hooks run transparently
3. **Single source of truth** - tasks.md is authoritative, not tasks-status.json
4. **No duplication** - dashboard parses source files directly
5. **Extensible** - add more hooks without modifying agents

---

## 📊 Dashboard Implementation

**When building dashboard pages:**

### Step 1: Check if source file exists

```python
# Good: Parse source file
def get_tasks(seam: str):
    tasks_md = Path(f"docs/seams/{seam}/tasks.md").read_text()
    return parse_checkbox_list(tasks_md)

# Bad: Require separate JSON
def get_tasks(seam: str):
    return json.load(f"docs/tracking/seams/{seam}/tasks-status.json")
```

### Step 2: Use hook-generated data

```python
# Good: Hook already captured it
def get_test_results(seam: str):
    return json.load(f"docs/tracking/seams/{seam}/test-results-backend.json")

# Bad: Re-run tests in dashboard
def get_test_results(seam: str):
    run_pytest()  # NO!
```

### Step 3: Request agent output (last resort)

```python
# Only if no source file exists and no hook can capture it
def get_coverage_audit():
    # Agent 101 must generate this during discovery
    return json.load(f"docs/tracking/coverage-audit.json")
```

---

## 🎯 Next Agent Updates

**Only one agent needs updating:**

### Agent 101: seam-discovery
**Add:** Generate `docs/tracking/coverage-audit.json` during Phase 0
**Why:** Aggregated per-module coverage data (no source file to parse)
**Format:**
```json
{
  "modules": [
    {
      "module_name": "UI/Forms",
      "total_files": 45,
      "covered_files": 45,
      "coverage_pct": 100
    }
  ]
}
```

**All other data is captured via hooks or parsed from source files!**
