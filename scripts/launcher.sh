#!/bin/bash

# Launcher Script - Central entry point for Narrative DNA system
# Manages API, daemon, and provides quick access to all tools

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LIGHTHOUSE_DIR="$PROJECT_ROOT/humanizer_api/lighthouse"
API_PID_FILE="$SCRIPT_DIR/api.pid"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'

# ASCII Art Banner
show_banner() {
    echo -e "${CYAN}"
    cat << 'EOF'
 ███▄    █  ▄▄▄       ██▀███   ██▀███   ▄▄▄     ▄▄▄█████▓ ██▓ ██▒   █▓▓█████ 
 ██ ▀█   █ ▒████▄    ▓██ ▒ ██▒▓██ ▒ ██▒▒████▄   ▓  ██▒ ▓▒▓██▒▓██░   █▒▓█   ▀ 
▓██  ▀█ ██▒▒██  ▀█▄  ▓██ ░▄█ ▒▓██ ░▄█ ▒▒██  ▀█▄ ▒ ▓██░ ▒░▒██▒ ▓██  █▒░▒███   
▓██▒  ▐▌██▒░██▄▄▄▄██ ▒██▀▀█▄  ▒██▀▀█▄  ░██▄▄▄▄██░ ▓██▓ ░ ░██░  ▒██ █░░▒▓█  ▄ 
▒██░   ▓██░ ▓█   ▓██▒░██▓ ▒██▒░██▓ ▒██▒ ▓█   ▓██▒ ▒██▒ ░ ░██░   ▒▀█░  ░▒████▒
░ ▒░   ▒ ▒  ▒▒   ▓▒█░░ ▒▓ ░▒▓░░ ▒▓ ░▒▓░ ▒▒   ▓▒█░ ▒ ░░   ░▓     ░ ▐░  ░░ ▒░ ░
░ ░░   ░ ▒░  ▒   ▒▒ ░  ░▒ ░ ▒░  ░▒ ░ ▒░  ▒   ▒▒ ░   ░     ▒ ░   ░ ░░   ░ ░  ░
   ░   ░ ░   ░   ▒     ░░   ░   ░░   ░   ░   ▒    ░       ▒ ░     ░░     ░   
         ░       ░  ░   ░        ░           ░  ░         ░        ░     ░  ░
                                                                   ░           
         ▓█████▄  ███▄    █  ▄▄▄          ▄████▄   ▒█████   ███▄ ▄███▓        
         ▒██▀ ██▌ ██ ▀█   █ ▒████▄       ▒██▀ ▀█  ▒██▒  ██▒▓██▒▀█▀ ██▒        
         ░██   █▌▓██  ▀█ ██▒▒██  ▀█▄     ▒▓█    ▄ ▒██░  ██▒▓██    ▓██░        
         ░▓█▄   ▌▓██▒  ▐▌██▒░██▄▄▄▄██    ▒▓▓▄ ▄██▒▒██   ██░▒██    ▒██         
         ░▒████▓ ▒██░   ▓██░ ▓█   ▓██▒   ▒ ▓███▀ ░░ ████▓▒░▒██▒   ░██▒        
          ▒▒▓  ▒ ░ ▒░   ▒ ▒  ▒▒   ▓▒█░   ░ ░▒ ▒  ░░ ▒░▒░▒░ ░ ▒░   ░  ░        
          ░ ▒  ▒ ░ ░░   ░ ▒░  ▒   ▒▒ ░     ░  ▒     ░ ▒ ▒░ ░  ░      ░        
          ░ ░  ░    ░   ░ ░   ░   ▒      ░        ░ ░ ░ ▒  ░      ░           
            ░             ░       ░  ░   ░ ░          ░ ░         ░           
          ░                             ░                                     
EOF
    echo -e "${WHITE}                    QUANTUM NARRATIVE DNA MANAGEMENT SYSTEM${NC}"
    echo -e "${GRAY}                           v1.0.0 - 2025-07-28${NC}"
    echo
}

# Check if API is running
check_api() {
    if curl -s http://localhost:8100/health > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Start API server
start_api() {
    if check_api; then
        echo -e "${YELLOW}API already running${NC}"
        return 0
    fi
    
    echo -e "${BLUE}Starting Lighthouse API...${NC}"
    
    if [[ ! -d "$LIGHTHOUSE_DIR" ]]; then
        echo -e "${RED}Lighthouse directory not found: $LIGHTHOUSE_DIR${NC}"
        return 1
    fi
    
    # Check for virtual environment
    if [[ ! -d "$LIGHTHOUSE_DIR/venv" ]]; then
        echo -e "${RED}Virtual environment not found: $LIGHTHOUSE_DIR/venv${NC}"
        echo "Please run: cd $LIGHTHOUSE_DIR && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
        return 1
    fi
    
    # Start API in background
    cd "$LIGHTHOUSE_DIR"
    source venv/bin/activate
    nohup python api_enhanced.py > "$SCRIPT_DIR/logs/api.log" 2>&1 &
    local api_pid=$!
    
    echo "$api_pid" > "$API_PID_FILE"
    
    # Wait for API to start
    local timeout=30
    while [[ $timeout -gt 0 ]] && ! check_api; do
        sleep 1
        ((timeout--))
    done
    
    if check_api; then
        echo -e "${GREEN}API started successfully (PID: $api_pid)${NC}"
    else
        echo -e "${RED}Failed to start API${NC}"
        return 1
    fi
}

# Stop API server
stop_api() {
    if [[ -f "$API_PID_FILE" ]]; then
        local pid=$(cat "$API_PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            echo -e "${BLUE}Stopping API (PID: $pid)...${NC}"
            kill "$pid" 2>/dev/null || true
            rm -f "$API_PID_FILE"
            echo -e "${GREEN}API stopped${NC}"
        else
            rm -f "$API_PID_FILE"
            echo -e "${YELLOW}API was not running${NC}"
        fi
    else
        echo -e "${YELLOW}API PID file not found${NC}"
    fi
}

# Show system status
show_status() {
    echo -e "${CYAN}=== Narrative DNA System Status ===${NC}"
    echo
    
    # API Status
    if check_api; then
        echo -e "🟢 ${GREEN}API Server: ONLINE${NC} (http://localhost:8100)"
    else
        echo -e "🔴 ${RED}API Server: OFFLINE${NC}"
    fi
    
    # Job Daemon Status
    if "$SCRIPT_DIR/job_daemon.sh" status > /dev/null 2>&1; then
        echo -e "🟢 ${GREEN}Job Daemon: RUNNING${NC}"
    else
        echo -e "🔴 ${RED}Job Daemon: STOPPED${NC}"
    fi
    
    # Check for attributes
    if [[ -f "$SCRIPT_DIR/results/attributes.json" ]]; then
        local attr_count=$(jq length "$SCRIPT_DIR/results/attributes.json" 2>/dev/null || echo "0")
        echo -e "📚 ${BLUE}DNA Attributes: $attr_count available${NC}"
    else
        echo -e "📚 ${YELLOW}DNA Attributes: None found${NC}"
    fi
    
    # Job queue status
    local pending_jobs=$(find "$SCRIPT_DIR/queue" -name "*.job" 2>/dev/null | wc -l)
    local completed_logs=$(find "$SCRIPT_DIR/logs" -name "*.log" 2>/dev/null | wc -l)
    echo -e "⏳ ${BLUE}Pending Jobs: $pending_jobs${NC}"
    echo -e "✅ ${BLUE}Job Logs: $completed_logs${NC}"
    
    echo
}

# Quick setup for new installation
quick_setup() {
    echo -e "${CYAN}=== Quick Setup ===${NC}"
    echo
    
    # Create directories
    mkdir -p "$SCRIPT_DIR/results" "$SCRIPT_DIR/logs" "$SCRIPT_DIR/queue"
    echo -e "✅ Created directory structure"
    
    # Start services
    start_api
    "$SCRIPT_DIR/job_daemon.sh" start
    
    echo
    echo -e "${GREEN}Setup complete!${NC}"
    echo
    echo "Next steps:"
    echo "1. Run: $0 extract    # Extract DNA from books"
    echo "2. Run: $0 commander  # Launch CLI dashboard"
    echo "3. Or: $0 transform 'persona|namespace|style' 'your text'"
}

# Launch commander interface
launch_commander() {
    echo -e "${BLUE}Launching DNA Navigator...${NC}"
    exec "$SCRIPT_DIR/dna_navigator.sh"
}

# Extract DNA quick command
quick_extract() {
    echo -e "${BLUE}Starting DNA extraction...${NC}"
    "$SCRIPT_DIR/dna_tools.sh" extract "$@"
}

# Transform text quick command
quick_transform() {
    local dna="$1"
    local text="$2"
    
    if [[ -z "$dna" || -z "$text" ]]; then
        echo "Usage: $0 transform 'persona|namespace|style' 'text to transform'"
        return 1
    fi
    
    echo -e "${BLUE}Transforming text...${NC}"
    "$SCRIPT_DIR/dna_tools.sh" transform "$dna" "$text"
}

# Show available DNA attributes
show_attributes() {
    "$SCRIPT_DIR/dna_tools.sh" list "$@"
}

# Show help
show_help() {
    cat << EOF
${CYAN}Narrative DNA System Launcher${NC}

SYSTEM MANAGEMENT:
  setup           - Quick setup for new installation
  start           - Start API and daemon
  stop            - Stop API and daemon
  restart         - Restart all services
  status          - Show system status

TOOLS:
  commander       - Launch DNA navigator (arrow key navigation)
  extract [books] - Extract DNA from books
  transform DNA TEXT - Transform text using DNA
  attributes [fmt] - List available DNA attributes
  inspect <cmd>   - Deep DNA analysis and inspection
  library <cmd>   - Build default library for website launch
  autonomous <cmd> - Autonomous book discovery and DNA extraction

DNA TOOLS:
  tools <cmd>     - Direct access to dna_tools.sh
  daemon <cmd>    - Direct access to job_daemon.sh
  inspect <cmd>   - Direct access to dna_inspector.sh
  library <cmd>   - Direct access to default_attribute_builder.sh

EXAMPLES:
  $0 setup
  $0 status
  $0 extract 1342 11 84
  $0 transform 'gothic_documenter|victorian_gothic_horror|gothic_realism' 'Hello world'
  $0 attributes table
  $0 commander
  $0 autonomous start    # Start continuous discovery (4h cycles)
  $0 autonomous stats    # Show discovery statistics

DNA FORMAT:
  DNA consists of three components separated by pipes:
  'persona|namespace|style'
  
  Example: 'philosophical_seafarer|maritime_existentialism|epic_philosophical_prose'

For more detailed help on specific tools:
  $0 tools help
  $0 daemon help
EOF
}

# Main command dispatcher
main() {
    local command="$1"
    shift
    
    # Always show banner unless it's a help command
    if [[ "$command" != "help" && "$command" != "--help" && "$command" != "-h" ]]; then
        show_banner
    fi
    
    case "$command" in
        "setup")
            quick_setup
            ;;
        "start")
            start_api
            "$SCRIPT_DIR/job_daemon.sh" start
            ;;
        "stop")
            stop_api
            "$SCRIPT_DIR/job_daemon.sh" stop
            ;;
        "restart")
            stop_api
            "$SCRIPT_DIR/job_daemon.sh" stop
            sleep 2
            start_api
            "$SCRIPT_DIR/job_daemon.sh" start
            ;;
        "status")
            show_status
            ;;
        "commander")
            launch_commander
            ;;
        "extract")
            quick_extract "$@"
            ;;
        "transform")
            quick_transform "$@"
            ;;
        "attributes")
            show_attributes "$@"
            ;;
        "tools")
            "$SCRIPT_DIR/dna_tools.sh" "$@"
            ;;
        "daemon")
            "$SCRIPT_DIR/job_daemon.sh" "$@"
            ;;
        "inspect")
            "$SCRIPT_DIR/dna_inspector.sh" "$@"
            ;;
        "library")
            "$SCRIPT_DIR/website_library_builder.sh" "$@"
            ;;
        "autonomous")
            "$SCRIPT_DIR/autonomous_dna_discoverer.sh" "$@"
            ;;
        "help"|"--help"|"-h"|"")
            show_help
            ;;
        *)
            echo -e "${RED}Unknown command: $command${NC}"
            echo "Use '$0 help' for usage information."
            exit 1
            ;;
    esac
}

# Entry point
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi