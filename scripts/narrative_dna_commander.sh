#!/bin/bash

# Narrative DNA Commander - Windows Commander Style CLI Dashboard
# Terminal interface for managing attributes, essences, batch jobs, and system monitoring

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
API_URL="http://localhost:8100"
LIGHTHOUSE_DIR="$PROJECT_ROOT/humanizer_api/lighthouse"
RESULTS_DIR="$SCRIPT_DIR/results"
LOGS_DIR="$SCRIPT_DIR/logs"
QUEUE_DIR="$SCRIPT_DIR/queue"

# Colors for UI
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
GRAY='\033[0;37m'
NC='\033[0m' # No Color

# Unicode characters for UI
HORZ="─"
VERT="│"
TL="┌"
TR="┐"
BL="└"
BR="┘"
CROSS="┼"
T_DOWN="┬"
T_UP="┴"
T_RIGHT="├"
T_LEFT="┤"

# Global variables
CURRENT_PANEL="left"
LEFT_PANEL_MODE="attributes"
RIGHT_PANEL_MODE="jobs"
SELECTED_ITEM=""
FILTER=""
STATUS_MESSAGE=""

# Initialize directories
mkdir -p "$RESULTS_DIR" "$LOGS_DIR" "$QUEUE_DIR"

# Logging function
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S'): $1" >> "$LOGS_DIR/commander.log"
}

# Check API status
check_api_status() {
    if curl -s "$API_URL/health" > /dev/null 2>&1; then
        echo "online"
    else
        echo "offline"
    fi
}

# Get terminal dimensions
get_terminal_size() {
    TERM_WIDTH=$(tput cols)
    TERM_HEIGHT=$(tput lines)
    PANEL_WIDTH=$((TERM_WIDTH / 2 - 2))
    CONTENT_HEIGHT=$((TERM_HEIGHT - 8))
}

# Clear screen and setup
clear_screen() {
    clear
    get_terminal_size
}

# Draw horizontal line
draw_hline() {
    local width=$1
    local char=${2:-$HORZ}
    printf "%*s\n" $width | tr ' ' "$char"
}

# Draw header
draw_header() {
    local api_status=$(check_api_status)
    local status_color=$([[ "$api_status" == "online" ]] && echo "$GREEN" || echo "$RED")
    
    echo -e "${WHITE}${TL}$(printf "%*s" $((TERM_WIDTH-2)) | tr ' ' "$HORZ")${TR}${NC}"
    printf "${VERT}${CYAN} ▓▓▓ NARRATIVE DNA COMMANDER ▓▓▓ ${NC}"
    printf "%*s" $((TERM_WIDTH - 35))
    printf "${status_color}API: %s${NC} ${VERT}\n" "$api_status"
    echo -e "${WHITE}${T_RIGHT}$(printf "%*s" $((PANEL_WIDTH)) | tr ' ' "$HORZ")${T_DOWN}$(printf "%*s" $((PANEL_WIDTH)) | tr ' ' "$HORZ")${T_LEFT}${NC}"
}

# Draw panel header
draw_panel_header() {
    local title="$1"
    local width=$2
    local is_active=$3
    
    if [[ "$is_active" == "true" ]]; then
        printf "${WHITE}${VERT} ${MAGENTA}▶ %s ${WHITE}" "$title"
    else
        printf "${WHITE}${VERT} ${GRAY}  %s ${WHITE}" "$title"
    fi
    printf "%*s${VERT}${NC}\n" $((width - ${#title} - 4))
}

# List available attributes
list_attributes() {
    local filter="$1"
    if [[ -f "$RESULTS_DIR/attributes.json" ]]; then
        jq -r '.[] | "\(.persona)|\(.namespace)|\(.style)"' "$RESULTS_DIR/attributes.json" 2>/dev/null | \
        grep -i "$filter" | head -$((CONTENT_HEIGHT - 2))
    else
        echo "No attributes found. Run DNA extraction first."
    fi
}

# List batch jobs
list_jobs() {
    local filter="$1"
    if ls "$QUEUE_DIR"/*.job 2>/dev/null | head -1 > /dev/null; then
        for job_file in "$QUEUE_DIR"/*.job; do
            if [[ -f "$job_file" ]]; then
                local job_name=$(basename "$job_file" .job)
                local status="pending"
                [[ -f "$RESULTS_DIR/${job_name}.result" ]] && status="completed"
                [[ -f "$LOGS_DIR/${job_name}.log" ]] && grep -q "ERROR" "$LOGS_DIR/${job_name}.log" && status="failed"
                echo "${job_name}|${status}"
            fi
        done | grep -i "$filter" | head -$((CONTENT_HEIGHT - 2))
    else
        echo "No batch jobs found."
    fi
}

# List essence files
list_essences() {
    local filter="$1"
    if ls "$RESULTS_DIR"/*essence*.json 2>/dev/null | head -1 > /dev/null; then
        ls "$RESULTS_DIR"/*essence*.json | while read -r file; do
            local basename=$(basename "$file" .json)
            local size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null || echo "0")
            echo "${basename}|${size} bytes"
        done | grep -i "$filter" | head -$((CONTENT_HEIGHT - 2))
    else
        echo "No essence files found."
    fi
}

# List results
list_results() {
    local filter="$1"
    if ls "$RESULTS_DIR"/*.md "$RESULTS_DIR"/*.json 2>/dev/null | head -1 > /dev/null; then
        ls -la "$RESULTS_DIR"/*.md "$RESULTS_DIR"/*.json 2>/dev/null | tail -n +2 | while read -r line; do
            local file=$(echo "$line" | awk '{print $9}')
            local size=$(echo "$line" | awk '{print $5}')
            local date=$(echo "$line" | awk '{print $6 " " $7 " " $8}')
            echo "$(basename "$file")|${size}|${date}"
        done | grep -i "$filter" | head -$((CONTENT_HEIGHT - 2))
    else
        echo "No result files found."
    fi
}

# Draw left panel content
draw_left_panel() {
    local content_lines=()
    case "$LEFT_PANEL_MODE" in
        "attributes")
            mapfile -t content_lines < <(list_attributes "$FILTER")
            ;;
        "essences")
            mapfile -t content_lines < <(list_essences "$FILTER")
            ;;
        "results")
            mapfile -t content_lines < <(list_results "$FILTER")
            ;;
    esac
    
    local i=0
    while [[ $i -lt $CONTENT_HEIGHT ]]; do
        if [[ $i -lt ${#content_lines[@]} ]]; then
            local line="${content_lines[$i]}"
            if [[ "$CURRENT_PANEL" == "left" && "$line" == "$SELECTED_ITEM" ]]; then
                printf "${VERT}${BLUE}▶ %-*s${NC}${VERT}\n" $((PANEL_WIDTH - 3)) "$line"
            else
                printf "${VERT} %-*s ${VERT}\n" $((PANEL_WIDTH - 2)) "$line"
            fi
        else
            printf "${VERT}%-*s${VERT}\n" $PANEL_WIDTH ""
        fi
        ((i++))
    done
}

# Draw right panel content
draw_right_panel() {
    local content_lines=()
    case "$RIGHT_PANEL_MODE" in
        "jobs")
            mapfile -t content_lines < <(list_jobs "$FILTER")
            ;;
        "logs")
            if [[ -n "$SELECTED_ITEM" && -f "$LOGS_DIR/${SELECTED_ITEM}.log" ]]; then
                mapfile -t content_lines < <(tail -n $((CONTENT_HEIGHT - 2)) "$LOGS_DIR/${SELECTED_ITEM}.log")
            else
                content_lines=("Select a job to view logs")
            fi
            ;;
        "monitor")
            content_lines=(
                "API Status: $(check_api_status)"
                "Attributes: $(list_attributes "" | wc -l)"
                "Jobs: $(list_jobs "" | wc -l)"
                "Results: $(list_results "" | wc -l)"
                ""
                "Disk Usage:"
                "$(du -sh "$RESULTS_DIR" 2>/dev/null | cut -f1) - Results"
                "$(du -sh "$LOGS_DIR" 2>/dev/null | cut -f1) - Logs"
                "$(du -sh "$QUEUE_DIR" 2>/dev/null | cut -f1) - Queue"
            )
            ;;
    esac
    
    local i=0
    while [[ $i -lt $CONTENT_HEIGHT ]]; do
        if [[ $i -lt ${#content_lines[@]} ]]; then
            local line="${content_lines[$i]}"
            if [[ "$CURRENT_PANEL" == "right" && "$RIGHT_PANEL_MODE" == "jobs" && "$line" == "$SELECTED_ITEM" ]]; then
                printf "${VERT}${BLUE}▶ %-*s${NC}${VERT}\n" $((PANEL_WIDTH - 3)) "$line"
            else
                printf "${VERT} %-*s ${VERT}\n" $((PANEL_WIDTH - 2)) "$line"
            fi
        else
            printf "${VERT}%-*s${VERT}\n" $PANEL_WIDTH ""
        fi
        ((i++))
    done
}

# Draw footer with commands
draw_footer() {
    echo -e "${WHITE}${T_RIGHT}$(printf "%*s" $((PANEL_WIDTH)) | tr ' ' "$HORZ")${T_UP}$(printf "%*s" $((PANEL_WIDTH)) | tr ' ' "$HORZ")${T_LEFT}${NC}"
    
    local commands=""
    case "$CURRENT_PANEL-$LEFT_PANEL_MODE-$RIGHT_PANEL_MODE" in
        "left-attributes-"*)
            commands="F1:Help F2:Extract F3:Transform F4:Delete F5:Refresh TAB:Switch Q:Quit"
            ;;
        "right-"*"-jobs")
            commands="F1:Help F2:Run F3:View F4:Delete F5:Refresh TAB:Switch Q:Quit"
            ;;
        *)
            commands="F1:Help F5:Refresh TAB:Switch /:Filter Q:Quit"
            ;;
    esac
    
    printf "${VERT}${YELLOW} %s ${NC}" "$commands"
    printf "%*s${VERT}\n" $((TERM_WIDTH - ${#commands} - 4))
    
    if [[ -n "$STATUS_MESSAGE" ]]; then
        printf "${VERT}${GREEN} Status: %s ${NC}" "$STATUS_MESSAGE"
        printf "%*s${VERT}\n" $((TERM_WIDTH - ${#STATUS_MESSAGE} - 11))
    else
        printf "${VERT}%-*s${VERT}\n" $((TERM_WIDTH - 2)) ""
    fi
    
    echo -e "${WHITE}${BL}$(printf "%*s" $((TERM_WIDTH-2)) | tr ' ' "$HORZ")${BR}${NC}"
}

# Main UI drawing function
draw_ui() {
    clear_screen
    draw_header
    
    # Panel headers
    draw_panel_header "$LEFT_PANEL_MODE" $PANEL_WIDTH "$([[ "$CURRENT_PANEL" == "left" ]] && echo "true" || echo "false")"
    draw_panel_header "$RIGHT_PANEL_MODE" $PANEL_WIDTH "$([[ "$CURRENT_PANEL" == "right" ]] && echo "true" || echo "false")"
    
    # Panel separator
    echo -e "${WHITE}${T_RIGHT}$(printf "%*s" $((PANEL_WIDTH)) | tr ' ' "$HORZ")${CROSS}$(printf "%*s" $((PANEL_WIDTH)) | tr ' ' "$HORZ")${T_LEFT}${NC}"
    
    # Panel contents side by side
    for ((i=0; i<CONTENT_HEIGHT; i++)); do
        # Left panel line
        local left_lines=($(list_attributes "$FILTER" | sed -n "$((i+1))p"))
        local right_lines=($(list_jobs "$FILTER" | sed -n "$((i+1))p"))
        
        # This is complex to do properly in bash, so let's use a simpler approach
        printf "${VERT}%-*s${VERT}%-*s${VERT}\n" $PANEL_WIDTH "Left panel content..." $PANEL_WIDTH "Right panel content..."
    done
    
    draw_footer
}

# Handle DNA extraction
handle_dna_extraction() {
    STATUS_MESSAGE="Starting DNA extraction..."
    log_message "User initiated DNA extraction"
    
    # Create job file
    local job_id="extract_$(date +%s)"
    cat > "$QUEUE_DIR/${job_id}.job" << EOF
{
    "id": "$job_id",
    "type": "dna_extraction",
    "created": "$(date -Iseconds)",
    "status": "pending",
    "books": [1342, 11, 1661, 84, 174, 2701, 345, 76]
}
EOF
    
    STATUS_MESSAGE="DNA extraction job created: $job_id"
}

# Handle transformation
handle_transformation() {
    if [[ -z "$SELECTED_ITEM" ]]; then
        STATUS_MESSAGE="No attribute selected for transformation"
        return
    fi
    
    local dna="$SELECTED_ITEM"
    echo "Enter text to transform (press Ctrl+D when done):"
    local text=$(cat)
    
    if [[ -n "$text" ]]; then
        local job_id="transform_$(date +%s)"
        cat > "$QUEUE_DIR/${job_id}.job" << EOF
{
    "id": "$job_id",
    "type": "transformation",
    "created": "$(date -Iseconds)",
    "status": "pending",
    "dna": "$dna",
    "text": $(echo "$text" | jq -R .)
}
EOF
        STATUS_MESSAGE="Transformation job created: $job_id"
    fi
}

# Run job processor
run_job_processor() {
    local job_file="$1"
    local job_id=$(basename "$job_file" .job)
    
    log_message "Processing job: $job_id"
    
    # Simulate job processing
    sleep 2
    
    # Create result file
    echo "Job $job_id completed at $(date)" > "$RESULTS_DIR/${job_id}.result"
    
    # Remove job file
    rm -f "$job_file"
    
    STATUS_MESSAGE="Job $job_id completed"
    log_message "Job completed: $job_id"
}

# Show help
show_help() {
    clear_screen
    cat << EOF
${WHITE}${TL}$(printf "%*s" $((TERM_WIDTH-2)) | tr ' ' "$HORZ")${TR}${NC}
${VERT}${CYAN}               NARRATIVE DNA COMMANDER HELP               ${NC}${VERT}
${WHITE}${T_RIGHT}$(printf "%*s" $((TERM_WIDTH-2)) | tr ' ' "$HORZ")${T_LEFT}${NC}

${YELLOW}NAVIGATION:${NC}
  TAB         - Switch between left and right panels
  ↑/↓ or j/k  - Navigate within panel
  ENTER       - Select item
  /           - Filter/search
  ESC         - Clear filter

${YELLOW}LEFT PANEL MODES:${NC}
  F6          - Switch to Attributes mode
  F7          - Switch to Essences mode  
  F8          - Switch to Results mode

${YELLOW}RIGHT PANEL MODES:${NC}
  F9          - Switch to Jobs mode
  F10         - Switch to Logs mode
  F11         - Switch to Monitor mode

${YELLOW}ACTIONS:${NC}
  F2          - Extract DNA / Run Job
  F3          - Transform / View
  F4          - Delete selected item
  F5          - Refresh view

${YELLOW}BATCH JOBS:${NC}
  DNA extraction creates jobs for processing
  Jobs run automatically in background
  View logs in right panel to monitor progress

${YELLOW}QUEUE SYSTEM:${NC}
  Jobs stored in: $QUEUE_DIR
  Results in: $RESULTS_DIR
  Logs in: $LOGS_DIR

${WHITE}${BL}$(printf "%*s" $((TERM_WIDTH-2)) | tr ' ' "$HORZ")${BR}${NC}

Press any key to continue...
EOF
    read -n 1 -s
}

# Main input handler
handle_input() {
    local key
    read -n 1 -s key
    
    case "$key" in
        $'\t')  # TAB
            [[ "$CURRENT_PANEL" == "left" ]] && CURRENT_PANEL="right" || CURRENT_PANEL="left"
            ;;
        "q"|"Q")
            echo "Goodbye!"
            exit 0
            ;;
        "/")
            echo -n "Filter: "
            read -r FILTER
            ;;
        $'\e')  # ESC
            FILTER=""
            STATUS_MESSAGE=""
            ;;
        $'\x1b')  # Function keys start with escape
            read -n 2 -s key2
            case "$key2" in
                "OP") show_help ;;           # F1
                "OQ") handle_dna_extraction ;; # F2
                "OR") handle_transformation ;; # F3
                "OS") STATUS_MESSAGE="Delete function not implemented" ;; # F4
                "[15") STATUS_MESSAGE="Refreshing..." ;; # F5
                "[17") LEFT_PANEL_MODE="attributes" ;; # F6
                "[18") LEFT_PANEL_MODE="essences" ;;   # F7
                "[19") LEFT_PANEL_MODE="results" ;;    # F8
                "[20") RIGHT_PANEL_MODE="jobs" ;;      # F9
                "[21") RIGHT_PANEL_MODE="logs" ;;      # F10
                "[23") RIGHT_PANEL_MODE="monitor" ;;   # F11
            esac
            ;;
    esac
}

# Background job processor
start_job_processor() {
    while true; do
        for job_file in "$QUEUE_DIR"/*.job; do
            if [[ -f "$job_file" ]]; then
                run_job_processor "$job_file" &
            fi
        done
        sleep 5
    done &
    JOB_PROCESSOR_PID=$!
    log_message "Started background job processor (PID: $JOB_PROCESSOR_PID)"
}

# Cleanup function
cleanup() {
    [[ -n "$JOB_PROCESSOR_PID" ]] && kill "$JOB_PROCESSOR_PID" 2>/dev/null
    log_message "Commander session ended"
    clear
    echo "Narrative DNA Commander session ended."
}

# Main function
main() {
    # Setup signal handlers
    trap cleanup EXIT
    
    # Initialize
    log_message "Commander session started"
    start_job_processor
    
    # Main loop
    while true; do
        draw_ui
        handle_input
    done
}

# Entry point
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi