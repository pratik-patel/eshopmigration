# Golden Baseline Capture Blockers

**Date**: 2026-03-02T00:00:00Z
**Blocker Status**: BLOCKED (Tool Limitations)
**Application Type**: Web Application (ASP.NET WebForms)

---

## Issues

### 1. Browser Automation Tool Not Available
- **Impact**: Cannot capture screenshots or interact with running legacy app at http://localhost:50586/
- **Root Cause**: Claude Code environment does not have Playwright/Selenium/Puppeteer installed
- **Workaround**: MANUAL CAPTURE required (see below)

### 2. WebFetch Tool Cannot Access Localhost
- **Impact**: Cannot fetch HTML responses from http://localhost:50586/
- **Root Cause**: WebFetch tool explicitly fails on localhost URLs
- **Workaround**: User must manually save HAR files or use curl commands

---

## Migration Impact

### What IS Possible
- ✅ All code implementation (already complete)
- ✅ Synthetic baseline generation from ui-behavior.md
- ✅ Manual visual validation by user
- ✅ Unit and integration tests (backend API)
- ✅ Component tests (frontend React)

### What Is BLOCKED
- ❌ Automated screenshot capture
- ❌ Automated parity tests comparing screenshots
- ❌ HAR file capture of HTTP traffic
- ❌ Automated user journey recording
- ❌ Full behavioral parity validation

### Impact Assessment
- **Parity validation**: Limited to manual comparison
- **Visual comparison**: User must visually compare legacy vs new
- **Behavior verification**: Code analysis + manual testing only
- **Automated regression tests**: Cannot generate screenshot-based tests

---

## Workarounds

### Option 1: User Manual Capture (RECOMMENDED)

User can capture baselines themselves using provided script:

**Required Tools**:
- Node.js 18+ with Playwright installed
- OR Python 3.12+ with Playwright installed
- Legacy app running at http://localhost:50586/

**Capture Script Location**: `scripts/capture-golden-baselines.js` (to be created)

**Steps**:
1. Ensure legacy app is running
2. Install Playwright: `npm install playwright` or `pip install playwright`
3. Run capture script: `node scripts/capture-golden-baselines.js catalog-list`
4. Script will save screenshots to `legacy-golden/catalog-list/screenshots/`

### Option 2: Synthetic Baselines (FALLBACK)

Generate synthetic baselines from existing documentation:
- Use `docs/seams/catalog-list/ui-behavior.md` for layout specifications
- Use `docs/context-fabric/business-rules.json` for validation rules
- Create mockup screenshots from UI behavior documentation
- Mark all baselines as **SYNTHETIC** in BASELINE_INDEX.md

### Option 3: Manual Visual Validation (CURRENT)

User performs side-by-side comparison:
1. Open legacy app: http://localhost:50586/
2. Open new app: http://localhost:5173/
3. Manually verify:
   - Table layout matches
   - Column order matches
   - Pagination behavior matches
   - Button text and styling matches
   - Validation messages match
4. Document results in `docs/seams/{seam}/evidence/manual-validation.md`

---

## Required Actions to Unblock

### Immediate (Current Sprint)
1. **User captures baselines** using Option 1 script (15-30 minutes per seam)
   - OR user performs Option 3 manual validation (5-10 minutes per seam)
2. **Agent proceeds** with remaining discovery/contract/data-strategy steps
3. **Parity tests**: Skip screenshot-based tests, focus on API/data tests

### Future (Post-Migration)
1. Set up CI/CD pipeline with Playwright in GitHub Actions
2. Automate screenshot regression tests in future sprints
3. Capture baselines in staging environment with full automation

---

## Timeline

**Current Status**: Migration 100% complete (code), 0% validated (automated parity)
**Blocker Introduced**: 2026-03-02 (during agent flow execution)
**Expected Resolution**:
- Manual validation by user: Immediate (today)
- Automated capture script: 1-2 hours development
- Full automated parity tests: Future sprint

---

## Fallback Strategy

If user cannot capture baselines:
1. Proceed with **SYNTHETIC_BASELINE_STRATEGY** (see below)
2. Mark all parity tests as "BASELINE_SYNTHETIC"
3. Require manual visual validation sign-off from user
4. Document known limitations in production deployment docs

---

## Mitigation for Current Migration

**Recommendation**: Proceed with Option 3 (Manual Visual Validation)

**Why**:
- Code is already complete and functional
- Manual validation is faster than setting up automation
- User can verify parity in 30-60 minutes total
- Automated parity tests can be added post-migration

**Action Items**:
1. ✅ Document this blocker (this file)
2. ✅ Create synthetic baseline strategy
3. ⏳ User performs manual validation
4. ⏳ Proceed with remaining agents (discovery, contracts, data-strategy)
5. ⏳ Document validation results in evidence.md per seam

---

## Contact

**Blocker Raised By**: Claude Code Agent (golden-baseline-capture)
**Severity**: Medium (blocks automated testing, not implementation)
**Priority**: Can proceed with manual validation

**Resolution Path**: User-driven manual capture or validation
