#!/bin/bash

echo "🔄 Restarting Humanizer Lighthouse Platform..."

# Function to kill processes on specific ports
kill_port() {
    local port=$1
    local name=$2
    echo "🛑 Stopping $name on port $port..."
    
    # Find and kill processes on the port
    pids=$(lsof -ti:$port 2>/dev/null)
    if [ ! -z "$pids" ]; then
        echo "$pids" | xargs kill -9
        echo "✅ Killed processes: $pids"
    else
        echo "ℹ️  No processes found on port $port"
    fi
}

# Kill all known services
echo "🧹 Cleaning up existing processes..."
kill_port 3100 "Frontend Dev Server"
kill_port 3101 "Frontend Dev Server (Alt)"
kill_port 8100 "Enhanced Lighthouse API"
kill_port 9000 "Rails GUI Server"
kill_port 7200 "Archive API"
kill_port 7201 "LPE API"

# Wait a moment for processes to cleanup
sleep 2

echo ""
echo "🚀 Starting services..."

# Start Rails GUI Server
echo "📱 Starting Rails GUI Server on port 9000..."
cd /Users/tem/humanizer-lighthouse/humanizer_rails
export RAILS_ENV=development
export PORT=9000

# Precompile assets first
echo "🎨 Precompiling assets..."
bundle exec rails assets:precompile

# Start Rails server in background
nohup bundle exec rails server -p 9000 > logs/rails_server.log 2>&1 &
RAILS_PID=$!
echo "✅ Rails GUI started (PID: $RAILS_PID)"

# Start Enhanced Lighthouse API
echo "🔬 Starting Enhanced Lighthouse API on port 8100..."
cd /Users/tem/humanizer-lighthouse/humanizer_api/lighthouse
source venv/bin/activate

# Start API in background
nohup python api_enhanced.py > logs/api_enhanced.log 2>&1 &
API_PID=$!
echo "✅ Enhanced API started (PID: $API_PID)"

# Start Frontend Dev Server
echo "🎨 Starting Frontend Dev Server on port 3100..."
cd /Users/tem/humanizer-lighthouse/lighthouse-ui

# Start frontend in background
nohup npm run dev > logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "✅ Frontend started (PID: $FRONTEND_PID)"

echo ""
echo "🎉 All services started!"
echo ""
echo "📋 Service URLs:"
echo "   🖥️  Rails GUI:        http://localhost:9000"
echo "   🎨 Frontend:         http://localhost:3100"
echo "   🔬 Enhanced API:     http://localhost:8100"
echo ""
echo "📁 Logs:"
echo "   Rails:   /Users/tem/humanizer-lighthouse/humanizer_rails/logs/rails_server.log"
echo "   API:     /Users/tem/humanizer-lighthouse/humanizer_api/lighthouse/logs/api_enhanced.log"
echo "   Frontend: /Users/tem/humanizer-lighthouse/lighthouse-ui/logs/frontend.log"
echo ""
echo "🛑 To stop all services: ./stop_all.sh"
echo ""

# Save PIDs for stopping later
echo "$RAILS_PID" > /tmp/humanizer_rails.pid
echo "$API_PID" > /tmp/humanizer_api.pid  
echo "$FRONTEND_PID" > /tmp/humanizer_frontend.pid