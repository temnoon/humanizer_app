#!/bin/bash
#
# Humanizer CLI Installation Script
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

echo -e "${BLUE}🚀 Installing Humanizer CLI${NC}"
echo "=================================="

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
pip3 install --user httpx rich

# Create zsh completion
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

# Create alias and functions for convenience
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

# Show available LLM models
function hmodels() {
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

# Interactive content transformation
function htrans() {
    local text="$1"
    if [[ -z "$text" ]]; then
        echo -n "Enter text to transform: "
        read text
    fi
    
    echo "Available engines: lpe, quantum, maieutic"
    echo -n "Choose engine (default: lpe): "
    read engine
    engine=${engine:-lpe}
    
    if [[ "$engine" == "lpe" ]]; then
        echo -n "Persona (optional): "
        read persona
        echo -n "Namespace (optional): "
        read namespace
        echo -n "Style (optional): "
        read style
        
        humanizer transform "$text" --engine lpe \
            ${persona:+--persona "$persona"} \
            ${namespace:+--namespace "$namespace"} \
            ${style:+--style "$style"}
    else
        humanizer transform "$text" --engine "$engine"
    fi
}

# Batch operations
function hbatch() {
    local action="$1"
    shift
    
    case "$action" in
        ingest)
            for file in "$@"; do
                echo "Processing: $file"
                humanizer content ingest --file "$file"
            done
            ;;
        search)
            for query in "$@"; do
                echo "Searching: $query"
                humanizer search "$query"
                echo "---"
            done
            ;;
        *)
            echo "Usage: hbatch <ingest|search> <files...>"
            ;;
    esac
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
        *)
            echo "Usage: hdev <start|stop|logs|test>"
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
echo "=================================="
echo -e "${GREEN}🎉 Installation Complete!${NC}"
echo "=================================="
echo ""
echo "📋 Available commands:"
echo "  humanizer health              - Check API health"
echo "  humanizer providers status    - Show LLM provider status"
echo "  humanizer keys add <provider> <key> - Add API key"
echo "  humanizer search \"query\"       - Search content"
echo "  humanizer transform \"text\"     - Transform content"
echo "  humanizer llm complete \"prompt\" - Get LLM completion"
echo ""
echo "🚀 Quick shortcuts:"
echo "  hhealth                       - Quick health check"
echo "  hsearch \"query\"               - Quick search"
echo "  hask \"question\"               - Ask LLM"
echo "  htransform \"text\"             - Transform with LPE"
echo "  hkey <provider>               - Add API key interactively"
echo ""
echo "🔧 Development helpers:"
echo "  hdev start                    - Start unified platform"
echo "  hdev stop                     - Stop unified platform"
echo "  hdev logs                     - View API logs"
echo "  hdev test                     - Run API tests"
echo ""
echo "💡 Next steps:"
echo "  1. Restart your terminal or run: source ~/.zshrc"
echo "  2. Add your API keys: humanizer keys migrate"
echo "  3. Check status: humanizer providers status"
echo "  4. Start testing: humanizer health"
echo ""
echo -e "${BLUE}Happy transforming! 🚀${NC}"