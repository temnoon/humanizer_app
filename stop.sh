#!/bin/bash

# Humanizer Lighthouse - Complete System Shutdown Script
# Usage: ./stop.sh

echo "🛑 Stopping Humanizer Lighthouse Platform"
echo "=========================================="

# Function to safely kill process
safe_kill() {
    local pid=$1
    local name=$2
    
    if [ -n "$pid" ] && kill -0 $pid 2>/dev/null; then
        echo "🔄 Stopping $name (PID: $pid)..."
        kill $pid 2>/dev/null
        
        # Wait up to 10 seconds for graceful shutdown
        for i in {1..10}; do
            if ! kill -0 $pid 2>/dev/null; then
                echo "✅ $name stopped gracefully"
                return 0
            fi
            sleep 1
        done
        
        # Force kill if still running
        echo "⚠️  Force stopping $name..."
        kill -9 $pid 2>/dev/null
        
        if ! kill -0 $pid 2>/dev/null; then
            echo "✅ $name force stopped"
        else
            echo "❌ Failed to stop $name"
        fi
    else
        echo "ℹ️  $name not running (PID: $pid)"
    fi
}

# Function to kill by port
kill_by_port() {
    local port=$1
    local name=$2
    
    local pids=$(lsof -ti:$port 2>/dev/null)
    if [ -n "$pids" ]; then
        echo "🔄 Killing processes on port $port ($name)..."
        echo "$pids" | xargs kill -9 2>/dev/null || true
        echo "✅ Processes on port $port stopped"
    else
        echo "ℹ️  No processes running on port $port ($name)"
    fi
}

# Stop services using PID files if they exist
if [ -f ".backend.pid" ]; then
    BACKEND_PID=$(cat .backend.pid)
    safe_kill "$BACKEND_PID" "Backend API"
    rm -f .backend.pid
else
    echo "ℹ️  No backend PID file found"
fi

if [ -f ".frontend.pid" ]; then
    FRONTEND_PID=$(cat .frontend.pid)
    safe_kill "$FRONTEND_PID" "Frontend Dev Server"
    rm -f .frontend.pid
else
    echo "ℹ️  No frontend PID file found"
fi

echo ""
echo "🔧 Cleaning up ports..."

# Kill any remaining processes on our ports
kill_by_port 8100 "Backend"
kill_by_port 3100 "Frontend"
kill_by_port 3101 "Frontend Alt"

# Kill any remaining Python processes that might be our API
echo ""
echo "🐍 Checking for remaining Python API processes..."
api_pids=$(ps aux | grep "api_enhanced.py" | grep -v grep | awk '{print $2}')
if [ -n "$api_pids" ]; then
    echo "🔄 Stopping remaining API processes..."
    echo "$api_pids" | xargs kill -9 2>/dev/null || true
    echo "✅ API processes stopped"
else
    echo "ℹ️  No API processes found"
fi

# Kill any remaining npm/node processes for our frontend
echo ""
echo "⚛️  Checking for remaining Node processes..."
node_pids=$(ps aux | grep "vite\|npm run dev" | grep lighthouse-ui | grep -v grep | awk '{print $2}')
if [ -n "$node_pids" ]; then
    echo "🔄 Stopping remaining Node processes..."
    echo "$node_pids" | xargs kill -9 2>/dev/null || true
    echo "✅ Node processes stopped"
else
    echo "ℹ️  No Node processes found"
fi

echo ""
echo "🔍 Final status check..."

# Check if ports are now free
for port in 8100 3100 3101; do
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "⚠️  Port $port still in use"
    else
        echo "✅ Port $port is free"
    fi
done

echo ""
echo "🎉 Humanizer Lighthouse Platform Stopped"
echo "========================================"
echo ""
echo "💡 To restart: ./start.sh"
echo "📋 To check if anything is still running: ./status.sh"