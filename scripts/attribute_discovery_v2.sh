#!/bin/bash

# Enhanced Gutenberg Attribute Discovery Pipeline
# Extracts actual QNT attributes (persona, namespace, style, essence) from Gutenberg analysis

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORK_DIR="${SCRIPT_DIR}/attribute_analysis_$(date +%Y%m%d_%H%M%S)"
LOG_FILE="${WORK_DIR}/analysis.log"
TARGET_PARAGRAPHS=100
TARGET_ATTRIBUTES=64

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Logging function
log() {
    # Ensure log directory exists
    mkdir -p "$(dirname "$LOG_FILE")"
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

# Initialize workspace
init_workspace() {
    log "Initializing workspace: $WORK_DIR"
    mkdir -p "$WORK_DIR"
    
    # Check dependencies
    for cmd in jq humanizer curl; do
        if ! command -v "$cmd" &> /dev/null; then
            error_exit "$cmd is required but not installed"
        fi
    done
    
    # Test API connection
    if ! humanizer health &> /dev/null; then
        error_exit "Cannot connect to Humanizer API. Please ensure the API server is running."
    fi
    
    log "✓ Workspace initialized and dependencies verified"
}

# Discover diverse books for analysis
discover_books() {
    log "🔍 Discovering diverse Gutenberg books..."
    
    # Use a curated set of high-quality, diverse books
    local book_selections=(
        "1342:Pride and Prejudice:Jane Austen:Romance/Social Commentary"
        "74:The Adventures of Tom Sawyer:Mark Twain:Adventure/Coming of Age"
        "2701:Moby Dick:Herman Melville:Adventure/Philosophy"
        "1513:Romeo and Juliet:William Shakespeare:Drama/Tragedy"
        "84:Frankenstein:Mary Shelley:Gothic/Science Fiction"
        "11:Alice's Adventures in Wonderland:Lewis Carroll:Fantasy/Children's"
        "345:Dracula:Bram Stoker:Gothic/Horror"
        "174:The Picture of Dorian Gray:Oscar Wilde:Victorian/Philosophical"
        "215:The Call of the Wild:Jack London:Adventure/Nature"
        "408:The Souls of Black Folk:W.E.B. Du Bois:Philosophy/Social Commentary"
    )
    
    echo -e "${YELLOW}Selected books for diverse attribute discovery:${NC}"
    
    local book_ids=()
    for selection in "${book_selections[@]}"; do
        IFS=':' read -r id title author genre <<< "$selection"
        book_ids+=("$id")
        printf "  %s - %s (%s) [%s]\n" "$id" "$title" "$author" "$genre"
    done
    
    printf '%s\n' "${book_ids[@]}" > "$WORK_DIR/selected_books.txt"
    
    log "✓ Selected ${#book_ids[@]} diverse books for analysis"
    echo -e "${GREEN}✓ Book selection complete${NC}"
}

# Start Gutenberg analysis jobs
start_analysis_jobs() {
    log "🚀 Starting Gutenberg analysis jobs..."
    
    local book_ids=($(cat "$WORK_DIR/selected_books.txt"))
    local job_ids=()
    
    echo -e "${YELLOW}Starting analysis for ${#book_ids[@]} books...${NC}"
    
    for i in "${!book_ids[@]}"; do
        local book_id="${book_ids[$i]}"
        show_progress $((i + 1)) ${#book_ids[@]} "Starting jobs"
        
        # Start targeted analysis
        local job_output=$(humanizer gutenberg analyze "$book_id" --type targeted 2>/dev/null || echo "")
        local job_id=$(echo "$job_output" | grep -oE '[a-f0-9-]{36}' | head -1 || echo "")
        
        if [ -n "$job_id" ]; then
            job_ids+=("$job_id")
            echo "$job_id:$book_id" >> "$WORK_DIR/job_mapping.txt"
            log "Started job $job_id for book $book_id"
            sleep 2  # Rate limiting
        else
            log "⚠️  Failed to start job for book $book_id"
        fi
    done
    
    printf '%s\n' "${job_ids[@]}" > "$WORK_DIR/job_ids.txt"
    
    echo -e "\n${GREEN}✓ Started ${#job_ids[@]} analysis jobs${NC}"
    log "✓ Analysis jobs started successfully"
}

# Wait for jobs to complete
wait_for_completion() {
    log "⏳ Waiting for job completion..."
    
    local job_ids=($(cat "$WORK_DIR/job_ids.txt"))
    local max_wait=600  # 10 minutes
    local elapsed=0
    local check_interval=15
    
    echo -e "${YELLOW}Monitoring ${#job_ids[@]} jobs (max wait: ${max_wait}s)${NC}"
    
    while [ $elapsed -lt $max_wait ]; do
        local completed=0
        
        for job_id in "${job_ids[@]}"; do
            local status=$(curl -s "http://localhost:8100/gutenberg/jobs/$job_id" | jq -r '.data.status // "unknown"')
            if [ "$status" = "completed" ] || [ "$status" = "failed" ]; then
                completed=$((completed + 1))
            fi
        done
        
        show_progress $completed ${#job_ids[@]} "Job completion"
        
        if [ $completed -eq ${#job_ids[@]} ]; then
            echo -e "\n${GREEN}✓ All jobs completed${NC}"
            return 0
        fi
        
        sleep $check_interval
        elapsed=$((elapsed + check_interval))
    done
    
    echo -e "\n${YELLOW}⚠️  Some jobs may still be running after timeout${NC}"
    log "⚠️  Timeout reached, proceeding with available results"
}

# Extract paragraphs from completed jobs
extract_paragraphs() {
    log "📊 Extracting paragraphs from analysis results..."
    
    local job_ids=($(cat "$WORK_DIR/job_ids.txt"))
    local all_paragraphs="[]"
    local total_paragraphs=0
    
    echo -e "${YELLOW}Collecting paragraphs from ${#job_ids[@]} jobs...${NC}"
    
    for i in "${!job_ids[@]}"; do
        local job_id="${job_ids[$i]}"
        show_progress $((i + 1)) ${#job_ids[@]} "Extracting paragraphs"
        
        # Get job results from API
        local results=$(curl -s "http://localhost:8100/gutenberg/jobs/$job_id/results" | jq '.data.results // []')
        
        if [ "$results" != "[]" ] && [ "$results" != "null" ]; then
            # Add job info to each paragraph
            local enhanced_results=$(echo "$results" | jq --arg job_id "$job_id" '
                map(. + {"source_job": $job_id})
            ')
            
            # Merge into all_paragraphs
            all_paragraphs=$(echo "$all_paragraphs" | jq --argjson new_results "$enhanced_results" '. + $new_results')
            
            local count=$(echo "$results" | jq 'length')
            total_paragraphs=$((total_paragraphs + count))
            log "Collected $count paragraphs from job $job_id"
        fi
    done
    
    echo "$all_paragraphs" > "$WORK_DIR/extracted_paragraphs.json"
    
    echo -e "\n${GREEN}✓ Extracted $total_paragraphs paragraphs total${NC}"
    log "✓ Paragraph extraction complete"
}

# Perform QNT analysis on selected paragraphs
analyze_paragraphs() {
    log "🧠 Performing QNT analysis on paragraphs..."
    
    local paragraphs=$(cat "$WORK_DIR/extracted_paragraphs.json")
    local paragraph_count=$(echo "$paragraphs" | jq 'length')
    
    # Limit to target number for analysis
    if [ $paragraph_count -gt $TARGET_PARAGRAPHS ]; then
        paragraphs=$(echo "$paragraphs" | jq ".[0:$TARGET_PARAGRAPHS]")
        paragraph_count=$TARGET_PARAGRAPHS
        log "Limited analysis to $TARGET_PARAGRAPHS paragraphs"
    fi
    
    echo -e "${YELLOW}Analyzing $paragraph_count paragraphs with QNT...${NC}"
    
    local analyzed_paragraphs="[]"
    
    for i in $(seq 0 $((paragraph_count - 1))); do
        show_progress $((i + 1)) $paragraph_count "QNT Analysis"
        
        local paragraph=$(echo "$paragraphs" | jq -r ".[$i]")
        local text=$(echo "$paragraph" | jq -r '.paragraph_text')
        
        if [ -n "$text" ] && [ "$text" != "null" ] && [ ${#text} -gt 50 ]; then
            # Run QNT analysis on the paragraph
            local analysis_output=$(humanizer analyze "$text" --format json 2>/dev/null || echo '{}')
            
            if [ "$analysis_output" != "{}" ]; then
                # Combine original paragraph data with QNT analysis
                local enhanced_paragraph=$(echo "$paragraph" | jq --argjson analysis "$analysis_output" '. + {"qnt_analysis": $analysis}')
                analyzed_paragraphs=$(echo "$analyzed_paragraphs" | jq ". + [$enhanced_paragraph]")
                
                log "Completed QNT analysis for paragraph $((i + 1))"
            else
                log "⚠️  Failed QNT analysis for paragraph $((i + 1))"
            fi
            
            # Rate limiting
            sleep 1
        fi
    done
    
    echo "$analyzed_paragraphs" > "$WORK_DIR/qnt_analyzed_paragraphs.json"
    
    local success_count=$(echo "$analyzed_paragraphs" | jq 'length')
    echo -e "\n${GREEN}✓ Successfully analyzed $success_count paragraphs${NC}"
    log "✓ QNT analysis complete"
}

# Extract and organize attributes
extract_attributes() {
    log "🏗️  Extracting narrative attributes..."
    
    local analyzed_paragraphs=$(cat "$WORK_DIR/qnt_analyzed_paragraphs.json")
    local all_attributes="[]"
    
    echo -e "${YELLOW}Extracting attributes from analyzed paragraphs...${NC}"
    
    # Extract attributes using jq
    local extraction_script='
    [
        .[] | 
        select(.qnt_analysis != null) |
        {
            source: {
                paragraph_id: .paragraph_id,
                book_id: .book_id,
                text: .paragraph_text,
                enrichment_score: .attribute_enrichment_score
            },
            persona: {
                type: "persona",
                name: .qnt_analysis.persona.name,
                confidence: .qnt_analysis.persona.confidence,
                characteristics: .qnt_analysis.persona.characteristics,
                voice_indicators: .qnt_analysis.persona.voice_indicators
            },
            namespace: {
                type: "namespace", 
                name: .qnt_analysis.namespace.name,
                confidence: .qnt_analysis.namespace.confidence,
                domain_markers: .qnt_analysis.namespace.domain_markers,
                cultural_context: .qnt_analysis.namespace.cultural_context
            },
            style: {
                type: "style",
                name: .qnt_analysis.style.name,
                confidence: .qnt_analysis.style.confidence,
                linguistic_features: .qnt_analysis.style.linguistic_features,
                tone: .qnt_analysis.style.tone
            },
            essence: {
                type: "essence",
                core_meaning: .qnt_analysis.essence.core_meaning,
                confidence: .qnt_analysis.essence.meaning_density,
                invariant_elements: .qnt_analysis.essence.invariant_elements,
                coherence_score: .qnt_analysis.essence.coherence_score
            }
        }
    ]'
    
    all_attributes=$(echo "$analyzed_paragraphs" | jq "$extraction_script")
    
    echo "$all_attributes" > "$WORK_DIR/extracted_attributes.json"
    
    local attribute_count=$(echo "$all_attributes" | jq 'length')
    echo -e "${GREEN}✓ Extracted attributes from $attribute_count paragraphs${NC}"
    log "✓ Attribute extraction complete"
}

# Select best attributes for final set
select_best_attributes() {
    log "🏆 Selecting best $TARGET_ATTRIBUTES attributes..."
    
    local all_attributes=$(cat "$WORK_DIR/extracted_attributes.json")
    
    # Flatten all attribute types into a single array for selection
    local flattened_script='
    [
        .[] |
        [.persona, .namespace, .style, .essence] |
        map(
            . + {
                source_text: (.source.text // ""),
                source_book: (.source.book_id // 0),
                enrichment_score: (.source.enrichment_score // 0)
            }
        )
    ] | flatten |
    map(select(.name != null and .confidence != null and .confidence > 0.5)) |
    sort_by(.confidence) | reverse
    '
    
    local flattened_attributes=$(echo "$all_attributes" | jq "$flattened_script")
    
    # Select diverse subset ensuring representation from each type
    local selection_script='
    group_by(.type) as $groups |
    [
        $groups[] | 
        sort_by(.confidence) | reverse |
        .[0:16]  # Take top 16 of each type
    ] | 
    flatten |
    sort_by(.confidence) | reverse |
    .[0:'"$TARGET_ATTRIBUTES"']
    '
    
    local selected_attributes=$(echo "$flattened_attributes" | jq "$selection_script")
    
    echo "$selected_attributes" > "$WORK_DIR/final_attributes.json"
    
    local final_count=$(echo "$selected_attributes" | jq 'length')
    echo -e "${GREEN}✓ Selected $final_count high-quality attributes${NC}"
    log "✓ Final attribute selection complete"
}

# Generate comprehensive attribute report
generate_attribute_report() {
    log "📋 Generating comprehensive attribute report..."
    
    local attributes=$(cat "$WORK_DIR/final_attributes.json")
    local report_file="$WORK_DIR/attribute_report.md"
    
    # Calculate statistics
    local total_count=$(echo "$attributes" | jq 'length')
    local persona_count=$(echo "$attributes" | jq '[.[] | select(.type == "persona")] | length')
    local namespace_count=$(echo "$attributes" | jq '[.[] | select(.type == "namespace")] | length')
    local style_count=$(echo "$attributes" | jq '[.[] | select(.type == "style")] | length')
    local essence_count=$(echo "$attributes" | jq '[.[] | select(.type == "essence")] | length')
    
    local avg_confidence=$(echo "$attributes" | jq '[.[] | .confidence] | add / length')
    local min_confidence=$(echo "$attributes" | jq '[.[] | .confidence] | min')
    local max_confidence=$(echo "$attributes" | jq '[.[] | .confidence] | max')
    
    # Generate markdown report
    cat > "$report_file" <<EOF
# Gutenberg Narrative Attribute Discovery Report

**Generated:** $(date '+%Y-%m-%d %H:%M:%S')  
**Workspace:** $WORK_DIR  
**Total Attributes Discovered:** $total_count

## Executive Summary

This report documents the extraction of high-quality narrative attributes from Project Gutenberg literature using Quantum Narrative Theory (QNT) analysis. The attributes can be used for narrative projections, transformations, and content analysis.

## Attribute Breakdown

| Type | Count | Description |
|------|-------|-------------|
| Persona | $persona_count | Narrative voice and perspective characteristics |
| Namespace | $namespace_count | Cultural and domain context markers |
| Style | $style_count | Linguistic and rhetorical approaches |
| Essence | $essence_count | Core meaning and invariant elements |
| **Total** | **$total_count** | **Complete attribute set** |

## Quality Metrics

- **Average Confidence:** $(printf "%.3f" "$avg_confidence")
- **Minimum Confidence:** $(printf "%.3f" "$min_confidence")  
- **Maximum Confidence:** $(printf "%.3f" "$max_confidence")
- **Quality Threshold:** > 0.500 (all attributes meet this standard)

## Discovered Personas

$(echo "$attributes" | jq -r '.[] | select(.type == "persona") | "- **\(.name)** (confidence: \(.confidence | tostring | .[0:5]))"')

## Discovered Namespaces  

$(echo "$attributes" | jq -r '.[] | select(.type == "namespace") | "- **\(.name)** (confidence: \(.confidence | tostring | .[0:5]))"')

## Discovered Styles

$(echo "$attributes" | jq -r '.[] | select(.type == "style") | "- **\(.name)** (confidence: \(.confidence | tostring | .[0:5]))"')

## Discovered Essences

$(echo "$attributes" | jq -r '.[] | select(.type == "essence") | "- **\(.core_meaning // .name)** (confidence: \(.confidence | tostring | .[0:5]))"')

## Usage Examples

### For Narrative Transformations
\`\`\`bash
# Use discovered personas
humanizer transform "Your text here" --persona "$(echo "$attributes" | jq -r '.[] | select(.type == "persona") | .name' | head -1)"

# Use discovered namespaces  
humanizer transform "Your text here" --namespace "$(echo "$attributes" | jq -r '.[] | select(.type == "namespace") | .name' | head -1)"

# Use discovered styles
humanizer transform "Your text here" --style "$(echo "$attributes" | jq -r '.[] | select(.type == "style") | .name' | head -1)"
\`\`\`

### For Content Analysis
\`\`\`bash
# Analyze text and compare with discovered attributes
humanizer analyze "Your narrative text" --depth deep --format json
\`\`\`

## Data Files

- \`final_attributes.json\` - Complete attribute dataset (JSON format)
- \`extracted_attributes.json\` - Raw extracted attributes with source context
- \`qnt_analyzed_paragraphs.json\` - QNT analysis results for all paragraphs
- \`analysis.log\` - Detailed processing log

## Technical Details

### Source Material
- **Books Analyzed:** 10 diverse classic works
- **Paragraphs Processed:** $TARGET_PARAGRAPHS selected for variety
- **Analysis Method:** Quantum Narrative Theory (QNT) with 4-component extraction

### Selection Criteria
- Minimum confidence threshold: 0.500
- Balanced representation across attribute types
- Preference for higher confidence scores
- Text quality and length optimization

### Algorithm Transparency
Each attribute includes:
- Confidence score from QNT analysis
- Source text and book identification
- Detailed characteristic descriptions
- Cultural and linguistic context markers

---

**Generated by Humanizer Lighthouse Platform**  
*Combining quantum narrative theory with classic literature for advanced content analysis*
EOF

    echo -e "${GREEN}✓ Comprehensive report generated: $report_file${NC}"
    log "✓ Attribute report saved successfully"
}

# Display interactive summary
display_summary() {
    local attributes=$(cat "$WORK_DIR/final_attributes.json")
    local total_count=$(echo "$attributes" | jq 'length')
    
    echo
    echo -e "${PURPLE}╔══════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${PURPLE}║                    ATTRIBUTE DISCOVERY COMPLETE                              ║${NC}"
    echo -e "${PURPLE}╚══════════════════════════════════════════════════════════════════════════════╝${NC}"
    echo
    echo -e "${CYAN}📊 Summary Statistics:${NC}"
    echo -e "   Total Attributes: ${GREEN}$total_count${NC}"
    echo -e "   Personas: ${YELLOW}$(echo "$attributes" | jq '[.[] | select(.type == "persona")] | length')${NC}"
    echo -e "   Namespaces: ${YELLOW}$(echo "$attributes" | jq '[.[] | select(.type == "namespace")] | length')${NC}"
    echo -e "   Styles: ${YELLOW}$(echo "$attributes" | jq '[.[] | select(.type == "style")] | length')${NC}"
    echo -e "   Essences: ${YELLOW}$(echo "$attributes" | jq '[.[] | select(.type == "essence")] | length')${NC}"
    echo
    echo -e "${CYAN}🎯 Top Discovered Attributes:${NC}"
    echo
    echo -e "${YELLOW}Personas:${NC}"
    echo "$attributes" | jq -r '.[] | select(.type == "persona") | "  • \(.name) (confidence: \(.confidence | tostring | .[0:5]))"' | head -5
    echo
    echo -e "${YELLOW}Namespaces:${NC}"
    echo "$attributes" | jq -r '.[] | select(.type == "namespace") | "  • \(.name) (confidence: \(.confidence | tostring | .[0:5]))"' | head -5
    echo
    echo -e "${YELLOW}Styles:${NC}"
    echo "$attributes" | jq -r '.[] | select(.type == "style") | "  • \(.name) (confidence: \(.confidence | tostring | .[0:5]))"' | head -5
    echo
    echo -e "${CYAN}📁 Files Generated:${NC}"
    echo -e "   ${GREEN}$WORK_DIR/final_attributes.json${NC} - Ready-to-use attribute set"
    echo -e "   ${GREEN}$WORK_DIR/attribute_report.md${NC} - Comprehensive documentation"
    echo
    echo -e "${CYAN}🚀 Next Steps:${NC}"
    echo -e "   • Use attributes in transformations: ${YELLOW}humanizer transform \"text\" --persona \"persona_name\"${NC}"
    echo -e "   • Integrate into your QNT analysis workflows"
    echo -e "   • Build custom content classification systems"
    echo
}

# Main execution
main() {
    echo -e "${PURPLE}╔══════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${PURPLE}║                    Gutenberg Attribute Discovery Pipeline v2                 ║${NC}"
    echo -e "${PURPLE}║                                                                              ║${NC}"
    echo -e "${PURPLE}║          Extract real QNT attributes from classic literature                ║${NC}"
    echo -e "${PURPLE}╚══════════════════════════════════════════════════════════════════════════════╝${NC}"
    echo
    
    init_workspace
    discover_books
    start_analysis_jobs
    wait_for_completion
    extract_paragraphs
    analyze_paragraphs
    extract_attributes
    select_best_attributes
    generate_attribute_report
    display_summary
    
    log "✓ Attribute discovery pipeline completed successfully"
}

# Execute if run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi