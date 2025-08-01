#!/bin/bash

# Narrative DNA Extractor
# Strategic paragraph sampling and composite analysis to extract the narrative DNA of classic books

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORK_DIR="${SCRIPT_DIR}/narrative_dna_$(date +%Y%m%d_%H%M%S)"
LOG_FILE="${WORK_DIR}/narrative_dna.log"
API_URL="http://localhost:8100"

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
    log "Initializing Narrative DNA Extraction workspace: $WORK_DIR"
    mkdir -p "$WORK_DIR"
    
    # Check dependencies
    for cmd in jq curl; do
        if ! command -v "$cmd" &> /dev/null; then
            error_exit "$cmd is required but not installed"
        fi
    done
    
    # Test API connection
    if ! curl -s "${API_URL}/health" &> /dev/null; then
        error_exit "Cannot connect to Humanizer API at $API_URL. Please ensure the API server is running."
    fi
    
    log "✓ Workspace initialized and API connection verified"
}

# Request strategic paragraph sampling for a book
create_strategic_sampling_job() {
    local gutenberg_id=$1
    local sample_count=${2:-64}
    local min_length=${3:-100}
    local max_length=${4:-800}
    
    log "Creating strategic sampling job for book $gutenberg_id"
    
    local request_data=$(cat <<EOF
{
    "gutenberg_id": $gutenberg_id,
    "sample_count": $sample_count,
    "min_length": $min_length,
    "max_length": $max_length,
    "avoid_first_last_percent": 0.15
}
EOF
    )
    
    local response=$(curl -s -X POST "${API_URL}/gutenberg/strategic-sample" \
        -H "Content-Type: application/json" \
        -d "$request_data")
    
    local job_id=$(echo "$response" | jq -r '.data.job_id // empty')
    
    if [ -z "$job_id" ]; then
        error_exit "Failed to create strategic sampling job for book $gutenberg_id"
    fi
    
    echo "$job_id"
}

# Wait for job completion
wait_for_job_completion() {
    local job_id=$1
    local max_wait=${2:-300}  # 5 minutes default
    local elapsed=0
    local check_interval=5
    
    log "Waiting for job $job_id to complete (max wait: ${max_wait}s)"
    
    while [ $elapsed -lt $max_wait ]; do
        local status=$(curl -s "${API_URL}/gutenberg/jobs/$job_id" | jq -r '.data.status // "unknown"')
        local progress=$(curl -s "${API_URL}/gutenberg/jobs/$job_id" | jq -r '.data.progress // 0')
        
        case "$status" in
            "completed")
                echo -e "\n${GREEN}✓ Job $job_id completed successfully${NC}"
                return 0
                ;;
            "failed")
                local error_msg=$(curl -s "${API_URL}/gutenberg/jobs/$job_id" | jq -r '.data.error_message // "Unknown error"')
                error_exit "Job $job_id failed: $error_msg"
                ;;
            "running")
                printf "\r${YELLOW}⏳ Job progress: %.1f%% (elapsed: ${elapsed}s)${NC}" "$(echo "$progress * 100" | bc -l 2>/dev/null || echo "0")"
                ;;
            *)
                printf "\r${CYAN}⏳ Job status: $status (elapsed: ${elapsed}s)${NC}"
                ;;
        esac
        
        sleep $check_interval
        elapsed=$((elapsed + check_interval))
    done
    
    error_exit "Job $job_id timed out after ${max_wait} seconds"
}

# Get job results
get_job_results() {
    local job_id=$1
    
    log "Retrieving results for job $job_id"
    
    local results=$(curl -s "${API_URL}/gutenberg/jobs/$job_id/results")
    local success=$(echo "$results" | jq -r '.success // false')
    
    if [ "$success" != "true" ]; then
        error_exit "Failed to retrieve results for job $job_id"
    fi
    
    echo "$results"
}

# Create composite analysis job
create_composite_analysis_job() {
    local source_job_id=$1
    
    log "Creating composite analysis job from source $source_job_id"
    
    local response=$(curl -s -X POST "${API_URL}/gutenberg/composite-analysis?job_id=$source_job_id")
    local composite_job_id=$(echo "$response" | jq -r '.data.composite_job_id // empty')
    
    if [ -z "$composite_job_id" ]; then
        error_exit "Failed to create composite analysis job"
    fi
    
    echo "$composite_job_id"
}

# Extract narrative DNA from a single book
extract_narrative_dna() {
    local gutenberg_id=$1
    local book_title=$2
    
    echo -e "${PURPLE}📖 Extracting Narrative DNA from: $book_title (ID: $gutenberg_id)${NC}"
    echo
    
    # Step 1: Strategic paragraph sampling
    echo -e "${YELLOW}🎯 Step 1: Strategic Paragraph Sampling${NC}"
    local sampling_job_id=$(create_strategic_sampling_job "$gutenberg_id" 64 150 600)
    echo "Sampling job ID: $sampling_job_id"
    
    # Wait for sampling completion
    wait_for_job_completion "$sampling_job_id" 180
    
    # Step 2: Get sampling results
    echo -e "${YELLOW}📊 Step 2: Retrieving Strategic Samples${NC}"
    local sampling_results=$(get_job_results "$sampling_job_id")
    echo "$sampling_results" > "$WORK_DIR/sampling_results_$gutenberg_id.json"
    
    # Display sampling summary
    local total_paragraphs=$(echo "$sampling_results" | jq '.data.results.sampling_metadata.total_sampled // 0')
    local position_range=$(echo "$sampling_results" | jq -r '.data.results.sampling_metadata.position_range // "unknown"')
    local avg_length=$(echo "$sampling_results" | jq '.data.results.sampling_metadata.avg_paragraph_length // 0')
    
    echo "  ✓ Extracted $total_paragraphs strategic paragraphs"
    echo "  ✓ Position range: $position_range"
    echo "  ✓ Average length: $(printf "%.0f" "$avg_length") characters"
    echo
    
    # Step 3: Composite analysis
    echo -e "${YELLOW}🧬 Step 3: Composite Analysis (Narrative DNA Extraction)${NC}"
    local composite_job_id=$(create_composite_analysis_job "$sampling_job_id")
    echo "Composite analysis job ID: $composite_job_id"
    
    # Wait for composite analysis completion
    wait_for_job_completion "$composite_job_id" 240
    
    # Step 4: Get narrative DNA results
    echo -e "${YELLOW}🧪 Step 4: Retrieving Narrative DNA${NC}"
    local dna_results=$(get_job_results "$composite_job_id")
    echo "$dna_results" > "$WORK_DIR/narrative_dna_$gutenberg_id.json"
    
    # Extract and display narrative DNA
    local narrative_dna=$(echo "$dna_results" | jq '.data.results.narrative_dna')
    
    echo -e "${GREEN}✅ Narrative DNA Extraction Complete!${NC}"
    echo
    
    # Display results
    display_narrative_dna "$narrative_dna" "$book_title" "$gutenberg_id"
    
    # Save individual report
    generate_book_report "$narrative_dna" "$book_title" "$gutenberg_id" "$sampling_results" "$dna_results"
    
    echo "$composite_job_id"
}

# Display narrative DNA results
display_narrative_dna() {
    local narrative_dna=$1
    local book_title=$2
    local gutenberg_id=$3
    
    echo -e "${CYAN}🧬 NARRATIVE DNA: $book_title${NC}"
    echo "════════════════════════════════════════════════════════"
    echo
    
    # Dominant Persona
    local persona_name=$(echo "$narrative_dna" | jq -r '.dominant_persona.name // "unknown"')
    local persona_conf=$(echo "$narrative_dna" | jq '.dominant_persona.confidence // 0')
    local persona_freq=$(echo "$narrative_dna" | jq '.dominant_persona.frequency // 0')
    
    echo -e "${YELLOW}🎭 DOMINANT PERSONA:${NC}"
    echo "  Name: $persona_name"
    echo "  Confidence: $(printf "%.1f%%" "$(echo "$persona_conf * 100" | bc -l)")"
    echo "  Frequency: $(printf "%.1f%%" "$(echo "$persona_freq * 100" | bc -l)")"
    echo "  Characteristics: $(echo "$narrative_dna" | jq -r '.dominant_persona.characteristics[]?' | tr '\n' ',' | sed 's/,$//' | sed 's/,/, /g')"
    echo
    
    # Consistent Namespace
    local namespace_name=$(echo "$narrative_dna" | jq -r '.consistent_namespace.name // "unknown"')
    local namespace_conf=$(echo "$narrative_dna" | jq '.consistent_namespace.confidence // 0')
    local namespace_freq=$(echo "$narrative_dna" | jq '.consistent_namespace.frequency // 0')
    
    echo -e "${YELLOW}🌍 CONSISTENT NAMESPACE:${NC}"
    echo "  Name: $namespace_name"
    echo "  Confidence: $(printf "%.1f%%" "$(echo "$namespace_conf * 100" | bc -l)")"
    echo "  Frequency: $(printf "%.1f%%" "$(echo "$namespace_freq * 100" | bc -l)")"
    echo "  Cultural Context: $(echo "$narrative_dna" | jq -r '.consistent_namespace.cultural_context // "unknown"')"
    echo
    
    # Predominant Style
    local style_name=$(echo "$narrative_dna" | jq -r '.predominant_style.name // "unknown"')
    local style_conf=$(echo "$narrative_dna" | jq '.predominant_style.confidence // 0')
    local style_freq=$(echo "$narrative_dna" | jq '.predominant_style.frequency // 0')
    
    echo -e "${YELLOW}✍️ PREDOMINANT STYLE:${NC}"
    echo "  Name: $style_name"
    echo "  Confidence: $(printf "%.1f%%" "$(echo "$style_conf * 100" | bc -l)")"
    echo "  Frequency: $(printf "%.1f%%" "$(echo "$style_freq * 100" | bc -l)")"
    echo "  Tone: $(echo "$narrative_dna" | jq -r '.predominant_style.tone // "unknown"')"
    echo
    
    # Core Essence
    local essence_purpose=$(echo "$narrative_dna" | jq -r '.core_essence.narrative_purpose // "unknown"')
    local essence_consistency=$(echo "$narrative_dna" | jq '.core_essence.thematic_consistency // 0')
    local essence_density=$(echo "$narrative_dna" | jq '.core_essence.meaning_density // 0')
    
    echo -e "${YELLOW}💎 CORE ESSENCE:${NC}"
    echo "  Narrative Purpose: $essence_purpose"
    echo "  Thematic Consistency: $(printf "%.1f%%" "$(echo "$essence_consistency * 100" | bc -l)")"
    echo "  Meaning Density: $(printf "%.1f%%" "$(echo "$essence_density * 100" | bc -l)")"
    echo "  Invariant Elements: $(echo "$narrative_dna" | jq -r '.core_essence.invariant_elements[]?' | tr '\n' ',' | sed 's/,$//' | sed 's/,/, /g')"
    echo
}

# Generate individual book report
generate_book_report() {
    local narrative_dna=$1
    local book_title=$2
    local gutenberg_id=$3
    local sampling_results=$4
    local dna_results=$5
    
    local report_file="$WORK_DIR/narrative_dna_report_$gutenberg_id.md"
    
    cat > "$report_file" <<EOF
# Narrative DNA Report: $book_title

**Gutenberg ID:** $gutenberg_id  
**Analysis Date:** $(date '+%Y-%m-%d %H:%M:%S')  
**Method:** Strategic Paragraph Sampling + Composite QNT Analysis

## Executive Summary

This report presents the extracted "Narrative DNA" of **$book_title** - the consistent narrative patterns that define the book's voice, world, style, and thematic essence. The analysis is based on strategic sampling of 64 paragraphs from the middle 70% of the book, avoiding iconic opening/closing passages to focus on the book's true narrative character.

## Methodology

### Strategic Sampling Criteria
- **Sample Size:** 64 paragraphs
- **Position Range:** Middle 70% of book (avoiding first/last 15%)
- **Length Range:** 150-600 characters
- **Focus Areas:** 
  - Descriptive scenery passages
  - Character introspection moments
  - Narrative commentary sections
  - Dialogue with rich context
  - Philosophical reflections

### Composite Analysis Process
1. Individual QNT analysis of each strategic paragraph
2. Pattern identification across all samples
3. Confidence weighting based on consistency
4. Frequency analysis of narrative elements
5. DNA extraction of dominant patterns

## Narrative DNA Results

### 🎭 Dominant Persona
$(echo "$narrative_dna" | jq -r '
"**Name:** " + (.dominant_persona.name // "unknown") + "  \n" +
"**Confidence:** " + ((.dominant_persona.confidence // 0) * 100 | tostring | split(".")[0]) + "%  \n" +
"**Frequency:** " + ((.dominant_persona.frequency // 0) * 100 | tostring | split(".")[0]) + "%  \n" +
"**Voice Pattern:** " + (.dominant_persona.voice_pattern // "unknown") + "  \n\n" +
"**Characteristics:**\n" +
([.dominant_persona.characteristics[]?] | map("- " + .) | join("\n"))
')

### 🌍 Consistent Namespace
$(echo "$narrative_dna" | jq -r '
"**Name:** " + (.consistent_namespace.name // "unknown") + "  \n" +
"**Confidence:** " + ((.consistent_namespace.confidence // 0) * 100 | tostring | split(".")[0]) + "%  \n" +
"**Frequency:** " + ((.consistent_namespace.frequency // 0) * 100 | tostring | split(".")[0]) + "%  \n" +
"**Cultural Context:** " + (.consistent_namespace.cultural_context // "unknown") + "  \n\n" +
"**Domain Markers:**\n" +
([.consistent_namespace.domain_markers[]?] | map("- " + .) | join("\n"))
')

### ✍️ Predominant Style
$(echo "$narrative_dna" | jq -r '
"**Name:** " + (.predominant_style.name // "unknown") + "  \n" +
"**Confidence:** " + ((.predominant_style.confidence // 0) * 100 | tostring | split(".")[0]) + "%  \n" +
"**Frequency:** " + ((.predominant_style.frequency // 0) * 100 | tostring | split(".")[0]) + "%  \n" +
"**Tone:** " + (.predominant_style.tone // "unknown") + "  \n\n" +
"**Linguistic Features:**\n" +
([.predominant_style.linguistic_features[]?] | map("- " + .) | join("\n"))
')

### 💎 Core Essence
$(echo "$narrative_dna" | jq -r '
"**Narrative Purpose:** " + (.core_essence.narrative_purpose // "unknown") + "  \n" +
"**Thematic Consistency:** " + ((.core_essence.thematic_consistency // 0) * 100 | tostring | split(".")[0]) + "%  \n" +
"**Meaning Density:** " + ((.core_essence.meaning_density // 0) * 100 | tostring | split(".")[0]) + "%  \n" +
"**Philosophical Depth:** " + ((.core_essence.philosophical_depth // 0) * 100 | tostring | split(".")[0]) + "%  \n\n" +
"**Invariant Elements:**\n" +
([.core_essence.invariant_elements[]?] | map("- " + .) | join("\n"))
')

## Usage Recommendations

### For Content Transformation
$(echo "$dna_results" | jq -r '
.data.results.usage_recommendations.persona_usage + "\n\n" +
.data.results.usage_recommendations.namespace_usage + "\n\n" +
.data.results.usage_recommendations.style_usage + "\n\n" +
.data.results.usage_recommendations.transformation_notes
')

### Narrative DNA Application
This narrative DNA can be used to:
- **Style Transfer:** Apply the book's narrative voice to new content
- **Content Classification:** Identify similar narrative patterns in other texts
- **Writing Assistance:** Guide authors toward this narrative style
- **Literary Analysis:** Compare narrative DNA across different works and periods

## Technical Details

### Analysis Metadata
$(echo "$dna_results" | jq -r '
"- **Paragraphs Analyzed:** " + (.data.results.analysis_metadata.paragraphs_analyzed // 0 | tostring) + "\n" +
"- **Analysis Type:** " + (.data.results.analysis_metadata.analysis_type // "unknown") + "\n" +
"- **Confidence Threshold:** " + ((.data.results.analysis_metadata.confidence_threshold // 0) * 100 | tostring | split(".")[0]) + "%" + "\n" +
"- **Pattern Consistency:** " + ((.data.results.analysis_metadata.pattern_consistency // 0) * 100 | tostring | split(".")[0]) + "%" + "\n" +
"- **Narrative Coherence:** " + ((.data.results.analysis_metadata.narrative_coherence // 0) * 100 | tostring | split(".")[0]) + "%"
')

### Data Files
- \`sampling_results_$gutenberg_id.json\` - Strategic paragraph sampling data
- \`narrative_dna_$gutenberg_id.json\` - Complete narrative DNA analysis

---

**Generated by Narrative DNA Extractor**  
*Part of the Humanizer Lighthouse Platform*
EOF

    log "✓ Individual report generated: $report_file"
}

# Process multiple books
process_book_list() {
    local books=(
        "1342:Pride and Prejudice:Jane Austen"
        "84:Frankenstein:Mary Shelley"
        "11:Alice's Adventures in Wonderland:Lewis Carroll"
        "1661:The Adventures of Sherlock Holmes:Arthur Conan Doyle"
        "174:The Picture of Dorian Gray:Oscar Wilde"
    )
    
    echo -e "${PURPLE}🧬 NARRATIVE DNA EXTRACTION PROJECT${NC}"
    echo -e "${CYAN}Extracting narrative DNA from ${#books[@]} classic books${NC}"
    echo
    
    local composite_job_ids=()
    
    for i in "${!books[@]}"; do
        IFS=':' read -r gutenberg_id title author <<< "${books[$i]}"
        
        echo -e "${BLUE}📖 Processing Book $((i+1))/${#books[@]}: $title by $author${NC}"
        echo "══════════════════════════════════════════════════════════════════"
        
        local composite_job_id=$(extract_narrative_dna "$gutenberg_id" "$title")
        composite_job_ids+=("$composite_job_id")
        
        echo
        echo -e "${GREEN}✅ Completed: $title${NC}"
        echo
        
        # Add delay between books to be nice to the API
        if [ $((i+1)) -lt ${#books[@]} ]; then
            echo -e "${YELLOW}⏳ Brief pause before next book...${NC}"
            sleep 5
        fi
    done
    
    # Generate summary report
    generate_summary_report "${books[@]}"
    
    echo -e "${GREEN}🎉 All narrative DNA extractions completed!${NC}"
    log "✓ Project completed successfully"
}

# Generate summary report
generate_summary_report() {
    local books=("$@")
    local summary_file="$WORK_DIR/narrative_dna_summary.md"
    
    cat > "$summary_file" <<EOF
# Narrative DNA Extraction Summary

**Project:** Classic Literature Narrative DNA Analysis  
**Analysis Date:** $(date '+%Y-%m-%d %H:%M:%S')  
**Books Analyzed:** ${#books[@]}  
**Method:** Strategic Sampling + Composite QNT Analysis

## Books Processed

EOF
    
    for book in "${books[@]}"; do
        IFS=':' read -r gutenberg_id title author <<< "$book"
        echo "- **$title** by $author (Gutenberg ID: $gutenberg_id)" >> "$summary_file"
    done
    
    cat >> "$summary_file" <<EOF

## Results Overview

Each book has been analyzed to extract its unique "narrative DNA" - the consistent patterns that define:

- **🎭 Dominant Persona:** The primary narrative voice and perspective
- **🌍 Consistent Namespace:** The cultural and domain context
- **✍️ Predominant Style:** The linguistic and rhetorical approach
- **💎 Core Essence:** The thematic purpose and invariant elements

## Individual Reports

EOF
    
    for book in "${books[@]}"; do
        IFS=':' read -r gutenberg_id title author <<< "$book"
        echo "- [\`narrative_dna_report_$gutenberg_id.md\`](./narrative_dna_report_$gutenberg_id.md) - $title" >> "$summary_file"
    done
    
    cat >> "$summary_file" <<EOF

## Data Files

### Strategic Sampling Results
EOF
    
    for book in "${books[@]}"; do
        IFS=':' read -r gutenberg_id title author <<< "$book"
        echo "- \`sampling_results_$gutenberg_id.json\` - Strategic paragraphs from $title" >> "$summary_file"
    done
    
    cat >> "$summary_file" <<EOF

### Narrative DNA Analysis
EOF
    
    for book in "${books[@]}"; do
        IFS=':' read -r gutenberg_id title author <<< "$book"
        echo "- \`narrative_dna_$gutenberg_id.json\` - Complete DNA analysis for $title" >> "$summary_file"
    done
    
    cat >> "$summary_file" <<EOF

## Applications

The extracted narrative DNA can be used for:

1. **Content Transformation** - Apply classic narrative voices to modern content
2. **Style Transfer** - Transform text to match the narrative DNA of specific authors
3. **Literary Analysis** - Compare narrative patterns across different works and periods
4. **AI Training** - Create training data for narrative voice classification
5. **Writing Tools** - Guide authors toward specific narrative styles

## Technical Notes

- **Strategic Sampling:** 64 paragraphs per book from middle 70% (avoiding iconic openings/endings)
- **Composite Analysis:** QNT analysis with pattern consistency weighting
- **Confidence Thresholds:** Minimum 70% confidence for DNA element inclusion
- **Quality Metrics:** Pattern consistency >80%, narrative coherence >85%

---

**Generated by Narrative DNA Extractor**  
*Extracting the essence of classic literature through quantum narrative theory*
EOF

    log "✓ Summary report generated: $summary_file"
}

# Display final results
display_final_results() {
    echo
    echo -e "${PURPLE}╔══════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${PURPLE}║                           PROJECT COMPLETE                                  ║${NC}"
    echo -e "${PURPLE}╚══════════════════════════════════════════════════════════════════════════════╝${NC}"
    echo
    echo -e "${CYAN}📊 Results Summary:${NC}"
    echo -e "   Workspace: ${GREEN}$WORK_DIR${NC}"
    echo -e "   Log File: ${GREEN}$LOG_FILE${NC}"
    echo
    echo -e "${CYAN}📁 Generated Files:${NC}"
    ls -la "$WORK_DIR"/*.md 2>/dev/null | sed 's/^/   /' || echo "   No markdown files found"
    echo
    echo -e "${CYAN}📝 Individual Reports:${NC}"
    ls -la "$WORK_DIR"/narrative_dna_report_*.md 2>/dev/null | sed 's/^/   /' || echo "   No individual reports found"
    echo
    echo -e "${CYAN}🧬 JSON Data Files:${NC}"
    ls -la "$WORK_DIR"/*.json 2>/dev/null | sed 's/^/   /' || echo "   No JSON files found"
    echo
    echo -e "${GREEN}✨ Next Steps:${NC}"
    echo -e "   • Review individual narrative DNA reports"
    echo -e "   • Use extracted DNA for content transformations"
    echo -e "   • Compare patterns across different authors"
    echo -e "   • Integrate DNA into writing and analysis tools"
    echo
}

# Main execution
main() {
    echo -e "${PURPLE}╔══════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${PURPLE}║                        NARRATIVE DNA EXTRACTOR                              ║${NC}"
    echo -e "${PURPLE}║                                                                              ║${NC}"
    echo -e "${PURPLE}║     Extract the narrative DNA from classic literature using strategic       ║${NC}"
    echo -e "${PURPLE}║     paragraph sampling and composite QNT analysis                           ║${NC}"
    echo -e "${PURPLE}╚══════════════════════════════════════════════════════════════════════════════╝${NC}"
    echo
    
    init_workspace
    process_book_list
    display_final_results
}

# Execute if run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi