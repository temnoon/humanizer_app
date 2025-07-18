#!/bin/bash

# Humanizer Lighthouse - System Status Check Script
# Usage: ./status.sh

echo "📊 Humanizer Lighthouse Platform Status"
echo "======================================="

# Function to check if port is in use and get PID
check_port_status() {
    local port=$1
    local service=$2
    
    local pid=$(lsof -ti:$port 2>/dev/null)
    if [ -n "$pid" ]; then
        local process_info=$(ps -p $pid -o comm= 2>/dev/null)
        echo "✅ $service: Running on port $port (PID: $pid, Process: $process_info)"
        return 0
    else
        echo "❌ $service: Not running on port $port"
        return 1
    fi
}

# Function to test HTTP endpoint
test_endpoint() {
    local url=$1
    local name=$2
    
    if curl -s --max-time 5 "$url" >/dev/null 2>&1; then
        echo "✅ $name: Responding at $url"
        return 0
    else
        echo "❌ $name: Not responding at $url"
        return 1
    fi
}

echo ""
echo "🔌 Port Status"
echo "=============="

backend_running=false
frontend_running=false

# Check backend port
if check_port_status 8100 "Backend API"; then
    backend_running=true
fi

# Check frontend ports
if check_port_status 3100 "Frontend"; then
    frontend_running=true
elif check_port_status 3101 "Frontend (Alt)"; then
    frontend_running=true
fi

echo ""
echo "🌐 Service Health Checks"
echo "========================"

# Test backend endpoints
if $backend_running; then
    test_endpoint "http://127.0.0.1:8100/health" "Backend Health"
    test_endpoint "http://127.0.0.1:8100/docs" "API Documentation"
    test_endpoint "http://127.0.0.1:8100/configurations" "Configurations Endpoint"
else
    echo "⏸️  Backend not running - skipping health checks"
fi

# Test frontend
if $frontend_running; then
    if curl -s --max-time 5 "http://127.0.0.1:3100/" >/dev/null 2>&1; then
        echo "✅ Frontend: Responding at http://127.0.0.1:3100"
    elif curl -s --max-time 5 "http://127.0.0.1:3101/" >/dev/null 2>&1; then
        echo "✅ Frontend: Responding at http://127.0.0.1:3101"
    else
        echo "❌ Frontend: Port open but not responding to HTTP"
    fi
else
    echo "⏸️  Frontend not running - skipping health checks"
fi

echo ""
echo "🔍 Process Details"
echo "=================="

# Check for API processes
echo "🐍 Python API Processes:"
api_procs=$(ps aux | grep "api_enhanced.py" | grep -v grep)
if [ -n "$api_procs" ]; then
    echo "$api_procs" | while read line; do
        echo "   $line"
    done
else
    echo "   No API processes found"
fi

echo ""
echo "⚛️  Node/Frontend Processes:"
node_procs=$(ps aux | grep -E "(vite|npm run dev)" | grep lighthouse-ui | grep -v grep)
if [ -n "$node_procs" ]; then
    echo "$node_procs" | while read line; do
        echo "   $line"
    done
else
    echo "   No frontend processes found"
fi

echo ""
echo "📁 PID Files"
echo "============"

if [ -f ".backend.pid" ]; then
    backend_pid=$(cat .backend.pid)
    if kill -0 $backend_pid 2>/dev/null; then
        echo "✅ Backend PID file: $backend_pid (process running)"
    else
        echo "⚠️  Backend PID file: $backend_pid (process not running)"
    fi
else
    echo "ℹ️  No backend PID file"
fi

if [ -f ".frontend.pid" ]; then
    frontend_pid=$(cat .frontend.pid)
    if kill -0 $frontend_pid 2>/dev/null; then
        echo "✅ Frontend PID file: $frontend_pid (process running)"
    else
        echo "⚠️  Frontend PID file: $frontend_pid (process not running)"
    fi
else
    echo "ℹ️  No frontend PID file"
fi

echo ""
echo "🎯 Summary"
echo "=========="

if $backend_running && $frontend_running; then
    echo "🎉 Status: FULLY OPERATIONAL"
    echo "📱 Frontend: http://127.0.0.1:3100 (or 3101)"
    echo "🔧 Backend:  http://127.0.0.1:8100"
    echo "📚 API Docs: http://127.0.0.1:8100/docs"
elif $backend_running; then
    echo "⚠️  Status: BACKEND ONLY"
    echo "🔧 Backend:  http://127.0.0.1:8100"
    echo "💡 Start frontend: cd lighthouse-ui && npm run dev"
elif $frontend_running; then
    echo "⚠️  Status: FRONTEND ONLY"
    echo "📱 Frontend: http://127.0.0.1:3100 (or 3101)"
    echo "💡 Start backend: cd humanizer_api/lighthouse && source venv/bin/activate && python api_enhanced.py"
else
    echo "❌ Status: NOT RUNNING"
    echo "💡 Start both: ./start.sh"
fi

echo ""
echo "🛠️  Available Commands"
echo "====================="
echo "./start.sh   - Start both services"
echo "./stop.sh    - Stop both services"
echo "./status.sh  - Show this status (current command)"

# If services are partially running, offer specific guidance
if $backend_running && ! $frontend_running; then
    echo ""
    echo "🔧 Quick Fix: Start frontend only"
    echo "   cd lighthouse-ui && npm run dev"
elif ! $backend_running && $frontend_running; then
    echo ""
    echo "🔧 Quick Fix: Start backend only"
    echo "   cd humanizer_api/lighthouse && source venv/bin/activate && python api_enhanced.py"
fi