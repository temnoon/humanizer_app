#!/bin/bash

# DNA Inspector - Deep analysis tool for narrative DNA attributes
# View detailed content including pre-prompts, vectors, and metadata

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
API_URL="http://localhost:8100"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
GRAY='\033[0;37m'
NC='\033[0m'

# Find all DNA extraction directories
find_dna_directories() {
    find "$SCRIPT_DIR" -name "expanded_attributes_*" -type d 2>/dev/null | sort -r
}

# Find all DNA JSON files
find_dna_files() {
    local search_dir="${1:-$SCRIPT_DIR}"
    find "$search_dir" -name "narrative_dna_*.json" -type f 2>/dev/null | sort
}

# Extract book title from Gutenberg ID
get_book_title() {
    local book_id="$1"
    case "$book_id" in
        "105") echo "Persuasion (Jane Austen)" ;;
        "1260") echo "Jane Eyre (Charlotte Brontë)" ;;
        "1342") echo "Pride and Prejudice (Jane Austen)" ;;
        "1513") echo "Romeo and Juliet (Shakespeare)" ;;
        "215") echo "The Call of the Wild (Jack London)" ;;
        "2701") echo "Moby Dick (Herman Melville)" ;;
        "345") echo "Dracula (Bram Stoker)" ;;
        "35") echo "The Time Machine (H.G. Wells)" ;;
        "76") echo "Adventures of Huckleberry Finn (Mark Twain)" ;;
        "11") echo "Alice's Adventures in Wonderland (Lewis Carroll)" ;;
        "84") echo "Frankenstein (Mary Shelley)" ;;
        "174") echo "The Picture of Dorian Gray (Oscar Wilde)" ;;
        "1661") echo "The Adventures of Sherlock Holmes (Arthur Conan Doyle)" ;;
        *) echo "Book ID: $book_id" ;;
    esac
}

# List all available DNA extractions
list_extractions() {
    echo -e "${CYAN}Available DNA Extractions:${NC}"
    echo "=========================="
    
    local count=0
    for dir in $(find_dna_directories); do
        local dirname=$(basename "$dir")
        local timestamp=$(echo "$dirname" | sed 's/expanded_attributes_//')
        local file_count=$(find "$dir" -name "narrative_dna_*.json" | wc -l)
        
        echo -e "${BLUE}[$((++count))] $dirname${NC}"
        echo "   📅 Timestamp: $timestamp"
        echo "   📚 Books: $file_count DNA files"
        
        # Show book titles
        for file in $(find "$dir" -name "narrative_dna_*.json" | head -5); do
            local book_id=$(basename "$file" .json | sed 's/narrative_dna_//')
            local title=$(get_book_title "$book_id")
            echo "      • $title"
        done
        
        if [[ $file_count -gt 5 ]]; then
            echo "      • ... and $((file_count - 5)) more"
        fi
        echo
    done
    
    if [[ $count -eq 0 ]]; then
        echo "No DNA extractions found. Run DNA extraction first."
    fi
}

# Show detailed DNA analysis for a specific book
show_detailed_dna() {
    local file_path="$1"
    
    if [[ ! -f "$file_path" ]]; then
        echo -e "${RED}File not found: $file_path${NC}"
        return 1
    fi
    
    local book_id=$(basename "$file_path" .json | sed 's/narrative_dna_//')
    local title=$(get_book_title "$book_id")
    
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${WHITE}📖 DETAILED DNA ANALYSIS${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${YELLOW}Book:${NC} $title"
    echo -e "${YELLOW}File:${NC} $file_path"
    echo
    
    # Check if file contains valid JSON
    if ! jq empty "$file_path" 2>/dev/null; then
        echo -e "${RED}Invalid JSON file${NC}"
        return 1
    fi
    
    # Extract and display detailed information
    echo -e "${MAGENTA}🎭 PERSONA ANALYSIS${NC}"
    echo "─────────────────────────────────────────────────────────────────"
    
    local persona_name=$(jq -r '.data.results.narrative_dna.dominant_persona.name // "unknown"' "$file_path")
    local persona_confidence=$(jq -r '.data.results.narrative_dna.dominant_persona.confidence // 0' "$file_path")
    local persona_frequency=$(jq -r '.data.results.narrative_dna.dominant_persona.frequency // 0' "$file_path")
    local voice_pattern=$(jq -r '.data.results.narrative_dna.dominant_persona.voice_pattern // "unknown"' "$file_path")
    
    echo -e "${BLUE}Name:${NC} $persona_name"
    echo -e "${BLUE}Confidence:${NC} ${persona_confidence} (${persona_frequency} frequency)"
    echo -e "${BLUE}Voice Pattern:${NC} $voice_pattern"
    echo -e "${BLUE}Characteristics:${NC}"
    
    jq -r '.data.results.narrative_dna.dominant_persona.characteristics[]? // empty' "$file_path" | \
    while read -r char; do
        echo "  • $char"
    done
    
    echo
    echo -e "${MAGENTA}🌍 NAMESPACE ANALYSIS${NC}"
    echo "─────────────────────────────────────────────────────────────────"
    
    local namespace_name=$(jq -r '.data.results.narrative_dna.consistent_namespace.name // "unknown"' "$file_path")
    local namespace_confidence=$(jq -r '.data.results.narrative_dna.consistent_namespace.confidence // 0' "$file_path")
    local namespace_frequency=$(jq -r '.data.results.narrative_dna.consistent_namespace.frequency // 0' "$file_path")
    local cultural_context=$(jq -r '.data.results.narrative_dna.consistent_namespace.cultural_context // "unknown"' "$file_path")
    
    echo -e "${BLUE}Name:${NC} $namespace_name"
    echo -e "${BLUE}Confidence:${NC} ${namespace_confidence} (${namespace_frequency} frequency)"
    echo -e "${BLUE}Cultural Context:${NC} $cultural_context"
    echo -e "${BLUE}Domain Markers:${NC}"
    
    jq -r '.data.results.narrative_dna.consistent_namespace.domain_markers[]? // empty' "$file_path" | \
    while read -r marker; do
        echo "  • $marker"
    done
    
    echo
    echo -e "${MAGENTA}✍️ STYLE ANALYSIS${NC}"
    echo "─────────────────────────────────────────────────────────────────"
    
    local style_name=$(jq -r '.data.results.narrative_dna.predominant_style.name // "unknown"' "$file_path")
    local style_confidence=$(jq -r '.data.results.narrative_dna.predominant_style.confidence // 0' "$file_path")
    local style_frequency=$(jq -r '.data.results.narrative_dna.predominant_style.frequency // 0' "$file_path")
    local tone=$(jq -r '.data.results.narrative_dna.predominant_style.tone // "unknown"' "$file_path")
    
    echo -e "${BLUE}Name:${NC} $style_name"
    echo -e "${BLUE}Confidence:${NC} ${style_confidence} (${style_frequency} frequency)"
    echo -e "${BLUE}Tone:${NC} $tone"
    echo -e "${BLUE}Linguistic Features:${NC}"
    
    jq -r '.data.results.narrative_dna.predominant_style.linguistic_features[]? // empty' "$file_path" | \
    while read -r feature; do
        echo "  • $feature"
    done
    
    echo
    echo -e "${MAGENTA}🧬 CORE ESSENCE${NC}"
    echo "─────────────────────────────────────────────────────────────────"
    
    local narrative_purpose=$(jq -r '.data.results.narrative_dna.core_essence.narrative_purpose // "unknown"' "$file_path")
    local thematic_consistency=$(jq -r '.data.results.narrative_dna.core_essence.thematic_consistency // 0' "$file_path")
    local meaning_density=$(jq -r '.data.results.narrative_dna.core_essence.meaning_density // 0' "$file_path")
    local philosophical_depth=$(jq -r '.data.results.narrative_dna.core_essence.philosophical_depth // 0' "$file_path")
    
    echo -e "${BLUE}Narrative Purpose:${NC} $narrative_purpose"
    echo -e "${BLUE}Thematic Consistency:${NC} $thematic_consistency"
    echo -e "${BLUE}Meaning Density:${NC} $meaning_density"
    echo -e "${BLUE}Philosophical Depth:${NC} $philosophical_depth"
    echo -e "${BLUE}Invariant Elements:${NC}"
    
    jq -r '.data.results.narrative_dna.core_essence.invariant_elements[]? // empty' "$file_path" | \
    while read -r element; do
        echo "  • $element"
    done
    
    echo
    echo -e "${MAGENTA}📊 ANALYSIS METADATA${NC}"
    echo "─────────────────────────────────────────────────────────────────"
    
    local job_id=$(jq -r '.data.job_info.job_id // "unknown"' "$file_path")
    local paragraphs_analyzed=$(jq -r '.data.results.analysis_metadata.paragraphs_analyzed // 0' "$file_path")
    local analysis_type=$(jq -r '.data.results.analysis_metadata.analysis_type // "unknown"' "$file_path")
    local confidence_threshold=$(jq -r '.data.results.analysis_metadata.confidence_threshold // 0' "$file_path")
    local pattern_consistency=$(jq -r '.data.results.analysis_metadata.pattern_consistency // 0' "$file_path")
    local narrative_coherence=$(jq -r '.data.results.analysis_metadata.narrative_coherence // 0' "$file_path")
    
    echo -e "${BLUE}Job ID:${NC} $job_id"
    echo -e "${BLUE}Paragraphs Analyzed:${NC} $paragraphs_analyzed"
    echo -e "${BLUE}Analysis Type:${NC} $analysis_type"
    echo -e "${BLUE}Confidence Threshold:${NC} $confidence_threshold"
    echo -e "${BLUE}Pattern Consistency:${NC} $pattern_consistency"
    echo -e "${BLUE}Narrative Coherence:${NC} $narrative_coherence"
    
    echo
    echo -e "${MAGENTA}💡 USAGE RECOMMENDATIONS${NC}"
    echo "─────────────────────────────────────────────────────────────────"
    
    jq -r '.data.results.usage_recommendations | to_entries[] | "\(.key): \(.value)"' "$file_path" | \
    while IFS=': ' read -r key value; do
        echo -e "${BLUE}${key}:${NC} $value"
    done
}

# Compare multiple DNA extractions
compare_dna() {
    local files=("$@")
    
    if [[ ${#files[@]} -lt 2 ]]; then
        echo "Usage: compare_dna file1.json file2.json [file3.json ...]"
        return 1
    fi
    
    echo -e "${CYAN}DNA COMPARISON ANALYSIS${NC}"
    echo "======================================================"
    
    for file in "${files[@]}"; do
        local book_id=$(basename "$file" .json | sed 's/narrative_dna_//')
        local title=$(get_book_title "$book_id")
        local persona=$(jq -r '.data.results.narrative_dna.dominant_persona.name // "unknown"' "$file")
        local namespace=$(jq -r '.data.results.narrative_dna.consistent_namespace.name // "unknown"' "$file")
        local style=$(jq -r '.data.results.narrative_dna.predominant_style.name // "unknown"' "$file")
        
        echo -e "${YELLOW}$title${NC}"
        echo "  🎭 $persona"
        echo "  🌍 $namespace"
        echo "  ✍️ $style"
        echo
    done
}

# Extract vectors (mock - would need real vector data)
show_vectors() {
    local file_path="$1"
    local vector_space="${2:-embedding}"
    
    echo -e "${CYAN}VECTOR ANALYSIS${NC}"
    echo "==============="
    echo -e "${YELLOW}File:${NC} $file_path"
    echo -e "${YELLOW}Vector Space:${NC} $vector_space"
    echo
    
    case "$vector_space" in
        "embedding"|"llm")
            echo -e "${BLUE}LLM Embedding Space Analysis:${NC}"
            echo "• Dimension: 1536 (standard embedding size)"
            echo "• This would show the high-dimensional embedding vectors"
            echo "• Currently using mock data - real vectors would come from API"
            ;;
        "density"|"quantum")
            echo -e "${BLUE}Quantum Density Matrix Analysis:${NC}"
            echo "• Dimension: 8×8 Hermitian matrix"
            echo "• Eigenvalues represent quantum narrative states"
            echo "• Would show the density matrix ρ = |ψ⟩⟨ψ|"
            ;;
        "povm")
            echo -e "${BLUE}POVM Measurement Space:${NC}"
            echo "• 24-dimensional SIC-POVM measurement space"
            echo "• Measurement probabilities for narrative observables"
            echo "• Born rule: p_i = Tr(ρE_i)"
            ;;
    esac
}

# Show transformation pre-prompts
show_prompts() {
    local dna_file="$1"
    
    if [[ ! -f "$dna_file" ]]; then
        echo -e "${RED}DNA file not found: $dna_file${NC}"
        return 1
    fi
    
    local persona=$(jq -r '.data.results.narrative_dna.dominant_persona.name // "unknown"' "$dna_file")
    local namespace=$(jq -r '.data.results.narrative_dna.consistent_namespace.name // "unknown"' "$dna_file")
    local style=$(jq -r '.data.results.narrative_dna.predominant_style.name // "unknown"' "$dna_file")
    
    echo -e "${CYAN}TRANSFORMATION PRE-PROMPTS${NC}"
    echo "================================"
    echo
    
    echo -e "${MAGENTA}🎭 PERSONA PROMPT ($persona):${NC}"
    echo "You are embodying the perspective of a $persona."
    echo "Your voice pattern follows: $(jq -r '.data.results.narrative_dna.dominant_persona.voice_pattern // "unknown"' "$dna_file")"
    echo "Key characteristics to maintain:"
    jq -r '.data.results.narrative_dna.dominant_persona.characteristics[]? // empty' "$dna_file" | \
    while read -r char; do
        echo "  - $char"
    done
    echo
    
    echo -e "${MAGENTA}🌍 NAMESPACE PROMPT ($namespace):${NC}"
    echo "Set your narrative in the world of: $namespace"
    echo "Cultural context: $(jq -r '.data.results.narrative_dna.consistent_namespace.cultural_context // "unknown"' "$dna_file")"
    echo "Include these domain markers:"
    jq -r '.data.results.narrative_dna.consistent_namespace.domain_markers[]? // empty' "$dna_file" | \
    while read -r marker; do
        echo "  - $marker"
    done
    echo
    
    echo -e "${MAGENTA}✍️ STYLE PROMPT ($style):${NC}"
    echo "Write in the style of: $style"
    echo "Tone: $(jq -r '.data.results.narrative_dna.predominant_style.tone // "unknown"' "$dna_file")"
    echo "Use these linguistic features:"
    jq -r '.data.results.narrative_dna.predominant_style.linguistic_features[]? // empty' "$dna_file" | \
    while read -r feature; do
        echo "  - $feature"
    done
    echo
    
    echo -e "${BLUE}Combined transformation prompt would integrate all three components"
    echo "to create the full narrative DNA transformation effect.${NC}"
}

# Interactive browser
interactive_browser() {
    while true; do
        clear
        echo -e "${CYAN}🧬 DNA INSPECTOR - Interactive Browser${NC}"
        echo "======================================"
        echo
        
        list_extractions
        
        echo -e "${YELLOW}Commands:${NC}"
        echo "  [number]        - Select extraction directory"
        echo "  list            - Refresh list"
        echo "  compare         - Compare multiple DNA files"
        echo "  quit            - Exit browser"
        echo
        
        read -p "Enter command: " command
        
        case "$command" in
            [0-9]*)
                local dirs=($(find_dna_directories))
                if [[ $command -gt 0 && $command -le ${#dirs[@]} ]]; then
                    local selected_dir="${dirs[$((command-1))]}"
                    browse_directory "$selected_dir"
                else
                    echo "Invalid selection"
                    read -p "Press Enter to continue..."
                fi
                ;;
            "list")
                continue
                ;;
            "compare")
                echo "Enter DNA file paths (space-separated):"
                read -r files_input
                if [[ -n "$files_input" ]]; then
                    compare_dna $files_input
                    read -p "Press Enter to continue..."
                fi
                ;;
            "quit"|"q"|"exit")
                break
                ;;
        esac
    done
}

# Browse specific directory
browse_directory() {
    local dir="$1"
    
    while true; do
        clear
        echo -e "${CYAN}📂 $(basename "$dir")${NC}"
        echo "========================================"
        
        local files=($(find "$dir" -name "narrative_dna_*.json" | sort))
        local count=0
        
        for file in "${files[@]}"; do
            local book_id=$(basename "$file" .json | sed 's/narrative_dna_//')
            local title=$(get_book_title "$book_id")
            echo -e "${BLUE}[$((++count))] $title${NC}"
        done
        
        echo
        echo -e "${YELLOW}Commands:${NC}"
        echo "  [number]     - View detailed DNA analysis"
        echo "  [number] v   - Show vectors"
        echo "  [number] p   - Show prompts"
        echo "  all          - Show all DNA summaries"
        echo "  back         - Return to main menu"
        echo
        
        read -p "Enter command: " command
        
        case "$command" in
            [0-9]*)
                if [[ $command =~ ^([0-9]+)\ *([vp]?)$ ]]; then
                    local num="${BASH_REMATCH[1]}"
                    local action="${BASH_REMATCH[2]}"
                    
                    if [[ $num -gt 0 && $num -le ${#files[@]} ]]; then
                        local selected_file="${files[$((num-1))]}"
                        
                        case "$action" in
                            "v")
                                clear
                                show_vectors "$selected_file"
                                read -p "Press Enter to continue..."
                                ;;
                            "p")
                                clear
                                show_prompts "$selected_file"
                                read -p "Press Enter to continue..."
                                ;;
                            *)
                                clear
                                show_detailed_dna "$selected_file"
                                read -p "Press Enter to continue..."
                                ;;
                        esac
                    else
                        echo "Invalid selection"
                        read -p "Press Enter to continue..."
                    fi
                fi
                ;;
            "all")
                clear
                for file in "${files[@]}"; do
                    show_detailed_dna "$file"
                    echo
                    echo -e "${GRAY}${'═'*80}${NC}"
                    echo
                done
                read -p "Press Enter to continue..."
                ;;
            "back"|"b")
                break
                ;;
        esac
    done
}

# Show help
show_help() {
    cat << EOF
DNA Inspector - Deep analysis tool for narrative DNA attributes

USAGE:
  $0 list                     - List all available DNA extractions
  $0 show <file.json>         - Show detailed DNA analysis
  $0 compare <file1> <file2>  - Compare multiple DNA files
  $0 vectors <file> [space]   - Show vector analysis (embedding/density/povm)
  $0 prompts <file>           - Show transformation pre-prompts
  $0 browse                   - Interactive browser

VECTOR SPACES:
  embedding/llm               - LLM embedding space (1536-dimensional)
  density/quantum             - Quantum density matrix (8×8 Hermitian)
  povm                        - POVM measurement space (24-dimensional)

EXAMPLES:
  $0 list
  $0 show expanded_attributes_20250728_003252/narrative_dna_1342.json
  $0 prompts expanded_attributes_20250728_003252/narrative_dna_345.json
  $0 vectors narrative_dna_1513.json density
  $0 browse

The inspector reveals the rich metadata hidden behind simple DNA strings,
including confidence scores, characteristics, linguistic features, and
quantum analysis components.
EOF
}

# Main command dispatcher
main() {
    local command="$1"
    shift
    
    case "$command" in
        "list")
            list_extractions
            ;;
        "show")
            if [[ $# -gt 0 ]]; then
                show_detailed_dna "$1"
            else
                echo "Usage: $0 show <file.json>"
            fi
            ;;
        "compare")
            compare_dna "$@"
            ;;
        "vectors")
            show_vectors "$@"
            ;;
        "prompts")
            if [[ $# -gt 0 ]]; then
                show_prompts "$1"
            else
                echo "Usage: $0 prompts <file.json>"
            fi
            ;;
        "browse")
            interactive_browser
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