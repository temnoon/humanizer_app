#!/bin/bash
"""
Humanizer Lighthouse Local Installation
======================================
Install CLI commands in ~/bin for easy access from anywhere
"""

# Get the current directory (should be lighthouse directory)
LIGHTHOUSE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="$LIGHTHOUSE_DIR/venv"
BIN_DIR="$HOME/bin"

echo "🏗️  Installing Humanizer Lighthouse Commands (Local)"
echo "   Lighthouse Directory: $LIGHTHOUSE_DIR"
echo "   Virtual Environment: $VENV_PATH"
echo "   Installing to: $BIN_DIR"

# Create bin directory if it doesn't exist
mkdir -p "$BIN_DIR"

# Check if virtual environment exists
if [ ! -d "$VENV_PATH" ]; then
    echo "❌ Virtual environment not found at $VENV_PATH"
    echo "   Run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Create wrapper scripts for each command

# 1. Archive CLI
cat > "$BIN_DIR/humanizer-archive" << EOF
#!/bin/bash
cd "$LIGHTHOUSE_DIR"
source venv/bin/activate
python archive_cli.py "\$@"
EOF

# 2. Integrated Processing CLI
cat > "$BIN_DIR/humanizer-process" << EOF
#!/bin/bash
cd "$LIGHTHOUSE_DIR"
source venv/bin/activate
python integrated_processing_cli.py "\$@"
EOF

# 3. Enhanced Humanizer CLI
cat > "$BIN_DIR/humanizer-transform" << EOF
#!/bin/bash
cd "$LIGHTHOUSE_DIR"
source venv/bin/activate
python humanizer_cli.py "\$@"
EOF

# 4. Batch Processing CLI
cat > "$BIN_DIR/humanizer-batch" << EOF
#!/bin/bash
cd "$LIGHTHOUSE_DIR"
source venv/bin/activate
python batch_curator.py "\$@"
EOF

# 5. Book Builder CLI
cat > "$BIN_DIR/humanizer-books" << EOF
#!/bin/bash
cd "$LIGHTHOUSE_DIR"
source venv/bin/activate
python book_builder.py "\$@"
EOF

# Make all scripts executable
chmod +x "$BIN_DIR/humanizer-archive"
chmod +x "$BIN_DIR/humanizer-process" 
chmod +x "$BIN_DIR/humanizer-transform"
chmod +x "$BIN_DIR/humanizer-batch"
chmod +x "$BIN_DIR/humanizer-books"

echo "✅ Installed Commands in ~/bin:"
echo "   📁 humanizer-archive    - Archive discovery and retrieval"
echo "   🔄 humanizer-process    - Intelligent processing workflows"
echo "   🎭 humanizer-transform  - Direct allegory transformations"
echo "   📦 humanizer-batch      - Batch curation and essay creation"
echo "   📚 humanizer-books      - Book compilation from essays"
echo ""

# Check if ~/bin is in PATH
if [[ ":$PATH:" != *":$HOME/bin:"* ]]; then
    echo "⚠️  Add ~/bin to your PATH to use commands from anywhere:"
    echo "   echo 'export PATH=\"\$HOME/bin:\$PATH\"' >> ~/.zshrc"
    echo "   source ~/.zshrc"
    echo ""
fi

echo "🎯 Quick Start:"
echo "   humanizer-archive discover --search 'quantum' --limit 10"
echo "   humanizer-batch curate --topic 'consciousness' --max-essays 15"
echo "   humanizer-books build 'philosophy' --max-chapters 8"
echo ""
echo "📚 Complete Guide: COMPLETE_WORKFLOW_GUIDE.md"