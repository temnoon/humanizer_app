#!/bin/bash

# Humanizer Lighthouse - Master Startup Script

echo "🔦 HUMANIZER LIGHTHOUSE LAUNCHER"
echo "================================"
echo ""

# Colors for output
=======
echo "================================"
echo ""

# Get the directory where the script is located to use relative paths
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# Colors for output

# Get the directory where the script is located to use relative paths
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if a port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        return 0
    else
        return 1
    fi
}

# Check if API is already running
if check_port 8100; then
    echo -e "${YELLOW}⚠️  API already running on port 8100${NC}"
else
    echo -e "${GREEN}🚀 Starting Lighthouse API...${NC}"
    cd "$SCRIPT_DIR/humanizer_api/lighthouse"

    # Check for .env file
    if [ ! -f ".env" ]; then
        echo "Creating .env file..."
        cp .env.example .env
        echo -e "${YELLOW}⚠️  Please edit $SCRIPT_DIR/humanizer_api/.env and add your API keys!${NC}"
        echo "Then run this script again."
        exit 1
    fi

    # Start API in background
    ./start.sh &
    API_PID=$!
    echo "API starting with PID: $API_PID"

    # Wait for API to be ready
    echo "Waiting for API to be ready..."
    for i in {1..30}; do
        if curl -s http://localhost:8100/health >/dev/null 2>&1; then
            echo -e "${GREEN}✅ API is ready!${NC}"
            break
        fi
        sleep 1
    done
fi

# Check if UI is already running
if check_port 3100; then
    echo -e "${YELLOW}⚠️  UI already running on port 3100${NC}"
else
    echo -e "${GREEN}🎨 Starting Lighthouse UI...${NC}"
    cd "$SCRIPT_DIR/lighthouse-ui"

    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        echo "Installing UI dependencies..."
        npm install
    fi

    # Start UI
    npm run dev &
    UI_PID=$!
    echo "UI starting with PID: $UI_PID"
fi

echo ""
echo -e "${GREEN}✨ LIGHTHOUSE IS READY!${NC}"
echo ""
echo "🔗 Access points:"
echo "   - UI: http://localhost:3100"
echo "   - API: http://localhost:8100"
echo "   - API Docs: http://localhost:8100/docs"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Shutting down services..."
    if [ ! -z "$API_PID" ]; then
        kill $API_PID 2>/dev/null
    fi
    if [ ! -z "$UI_PID" ]; then
        kill $UI_PID 2>/dev/null
    fi
    exit 0
}

# Set up trap to cleanup on Ctrl+C
trap cleanup INT

# Wait forever
while true; do
    sleep 1
done
