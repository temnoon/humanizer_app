#!/bin/bash

# Humanizer Lighthouse - Complete System Startup Script
# Usage: ./start.sh

echo "🌟 Starting Humanizer Lighthouse Platform"
echo "=========================================="

# Check if we're in the right directory
if [ ! -d "humanizer_api" ] || [ ! -d "lighthouse-ui" ]; then
    echo "❌ Error: Run this script from the humanizer-lighthouse root directory"
    echo "   Current: $(pwd)"
    echo "   Expected: /Users/tem/humanizer-lighthouse"
    exit 1
fi

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Check and kill existing processes
echo "🔧 Checking for existing processes..."

if check_port 8100; then
    echo "⚠️  Port 8100 in use, killing existing backend..."
    lsof -ti:8100 | xargs kill -9 2>/dev/null || true
    sleep 2
fi

if check_port 3100; then
    echo "⚠️  Port 3100 in use, killing existing frontend..."
    lsof -ti:3100 | xargs kill -9 2>/dev/null || true
    sleep 2
fi

if check_port 3101; then
    echo "⚠️  Port 3101 in use, killing existing frontend..."
    lsof -ti:3101 | xargs kill -9 2>/dev/null || true
    sleep 2
fi

# Start Backend
echo ""
echo "🐍 Starting Python Backend (Port 8100)"
echo "======================================"

cd humanizer_api/lighthouse

# Check Python environment
if [ ! -d "venv" ]; then
    echo "❌ Error: venv not found in lighthouse directory"
    echo "   Expected: humanizer_api/lighthouse/venv/"
    exit 1
fi

# Start backend in background
echo "🔄 Activating Python environment and starting API..."
source venv/bin/activate

# Check Python version
python_version=$(python --version 2>&1)
echo "✅ Using: $python_version"

# Start the API in background and capture PID
python api_enhanced.py &
BACKEND_PID=$!

# Wait a moment for server to start
sleep 3

# Check if backend started successfully
if kill -0 $BACKEND_PID 2>/dev/null; then
    echo "✅ Backend started successfully (PID: $BACKEND_PID)"
    echo "   URL: http://127.0.0.1:8100"
    echo "   API Docs: http://127.0.0.1:8100/docs"
else
    echo "❌ Backend failed to start"
    exit 1
fi

# Return to root directory
cd ../..

# Start Frontend
echo ""
echo "⚛️  Starting React Frontend (Port 3100/3101)"
echo "==========================================="

cd lighthouse-ui

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing Node dependencies..."
    npm install
fi

# Start frontend in background
echo "🔄 Starting Vite development server..."
npm run dev &
FRONTEND_PID=$!

# Wait for frontend to start
sleep 5

# Check if frontend started
if kill -0 $FRONTEND_PID 2>/dev/null; then
    echo "✅ Frontend started successfully (PID: $FRONTEND_PID)"
    
    # Determine which port was used
    if check_port 3100; then
        echo "   URL: http://127.0.0.1:3100"
    elif check_port 3101; then
        echo "   URL: http://127.0.0.1:3101"
    else
        echo "   URL: Check terminal output for assigned port"
    fi
else
    echo "❌ Frontend failed to start"
    # Kill backend if frontend failed
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

# Return to root
cd ..

# Create PID file for shutdown script
echo "$BACKEND_PID" > .backend.pid
echo "$FRONTEND_PID" > .frontend.pid

echo ""
echo "🎉 Humanizer Lighthouse Platform Started Successfully!"
echo "===================================================="
echo "📱 Frontend:  http://127.0.0.1:3100 (or 3101)"
echo "🔧 Backend:   http://127.0.0.1:8100"
echo "📚 API Docs:  http://127.0.0.1:8100/docs"
echo ""
echo "💡 To stop the services: ./stop.sh"
echo "📋 To check status: ./status.sh"
echo ""
echo "🔍 Logs:"
echo "   Backend:  Check terminal where script was run"
echo "   Frontend: Check terminal where script was run"
echo ""
echo "Press Ctrl+C to stop both services, or run ./stop.sh"

# Keep script running and wait for Ctrl+C
trap 'echo -e "\n👋 Stopping services..."; ./stop.sh; exit 0' INT

# Keep the script alive
wait