# Humanizer CLI

A powerful command-line interface for the Unified Humanizer Platform, providing full access to content transformation, search, and LLM capabilities directly from your terminal.

## 🚀 Quick Installation

```bash
# Install CLI and set up zsh integration
cd unified-platform/cli
./install.sh

# Restart terminal or reload zsh
source ~/.zshrc
```

## 🔑 API Key Setup

### Migrate from Legacy System
```bash
# Migrate existing API keys from lighthouse keychain
humanizer keys migrate
```

### Add New API Keys
```bash
# Add individual API keys
humanizer keys add openai sk-...
humanizer keys add anthropic claude-...
humanizer keys add deepseek sk-...

# Interactive key addition
hkey openai
```

## 📋 Available Commands

### Health & Status
```bash
# Check API health
humanizer health
hhealth  # Quick alias

# Check LLM provider status
humanizer providers status
hproviders  # Quick alias
```

### Content Management
```bash
# Ingest text content
humanizer content ingest "Your text here"
hingest "Your text here"  # Quick alias

# Ingest files
humanizer content ingest --file document.txt --title "My Document"
hingest document.txt  # Quick alias

# Batch ingest multiple files
hbatch ingest *.txt
```

### Search
```bash
# Semantic search
humanizer search "machine learning"
hsearch "machine learning"  # Quick alias

# Full-text search
humanizer search "machine learning" --type fulltext

# Search with filters
humanizer search "AI" --content-types text markdown --limit 5
```

### Content Transformation
```bash
# LPE transformation
humanizer transform "Transform this text" --engine lpe --persona academic --style formal
htransform "Transform this text" --persona academic  # Quick alias

# Quantum analysis
humanizer transform "Analyze this narrative" --engine quantum

# Maieutic dialogue
humanizer transform "Explore this topic" --engine maieutic

# Interactive transformation
htrans  # Prompts for all parameters
```

### LLM Operations
```bash
# Get completion
humanizer llm complete "What is artificial intelligence?"
hask "What is artificial intelligence?"  # Quick alias

# With specific parameters
humanizer llm complete "Explain quantum computing" --temperature 0.3 --max-tokens 500
```

### Configuration
```bash
# Show current configuration
humanizer config
```

## 🚀 Quick Shortcuts

The CLI includes convenient shortcuts for common operations:

| Command | Shortcut | Description |
|---------|----------|-------------|
| `humanizer health` | `hhealth` | Quick health check |
| `humanizer search "query"` | `hsearch "query"` | Quick search |
| `humanizer llm complete "prompt"` | `hask "prompt"` | Ask LLM |
| `humanizer transform "text"` | `htransform "text"` | Transform with LPE |
| `humanizer providers status` | `hproviders` | Provider status |
| `humanizer content ingest` | `hingest` | Ingest content |

## 🔧 Development Helpers

```bash
# Start/stop unified platform
hdev start
hdev stop

# View logs
hdev logs

# Run API tests
hdev test
```

## 📚 Advanced Usage

### Batch Operations
```bash
# Process multiple files
hbatch ingest *.md *.txt

# Multiple searches
hbatch search "AI" "machine learning" "neural networks"
```

### Interactive Key Management
```bash
# Add API key with secure prompt
hkey openai

# Check all provider status
hproviders
```

### Pipeline Operations
```bash
# Ingest → Transform → Search pipeline
content_id=$(humanizer content ingest "Raw text" | grep "Content ID" | cut -d: -f2)
humanizer transform "Raw text" --engine lpe --persona academic > transformed.txt
humanizer search "academic analysis"
```

## 🎯 Examples

### Content Transformation Workflow
```bash
# 1. Check if API is ready
hhealth

# 2. Check available providers
hproviders

# 3. Ingest source content
hingest document.txt --title "Research Paper"

# 4. Transform with different engines
htransform "Research findings show..." --persona scientist --style formal
humanizer transform "Research findings show..." --engine quantum
humanizer transform "Research findings show..." --engine maieutic

# 5. Search for related content
hsearch "research findings"
```

### LLM Provider Testing
```bash
# Test different providers
hask "Hello, how are you?" --model gpt-4
hask "Hello, how are you?" --model claude-3-sonnet
hask "Hello, how are you?" --model deepseek-chat
```

### Academic Workflow
```bash
# Transform academic text to different audiences
htransform "Complex academic concept..." --persona student --style simple
htransform "Complex academic concept..." --persona expert --style technical
htransform "Complex academic concept..." --persona general --style accessible
```

## 🔍 Troubleshooting

### CLI Not Found
```bash
# Check if in PATH
echo $PATH | grep -o ~/.local/bin

# If not, add to PATH
export PATH="$HOME/.local/bin:$PATH"
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
```

### API Connection Issues
```bash
# Check if unified platform is running
hhealth

# If not running, start it
hdev start

# Check Docker status
docker-compose ps
```

### Provider Issues
```bash
# Check provider status
hproviders

# Test specific provider
humanizer keys add provider_name api_key

# Migrate legacy keys
humanizer keys migrate
```

### Permission Issues
```bash
# Fix CLI permissions
chmod +x ~/.local/bin/humanizer

# Reinstall if needed
cd unified-platform/cli
./install.sh
```

## 🎨 Customization

### Custom Aliases
Add to your `~/.zshrc`:

```bash
# Custom shortcuts
alias hai="hask"  # AI assistant
alias ht="htransform"  # Transform
alias hs="hsearch"  # Search
alias hc="humanizer config"  # Config

# Transformation presets
alias academic="htransform --persona academic --style formal"
alias casual="htransform --persona general --style casual"
alias technical="htransform --persona expert --style technical"
```

### Custom Functions
```bash
# Smart content processor
function hprocess() {
    local file="$1"
    local persona="${2:-academic}"
    
    echo "Processing $file with $persona persona..."
    content_id=$(hingest "$file")
    htransform "$(cat "$file")" --persona "$persona" --style formal
}

# Multi-engine comparison
function hcompare() {
    local text="$1"
    
    echo "=== LPE ==="
    htransform "$text" --engine lpe
    
    echo "=== Quantum ==="
    humanizer transform "$text" --engine quantum
    
    echo "=== Maieutic ==="
    humanizer transform "$text" --engine maieutic
}
```

## 🤖 Integration with Other Tools

### With jq for JSON Processing
```bash
# Extract specific data
humanizer providers status | jq '.openai.available'
humanizer search "AI" | jq '.results[].content.metadata.title'
```

### With fzf for Interactive Selection
```bash
# Interactive search
hsearch "$(echo "machine learning\nartificial intelligence\nneural networks" | fzf)"
```

### With Vim/Neovim
Add to your vim config:
```vim
" Transform selected text
vnoremap <leader>ht :'<,'>!humanizer transform "$(cat)" --engine lpe<CR>

" Ask AI about selected text
vnoremap <leader>ha :'<,'>!humanizer llm complete "Explain: $(cat)"<CR>
```

---

**Happy transforming! 🚀**

For more help: `humanizer --help` or visit the [Unified Platform Documentation](../README.md)