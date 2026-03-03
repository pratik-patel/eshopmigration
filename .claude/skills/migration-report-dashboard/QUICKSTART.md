# Migration Report Dashboard - Quick Start Guide

Get up and running in 10 minutes with this quick start guide.

## Prerequisites

- Python 3.9+ installed
- Node.js 18+ installed
- Both legacy and modern applications running

## 1. Installation (2 minutes)

```bash
cd .claude/skills/migration-report-dashboard

# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies (for Lighthouse)
npm install
```

## 2. Configuration (3 minutes)

Edit `config.yaml`:

```bash
vim config.yaml
```

**Minimum required changes:**

```yaml
legacy:
  frontend_url: "http://localhost:8080"  # ← Change to your legacy app URL
  backend_url: "http://localhost:8080/api"

modern:
  frontend_url: "http://localhost:5173"  # ← Change to your modern app URL
  backend_url: "http://localhost:8000"
```

## 3. Collect Metrics (5 minutes)

```bash
# Ensure both apps are running first!

# Run collection
./scripts/collect-all-metrics.sh
```

Expected output:
```
🚀 Migration Report Dashboard - Metrics Collection
===================================================

1️⃣  Frontend (Lighthouse)... ✅
2️⃣  Backend (API)... ✅
3️⃣  Database... ✅
4️⃣  Quality (SonarQube)... ✅
5️⃣  Coverage... ✅

✅ Collection complete!
```

## 4. Launch Dashboard (instant)

```bash
streamlit run app/main.py
```

Opens automatically in browser: **http://localhost:8501**

## 5. Explore (your pace)

Navigate through pages:

1. **🏠 Home** - See overall score
2. **🎨 Frontend** - UI comparison
3. **⚙️ Backend** - API analysis
4. **💾 Database** - Schema diff
5. **✅ Quality** - Code quality metrics
6. **⚡ Performance** - NFR metrics
7. **📊 Summary** - Executive report

## Expected Results

After collection, you should see:

### Overall Score
```
Overall Score: 87/100 (Near Ready)

Dimension Scores:
  Frontend:     92/100 ✅
  Backend:      85/100 🟢
  Database:     95/100 ✅
  Quality:      78/100 🟡
  NFR:          84/100 🟢
```

### Critical Gaps
```
🔴 Test coverage below 80% (currently 72%)
🟠 3 API endpoints missing in modern
```

## Troubleshooting

### Issue: Collection fails

**Check if apps are running:**
```bash
curl http://localhost:8080
curl http://localhost:5173
```

### Issue: "No data available"

**Verify metrics files exist:**
```bash
ls -la data/legacy/metrics.json
ls -la data/modern/metrics.json
```

**If missing, re-run collection:**
```bash
./scripts/collect-all-metrics.sh
```

### Issue: Dashboard shows errors

**Check Python dependencies:**
```bash
pip list | grep streamlit
```

**Reinstall if needed:**
```bash
pip install -r requirements.txt
```

## Next Steps

After reviewing the dashboard:

1. **Address Critical Gaps** - Focus on red items first
2. **Re-collect Metrics** - After fixes: `./scripts/collect-all-metrics.sh`
3. **Export Report** - Click "Export" in sidebar → Select PDF
4. **Share with Team** - Share executive summary with stakeholders

## Advanced Usage

### Customize Scoring Weights

Edit `config.yaml`:
```yaml
scoring:
  weights:
    frontend: 0.30  # Increase if UI is critical
    backend: 0.25
    quality: 0.25   # Increase for quality focus
```

### Add Custom Metrics

See [ARCHITECTURE.md](ARCHITECTURE.md) for guide on adding collectors.

### CI/CD Integration

Add to your pipeline:
```yaml
- name: Migration Report
  run: |
    cd .claude/skills/migration-report-dashboard
    ./scripts/collect-all-metrics.sh
    SCORE=$(python3 scripts/get_score.py)
    if [ $SCORE -lt 85 ]; then exit 1; fi
```

## Resources

- **Full Documentation**: [README.md](README.md)
- **Architecture Details**: [ARCHITECTURE.md](ARCHITECTURE.md)
- **Skill Definition**: [SKILL.md](SKILL.md)

## Support

For issues:
1. Check [README.md](README.md) troubleshooting section
2. Review logs in `data/collection.log`
3. Verify configuration in `config.yaml`

---

**That's it!** You now have a comprehensive migration assessment dashboard running.
