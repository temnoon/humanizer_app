#!/bin/bash
#
# Humanizer CLI Installation Script (Fixed for Virtual Environments)
# Installs the CLI tool and sets up zsh integration
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
CLI_NAME="humanizer"
INSTALL_DIR="$HOME/.local/bin"
CLI_SOURCE="$(dirname "$0")/$CLI_NAME"
CLI_TARGET="$INSTALL_DIR/$CLI_NAME"
COMPLETION_DIR="$HOME/.local/share/zsh/site-functions"
COMPLETION_FILE="_$CLI_NAME"

echo -e "${BLUE}🚀 Installing Humanizer CLI (Fixed Version)${NC}"
echo "=============================================="

# Check if we're in a virtual environment
if [ -n "$VIRTUAL_ENV" ]; then
    echo -e "${GREEN}✅ Virtual environment detected: $VIRTUAL_ENV${NC}"
    USE_VENV=true
else
    echo -e "${YELLOW}⚠️  No virtual environment detected${NC}"
    echo "Checking for unified-platform venv..."
    
    # Look for unified platform venv
    UNIFIED_VENV="../venv"
    if [ -d "$UNIFIED_VENV" ]; then
        echo -e "${GREEN}✅ Found unified platform venv${NC}"
        source "$UNIFIED_VENV/bin/activate"
        USE_VENV=true
    else
        echo -e "${YELLOW}⚠️  No unified platform venv found${NC}"
        echo "Will attempt to install dependencies with --user flag"
        USE_VENV=false
    fi
fi

# Check if source CLI exists
if [ ! -f "$CLI_SOURCE" ]; then
    echo -e "${RED}❌ CLI source not found: $CLI_SOURCE${NC}"
    exit 1
fi

# Create directories
echo -e "${BLUE}📁 Creating directories...${NC}"
mkdir -p "$INSTALL_DIR"
mkdir -p "$COMPLETION_DIR"

# Install CLI
echo -e "${BLUE}📦 Installing CLI to $CLI_TARGET${NC}"
cp "$CLI_SOURCE" "$CLI_TARGET"
chmod +x "$CLI_TARGET"

# Check if directory is in PATH
if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
    echo -e "${YELLOW}⚠️  Adding $INSTALL_DIR to PATH${NC}"
    
    # Add to zshrc if it exists
    if [ -f "$HOME/.zshrc" ]; then
        echo "" >> "$HOME/.zshrc"
        echo "# Humanizer CLI" >> "$HOME/.zshrc"
        echo "export PATH=\"\$HOME/.local/bin:\$PATH\"" >> "$HOME/.zshrc"
        echo -e "${GREEN}✅ Added to ~/.zshrc${NC}"
    fi
    
    # Add to current session
    export PATH="$HOME/.local/bin:$PATH"
fi

# Install dependencies
echo -e "${BLUE}📦 Installing Python dependencies...${NC}"

if [ "$USE_VENV" = true ]; then
    echo "Installing in virtual environment..."
    pip install httpx rich
else
    echo "Installing with --user flag..."
    python3 -m pip install --user httpx rich
fi

# Create wrapper script that handles virtual environment
echo -e "${BLUE}🔧 Creating environment-aware wrapper...${NC}"

cat > "$CLI_TARGET" << 'EOF'
#!/usr/bin/env python3
"""
Humanizer CLI - Environment-aware wrapper
Automatically activates the correct Python environment
"""
import os
import sys
import subprocess
from pathlib import Path

# Find the unified platform directory
script_dir = Path(__file__).parent
unified_platform_dirs = [
    Path.home() / "humanizer-lighthouse" / "unified-platform",
    script_dir.parent / "unified-platform",
    Path.cwd() / "unified-platform",
    Path.cwd(),
]

unified_platform_dir = None
for directory in unified_platform_dirs:
    if directory.exists() and (directory / "api").exists():
        unified_platform_dir = directory
        break

# Check for virtual environment
venv_paths = []
if unified_platform_dir:
    venv_paths.extend([
        unified_platform_dir / "venv",
        unified_platform_dir / "api" / "venv",
    ])

# Also check current directory
venv_paths.extend([
    Path.cwd() / "venv",
    Path.cwd() / "api" / "venv",
])

# Find and activate virtual environment
python_exe = sys.executable
for venv_path in venv_paths:
    if venv_path.exists():
        if sys.platform == "win32":
            potential_python = venv_path / "Scripts" / "python.exe"
        else:
            potential_python = venv_path / "bin" / "python"
        
        if potential_python.exists():
            python_exe = str(potential_python)
            break

# Add unified platform to Python path
if unified_platform_dir:
    sys.path.insert(0, str(unified_platform_dir))
    sys.path.insert(0, str(unified_platform_dir / "shared"))
    sys.path.insert(0, str(unified_platform_dir / "api"))

# If we're not using the right Python, re-execute with correct one
if python_exe != sys.executable:
    env = os.environ.copy()
    if unified_platform_dir:
        env['PYTHONPATH'] = f"{unified_platform_dir}:{unified_platform_dir}/shared:{unified_platform_dir}/api"
    
    # Re-run with correct Python
    result = subprocess.run([python_exe, __file__ + "_real"] + sys.argv[1:], env=env)
    sys.exit(result.returncode)

# Import the real CLI
try:
    # Try to import from the unified platform
    if unified_platform_dir:
        cli_path = unified_platform_dir / "cli" / "humanizer_real"
        if cli_path.exists():
            exec(open(cli_path).read())
        else:
            print("❌ Humanizer CLI not found in unified platform")
            sys.exit(1)
    else:
        print("❌ Unified platform directory not found")
        print("Please run this from the unified-platform directory or ensure it's in a standard location")
        sys.exit(1)
        
except ImportError as e:
    print(f"❌ Failed to import required dependencies: {e}")
    print("Please ensure you have installed the requirements:")
    print("  pip install httpx rich")
    sys.exit(1)
EOF

# Copy the actual CLI logic to _real file
cp "$(dirname "$0")/$CLI_NAME" "${CLI_TARGET}_real"

# Create zsh completion (same as before)
echo -e "${BLUE}🔧 Setting up zsh completion...${NC}"

cat > "$COMPLETION_DIR/$COMPLETION_FILE" << 'EOF'
#compdef humanizer

_humanizer() {
    local context state line
    typeset -A opt_args
    
    _arguments -C \
        '--api-url[API base URL]:url:' \
        '--verbose[Verbose output]' \
        '--help[Show help]' \
        '1:command:->commands' \
        '*::arg:->args'
    
    case $state in
        commands)
            local commands=(
                'health:Check API health'
                'providers:Manage LLM providers'
                'keys:Manage API keys'
                'content:Manage content'
                'search:Search content'
                'transform:Transform content'
                'llm:LLM operations'
                'config:Show configuration'
            )
            _describe 'command' commands
            ;;
        args)
            case $words[1] in
                providers)
                    _arguments \
                        '1:action:(status)'
                    ;;
                keys)
                    _arguments \
                        '1:action:(add migrate)' \
                        '2:provider:(openai anthropic deepseek groq google ollama together)'
                    ;;
                content)
                    _arguments \
                        '1:action:(ingest)' \
                        '--file[File to ingest]:file:_files' \
                        '--type[Content type]:(text html markdown json pdf)' \
                        '--source[Content source]:' \
                        '--title[Content title]:' \
                        '--tags[Content tags]:'
                    ;;
                search)
                    _arguments \
                        '1:query:' \
                        '--type[Search type]:(semantic fulltext)' \
                        '--limit[Result limit]:number:' \
                        '--content-types[Content types]:(text html markdown json)'
                    ;;
                transform)
                    _arguments \
                        '1:text:' \
                        '--engine[Engine]:(lpe quantum maieutic)' \
                        '--persona[Persona]:' \
                        '--namespace[Namespace]:' \
                        '--style[Style]:'
                    ;;
                llm)
                    _arguments \
                        '1:action:(complete)' \
                        '--model[Model]:' \
                        '--temperature[Temperature]:number:' \
                        '--max-tokens[Max tokens]:number:'
                    ;;
            esac
            ;;
    esac
}

_humanizer "$@"
EOF

# Create convenience functions (same as before)
echo -e "${BLUE}🔧 Setting up convenience functions...${NC}"

FUNCTIONS_FILE="$HOME/.local/share/humanizer_functions.zsh"

cat > "$FUNCTIONS_FILE" << 'EOF'
# Humanizer CLI convenience functions

# Quick health check
function hhealth() {
    humanizer health
}

# Quick search
function hsearch() {
    humanizer search "$@"
}

# Quick transform with LPE
function htransform() {
    local text="$1"
    shift
    humanizer transform "$text" --engine lpe "$@"
}

# Quick LLM completion
function hask() {
    humanizer llm complete "$@"
}

# Quick content ingestion
function hingest() {
    if [[ -f "$1" ]]; then
        humanizer content ingest --file "$1" "${@:2}"
    else
        humanizer content ingest "$@"
    fi
}

# Provider status with alias
function hproviders() {
    humanizer providers status
}

# Add API key with interactive prompt
function hkey() {
    local provider="$1"
    if [[ -z "$provider" ]]; then
        echo "Usage: hkey <provider>"
        echo "Available providers: openai, anthropic, deepseek, groq, google"
        return 1
    fi
    
    echo -n "Enter API key for $provider: "
    read -s api_key
    echo
    
    humanizer keys add "$provider" "$api_key"
}

# Development helpers
function hdev() {
    case "$1" in
        start)
            echo "Starting unified platform..."
            cd ~/humanizer-lighthouse/unified-platform
            ./start.sh
            ;;
        stop)
            echo "Stopping unified platform..."
            cd ~/humanizer-lighthouse/unified-platform
            docker-compose down
            ;;
        logs)
            cd ~/humanizer-lighthouse/unified-platform
            docker-compose logs -f api
            ;;
        test)
            cd ~/humanizer-lighthouse/unified-platform
            python test_api.py
            ;;
        env)
            echo "Setting up Python environment..."
            cd ~/humanizer-lighthouse/unified-platform
            ./setup_env.sh
            ;;
        *)
            echo "Usage: hdev <start|stop|logs|test|env>"
            ;;
    esac
}
EOF

# Add to zshrc
if [ -f "$HOME/.zshrc" ]; then
    if ! grep -q "humanizer_functions.zsh" "$HOME/.zshrc"; then
        echo "" >> "$HOME/.zshrc"
        echo "# Humanizer CLI functions" >> "$HOME/.zshrc"
        echo "source ~/.local/share/humanizer_functions.zsh" >> "$HOME/.zshrc"
    fi
fi

# Test installation
echo -e "${BLUE}🧪 Testing installation...${NC}"

if command -v "$CLI_NAME" >/dev/null 2>&1; then
    echo -e "${GREEN}✅ CLI installed successfully${NC}"
    
    # Test basic functionality
    if "$CLI_NAME" --help >/dev/null 2>&1; then
        echo -e "${GREEN}✅ CLI is working${NC}"
    else
        echo -e "${YELLOW}⚠️  CLI installed but may have dependency issues${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  CLI installed but not in PATH. Restart your terminal.${NC}"
fi

# Show completion
echo ""
echo "=============================================="
echo -e "${GREEN}🎉 Installation Complete!${NC}"
echo "=============================================="
echo ""
echo "🔧 Environment Setup:"
echo "  Current Python: $(python --version 2>/dev/null || echo 'Not found')"
echo "  Virtual Env: ${VIRTUAL_ENV:-'None'}"
echo ""
echo "📋 Next steps:"
echo "  1. Restart your terminal or run: source ~/.zshrc"
echo "  2. Set up Python environment: hdev env"
echo "  3. Migrate API keys: humanizer keys migrate"
echo "  4. Test: humanizer health"
echo ""
echo -e "${BLUE}Happy transforming! 🚀${NC}"