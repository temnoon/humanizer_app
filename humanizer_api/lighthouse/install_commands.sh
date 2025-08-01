#!/bin/bash
"""
Humanizer Lighthouse Command Installation
========================================
Install CLI commands globally for easy access from anywhere
"""

# Get the current directory (should be lighthouse directory)
LIGHTHOUSE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="$LIGHTHOUSE_DIR/venv"
BIN_DIR="/usr/local/bin"

echo "🏗️  Installing Humanizer Lighthouse Commands"
echo "   Lighthouse Directory: $LIGHTHOUSE_DIR"
echo "   Virtual Environment: $VENV_PATH"
echo "   Installing to: $BIN_DIR"

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

# 4. Batch Processing CLI (new)
cat > "$BIN_DIR/humanizer-batch" << EOF
#!/bin/bash
cd "$LIGHTHOUSE_DIR"
source venv/bin/activate
python batch_curator.py "\$@"
EOF

# 5. Book Builder CLI (new)
cat > "$BIN_DIR/humanizer-books" << EOF
#!/bin/bash
cd "$LIGHTHOUSE_DIR"
source venv/bin/activate
python book_builder.py "\$@"
EOF

# 6. Essay Publisher CLI (new)
cat > "$BIN_DIR/humanizer-publish" << EOF
#!/bin/bash
cd "$LIGHTHOUSE_DIR"
source venv/bin/activate
python essay_publisher.py "\$@"
EOF

# Make all scripts executable
chmod +x "$BIN_DIR/humanizer-archive"
chmod +x "$BIN_DIR/humanizer-process"
chmod +x "$BIN_DIR/humanizer-transform"
chmod +x "$BIN_DIR/humanizer-batch"
chmod +x "$BIN_DIR/humanizer-books"
chmod +x "$BIN_DIR/humanizer-publish"

echo "✅ Installed Commands:"
echo "   📁 humanizer-archive    - Archive discovery and retrieval"
echo "   🔄 humanizer-process    - Intelligent processing workflows"
echo "   🎭 humanizer-transform  - Direct allegory transformations"
echo "   📦 humanizer-batch      - Batch curation and essay creation"
echo "   📚 humanizer-books      - Book compilation from essays"
echo "   🌐 humanizer-publish    - Essay publishing to Discourse"
echo ""
echo "🎯 Quick Start:"
echo "   humanizer-archive discover --search 'quantum' --limit 10"
echo "   humanizer-process workflow 'consciousness' --auto-process"
echo "   humanizer-batch curate --topic 'philosophy' --max-essays 20"
echo "   humanizer-books compile --subject 'Modern Physics' --auto-chapters"
echo ""
echo "📚 Documentation:"
echo "   Each command supports --help for detailed usage"
echo "   See INTELLIGENT_PROCESSING_SYSTEM.md for full workflow documentation"