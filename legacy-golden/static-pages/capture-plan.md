# Golden Baseline Capture Plan: static-pages

**Seam**: static-pages
**Date**: 2026-03-02
**Status**: SYNTHETIC (browser automation blocked)

---

## Workflows to Capture

### 1. About Page
**URL**: http://localhost:50586/About
**Purpose**: Static informational page about the application
**Content**:
- Title: "About."
- Heading: "Your application description page."
- Paragraph: "Use this area to provide additional information."

**Expected Captures**:
- ❌ Screenshot of About page
- ✅ Static content extraction (from About.aspx)
- ❌ No database operations
- ❌ No HTTP requests/responses (static content only)

---

### 2. Contact Page
**URL**: http://localhost:50586/Contact
**Purpose**: Static contact information display
**Content**:
- Title: "Contact."
- Heading: "Your contact page."
- Address block:
  - One Microsoft Way
  - Redmond, WA 98052-6399
  - P: 425.555.0100
- Email contacts:
  - Support: Support@example.com
  - Marketing: Marketing@example.com

**Expected Captures**:
- ❌ Screenshot of Contact page
- ✅ Static content extraction (from Contact.aspx)
- ❌ No database operations
- ❌ No HTTP requests/responses (static content only)

---

## What Was NOT Captured (Browser Automation Blocked)

1. **Screenshots**: Could not capture visual layout of About/Contact pages
2. **Runtime styling**: Could not capture actual rendered CSS/layout
3. **Navigation flow**: Could not capture click-through from navbar to pages

---

## What WAS Captured (Synthetic Baselines)

1. **Content Extraction**: Exact HTML content from About.aspx and Contact.aspx source files
2. **Layout Structure**: Master page integration (Site.Master)
3. **Static Text**: All text content preserved exactly

---

## Capture Method

**Source**: Direct read of .aspx markup files
**Files Read**:
- `src/eShopLegacyWebForms/About.aspx`
- `src/eShopLegacyWebForms/Contact.aspx`

---

## Limitations

**No Dynamic Behavior**: These pages have zero dynamic behavior, so synthetic baselines are sufficient.

**No Database Operations**: No data fetching, no API calls, no state management.

**Manual Validation**: User should visually compare:
- Legacy: http://localhost:50586/About
- New: http://localhost:5173/about

**Manual Validation**: User should visually compare:
- Legacy: http://localhost:50586/Contact
- New: http://localhost:5173/contact

---

## Validation Checklist

### About Page
- [ ] Title displays: "About."
- [ ] Heading displays: "Your application description page."
- [ ] Paragraph text matches exactly
- [ ] Page uses site layout (header, nav, footer)
- [ ] Navigation link "About" in navbar works

### Contact Page
- [ ] Title displays: "Contact."
- [ ] Heading displays: "Your contact page."
- [ ] Address block displays correctly
- [ ] Email links are clickable (mailto:)
- [ ] Page uses site layout (header, nav, footer)
- [ ] Navigation link "Contact" in navbar works

---

## Notes

- **Complexity**: VERY LOW (pure static content)
- **Risk**: NONE (no business logic, no data operations)
- **Testing**: Visual comparison only (no functional testing needed)
- **Priority**: LOW (seam priority 4)

---

**Capture Method**: SYNTHETIC (source file extraction)
**Capture Date**: 2026-03-02
**Capture Status**: COMPLETE
