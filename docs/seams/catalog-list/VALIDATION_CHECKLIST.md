# Validation Checklist: catalog-list Frontend

**Seam**: catalog-list
**Date**: 2026-03-02
**Status**: Ready for Validation

---

## Pre-Validation Setup

### Step 1: Start Backend
```bash
cd C:\Users\pratikp6\codebase\eshopmigration\backend
poetry run uvicorn app.main:app --reload --port 8000
```

**Expected Output**:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Verify Backend**:
```bash
curl http://localhost:8000/api/catalog/items?page_size=2&page_index=0
```

**Expected Response**: JSON with 2 catalog items

---

### Step 2: Install Frontend Dependencies (if not already done)
```bash
cd C:\Users\pratikp6\codebase\eshopmigration\frontend
npm install
```

**Expected Output**: No errors, all packages installed

---

### Step 3: Start Frontend Dev Server
```bash
cd C:\Users\pratikp6\codebase\eshopmigration\frontend
npm run dev
```

**Expected Output**:
```
VITE v5.0.12  ready in XXX ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

---

## Quality Gate 1: Type Checking

### Command
```bash
cd frontend
npm run build
```

### Expected Result
- ✅ TypeScript compilation succeeds
- ✅ No type errors
- ✅ Build output created in `frontend/dist/`

### Common Issues
- ❌ Type errors → Fix TypeScript errors in components
- ❌ Missing dependencies → Run `npm install`

---

## Quality Gate 2: Linting

### Command
```bash
cd frontend
npm run lint
```

### Expected Result
- ✅ ESLint passes with 0 warnings/errors
- ✅ All files conform to style rules

### Common Issues
- ❌ Unused variables → Remove or prefix with `_`
- ❌ Missing dependencies in useEffect → Add to dependency array

---

## Quality Gate 3: Unit Tests

### Command
```bash
cd frontend
npm run test
```

### Expected Result
- ✅ All 15 tests pass
- ✅ Coverage: 100% for catalog-list components
- ✅ No test failures or timeouts

### Test Breakdown
| Test Category | Count | Status |
|---------------|-------|--------|
| Loading states | 1 | ✅ |
| Data rendering | 4 | ✅ |
| UI elements | 3 | ✅ |
| Pagination | 2 | ✅ |
| Empty/error states | 2 | ✅ |
| CSS classes | 2 | ✅ |
| Asset helpers | 1 | ✅ |

---

## Quality Gate 4: E2E Tests

### Command
```bash
cd frontend
npx playwright test tests/catalog-list.spec.ts
```

### Expected Result
- ✅ All 14 E2E tests pass
- ✅ No navigation errors
- ✅ All elements visible and clickable

### Test Breakdown
| Test Category | Count | Status |
|---------------|-------|--------|
| Page load | 1 | ✅ |
| Table rendering | 3 | ✅ |
| Navigation | 4 | ✅ |
| CSS validation | 1 | ✅ |
| Pagination | 2 | ✅ |
| Edge cases | 2 | ✅ |
| Visual regression | 1 | ✅ |

---

## Quality Gate 5: Visual Parity

### Manual Validation Steps

#### Step 1: Open Application
1. Navigate to `http://localhost:5173/`
2. Wait for page to load

#### Step 2: Compare Layout
Open legacy screenshot: `docs\seams\catalog-list\..\..\..\..\legacy-golden\screenshots\screen_000_depth0.png`

**Verify**:
- ✅ Create New button at top-left
- ✅ Product table below button
- ✅ 11 columns (Image + 9 data + Actions)
- ✅ Pagination controls at bottom (may be hidden with 10 items)

#### Step 3: Compare Styling

**Create New Button**:
- ✅ Green background (#83D01B)
- ✅ White text, uppercase
- ✅ Padding: 1rem 1.5rem
- ✅ Hover: darker green (#4A760f)

**Table**:
- ✅ Header row: uppercase text
- ✅ Image column: thumbnails max-width 120px
- ✅ Price column: $ prefix (from CSS :before)
- ✅ Action links: green hover (#75b918)

**Pagination** (if visible):
- ✅ Previous/Next buttons clickable
- ✅ Page info text centered
- ✅ Hidden buttons have opacity: 0

#### Step 4: Compare Colors

**Reference** (from legacy Site.css):
| Element | Color | Verified |
|---------|-------|----------|
| Primary button | #83D01B | ☐ |
| Primary button hover | #4A760f | ☐ |
| Secondary button | #E52638 | ☐ |
| Secondary button hover | #b20000 | ☐ |
| Link hover | #75b918 | ☐ |
| Body title background | #00A69C | ☐ |

#### Step 5: Compare Typography

**Reference**:
| Element | Font | Size | Weight | Transform | Verified |
|---------|------|------|--------|-----------|----------|
| Body title | Montserrat | 3rem | normal | none | ☐ |
| Table header | inherit | 1rem | normal | uppercase | ☐ |
| Table cell | inherit | 1rem | 300 | none | ☐ |
| Button | inherit | 1rem | 400 | uppercase | ☐ |
| Link item | inherit | 2rem | 600 | none | ☐ |

---

## Quality Gate 6: Functional Testing

### Test Scenario 1: View Catalog List
**Steps**:
1. Navigate to `http://localhost:5173/`
2. Wait for products to load

**Expected**:
- ✅ 10 products displayed (or fewer if DB has less)
- ✅ All columns populated
- ✅ Images load without 404 errors
- ✅ No console errors

### Test Scenario 2: Click Create New
**Steps**:
1. Click "Create New" button

**Expected**:
- ✅ Navigate to `/catalog/create`
- ✅ Create form displays

### Test Scenario 3: Click Edit
**Steps**:
1. Click "Edit" link on first product

**Expected**:
- ✅ Navigate to `/catalog/edit/1`
- ✅ Edit form displays with product data

### Test Scenario 4: Click Details
**Steps**:
1. Click "Details" link on first product

**Expected**:
- ✅ Navigate to `/catalog/details/1`
- ✅ Details view displays product data

### Test Scenario 5: Click Delete
**Steps**:
1. Click "Delete" link on first product

**Expected**:
- ✅ Navigate to `/catalog/delete/1`
- ✅ Delete confirmation displays

### Test Scenario 6: Image Fallback
**Steps**:
1. Edit database to set `picture_file_name` to NULL or invalid
2. Reload catalog list

**Expected**:
- ✅ Placeholder image (`dummy.png`) displays
- ✅ No broken image icon
- ✅ Console warning logged

### Test Scenario 7: Empty State
**Steps**:
1. Empty database (or mock empty response)
2. Reload catalog list

**Expected**:
- ✅ "No data was returned." message displays
- ✅ No table rows
- ✅ Create New button still visible

### Test Scenario 8: API Error
**Steps**:
1. Stop backend server
2. Reload catalog list

**Expected**:
- ✅ Error message displays
- ✅ Error details shown
- ✅ No page crash

### Test Scenario 9: Pagination (if >10 products)
**Steps**:
1. Add 15 products to database
2. Reload catalog list

**Expected**:
- ✅ "Showing 10 of 15 products - Page 1 - 2" displays
- ✅ Previous button hidden
- ✅ Next button visible
3. Click Next

**Expected**:
- ✅ Navigate to page 2
- ✅ 5 products display
- ✅ Previous button visible
- ✅ Next button hidden

---

## Quality Gate 7: Asset Verification

### Images
**Command**:
```bash
cd frontend/public/pics
ls -la
```

**Expected**:
- ✅ 14 PNG files present (1.png - 13.png + dummy.png)
- ✅ All files are valid PNG images
- ✅ No 404 errors when loading images in browser

**Verify in Browser**:
1. Open DevTools → Network tab
2. Filter: Images
3. Reload page
4. ✅ All images load with HTTP 200
5. ✅ No 404 errors

### CSS Classes
**Verify in Browser DevTools**:
1. Inspect Create New button
   - ✅ Classes: `btn esh-button esh-button-primary`
2. Inspect product image
   - ✅ Class: `esh-thumbnail`
3. Inspect price cell
   - ✅ Class: `esh-price`
4. Inspect action link
   - ✅ Class: `esh-table-link`
5. Inspect pagination button
   - ✅ Classes: `esh-pager-item esh-pager-item--navigable`

---

## Quality Gate 8: Performance

### Lighthouse Audit
**Steps**:
1. Open Chrome DevTools
2. Go to Lighthouse tab
3. Run audit (Performance, Accessibility, Best Practices)

**Expected Scores**:
- ✅ Performance: ≥ 90
- ✅ Accessibility: ≥ 90
- ✅ Best Practices: ≥ 90

### Network Performance
**Verify in DevTools → Network tab**:
- ✅ API call completes in < 500ms
- ✅ Images lazy-loaded (not all at once)
- ✅ Total page load < 2s

---

## Quality Gate 9: Responsive Design

### Viewport Testing
**Test Viewports**:
| Viewport | Width | Expected Behavior | Verified |
|----------|-------|------------------|----------|
| Mobile | 320px | Table scrolls horizontally | ☐ |
| Mobile | 375px | Table scrolls horizontally | ☐ |
| Tablet | 768px | Table fits, some wrapping | ☐ |
| Desktop | 1024px | Table fits comfortably | ☐ |
| Desktop | 1440px | Max-width applied (1440px) | ☐ |
| Desktop | 1920px | Max-width applied (1440px) | ☐ |

**Responsive Adjustments** (from CSS):
- ✅ Pagination text size reduced < 1280px (0.85rem)
- ✅ Pagination margins reduced < 1024px (2.5vw)
- ✅ Hero height increases < 1024px (20vw)

---

## Quality Gate 10: Browser Compatibility

### Browsers to Test
| Browser | Version | Status |
|---------|---------|--------|
| Chrome | Latest | ☐ |
| Firefox | Latest | ☐ |
| Edge | Latest | ☐ |
| Safari | Latest (if available) | ☐ |

**Verify in Each Browser**:
- ✅ Page loads
- ✅ Images display
- ✅ CSS classes applied correctly
- ✅ Navigation works
- ✅ No console errors

---

## Final Sign-Off

### Implementation Checklist
- ✅ All components created
- ✅ All hooks implemented
- ✅ All API client methods defined
- ✅ All routes registered
- ✅ All assets copied
- ✅ All CSS classes extracted
- ✅ Typed asset index created
- ✅ Unit tests written (15 tests)
- ✅ E2E tests written (14 tests)

### Quality Gate Checklist
- ☐ Type checking passes
- ☐ Linting passes
- ☐ Unit tests pass (15/15)
- ☐ E2E tests pass (14/14)
- ☐ Visual parity verified
- ☐ Functional testing complete
- ☐ Asset verification complete
- ☐ Performance acceptable
- ☐ Responsive design verified
- ☐ Browser compatibility confirmed

### Evidence Checklist
- ✅ Implementation summary document
- ✅ Test coverage report
- ✅ Screenshots of running application
- ☐ Lighthouse audit results
- ☐ Network performance data
- ☐ Visual comparison to legacy screenshot

---

## Sign-Off

**Implemented By**: Claude Opus 4.6 (Frontend Migration Agent)
**Date**: 2026-03-02

**Validated By**: _____________________
**Date**: _____________________

**Notes**:
_________________________________________
_________________________________________
_________________________________________

**Status**: ☐ APPROVED ☐ NEEDS REVISION

**Revision Notes** (if applicable):
_________________________________________
_________________________________________
_________________________________________
