#!/bin/bash

# Lighthouse API Startup Script

echo "🔦 Starting Humanizer Lighthouse API..."

# Find a stable Python version (3.12 or 3.11) to avoid build issues.
if command -v python3.12 &> /dev/null; then
    PYTHON_EXEC="python3.12"
elif command -v python3.11 &> /dev/null; then
    PYTHON_EXEC="python3.11"
else
    echo "❌ Could not find Python 3.12 or 3.11. Please install one to ensure dependency compatibility."
    exit 1
fi
echo "✅ Using Python executable: $PYTHON_EXEC"


# Check if virtual environment exists and was created with a compatible Python
VENV_PYTHON_EXEC="venv/bin/python"
if [ ! -d "venv" ] || ! $VENV_PYTHON_EXEC -c "import sys; assert sys.version_info.major == 3 and sys.version_info.minor in (11, 12)" &>/dev/null; then
    echo "Re-creating virtual environment with $PYTHON_EXEC to ensure compatibility..."
    rm -rf venv
    $PYTHON_EXEC -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/update requirements
echo "Installing dependencies..."
pip install -r requirements.txt

# The transformer model requires this specific library.
# We install it here explicitly to ensure it's present.
pip install spacy-transformers==1.3.4

# Download the spaCy transformer model for NLP tasks.
# This command is idempotent; it won't re-download if the model already exists.
echo "Downloading NLP model (en_core_web_trf)..."
python -m spacy download en_core_web_trf

# Check for .env file
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your API keys!"
fi

# Start the API
echo "Starting API on port 8100..."
python api.py
