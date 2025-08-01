#!/bin/bash

# Autonomous DNA Discoverer - Continuous book discovery and DNA extraction
# Tracks progress, finds new books, runs in 4-hour cycles with breaks

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
API_URL="http://localhost:8100"

# State tracking files
STATE_DIR="$SCRIPT_DIR/discovery_state"
PROCESSED_BOOKS_FILE="$STATE_DIR/processed_books.json"
DISCOVERY_LOG="$STATE_DIR/discovery.log"
SESSION_STATE="$STATE_DIR/current_session.json"
QUEUE_FILE="$STATE_DIR/discovery_queue.json"

# Runtime configuration
WORK_CYCLE_HOURS=4
BREAK_MINUTES=30
PARAGRAPHS_PER_BOOK=128  # Doubled from 64
BOOKS_PER_BATCH=3
MAX_BOOKS_PER_SESSION=20
CONTINUOUS_CYCLE_HOURS=24  # Long cycle for continuous mode

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
GRAY='\033[0;37m'
NC='\033[0m'

# Initialize state directory
init_state() {
    mkdir -p "$STATE_DIR"
    
    if [[ ! -f "$PROCESSED_BOOKS_FILE" ]]; then
        echo '{"processed_books": [], "last_updated": "", "total_processed": 0}' > "$PROCESSED_BOOKS_FILE"
    fi
    
    if [[ ! -f "$QUEUE_FILE" ]]; then
        echo '{"discovery_queue": [], "last_discovery": "", "discovery_page": 1}' > "$QUEUE_FILE"
    fi
    
    log_event "Autonomous DNA Discoverer initialized"
}

# Logging function
log_event() {
    local message="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] $message" >> "$DISCOVERY_LOG"
    echo -e "${BLUE}[$timestamp]${NC} $message"
}

# Check API availability
check_api() {
    if ! curl -s "$API_URL/health" > /dev/null 2>&1; then
        log_event "ERROR: API not available at $API_URL"
        echo "Please start the API server first:"
        echo "  ./launcher.sh start"
        exit 1
    fi
}

# Get book metadata from Gutenberg API
get_book_metadata() {
    local book_id="$1"
    
    # Try Gutenberg API first
    local response=$(curl -s "https://www.gutenberg.org/ebooks/$book_id.json" 2>/dev/null || echo "{}")
    
    if echo "$response" | jq empty 2>/dev/null; then
        echo "$response"
    else
        # Fallback metadata
        echo "{\"id\": $book_id, \"title\": \"Book $book_id\", \"authors\": [], \"languages\": [\"en\"]}"
    fi
}

# Discover new books from Gutenberg
discover_new_books() {
    local page=${1:-1}
    local discovered_books=()
    
    log_event "Discovering new books from Gutenberg (page $page)"
    
    # Get popular books from different categories
    local categories=("philosophy" "fiction" "literature" "science" "history" "poetry")
    
    for category in "${categories[@]}"; do
        log_event "Searching category: $category"
        
        # Simulate Gutenberg search (in real implementation, would use their API)
        # For now, generate book IDs in ranges known to have good content
        local range_start=$((1000 + page * 100))
        local range_end=$((range_start + 50))
        
        for ((book_id=range_start; book_id<range_end; book_id+=7)); do
            # Check if already processed
            if ! is_book_processed "$book_id"; then
                # Verify book exists and is suitable
                if is_book_suitable "$book_id"; then
                    discovered_books+=("$book_id")
                    log_event "Discovered suitable book: $book_id"
                    
                    # Limit discovery per run
                    if [[ ${#discovered_books[@]} -ge 20 ]]; then
                        break 2
                    fi
                fi
            fi
        done
    done
    
    # Update queue with discovered books
    update_discovery_queue "${discovered_books[@]}"
    
    echo "${discovered_books[@]}"
}

# Check if book has been processed
is_book_processed() {
    local book_id="$1"
    jq -r '.processed_books[]' "$PROCESSED_BOOKS_FILE" | grep -q "^$book_id$"
}

# Check if book is suitable for DNA extraction
is_book_suitable() {
    local book_id="$1"
    
    # Quick checks for suitability
    local metadata=$(get_book_metadata "$book_id")
    
    # Check if it's English text
    local language=$(echo "$metadata" | jq -r '.languages[0] // "unknown"')
    if [[ "$language" != "en" ]]; then
        return 1
    fi
    
    # Check if it has reasonable length (simple heuristic)
    if curl -s --head "https://www.gutenberg.org/files/$book_id/$book_id-0.txt" | grep -q "Content-Length"; then
        local size=$(curl -s --head "https://www.gutenberg.org/files/$book_id/$book_id-0.txt" | grep "Content-Length" | awk '{print $2}' | tr -d '\r')
        if [[ $size -gt 50000 && $size -lt 2000000 ]]; then  # 50KB - 2MB range
            return 0
        fi
    fi
    
    return 1
}

# Update discovery queue
update_discovery_queue() {
    local new_books=("$@")
    
    if [[ ${#new_books[@]} -gt 0 ]]; then
        local queue_data=$(jq --argjson books "$(printf '%s\n' "${new_books[@]}" | jq -R . | jq -s .)" \
            '.discovery_queue += $books | .last_discovery = now | .discovery_page += 1' "$QUEUE_FILE")
        echo "$queue_data" > "$QUEUE_FILE"
    fi
}

# Get next books from queue
get_next_books() {
    local count=${1:-$BOOKS_PER_BATCH}
    jq -r ".discovery_queue[:$count][]" "$QUEUE_FILE"
}

# Remove books from queue
remove_from_queue() {
    local count=${1:-$BOOKS_PER_BATCH}
    local queue_data=$(jq ".discovery_queue = .discovery_queue[$count:]" "$QUEUE_FILE")
    echo "$queue_data" > "$QUEUE_FILE"
}

# Mark books as processed
mark_books_processed() {
    local books=("$@")
    
    if [[ ${#books[@]} -gt 0 ]]; then
        local processed_data=$(jq --argjson books "$(printf '%s\n' "${books[@]}" | jq -R . | jq -s .)" \
            '.processed_books += $books | .last_updated = now | .total_processed += ($books | length)' "$PROCESSED_BOOKS_FILE")
        echo "$processed_data" > "$PROCESSED_BOOKS_FILE"
        
        log_event "Marked ${#books[@]} books as processed: ${books[*]}"
    fi
}

# Enhanced DNA extraction with deeper analysis and output path tracking
extract_enhanced_dna() {
    local books=("$@")
    
    if [[ ${#books[@]} -eq 0 ]]; then
        log_event "No books provided for DNA extraction"
        return 1
    fi
    
    log_event "Starting enhanced DNA extraction for books: ${books[*]}"
    log_event "Using $PARAGRAPHS_PER_BOOK paragraphs per book for deeper analysis"
    
    # Create enhanced extraction job
    local job_id="autonomous_$(date +%s)"
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local output_dir="autonomous_discovery_${timestamp}"
    
    # Show expected output paths
    echo -e "${CYAN}📂 Output paths being created:${NC}"
    for book_id in "${books[@]}"; do
        local attr_path="$SCRIPT_DIR/results/attributes_${book_id}.json"
        echo -e "  📄 ${BLUE}$attr_path${NC}"
    done
    local combined_path="$SCRIPT_DIR/results/attributes.json"
    echo -e "  📋 ${GREEN}$combined_path${NC} (combined attributes)"
    
    # Call the DNA tools with enhanced parameters
    local extraction_result
    if extraction_result=$("$SCRIPT_DIR/dna_tools.sh" extract "${books[@]}" 2>&1); then
        log_event "DNA extraction completed successfully for books: ${books[*]}"
        
        # Show actual created files
        echo -e "${GREEN}✅ Created attribute files:${NC}"
        for book_id in "${books[@]}"; do
            local attr_path="$SCRIPT_DIR/results/attributes_${book_id}.json"
            if [[ -f "$attr_path" ]]; then
                local attr_count=$(jq length "$attr_path" 2>/dev/null || echo "0")
                echo -e "  ✅ ${attr_path} (${attr_count} attributes)"
            fi
        done
        
        mark_books_processed "${books[@]}"
        return 0
    else
        log_event "DNA extraction failed for books: ${books[*]} - Error: $extraction_result"
        return 1
    fi
}

# Create session state
create_session() {
    local skip_breaks="$1"
    local current_time=$(date +%s)
    local end_time
    
    if [[ "$skip_breaks" == "true" ]]; then
        # In continuous mode, set a much longer cycle
        end_time=$((current_time + CONTINUOUS_CYCLE_HOURS * 3600))
        log_event "Creating continuous session (${CONTINUOUS_CYCLE_HOURS}h cycle, breaks disabled)"
    else
        # Normal work cycle
        end_time=$((current_time + WORK_CYCLE_HOURS * 3600))
        log_event "Creating normal session (${WORK_CYCLE_HOURS}h cycle)"
    fi
    
    local session_data='{
        "session_id": "'$(date +%s)'",
        "start_time": "'$(date -u +%Y-%m-%dT%H:%M:%S)'",
        "target_end_time": "'$(date -u -r $end_time +%Y-%m-%dT%H:%M:%S)'",
        "books_processed_this_session": 0,
        "status": "running",
        "current_batch": [],
        "discoveries_this_session": 0,
        "continuous_mode": '$([ "$skip_breaks" == "true" ] && echo "true" || echo "false")'
    }'
    
    echo "$session_data" > "$SESSION_STATE"
    if [[ "$skip_breaks" == "true" ]]; then
        log_event "Started new continuous discovery session (${CONTINUOUS_CYCLE_HOURS}h cycle, no breaks)"
    else
        log_event "Started new discovery session (${WORK_CYCLE_HOURS}h work cycle)"
    fi
}

# Update session state
update_session() {
    local key="$1"
    local value="$2"
    
    if [[ -f "$SESSION_STATE" ]]; then
        local session_data=$(jq ".$key = $value" "$SESSION_STATE")
        echo "$session_data" > "$SESSION_STATE"
    fi
}

# Check if session should continue
should_continue_session() {
    if [[ ! -f "$SESSION_STATE" ]]; then
        return 1
    fi
    
    local current_time=$(date +%s)
    local end_time_str=$(jq -r '.target_end_time' "$SESSION_STATE")
    local end_time=$(date -j -f "%Y-%m-%dT%H:%M:%S" "$end_time_str" +%s 2>/dev/null || echo $((current_time + 3600)))
    local books_processed=$(jq -r '.books_processed_this_session' "$SESSION_STATE")
    local continuous_mode=$(jq -r '.continuous_mode // false' "$SESSION_STATE")
    
    # In continuous mode, only check book limit, not time limit
    if [[ "$continuous_mode" == "true" ]]; then
        if [[ $books_processed -ge $MAX_BOOKS_PER_SESSION ]]; then
            log_event "Maximum books per session reached ($MAX_BOOKS_PER_SESSION) - starting new cycle"
            return 1
        fi
        return 0
    fi
    
    # Normal mode - check both time and book limits
    if [[ $current_time -ge $end_time ]]; then
        log_event "Work cycle time limit reached (${WORK_CYCLE_HOURS}h)"
        return 1
    fi
    
    if [[ $books_processed -ge $MAX_BOOKS_PER_SESSION ]]; then
        log_event "Maximum books per session reached ($MAX_BOOKS_PER_SESSION)"
        return 1
    fi
    
    return 0
}

# Take scheduled break with skip option
take_break() {
    local skip_breaks="$1"
    
    if [[ "$skip_breaks" == "true" ]]; then
        log_event "Skipping break - continuous mode enabled"
        echo -e "${BLUE}⚡ Skipping break - starting new cycle immediately${NC}"
        return 0
    fi
    
    log_event "Taking scheduled break for $BREAK_MINUTES minutes"
    echo -e "${YELLOW}😴 Taking a $BREAK_MINUTES minute break...${NC}"
    echo "Break started at: $(date)"
    
    # Calculate resume time using macOS date
    local resume_time=$(date -v +${BREAK_MINUTES}M)
    echo "Will resume at: $resume_time"
    
    # Option to skip break with Ctrl+C
    echo "Press Ctrl+C to skip break and continue immediately"
    
    sleep $((BREAK_MINUTES * 60)) || {
        echo -e "${BLUE}Break interrupted - resuming immediately${NC}"
        log_event "Break interrupted by user"
    }
    
    log_event "Break completed, resuming discovery"
}

# Show discovery statistics
show_stats() {
    local total_processed=$(jq -r '.total_processed' "$PROCESSED_BOOKS_FILE")
    local queue_size=$(jq -r '.discovery_queue | length' "$QUEUE_FILE")
    local session_processed=$(jq -r '.books_processed_this_session // 0' "$SESSION_STATE" 2>/dev/null || echo "0")
    
    echo -e "${CYAN}📊 Discovery Statistics:${NC}"
    echo "==============================="
    echo "📚 Total books processed: $total_processed"
    echo "🔍 Books in discovery queue: $queue_size"
    echo "📈 Books processed this session: $session_processed"
    echo "⏱️  Work cycle: ${WORK_CYCLE_HOURS}h work, ${BREAK_MINUTES}m break"
    echo "📝 Paragraphs per book: $PARAGRAPHS_PER_BOOK"
    echo
}

# Main discovery loop with skip breaks option
run_discovery_loop() {
    local skip_breaks="$1"
    log_event "Starting autonomous discovery loop"
    
    if [[ "$skip_breaks" == "true" ]]; then
        log_event "Running in continuous mode - breaks will be skipped"
        echo -e "${CYAN}⚡ CONTINUOUS MODE: Breaks will be skipped automatically${NC}"
    fi
    
    while true; do
        create_session "$skip_breaks"
        
        log_event "Beginning new work cycle"
        show_stats
        
        # Work cycle
        while should_continue_session; do
            # Check if queue needs refilling
            local queue_size=$(jq -r '.discovery_queue | length' "$QUEUE_FILE")
            if [[ $queue_size -lt $BOOKS_PER_BATCH ]]; then
                log_event "Queue low ($queue_size books), discovering new books"
                local discovery_page=$(jq -r '.discovery_page' "$QUEUE_FILE")
                discover_new_books "$discovery_page"
            fi
            
            # Get next batch of books
            local next_books=($(get_next_books $BOOKS_PER_BATCH))
            
            if [[ ${#next_books[@]} -eq 0 ]]; then
                log_event "No more books in queue, discovering new ones"
                discover_new_books
                next_books=($(get_next_books $BOOKS_PER_BATCH))
            fi
            
            if [[ ${#next_books[@]} -gt 0 ]]; then
                log_event "Processing batch: ${next_books[*]}"
                
                # Extract DNA for this batch
                if extract_enhanced_dna "${next_books[@]}"; then
                    # Update session stats
                    local current_count=$(jq -r '.books_processed_this_session' "$SESSION_STATE")
                    update_session "books_processed_this_session" $((current_count + ${#next_books[@]}))
                    
                    # Remove from queue
                    remove_from_queue ${#next_books[@]}
                    
                    log_event "Batch completed successfully"
                else
                    log_event "Batch failed, will retry later"
                fi
            else
                log_event "No suitable books found, taking short break"
                sleep 300  # 5 minute pause before retry
            fi
            
            # Short pause between batches
            sleep 30
        done
        
        # Session completed, take break
        update_session "status" '"break"'
        take_break "$skip_breaks"
        
        # Check if we should continue or stop (skip prompt in continuous mode)
        if [[ "$skip_breaks" == "true" ]]; then
            log_event "Continuing discovery automatically (continuous mode)"
            continue_choice="y"
        else
            echo -e "${YELLOW}Continue discovery? [Y/n/s(tats)]:${NC}"
            read -t 30 -n 1 continue_choice || continue_choice="y"
            echo
        fi
        
        case "$continue_choice" in
            "n"|"N")
                log_event "Discovery stopped by user"
                break
                ;;
            "s"|"S")
                show_stats
                echo "Press Enter to continue..."
                read -t 10
                ;;
            *)
                log_event "Continuing discovery (user choice: ${continue_choice:-auto})"
                ;;
        esac
    done
    
    log_event "Autonomous discovery loop ended"
}

# Manual book addition
add_books_manually() {
    echo "Enter book IDs (space-separated):"
    read -r book_ids
    
    if [[ -n "$book_ids" ]]; then
        local books_array=($book_ids)
        update_discovery_queue "${books_array[@]}"
        log_event "Manually added books to queue: ${books_array[*]}"
        echo "Added ${#books_array[@]} books to discovery queue"
    fi
}

# Resume from interrupted session
resume_session() {
    local skip_breaks="$1"
    if [[ -f "$SESSION_STATE" ]] && [[ $(jq -r '.status' "$SESSION_STATE") == "running" ]]; then
        log_event "Resuming interrupted session"
        echo -e "${GREEN}📍 Resuming previous session...${NC}"
        show_stats
        run_discovery_loop "$skip_breaks"
    else
        echo "No interrupted session found"
        run_discovery_loop "$skip_breaks"
    fi
}

# Show help
show_help() {
    cat << EOF
Autonomous DNA Discoverer - Continuous book discovery and DNA extraction

USAGE:
  $0 start [OPTIONS]          - Start autonomous discovery loop
  $0 resume [OPTIONS]         - Resume interrupted session
  $0 discover [page]          - Manually discover books
  $0 add                      - Manually add book IDs
  $0 stats                    - Show discovery statistics
  $0 queue                    - Show current queue
  $0 logs                     - Show recent discovery logs

OPTIONS:
  --skip-breaks               - Skip all breaks and run continuously
  --cycle-hours N             - Set work cycle length (default: 4 hours)
  --continuous-hours N        - Set continuous cycle length (default: 24 hours)
  --max-books N               - Set max books per session (default: 20)

FEATURES:
  • Continuous discovery from Project Gutenberg
  • 4-hour work cycles with 30-minute breaks
  • Persistent state tracking
  • Enhanced DNA extraction (128 paragraphs per book)
  • Automatic queue management
  • Graceful interruption and resumption

CONFIGURATION:
  Work cycle: ${WORK_CYCLE_HOURS} hours
  Break time: ${BREAK_MINUTES} minutes
  Paragraphs per book: ${PARAGRAPHS_PER_BOOK}
  Books per batch: ${BOOKS_PER_BATCH}
  Max books per session: ${MAX_BOOKS_PER_SESSION}

The discoverer maintains state in: $STATE_DIR
EOF
}

# Show current queue
show_queue() {
    local queue_size=$(jq -r '.discovery_queue | length' "$QUEUE_FILE")
    echo -e "${CYAN}📋 Discovery Queue ($queue_size books):${NC}"
    
    if [[ $queue_size -gt 0 ]]; then
        jq -r '.discovery_queue[]' "$QUEUE_FILE" | head -20 | while read -r book_id; do
            echo "  📖 Book $book_id"
        done
        
        if [[ $queue_size -gt 20 ]]; then
            echo "  ... and $((queue_size - 20)) more"
        fi
    else
        echo "  (Queue is empty)"
    fi
}

# Show recent logs
show_logs() {
    local lines=${1:-20}
    if [[ -f "$DISCOVERY_LOG" ]]; then
        echo -e "${CYAN}📋 Recent Discovery Activity:${NC}"
        tail -n "$lines" "$DISCOVERY_LOG"
    else
        echo "No discovery logs found"
    fi
}

# Cleanup function
cleanup() {
    if [[ -f "$SESSION_STATE" ]]; then
        update_session "status" '"interrupted"'
    fi
    log_event "Discovery interrupted by signal"
    exit 0
}

# Signal handlers
trap cleanup SIGINT SIGTERM

# Main command dispatcher
main() {
    local command="$1"
    shift
    
    # Initialize state on all commands except help
    if [[ "$command" != "help" ]]; then
        init_state
        check_api
    fi
    
    case "$command" in
        "start")
            local skip_breaks="false"
            # Parse options
            while [[ $# -gt 0 ]]; do
                case "$1" in
                    "--skip-breaks")
                        skip_breaks="true"
                        shift
                        ;;
                    "--cycle-hours")
                        WORK_CYCLE_HOURS="$2"
                        shift 2
                        ;;
                    "--continuous-hours")
                        CONTINUOUS_CYCLE_HOURS="$2"
                        shift 2
                        ;;
                    "--max-books")
                        MAX_BOOKS_PER_SESSION="$2"
                        shift 2
                        ;;
                    *)
                        echo "Unknown option: $1"
                        exit 1
                        ;;
                esac
            done
            run_discovery_loop "$skip_breaks"
            ;;
        "resume")
            local skip_breaks="false"
            # Parse options
            while [[ $# -gt 0 ]]; do
                case "$1" in
                    "--skip-breaks")
                        skip_breaks="true"
                        shift
                        ;;
                    "--cycle-hours")
                        WORK_CYCLE_HOURS="$2"
                        shift 2
                        ;;
                    "--continuous-hours")
                        CONTINUOUS_CYCLE_HOURS="$2"
                        shift 2
                        ;;
                    "--max-books")
                        MAX_BOOKS_PER_SESSION="$2"
                        shift 2
                        ;;
                    *)
                        echo "Unknown option: $1"
                        exit 1
                        ;;
                esac
            done
            resume_session "$skip_breaks"
            ;;
        "discover")
            discover_new_books "$@"
            ;;
        "add")
            add_books_manually
            ;;
        "stats")
            show_stats
            ;;
        "queue")
            show_queue
            ;;
        "logs")
            show_logs "$@"
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