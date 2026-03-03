# Baseline Index: static-pages

**Captured**: 2026-03-02T00:00:00Z
**Application Type**: Web (ASP.NET WebForms 4.7.2)
**Framework**: ASP.NET WebForms
**Capture Tools**: SYNTHETIC (browser automation not available)
**Environment**: N/A (baselines generated from source files)
**Status**: ⚠️ **SYNTHETIC BASELINES** - Static content extraction only

---

## ⚠️ SYNTHETIC BASELINE NOTICE

**These baselines were NOT captured from the running legacy application.**

**Reason**: Browser automation tools (Playwright/Selenium) not available in Claude Code environment.

**Source**: Generated from:
- `src/eShopLegacyWebForms/About.aspx` (markup extraction)
- `src/eShopLegacyWebForms/Contact.aspx` (markup extraction)

**Validation Approach**: Manual user validation required (visual comparison)

---

## Screenshots

**Status**: NOT CAPTURED

| File | Page | Notes |
|------|------|-------|
| N/A | About | ⚠️ SYNTHETIC BASELINE - No real screenshots captured |
| N/A | Contact | ⚠️ SYNTHETIC BASELINE - No real screenshots captured |

**Alternative**: Static content preserved in JSON exports

---

## Exports

### Page Content

| File | Source | Notes |
|------|--------|-------|
| `exports/synthetic_about_content.json` | About.aspx | Complete static content and markup |
| `exports/synthetic_contact_content.json` | Contact.aspx | Complete static content and markup |

**Data Accuracy**: ✅ Exact match to source .aspx markup

---

## Database Snapshots

**Status**: N/A (no database operations)

These pages have zero database access - they are pure static content.

---

## API/HTTP Captures

**Status**: N/A (no API calls)

| Endpoint | File | Status Code | Notes |
|----------|------|-------------|-------|
| GET /About | N/A | N/A | Static page, no API |
| GET /Contact | N/A | N/A | Static page, no API |

---

## User Journeys

**File**: N/A (workflows documented in capture-plan.md)

**Workflows**:
1. Navigate to About page → View static content → Return to home
2. Navigate to Contact page → View static content → Return to home

**Complexity**: VERY LOW (zero dynamic behavior)

---

## Coverage

**Spec Workflows Captured**: 2/2 (SYNTHETIC fallback used)

### Workflows
1. ✅ About page - SYNTHETIC content extraction
2. ✅ Contact page - SYNTHETIC content extraction

**Edge Cases Captured**: 0 (no edge cases - static content only)

**Synthetic Baselines**: YES (all baselines are synthetic)

---

## Parity Test Strategy

### What CAN Be Validated

✅ **Content Accuracy**:
- About page title, heading, and body text match exactly
- Contact page title, heading, address, and email links match exactly

✅ **Layout Integration**:
- Pages use site layout (header, nav, footer)
- Navigation links work correctly

### What CANNOT Be Validated (Requires Real Baselines)

❌ **Visual Styling**:
- Font sizes, colors, spacing
- Responsive layout behavior
- CSS styling details

❌ **Interactive Behavior**:
- Hover states
- Link click behavior (beyond navigation)
- Accessibility features

---

## Manual Validation Required

**User must verify visually by comparing**:
- Legacy About: http://localhost:50586/About
- New About: http://localhost:5173/about
- Legacy Contact: http://localhost:50586/Contact
- New Contact: http://localhost:5173/contact

**Checklist**: See capture-plan.md → "Validation Checklist"

---

## Validation Test Cases

### About Page
- [ ] Page loads at /about route
- [ ] Title displays: "About."
- [ ] Heading displays: "Your application description page."
- [ ] Body text displays: "Use this area to provide additional information."
- [ ] Site layout (header, nav, footer) present
- [ ] "About" link in navbar is highlighted/active

### Contact Page
- [ ] Page loads at /contact route
- [ ] Title displays: "Contact."
- [ ] Heading displays: "Your contact page."
- [ ] Address displays: One Microsoft Way, Redmond, WA 98052-6399
- [ ] Phone displays: P: 425.555.0100
- [ ] Support email link: Support@example.com (clickable mailto:)
- [ ] Marketing email link: Marketing@example.com (clickable mailto:)
- [ ] Site layout (header, nav, footer) present
- [ ] "Contact" link in navbar is highlighted/active

---

## Limitations

**Known Gaps Due to Synthetic Baselines**:
1. Cannot auto-generate screenshot comparison tests
2. Cannot verify exact visual styling
3. Cannot capture hover/focus states
4. Visual parity requires manual user sign-off

**Mitigation**:
- Static content preserved exactly in JSON exports
- Manual visual validation by user (5 minutes)
- No functional testing needed (zero dynamic behavior)

---

## Future Improvements

**If real capture becomes possible**:
1. Install Playwright: `npm install -D @playwright/test`
2. Capture screenshots of About and Contact pages
3. Replace synthetic baselines with real screenshots
4. Enable visual regression testing

**Estimated Effort**: 30 minutes setup + 10 minutes capture

---

## Validation Status

- ✅ Synthetic content generated (About, Contact)
- ✅ Documentation complete
- ⏳ **Awaiting user manual validation**
- ⏳ Implementation status: TBD

---

## Readiness Assessment

**Ready for Implementation**: ✅ YES

**Confidence**: HIGH
- Zero complexity (static content only)
- No database operations
- No API calls
- No business logic
- Exact content preserved in exports

**Blockers**: NONE

---

**Next Step**: Proceed to implementation (STEPS 10-11) for this seam, OR complete discovery/contract/data-strategy steps for remaining seams first.

**Note**: For static-pages seam, STEPS 6-9 can be SKIPPED (no discovery/contracts/data-strategy needed for pure static content).
