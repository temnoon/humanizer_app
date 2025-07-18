#!/bin/bash

# Enhanced Humanizer Lighthouse - Master Startup Script
# Starts the enhanced API with full LPE features

echo "🔦 ENHANCED HUMANIZER LIGHTHOUSE LAUNCHER"
echo "=========================================="
echo ""
echo "Starting full-featured Lamish Projection Engine with:"
echo "• Advanced 5-step transformation pipeline"
echo "• Maieutic (Socratic) dialogue system"
echo "• Translation round-trip analysis"
echo "• Enhanced UI with tabbed interface"
echo ""

# Get the directory where the script is located
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to check if a port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        return 0
    else
        return 1
    fi
}

# Function to wait for service to be ready
wait_for_service() {
    local port=$1
    local service_name=$2
    local max_attempts=30
    local attempt=0
    
    echo "Waiting for $service_name to be ready..."
    while [ $attempt -lt $max_attempts ]; do
        if curl -s http://localhost:$port/health >/dev/null 2>&1; then
            echo -e "${GREEN}✅ $service_name is ready!${NC}"
            return 0
        fi
        sleep 1
        ((attempt++))
    done
    
    echo -e "${RED}❌ $service_name failed to start after $max_attempts seconds${NC}"
    return 1
}

# Check if enhanced API is already running
if check_port 8100; then
    echo -e "${YELLOW}⚠️  Enhanced API already running on port 8100${NC}"
else
    echo -e "${GREEN}🚀 Starting Enhanced Lighthouse API...${NC}"
    cd "$SCRIPT_DIR/humanizer_api/lighthouse"

    # Check for .env file
    if [ ! -f ".env" ]; then
        echo "Creating .env file..."
        cat > .env << EOF
# LLM Provider Configuration
LPE_PROVIDER=mock
LPE_MODEL=gpt-4o-mini
LPE_EMBEDDING_MODEL=text-embedding-3-small

# API Keys (uncomment and add your keys)
# OPENAI_API_KEY=your_openai_key_here
# ANTHROPIC_API_KEY=your_anthropic_key_here
# DEEPSEEK_API_KEY=your_deepseek_key_here

# Database Configuration
CHROMADB_PATH=./chromadb_data
SQLITE_PATH=./data/humanizer.db

# API Settings
API_PORT=8100
EOF
        echo -e "${YELLOW}⚠️  Created .env file with mock provider. Edit to add real API keys!${NC}"
    fi

    # Check for virtual environment and create if needed
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
        if [ $? -ne 0 ]; then
            echo -e "${RED}❌ Failed to create virtual environment${NC}"
            exit 1
        fi
    fi

    # Activate virtual environment
    source venv/bin/activate
    
    # Install required dependencies
    if [ -f "requirements_enhanced.txt" ]; then
        echo "Installing/updating dependencies from requirements_enhanced.txt..."
        pip install --quiet -r requirements_enhanced.txt
    else
        echo "Installing/updating basic dependencies..."
        pip install --quiet fastapi uvicorn pydantic python-dotenv litellm websockets
    fi
    
    # Start enhanced API in background
    echo "Starting enhanced API with full LPE features..."
    python api_enhanced.py &
    API_PID=$!
    echo "Enhanced API starting with PID: $API_PID"

    # Wait for API to be ready
    if wait_for_service 8100 "Enhanced API"; then
        echo -e "${GREEN}🎉 Enhanced API features available:${NC}"
        echo "   • Advanced transformation pipeline"
        echo "   • Maieutic dialogue system"
        echo "   • Translation analysis"
        echo "   • WebSocket support for real-time interaction"
    else
        echo -e "${RED}❌ Failed to start Enhanced API${NC}"
        exit 1
    fi
fi

# Check if UI is already running
if check_port 3100; then
    echo -e "${YELLOW}⚠️  UI already running on port 3100${NC}"
else
    echo -e "${GREEN}🎨 Starting Enhanced Lighthouse UI...${NC}"
    cd "$SCRIPT_DIR/lighthouse-ui"

    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        echo "Installing UI dependencies..."
        npm install
        if [ $? -ne 0 ]; then
            echo -e "${RED}❌ Failed to install UI dependencies${NC}"
            exit 1
        fi
    fi

    # Update vite.config.js to point to enhanced API
    if [ -f "vite.config.js" ]; then
        # Update the proxy target to point to enhanced API
        sed -i.bak 's/target: "http:\/\/localhost:8100"/target: "http:\/\/localhost:8100"/' vite.config.js
        echo "Updated vite.config.js to use enhanced API"
    fi

    # Start UI
    npm run dev &
    UI_PID=$!
    echo "Enhanced UI starting with PID: $UI_PID"
    
    # Wait for UI to be ready
    sleep 3
    if check_port 3100; then
        echo -e "${GREEN}✅ Enhanced UI is ready!${NC}"
    else
        echo -e "${RED}❌ Failed to start Enhanced UI${NC}"
        exit 1
    fi
fi

echo ""
echo -e "${GREEN}🎉 ENHANCED LIGHTHOUSE IS READY!${NC}"
echo ""
echo "🔗 Access points:"
echo "   - Enhanced UI: http://localhost:3100"
echo "   - Enhanced API: http://localhost:8100"
echo "   - API Documentation: http://localhost:8100/docs"
echo ""
echo "🚀 New features available:"
echo "   - Transform: Advanced 5-step projection pipeline"
echo "   - Maieutic: Socratic dialogue for narrative exploration"
echo "   - Translation: Round-trip analysis and stability testing"
echo ""
echo "📚 Try these examples:"
echo "   1. Transform: 'Sam Altman dropped out of Stanford to start OpenAI'"
echo "   2. Maieutic: Explore deeper meanings through guided questioning"
echo "   3. Translation: Test semantic stability across languages"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Shutting down enhanced services..."
    if [ ! -z "$API_PID" ]; then
        kill $API_PID 2>/dev/null
        echo "Stopped Enhanced API"
    fi
    if [ ! -z "$UI_PID" ]; then
        kill $UI_PID 2>/dev/null
        echo "Stopped Enhanced UI"
    fi
    echo "Enhanced Lighthouse shutdown complete"
    exit 0
}

# Set up trap to cleanup on Ctrl+C
trap cleanup INT

# Keep the script running
echo "Enhanced Lighthouse is running. Press Ctrl+C to stop."
while true; do
    sleep 1
done