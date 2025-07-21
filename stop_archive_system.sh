#!/bin/bash
"""
Stop Archive System Script
Gracefully stops all archive system services
"""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_header() {
    echo -e "${PURPLE}$1${NC}"
}

# Kill process on port
kill_port() {
    local port=$1
    local name=$2
    local pid=$(lsof -ti:$port)
    if [ ! -z "$pid" ]; then
        kill -9 $pid 2>/dev/null
        print_success "Stopped $name (port $port)"
    else
        print_status "$name was not running (port $port)"
    fi
}

# Kill process by PID file
kill_by_pid() {
    local pidfile=$1
    local name=$2
    if [ -f "$pidfile" ]; then
        local pid=$(cat "$pidfile")
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid"
            print_success "Stopped $name (PID: $pid)"
        fi
        rm -f "$pidfile"
    fi
}

print_header "🛑 STOPPING HUMANIZER ARCHIVE SYSTEM"
print_header "====================================="

cd "$(dirname "$0")"

# Stop services by PID files first
kill_by_pid "archive_api.pid" "Archive API"
kill_by_pid "lighthouse_ui.pid" "Lighthouse UI"

# Stop services by port (backup method)
kill_port 7200 "Archive API"
kill_port 3100 "Lighthouse UI"
kill_port 3101 "Lighthouse UI (alt)"

# Stop any Python processes related to archive
print_status "Stopping any remaining archive processes..."
pkill -f "archive_api_enhanced.py" 2>/dev/null
pkill -f "smart_archive_processor.py" 2>/dev/null

# Stop any npm dev servers
pkill -f "vite" 2>/dev/null

print_success "All archive system services stopped"

print_header "\n📁 Log files preserved:"
echo "- archive_api.log"
echo "- lighthouse_ui.log"

print_header "\n💡 To restart the system:"
echo "./start_archive_system.sh"

print_success "Archive system shutdown complete"