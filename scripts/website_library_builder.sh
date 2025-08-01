#!/bin/bash

# Website Library Builder - Create diverse DNA library for website launch
# Compatible with bash 3.2+ (no associative arrays needed)

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
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'

# Book collections for distinct DNA profiles (name:books format)
COLLECTIONS=(
    "Victorian_Gothic:345 84 174"
    "Regency_Romance:1342 105 161"
    "American_Realism:76 2701 74"
    "Gothic_Romance:1260 145 768"
    "Maritime_Adventure:120 2083 1268"
    "Wilderness_Adventure:215 1837 751"
    "Detective_Mystery:1661 2147 244"
    "Early_Sci_Fi:35 36 5230"
    "Scientific_Romance:159 30 863"
    "Russian_Realism:2554 2638 996"
    "French_Realism:135 150 1717"
    "Children_Fantasy:11 107 114"
    "Social_Satire:829 1080 2500"
    "Epic_Poetry:1727 6130 2199"
    "Modernist_Early:4300 1184 2641"
    "Psychological:2638 158 1259"
)

# Parse collection entry
parse_collection() {
    local entry="$1"
    local name="${entry%%:*}"
    local books="${entry#*:}"
    echo "$name|$books"
}

# Get collection books by name
get_collection_books() {
    local target_name="$1"
    for collection in "${COLLECTIONS[@]}"; do
        local parsed=$(parse_collection "$collection")
        local name="${parsed%%|*}"
        local books="${parsed#*|}"
        if [[ "$name" == "$target_name" ]]; then
            echo "$books"
            return 0
        fi
    done
    return 1
}

# Check API availability
check_api() {
    if ! curl -s "$API_URL/health" > /dev/null 2>&1; then
        echo -e "${RED}ERROR: API not available at $API_URL${NC}"
        echo "Please start the API server first:"
        echo "  ./launcher.sh start"
        exit 1
    fi
}

# List all available collections
list_collections() {
    echo -e "${CYAN}Available DNA Collections for Website Launch:${NC}"
    echo "=============================================="
    echo
    
    echo -e "${YELLOW}Classic Narrative Styles:${NC}"
    echo "  1. Victorian_Gothic     - Dracula, Frankenstein, Dorian Gray"
    echo "  2. Regency_Romance      - Pride & Prejudice, Persuasion"
    echo "  3. American_Realism     - Huck Finn, Moby Dick, Tom Sawyer"
    echo "  4. Gothic_Romance       - Jane Eyre, Wuthering Heights"
    echo
    
    echo -e "${YELLOW}Adventure & Action:${NC}"
    echo "  5. Maritime_Adventure   - Treasure Island, Twenty Thousand Leagues"
    echo "  6. Wilderness_Adventure - Call of the Wild, White Fang"
    echo "  7. Detective_Mystery    - Sherlock Holmes, The Moonstone"
    echo
    
    echo -e "${YELLOW}Science Fiction:${NC}"
    echo "  8. Early_Sci_Fi         - Time Machine, War of the Worlds"
    echo "  9. Scientific_Romance   - 20,000 Leagues, Mysterious Island"
    echo
    
    echo -e "${YELLOW}International & Specialized:${NC}"
    echo " 10. Russian_Realism      - Crime & Punishment, Brothers Karamazov"
    echo " 11. French_Realism       - Les Miserables, Count of Monte Cristo"
    echo " 12. Children_Fantasy     - Alice in Wonderland, Peter Pan"
    echo " 13. Social_Satire        - Gulliver's Travels, Candide"
    echo " 14. Epic_Poetry          - Iliad, Odyssey, Paradise Lost"
    echo " 15. Modernist_Early      - Ulysses, The Metamorphosis"
    echo " 16. Psychological        - Brothers Karamazov, Emma"
    echo
    
    echo -e "${CYAN}Total: ${#COLLECTIONS[@]} collections available${NC}"
}

# Build specific collection
build_collection() {
    local collection_name="$1"
    local books=$(get_collection_books "$collection_name")
    
    if [[ -z "$books" ]]; then
        echo -e "${RED}Unknown collection: $collection_name${NC}"
        echo "Use 'list' command to see available collections"
        return 1
    fi
    
    check_api
    
    echo -e "${BLUE}Building collection: $collection_name${NC}"
    echo "Books: $books"
    echo
    
    "$SCRIPT_DIR/dna_tools.sh" extract $books
}

# Build demo library with maximally distinct collections
build_demo_library() {
    echo -e "${CYAN}Creating Website Demo Library${NC}"
    echo "============================="
    echo "Building 6 maximally distinct collections for website demonstration."
    echo
    
    # Select 6 most distinct collections
    local demo_collections=(
        "Victorian_Gothic"
        "American_Realism"
        "Early_Sci_Fi"
        "Russian_Realism"
        "Children_Fantasy"
        "Epic_Poetry"
    )
    
    check_api
    
    echo "Selected collections for maximum distinctiveness:"
    for collection in "${demo_collections[@]}"; do
        local books=$(get_collection_books "$collection")
        echo "  • $collection: $books"
    done
    echo
    
    read -p "Proceed with demo library creation? [y/N]: " confirm
    if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
        echo "Cancelled."
        return 0
    fi
    
    local count=0
    for collection in "${demo_collections[@]}"; do
        ((count++))
        echo -e "${YELLOW}[$count/6] Extracting: $collection${NC}"
        build_collection "$collection"
        echo
        sleep 2  # Brief pause between extractions
    done
    
    echo -e "${GREEN}Demo library creation complete!${NC}"
    echo "Use 'navigate' command to review the DNA profiles."
}

# Build production library (all collections)
build_production_library() {
    echo -e "${CYAN}Building Complete Production Library${NC}"
    echo "===================================="
    echo "This will extract DNA from all ${#COLLECTIONS[@]} collections."
    echo "This may take 30-60 minutes depending on API response time."
    echo
    
    read -p "Proceed with full production build? [y/N]: " confirm
    if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
        echo "Cancelled."
        return 0
    fi
    
    check_api
    
    local count=0
    local total=${#COLLECTIONS[@]}
    
    for collection_entry in "${COLLECTIONS[@]}"; do
        ((count++))
        local parsed=$(parse_collection "$collection_entry")
        local name="${parsed%%|*}"
        local books="${parsed#*|}"
        
        echo -e "${YELLOW}[$count/$total] Processing: $name${NC}"
        echo "Books: $books"
        echo "  → Starting extraction..."
        
        if "$SCRIPT_DIR/dna_tools.sh" extract $books; then
            echo -e "  ✅ ${GREEN}$name completed${NC}"
        else
            echo -e "  ❌ ${RED}$name failed${NC}"
        fi
        
        echo
        sleep 3  # Pause between collections
    done
    
    echo -e "${GREEN}Production library build complete!${NC}"
}

# Quick starter sets for immediate website functionality
build_starter_sets() {
    echo -e "${CYAN}Building Starter Sets${NC}"
    echo "===================="
    echo "Quick extraction of 3 highly distinct collections for immediate use."
    echo
    
    local starter_collections=(
        "Victorian_Gothic"
        "American_Realism"
        "Early_Sci_Fi"
    )
    
    check_api
    
    for collection in "${starter_collections[@]}"; do
        echo -e "${BLUE}Extracting starter set: $collection${NC}"
        build_collection "$collection"
        echo
    done
    
    echo -e "${GREEN}Starter sets complete!${NC}"
    echo "You now have 3 distinct DNA types for website testing."
}

# Interactive collection builder
interactive_builder() {
    while true; do
        echo -e "${WHITE}=== Interactive DNA Library Builder ===${NC}"
        echo
        echo "1. List available collections"
        echo "2. Build specific collection"
        echo "3. Build starter sets (3 collections)"
        echo "4. Build demo library (6 collections)"
        echo "5. Build production library (all collections)"
        echo "6. Launch DNA navigator"
        echo "0. Exit"
        echo
        
        read -p "Choose option [0-6]: " choice
        echo
        
        case "$choice" in
            1)
                list_collections
                ;;
            2)
                echo "Available collections:"
                local i=1
                for collection_entry in "${COLLECTIONS[@]}"; do
                    local parsed=$(parse_collection "$collection_entry")
                    local name="${parsed%%|*}"
                    echo "  $i. $name"
                    ((i++))
                done
                echo
                read -p "Enter collection name: " collection_name
                if [[ -n "$collection_name" ]]; then
                    build_collection "$collection_name"
                fi
                ;;
            3)
                build_starter_sets
                ;;
            4)
                build_demo_library
                ;;
            5)
                build_production_library
                ;;
            6)
                exec "$SCRIPT_DIR/dna_navigator.sh"
                ;;
            0)
                echo "Goodbye!"
                exit 0
                ;;
            *)
                echo -e "${RED}Invalid choice${NC}"
                ;;
        esac
        
        echo
        read -p "Press Enter to continue..."
        clear
    done
}

# Show help
show_help() {
    cat << EOF
Website Library Builder - Create diverse DNA library for website launch

USAGE:
  $0 list                    - Show available collections
  $0 build <collection>      - Build specific collection
  $0 starter                 - Build 3 starter collections
  $0 demo                    - Build 6 demo collections
  $0 production              - Build all collections
  $0 interactive             - Interactive builder menu
  $0 navigate                - Launch DNA navigator

COLLECTIONS:
  Curated book collections designed to produce maximally distinct
  narrative DNA profiles optimized for website launch.

EXAMPLES:
  $0 list                    # See all collections
  $0 build Victorian_Gothic  # Extract gothic literature DNA
  $0 starter                 # Quick 3-collection setup
  $0 demo                    # 6 collections for demo
  $0 navigate                # Browse extracted DNA

WEBSITE PREPARATION:
  The builder creates depth in default DNA library ensuring
  users have rich, distinct transformation options from day one.
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
        "starter")
            build_starter_sets
            ;;
        "demo")
            build_demo_library
            ;;
        "production")
            build_production_library
            ;;
        "interactive")
            interactive_builder
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