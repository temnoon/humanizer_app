#!/bin/bash
# quick_fix.sh - Install missing dependencies and start services

echo "🔧 Quick Fix: Installing Missing Dependencies"
echo "==========================================="

cd /Users/tem/humanizer_api

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Install critical missing dependencies
echo "⬇️  Installing missing packages..."
pip install httpx==0.25.2 rich==13.7.0 pydantic-settings==2.0.3 2>/dev/null

echo "✅ Dependencies installed!"

# Test the setup
echo "🧪 Testing setup..."
python test_setup.py

# Offer to start services
echo ""
echo "🚀 Ready to start services:"
echo "   python test_setup.py archive    # Start Archive API on port 7200"
echo "   python test_setup.py lpe        # Start LPE API on port 7201"
echo "   python main.py dashboard        # Start dashboard"
echo ""
echo "📖 Documentation URLs:"
echo "   http://localhost:7200/docs      # Archive API docs"
echo "   http://localhost:7201/docs      # LPE API docs"
