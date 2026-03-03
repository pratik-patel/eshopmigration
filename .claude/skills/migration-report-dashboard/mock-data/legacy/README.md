# Legacy System Mock Data

**Purpose:** Provide baseline metrics for legacy system comparison in unified dashboard

**Created:** 2026-03-03

---

## Files Overview

| File | Purpose | Data Type |
|------|---------|-----------|
| `legacy-metrics.xml` | Performance, resource utilization, availability metrics | Runtime Metrics |
| `legacy-code-stats.xml` | Codebase statistics, complexity, technical debt | Static Analysis |
| `legacy-test-results.xml` | Test coverage, pass rates, test suites | Quality Metrics |
| `legacy-dependencies.xml` | Package versions, CVEs, vulnerabilities | Security |
| `legacy-architecture.xml` | Architecture patterns, layers, components | Design |

---

## Why Mock Data?

The legacy system (eShopModernizedWebForms) metrics are mocked because:

1. **Legacy system not instrumented** - No telemetry collection was in place
2. **Historical data unavailable** - Metrics weren't tracked during legacy operation
3. **Migration focus** - Dashboard focuses on forward progress, not legacy deep-dive
4. **Reasonable estimates** - Mock data based on typical ASP.NET WebForms applications

---

## Data Sources

### Real Data (Modern System)
- Test results → `docs/tracking/seams/{seam}/test-results-*.json`
- Coverage → `docs/tracking/seams/{seam}/coverage-*.json`
- Dependencies → `docs/tracking/seams/{seam}/dependency-scan-*.json`
- Lighthouse → `docs/tracking/seams/{seam}/lighthouse-results.json`
- Code quality → `docs/tracking/seams/{seam}/code-quality.json`

### Mock Data (Legacy System)
- Performance → `mock-data/legacy/legacy-metrics.xml`
- Code stats → `mock-data/legacy/legacy-code-stats.xml`
- Tests → `mock-data/legacy/legacy-test-results.xml`
- Dependencies → `mock-data/legacy/legacy-dependencies.xml`
- Architecture → `mock-data/legacy/legacy-architecture.xml`

---

## Usage in Dashboard

### Comparison Pages

```python
# Example: Compare response times
from unified_app.lib.legacy_loader import LegacyLoader
from unified_app.lib.modern_loader import ModernLoader

legacy_loader = LegacyLoader()
modern_loader = ModernLoader()

# Legacy (from XML)
legacy_p95 = legacy_loader.get_response_time(path="/", percentile="p95")
# Returns: 1350ms (from legacy-metrics.xml)

# Modern (from JSON)
modern_p95 = modern_loader.get_lighthouse_metric(seam="catalog-management", metric="p95")
# Returns: <actual Lighthouse data> (from lighthouse-results.json)

# Display comparison
improvement = ((legacy_p95 - modern_p95) / legacy_p95) * 100
print(f"Response time improved by {improvement:.1f}%")
```

---

## Mock Data Characteristics

### Realistic Estimates
Mock data reflects typical ASP.NET WebForms application characteristics:

- **Response Times:** Slower than modern (p95: 1350ms vs ~200ms target)
- **Test Coverage:** Low (42% vs 80% target)
- **Vulnerabilities:** Multiple CVEs (31 total vs 0 target)
- **Code Complexity:** Higher complexity (avg 12.5 vs <10 target)
- **Tech Debt:** Significant (420 hours vs 0 target)

### Based On:
- Industry benchmarks for .NET 4.8 WebForms apps
- Common patterns from similar migrations
- Typical technical debt in 8-year-old applications
- Known ASP.NET WebForms performance characteristics

---

## Validation

Dashboard shows **"ESTIMATED"** labels for all legacy metrics to indicate mock data.

**UI Example:**
```
Legacy Response Time (ESTIMATED): 1350ms p95
Modern Response Time (MEASURED): 245ms p95
Improvement: 81.9% faster ✅
```

---

## Replacing Mock Data with Real Data

If real legacy metrics become available:

1. Export legacy system telemetry to XML format (matching schema)
2. Replace files in `mock-data/legacy/`
3. Update `README.md` to indicate real data
4. Remove "ESTIMATED" labels in dashboard UI

**No code changes required** - XML parser will load real data automatically.

---

## XML Schema

### legacy-metrics.xml
```xml
<metrics timestamp="ISO-8601" application="string" version="string">
  <performance>
    <response_times unit="milliseconds">
      <endpoint path="string" method="string" p50="float" p95="float" p99="float" max="float"/>
    </response_times>
    <throughput unit="requests_per_second">
      <total value="float"/>
    </throughput>
    <error_rates unit="percent">
      <total value="float"/>
    </error_rates>
  </performance>
  <resources>
    <memory unit="megabytes">
      <average value="int"/>
    </memory>
    <cpu unit="percent">
      <average value="int"/>
    </cpu>
  </resources>
</metrics>
```

### legacy-code-stats.xml
```xml
<codebase timestamp="ISO-8601">
  <loc>
    <total value="int"/>
    <by_language>
      <language name="string" lines="int" percent="float"/>
    </by_language>
  </loc>
  <complexity>
    <cyclomatic_complexity>
      <average value="float"/>
    </cyclomatic_complexity>
  </complexity>
  <technical_debt>
    <total_debt unit="hours" value="int"/>
  </technical_debt>
</codebase>
```

### legacy-test-results.xml
```xml
<test_results timestamp="ISO-8601">
  <summary>
    <total_tests count="int"/>
    <passed count="int"/>
    <failed count="int"/>
    <pass_rate unit="percent" value="float"/>
  </summary>
  <coverage>
    <line_coverage unit="percent" value="float"/>
  </coverage>
</test_results>
```

### legacy-dependencies.xml
```xml
<dependencies timestamp="ISO-8601">
  <vulnerabilities>
    <critical count="int"/>
    <high count="int"/>
    <medium count="int"/>
    <low count="int"/>
  </vulnerabilities>
  <nuget_packages>
    <package name="string" current_version="string" latest_version="string">
      <vulnerabilities>
        <vulnerability severity="string" cve="string">
          <cvss_score>float</cvss_score>
        </vulnerability>
      </vulnerabilities>
    </package>
  </nuget_packages>
</dependencies>
```

### legacy-architecture.xml
```xml
<architecture timestamp="ISO-8601">
  <overview>
    <pattern name="string"/>
    <framework name="string" version="string"/>
  </overview>
  <layers>
    <layer name="string" type="string">
      <components>
        <component name="string" type="string">
          <responsibility>string</responsibility>
        </component>
      </components>
    </layer>
  </layers>
</architecture>
```

---

## License

Mock data is for internal migration dashboard use only.
Do not distribute outside organization.

---

**Status:** ✅ All 5 XML files complete and ready for dashboard use
