---
name: migration-report-dashboard
description: Enterprise-grade migration comparison dashboard with comprehensive analysis across frontend, backend, database, quality, and non-functional aspects. Generates interactive Streamlit reports.
disable-model-invocation: false
context: fork
agent: general-purpose
---

# Migration Report Dashboard

Comprehensive migration comparison and analysis tool that provides:
- Multi-dimensional comparison (FE, BE, DB, Quality, NFR)
- Interactive Streamlit dashboard
- Automated metrics collection
- Executive summary reports
- Gap analysis and recommendations

**Arguments:** `[collect|dashboard|report] [--legacy <url>] [--modern <url>] [--seam <name>]`

---

## Overview

This skill generates a comprehensive migration comparison dashboard that evaluates:

### 📊 Comparison Dimensions

1. **Frontend (FE)**
   - Feature parity (screen-by-screen)
   - Performance (Lighthouse: Performance, Accessibility, Best Practices, SEO)
   - Bundle size and load metrics
   - Browser compatibility
   - Accessibility (WCAG compliance)

2. **Backend (BE)**
   - API parity (endpoint comparison)
   - Response time analysis
   - Error rate comparison
   - Business logic coverage
   - API contract compliance

3. **Database (DB)**
   - Schema comparison
   - Query performance
   - Data integrity validation
   - Migration completeness
   - Storage optimization

4. **External Systems**
   - Integration points mapping
   - Third-party dependencies
   - API compatibility
   - Network calls analysis

5. **Quality Metrics**
   - SonarQube analysis (complexity, duplication, vulnerabilities)
   - Unit test coverage
   - Code smells
   - Technical debt
   - Security vulnerabilities

6. **Non-Functional Requirements (NFR)**
   - Performance benchmarks
   - Scalability metrics
   - Security posture
   - Observability (logs, metrics, traces)
   - Reliability (uptime, error rates)

7. **Migration Readiness**
   - Overall migration score (0-100)
   - Gap analysis
   - Risk assessment
   - Recommendations

---

## Architecture

```
Collectors → Analyzers → Dashboard
    ↓           ↓           ↓
  JSON      Scoring    Streamlit UI
```

**Data Flow:**
1. Collectors gather metrics from both legacy and modern apps
2. Analyzers compute comparisons, scores, and gaps
3. Dashboard displays interactive visualizations
4. Reports generate executive summaries

---

## Usage Modes

### Mode 1: Collect Metrics

Gather all metrics from legacy and modern applications:

```bash
/migration-report-dashboard collect --legacy http://localhost:8080 --modern http://localhost:5173 --seam channels
```

**Collects:**
- Frontend Lighthouse scores
- Backend API endpoints and performance
- Database schema and query stats
- SonarQube quality metrics
- Test coverage reports
- Accessibility scores

**Output:** `data/{legacy,modern}/metrics.json`

### Mode 2: Launch Dashboard

Start interactive Streamlit dashboard:

```bash
/migration-report-dashboard dashboard
```

**Features:**
- Multi-page navigation
- Real-time filtering
- Interactive charts
- Drill-down capabilities
- Export to PDF/Excel

**Accessible at:** `http://localhost:8501`

### Mode 3: Generate Report

Create executive summary PDF:

```bash
/migration-report-dashboard report --output reports/migration-summary.pdf
```

**Includes:**
- Executive summary
- Score breakdown
- Gap analysis
- Recommendations
- Action items

---

## Dashboard Pages

### 1. 🏠 Home - Overview Dashboard
- Migration readiness score (0-100)
- Dimension scores (radar chart)
- Critical gaps summary
- Recent activity timeline

### 2. 🎨 Frontend Comparison
- Feature parity matrix (screen-by-screen)
- Lighthouse scores comparison
- Accessibility audit
- Bundle size analysis
- Performance waterfall
- Browser compatibility matrix

### 3. ⚙️ Backend Comparison
- API endpoint parity table
- Response time comparison (box plots)
- Error rate analysis
- Business logic coverage
- API contract validation
- Endpoint-by-endpoint drill-down

### 4. 💾 Database Comparison
- Schema diff viewer
- Query performance comparison
- Data integrity checks
- Migration status
- Index optimization suggestions

### 5. 🔌 Integration Points
- External system mapping
- Third-party dependency comparison
- API compatibility matrix
- Network call analysis
- Integration test results

### 6. ✅ Quality Metrics
- SonarQube dashboard
  - Code complexity
  - Duplications
  - Vulnerabilities
  - Code smells
- Test coverage comparison
- Technical debt estimation
- Security scan results

### 7. ⚡ Non-Functional Requirements
- Performance benchmarks
- Load test results
- Scalability metrics
- Security posture
- Observability comparison
- Reliability metrics (SLA, uptime)

### 8. 📊 Executive Summary
- Migration readiness assessment
- Risk analysis
- Cost-benefit analysis
- Recommendations
- Action plan with priorities

---

## Scoring Methodology

### Overall Migration Score (0-100)

Weighted average across dimensions:

| Dimension | Weight | Components |
|-----------|--------|------------|
| **Frontend** | 25% | Feature parity (60%), Performance (20%), Accessibility (20%) |
| **Backend** | 25% | API parity (50%), Performance (30%), Error handling (20%) |
| **Database** | 10% | Schema parity (40%), Performance (40%), Integrity (20%) |
| **Quality** | 20% | SonarQube (50%), Coverage (30%), Security (20%) |
| **NFR** | 15% | Performance (40%), Security (30%), Observability (30%) |
| **Integration** | 5% | Integration parity (100%) |

### Score Interpretation

- **90-100**: ✅ **Production Ready** — All critical aspects migrated, minor polish needed
- **75-89**: 🟢 **Near Ready** — Few gaps, low risk to deploy
- **60-74**: 🟡 **In Progress** — Significant work remaining, medium risk
- **40-59**: 🟠 **Early Stage** — Major gaps, high risk
- **0-39**: 🔴 **Not Ready** — Critical gaps, not viable for production

---

## Metrics Collection

### Frontend Collectors

**Lighthouse Collector** (`collectors/lighthouse_collector.py`)
- Runs Lighthouse audits on both apps
- Captures: Performance, Accessibility, Best Practices, SEO
- Generates detailed reports

**Feature Parity Collector** (`collectors/frontend_collector.py`)
- Uses browser-agent skill to discover features
- Compares screen-by-screen
- Tracks missing features

**Bundle Analysis**
- Webpack bundle analyzer
- Package size comparison
- Dependency audit

### Backend Collectors

**API Collector** (`collectors/api_collector.py`)
- Discovers all API endpoints (legacy + modern)
- Tests each endpoint for parity
- Measures response times
- Compares error rates

**OpenAPI Comparison**
- Parses OpenAPI/Swagger specs
- Validates contract compliance
- Identifies breaking changes

### Database Collectors

**Schema Collector** (`collectors/database_collector.py`)
- Exports schema from both databases
- Compares tables, columns, indexes
- Identifies missing migrations
- Checks data types consistency

**Query Performance**
- Captures slow query logs
- Compares execution plans
- Identifies optimization opportunities

### Quality Collectors

**SonarQube Collector** (`collectors/sonar_collector.py`)
- Fetches SonarQube metrics via API
- Compares: complexity, duplication, vulnerabilities
- Tracks technical debt

**Coverage Collector** (`collectors/coverage_collector.py`)
- Parses coverage reports (lcov, cobertura, JaCoCo)
- Compares line/branch coverage
- Identifies untested code

**Security Scanner**
- npm audit / pip-audit results
- OWASP ZAP scan results
- Dependency vulnerability comparison

### NFR Collectors

**Performance Collector**
- Load test results (JMeter, k6)
- Response time percentiles
- Throughput comparison

**Observability Collector**
- Logs analysis (volume, error rate)
- Metrics comparison (Prometheus/Grafana)
- Trace analysis (Jaeger/Zipkin)

---

## Configuration

`config.yaml`:

```yaml
# Migration Report Dashboard Configuration

legacy:
  name: "Legacy .NET Application"
  frontend_url: "http://localhost:8080"
  backend_url: "http://localhost:8080/api"
  database_url: "Server=localhost;Database=LegacyDB"
  sonarqube_project: "legacy-app"

modern:
  name: "Modern Python + React Application"
  frontend_url: "http://localhost:5173"
  backend_url: "http://localhost:8000/api"
  database_url: "postgresql://localhost/modern_db"
  sonarqube_project: "modern-app"

collection:
  lighthouse:
    enabled: true
    runs: 3  # Average of 3 runs
    throttling: "4g"
  api:
    timeout: 30
    retries: 2
  database:
    sample_queries: true
    slow_query_threshold_ms: 100

scoring:
  weights:
    frontend: 0.25
    backend: 0.25
    database: 0.10
    quality: 0.20
    nfr: 0.15
    integration: 0.05

  thresholds:
    lighthouse_performance: 90
    lighthouse_accessibility: 95
    api_response_time_ms: 200
    test_coverage: 80
    sonar_reliability: "A"
    sonar_security: "A"

dashboard:
  port: 8501
  theme: "light"
  auto_refresh: false
  cache_ttl: 3600

export:
  formats: ["pdf", "html", "json", "excel"]
  include_screenshots: true
```

---

## Installation

```bash
cd .claude/skills/migration-report-dashboard

# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies (for Lighthouse)
npm install

# Verify installation
./scripts/verify-installation.sh
```

---

## Quick Start

### Step 1: Collect Metrics

```bash
# Configure URLs in config.yaml first
vim config.yaml

# Run collection
./scripts/collect-all-metrics.sh
```

### Step 2: Launch Dashboard

```bash
# Start Streamlit app
streamlit run app/main.py

# Open browser
# http://localhost:8501
```

### Step 3: Explore Reports

- Navigate through pages
- Filter by seam/feature
- Drill down into details
- Export reports

---

## Integration with Migration Pipeline

### Phase 0: Baseline

```bash
# Collect legacy baseline
/migration-report-dashboard collect --legacy http://localhost:8080 --mode baseline
```

### Phase 5: Verification

```bash
# Collect modern metrics
/migration-report-dashboard collect --modern http://localhost:5173

# Launch comparison dashboard
/migration-report-dashboard dashboard

# Generate executive report
/migration-report-dashboard report --output reports/final-assessment.pdf
```

---

## API Endpoints (Dashboard Backend)

The Streamlit app exposes REST API for programmatic access:

```bash
GET  /api/metrics/summary
GET  /api/metrics/frontend
GET  /api/metrics/backend
GET  /api/metrics/database
GET  /api/metrics/quality
GET  /api/score
POST /api/export/pdf
```

---

## Advanced Features

### 1. Trend Analysis

Track migration progress over time:

```bash
# Collect with timestamp
/migration-report-dashboard collect --timestamp

# View trends in dashboard
# Navigate to: Trends page
```

### 2. Custom Metrics

Add custom metrics via plugins:

```python
# collectors/custom_metric_collector.py
from collectors.base_collector import BaseCollector

class CustomMetricCollector(BaseCollector):
    def collect(self):
        # Your custom logic
        return {"metric": value}
```

### 3. Alerting

Set up alerts for critical gaps:

```yaml
alerts:
  - name: "Critical Performance Regression"
    condition: "modern.lighthouse.performance < legacy.lighthouse.performance - 10"
    severity: "critical"
  - name: "Low Test Coverage"
    condition: "modern.coverage < 80"
    severity: "warning"
```

---

## Output Examples

### Executive Summary (PDF)

```
MIGRATION ASSESSMENT REPORT
============================

Overall Score: 87/100 (Near Ready)

Dimension Scores:
  Frontend:     92/100 ✅
  Backend:      85/100 🟢
  Database:     95/100 ✅
  Quality:      78/100 🟡
  NFR:          84/100 🟢
  Integration:  90/100 ✅

Critical Gaps:
  1. Test coverage below 80% (currently 72%)
  2. 3 API endpoints missing in modern
  3. SonarQube: 12 code smells to address

Recommendations:
  1. Add missing API endpoints before release
  2. Increase test coverage in backend services
  3. Address SonarQube code smells
  4. Run load tests at 2x expected traffic

Estimated Effort: 40 hours
Risk Level: Low
```

---

## Troubleshooting

### Issue: Lighthouse collection fails

**Solution:** Ensure frontend URLs are accessible and apps are running

```bash
# Test manually
npx lighthouse http://localhost:8080 --output json
```

### Issue: SonarQube data not loading

**Solution:** Configure SonarQube token in environment

```bash
export SONAR_TOKEN="your-token"
export SONAR_HOST_URL="http://localhost:9000"
```

### Issue: Dashboard shows "No data"

**Solution:** Run collection first

```bash
./scripts/collect-all-metrics.sh
```

---

## Success Criteria

Dashboard is ready when:

- ✅ All collectors successfully gather data
- ✅ Overall migration score calculated
- ✅ All 8 dashboard pages load without errors
- ✅ Charts render correctly
- ✅ Export to PDF works
- ✅ No critical gaps in data collection

---

## Next Steps

After reviewing the dashboard:

1. **Address Critical Gaps** — Focus on red/orange items first
2. **Re-run Collection** — After fixes, collect metrics again
3. **Track Progress** — Compare scores over time
4. **Share with Stakeholders** — Export executive summary
5. **Plan Deployment** — Use score to inform go/no-go decision
