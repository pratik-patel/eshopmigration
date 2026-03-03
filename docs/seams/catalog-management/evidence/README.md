# Evidence Pack: Catalog Management Seam

This directory will contain evidence artifacts for verifying parity between legacy and modern implementations.

---

## Evidence Types

### 1. Golden Output Captures
Baseline outputs from legacy system for comparison testing.

**Files** (to be generated):
- `catalog-list-response.json` - Sample product list response
- `catalog-details-response.json` - Sample product details response
- `catalog-types-response.json` - All catalog types
- `catalog-brands-response.json` - All catalog brands

### 2. API Contract Tests
OpenAPI specification and contract validation tests.

**Files** (to be generated):
- `openapi-spec.yaml` - Generated OpenAPI 3.0 specification
- `contract-tests.py` - Automated contract validation tests

### 3. Functional Test Results
End-to-end test results comparing legacy vs modern.

**Files** (to be generated):
- `e2e-test-results.html` - Playwright test report
- `parity-test-results.json` - Side-by-side comparison results

### 4. Performance Benchmarks
Response time and load testing comparisons.

**Files** (to be generated):
- `performance-baseline.json` - Legacy performance metrics
- `performance-modern.json` - Modern API performance metrics
- `load-test-results.html` - k6 load test report

### 5. UI Screenshots
Visual regression testing evidence.

**Files** (to be generated):
- `screenshots/legacy/` - Screenshots from legacy UI
- `screenshots/modern/` - Screenshots from modern UI
- `visual-diff-report.html` - Pixel-perfect comparison report

---

## Verification Checklist

### Phase 1: Backend API Parity

- [ ] **List Products**
  - [ ] Response structure matches legacy
  - [ ] Pagination logic identical
  - [ ] Product fields populated correctly
  - [ ] Brand/type relationships loaded

- [ ] **Get Product Details**
  - [ ] Single product retrieval works
  - [ ] All fields present
  - [ ] Image URL format correct

- [ ] **Create Product**
  - [ ] Product creation succeeds
  - [ ] Image upload and association works
  - [ ] Validation errors match legacy

- [ ] **Update Product**
  - [ ] Product update succeeds
  - [ ] Image replacement works
  - [ ] Validation errors match legacy

- [ ] **Delete Product**
  - [ ] Product deletion succeeds
  - [ ] FK constraints enforced
  - [ ] Image cleanup works (NEW - not in legacy)

- [ ] **Upload Image**
  - [ ] Image upload to temp storage works
  - [ ] Authentication enforced (NEW - not in legacy)

### Phase 2: Frontend Parity

- [ ] **Product List Page**
  - [ ] Layout matches legacy
  - [ ] Pagination controls work
  - [ ] Product cards display correctly
  - [ ] Navigation to details/edit/delete works

- [ ] **Product Details Page**
  - [ ] Layout matches legacy
  - [ ] All fields display correctly
  - [ ] Image displays correctly
  - [ ] Back navigation works

- [ ] **Create Product Form**
  - [ ] Form layout matches legacy
  - [ ] All fields present
  - [ ] Validation works
  - [ ] Image upload works
  - [ ] Submit succeeds

- [ ] **Edit Product Form**
  - [ ] Form pre-populated correctly
  - [ ] All fields editable
  - [ ] Validation works
  - [ ] Image replacement works
  - [ ] Submit succeeds

- [ ] **Delete Confirmation**
  - [ ] Confirmation dialog displays
  - [ ] Product info shown
  - [ ] Delete succeeds
  - [ ] Cancel works

### Phase 3: Non-Functional Parity

- [ ] **Performance**
  - [ ] List response time ≤ legacy
  - [ ] Details response time ≤ legacy
  - [ ] Create operation time ≤ legacy
  - [ ] Update operation time ≤ legacy
  - [ ] Delete operation time ≤ legacy

- [ ] **Security**
  - [ ] JWT authentication works
  - [ ] Unauthorized access blocked
  - [ ] Image upload requires auth (NEW)
  - [ ] CORS configured correctly

- [ ] **Accessibility**
  - [ ] Keyboard navigation works
  - [ ] Screen reader compatible
  - [ ] WCAG 2.1 Level AA compliant
  - [ ] Color contrast sufficient

- [ ] **Browser Compatibility**
  - [ ] Chrome/Edge (latest)
  - [ ] Firefox (latest)
  - [ ] Safari (latest)
  - [ ] Mobile browsers

---

## Data Migration Validation

### Database Integrity

- [ ] **Record Counts**
  - [ ] Catalog: legacy count = modern count
  - [ ] CatalogType: legacy count = modern count
  - [ ] CatalogBrand: legacy count = modern count

- [ ] **Data Accuracy**
  - [ ] Sample spot checks (10 random products)
  - [ ] Price values match
  - [ ] Stock values match
  - [ ] Names and descriptions match

- [ ] **Relationships**
  - [ ] All FK references valid
  - [ ] No orphaned records
  - [ ] Cascade behavior correct

### Image Migration

- [ ] **Image Files**
  - [ ] All images copied to new storage
  - [ ] File paths/URLs correct
  - [ ] Images accessible via HTTP
  - [ ] No broken image links

---

## Test Data

### Reference Data

**CatalogType** (example):
```json
[
  {"id": 1, "type": "Mug"},
  {"id": 2, "type": "T-Shirt"},
  {"id": 3, "type": "Sheet"},
  {"id": 4, "type": "USB Memory Stick"}
]
```

**CatalogBrand** (example):
```json
[
  {"id": 1, "brand": ".NET"},
  {"id": 2, "brand": "Other"}
]
```

### Sample Product

```json
{
  "id": 1,
  "name": ".NET Bot Blue Sweatshirt (M)",
  "description": "Lorem ipsum dolor sit amet...",
  "price": 19.50,
  "picture_filename": "1.png",
  "picture_uri": "http://localhost:5200/pics/1.png",
  "catalog_type_id": 2,
  "catalog_brand_id": 1,
  "available_stock": 100,
  "restock_threshold": 0,
  "max_stock_threshold": 200,
  "on_reorder": false
}
```

---

## How to Generate Evidence

### 1. Capture Legacy Outputs

```bash
# From legacy application (running on http://localhost:50586)
curl http://localhost:50586/ > evidence/legacy-list.html
curl http://localhost:50586/api/catalog > evidence/catalog-list-legacy.json
```

### 2. Generate OpenAPI Spec

```bash
# From modern API (after implementation)
curl http://localhost:8000/openapi.json > evidence/openapi-spec.json
```

### 3. Run Contract Tests

```bash
cd backend
pytest tests/contract/ --html=evidence/contract-tests.html
```

### 4. Run E2E Tests

```bash
cd frontend
npm run test:e2e -- --reporter=html --output=evidence/e2e-test-results.html
```

### 5. Performance Testing

```bash
# Load test modern API
k6 run load-test.js --out html=evidence/load-test-results.html
```

### 6. Visual Regression

```bash
# Capture screenshots and compare
npm run test:visual -- --output=evidence/visual-diff-report.html
```

---

## Acceptance Criteria

Evidence pack is **complete** when:

✅ All functional tests pass
✅ All non-functional tests pass
✅ Data migration validated
✅ Performance meets or exceeds legacy
✅ Visual parity confirmed
✅ Security tests pass
✅ Accessibility tests pass

---

## Notes

- This directory is intentionally empty at discovery phase
- Evidence files will be generated during migration implementation
- All evidence should be versioned and reviewed before production deployment
