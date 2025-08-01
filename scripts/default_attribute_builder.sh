#!/usr/bin/env bash

# Default Attribute Builder - Create diverse, high-quality DNA library
# Builds depth for website launch with distinct, proven attributes

set -e

# Check for bash 4+ (required for associative arrays)
if [[ ${BASH_VERSION%%.*} -lt 4 ]]; then
    echo "Error: This script requires bash 4.0 or later for associative arrays"
    exit 1
fi

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
API_URL="http://localhost:8100"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'

# Curated book collections for distinct DNA profiles
declare -A BOOK_COLLECTIONS=(
    # Classic narrative styles - proven distinct
    ["Victorian_Gothic"]="345 84 174"          # Dracula, Frankenstein, Dorian Gray
    ["Regency_Romance"]="1342 105 161"         # Pride & Prejudice, Persuasion, Sense & Sensibility  
    ["American_Realism"]="76 2701 74"          # Huck Finn, Moby Dick, Tom Sawyer
    ["Gothic_Romance"]="1260 145 768"          # Jane Eyre, Wuthering Heights, Northanger Abbey
    
    # Adventure & Action - distinct voice patterns
    ["Maritime_Adventure"]="120 2083 1268"     # Treasure Island, Twenty Thousand Leagues, Mysterious Island
    ["Wilderness_Adventure"]="215 1837 751"    # Call of the Wild, White Fang, Sea Wolf
    ["Detective_Mystery"]="1661 2147 244"      # Sherlock Holmes, The Moonstone, Murders in Rue Morgue
    ["Historical_Adventure"]="1400 74 5000"    # Great Expectations, Tom Sawyer, Prince & Pauper
    
    # Science Fiction - emerging genre patterns
    ["Early_Sci_Fi"]="35 36 5230"             # Time Machine, War of the Worlds, Food of the Gods
    ["Scientific_Romance"]="159 30 863"        # 20,000 Leagues, Mysterious Island, Journey to Center
    ["Social_Sci_Fi"]="131 74 2852"           # The Sleeper Awakes, Connecticut Yankee, Looking Backward
    
    # International perspectives - cultural variation
    ["Russian_Realism"]="2554 2638 996"       # Crime & Punishment, Brothers Karamazov, War & Peace
    ["French_Realism"]="135 150 1717"         # Les Miserables, Count of Monte Cristo, Madame Bovary
    ["German_Philosophy"]="815 1232 5827"     # Critique of Pure Reason, Thus Spoke Zarathustra, Faust
    
    # Specialized genres - unique voice patterns
    ["Children_Fantasy"]="11 107 114"          # Alice in Wonderland, Peter Pan, Wind in the Willows
    ["Social_Satire"]="829 1080 2500"         # Gulliver's Travels, Candide, The Way of All Flesh
    ["Philosophical"]="815 1998 2150"         # Critique, Republic, Prince
    ["Epic_Poetry"]="1727 6130 2199"          # Iliad, Odyssey, Paradise Lost
    
    # Modern transitions - bridging classical and contemporary
    ["Modernist_Early"]="4300 1184 2641"      # Ulysses, The Metamorphosis, Heart of Darkness
    ["Psychological"]="2638 158 1259"         # Brothers Karamazov, Emma, Great Gatsby
    ["Social_Commentary"]="398 1156 205"      # Jungle, How the Other Half Lives, Progress and Poverty
)

# Check API availability
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

# Build comprehensive default library
build_complete_library() {
    echo -e "${CYAN}Building Complete Default DNA Library${NC}"
    echo "======================================"
    echo "This will create a diverse, high-quality DNA library"
    echo "optimized for website launch with distinct attributes."
    echo
    
    check_api
    
    local total_collections=${#BOOK_COLLECTIONS[@]}
    local current=0
    
    for collection_name in "${!BOOK_COLLECTIONS[@]}"; do
        ((current++))
        
        echo -e "${YELLOW}[$current/$total_collections] Processing: $collection_name${NC}"
        echo "Books: ${BOOK_COLLECTIONS[$collection_name]}"
        
        # Extract DNA for this collection
        local timestamp=$(date +%Y%m%d_%H%M%S)
        local output_dir="default_library_${collection_name,,}_${timestamp}"
        
        echo "  → Starting extraction..."
        if "$SCRIPT_DIR/dna_tools.sh" extract ${BOOK_COLLECTIONS[$collection_name]}; then
            echo -e "  ✅ ${GREEN}$collection_name extraction completed${NC}"
        else
            echo -e "  ❌ ${RED}$collection_name extraction failed${NC}"
        fi
        
        echo
        sleep 2  # Brief pause between collections
    done
    
    echo -e "${GREEN}Complete library build finished!${NC}"
    echo
    echo "Library now contains distinct DNA from:"
    for collection_name in "${!BOOK_COLLECTIONS[@]}"; do
        echo "  • $collection_name"
    done
}

# Build specific collection
build_collection() {
    local collection_name="$1"
    
    if [[ -z "${BOOK_COLLECTIONS[$collection_name]}" ]]; then
        echo -e "${RED}Unknown collection: $collection_name${NC}"
        echo "Available collections:"
        for name in "${!BOOK_COLLECTIONS[@]}"; do
            echo "  • $name"
        done
        return 1
    fi
    
    check_api
    
    echo -e "${BLUE}Building collection: $collection_name${NC}"
    echo "Books: ${BOOK_COLLECTIONS[$collection_name]}"
    echo
    
    "$SCRIPT_DIR/dna_tools.sh" extract ${BOOK_COLLECTIONS[$collection_name]}
}

# Show available collections
list_collections() {
    echo -e "${CYAN}Available DNA Collections for Website Launch:${NC}"
    echo "=============================================="
    echo
    
    echo -e "${YELLOW}Classic Narrative Styles:${NC}"
    echo "  • Victorian_Gothic    - Dracula, Frankenstein, Dorian Gray"
    echo "  • Regency_Romance     - Pride & Prejudice, Persuasion, Sense & Sensibility"
    echo "  • American_Realism    - Huck Finn, Moby Dick, Tom Sawyer"
    echo "  • Gothic_Romance      - Jane Eyre, Wuthering Heights, Northanger Abbey"
    echo
    
    echo -e "${YELLOW}Adventure & Action:${NC}"
    echo "  • Maritime_Adventure  - Treasure Island, Twenty Thousand Leagues"
    echo "  • Wilderness_Adventure - Call of the Wild, White Fang, Sea Wolf"
    echo "  • Detective_Mystery   - Sherlock Holmes, The Moonstone"
    echo "  • Historical_Adventure - Great Expectations, Tom Sawyer"
    echo
    
    echo -e "${YELLOW}Science Fiction:${NC}"
    echo "  • Early_Sci_Fi        - Time Machine, War of the Worlds"
    echo "  • Scientific_Romance  - 20,000 Leagues, Mysterious Island"
    echo "  • Social_Sci_Fi       - The Sleeper Awakes, Connecticut Yankee"
    echo
    
    echo -e "${YELLOW}International Perspectives:${NC}"
    echo "  • Russian_Realism     - Crime & Punishment, Brothers Karamazov"
    echo "  • French_Realism      - Les Miserables, Count of Monte Cristo"
    echo "  • German_Philosophy   - Critique of Pure Reason, Zarathustra"
    echo
    
    echo -e "${YELLOW}Specialized Genres:${NC}"
    echo "  • Children_Fantasy    - Alice in Wonderland, Peter Pan"
    echo "  • Social_Satire       - Gulliver's Travels, Candide"
    echo "  • Philosophical       - Critique, Republic, Prince"
    echo "  • Epic_Poetry         - Iliad, Odyssey, Paradise Lost"
    echo
    
    echo -e "${YELLOW}Modern Transitions:${NC}"
    echo "  • Modernist_Early     - Ulysses, The Metamorphosis"
    echo "  • Psychological       - Brothers Karamazov, Emma"
    echo "  • Social_Commentary   - Jungle, How the Other Half Lives"
    echo
    
    local total_books=0
    for collection in "${BOOK_COLLECTIONS[@]}"; do
        local count=$(echo "$collection" | wc -w)
        total_books=$((total_books + count))
    done
    
    echo -e "${CYAN}Total: ${#BOOK_COLLECTIONS[@]} collections, ~$total_books books${NC}"
}

# Validate distinctiveness of collections
validate_distinctiveness() {
    echo -e "${CYAN}Validating Collection Distinctiveness${NC}"
    echo "====================================="
    echo "This will analyze existing DNA to ensure collections produce"
    echo "distinct, non-overlapping narrative DNA profiles."
    echo
    
    # Find recent extractions
    local recent_dirs=($(find "$SCRIPT_DIR" -name "expanded_attributes_*" -type d -mtime -1 2>/dev/null | sort -r | head -5))
    
    if [[ ${#recent_dirs[@]} -eq 0 ]]; then
        echo -e "${YELLOW}No recent extractions found. Run extractions first.${NC}"
        return 1
    fi
    
    echo "Analyzing recent extractions..."
    echo
    
    declare -A persona_counts
    declare -A namespace_counts
    declare -A style_counts
    
    # Count occurrences of each DNA component
    for dir in "${recent_dirs[@]}"; do
        echo "Processing: $(basename "$dir")"
        
        for file in "$dir"/narrative_dna_*.json; do
            if [[ -f "$file" ]]; then
                local persona=$(jq -r '.data.results.narrative_dna.dominant_persona.name // "unknown"' "$file" 2>/dev/null)
                local namespace=$(jq -r '.data.results.narrative_dna.consistent_namespace.name // "unknown"' "$file" 2>/dev/null)
                local style=$(jq -r '.data.results.narrative_dna.predominant_style.name // "unknown"' "$file" 2>/dev/null)
                
                ((persona_counts["$persona"]++))
                ((namespace_counts["$namespace"]++))
                ((style_counts["$style"]++))
            fi
        done
    done
    
    echo
    echo -e "${YELLOW}Distinctiveness Analysis:${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    echo -e "${BLUE}Persona Diversity:${NC}"
    for persona in "${!persona_counts[@]}"; do
        echo "  $persona: ${persona_counts[$persona]} occurrences"
    done
    echo
    
    echo -e "${BLUE}Namespace Diversity:${NC}"
    for namespace in "${!namespace_counts[@]}"; do
        echo "  $namespace: ${namespace_counts[$namespace]} occurrences"
    done
    echo
    
    echo -e "${BLUE}Style Diversity:${NC}"
    for style in "${!style_counts[@]}"; do
        echo "  $style: ${style_counts[$style]} occurrences"
    done
    echo
    
    # Calculate distinctiveness score
    local total_personas=${#persona_counts[@]}
    local total_namespaces=${#namespace_counts[@]}
    local total_styles=${#style_counts[@]}
    local total_combinations=$((total_personas * total_namespaces * total_styles))
    
    echo -e "${GREEN}Distinctiveness Score:${NC}"
    echo "  Unique Personas: $total_personas"
    echo "  Unique Namespaces: $total_namespaces"
    echo "  Unique Styles: $total_styles"
    echo "  Potential Combinations: $total_combinations"
    
    if [[ $total_combinations -gt 100 ]]; then
        echo -e "  ${GREEN}✅ Excellent diversity for website launch${NC}"
    elif [[ $total_combinations -gt 50 ]]; then
        echo -e "  ${YELLOW}⚠️ Good diversity, consider expanding${NC}"
    else
        echo -e "  ${RED}❌ Limited diversity, more collections needed${NC}"
    fi
}

# Create optimized extraction for website demo
create_demo_library() {
    echo -e "${CYAN}Creating Optimized Demo Library${NC}"
    echo "==============================="
    echo "Building a curated set of maximally distinct DNA for website demonstration."
    echo
    
    # Select 6 most distinct collections for demo
    local demo_collections=(
        "Victorian_Gothic"
        "American_Realism" 
        "Early_Sci_Fi"
        "Russian_Realism"
        "Children_Fantasy"
        "Epic_Poetry"
    )
    
    check_api
    
    echo "Demo collections selected for maximum distinctiveness:"
    for collection in "${demo_collections[@]}"; do
        echo "  • $collection: ${BOOK_COLLECTIONS[$collection]}"
    done
    echo
    
    read -p "Proceed with demo library creation? [y/N]: " confirm
    if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
        echo "Cancelled."
        return 0
    fi
    
    for collection in "${demo_collections[@]}"; do
        echo -e "${BLUE}Extracting: $collection${NC}"
        build_collection "$collection"
        echo
    done
    
    echo -e "${GREEN}Demo library creation complete!${NC}"
    echo "Launch the navigator to review the distinct DNA profiles:"
    echo "  $0 navigate"
}

# Show help
show_help() {
    cat << EOF
Default Attribute Builder - Create diverse DNA library for website launch

USAGE:
  $0 list                     - Show available collections
  $0 build <collection>       - Build specific collection
  $0 build-all               - Build complete library (all collections)
  $0 demo                    - Create optimized demo library
  $0 validate                - Validate distinctiveness of existing DNA
  $0 navigate                - Launch navigator for review

COLLECTIONS:
  Curated book collections designed to produce maximally distinct
  narrative DNA profiles for website launch.

EXAMPLES:
  $0 list                    # See all available collections
  $0 build Victorian_Gothic  # Extract DNA from gothic literature
  $0 demo                    # Create demo library with 6 distinct collections
  $0 validate                # Check distinctiveness of current library

The builder focuses on creating depth and distinctiveness in the
default DNA library to ensure website users have rich, varied
transformation options.
EOF
}

# Main command dispatcher
main() {
    local command="$1"
    shift
    
    case "$command" in
        "list")
            list_collections
            ;;
        "build")
            if [[ $# -gt 0 ]]; then
                build_collection "$1"
            else
                echo "Usage: $0 build <collection_name>"
                echo "Use '$0 list' to see available collections"
            fi
            ;;
        "build-all")
            build_complete_library
            ;;
        "demo")
            create_demo_library
            ;;
        "validate")
            validate_distinctiveness
            ;;
        "navigate")
            exec "$SCRIPT_DIR/dna_navigator.sh"
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