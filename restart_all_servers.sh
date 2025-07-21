#!/bin/bash

echo "🔄 Restarting All Lighthouse Servers..."

# Kill all existing processes
echo "🛑 Killing existing servers..."
lsof -ti:3100 | xargs kill -9 2>/dev/null || true
lsof -ti:7200 | xargs kill -9 2>/dev/null || true
lsof -ti:8100 | xargs kill -9 2>/dev/null || true

# Wait a moment for processes to clean up
sleep 2

echo "🚀 Starting servers..."

# Start Archive Upload Server (port 7200)
echo "📁 Starting Archive Upload Server on port 7200..."
cd /Users/tem/humanizer-lighthouse/humanizer_api/lighthouse
source venv/bin/activate
cd /Users/tem/humanizer-lighthouse
nohup python archive_upload_server.py > archive_server.log 2>&1 &
ARCHIVE_PID=$!
echo "   Archive Server PID: $ARCHIVE_PID"

# Wait a moment
sleep 3

# Start Enhanced Lighthouse API (port 8100)
echo "⚡ Starting Enhanced Lighthouse API on port 8100..."
cd /Users/tem/humanizer-lighthouse/humanizer_api/lighthouse
source venv/bin/activate
nohup python api_enhanced.py > lighthouse_api.log 2>&1 &
LIGHTHOUSE_PID=$!
echo "   Lighthouse API PID: $LIGHTHOUSE_PID"

# Wait a moment
sleep 3

# Start Frontend (port 3100)
echo "🎨 Starting Frontend on port 3100..."
cd /Users/tem/humanizer-lighthouse/lighthouse-ui
nohup npm run dev > frontend.log 2>&1 &
FRONTEND_PID=$!
echo "   Frontend PID: $FRONTEND_PID"

# Wait a moment for servers to start
sleep 5

echo ""
echo "✅ Server Status Check:"
echo "---------------------"

# Check if servers are running
if lsof -i :7200 >/dev/null 2>&1; then
    echo "✅ Archive Server (7200): RUNNING"
else
    echo "❌ Archive Server (7200): FAILED"
fi

if lsof -i :8100 >/dev/null 2>&1; then
    echo "✅ Lighthouse API (8100): RUNNING"
else
    echo "❌ Lighthouse API (8100): FAILED"
fi

if lsof -i :3100 >/dev/null 2>&1; then
    echo "✅ Frontend (3100): RUNNING"
else
    echo "❌ Frontend (3100): FAILED"
fi

echo ""
echo "🌐 Access URLs:"
echo "   Frontend:     http://127.0.0.1:3100/"
echo "   Archive API:  http://127.0.0.1:7200/"
echo "   Lighthouse:   http://127.0.0.1:8100/"
echo ""
echo "📋 Log files:"
echo "   Archive:      /Users/tem/humanizer-lighthouse/archive_server.log"
echo "   Lighthouse:   /Users/tem/humanizer-lighthouse/humanizer_api/lighthouse/lighthouse_api.log"
echo "   Frontend:     /Users/tem/humanizer-lighthouse/lighthouse-ui/frontend.log"
echo ""
echo "🎯 All servers started in detached mode!"