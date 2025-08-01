# Haw Command Setup

## ✅ Installation Complete

The `haw` (Humanizer Archive Wrapper) command wrapper is now installed and ready to use!

## 🚀 Usage

```bash
# Add to your current session PATH (or restart terminal)
export PATH="$HOME/.local/bin:$PATH"

# Show all available commands
haw help

# Extract your personal writing style
haw extract-writing extract --limit 500

# Run hierarchical embedding 
haw embed embed --limit 50

# Full archive embedding
haw embed-full --batch-size 50

# Monitor embedding progress
haw monitor dashboard
```

## 📂 What's Installed

- **Command wrapper**: `/Users/tem/humanizer-lighthouse/haw`
- **Symlink**: `~/.local/bin/haw` (accessible from anywhere)
- **PATH addition**: Added to `~/.zshrc` for permanent access

## 🎯 Key Features

1. **Auto-discovers project root** - Works from any directory
2. **Manages Python environment** - Automatically uses lighthouse venv
3. **Reliable execution** - Consistent environment every time
4. **User-friendly commands** - Simple aliases for complex scripts

## 📝 Available Commands

### Writing Analysis
- `haw extract-writing extract` - Extract and analyze your personal writing style

### Embedding & Search  
- `haw embed embed` - Test hierarchical embedding batches
- `haw embed-full` - Full archive embedding process
- `haw monitor dashboard` - Monitor embedding progress

### Content Analysis
- `haw assess` - Batch conversation quality assessment
- `haw sample` - Extract representative conversation samples
- `haw wordcloud` - Generate archive word clouds
- `haw categorize` - Content categorization

## 🔧 Troubleshooting

If the command isn't found after installation:

```bash
# Reload your shell configuration
source ~/.zshrc

# Or restart your terminal

# Check if haw is in PATH
which haw
```

The command automatically:
- Finds the project root from any directory
- Activates the correct Python virtual environment
- Sets the proper working directory
- Runs scripts with correct paths

**You can now run `haw` commands from anywhere on your system!**