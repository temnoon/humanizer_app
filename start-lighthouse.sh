#!/bin/bash

echo "🚀 Starting Lighthouse UI with secure API key management..."

# Kill any existing processes
echo "Cleaning up existing processes..."
pkill -f api_enhanced.py 2>/dev/null || true
pkill -f vite 2>/dev/null || true
sleep 2

# Start backend
echo "Starting backend on port 8100..."
cd /Users/tem/humanizer-lighthouse/humanizer_api/lighthouse
source venv/bin/activate
python api_enhanced.py &
BACKEND_PID=$!
echo "Backend started with PID: $BACKEND_PID"

# Wait for backend to be ready
echo "Waiting for backend to start..."
sleep 5

# Test backend
if curl -s http://127.0.0.1:8100/health > /dev/null; then
    echo "✅ Backend is responding"
else
    echo "❌ Backend failed to start"
    exit 1
fi

# Start frontend
echo "Starting frontend on port 3100..."
cd /Users/tem/humanizer-lighthouse/lighthouse-ui

# Clean install to fix any dependency issues
echo "Refreshing dependencies..."
rm -rf node_modules/.vite 2>/dev/null || true

npm run dev &
FRONTEND_PID=$!
echo "Frontend started with PID: $FRONTEND_PID"

echo "
🎉 Lighthouse UI started successfully!

📍 Access URLs:
   Frontend: http://127.0.0.1:3100
   Backend:  http://127.0.0.1:8100

🔑 Features available:
   ✅ 11 LLM providers with secure keychain storage
   ✅ Comprehensive API key management
   ✅ Per-task LLM configuration
   ✅ Real-time provider testing

⚠️  Security: Localhost only (no network access)

To stop: pkill -f 'api_enhanced.py|vite'
"

# Keep script running to show status
wait