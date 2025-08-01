#!/bin/bash

# Job Daemon - Background job processor for Narrative DNA system
# Monitors queue directory and processes jobs automatically

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
QUEUE_DIR="$SCRIPT_DIR/queue"
LOGS_DIR="$SCRIPT_DIR/logs"
PID_FILE="$SCRIPT_DIR/job_daemon.pid"
DAEMON_LOG="$LOGS_DIR/daemon.log"
POLL_INTERVAL=5
MAX_CONCURRENT_JOBS=3

# Colors for logging
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Initialize directories
mkdir -p "$QUEUE_DIR" "$LOGS_DIR"

# Logging function with timestamp
log_daemon() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [DAEMON]: $1" | tee -a "$DAEMON_LOG"
}

# Check if daemon is already running
check_running() {
    if [[ -f "$PID_FILE" ]]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            return 0  # Running
        else
            rm -f "$PID_FILE"
            return 1  # Not running
        fi
    fi
    return 1  # Not running
}

# Start the daemon
start_daemon() {
    if check_running; then
        echo -e "${YELLOW}Daemon already running (PID: $(cat "$PID_FILE"))${NC}"
        return 1
    fi
    
    echo -e "${BLUE}Starting Job Daemon...${NC}"
    log_daemon "Starting job daemon"
    
    # Start daemon in background
    nohup bash "$0" run_daemon > /dev/null 2>&1 &
    local daemon_pid=$!
    
    echo "$daemon_pid" > "$PID_FILE"
    log_daemon "Daemon started with PID: $daemon_pid"
    echo -e "${GREEN}Job Daemon started (PID: $daemon_pid)${NC}"
}

# Stop the daemon
stop_daemon() {
    if ! check_running; then
        echo -e "${YELLOW}Daemon not running${NC}"
        return 1
    fi
    
    local pid=$(cat "$PID_FILE")
    echo -e "${BLUE}Stopping Job Daemon (PID: $pid)...${NC}"
    log_daemon "Stopping daemon (PID: $pid)"
    
    kill "$pid" 2>/dev/null || true
    rm -f "$PID_FILE"
    
    # Wait for process to stop
    local timeout=10
    while [[ $timeout -gt 0 ]] && ps -p "$pid" > /dev/null 2>&1; do
        sleep 1
        ((timeout--))
    done
    
    if ps -p "$pid" > /dev/null 2>&1; then
        echo -e "${RED}Force killing daemon${NC}"
        kill -9 "$pid" 2>/dev/null || true
    fi
    
    log_daemon "Daemon stopped"
    echo -e "${GREEN}Job Daemon stopped${NC}"
}

# Restart the daemon
restart_daemon() {
    stop_daemon
    sleep 2
    start_daemon
}

# Get daemon status
daemon_status() {
    if check_running; then
        local pid=$(cat "$PID_FILE")
        local uptime=$(ps -o etime= -p "$pid" 2>/dev/null | tr -d ' ')
        echo -e "${GREEN}Daemon running${NC} (PID: $pid, uptime: $uptime)"
        
        # Show job statistics
        local pending=$(find "$QUEUE_DIR" -name "*.job" 2>/dev/null | wc -l)
        local running=$(pgrep -f "dna_tools.sh process" | wc -l)
        echo "Jobs - Pending: $pending, Running: $running"
    else
        echo -e "${RED}Daemon not running${NC}"
    fi
}

# Count active job processes
count_active_jobs() {
    pgrep -f "dna_tools.sh process" | wc -l
}

# Process a single job
process_single_job() {
    local job_file="$1"
    local job_id=$(basename "$job_file" .job)
    
    log_daemon "Processing job: $job_id"
    
    # Call dna_tools to process the job
    if "$SCRIPT_DIR/dna_tools.sh" process "$job_file"; then
        log_daemon "Job completed successfully: $job_id"
    else
        log_daemon "Job failed: $job_id"
    fi
}

# Main daemon loop
run_daemon() {
    log_daemon "Daemon main loop started"
    
    # Handle signals for graceful shutdown
    trap 'log_daemon "Received shutdown signal"; exit 0' TERM INT
    
    while true; do
        # Check for jobs only if we have capacity
        local active_jobs=$(count_active_jobs)
        
        if [[ $active_jobs -lt $MAX_CONCURRENT_JOBS ]]; then
            # Find oldest job file
            local oldest_job=$(find "$QUEUE_DIR" -name "*.job" -type f 2>/dev/null | \
                              head -1)
            
            if [[ -n "$oldest_job" && -f "$oldest_job" ]]; then
                log_daemon "Found job to process: $(basename "$oldest_job")"
                
                # Process job in background
                process_single_job "$oldest_job" &
                
                # Small delay to prevent overwhelming the system
                sleep 1
            fi
        fi
        
        # Poll interval
        sleep "$POLL_INTERVAL"
    done
}

# Monitor daemon logs
tail_logs() {
    if [[ ! -f "$DAEMON_LOG" ]]; then
        echo "No daemon log file found: $DAEMON_LOG"
        return 1
    fi
    
    echo -e "${CYAN}Following daemon logs (Ctrl+C to stop):${NC}"
    tail -f "$DAEMON_LOG"
}

# Show recent daemon activity
show_activity() {
    local lines=${1:-50}
    
    if [[ ! -f "$DAEMON_LOG" ]]; then
        echo "No daemon log file found: $DAEMON_LOG"
        return 1
    fi
    
    echo -e "${CYAN}Recent daemon activity (last $lines lines):${NC}"
    tail -n "$lines" "$DAEMON_LOG"
}

# Clean up old daemon logs
cleanup_logs() {
    local days=${1:-7}
    
    echo -e "${YELLOW}Cleaning up daemon logs older than $days days...${NC}"
    
    # Rotate current log if it's too large (>10MB)
    if [[ -f "$DAEMON_LOG" ]] && [[ $(stat -f%z "$DAEMON_LOG" 2>/dev/null || stat -c%s "$DAEMON_LOG" 2>/dev/null || echo 0) -gt 10485760 ]]; then
        mv "$DAEMON_LOG" "${DAEMON_LOG}.$(date +%Y%m%d)"
        touch "$DAEMON_LOG"
        log_daemon "Rotated daemon log"
    fi
    
    # Remove old rotated logs
    find "$LOGS_DIR" -name "daemon.log.*" -mtime +$days -delete 2>/dev/null || true
    
    echo "Log cleanup completed."
}

# Show help
show_help() {
    cat << EOF
Job Daemon - Background processor for Narrative DNA jobs

COMMANDS:
  start       - Start the daemon
  stop        - Stop the daemon  
  restart     - Restart the daemon
  status      - Show daemon status
  logs [n]    - Show recent activity (default: 50 lines)
  tail        - Follow daemon logs in real-time
  cleanup [days] - Clean up old logs (default: 7 days)

CONFIGURATION:
  Queue directory: $QUEUE_DIR
  Logs directory: $LOGS_DIR
  PID file: $PID_FILE
  Poll interval: ${POLL_INTERVAL}s
  Max concurrent jobs: $MAX_CONCURRENT_JOBS

The daemon automatically monitors the queue directory for .job files
and processes them using the dna_tools.sh script.

EXAMPLES:
  $0 start
  $0 status
  $0 logs 100
  $0 tail
EOF
}

# Main command dispatcher
main() {
    local command="$1"
    shift
    
    case "$command" in
        "start")
            start_daemon
            ;;
        "stop")
            stop_daemon
            ;;
        "restart")
            restart_daemon
            ;;
        "status")
            daemon_status
            ;;
        "logs")
            show_activity "$@"
            ;;
        "tail")
            tail_logs
            ;;
        "cleanup")
            cleanup_logs "$@"
            ;;
        "run_daemon")
            # Internal command - don't document in help
            run_daemon
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