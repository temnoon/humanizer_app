#!/bin/bash
# stop_humanizer_api.sh - Stop all Humanizer API services

echo "🛑 Stopping Humanizer API Ecosystem..."
echo "======================================"

# Function to stop service by PID file
stop_service() {
    local name=$1
    local pid_file="logs/${name}.pid"
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        echo "🛑 Stopping $name (PID: $pid)..."
        
        if kill -0 $pid 2>/dev/null; then
            kill $pid
            # Wait up to 10 seconds for graceful shutdown
            local count=0
            while kill -0 $pid 2>/dev/null && [ $count -lt 10 ]; do
                sleep 1
                count=$((count + 1))
            done
            
            # Force kill if still running
            if kill -0 $pid 2>/dev/null; then
                echo "⚠️  Force killing $name..."
                kill -9 $pid
            fi
        fi
        
        rm -f "$pid_file"
        echo "✅ $name stopped"
    else
        echo "ℹ️  $name PID file not found"
    fi
}

# Stop services
stop_service "archive_api"
stop_service "lpe_api"

# Also kill any remaining processes on the ports
ports=("${ARCHIVE_API_PORT:-7200}" "${LPE_API_PORT:-7201}")

for port in "${ports[@]}"; do
    pid=$(lsof -ti:$port 2>/dev/null)
    if [ ! -z "$pid" ]; then
        echo "🔄 Killing remaining process on port $port (PID: $pid)"
        kill -9 $pid 2>/dev/null
    fi
done

echo ""
echo "✅ All Humanizer API services stopped"
echo "📝 Logs preserved in logs/ directory"
