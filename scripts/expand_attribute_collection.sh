#!/bin/bash

# Expand Attribute Collection
# Add more books to grow the narrative DNA attribute library

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORK_DIR="${SCRIPT_DIR}/expanded_attributes_$(date +%Y%m%d_%H%M%S)"
LOG_FILE="${WORK_DIR}/expansion.log"
API_URL="http://localhost:8100"

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
NC='\033[0m'

# Logging function
log() {
    mkdir -p "$(dirname "$LOG_FILE")"
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Initialize workspace
init_workspace() {
    log "Initializing expanded attribute collection workspace: $WORK_DIR"
    mkdir -p "$WORK_DIR"
    
    # Test API connection
    if ! curl -s "${API_URL}/health" &> /dev/null; then
        echo "❌ Cannot connect to API at $API_URL"
        exit 1
    fi
    
    log "✓ Workspace initialized"
}

# Create strategic sampling job
create_sampling_job() {
    local gutenberg_id=$1
    
    local response=$(curl -s -X POST "${API_URL}/gutenberg/strategic-sample" \
        -H "Content-Type: application/json" \
        -d "{\"gutenberg_id\": $gutenberg_id, \"sample_count\": 64}")
    
    echo "$response" | jq -r '.data.job_id // empty'
}

# Wait for job completion with simple polling
wait_for_job() {
    local job_id=$1
    local max_wait=120
    local elapsed=0
    
    while [ $elapsed -lt $max_wait ]; do
        local status=$(curl -s "${API_URL}/gutenberg/jobs/$job_id" | jq -r '.status // "unknown"')
        
        case "$status" in
            "completed")
                return 0
                ;;
            "failed")
                echo "Job $job_id failed"
                return 1
                ;;
            *)
                printf "."
                sleep 5
                elapsed=$((elapsed + 5))
                ;;
        esac
    done
    
    echo "Job $job_id timed out"
    return 1
}

# Process a single book
process_book() {
    local gutenberg_id=$1
    local title=$2
    local author=$3
    
    echo -e "${CYAN}📖 Processing: $title by $author (ID: $gutenberg_id)${NC}"
    
    # Create sampling job
    local job_id=$(create_sampling_job "$gutenberg_id")
    
    if [ -z "$job_id" ]; then
        echo "   ❌ Failed to create sampling job"
        return 1
    fi
    
    echo "   Job ID: $job_id"
    printf "   Waiting for completion"
    
    if wait_for_job "$job_id"; then
        echo " ✅"
        
        # Create composite analysis
        local composite_response=$(curl -s -X POST "${API_URL}/gutenberg/composite-analysis?job_id=$job_id")
        local composite_job_id=$(echo "$composite_response" | jq -r '.data.composite_job_id // empty')
        
        if [ -n "$composite_job_id" ]; then
            printf "   Composite analysis"
            if wait_for_job "$composite_job_id"; then
                echo " ✅"
                
                # Get narrative DNA
                local dna_results=$(curl -s "${API_URL}/gutenberg/jobs/$composite_job_id/results")
                echo "$dna_results" > "$WORK_DIR/narrative_dna_$gutenberg_id.json"
                
                # Extract key attributes from the correct JSON path
                local persona=$(echo "$dna_results" | jq -r '.data.results.narrative_dna.dominant_persona.name // "unknown"')
                local namespace=$(echo "$dna_results" | jq -r '.data.results.narrative_dna.consistent_namespace.name // "unknown"')
                local style=$(echo "$dna_results" | jq -r '.data.results.narrative_dna.predominant_style.name // "unknown"')
                
                echo "   🧬 DNA: $persona | $namespace | $style"
                log "Extracted DNA for $title: $persona, $namespace, $style"
                
                # Add to attribute catalog
                echo "$gutenberg_id|$title|$author|$persona|$namespace|$style" >> "$WORK_DIR/attribute_catalog.txt"
                
                return 0
            else
                echo " ❌"
                return 1
            fi
        else
            echo "   ❌ Failed to create composite analysis"
            return 1
        fi
    else
        echo " ❌"
        return 1
    fi
}

# Main execution
main() {
    echo -e "${PURPLE}🧬 EXPANDING NARRATIVE DNA ATTRIBUTE COLLECTION${NC}"
    echo -e "${CYAN}Adding diverse literary works to grow the attribute library${NC}"
    echo
    
    init_workspace
    
    # Additional diverse books for attribute expansion
    declare -a books=(
        "2701:Moby Dick:Herman Melville"
        "1513:Romeo and Juliet:William Shakespeare"
        "345:Dracula:Bram Stoker"
        "215:The Call of the Wild:Jack London"
        "76:Adventures of Huckleberry Finn:Mark Twain"
        "1260:Jane Eyre:Charlotte Brontë"
        "105:Persuasion:Jane Austen"
        "35:The Time Machine:H.G. Wells"
    )
    
    # Initialize catalog
    echo "# Narrative DNA Attribute Catalog" > "$WORK_DIR/attribute_catalog.txt"
    echo "# Format: ID|Title|Author|Persona|Namespace|Style" >> "$WORK_DIR/attribute_catalog.txt"
    
    local successful=0
    local total=${#books[@]}
    
    for book in "${books[@]}"; do
        IFS=':' read -r gutenberg_id title author <<< "$book"
        
        if process_book "$gutenberg_id" "$title" "$author"; then
            successful=$((successful + 1))
        fi
        
        echo
        sleep 2  # Rate limiting
    done
    
    # Generate summary
    echo -e "${GREEN}📊 EXPANSION COMPLETE${NC}"
    echo "   Processed: $successful/$total books"
    echo "   Workspace: $WORK_DIR"
    echo
    
    # Show collected attributes
    if [ -f "$WORK_DIR/attribute_catalog.txt" ]; then
        echo -e "${CYAN}🎭 New Personas Discovered:${NC}"
        grep -v "^#" "$WORK_DIR/attribute_catalog.txt" | cut -d'|' -f4 | sort -u | sed 's/^/   • /'
        echo
        
        echo -e "${CYAN}🌍 New Namespaces Discovered:${NC}"
        grep -v "^#" "$WORK_DIR/attribute_catalog.txt" | cut -d'|' -f5 | sort -u | sed 's/^/   • /'
        echo
        
        echo -e "${CYAN}✍️ New Styles Discovered:${NC}"
        grep -v "^#" "$WORK_DIR/attribute_catalog.txt" | cut -d'|' -f6 | sort -u | sed 's/^/   • /'
        echo
    fi
    
    log "Attribute expansion completed: $successful/$total books processed"
}

# Execute
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi