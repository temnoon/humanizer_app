#!/bin/bash
# setup.sh - Initial setup for Humanizer API

echo "🏗️  Setting up Humanizer API Project..."
echo "======================================="

# Check system requirements
echo "📋 Checking system requirements..."

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3.9+ is required but not installed"
    exit 1
fi

if ! command -v git &> /dev/null; then
    echo "❌ Git is required but not installed"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.9"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 9) else 1)"; then
    echo "❌ Python 3.9+ required, found $PYTHON_VERSION"
    exit 1
fi

echo "✅ Python $PYTHON_VERSION found"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📥 Installing Python dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating project directories..."
mkdir -p logs
mkdir -p data
mkdir -p config
mkdir -p tests
mkdir -p chromadb_data

# Create environment file template
if [ ! -f ".env" ]; then
    echo "⚙️  Creating environment configuration..."
    cat > .env << EOF
# API Configuration
ARCHIVE_API_PORT=8001
LPE_API_PORT=8002
LAWYER_API_PORT=8003
PULSE_API_PORT=8004

# Database Configuration
CHROMADB_PATH=./chromadb_data
POSTGRES_URL=postgresql://user:pass@localhost/humanizer

# LLM Provider Keys (add your actual keys)
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
DEEPSEEK_API_KEY=your_deepseek_key_here
OLLAMA_HOST=http://localhost:11434

# Discourse Integration
DISCOURSE_URL=https://humanizer.com
DISCOURSE_API_KEY=your_discourse_key_here
DISCOURSE_USERNAME=api_user

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/humanizer_api.log

# Development
DEBUG=true
ENVIRONMENT=development
EOF
    echo "✅ Environment template created (.env)"
    echo "📝 Please edit .env with your actual API keys"
else
    echo "✅ Environment file already exists"
fi

# Initialize git if not already initialized
if [ ! -d ".git" ]; then
    echo "📚 Initializing git repository..."
    git init
    
    # Create .gitignore
    cat > .gitignore << EOF
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environment
venv/
env/
ENV/

# Environment variables
.env
.env.local
.env.production

# Logs
logs/
*.log

# Database
*.db
*.sqlite3
chromadb_data/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# API Keys and sensitive data
config/secrets.yaml
*.key
*.pem
EOF
    
    git add .gitignore README.md requirements.txt setup.sh
    git commit -m "Initial project setup"
    echo "✅ Git repository initialized"
fi

# Check ChromaDB Memory server
echo "🧠 Checking ChromaDB Memory server..."
if curl -s http://localhost:8000 > /dev/null 2>&1; then
    echo "✅ ChromaDB Memory server is running"
else
    echo "⚠️  ChromaDB Memory server not detected"
    echo "💡 Start your ChromaDB Memory MCP server for full functionality"
fi

echo ""
echo "🎉 Humanizer API setup complete!"
echo "================================="
echo "📁 Project directory: $(pwd)"
echo "🐍 Python virtual environment: venv/"
echo "⚙️  Configuration file: .env"
echo "📋 Next steps:"
echo "   1. Edit .env with your API keys"
echo "   2. Run: ./start_humanizer_api.sh"
echo "   3. Open: http://localhost:8001/docs (Archive API)"
echo "   4. Open: http://localhost:8002/docs (LPE API)"
echo ""
