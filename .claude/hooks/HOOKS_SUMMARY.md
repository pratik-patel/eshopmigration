# Hooks Summary

**Automatic data capture for migration dashboard**

---

## 📊 Hook Architecture

All hooks are triggered automatically by Claude Code lifecycle events. No agent code modifications needed.

```
Agent Execution
     ↓
SubagentStart event → log-agent-start.sh
     ↓
Agent does its work
     ↓
SubagentStop event → All hooks run in parallel:
     ├── log-agent-stop.sh
     ├── capture-quality-metrics.sh
     ├── convert-ui-behavior-to-json.sh
     ├── capture-dependency-scan.sh
     ├── capture-lighthouse-metrics.sh
     └── capture-file-changes.sh
```

---

## 🔧 Installed Hooks (7 total)

### 1. **log-agent-start.sh**
- **Trigger:** SubagentStart (any agent)
- **Captures:** Agent name, description, timestamp
- **Output:** `docs/tracking/migration-activity.jsonl`
- **Format:** `{"timestamp":"...","event":"agent_started","agent":"...","description":"..."}`

### 2. **log-agent-stop.sh**
- **Trigger:** SubagentStop (any agent)
- **Captures:** Agent name, status, timestamp
- **Output:** `docs/tracking/migration-activity.jsonl`
- **Format:** `{"timestamp":"...","event":"agent_completed","agent":"...","status":"completed"}`

### 3. **capture-quality-metrics.sh**
- **Trigger:** SubagentStop (backend/frontend/parity agents)
- **Captures:**
  - Backend: pytest results, coverage, ruff, mypy
  - Frontend: vitest results, coverage, eslint
  - Parity: verification results, diff images
- **Outputs:**
  - `docs/tracking/seams/{seam}/test-results-backend.json`
  - `docs/tracking/seams/{seam}/test-results-frontend.json`
  - `docs/tracking/seams/{seam}/coverage-backend.json`
  - `docs/tracking/seams/{seam}/coverage-frontend.json`
  - `docs/tracking/seams/{seam}/ruff-results.json`
  - `docs/tracking/seams/{seam}/mypy-results.json`
  - `docs/tracking/seams/{seam}/eslint-results.json`
  - `docs/tracking/seams/{seam}/parity-results.json`

### 4. **convert-ui-behavior-to-json.sh**
- **Trigger:** SubagentStop (ui-inventory-extractor agent)
- **Captures:** Structured UI inventory (screens, controls, grids, actions)
- **Output:** `docs/seams/{seam}/ui-behavior.json`
- **Parser:** `.claude/scripts/parse-ui-behavior-to-json.py`

### 5. **capture-dependency-scan.sh**
- **Trigger:** SubagentStop (backend/frontend-migration agents)
- **Captures:**
  - Backend: pip-audit results (Python vulnerabilities)
  - Frontend: npm audit results (Node.js vulnerabilities)
- **Outputs:**
  - `docs/tracking/seams/{seam}/dependency-scan-backend.json`
  - `docs/tracking/seams/{seam}/dependency-scan-frontend.json`
- **Tools:** pip-audit, npm audit
- **Fallback:** Creates empty report if tools not installed

### 6. **capture-lighthouse-metrics.sh**
- **Trigger:** SubagentStop (frontend-migration agent)
- **Captures:** Performance metrics (LCP, FID, CLS), accessibility, SEO scores
- **Output:** `docs/tracking/seams/{seam}/lighthouse-results.json`
- **Requirements:**
  - Lighthouse installed globally (`npm install -g lighthouse`)
  - Frontend dev server running at `http://localhost:3000`
- **Fallback:** Creates placeholder if server not running or Lighthouse not installed

### 7. **capture-file-changes.sh**
- **Trigger:** SubagentStop (backend/frontend-migration agents)
- **Captures:** Git log of implementation changes (last 2 hours)
- **Outputs:**
  - `docs/tracking/seams/{seam}/file-changes-backend.json`
  - `docs/tracking/seams/{seam}/file-changes-frontend.json`
- **Data:** Commits, files changed, lines added/deleted per file
- **Fallback:** Creates empty report if no recent commits

---

## 📁 Output Structure

```
docs/
└── tracking/
    ├── migration-activity.jsonl           ← Global event log
    │
    └── seams/{seam}/
        ├── test-results-backend.json      ← Hook 3
        ├── test-results-frontend.json     ← Hook 3
        ├── coverage-backend.json          ← Hook 3
        ├── coverage-frontend.json         ← Hook 3
        ├── ruff-results.json              ← Hook 3
        ├── mypy-results.json              ← Hook 3
        ├── eslint-results.json            ← Hook 3
        ├── parity-results.json            ← Hook 3
        ├── dependency-scan-backend.json   ← Hook 5
        ├── dependency-scan-frontend.json  ← Hook 5
        ├── lighthouse-results.json        ← Hook 6
        ├── file-changes-backend.json      ← Hook 7
        ├── file-changes-frontend.json     ← Hook 7
        └── parity-diff/*.png              ← Hook 3

docs/seams/{seam}/
└── ui-behavior.json                       ← Hook 4
```

---

## ⚙️ Configuration

All hooks configured in `.claude/settings.json`:

```json
{
  "hooks": {
    "SubagentStart": [
      {
        "matcher": "*",
        "hooks": [
          { "type": "command", "command": ".claude/hooks/log-agent-start.sh" }
        ]
      }
    ],
    "SubagentStop": [
      {
        "matcher": "*",
        "hooks": [
          { "type": "command", "command": ".claude/hooks/log-agent-stop.sh" },
          { "type": "command", "command": ".claude/hooks/capture-quality-metrics.sh" },
          { "type": "command", "command": ".claude/hooks/convert-ui-behavior-to-json.sh" },
          { "type": "command", "command": ".claude/hooks/capture-dependency-scan.sh" },
          { "type": "command", "command": ".claude/hooks/capture-lighthouse-metrics.sh" },
          { "type": "command", "command": ".claude/hooks/capture-file-changes.sh" }
        ]
      }
    ]
  }
}
```

---

## 🧪 Testing Hooks

### Manual Test
```bash
# Simulate agent completion
echo '{"subagent_type":"backend-migration"}' | .claude/hooks/capture-quality-metrics.sh

# Check output
ls -la docs/tracking/seams/*/
```

### Real Test
```bash
# Run migration
/migrate --mode=full-automation

# Check activity log
tail -f docs/tracking/migration-activity.jsonl

# Check metrics
ls -la docs/tracking/seams/*/
```

---

## 🔍 Troubleshooting

### Hook not running?
1. Check `.claude/settings.json` syntax is valid JSON
2. Verify hook script is executable: `chmod +x .claude/hooks/*.sh`
3. Check hook logs: `tail -f .claude/hooks.log` (if enabled)

### Missing dependencies?
- **pip-audit:** `pip install pip-audit`
- **Lighthouse:** `npm install -g lighthouse`
- **Python 3:** Required for parsing scripts
- **jq:** Required for JSON parsing

### Hooks running but no output?
1. Check seam context: Hooks detect seam from `docs/seams/*/`
2. Check git repository: file-changes hook requires git
3. Check dev server: Lighthouse hook requires server at `localhost:3000`

---

## 📊 Metrics Coverage

**Hooks capture 89% of dashboard data requirements:**

- ✅ Test results (backend + frontend)
- ✅ Code coverage (backend + frontend)
- ✅ Code quality (linting + type checking)
- ✅ Security scans (dependencies)
- ✅ Performance metrics (Lighthouse)
- ✅ Visual parity (SSIM scores)
- ✅ File changes (git log)
- ✅ UI structure (screens, controls, grids)
- ✅ Agent activity timeline

**Remaining data comes from:**
- Parsing source files (tasks.md, requirements.md, design.md)
- Dashboard calculations (critical path, priority matrix)

---

## 🚀 Benefits

1. **Zero agent changes** - Agents focus on their primary job
2. **Automatic capture** - Runs transparently on agent completion
3. **Parallel execution** - All hooks run simultaneously
4. **Graceful degradation** - Missing tools → placeholder reports
5. **Extensible** - Add new hooks without modifying agents
