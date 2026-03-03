#!/bin/bash
# Launch Migration Progress Dashboard
# Usage: ./launch-progress-dashboard.sh

echo "🎯 Launching Migration Progress Dashboard..."
echo ""

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "⚠️ Streamlit not installed"
    echo "Installing dependencies..."
    pip install streamlit pandas plotly pyyaml
fi

# Navigate to progress dashboard
cd progress-app

# Check if docs directory exists
if [ ! -d "../../docs/context-fabric" ]; then
    echo "⚠️ No migration data found in docs/"
    echo "   Run /migrate to start migration, or use sample data for demo"
    echo ""
fi

# Launch dashboard
echo "✅ Starting dashboard..."
echo "   → Open http://localhost:8501 in your browser"
echo ""

streamlit run main.py --server.port=8501 --server.headless=true
