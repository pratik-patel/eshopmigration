#!/bin/bash
# Collect all metrics from legacy and modern applications

set -e

echo "🚀 Migration Report Dashboard - Metrics Collection"
echo "==================================================="

# Change to skill directory
cd "$(dirname "$0")/.."

# Check configuration
if [ ! -f "config.yaml" ]; then
    echo "❌ Error: config.yaml not found"
    echo "   Copy config.yaml.example and customize it"
    exit 1
fi

# Check dependencies
echo ""
echo "📦 Checking dependencies..."

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found"
    exit 1
fi
echo "  ✅ Python 3"

if ! command -v npx &> /dev/null; then
    echo "❌ Node.js/npx not found"
    exit 1
fi
echo "  ✅ Node.js"

# Ensure Python packages installed
if ! python3 -c "import streamlit" 2>/dev/null; then
    echo "⚠️  Python dependencies not installed"
    echo "   Installing..."
    pip install -r requirements.txt
fi

# Ensure Node packages installed
if [ ! -d "node_modules" ]; then
    echo "⚠️  Node dependencies not installed"
    echo "   Installing..."
    npm install
fi

# Create data directories
mkdir -p data/legacy
mkdir -p data/modern

echo ""
echo "=================================="
echo "📊 Collecting LEGACY metrics"
echo "=================================="

echo ""
echo "1️⃣  Frontend (Lighthouse)..."
python3 -m collectors.run_collector lighthouse legacy || echo "⚠️  Lighthouse failed (legacy)"

echo ""
echo "2️⃣  Backend (API)..."
python3 -m collectors.run_collector api legacy || echo "⚠️  API collection failed (legacy)"

echo ""
echo "3️⃣  Database..."
python3 -m collectors.run_collector database legacy || echo "⚠️  Database collection failed (legacy)"

echo ""
echo "4️⃣  Quality (SonarQube)..."
python3 -m collectors.run_collector sonar legacy || echo "⚠️  SonarQube failed (legacy)"

echo ""
echo "5️⃣  Coverage..."
python3 -m collectors.run_collector coverage legacy || echo "⚠️  Coverage failed (legacy)"

echo ""
echo "=================================="
echo "📊 Collecting MODERN metrics"
echo "=================================="

echo ""
echo "1️⃣  Frontend (Lighthouse)..."
python3 -m collectors.run_collector lighthouse modern || echo "⚠️  Lighthouse failed (modern)"

echo ""
echo "2️⃣  Backend (API)..."
python3 -m collectors.run_collector api modern || echo "⚠️  API collection failed (modern)"

echo ""
echo "3️⃣  Database..."
python3 -m collectors.run_collector database modern || echo "⚠️  Database collection failed (modern)"

echo ""
echo "4️⃣  Quality (SonarQube)..."
python3 -m collectors.run_collector sonar modern || echo "⚠️  SonarQube failed (modern)"

echo ""
echo "5️⃣  Coverage..."
python3 -m collectors.run_collector coverage modern || echo "⚠️  Coverage failed (modern)"

echo ""
echo "6️⃣  Feature Parity (Browser Agent)..."
# Check if browser-agent skill is available
if [ -f "../browser-agent/scripts/run-verification.sh" ]; then
    cd ../browser-agent
    ./scripts/run-verification.sh \
        --legacy $(grep 'frontend_url' ../migration-report-dashboard/config.yaml | head -1 | awk '{print $2}') \
        --modern $(grep 'frontend_url' ../migration-report-dashboard/config.yaml | tail -1 | awk '{print $2}') \
        --output ../migration-report-dashboard/data/modern/parity.json
    cd -
else
    echo "⚠️  browser-agent skill not found. Feature parity will be limited."
fi

echo ""
echo "=================================="
echo "🔄 Aggregating metrics..."
echo "=================================="

python3 scripts/aggregate_metrics.py

# Check if aggregation succeeded
if [ ! -f "data/legacy/metrics.json" ] || [ ! -f "data/modern/metrics.json" ]; then
    echo "❌ Error: Metrics aggregation failed"
    exit 1
fi

echo ""
echo "✅ Collection complete!"
echo ""
echo "📂 Results:"
echo "  - Legacy metrics: data/legacy/metrics.json"
echo "  - Modern metrics: data/modern/metrics.json"
echo ""
echo "🚀 Next steps:"
echo "  1. Launch dashboard: streamlit run app/main.py"
echo "  2. Open browser: http://localhost:8501"
echo "  3. Review comparison reports"
echo ""
echo "💡 Tip: Re-run this script after making changes to update metrics"
