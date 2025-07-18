#!/bin/bash
# start_humanizer_api.sh - Launch the complete Humanizer API ecosystem

echo "🚀 Starting Humanizer API Ecosystem..."
echo "======================================"

# Source environment if it exists
if [ -f ".env" ]; then
    set -a
    source .env
    set +a
    echo "✅ Environment variables loaded"
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run ./setup.sh first"
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check if APIs are already running
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to start service in background
start_service() {
    local name=$1
    local script=$2
    local port=$3
    local log_file="logs/${name}.log"
    
    if check_port $port; then
        echo "⚠️  $name already running on port $port"
    else
        echo "🚀 Starting $name on port $port..."
        cd src
        python $script > "../$log_file" 2>&1 &
        local pid=$!
        cd ..
        echo $pid > "logs/${name}.pid"
        sleep 2
        
        if check_port $port; then
            echo "✅ $name started successfully (PID: $pid)"
        else
            echo "❌ $name failed to start (check $log_file)"
            return 1
        fi
    fi
    return 0
}

# Create logs directory
mkdir -p logs

# Start Archive API
start_service "archive_api" "archive_api.py" "${ARCHIVE_API_PORT:-7200}"
if [ $? -ne 0 ]; then
    echo "❌ Failed to start Archive API"
    exit 1
fi

# Start LPE API
start_service "lpe_api" "lpe_api.py" "${LPE_API_PORT:-7201}"
if [ $? -ne 0 ]; then
    echo "❌ Failed to start LPE API"
    exit 1
fi

# Wait a moment for services to fully initialize
sleep 3

# Test API connectivity
echo ""
echo "🔍 Testing API connectivity..."

# Test Archive API
if curl -s "http://localhost:${ARCHIVE_API_PORT:-7200}/health" > /dev/null; then
    echo "✅ Archive API is healthy"
else
    echo "❌ Archive API health check failed"
fi

# Test LPE API
if curl -s "http://localhost:${LPE_API_PORT:-7201}/health" > /dev/null; then
    echo "✅ LPE API is healthy"
else
    echo "❌ LPE API health check failed"
fi

echo ""
echo "🎉 Humanizer API Ecosystem is running!"
echo "====================================="
echo "📚 Archive API:     http://localhost:${ARCHIVE_API_PORT:-7200}"
echo "🧠 LPE API:         http://localhost:${LPE_API_PORT:-7201}"
echo ""
echo "📖 API Documentation:"
echo "   Archive API docs: http://localhost:${ARCHIVE_API_PORT:-7200}/docs"
echo "   LPE API docs:     http://localhost:${LPE_API_PORT:-7201}/docs"
echo ""
echo "📊 Health Checks:"
echo "   Archive health:   http://localhost:${ARCHIVE_API_PORT:-7200}/health"
echo "   LPE health:       http://localhost:${LPE_API_PORT:-7201}/health"
echo ""
echo "📝 Logs:"
echo "   Archive API:      logs/archive_api.log"
echo "   LPE API:          logs/lpe_api.log"
echo ""
echo "🛑 To stop all services: ./stop_humanizer_api.sh"
echo ""
echo "Press Ctrl+C to view logs in real-time..."

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down services..."
    ./stop_humanizer_api.sh
    exit 0
}

# Set trap for cleanup
trap cleanup SIGINT SIGTERM

# Follow logs in real-time (optional)
if [ "$1" = "--logs" ] || [ "$1" = "-l" ]; then
    echo "📄 Following logs (Ctrl+C to stop)..."
    tail -f logs/archive_api.log logs/lpe_api.log
else
    echo "💡 Add --logs or -l to follow logs in real-time"
    echo "💡 Check individual logs: tail -f logs/archive_api.log"
    
    # Keep script running to maintain trap
    while true; do
        sleep 10
        # Check if services are still running
        if ! check_port "${ARCHIVE_API_PORT:-7200}" || ! check_port "${LPE_API_PORT:-7201}"; then
            echo "⚠️  Some services appear to have stopped. Check logs for details."
            break
        fi
    done
fi
