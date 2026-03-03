#!/bin/bash
#
# Post-Implementation Hook
# Runs comprehensive quality gates after seam implementation
#

set -euo pipefail

SEAM_NAME="${1:-}"

if [ -z "$SEAM_NAME" ]; then
    echo "Error: No seam name provided"
    exit 1
fi

SEAM_DIR="docs/seams/$SEAM_NAME"

if [ ! -d "$SEAM_DIR" ]; then
    echo "Error: Seam directory not found: $SEAM_DIR"
    exit 1
fi

echo "🚀 Running post-implementation quality gates for seam: $SEAM_NAME"
echo "========================================================"

TOTAL_ISSUES=0

# 1. Backend Quality Gates
echo ""
echo "📦 Backend Quality Gates"
echo "------------------------"

if [ -d "backend/app/${SEAM_NAME}" ]; then
    echo "  → Running backend tests..."
    if ! pytest backend/tests/ -k "$SEAM_NAME" --cov=app/"$SEAM_NAME" --cov-report=term-missing --cov-fail-under=80 2>/dev/null; then
        echo "    ❌ Backend tests failed or coverage < 80%"
        TOTAL_ISSUES=$((TOTAL_ISSUES + 1))
    else
        echo "    ✅ Backend tests passed with coverage ≥ 80%"
    fi

    echo "  → Running backend security scan..."
    if ! bandit -r backend/app/"$SEAM_NAME" -ll -q 2>/dev/null; then
        echo "    ❌ Security issues found in backend"
        TOTAL_ISSUES=$((TOTAL_ISSUES + 1))
    else
        echo "    ✅ Backend security scan passed"
    fi

    echo "  → Checking type annotations..."
    if ! mypy backend/app/"$SEAM_NAME" --strict 2>/dev/null; then
        echo "    ❌ Type checking issues found"
        TOTAL_ISSUES=$((TOTAL_ISSUES + 1))
    else
        echo "    ✅ Type checking passed"
    fi
else
    echo "  ⚠️  No backend code found for this seam"
fi

# 2. Frontend Quality Gates
echo ""
echo "🎨 Frontend Quality Gates"
echo "-------------------------"

if [ -d "frontend/src/pages/${SEAM_NAME}" ] || [ -d "frontend/src/components/${SEAM_NAME}" ]; then
    echo "  → Running frontend tests..."
    if ! npm --prefix frontend run test -- --run --coverage 2>/dev/null; then
        echo "    ❌ Frontend tests failed or coverage < 75%"
        TOTAL_ISSUES=$((TOTAL_ISSUES + 1))
    else
        echo "    ✅ Frontend tests passed with coverage ≥ 75%"
    fi

    echo "  → Running accessibility audit..."
    if [ -f "frontend/src/pages/${SEAM_NAME}/${SEAM_NAME^}Page.test.tsx" ]; then
        if ! grep -q "toHaveNoViolations" "frontend/src/pages/${SEAM_NAME}/${SEAM_NAME^}Page.test.tsx"; then
            echo "    ⚠️  No accessibility tests found - add jest-axe tests"
            TOTAL_ISSUES=$((TOTAL_ISSUES + 1))
        else
            echo "    ✅ Accessibility tests present"
        fi
    fi

    echo "  → Running bundle size check..."
    BUNDLE_SIZE=$(du -sb frontend/dist 2>/dev/null | cut -f1 || echo "0")
    MAX_BUNDLE_SIZE=$((500 * 1024))  # 500KB

    if [ "$BUNDLE_SIZE" -gt "$MAX_BUNDLE_SIZE" ]; then
        echo "    ⚠️  Bundle size exceeds 500KB: $(($BUNDLE_SIZE / 1024))KB"
        TOTAL_ISSUES=$((TOTAL_ISSUES + 1))
    else
        echo "    ✅ Bundle size within limits: $(($BUNDLE_SIZE / 1024))KB"
    fi
else
    echo "  ⚠️  No frontend code found for this seam"
fi

# 3. Contract Validation
echo ""
echo "📋 Contract Validation"
echo "----------------------"

if [ -f "$SEAM_DIR/contracts/openapi.yaml" ]; then
    echo "  → Validating OpenAPI contract..."
    if ! python .claude/scripts/validate_contract_backend.py "$SEAM_NAME" 2>/dev/null; then
        echo "    ❌ Backend doesn't match contract"
        TOTAL_ISSUES=$((TOTAL_ISSUES + 1))
    else
        echo "    ✅ Backend matches contract"
    fi

    if ! python .claude/scripts/validate_contract_frontend.py "$SEAM_NAME" 2>/dev/null; then
        echo "    ❌ Frontend doesn't match contract"
        TOTAL_ISSUES=$((TOTAL_ISSUES + 1))
    else
        echo "    ✅ Frontend matches contract"
    fi
else
    echo "    ⚠️  No OpenAPI contract found"
    TOTAL_ISSUES=$((TOTAL_ISSUES + 1))
fi

# 4. Integration Tests
echo ""
echo "🔗 Integration Tests"
echo "--------------------"

if [ -f "backend/tests/integration/test_${SEAM_NAME}_integration.py" ]; then
    echo "  → Running integration tests..."
    if ! pytest backend/tests/integration/test_"${SEAM_NAME}"_integration.py -v 2>/dev/null; then
        echo "    ❌ Integration tests failed"
        TOTAL_ISSUES=$((TOTAL_ISSUES + 1))
    else
        echo "    ✅ Integration tests passed"
    fi
else
    echo "    ⚠️  No integration tests found"
    TOTAL_ISSUES=$((TOTAL_ISSUES + 1))
fi

# 5. E2E Tests
echo ""
echo "🌐 End-to-End Tests"
echo "-------------------"

if [ -f "frontend/tests/e2e/${SEAM_NAME}.spec.ts" ]; then
    echo "  → Running E2E tests..."
    if ! npx playwright test "frontend/tests/e2e/${SEAM_NAME}.spec.ts" 2>/dev/null; then
        echo "    ❌ E2E tests failed"
        TOTAL_ISSUES=$((TOTAL_ISSUES + 1))
    else
        echo "    ✅ E2E tests passed"
    fi
else
    echo "    ⚠️  No E2E tests found"
    TOTAL_ISSUES=$((TOTAL_ISSUES + 1))
fi

# 6. Documentation Check
echo ""
echo "📚 Documentation Check"
echo "----------------------"

REQUIRED_DOCS=("spec.md" "discovery.md" "contracts/openapi.yaml")

for doc in "${REQUIRED_DOCS[@]}"; do
    if [ ! -f "$SEAM_DIR/$doc" ]; then
        echo "    ❌ Missing required document: $doc"
        TOTAL_ISSUES=$((TOTAL_ISSUES + 1))
    else
        echo "    ✅ Found: $doc"
    fi
done

# 7. Security Review
echo ""
echo "🔒 Security Review"
echo "------------------"

echo "  → Running comprehensive security scan..."

# Backend security
if [ -d "backend/app/${SEAM_NAME}" ]; then
    bash .claude/scripts/security-analysis.sh "backend/app/${SEAM_NAME}" "backend" || TOTAL_ISSUES=$((TOTAL_ISSUES + 1))
fi

# Frontend security
if [ -d "frontend/src/pages/${SEAM_NAME}" ]; then
    bash .claude/scripts/security-analysis.sh "frontend/src/pages/${SEAM_NAME}" "frontend" || TOTAL_ISSUES=$((TOTAL_ISSUES + 1))
fi

# 8. Performance Check
echo ""
echo "⚡ Performance Check"
echo "--------------------"

echo "  → Running Lighthouse audit..."
if command -v lighthouse &> /dev/null; then
    if ! lighthouse http://localhost:5173/"$SEAM_NAME" --quiet --chrome-flags="--headless" --only-categories=performance 2>/dev/null; then
        echo "    ⚠️  Performance audit failed"
        TOTAL_ISSUES=$((TOTAL_ISSUES + 1))
    else
        echo "    ✅ Performance audit passed"
    fi
else
    echo "    ⚠️  Lighthouse not installed - skipping"
fi

# Summary
echo ""
echo "========================================================"
echo "📊 Quality Gate Summary"
echo "========================================================"

if [ $TOTAL_ISSUES -eq 0 ]; then
    echo "✅ ALL QUALITY GATES PASSED"
    echo ""
    echo "Seam '$SEAM_NAME' is ready for production!"
    exit 0
else
    echo "❌ $TOTAL_ISSUES ISSUE(S) FOUND"
    echo ""
    echo "Please fix the issues above before marking seam complete."
    echo ""
    echo "To trigger auto-fix, run:"
    echo "  bash .claude/scripts/auto-fix-seam.sh $SEAM_NAME"
    exit 1
fi
