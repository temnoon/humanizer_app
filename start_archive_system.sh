#!/bin/bash
"""
Complete Archive System Startup Script
Starts all components of the Humanizer Archive system in the correct order
"""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${PURPLE}$1${NC}"
}

# Check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if a service is running
check_service() {
    local service=$1
    local port=$2
    local name=$3
    
    if curl -s "http://localhost:$port" >/dev/null 2>&1; then
        print_success "$name is running on port $port"
        return 0
    else
        return 1
    fi
}

# Kill process on port
kill_port() {
    local port=$1
    local pid=$(lsof -ti:$port)
    if [ ! -z "$pid" ]; then
        kill -9 $pid 2>/dev/null
        print_status "Killed existing process on port $port"
    fi
}

print_header "🚀 HUMANIZER ARCHIVE SYSTEM STARTUP"
print_header "======================================"

# Step 1: Check prerequisites
print_status "Checking prerequisites..."

if ! command_exists psql; then
    print_error "PostgreSQL not found. Please install PostgreSQL first."
    exit 1
fi

if ! command_exists ollama; then
    print_error "Ollama not found. Please install Ollama first."
    exit 1
fi

if ! command_exists node; then
    print_error "Node.js not found. Please install Node.js first."
    exit 1
fi

if ! command_exists python3; then
    print_error "Python 3 not found. Please install Python 3 first."
    exit 1
fi

print_success "All prerequisites found"

# Step 2: Check and start PostgreSQL
print_status "Checking PostgreSQL..."
if ! pg_isready >/dev/null 2>&1; then
    print_warning "PostgreSQL not running, attempting to start..."
    if command_exists brew; then
        brew services start postgresql
    else
        sudo systemctl start postgresql
    fi
    sleep 3
    
    if ! pg_isready >/dev/null 2>&1; then
        print_error "Could not start PostgreSQL. Please start it manually."
        exit 1
    fi
fi
print_success "PostgreSQL is running"

# Step 3: Check and start Ollama
print_status "Checking Ollama..."
if ! ollama list >/dev/null 2>&1; then
    print_warning "Ollama not running, starting..."
    nohup ollama serve > /dev/null 2>&1 &
    sleep 5
    
    if ! ollama list >/dev/null 2>&1; then
        print_error "Could not start Ollama. Please start it manually."
        exit 1
    fi
fi
print_success "Ollama is running"

# Step 4: Check nomic-embed-text model
print_status "Checking nomic-embed-text model..."
if ! ollama list | grep -q "nomic-embed-text"; then
    print_warning "nomic-embed-text model not found, pulling..."
    ollama pull nomic-embed-text
    if [ $? -ne 0 ]; then
        print_error "Failed to pull nomic-embed-text model"
        exit 1
    fi
fi
print_success "nomic-embed-text model is available"

# Step 5: Setup database if needed
print_status "Checking database setup..."
if ! psql -d humanizer_archive -c "SELECT 1" >/dev/null 2>&1; then
    print_warning "Creating humanizer_archive database..."
    createdb humanizer_archive
    psql -d humanizer_archive -c "CREATE EXTENSION IF NOT EXISTS vector;" >/dev/null 2>&1
fi
print_success "Database is ready"

# Step 6: Install Python dependencies
print_status "Checking Python dependencies..."
cd "$(dirname "$0")"
if [ ! -f ".venv_ready" ]; then
    print_status "Installing Python dependencies..."
    pip3 install pgvector asyncpg httpx sentence-transformers numpy tiktoken fastapi uvicorn
    touch .venv_ready
fi
print_success "Python dependencies ready"

# Step 7: Install UI dependencies
print_status "Checking UI dependencies..."
cd lighthouse-ui
if [ ! -d "node_modules" ]; then
    print_status "Installing UI dependencies..."
    npm install
fi
cd ..
print_success "UI dependencies ready"

# Step 8: Start services
print_header "\n🎯 Starting Services..."

# Kill any existing services
kill_port 7200
kill_port 3100

# Start Archive API
print_status "Starting Archive API..."
cd humanizer_api/src
nohup python3 archive_api_enhanced.py > ../../archive_api.log 2>&1 &
ARCHIVE_API_PID=$!
cd ../..

# Wait for Archive API to start
sleep 5
if check_service "archive_api" 7200 "Archive API"; then
    echo $ARCHIVE_API_PID > archive_api.pid
else
    print_error "Archive API failed to start. Check archive_api.log"
    exit 1
fi

# Start Lighthouse UI
print_status "Starting Lighthouse UI..."
cd lighthouse-ui
nohup npm run dev > ../lighthouse_ui.log 2>&1 &
LIGHTHOUSE_PID=$!
cd ..

# Wait for UI to start
sleep 8
if check_service "lighthouse_ui" 3100 "Lighthouse UI"; then
    echo $LIGHTHOUSE_PID > lighthouse_ui.pid
else
    print_error "Lighthouse UI failed to start. Check lighthouse_ui.log"
    exit 1
fi

print_header "\n🎉 ARCHIVE SYSTEM STARTUP COMPLETE!"
print_header "===================================="

print_success "Archive API: http://localhost:7200"
print_success "API Documentation: http://localhost:7200/docs" 
print_success "Lighthouse UI: http://localhost:3100"
print_success "Archive Tab: http://localhost:3100 (click Archive tab)"

print_header "\n📋 Next Steps:"
echo "1. Open http://localhost:3100 in your browser"
echo "2. Click on the 'Archive' tab"
echo "3. Click 'Start Import' to begin processing your Node Archive"
echo "4. Watch the real-time progress updates"

print_header "\n🛑 To Stop Services:"
echo "./stop_archive_system.sh"

print_header "\n📊 Logs:"
echo "Archive API: tail -f archive_api.log"
echo "Lighthouse UI: tail -f lighthouse_ui.log"

print_header "\n✨ Ready to explore your archive!"