#!/bin/bash
#
# Security Analysis Script
# Runs security scanning and vulnerability detection
#

set -euo pipefail

FILE_PATH="$1"
STACK="$2"

SECURITY_ISSUES=0

echo "🔒 Running security analysis..."

if [ "$STACK" = "backend" ]; then
    # Python security checks

    # 1. Bandit security linter
    echo "  → Running Bandit security scanner..."
    if ! bandit -r "$FILE_PATH" -f txt -q -ll 2>/dev/null; then
        echo "    ❌ Security issues found"
        SECURITY_ISSUES=1
        bandit -r "$FILE_PATH" -f txt -ll
    else
        echo "    ✅ Bandit scan passed"
    fi

    # 2. Check for hardcoded secrets
    echo "  → Checking for hardcoded secrets..."
    SECRET_PATTERNS=(
        "password\s*=\s*['\"][^'\"]+['\"]"
        "api[_-]?key\s*=\s*['\"][^'\"]+['\"]"
        "secret\s*=\s*['\"][^'\"]+['\"]"
        "token\s*=\s*['\"][^'\"]+['\"]"
        "db_url\s*=\s*['\"].*://.*:.*@"
    )

    for pattern in "${SECRET_PATTERNS[@]}"; do
        if grep -iE "$pattern" "$FILE_PATH" 2>/dev/null; then
            echo "    ❌ Potential hardcoded secret found: $pattern"
            SECURITY_ISSUES=1
        fi
    done

    # 3. Check for SQL injection vulnerabilities
    echo "  → Checking for SQL injection risks..."
    if grep -E "execute\(.*%|execute\(.*\.format\(|execute\(.*f['\"]" "$FILE_PATH" 2>/dev/null; then
        echo "    ⚠️  Potential SQL injection risk - use parameterized queries"
        SECURITY_ISSUES=1
    fi

    # 4. Check for unsafe imports
    echo "  → Checking for unsafe imports..."
    UNSAFE_IMPORTS=("pickle" "eval" "exec" "compile" "input" "__import__")
    for import in "${UNSAFE_IMPORTS[@]}"; do
        if grep -E "^import $import|from .* import .*$import" "$FILE_PATH" 2>/dev/null; then
            echo "    ⚠️  Unsafe import detected: $import"
            SECURITY_ISSUES=1
        fi
    done

elif [ "$STACK" = "frontend" ]; then
    # TypeScript/React security checks

    # 1. npm audit
    echo "  → Running npm audit..."
    if ! npm audit --audit-level=high --production 2>/dev/null; then
        echo "    ❌ npm audit found vulnerabilities"
        SECURITY_ISSUES=1
        npm audit --audit-level=high --production
    else
        echo "    ✅ npm audit passed"
    fi

    # 2. Check for XSS vulnerabilities
    echo "  → Checking for XSS vulnerabilities..."
    if grep -q "dangerouslySetInnerHTML" "$FILE_PATH" 2>/dev/null; then
        if ! grep -q "DOMPurify\|sanitize" "$FILE_PATH" 2>/dev/null; then
            echo "    ❌ dangerouslySetInnerHTML without sanitization"
            SECURITY_ISSUES=1
        fi
    fi

    # 3. Check for hardcoded secrets
    echo "  → Checking for hardcoded secrets..."
    if grep -iE "(api[_-]?key|password|secret|token)\s*[:=]\s*['\"][a-zA-Z0-9]{20,}" "$FILE_PATH" 2>/dev/null; then
        echo "    ❌ Potential hardcoded secret found"
        SECURITY_ISSUES=1
    fi

    # 4. Check for unsafe practices
    echo "  → Checking for unsafe practices..."
    if grep -q "eval(" "$FILE_PATH" 2>/dev/null; then
        echo "    ❌ eval() usage detected - potential code injection"
        SECURITY_ISSUES=1
    fi

    if grep -E "innerHTML\s*=" "$FILE_PATH" 2>/dev/null; then
        echo "    ⚠️  innerHTML usage detected - verify sanitization"
        SECURITY_ISSUES=1
    fi

    # 5. Check for localStorage with sensitive data
    echo "  → Checking localStorage usage..."
    if grep -iE "localStorage\.setItem.*('|\"|`)?(token|password|secret)" "$FILE_PATH" 2>/dev/null; then
        echo "    ⚠️  Storing sensitive data in localStorage - use httpOnly cookies"
        SECURITY_ISSUES=1
    fi

    # 6. Check for external links without security
    echo "  → Checking external links..."
    if grep -E "<a[^>]*href=['\"]http" "$FILE_PATH" 2>/dev/null; then
        if ! grep -q 'rel="noopener noreferrer"' "$FILE_PATH" 2>/dev/null; then
            echo "    ⚠️  External links without rel=\"noopener noreferrer\""
            SECURITY_ISSUES=1
        fi
    fi
fi

# OWASP Top 10 checklist
echo "  → OWASP Top 10 checks..."

# A01: Broken Access Control
if grep -iE "(admin|role|permission).*=.*true" "$FILE_PATH" 2>/dev/null; then
    echo "    ⚠️  Hardcoded authorization detected - use proper access control"
    SECURITY_ISSUES=1
fi

# A02: Cryptographic Failures
if grep -iE "(md5|sha1)\(" "$FILE_PATH" 2>/dev/null; then
    echo "    ⚠️  Weak hashing algorithm detected - use bcrypt or Argon2"
    SECURITY_ISSUES=1
fi

if [ $SECURITY_ISSUES -eq 1 ]; then
    touch /tmp/claude-code-fixes-needed.flag
    echo "❌ Security issues found - review required"
    exit 1
else
    echo "✅ All security checks passed"
    exit 0
fi
