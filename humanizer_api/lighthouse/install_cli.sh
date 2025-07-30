#!/bin/bash
"""
Humanizer CLI Installer
Simple installer script for the Humanizer CLI
"""

set -e

CLI_NAME="humanizer_cli.py"
INSTALL_DIR="/usr/local/bin"
SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLI_SOURCE="$SOURCE_DIR/$CLI_NAME"

echo "🚀 Humanizer CLI Installer"
echo "=========================="

# Check if source file exists
if [ ! -f "$CLI_SOURCE" ]; then
    echo "❌ Error: $CLI_NAME not found in $SOURCE_DIR"
    exit 1
fi

# Check Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 not found. Please install Python 3.7+:"
    echo "   macOS: brew install python3"
    echo "   Ubuntu: sudo apt install python3"
    exit 1
fi

echo "✅ Found Python: $(python3 --version)"

# Check requests library
if ! python3 -c "import requests" 2>/dev/null; then
    echo "⚠️  requests library not found. Installing..."
    if command -v pip3 &> /dev/null; then
        pip3 install requests
    else
        echo "❌ Error: pip3 not found. Please install requests manually:"
        echo "   pip3 install requests"
        exit 1
    fi
fi

echo "✅ requests library available"

# Installation options
echo ""
echo "Installation options:"
echo "1. Install globally (requires sudo)"
echo "2. Install to user directory"
echo "3. Add to PATH only"
echo "4. Skip installation (just run checks)"

read -p "Choose option (1-4): " choice

case $choice in
    1)
        echo "Installing globally to $INSTALL_DIR..."
        sudo cp "$CLI_SOURCE" "$INSTALL_DIR/humanizer"
        sudo chmod +x "$INSTALL_DIR/humanizer"
        echo "✅ Installed as 'humanizer' command"
        echo "Test with: humanizer status"
        ;;
    2)
        USER_BIN="$HOME/.local/bin"
        mkdir -p "$USER_BIN"
        cp "$CLI_SOURCE" "$USER_BIN/humanizer"
        chmod +x "$USER_BIN/humanizer"
        
        # Add to PATH if not already there
        if [[ ":$PATH:" != *":$USER_BIN:"* ]]; then
            echo "export PATH=\"$USER_BIN:\$PATH\"" >> ~/.bashrc
            echo "export PATH=\"$USER_BIN:\$PATH\"" >> ~/.zshrc 2>/dev/null || true
            echo "✅ Installed to $USER_BIN"
            echo "⚠️  Restart your shell or run: source ~/.bashrc"
            echo "Test with: humanizer status"
        else
            echo "✅ Installed to $USER_BIN"
            echo "Test with: humanizer status"
        fi
        ;;
    3)
        echo "Adding $SOURCE_DIR to PATH..."
        SHELL_RC=""
        if [ -n "$ZSH_VERSION" ]; then
            SHELL_RC="$HOME/.zshrc"
        elif [ -n "$BASH_VERSION" ]; then
            SHELL_RC="$HOME/.bashrc"
        else
            SHELL_RC="$HOME/.profile"
        fi
        
        if [[ ":$PATH:" != *":$SOURCE_DIR:"* ]]; then
            echo "export PATH=\"$SOURCE_DIR:\$PATH\"" >> "$SHELL_RC"
            echo "✅ Added to PATH in $SHELL_RC"
            echo "⚠️  Restart your shell or run: source $SHELL_RC"
            echo "Test with: $CLI_NAME status"
        else
            echo "✅ Already in PATH"
            echo "Test with: $CLI_NAME status"
        fi
        ;;
    4)
        echo "✅ System checks passed. CLI is ready to use."
        echo "Run with: python3 $CLI_SOURCE status"
        ;;
    *)
        echo "❌ Invalid option"
        exit 1
        ;;
esac

echo ""
echo "🎉 Installation complete!"
echo ""
echo "Next steps:"
echo "1. Start the API server:"
echo "   cd $SOURCE_DIR"
echo "   source venv/bin/activate"
echo "   python api_enhanced.py"
echo ""
echo "2. Test the CLI:"
echo "   humanizer status  # (if installed globally)"
echo "   python3 $CLI_SOURCE status  # (direct usage)"
echo ""
echo "📚 Usage guide: $SOURCE_DIR/CLI_USAGE.md"