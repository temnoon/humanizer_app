#!/bin/bash
# Setup script for 'ha' command alias

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HA_SCRIPT="$SCRIPT_DIR/ha"

echo "🚀 Setting up Humanizer Archive 'ha' command..."

# Detect shell
if [[ -n "$ZSH_VERSION" ]]; then
    SHELL_RC="$HOME/.zshrc"
    SHELL_NAME="zsh"
elif [[ -n "$BASH_VERSION" ]]; then
    SHELL_RC="$HOME/.bashrc"
    SHELL_NAME="bash"
else
    echo "⚠️  Unable to detect shell. Please manually add to your shell config:"
    echo "alias ha='$HA_SCRIPT'"
    echo "export PATH=\"$SCRIPT_DIR:\$PATH\""
    exit 1
fi

echo "📝 Detected shell: $SHELL_NAME"
echo "📁 Config file: $SHELL_RC"

# Check if alias already exists
if grep -q "alias ha=" "$SHELL_RC" 2>/dev/null; then
    echo "⚠️  'ha' alias already exists in $SHELL_RC"
    echo "🔧 Updating existing alias..."
    
    # Remove old alias
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS sed
        sed -i '' '/alias ha=/d' "$SHELL_RC"
    else
        # Linux sed
        sed -i '/alias ha=/d' "$SHELL_RC"
    fi
fi

# Add new alias and PATH
echo "" >> "$SHELL_RC"
echo "# Humanizer Archive command" >> "$SHELL_RC"
echo "alias ha='$HA_SCRIPT'" >> "$SHELL_RC"
echo "export PATH=\"$SCRIPT_DIR:\$PATH\"" >> "$SHELL_RC"

echo "✅ Added 'ha' alias to $SHELL_RC"
echo ""
echo "🔄 To use immediately, run:"
echo "  source $SHELL_RC"
echo ""
echo "📋 Available commands after setup:"
echo "  ha           - Launch batch monitor UI"
echo "  ha status    - Quick status check"
echo "  ha archive   - Launch archive CLI"
echo "  ha processes - Show active processes"
echo "  ha logs      - View recent logs"
echo "  ha help      - Show all commands"
echo ""
echo "🎉 Setup complete! Restart your terminal or run 'source $SHELL_RC'"

# Test the alias
echo "🧪 Testing the setup..."
if source "$SHELL_RC" && command -v ha >/dev/null 2>&1; then
    echo "✅ 'ha' command is now available!"
    ha help | head -5
else
    echo "⚠️  You may need to restart your terminal for the alias to work"
fi