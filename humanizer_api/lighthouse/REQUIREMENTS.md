# Humanizer CLI Requirements

## Shell Environment Requirements

### ✅ **Minimal Requirements (Most Users)**
The CLI is designed to work with **system Python** without requiring virtual environments:

```bash
# Only requires system Python 3.7+ with requests library
python3 humanizer_cli.py status
```

### 📋 **System Dependencies**
1. **Python 3.7+** (system installation)
2. **requests library** - Usually pre-installed on macOS via Homebrew

### 🔍 **Check Your System**
```bash
# Verify Python availability
python3 --version
# Should show: Python 3.x.x

# Verify requests library
python3 -c "import requests; print('✅ requests available')"
# Should show: ✅ requests available
```

## Installation Options

### **Option 1: Direct Usage (Recommended)**
If you have Python 3.7+ with requests (most macOS systems):
```bash
# From any directory, just provide the full path
/path/to/humanizer_cli.py status

# Or add to PATH for global access
export PATH="/Users/tem/humanizer-lighthouse/humanizer_api/lighthouse:$PATH"
humanizer_cli.py status
```

### **Option 2: Install Missing Dependencies**
If requests is missing:
```bash
# Install requests globally (requires admin)
sudo pip3 install requests

# Or use Homebrew Python (recommended)
brew install python3
pip3 install requests
```

### **Option 3: Virtual Environment (Development)**
For development or if you want isolated dependencies:
```bash
cd /Users/tem/humanizer-lighthouse/humanizer_api/lighthouse
source venv/bin/activate
python humanizer_cli.py status
```

## Current System Status

### ✅ **Your System (macOS with Homebrew)**
- Python 3.13.5 available at `/opt/homebrew/bin/python3`
- Requests 2.32.4 already installed
- **CLI works immediately** without virtual environment

### 🛠️ **Server Requirements**
The CLI is just a client. The server requires the full environment:
```bash
# Start the Enhanced API server (requires venv)
cd /Users/tem/humanizer-lighthouse/humanizer_api/lighthouse
source venv/bin/activate
python api_enhanced.py
```

## Usage Patterns

### **Casual Usage**
```bash
# Works from any directory with system Python
python3 /path/to/humanizer_cli.py transform --text "Hello world"
```

### **Development Usage**
```bash
# If working on the codebase
cd /Users/tem/humanizer-lighthouse/humanizer_api/lighthouse
source venv/bin/activate  # Only needed for server
python humanizer_cli.py status
```

### **System Integration**
```bash
# Add to shell profile for global access
echo 'export PATH="/Users/tem/humanizer-lighthouse/humanizer_api/lighthouse:$PATH"' >> ~/.zshrc
source ~/.zshrc

# Now works globally
humanizer_cli.py status
```

## Cross-Platform Compatibility

### **macOS** ✅
- Homebrew Python includes requests
- System Python works out of the box
- Full keychain integration available

### **Linux** ⚠️
```bash
# May need to install requests
sudo apt-get install python3-requests  # Ubuntu/Debian
sudo yum install python3-requests      # RHEL/CentOS

# Then works normally
python3 humanizer_cli.py status
```

### **Windows** ⚠️
```bash
# Install Python from python.org
# Install requests
pip install requests

# Use with py launcher
py humanizer_cli.py status
```

## CLI vs Server Dependencies

### **CLI Dependencies (Minimal)**
- Python 3.7+
- requests library
- Standard library modules (json, sys, argparse, pathlib)

### **Server Dependencies (Full Environment)**
- All CLI dependencies plus:
- sentence-transformers
- faiss-cpu
- psycopg2
- chromadb
- fastapi
- uvicorn
- And 20+ other packages

## Troubleshooting

### **ImportError: No module named 'requests'**
```bash
# Solution 1: Install requests
pip3 install requests

# Solution 2: Use system package manager
brew install python3  # macOS
sudo apt install python3-requests  # Ubuntu
```

### **Permission Denied**
```bash
# Make CLI executable
chmod +x humanizer_cli.py

# Or use python3 explicitly
python3 humanizer_cli.py status
```

### **API Connection Failed**
```bash
# Check if server is running
curl http://127.0.0.1:8100/health

# Start server if needed
cd /path/to/lighthouse
source venv/bin/activate
python api_enhanced.py
```

## Summary

**✅ For most users**: The CLI works immediately with system Python  
**🔧 For developers**: Use the virtual environment for server development  
**🌍 For deployment**: Single-file CLI with minimal dependencies  

The CLI is designed to be **lightweight and portable** - it's just a REST API client that requires minimal system dependencies while the heavy processing happens server-side.