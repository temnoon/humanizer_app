#!/bin/bash
#
# Quick Environment Fix for Unified Platform
# Solves immediate Python environment issues
#

set -e

echo "🔧 Quick Environment Fix for Unified Platform"
echo "============================================="

# Deactivate any current environment
if [ -n "$VIRTUAL_ENV" ]; then
    echo "📤 Deactivating current environment..."
    deactivate 2>/dev/null || true
fi

# Go to unified platform directory
cd "$(dirname "$0")"
pwd

echo "🐍 Setting up fresh Python environment..."

# Remove old venv if it exists
if [ -d "venv" ]; then
    echo "🗑️  Removing old venv..."
    rm -rf venv
fi

# Create new virtual environment
echo "🏗️  Creating new virtual environment..."
python3 -m venv venv

# Activate it
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install essential packages
echo "📦 Installing essential packages..."
pip install --no-deps httpx rich click

# Try to install more packages
echo "📦 Installing additional packages..."
pip install --no-deps pydantic fastapi uvicorn || echo "⚠️  Some packages failed - continuing..."

echo ""
echo "✅ Quick fix complete!"
echo ""
echo "🎯 To use this environment:"
echo "  cd unified-platform"
echo "  source venv/bin/activate"
echo ""
echo "🧪 Test the CLI:"
echo "  cd cli"
echo "  python humanizer --help"
echo ""
echo "🚀 Current environment:"
echo "  Python: $(python --version)"
echo "  Location: $(which python)"
echo "  Virtual Env: $VIRTUAL_ENV"
echo ""

# Create a simple activation script
cat > activate.sh << 'EOF'
#!/bin/bash
# Quick activation for unified platform
source venv/bin/activate
echo "✅ Unified Platform environment activated"
echo "Python: $(python --version)"
echo "To test CLI: cd cli && python humanizer --help"
EOF

chmod +x activate.sh

echo "💡 Created quick activation script: ./activate.sh"