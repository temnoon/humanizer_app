#!/bin/bash

echo "🔄 Manual Server Restart with Visible Output..."

# Kill existing processes
echo "🛑 Stopping existing servers..."
lsof -ti:3100 | xargs kill -9 2>/dev/null || true
lsof -ti:7200 | xargs kill -9 2>/dev/null || true  
lsof -ti:8100 | xargs kill -9 2>/dev/null || true

sleep 3

echo ""
echo "🚀 Starting servers with visible output..."
echo ""

# Start Archive Server
echo "📁 Starting Archive Upload Server..."
cd /Users/tem/humanizer-lighthouse/humanizer_api/lighthouse
source venv/bin/activate
cd /Users/tem/humanizer-lighthouse  
python archive_upload_server.py &
ARCHIVE_PID=$!

sleep 3

# Start Lighthouse API
echo "⚡ Starting Enhanced Lighthouse API..."
cd /Users/tem/humanizer-lighthouse/humanizer_api/lighthouse
source venv/bin/activate
python api_enhanced.py &
LIGHTHOUSE_PID=$!

sleep 3

# Start Frontend
echo "🎨 Starting Frontend..."
cd /Users/tem/humanizer-lighthouse/lighthouse-ui
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ All servers started!"
echo "📝 PIDs: Archive=$ARCHIVE_PID, Lighthouse=$LIGHTHOUSE_PID, Frontend=$FRONTEND_PID"
echo ""
echo "🌐 Access the app at: http://127.0.0.1:3100/"
echo ""
echo "Press Ctrl+C to stop all servers"

# Wait for user interrupt
wait