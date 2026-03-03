

# Migration Report Dashboard

Enterprise-grade migration comparison dashboard that provides comprehensive analysis across frontend, backend, database, quality, and non-functional aspects.

## 🎯 Purpose

This Claude Code skill generates an interactive Streamlit dashboard that compares legacy and modern applications across multiple dimensions:

- **Frontend**: UI/UX, performance (Lighthouse), accessibility, bundle size
- **Backend**: API parity, response times, error rates, business logic
- **Database**: Schema comparison, query performance, data integrity
- **Quality**: SonarQube metrics, test coverage, security vulnerabilities
- **NFR**: Performance benchmarks, scalability, observability
- **Integration**: External system compatibility

## 📊 What You Get

### Interactive Dashboard (Streamlit)
- Multi-page navigation
- Real-time filtering and drill-down
- Interactive charts (Plotly)
- Export to PDF/Excel

### Comprehensive Scoring (0-100)
- Overall migration readiness score
- Per-dimension breakdown
- Weighted scoring based on enterprise priorities

### Gap Analysis
- Identifies critical gaps
- Risk assessment
- Prioritized recommendations

### Executive Reports
- PDF summary for stakeholders
- HTML reports with charts
- Excel exports with raw data

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Migration Dashboard                    │
│                     (Streamlit UI)                       │
└──────────────────────┬──────────────────────────────────┘
                       │
         ┌─────────────┴─────────────┐
         │                           │
    ┌────▼────┐                 ┌────▼────┐
    │ Legacy  │                 │ Modern  │
    │ Metrics │                 │ Metrics │
    └────┬────┘                 └────┬────┘
         │                           │
    ┌────▼───────────────────────────▼────┐
    │          Collectors                  │
    │  • Lighthouse    • API               │
    │  • SonarQube     • Database          │
    │  • Coverage      • Browser Agent     │
    └──────────────────────────────────────┘
```

## 📦 Installation

### Prerequisites

- Python 3.9+
- Node.js 18+
- SonarQube (optional, for quality metrics)

### Setup

```bash
cd .claude/skills/migration-report-dashboard

# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies (for Lighthouse)
npm install

# Copy and configure
cp config.yaml.example config.yaml
vim config.yaml  # Edit URLs and settings
```

### Configuration

Edit `config.yaml`:

```yaml
legacy:
  name: "Legacy Application"
  frontend_url: "http://localhost:8080"
  backend_url: "http://localhost:8080/api"
  # ... more settings

modern:
  name: "Modern Application"
  frontend_url: "http://localhost:5173"
  backend_url: "http://localhost:8000"
  # ... more settings
```

## 🚀 Usage

### 1. Collect Metrics

Gather all metrics from both applications:

```bash
# Ensure both applications are running
# Legacy: http://localhost:8080
# Modern: http://localhost:5173

# Run collection
./scripts/collect-all-metrics.sh
```

**Collection time**: 5-10 minutes depending on configuration

**What gets collected:**
- Lighthouse audits (3 runs, averaged)
- API endpoint inventory
- Response time benchmarks
- SonarQube quality metrics
- Test coverage reports
- Feature parity via browser-agent

### 2. Launch Dashboard

Start the Streamlit application:

```bash
streamlit run app/main.py
```

Dashboard will be available at: **http://localhost:8501**

### 3. Explore Reports

Navigate through 8 dashboard pages:

1. **🏠 Home** - Overview and overall score
2. **🎨 Frontend** - UI/UX, performance, accessibility
3. **⚙️ Backend** - API comparison, response times
4. **💾 Database** - Schema diff, query performance
5. **🔌 Integrations** - External systems mapping
6. **✅ Quality** - SonarQube, coverage, security
7. **⚡ Performance** - NFR metrics, load tests
8. **📊 Summary** - Executive report with recommendations

### 4. Export Reports

From the dashboard sidebar:
- Select format (PDF, Excel, JSON, HTML)
- Click "Export Report"
- Reports saved to `reports/` directory

## 📈 Scoring System

### Overall Score Calculation

```
Overall Score =
  Frontend (25%)     +
  Backend (25%)      +
  Database (10%)     +
  Quality (20%)      +
  NFR (15%)          +
  Integration (5%)
```

### Score Interpretation

| Score | Status | Meaning |
|-------|--------|---------|
| 90-100 | ✅ Production Ready | All critical aspects migrated |
| 75-89 | 🟢 Near Ready | Few gaps, low risk |
| 60-74 | 🟡 In Progress | Significant work remaining |
| 40-59 | 🟠 Early Stage | Major gaps exist |
| 0-39 | 🔴 Not Ready | Critical gaps, not viable |

### Dimension Scores

#### Frontend (25% weight)
- **Feature Parity** (60%): Screen-by-screen comparison
- **Performance** (20%): Lighthouse performance score
- **Accessibility** (20%): WCAG compliance

#### Backend (25% weight)
- **API Parity** (50%): Endpoint coverage
- **Performance** (30%): Response times
- **Error Handling** (20%): Error rates

#### Database (10% weight)
- **Schema Parity** (40%): Table/column matching
- **Performance** (40%): Query execution times
- **Integrity** (20%): Data validation

#### Quality (20% weight)
- **SonarQube** (50%): Code quality metrics
- **Coverage** (30%): Test coverage percentage
- **Security** (20%): Vulnerability count

#### NFR (15% weight)
- **Performance** (40%): Load test results
- **Security** (30%): Security posture
- **Observability** (30%): Logging/monitoring

## 🔧 Collectors

### Lighthouse Collector

Runs Google Lighthouse audits:

```python
from collectors.lighthouse_collector import LighthouseCollector

collector = LighthouseCollector(config, app_type="modern")
metrics = collector.safe_collect()
```

**Metrics collected:**
- Performance score (0-100)
- Accessibility score
- Best Practices score
- SEO score
- Core Web Vitals (FCP, LCP, TTI, CLS)

### API Collector

Discovers and tests API endpoints:

```python
from collectors.api_collector import APICollector

collector = APICollector(config, app_type="modern")
metrics = collector.safe_collect()
```

**Metrics collected:**
- Endpoint inventory
- Response times (avg, p95, p99)
- Error rates
- API parity score

### SonarQube Collector

Fetches code quality metrics:

```python
from collectors.sonar_collector import SonarQubeCollector

collector = SonarQubeCollector(config, app_type="modern")
metrics = collector.safe_collect()
```

**Metrics collected:**
- Bugs, vulnerabilities, code smells
- Complexity, duplication
- Reliability/Security/Maintainability ratings
- Technical debt

### Coverage Collector

Parses test coverage reports:

```python
from collectors.coverage_collector import CoverageCollector

collector = CoverageCollector(config, app_type="modern")
metrics = collector.safe_collect()
```

**Metrics collected:**
- Line coverage %
- Branch coverage %
- Function coverage %
- Uncovered files

## 📊 Dashboard Pages Detail

### Home Page

**Overview dashboard with:**
- Overall migration score (0-100)
- Radar chart showing dimension scores
- Critical gaps summary
- Recent activity timeline

**Example:**
```
Overall Score: 87/100 (Near Ready)

Dimension Scores:
  Frontend:     92/100 ✅
  Backend:      85/100 🟢
  Database:     95/100 ✅
  Quality:      78/100 🟡
  NFR:          84/100 🟢

Critical Gaps:
  🔴 Test coverage below 80% (currently 72%)
  🟠 3 API endpoints missing in modern
```

### Frontend Page

**Detailed UI/UX analysis:**
- Lighthouse score comparison (bar charts)
- Feature parity matrix (table)
- Bundle size breakdown
- Performance metrics (FCP, LCP, TTI, CLS)
- Accessibility issues list
- Browser compatibility matrix

### Backend Page

**API and service comparison:**
- Endpoint parity table
- Response time box plots
- Error rate trends
- Business logic coverage
- OpenAPI contract validation
- Drill-down per endpoint

### Database Page

**Schema and data analysis:**
- Side-by-side schema diff
- Query performance comparison
- Slow query identification
- Data integrity checks
- Migration status
- Index recommendations

### Quality Page

**Code quality metrics:**
- SonarQube dashboard
  - Bugs, vulnerabilities, code smells
  - Complexity trends
  - Duplication percentage
- Test coverage comparison
- Security vulnerabilities
- Technical debt estimation

### Performance (NFR) Page

**Non-functional requirements:**
- Load test results
- Response time percentiles
- Throughput comparison
- Scalability metrics
- Security posture
- Observability score

## 🔄 Integration with Migration Pipeline

### Phase 0: Baseline Collection

```bash
# Collect legacy baseline before migration starts
/migration-report-dashboard collect --legacy http://localhost:8080 --mode baseline
```

### Phase 5: Verification

```bash
# Collect modern metrics after migration
/migration-report-dashboard collect --modern http://localhost:5173

# Launch dashboard for comparison
/migration-report-dashboard dashboard

# Generate executive report
/migration-report-dashboard report --output reports/final-assessment.pdf
```

### Continuous Integration

Add to CI/CD pipeline:

```yaml
# .github/workflows/migration-report.yml
name: Migration Report

on:
  push:
    branches: [main]

jobs:
  report:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Collect Metrics
        run: |
          cd .claude/skills/migration-report-dashboard
          ./scripts/collect-all-metrics.sh

      - name: Check Score
        run: |
          SCORE=$(python3 scripts/get_score.py)
          if [ $SCORE -lt 75 ]; then
            echo "Migration score below threshold: $SCORE"
            exit 1
          fi
```

## 🎨 Customization

### Adding Custom Metrics

1. Create collector class:

```python
# collectors/custom_collector.py
from collectors.base_collector import BaseCollector

class CustomCollector(BaseCollector):
    def collect(self):
        # Your collection logic
        return {
            "metric1": value1,
            "metric2": value2
        }
```

2. Register in collection script:

```bash
# scripts/collect-all-metrics.sh
echo "Custom Metrics..."
python3 -m collectors.run_collector custom modern
```

3. Display in dashboard:

```python
# app/pages/custom_page.py
import streamlit as st

st.title("Custom Metrics")
metrics = st.session_state.modern_metrics.get('custom', {})
st.metric("Custom Metric", metrics.get('metric1', 0))
```

### Adjusting Weights

Edit `config.yaml`:

```yaml
scoring:
  weights:
    frontend: 0.30  # Increase if UI is critical
    backend: 0.30
    quality: 0.25   # Increase for quality-focused projects
    # ... adjust as needed
```

## 🐛 Troubleshooting

### Issue: "No data available"

**Solution:** Run collection first

```bash
./scripts/collect-all-metrics.sh
```

### Issue: Lighthouse fails

**Solution:** Check if frontend is accessible

```bash
curl http://localhost:5173
npx lighthouse http://localhost:5173 --output json
```

### Issue: SonarQube data missing

**Solution:** Set SonarQube token

```bash
export SONAR_TOKEN="your-token-here"
```

Edit `config.yaml` to point to correct SonarQube server.

### Issue: Dashboard won't start

**Solution:** Check Python dependencies

```bash
pip install -r requirements.txt
streamlit --version
```

## 📚 Examples

### Example 1: First-Time Assessment

```bash
# 1. Configure
cp config.yaml.example config.yaml
vim config.yaml

# 2. Start applications
cd legacy-app && dotnet run &
cd frontend && npm run dev &

# 3. Collect
./scripts/collect-all-metrics.sh

# 4. Review
streamlit run app/main.py
```

### Example 2: After Fixes

```bash
# After addressing gaps, re-collect to see improvement
./scripts/collect-all-metrics.sh

# Dashboard will auto-refresh
```

### Example 3: CI/CD Integration

```bash
# Run as part of deployment pipeline
if ./scripts/collect-all-metrics.sh; then
  SCORE=$(python3 scripts/get_score.py)
  if [ $SCORE -ge 85 ]; then
    echo "✅ Migration ready for deployment"
    exit 0
  else
    echo "⚠️  Score: $SCORE. Need 85+ for deployment."
    exit 1
  fi
fi
```

## 📖 Related Skills

- **browser-agent**: Captures UI workflows and feature parity
- **parity-harness-generator**: Generates automated parity tests
- **golden-baseline-capture**: Captures legacy baselines

## 🤝 Contributing

To extend the dashboard:

1. Add new collectors in `collectors/`
2. Add new analyzers in `analyzers/`
3. Add new pages in `app/pages/`
4. Update scoring in `app/state.py`
5. Update documentation

## 📄 License

Part of Claude Code migration toolkit. See main project license.

## 🆘 Support

- Check [EXAMPLES.md](EXAMPLES.md) for detailed scenarios
- Review [INSTALLATION.md](INSTALLATION.md) for setup issues
- See [SKILL.md](SKILL.md) for skill definition

## 🎯 Roadmap

- [ ] Real-time monitoring integration
- [ ] Trend analysis over time
- [ ] AI-powered recommendations
- [ ] Slack/Teams notifications
- [ ] Multi-environment comparison
- [ ] Cost analysis (cloud resources)
- [ ] Migration velocity tracking
