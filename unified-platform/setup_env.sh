#!/bin/bash
#
# Unified Platform Python Environment Setup
# Creates a proper Python environment for the unified platform
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🐍 Setting Up Unified Platform Python Environment${NC}"
echo "================================================="

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
echo -e "${BLUE}📋 Python version: $PYTHON_VERSION${NC}"

if [[ $(echo "$PYTHON_VERSION < 3.8" | bc -l) == 1 ]]; then
    echo -e "${RED}❌ Python 3.8+ required. Current: $PYTHON_VERSION${NC}"
    exit 1
fi

# Create new virtual environment in unified-platform
VENV_PATH="./venv"

if [ -d "$VENV_PATH" ]; then
    echo -e "${YELLOW}⚠️  Existing venv found. Removing...${NC}"
    rm -rf "$VENV_PATH"
fi

echo -e "${BLUE}🏗️  Creating new virtual environment...${NC}"
python3 -m venv "$VENV_PATH"

echo -e "${BLUE}🔌 Activating virtual environment...${NC}"
source "$VENV_PATH/bin/activate"

echo -e "${BLUE}📦 Upgrading pip...${NC}"
pip install --upgrade pip setuptools wheel

echo -e "${BLUE}📦 Installing core dependencies...${NC}"
pip install httpx rich click

echo -e "${BLUE}📦 Installing API dependencies...${NC}"
if [ -f "api/requirements.txt" ]; then
    pip install -r api/requirements.txt
else
    echo -e "${YELLOW}⚠️  API requirements.txt not found, installing common packages...${NC}"
    pip install fastapi uvicorn pydantic sqlalchemy asyncpg redis chromadb sentence-transformers
fi

echo -e "${BLUE}📦 Installing additional LLM packages...${NC}"
pip install openai anthropic ollama litellm

echo -e "${BLUE}🧪 Testing installation...${NC}"

# Test imports
python3 -c "
import httpx
import rich
import fastapi
import pydantic
print('✅ Core packages imported successfully')
"

echo -e "${GREEN}✅ Environment setup complete!${NC}"
echo ""
echo "To activate this environment in the future:"
echo -e "${BLUE}  cd unified-platform${NC}"
echo -e "${BLUE}  source venv/bin/activate${NC}"
echo ""
echo "Current environment:"
echo "  Python: $(python --version)"
echo "  Pip: $(pip --version)"
echo "  Location: $(which python)"
echo ""

# Create activation script
cat > activate_env.sh << 'EOF'
#!/bin/bash
# Quick activation script for unified platform environment
cd "$(dirname "$0")"
source venv/bin/activate
echo "✅ Unified Platform environment activated"
echo "Python: $(python --version)"
echo "Location: $(which python)"
EOF

chmod +x activate_env.sh

echo -e "${GREEN}💡 Created activation script: ./activate_env.sh${NC}"