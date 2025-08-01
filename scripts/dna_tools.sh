#!/bin/bash

# DNA Tools - Supporting utilities for Narrative DNA Commander
# Attribute management, batch processing, and system utilities

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
API_URL="http://localhost:8100"
RESULTS_DIR="$SCRIPT_DIR/results"
LOGS_DIR="$SCRIPT_DIR/logs"
QUEUE_DIR="$SCRIPT_DIR/queue"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Initialize directories
mkdir -p "$RESULTS_DIR" "$LOGS_DIR" "$QUEUE_DIR"

# Logging function
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S'): $1" | tee -a "$LOGS_DIR/dna_tools.log"
}

# API health check
check_api() {
    if ! curl -s "$API_URL/health" > /dev/null 2>&1; then
        echo -e "${RED}ERROR: API not available at $API_URL${NC}"
        echo "Please start the API server first:"
        echo "  cd $PROJECT_ROOT/humanizer_api/lighthouse"
        echo "  source venv/bin/activate"
        echo "  python api_enhanced.py"
        exit 1
    fi
}

# List available DNA attributes
list_attributes() {
    local format=${1:-"table"}
    
    if [[ ! -f "$RESULTS_DIR/attributes.json" ]]; then
        echo -e "${YELLOW}No attributes found. Run 'extract_dna' first.${NC}"
        return 1
    fi
    
    case "$format" in
        "table")
            echo -e "${CYAN}Available Narrative DNA Attributes:${NC}"
            echo "=================================================="
            printf "%-25s %-30s %-25s\n" "PERSONA" "NAMESPACE" "STYLE"
            echo "=================================================="
            jq -r '.[] | "\(.persona)|\(.namespace)|\(.style)"' "$RESULTS_DIR/attributes.json" | \
            while IFS='|' read -r persona namespace style; do
                printf "%-25s %-30s %-25s\n" "$persona" "$namespace" "$style"
            done
            ;;
        "json")
            jq . "$RESULTS_DIR/attributes.json"
            ;;
        "list")
            jq -r '.[] | "\(.persona)|\(.namespace)|\(.style)"' "$RESULTS_DIR/attributes.json"
            ;;
        "count")
            local count=$(jq length "$RESULTS_DIR/attributes.json")
            echo "Total DNA attributes: $count"
            ;;
    esac
}

# Extract DNA from books
extract_dna() {
    local books=("$@")
    
    if [[ ${#books[@]} -eq 0 ]]; then
        books=(1342 11 1661 84 174 2701 345 76)  # Default book set
    fi
    
    log "Starting DNA extraction from ${#books[@]} books"
    check_api
    
    local job_id="extract_$(date +%s)"
    local job_file="$QUEUE_DIR/${job_id}.job"
    
    # Create job file
    cat > "$job_file" << EOF
{
    "id": "$job_id",
    "type": "dna_extraction",
    "created": "$(date -Iseconds)",
    "status": "pending",
    "books": [$(IFS=','; echo "${books[*]}")]
}
EOF
    
    echo -e "${BLUE}Created DNA extraction job: $job_id${NC}"
    echo "Books to process: ${books[*]}"
    
    # Process immediately
    process_job "$job_file"
}

# Transform text using DNA
transform_text() {
    local dna="$1"
    local text="$2"
    local output_file="$3"
    
    if [[ -z "$dna" || -z "$text" ]]; then
        echo "Usage: transform_text 'persona|namespace|style' 'text to transform' [output_file]"
        return 1
    fi
    
    check_api
    
    IFS='|' read -r persona namespace style <<< "$dna"
    
    local job_id="transform_$(date +%s)"
    local job_file="$QUEUE_DIR/${job_id}.job"
    
    cat > "$job_file" << EOF
{
    "id": "$job_id",
    "type": "transformation",
    "created": "$(date -Iseconds)",
    "status": "pending",
    "persona": "$persona",
    "namespace": "$namespace", 
    "style": "$style",
    "text": $(echo "$text" | jq -R .),
    "output_file": "$output_file"
}
EOF
    
    echo -e "${BLUE}Created transformation job: $job_id${NC}"
    echo "DNA: $dna"
    
    # Process immediately
    process_job "$job_file"
}

# Process a job file
process_job() {
    local job_file="$1"
    local job_id=$(basename "$job_file" .job)
    
    if [[ ! -f "$job_file" ]]; then
        echo -e "${RED}Job file not found: $job_file${NC}"
        return 1
    fi
    
    local job_type=$(jq -r '.type' "$job_file")
    local log_file="$LOGS_DIR/${job_id}.log"
    
    log "Processing job: $job_id (type: $job_type)"
    echo -e "${YELLOW}Processing job: $job_id${NC}"
    
    case "$job_type" in
        "dna_extraction")
            process_dna_extraction_job "$job_file" > "$log_file" 2>&1
            ;;
        "transformation")
            process_transformation_job "$job_file" > "$log_file" 2>&1
            ;;
        *)
            echo "ERROR: Unknown job type: $job_type" > "$log_file"
            return 1
            ;;
    esac
    
    if [[ $? -eq 0 ]]; then
        echo -e "${GREEN}Job completed: $job_id${NC}"
        rm -f "$job_file"
    else
        echo -e "${RED}Job failed: $job_id${NC}"
        echo "Check log: $log_file"
    fi
}

# Process DNA extraction job
process_dna_extraction_job() {
    local job_file="$1"
    local job_id=$(basename "$job_file" .job)
    local books=$(jq -r '.books[]' "$job_file")
    
    echo "$(date): Starting DNA extraction for job $job_id"
    
    local temp_results=()
    
    for book_id in $books; do
        echo "$(date): Processing book $book_id"
        
        # Strategic sampling
        local sample_response=$(curl -s -X POST "$API_URL/gutenberg/strategic-sample" \
            -H "Content-Type: application/json" \
            -d "{\"book_id\": $book_id, \"target_paragraphs\": 64}")
        
        if [[ $? -ne 0 ]]; then
            echo "ERROR: Failed to get strategic sample for book $book_id"
            continue
        fi
        
        # Composite analysis
        local analysis_response=$(curl -s -X POST "$API_URL/gutenberg/composite-analysis" \
            -H "Content-Type: application/json" \
            -d "$sample_response")
        
        if [[ $? -ne 0 ]]; then
            echo "ERROR: Failed to analyze book $book_id"
            continue
        fi
        
        # Extract DNA
        local dna=$(echo "$analysis_response" | jq -r '.narrative_dna // empty')
        if [[ -n "$dna" ]]; then
            temp_results+=("$dna")
            echo "$(date): Extracted DNA from book $book_id: $dna"
        fi
    done
    
    # Save results
    if [[ ${#temp_results[@]} -gt 0 ]]; then
        printf '%s\n' "${temp_results[@]}" | jq -R 'split("|") | {persona: .[0], namespace: .[1], style: .[2]}' | \
        jq -s . > "$RESULTS_DIR/attributes.json"
        
        echo "$(date): Saved ${#temp_results[@]} DNA attributes to attributes.json"
        echo -e "${GREEN}DNA extraction completed successfully${NC}"
    else
        echo "ERROR: No DNA attributes extracted"
        return 1
    fi
}

# Process transformation job
process_transformation_job() {
    local job_file="$1"
    local job_id=$(basename "$job_file" .job)
    
    local persona=$(jq -r '.persona' "$job_file")
    local namespace=$(jq -r '.namespace' "$job_file")
    local style=$(jq -r '.style' "$job_file")
    local text=$(jq -r '.text' "$job_file")
    local output_file=$(jq -r '.output_file // empty' "$job_file")
    
    echo "$(date): Starting transformation for job $job_id"
    echo "DNA: $persona | $namespace | $style"
    
    # Call transformation API
    local transform_request=$(jq -n \
        --arg text "$text" \
        --arg persona "$persona" \
        --arg namespace "$namespace" \
        --arg style "$style" \
        '{
            text: $text,
            persona: $persona,
            namespace: $namespace,
            style: $style
        }')
    
    local transform_response=$(curl -s -X POST "$API_URL/transform" \
        -H "Content-Type: application/json" \
        -d "$transform_request")
    
    if [[ $? -ne 0 ]]; then
        echo "ERROR: Transformation API call failed"
        return 1
    fi
    
    # Extract transformed text
    local transformed=$(echo "$transform_response" | jq -r '.transformed_text // .result // empty')
    
    if [[ -z "$transformed" ]]; then
        echo "ERROR: No transformed text in response"
        echo "Response: $transform_response"
        return 1
    fi
    
    # Save result
    if [[ -n "$output_file" ]]; then
        echo "$transformed" > "$RESULTS_DIR/$output_file"
        echo "$(date): Saved transformation to $output_file"
    else
        local result_file="$RESULTS_DIR/${job_id}_result.txt"
        echo "$transformed" > "$result_file"
        echo "$(date): Saved transformation to $result_file"
    fi
    
    echo "$(date): Transformation completed successfully"
}

# Process all pending jobs
process_queue() {
    echo -e "${CYAN}Processing job queue...${NC}"
    
    local job_count=0
    for job_file in "$QUEUE_DIR"/*.job; do
        if [[ -f "$job_file" ]]; then
            process_job "$job_file"
            ((job_count++))
        fi
    done
    
    if [[ $job_count -eq 0 ]]; then
        echo "No pending jobs found."
    else
        echo -e "${GREEN}Processed $job_count jobs.${NC}"
    fi
}

# Show job status
job_status() {
    echo -e "${CYAN}Job Queue Status:${NC}"
    echo "=================="
    
    local pending=0
    local completed=0
    local failed=0
    
    # Count pending jobs
    for job_file in "$QUEUE_DIR"/*.job; do
        if [[ -f "$job_file" ]]; then
            ((pending++))
        fi
    done
    
    # Count completed/failed jobs from logs
    for log_file in "$LOGS_DIR"/*.log; do
        if [[ -f "$log_file" ]]; then
            if grep -q "completed successfully" "$log_file"; then
                ((completed++))
            elif grep -q "ERROR" "$log_file"; then
                ((failed++))
            fi
        fi
    done
    
    echo "Pending jobs: $pending"
    echo "Completed jobs: $completed"
    echo "Failed jobs: $failed"
    
    if [[ $pending -gt 0 ]]; then
        echo
        echo "Pending jobs:"
        for job_file in "$QUEUE_DIR"/*.job; do
            if [[ -f "$job_file" ]]; then
                local job_id=$(basename "$job_file" .job)
                local job_type=$(jq -r '.type' "$job_file")
                local created=$(jq -r '.created' "$job_file")
                echo "  $job_id ($job_type) - created $created"
            fi
        done
    fi
}

# Clean up old logs and results
cleanup() {
    local days=${1:-30}
    
    echo -e "${YELLOW}Cleaning up files older than $days days...${NC}"
    
    find "$LOGS_DIR" -name "*.log" -mtime +$days -delete 2>/dev/null || true
    find "$RESULTS_DIR" -name "*_result.txt" -mtime +$days -delete 2>/dev/null || true
    
    echo "Cleanup completed."
}

# Show help
show_help() {
    cat << EOF
DNA Tools - Narrative DNA Management Utilities

COMMANDS:
  list [format]           - List available DNA attributes
                           Formats: table, json, list, count
  
  extract [book_ids...]   - Extract DNA from books
                           Default books: 1342 11 1661 84 174 2701 345 76
  
  transform DNA TEXT [output] - Transform text using DNA
                               DNA format: 'persona|namespace|style'
  
  process [job_file]      - Process specific job or all pending jobs
  
  status                  - Show job queue status
  
  cleanup [days]          - Clean up old files (default: 30 days)

EXAMPLES:
  $0 list table
  $0 extract 1342 11 84
  $0 transform 'gothic_documenter|victorian_gothic_horror|gothic_realism' 'Hello world'
  $0 process
  $0 status

FILES:
  Attributes: $RESULTS_DIR/attributes.json
  Logs: $LOGS_DIR/
  Queue: $QUEUE_DIR/
  Results: $RESULTS_DIR/
EOF
}

# Main command dispatcher
main() {
    local command="$1"
    shift
    
    case "$command" in
        "list")
            list_attributes "$@"
            ;;
        "extract")
            extract_dna "$@"
            ;;
        "transform")
            transform_text "$@"
            ;;
        "process")
            if [[ $# -gt 0 ]]; then
                process_job "$1"
            else
                process_queue
            fi
            ;;
        "status")
            job_status
            ;;
        "cleanup")
            cleanup "$@"
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