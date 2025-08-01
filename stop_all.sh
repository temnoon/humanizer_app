#!/bin/bash

echo "🛑 Stopping all Humanizer Lighthouse services..."

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

# Kill by PID if available
if [ -f "/tmp/humanizer_rails.pid" ]; then
    RAILS_PID=$(cat /tmp/humanizer_rails.pid)
    echo "🛑 Stopping Rails server (PID: $RAILS_PID)..."
    kill -9 $RAILS_PID 2>/dev/null
    rm /tmp/humanizer_rails.pid
fi

if [ -f "/tmp/humanizer_api.pid" ]; then
    API_PID=$(cat /tmp/humanizer_api.pid)
    echo "🛑 Stopping API server (PID: $API_PID)..."
    kill -9 $API_PID 2>/dev/null
    rm /tmp/humanizer_api.pid
fi

if [ -f "/tmp/humanizer_frontend.pid" ]; then
    FRONTEND_PID=$(cat /tmp/humanizer_frontend.pid)
    echo "🛑 Stopping Frontend server (PID: $FRONTEND_PID)..."
    kill -9 $FRONTEND_PID 2>/dev/null
    rm /tmp/humanizer_frontend.pid
fi

# Also kill by port as backup
kill_port 9000 "Rails GUI Server"
kill_port 3100 "Frontend Dev Server"
kill_port 3101 "Frontend Dev Server (Alt)"
kill_port 8100 "Enhanced Lighthouse API"
kill_port 7200 "Archive API"
kill_port 7201 "LPE API"

echo "✅ All services stopped!"