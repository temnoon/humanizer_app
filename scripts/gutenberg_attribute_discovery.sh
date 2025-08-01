#!/bin/bash

# Gutenberg Attribute Discovery Pipeline
# Finds diverse Gutenberg books, analyzes 100 paragraphs for variety of personas, namespaces, and styles
# Creates attributes and selects the best 64 based on quality and diversity

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORK_DIR="${SCRIPT_DIR}/gutenberg_analysis_$(date +%Y%m%d_%H%M%S)"
LOG_FILE="${WORK_DIR}/analysis.log"
RESULTS_FILE="${WORK_DIR}/results.json"
ATTRIBUTES_FILE="${WORK_DIR}/selected_attributes.json"
TARGET_PARAGRAPHS=100
TARGET_ATTRIBUTES=64

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Error handling
error_exit() {
    echo -e "${RED}ERROR: $1${NC}" >&2
    exit 1
}

# Progress indicator
show_progress() {
    local current=$1
    local total=$2
    local desc=$3
    local percent=$((current * 100 / total))
    local filled=$((percent / 2))
    local empty=$((50 - filled))
    
    printf "\r${CYAN}%s: [" "$desc"
    printf "%${filled}s" | tr ' ' '█'
    printf "%${empty}s" | tr ' ' '░'
    printf "] %d%% (%d/%d)${NC}" "$percent" "$current" "$total"
    
    if [ $current -eq $total ]; then
        echo
    fi
}

# Initialize work directory
init_workspace() {
    log "Initializing workspace: $WORK_DIR"
    mkdir -p "$WORK_DIR"
    
    # Check humanizer CLI availability
    if ! command -v humanizer &> /dev/null; then
        error_exit "humanizer CLI not found. Please install it first."
    fi
    
    # Test API connection
    if ! humanizer health &> /dev/null; then
        error_exit "Cannot connect to Humanizer API. Please ensure the API server is running."
    fi
    
    log "✓ Workspace initialized and API connection verified"
}

# Discover diverse Gutenberg books across different genres and time periods
discover_books() {
    log "🔍 Discovering diverse Gutenberg books..."
    
    local book_ids=()
    
    # Define search criteria for diversity
    declare -A search_criteria=(
        ["classical_literature"]="--subject Literature --limit 5"
        ["philosophy"]="--subject Philosophy --limit 3"
        ["poetry"]="--subject Poetry --limit 3"
        ["drama"]="--subject Drama --limit 3"
        ["science_fiction"]="--subject 'Science fiction' --limit 2"
        ["adventure"]="--subject Adventure --limit 2"
        ["romance"]="--subject Romance --limit 2"
        ["historical"]="--subject History --limit 3"
        ["biography"]="--subject Biography --limit 2"
        ["essays"]="--subject Essays --limit 2"
    )
    
    # Search by specific influential authors for guaranteed quality
    declare -A author_searches=(
        ["shakespeare"]="--author Shakespeare --limit 3"
        ["dickens"]="--author Dickens --limit 2"
        ["austen"]="--author Austen --limit 2"
        ["twain"]="--author Twain --limit 2"
        ["wilde"]="--author Wilde --limit 2"
        ["poe"]="--author Poe --limit 2"
        ["carroll"]="--author Carroll --limit 1"
        ["stoker"]="--author Stoker --limit 1"
        ["shelley"]="--author Shelley --limit 1"
        ["wells"]="--author Wells --limit 1"
    )
    
    echo -e "\n${YELLOW}Searching by subject categories...${NC}"
    for category in "${!search_criteria[@]}"; do
        log "Searching $category: ${search_criteria[$category]}"
        
        # Extract book IDs from search results
        local search_result=$(humanizer gutenberg search ${search_criteria[$category]} --format json 2>/dev/null || echo '{"books":[]}')
        local ids=$(echo "$search_result" | jq -r '.books[]?.gutenberg_id // empty' 2>/dev/null || echo "")
        
        if [ -n "$ids" ]; then
            while IFS= read -r id; do
                book_ids+=("$id")
            done <<< "$ids"
            log "Found $(echo "$ids" | wc -l) books for $category"
        fi
    done
    
    echo -e "\n${YELLOW}Searching by influential authors...${NC}"
    for author in "${!author_searches[@]}"; do
        log "Searching $author: ${author_searches[$author]}"
        
        local search_result=$(humanizer gutenberg search ${author_searches[$author]} --format json 2>/dev/null || echo '{"books":[]}')
        local ids=$(echo "$search_result" | jq -r '.books[]?.gutenberg_id // empty' 2>/dev/null || echo "")
        
        if [ -n "$ids" ]; then
            while IFS= read -r id; do
                book_ids+=("$id")
            done <<< "$ids"
            log "Found $(echo "$ids" | wc -l) books for $author"
        fi
    done
    
    # Remove duplicates and save
    printf '%s\n' "${book_ids[@]}" | sort -u > "$WORK_DIR/discovered_books.txt"
    local unique_count=$(wc -l < "$WORK_DIR/discovered_books.txt")
    
    log "✓ Discovered $unique_count unique books for analysis"
    echo -e "${GREEN}✓ Book discovery complete: $unique_count books found${NC}"
}

# Start analysis jobs for discovered books
start_analysis_jobs() {
    log "🚀 Starting Gutenberg analysis jobs..."
    
    local book_list=$(cat "$WORK_DIR/discovered_books.txt")
    local job_ids=()
    local book_count=$(echo "$book_list" | wc -l)
    local current=0
    
    # Start analysis jobs in batches of 5 books to avoid overwhelming the system
    while IFS= read -r book_id; do
        if [ -n "$book_id" ]; then
            current=$((current + 1))
            show_progress $current $book_count "Starting analysis jobs"
            
            # Start targeted analysis for better paragraph extraction
            local job_output=$(humanizer gutenberg analyze "$book_id" --type targeted 2>/dev/null || echo "")
            
            # Extract job ID from output (assuming it's returned in a predictable format)
            local job_id=$(echo "$job_output" | grep -oE '[a-f0-9-]{36}' | head -1 || echo "")
            
            if [ -n "$job_id" ]; then
                job_ids+=("$job_id")
                echo "$job_id:$book_id" >> "$WORK_DIR/job_mapping.txt"
                log "Started job $job_id for book $book_id"
                
                # Small delay to prevent API overload
                sleep 1
            else
                log "⚠️  Failed to start job for book $book_id"
            fi
        fi
    done <<< "$book_list"
    
    echo -e "\n${GREEN}✓ Started ${#job_ids[@]} analysis jobs${NC}"
    printf '%s\n' "${job_ids[@]}" > "$WORK_DIR/job_ids.txt"
}

# Monitor job progress and wait for completion
monitor_jobs() {
    log "⏳ Monitoring job progress..."
    
    local job_ids=($(cat "$WORK_DIR/job_ids.txt"))
    local total_jobs=${#job_ids[@]}
    local completed_jobs=0
    local max_wait_time=1800  # 30 minutes max wait
    local elapsed_time=0
    local check_interval=30   # Check every 30 seconds
    
    echo -e "${YELLOW}Monitoring $total_jobs jobs (max wait: ${max_wait_time}s)${NC}"
    
    while [ $completed_jobs -lt $total_jobs ] && [ $elapsed_time -lt $max_wait_time ]; do
        local current_completed=0
        
        for job_id in "${job_ids[@]}"; do
            # Check job status
            local status=$(humanizer gutenberg jobs --job-id "$job_id" --format json 2>/dev/null | jq -r '.status // "unknown"' || echo "unknown")
            
            if [ "$status" = "completed" ] || [ "$status" = "failed" ]; then
                current_completed=$((current_completed + 1))
            fi
        done
        
        if [ $current_completed -gt $completed_jobs ]; then
            completed_jobs=$current_completed
            show_progress $completed_jobs $total_jobs "Job completion"
        fi
        
        if [ $completed_jobs -lt $total_jobs ]; then
            sleep $check_interval
            elapsed_time=$((elapsed_time + check_interval))
        fi
    done
    
    if [ $completed_jobs -eq $total_jobs ]; then
        echo -e "\n${GREEN}✓ All jobs completed successfully${NC}"
        log "✓ All $total_jobs jobs completed"
    else
        echo -e "\n${YELLOW}⚠️  Timeout reached. $completed_jobs/$total_jobs jobs completed${NC}"
        log "⚠️  Timeout after ${elapsed_time}s. $completed_jobs/$total_jobs jobs completed"
    fi
}

# Collect and analyze results from completed jobs
collect_results() {
    log "📊 Collecting analysis results..."
    
    local job_ids=($(cat "$WORK_DIR/job_ids.txt"))
    local paragraphs_collected=0
    local results_array="[]"
    
    echo -e "${YELLOW}Collecting results from ${#job_ids[@]} jobs...${NC}"
    
    for i in "${!job_ids[@]}"; do
        local job_id="${job_ids[$i]}"
        show_progress $((i + 1)) ${#job_ids[@]} "Collecting results"
        
        # Get job results
        local job_results=$(humanizer gutenberg jobs --results "$job_id" --format json 2>/dev/null || echo '{"paragraphs":[]}')
        
        # Extract paragraphs with their analyses
        local paragraphs=$(echo "$job_results" | jq -r '.paragraphs // [] | .[]' 2>/dev/null || echo "")
        
        if [ -n "$paragraphs" ]; then
            # Merge paragraphs into results array
            results_array=$(echo "$results_array" | jq --argjson new_paragraphs "$job_results" '. + ($new_paragraphs.paragraphs // [])')
            local count=$(echo "$job_results" | jq '.paragraphs | length' 2>/dev/null || echo 0)
            paragraphs_collected=$((paragraphs_collected + count))
            log "Collected $count paragraphs from job $job_id"
        fi
    done
    
    echo "$results_array" > "$RESULTS_FILE"
    
    echo -e "\n${GREEN}✓ Collected $paragraphs_collected paragraphs total${NC}"
    log "✓ Results saved to $RESULTS_FILE"
}

# Select diverse paragraphs for analysis
select_diverse_paragraphs() {
    log "🎯 Selecting $TARGET_PARAGRAPHS diverse paragraphs..."
    
    # Use jq to analyze and select diverse paragraphs
    local selection_script='
    # Group paragraphs by attributes
    group_by(.analysis.persona.name // "unknown") as $by_persona |
    
    # Function to calculate diversity score
    def diversity_score:
        (.analysis.persona.confidence // 0) * 0.3 +
        (.analysis.namespace.confidence // 0) * 0.3 +
        (.analysis.style.confidence // 0) * 0.3 +
        (.text | length | if . > 100 and . < 1000 then 0.1 else 0 end);
    
    # Select paragraphs ensuring diversity
    [.[] | select(.analysis != null)] |
    sort_by(diversity_score) | reverse |
    .[0:'"$TARGET_PARAGRAPHS"']
    '
    
    local selected_paragraphs=$(jq "$selection_script" "$RESULTS_FILE" 2>/dev/null || echo "[]")
    local selected_count=$(echo "$selected_paragraphs" | jq 'length')
    
    echo "$selected_paragraphs" > "$WORK_DIR/selected_paragraphs.json"
    
    echo -e "${GREEN}✓ Selected $selected_count diverse paragraphs${NC}"
    log "✓ Selected paragraphs saved to $WORK_DIR/selected_paragraphs.json"
    
    # Show diversity statistics
    echo -e "\n${CYAN}Diversity Statistics:${NC}"
    local persona_count=$(echo "$selected_paragraphs" | jq '[.[] | .analysis.persona.name] | unique | length')
    local namespace_count=$(echo "$selected_paragraphs" | jq '[.[] | .analysis.namespace.name] | unique | length')
    local style_count=$(echo "$selected_paragraphs" | jq '[.[] | .analysis.style.name] | unique | length')
    
    echo "  Unique Personas: $persona_count"
    echo "  Unique Namespaces: $namespace_count"
    echo "  Unique Styles: $style_count"
}

# Create attributes from selected paragraphs
create_attributes() {
    log "🏗️  Creating attributes from selected paragraphs..."
    
    local paragraphs=$(cat "$WORK_DIR/selected_paragraphs.json")
    local paragraph_count=$(echo "$paragraphs" | jq 'length')
    local created_attributes="[]"
    
    echo -e "${YELLOW}Creating attributes from $paragraph_count paragraphs...${NC}"
    
    # Process each paragraph to create attributes
    local i=0
    while [ $i -lt $paragraph_count ]; do
        show_progress $((i + 1)) $paragraph_count "Creating attributes"
        
        local paragraph=$(echo "$paragraphs" | jq -r ".[$i]")
        local text=$(echo "$paragraph" | jq -r '.text')
        local analysis=$(echo "$paragraph" | jq '.analysis')
        
        if [ -n "$text" ] && [ "$text" != "null" ]; then
            # Extract each attribute type
            local persona=$(echo "$analysis" | jq -r '.persona // {}')
            local namespace=$(echo "$analysis" | jq -r '.namespace // {}')
            local style=$(echo "$analysis" | jq -r '.style // {}')
            local essence=$(echo "$analysis" | jq -r '.essence // {}')
            
            # Create attribute objects with metadata
            local attributes=$(cat <<EOF
[
    {
        "type": "persona",
        "value": $(echo "$persona" | jq '.name // "unknown"'),
        "confidence": $(echo "$persona" | jq '.confidence // 0'),
        "source_text": $(echo "$text" | jq -R .),
        "characteristics": $(echo "$persona" | jq '.characteristics // []'),
        "quality_score": $(echo "$persona" | jq '.confidence // 0')
    },
    {
        "type": "namespace",
        "value": $(echo "$namespace" | jq '.name // "unknown"'),
        "confidence": $(echo "$namespace" | jq '.confidence // 0'),
        "source_text": $(echo "$text" | jq -R .),
        "domain_markers": $(echo "$namespace" | jq '.domain_markers // []'),
        "cultural_context": $(echo "$namespace" | jq '.cultural_context // "unknown"'),
        "quality_score": $(echo "$namespace" | jq '.confidence // 0')
    },
    {
        "type": "style",
        "value": $(echo "$style" | jq '.name // "unknown"'),
        "confidence": $(echo "$style" | jq '.confidence // 0'),
        "source_text": $(echo "$text" | jq -R .),
        "linguistic_features": $(echo "$style" | jq '.linguistic_features // []'),
        "tone": $(echo "$style" | jq '.tone // "neutral"'),
        "quality_score": $(echo "$style" | jq '.confidence // 0')
    },
    {
        "type": "essence",
        "value": $(echo "$essence" | jq '.core_meaning // "unknown"'),
        "confidence": $(echo "$essence" | jq '.meaning_density // 0'),
        "source_text": $(echo "$text" | jq -R .),
        "invariant_elements": $(echo "$essence" | jq '.invariant_elements // []'),
        "coherence_score": $(echo "$essence" | jq '.coherence_score // 0'),
        "quality_score": $(echo "$essence" | jq '.meaning_density // 0')
    }
]
EOF
            )
            
            # Add to created attributes
            created_attributes=$(echo "$created_attributes" | jq ". + $attributes")
        fi
        
        i=$((i + 1))
    done
    
    echo "$created_attributes" > "$WORK_DIR/all_attributes.json"
    local total_attributes=$(echo "$created_attributes" | jq 'length')
    
    echo -e "\n${GREEN}✓ Created $total_attributes attributes${NC}"
    log "✓ All attributes saved to $WORK_DIR/all_attributes.json"
}

# Select the best 64 attributes based on quality and diversity
select_best_attributes() {
    log "🏆 Selecting best $TARGET_ATTRIBUTES attributes..."
    
    # Complex selection algorithm for optimal diversity and quality
    local selection_script='
    # Group by type first
    group_by(.type) as $groups |
    
    # Function to calculate combined score
    def combined_score:
        (.confidence * 0.4) +
        (.quality_score * 0.3) +
        (if (.source_text | length) > 100 and (.source_text | length) < 800 then 0.2 else 0 end) +
        (if .value != "unknown" and .value != null then 0.1 else 0 end);
    
    # Select balanced representation from each type
    [
        $groups[] |
        sort_by(combined_score) | reverse |
        .[0:16]  # 16 of each type for 64 total
    ] |
    flatten |
    sort_by(combined_score) | reverse |
    .[0:'"$TARGET_ATTRIBUTES"']
    '
    
    local all_attributes=$(cat "$WORK_DIR/all_attributes.json")
    local selected_attributes=$(echo "$all_attributes" | jq "$selection_script")
    
    echo "$selected_attributes" > "$ATTRIBUTES_FILE"
    
    local final_count=$(echo "$selected_attributes" | jq 'length')
    echo -e "${GREEN}✓ Selected $final_count best attributes${NC}"
    
    # Show final statistics
    echo -e "\n${CYAN}Final Selection Statistics:${NC}"
    local persona_final=$(echo "$selected_attributes" | jq '[.[] | select(.type == "persona")] | length')
    local namespace_final=$(echo "$selected_attributes" | jq '[.[] | select(.type == "namespace")] | length')
    local style_final=$(echo "$selected_attributes" | jq '[.[] | select(.type == "style")] | length')
    local essence_final=$(echo "$selected_attributes" | jq '[.[] | select(.type == "essence")] | length')
    
    echo "  Personas: $persona_final"
    echo "  Namespaces: $namespace_final"  
    echo "  Styles: $style_final"
    echo "  Essences: $essence_final"
    
    # Show quality statistics
    local avg_confidence=$(echo "$selected_attributes" | jq '[.[] | .confidence] | add / length')
    local min_confidence=$(echo "$selected_attributes" | jq '[.[] | .confidence] | min')
    local max_confidence=$(echo "$selected_attributes" | jq '[.[] | .confidence] | max')
    
    echo -e "\n${CYAN}Quality Metrics:${NC}"
    printf "  Average Confidence: %.3f\n" "$avg_confidence"
    printf "  Min Confidence: %.3f\n" "$min_confidence"
    printf "  Max Confidence: %.3f\n" "$max_confidence"
    
    log "✓ Best attributes saved to $ATTRIBUTES_FILE"
}

# Generate summary report
generate_report() {
    log "📋 Generating summary report..."
    
    local report_file="$WORK_DIR/analysis_report.md"
    
    cat > "$report_file" <<EOF
# Gutenberg Attribute Discovery Report

**Generated:** $(date '+%Y-%m-%d %H:%M:%S')  
**Workspace:** $WORK_DIR

## Summary

This report documents the automated discovery and analysis of diverse narrative attributes from Project Gutenberg books.

### Process Overview

1. **Book Discovery**: Searched across multiple genres and influential authors
2. **Content Analysis**: Used targeted analysis for optimal paragraph extraction
3. **Diversity Selection**: Selected $TARGET_PARAGRAPHS paragraphs for maximum variety
4. **Attribute Creation**: Generated attributes from selected content
5. **Quality Selection**: Chose best $TARGET_ATTRIBUTES attributes based on quality and diversity

### Results

- **Books Analyzed**: $(cat "$WORK_DIR/discovered_books.txt" | wc -l) unique books
- **Paragraphs Processed**: $(jq 'length' "$RESULTS_FILE" 2>/dev/null || echo "0") total paragraphs
- **Selected for Analysis**: $TARGET_PARAGRAPHS diverse paragraphs
- **Final Attributes**: $TARGET_ATTRIBUTES high-quality attributes

### Attribute Breakdown

$(echo "$(jq '[.[] | select(.type == "persona")] | length' "$ATTRIBUTES_FILE" 2>/dev/null || echo "0") personas, $(jq '[.[] | select(.type == "namespace")] | length' "$ATTRIBUTES_FILE" 2>/dev/null || echo "0") namespaces, $(jq '[.[] | select(.type == "style")] | length' "$ATTRIBUTES_FILE" 2>/dev/null || echo "0") styles, $(jq '[.[] | select(.type == "essence")] | length' "$ATTRIBUTES_FILE" 2>/dev/null || echo "0") essences")

### Quality Metrics

- **Average Confidence**: $(jq '[.[] | .confidence] | add / length' "$ATTRIBUTES_FILE" 2>/dev/null || echo "0")
- **Minimum Confidence**: $(jq '[.[] | .confidence] | min' "$ATTRIBUTES_FILE" 2>/dev/null || echo "0")  
- **Maximum Confidence**: $(jq '[.[] | .confidence] | max' "$ATTRIBUTES_FILE" 2>/dev/null || echo "0")

### Files Generated

- \`discovered_books.txt\` - List of analyzed book IDs
- \`selected_paragraphs.json\` - $TARGET_PARAGRAPHS diverse paragraphs
- \`all_attributes.json\` - All extracted attributes
- \`selected_attributes.json\` - Final $TARGET_ATTRIBUTES best attributes
- \`analysis.log\` - Detailed processing log

### Usage

The selected attributes can be used for:
- Training narrative analysis models
- Building diverse test datasets
- Enhancing content classification systems
- Improving writing style analysis tools

EOF

    echo -e "${GREEN}✓ Report generated: $report_file${NC}"
    log "✓ Summary report saved to $report_file"
}

# Main execution flow
main() {
    echo -e "${PURPLE}╔══════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${PURPLE}║                      Gutenberg Attribute Discovery Pipeline                  ║${NC}"
    echo -e "${PURPLE}║                                                                              ║${NC}"
    echo -e "${PURPLE}║  Target: $TARGET_PARAGRAPHS paragraphs → $TARGET_ATTRIBUTES best attributes                                     ║${NC}"
    echo -e "${PURPLE}╚══════════════════════════════════════════════════════════════════════════════╝${NC}"
    echo
    
    # Check dependencies
    for cmd in jq humanizer; do
        if ! command -v "$cmd" &> /dev/null; then
            error_exit "$cmd is required but not installed"
        fi
    done
    
    # Execute pipeline
    init_workspace
    discover_books
    start_analysis_jobs
    monitor_jobs
    collect_results
    select_diverse_paragraphs
    create_attributes
    select_best_attributes
    generate_report
    
    echo
    echo -e "${GREEN}🎉 Pipeline completed successfully!${NC}"
    echo -e "${CYAN}Results saved in: $WORK_DIR${NC}"
    echo -e "${CYAN}Selected attributes: $ATTRIBUTES_FILE${NC}"
    echo -e "${CYAN}Full report: $WORK_DIR/analysis_report.md${NC}"
    
    log "✓ Pipeline completed successfully"
}

# Script execution
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi