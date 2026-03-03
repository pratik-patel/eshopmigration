

# Migration Report Dashboard - Installation Guide

Complete installation instructions for the Migration Report Dashboard.

## 📋 Prerequisites

### Required Software

1. **Python 3.9+**
   - Download: https://www.python.org/downloads/
   - Verify: `python3 --version`

2. **Node.js 18+**
   - Download: https://nodejs.org/
   - Verify: `node --version`

3. **pip** (Python package manager)
   - Usually comes with Python
   - Verify: `pip --version`

### Optional (for full metrics collection)

- **SonarQube Server** - For code quality metrics
- **Database Access** - For schema comparison
- **Legacy & Modern Apps** - Running and accessible

## 🚀 Quick Installation

### Option 1: Automated Install (Recommended)

```bash
cd .claude/skills/migration-report-dashboard

# Run installation script
./scripts/install.sh
```

This will:
1. Check prerequisites
2. Install Python dependencies
3. Install Node.js dependencies
4. Create data directories
5. Generate sample data for demo

### Option 2: Manual Installation

```bash
cd .claude/skills/migration-report-dashboard

# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies
npm install

# Create directories
mkdir -p data/legacy data/modern reports

# Generate sample data
python3 scripts/generate_sample_data.py
```

## ✅ Verify Installation

```bash
# Check Python packages
pip list | grep streamlit

# Check Node packages
npm list lighthouse

# Verify sample data
ls -la data/legacy/metrics.json
ls -la data/modern/metrics.json
```

Expected output:
```
✓ streamlit installed
✓ lighthouse installed
✓ Sample data present
```

## 🎯 First Run

### Launch Dashboard with Sample Data

```bash
streamlit run app/main.py
```

Dashboard opens automatically at: **http://localhost:8501**

You should see:
- Overall migration score
- 6 dimension scores
- Sample metrics across all pages

## ⚙️ Configuration

### Configure for Your Applications

```bash
# Copy example config
cp config.yaml config.yaml.backup

# Edit configuration
vim config.yaml
```

**Minimum configuration:**

```yaml
legacy:
  frontend_url: "http://localhost:8080"  # ← Your legacy app
  backend_url: "http://localhost:8080/api"

modern:
  frontend_url: "http://localhost:5173"  # ← Your modern app
  backend_url: "http://localhost:8000"
```

### Optional: SonarQube Integration

```bash
# Set SonarQube token
export SONAR_TOKEN="your-sonar-token"

# Or edit config.yaml
vim config.yaml
# Update sonarqube.token value
```

## 📊 Collect Real Metrics

Once configured, collect metrics from your applications:

```bash
# Ensure both apps are running
curl http://localhost:8080  # Legacy
curl http://localhost:5173  # Modern

# Run collection
./scripts/collect-all-metrics.sh
```

This takes 5-10 minutes and collects:
- Frontend: Lighthouse audits
- Backend: API endpoints and performance
- Database: Schema comparison
- Quality: SonarQube metrics
- Coverage: Test coverage reports

## 🔧 Troubleshooting

### Issue: Python dependencies fail to install

**Solution:**
```bash
# Upgrade pip
python3 -m pip install --upgrade pip

# Install with verbose output
pip install -r requirements.txt -v
```

### Issue: Node dependencies fail

**Solution:**
```bash
# Clear npm cache
npm cache clean --force

# Reinstall
rm -rf node_modules package-lock.json
npm install
```

### Issue: Streamlit won't start

**Solution:**
```bash
# Check if port 8501 is in use
lsof -i :8501

# Kill process if needed
kill -9 <PID>

# Or use different port
streamlit run app/main.py --server.port 8502
```

### Issue: Sample data not loading

**Solution:**
```bash
# Regenerate sample data
python3 scripts/generate_sample_data.py

# Verify files exist
ls -la data/*/metrics.json

# Check file contents
cat data/modern/metrics.json | head
```

### Issue: Lighthouse collection fails

**Solution:**
```bash
# Test Lighthouse manually
npx lighthouse http://localhost:5173 --output json

# Check if app is accessible
curl -I http://localhost:5173
```

### Issue: SonarQube data not loading

**Solution:**
```bash
# Verify token
echo $SONAR_TOKEN

# Test SonarQube API
curl -u $SONAR_TOKEN: http://localhost:9000/api/system/status

# Check project key in config
grep sonarqube_project config.yaml
```

## 🎓 Next Steps

After successful installation:

1. **Explore Sample Data**
   - Navigate through all 8 dashboard pages
   - Understand the metrics displayed
   - Review the scoring algorithm

2. **Configure for Your Apps**
   - Update `config.yaml` with real URLs
   - Test connectivity to both applications

3. **Collect Initial Metrics**
   - Run `./scripts/collect-all-metrics.sh`
   - Review results in dashboard
   - Identify initial gaps

4. **Share with Team**
   - Export executive summary
   - Present findings to stakeholders
   - Plan remediation work

## 📚 Documentation

- **README.md** - Complete feature documentation
- **QUICKSTART.md** - 10-minute getting started guide
- **ARCHITECTURE.md** - Technical architecture details
- **EXAMPLES.md** - Usage examples (to be created)

## 🆘 Getting Help

If you encounter issues:

1. **Check Logs**
   ```bash
   tail -f data/collection.log
   ```

2. **Verify Configuration**
   ```bash
   python3 -c "from app.config import load_config; print(load_config())"
   ```

3. **Test Individual Components**
   ```bash
   # Test Lighthouse collector
   python3 -m collectors.run_collector lighthouse modern

   # Test API collector
   python3 -m collectors.run_collector api modern
   ```

4. **Review Documentation**
   - Check README.md for detailed information
   - Review ARCHITECTURE.md for design details

## ✨ What's Installed

After successful installation, you have:

### Python Packages (30+)
- streamlit - Dashboard framework
- plotly - Interactive charts
- pandas - Data processing
- requests - API calls
- sqlalchemy - Database access
- And many more...

### Node.js Packages
- lighthouse - Performance audits
- chrome-launcher - Browser automation
- puppeteer - Headless Chrome

### Project Structure
```
migration-report-dashboard/
├── app/                    # Streamlit application
│   ├── main.py            # Entry point
│   ├── config.py          # Configuration
│   ├── state.py           # State management
│   └── pages/             # Dashboard pages (8 total)
├── collectors/            # Metrics collectors (6 types)
├── scripts/               # Utility scripts
├── data/                  # Collected metrics
└── reports/               # Generated reports
```

### Features Available
- ✅ 8-page interactive dashboard
- ✅ 6-dimension scoring system
- ✅ Real-time metrics collection
- ✅ Sample data for demos
- ✅ Multiple export formats
- ✅ Comprehensive documentation

## 🎉 Success Criteria

Installation is successful when:

- [x] Dashboard launches without errors
- [x] Sample data displays correctly
- [x] All 8 pages are accessible
- [x] Metrics cards show values
- [x] Charts render properly
- [x] Configuration is customizable

## 🚀 Ready to Use!

Your Migration Report Dashboard is now installed and ready. Start exploring with sample data or configure it for your applications!

```bash
# Launch dashboard
streamlit run app/main.py

# Open browser
open http://localhost:8501
```

Enjoy! 🎊
