# Claude Code Hooks Integration

## Overview

This hook system provides automated code review, security analysis, and quality gates that run automatically during migration. The hooks are configured in `.claude/settings.json` and executed by shell scripts.

## Hook Types

### 1. Post-Write Hook
**Trigger**: After any file is written using the Write tool
**Purpose**: Immediate code quality and security check
**Script**: `post-code-hook.sh`

### 2. Post-Edit Hook
**Trigger**: After any file is edited using the Edit tool
**Purpose**: Immediate code quality and security check
**Script**: `post-code-hook.sh`

### 3. Post-Implementation Hook
**Trigger**: After a seam implementation completes
**Purpose**: Comprehensive quality gates before marking seam complete
**Script**: `post-implementation-hook.sh`

## Hook Execution Flow

```
┌─────────────────────────────────────────────────────────┐
│ Code Written/Edited                                     │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ post-code-hook.sh                                       │
│ ├── Determine stack (backend/frontend)                 │
│ ├── Run code-quality-check.sh                          │
│ ├── Run security-analysis.sh                           │
│ └── If issues found → auto-fix.sh                      │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ code-quality-check.sh                                   │
│ ├── Backend: Ruff, Black, MyPy, Complexity             │
│ ├── Frontend: ESLint, Prettier, TSC, Anti-patterns     │
│ └── Output: ✅ Pass or ❌ Fail                          │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ security-analysis.sh                                    │
│ ├── Backend: Bandit, Secret scan, SQL injection check  │
│ ├── Frontend: npm audit, XSS check, localStorage scan  │
│ ├── OWASP Top 10 checks                                │
│ └── Output: ✅ Pass or ❌ Fail                          │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
        ┌────────┴────────┐
        │   Issues?       │
        └────────┬────────┘
                 │
        ┌────────┴────────┐
        │  Yes            │  No
        ▼                 ▼
┌───────────────┐  ┌──────────────┐
│ auto-fix.sh   │  │ ✅ Complete  │
│ ├── Ruff fix │  └──────────────┘
│ ├── Black fmt│
│ ├── ESLint fx│
│ ├── Prettier │
│ └── Iterate  │
└───────┬───────┘
        │
        ▼
┌───────────────────┐
│ Re-check quality  │
│ Max 3 iterations  │
└───────────────────┘
```

## Quality Gates (Post-Implementation)

When a seam implementation completes, the `post-implementation-hook.sh` runs comprehensive checks:

### Backend Quality Gates
- ✅ Tests pass with ≥80% coverage
- ✅ Security scan passes (no high/critical issues)
- ✅ Type checking passes (strict mode)
- ✅ Code complexity within limits

### Frontend Quality Gates
- ✅ Tests pass with ≥75% coverage
- ✅ Accessibility tests present (jest-axe)
- ✅ Bundle size < 500KB
- ✅ No console.log in production code

### Contract Validation
- ✅ Backend endpoints match OpenAPI spec
- ✅ Frontend API calls match OpenAPI spec
- ✅ Required fields validation

### Integration & E2E Tests
- ✅ Integration tests pass
- ✅ E2E tests pass (Playwright)

### Documentation
- ✅ spec.md exists
- ✅ discovery.md exists
- ✅ contracts/openapi.yaml exists

### Security Review
- ✅ No hardcoded secrets
- ✅ No SQL injection risks
- ✅ No XSS vulnerabilities
- ✅ OWASP Top 10 compliance

### Performance
- ✅ Lighthouse score > 90
- ✅ API response times < 500ms

## Configuration

### Settings File: `.claude/settings.json`

```json
{
  "hooks": {
    "post-write": {
      "description": "Run code review and security analysis after writing code",
      "command": "bash .claude/scripts/post-code-hook.sh \"{{file_path}}\"",
      "background": false
    }
  },
  "quality_gates": {
    "code_coverage": {
      "backend_minimum": 80,
      "frontend_minimum": 75,
      "critical_paths": 95
    },
    "security": {
      "severity_threshold": "high",
      "block_on_critical": true,
      "auto_fix_enabled": true
    }
  }
}
```

### Quality Gate Thresholds

| Metric | Backend | Frontend |
|--------|---------|----------|
| Code Coverage | 80% | 75% |
| Critical Paths Coverage | 95% | 95% |
| Complexity (Cyclomatic) | ≤ 10 | ≤ 10 |
| Function Lines | ≤ 50 | ≤ 50 |
| File Lines | ≤ 500 | ≤ 500 |
| Bundle Size | N/A | < 500KB |

## Auto-Fix Features

The auto-fix system attempts to resolve issues automatically:

### Backend Auto-Fixes
1. **Ruff**: Fix linting errors
2. **Black**: Format code
3. **isort**: Sort imports
4. **autoflake**: Remove unused imports

### Frontend Auto-Fixes
1. **ESLint**: Fix linting errors (with --fix)
2. **Prettier**: Format code
3. **Remove console.log**: Strip from production code

### Iteration Limit
- Max 3 iterations per file
- After 3 iterations, manual review required

## Integration with Migration Agents

### Backend Migration Agent

The backend migration agent should trigger post-implementation hook:

```python
# At end of backend-migration agent
subprocess.run([
    "bash",
    ".claude/scripts/post-implementation-hook.sh",
    seam_name
], check=True)
```

### Frontend Migration Agent

The frontend migration agent should trigger post-implementation hook:

```typescript
// At end of frontend-migration agent
await exec(
  `bash .claude/scripts/post-implementation-hook.sh ${seamName}`
);
```

## Manual Execution

### Run post-code hook manually
```bash
bash .claude/scripts/post-code-hook.sh backend/app/catalog/router.py
```

### Run post-implementation hook manually
```bash
bash .claude/scripts/post-implementation-hook.sh catalog-list
```

### Run auto-fix for entire seam
```bash
bash .claude/scripts/auto-fix-seam.sh catalog-list
```

## Bypassing Hooks (Emergency)

To temporarily disable hooks during development:

```bash
export CLAUDE_HOOKS_DISABLED=1
# Your command here
unset CLAUDE_HOOKS_DISABLED
```

Or modify `.claude/settings.json`:
```json
{
  "hooks": {
    "post-write": {
      "enabled": false
    }
  }
}
```

## Troubleshooting

### Hook not executing
1. Check hook permissions: `chmod +x .claude/scripts/*.sh`
2. Verify settings.json syntax
3. Check logs in `/tmp/claude-hooks.log`

### Auto-fix not working
1. Ensure tools are installed (ruff, black, eslint, prettier)
2. Check Python/Node environment
3. Review `/tmp/claude-code-fixes-needed.flag`

### Quality gates failing
1. Run manual checks to see detailed errors
2. Use auto-fix-seam.sh to fix common issues
3. Review seam documentation for missing artifacts

## Dependencies

### Backend Tools
```bash
pip install ruff black mypy isort autoflake bandit safety radon pytest pytest-cov
```

### Frontend Tools
```bash
npm install -D eslint prettier typescript @typescript-eslint/parser @typescript-eslint/eslint-plugin
npm install -D @axe-core/react jest-axe
npm install -D playwright @playwright/test
```

### Optional Tools
```bash
# Lighthouse (performance)
npm install -g lighthouse

# k6 (load testing)
brew install k6  # or download from k6.io
```

## Best Practices

1. **Let hooks run**: Don't bypass unless necessary
2. **Review auto-fixes**: Check git diff after auto-fix
3. **Add tests first**: Hooks enforce coverage requirements
4. **Fix security issues immediately**: Don't commit with security flags
5. **Keep iterations low**: If auto-fix takes >3 iterations, refactor manually

## Continuous Improvement

The hook system should evolve with the project:
- Add new security patterns as discovered
- Update complexity thresholds based on team consensus
- Add custom linting rules for domain-specific patterns
- Integrate with CI/CD pipeline

## Support

For issues or improvements to the hook system:
1. Check this documentation
2. Review `.claude/scripts/*.sh` for implementation details
3. Consult CLAUDE.md for code quality standards
4. Report bugs in project issue tracker
