#!/bin/bash
set -e

echo "🧹 Cleaning up any existing processes..."
lsof -ti:7200 | xargs kill -9 2>/dev/null || true

echo "📁 Navigating to lighthouse directory..."
cd /Users/tem/humanizer-lighthouse/humanizer_api/lighthouse

echo "🐍 Activating lighthouse venv..."
source venv/bin/activate

echo "📦 Checking python-multipart installation..."
pip install python-multipart --upgrade

echo "🔍 Testing imports..."
python -c "
import sys
print(f'Python: {sys.executable}')
try:
    import fastapi
    print('✅ FastAPI available')
except Exception as e:
    print(f'❌ FastAPI error: {e}')
    exit(1)

try:
    # Test the actual import that FastAPI uses internally
    import multipart
    print('✅ multipart available')
except Exception as e:
    print(f'❌ multipart error: {e}')
    # Try alternative import
    try:
        import python_multipart
        print('✅ python_multipart available as fallback')
    except Exception as e2:
        print(f'❌ python_multipart error: {e2}')
        exit(1)
"

echo "🚀 Starting archive upload server..."
python /Users/tem/humanizer-lighthouse/archive_upload_server.py