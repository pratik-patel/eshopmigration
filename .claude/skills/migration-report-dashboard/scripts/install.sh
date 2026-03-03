#!/bin/bash
# Installation script for Migration Report Dashboard

set -e

echo "📦 Migration Report Dashboard - Installation"
echo "============================================="

# Check Python
echo ""
echo "1️⃣ Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "  ✅ $PYTHON_VERSION"
else
    echo "  ❌ Python 3 not found. Please install Python 3.9+"
    exit 1
fi

# Check Node.js
echo ""
echo "2️⃣ Checking Node.js..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo "  ✅ Node.js $NODE_VERSION"
else
    echo "  ❌ Node.js not found. Please install Node.js 18+"
    exit 1
fi

# Install Python dependencies
echo ""
echo "3️⃣ Installing Python dependencies..."
pip install -r requirements.txt

# Install Node dependencies
echo ""
echo "4️⃣ Installing Node.js dependencies..."
npm install

# Create data directories
echo ""
echo "5️⃣ Creating data directories..."
mkdir -p data/legacy
mkdir -p data/modern
mkdir -p reports
echo "  ✅ Directories created"

# Generate sample data
echo ""
echo "6️⃣ Generating sample data..."
python3 scripts/generate_sample_data.py

echo ""
echo "✅ Installation complete!"
echo ""
echo "🚀 Quick Start:"
echo "  1. Configure: vim config.yaml"
echo "  2. Launch: streamlit run app/main.py"
echo "  3. Open: http://localhost:8501"
echo ""
echo "📚 Documentation:"
echo "  - README.md - Full documentation"
echo "  - QUICKSTART.md - 10-minute guide"
echo "  - ARCHITECTURE.md - Technical details"
echo ""
echo "🎯 The dashboard is ready with sample data!"
