#!/bin/bash

# DNA Navigator - Tab/Arrow navigable interface for DNA management
# Proper list navigation without manual filepath entry

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

# Global state
CURRENT_SELECTION=0
DNA_FILES=()
DNA_TITLES=()
MODE="list"

# Initialize terminal
init_terminal() {
    # Save terminal state
    tput smcup
    # Hide cursor
    tput civis
    # Clear screen
    clear
}

# Restore terminal
restore_terminal() {
    # Show cursor
    tput cnorm
    # Restore terminal state
    tput rmcup
}

# Cleanup on exit
cleanup() {
    restore_terminal
    exit 0
}

# Set up signal handlers
trap cleanup EXIT INT TERM

# Get book title from ID
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

# Load all DNA files into arrays
load_dna_files() {
    DNA_FILES=()
    DNA_TITLES=()
    
    # Find all DNA directories in reverse chronological order
    local dirs=($(find "$SCRIPT_DIR" -name "expanded_attributes_*" -type d 2>/dev/null | sort -r))
    
    for dir in "${dirs[@]}"; do
        local timestamp=$(basename "$dir" | sed 's/expanded_attributes_//')
        
        # Find DNA files in this directory
        for file in "$dir"/narrative_dna_*.json; do
            if [[ -f "$file" ]]; then
                local book_id=$(basename "$file" .json | sed 's/narrative_dna_//')
                local title=$(get_book_title "$book_id")
                local display_title="$title [$timestamp]"
                
                DNA_FILES+=("$file")
                DNA_TITLES+=("$display_title")
            fi
        done
    done
}

# Draw the main interface
draw_interface() {
    clear
    
    # Header
    echo -e "${WHITE}╔══════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${WHITE}║${CYAN}                          DNA NAVIGATOR - Quick Selection                      ${WHITE}║${NC}"
    echo -e "${WHITE}╚══════════════════════════════════════════════════════════════════════════════╝${NC}"
    echo
    
    case "$MODE" in
        "list")
            draw_file_list
            ;;
        "detail")
            draw_detail_view
            ;;
        "prompts")
            draw_prompts_view
            ;;
        "extract")
            draw_extract_view
            ;;
    esac
    
    # Footer
    draw_footer
}

# Draw file list with navigation
draw_file_list() {
    echo -e "${CYAN}DNA Files (${#DNA_FILES[@]} available):${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo
    
    local start_idx=0
    local max_display=15
    
    # Calculate display window
    if [[ $CURRENT_SELECTION -gt $((max_display - 3)) ]]; then
        start_idx=$((CURRENT_SELECTION - max_display + 3))
    fi
    
    local end_idx=$((start_idx + max_display))
    if [[ $end_idx -gt ${#DNA_FILES[@]} ]]; then
        end_idx=${#DNA_FILES[@]}
    fi
    
    # Show selection indicator
    if [[ ${#DNA_FILES[@]} -gt 0 ]]; then
        echo -e "${GRAY}Selection: $((CURRENT_SELECTION + 1)) of ${#DNA_FILES[@]}${NC}"
        echo
    fi
    
    # Draw list items
    for ((i=start_idx; i<end_idx; i++)); do
        local prefix="  "
        local color="$NC"
        
        if [[ $i -eq $CURRENT_SELECTION ]]; then
            prefix="▶ "
            color="$GREEN"
        fi
        
        echo -e "${color}${prefix}${DNA_TITLES[$i]}${NC}"
    done
    
    # Show scroll indicators
    if [[ $start_idx -gt 0 ]]; then
        echo -e "${GRAY}  ↑ More items above...${NC}"
    fi
    
    if [[ $end_idx -lt ${#DNA_FILES[@]} ]]; then
        echo -e "${GRAY}  ↓ More items below...${NC}"
    fi
    
    # Quick preview of selected item
    if [[ ${#DNA_FILES[@]} -gt 0 && $CURRENT_SELECTION -ge 0 && $CURRENT_SELECTION -lt ${#DNA_FILES[@]} ]]; then
        echo
        echo -e "${YELLOW}Quick Preview:${NC}"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        show_quick_preview "${DNA_FILES[$CURRENT_SELECTION]}"
    fi
}

# Show quick preview of DNA
show_quick_preview() {
    local file="$1"
    
    if [[ ! -f "$file" ]]; then
        echo "File not found"
        return
    fi
    
    local persona=$(jq -r '.data.results.narrative_dna.dominant_persona.name // "unknown"' "$file" 2>/dev/null)
    local namespace=$(jq -r '.data.results.narrative_dna.consistent_namespace.name // "unknown"' "$file" 2>/dev/null)
    local style=$(jq -r '.data.results.narrative_dna.predominant_style.name // "unknown"' "$file" 2>/dev/null)
    local persona_conf=$(jq -r '.data.results.narrative_dna.dominant_persona.confidence // 0' "$file" 2>/dev/null)
    local namespace_conf=$(jq -r '.data.results.narrative_dna.consistent_namespace.confidence // 0' "$file" 2>/dev/null)
    local style_conf=$(jq -r '.data.results.narrative_dna.predominant_style.confidence // 0' "$file" 2>/dev/null)
    
    echo -e "${BLUE}🎭 Persona:${NC} $persona ${GRAY}(conf: $persona_conf)${NC}"
    echo -e "${BLUE}🌍 Namespace:${NC} $namespace ${GRAY}(conf: $namespace_conf)${NC}"
    echo -e "${BLUE}✍️ Style:${NC} $style ${GRAY}(conf: $style_conf)${NC}"
    
    # Show a few characteristics
    local characteristics=$(jq -r '.data.results.narrative_dna.dominant_persona.characteristics[0:2][]? // empty' "$file" 2>/dev/null)
    if [[ -n "$characteristics" ]]; then
        echo -e "${GRAY}Key traits: $(echo "$characteristics" | tr '\n' ', ' | sed 's/, $//')${NC}"
    fi
}

# Draw detailed view
draw_detail_view() {
    if [[ ${#DNA_FILES[@]} -eq 0 || $CURRENT_SELECTION -lt 0 || $CURRENT_SELECTION -ge ${#DNA_FILES[@]} ]]; then
        echo "No file selected"
        return
    fi
    
    local file="${DNA_FILES[$CURRENT_SELECTION]}"
    local title="${DNA_TITLES[$CURRENT_SELECTION]}"
    
    echo -e "${CYAN}Detailed Analysis: $title${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo
    
    # Pipe to less-like viewer with scrolling
    "$SCRIPT_DIR/dna_inspector.sh" show "$file" | head -25
    
    echo
    echo -e "${GRAY}[Showing first 25 lines - press 'f' for full view]${NC}"
}

# Draw prompts view
draw_prompts_view() {
    if [[ ${#DNA_FILES[@]} -eq 0 || $CURRENT_SELECTION -lt 0 || $CURRENT_SELECTION -ge ${#DNA_FILES[@]} ]]; then
        echo "No file selected"
        return
    fi
    
    local file="${DNA_FILES[$CURRENT_SELECTION]}"
    local title="${DNA_TITLES[$CURRENT_SELECTION]}"
    
    echo -e "${CYAN}Transformation Prompts: $title${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo
    
    "$SCRIPT_DIR/dna_inspector.sh" prompts "$file" | head -20
}

# Draw extract view
draw_extract_view() {
    echo -e "${CYAN}Extract New DNA Attributes${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo
    echo "Quick extraction from popular books:"
    echo
    echo "  1. Classic Literature Set: Pride & Prejudice, Jane Eyre, Romeo & Juliet"
    echo "  2. Gothic Horror Set: Dracula, Frankenstein, Dr. Jekyll & Hyde"
    echo "  3. Adventure Set: Treasure Island, Robinson Crusoe, Call of the Wild"
    echo "  4. Science Fiction Set: Time Machine, War of the Worlds, Foundation"
    echo "  5. Mystery Set: Sherlock Holmes, The Moonstone, Murders in Rue Morgue"
    echo "  6. American Literature Set: Huckleberry Finn, Moby Dick, Tom Sawyer"
    echo
    echo "  c. Custom book IDs (enter manually)"
    echo "  r. Random selection (8 books)"
    echo
    echo -e "${YELLOW}Select extraction set [1-6, c, r]:${NC}"
}

# Draw footer
draw_footer() {
    echo
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    case "$MODE" in
        "list")
            echo -e "${YELLOW}Navigation:${NC} ↑/↓ or j/k to move | ${YELLOW}Actions:${NC} Enter=Details | d=Details | p=Prompts | e=Extract | q=Quit"
            ;;
        "detail"|"prompts")
            echo -e "${YELLOW}Navigation:${NC} ↑/↓ for files | ${YELLOW}Actions:${NC} b=Back | f=Full view | p=Prompts | e=Extract | q=Quit"
            ;;
        "extract")
            echo -e "${YELLOW}Actions:${NC} 1-6=Sets | c=Custom | r=Random | b=Back | q=Quit"
            ;;
    esac
}

# Handle keyboard input
handle_input() {
    local key
    read -rsn1 key
    
    case "$key" in
        $'\x1b')  # Escape sequence
            read -rsn2 key
            case "$key" in
                '[A'|'[k')  # Up arrow or k
                    if [[ $MODE == "list" ]]; then
                        if [[ $CURRENT_SELECTION -gt 0 ]]; then
                            ((CURRENT_SELECTION--))
                        fi
                    fi
                    ;;
                '[B'|'[j')  # Down arrow or j
                    if [[ $MODE == "list" ]]; then
                        if [[ $CURRENT_SELECTION -lt $((${#DNA_FILES[@]} - 1)) ]]; then
                            ((CURRENT_SELECTION++))
                        fi
                    fi
                    ;;
            esac
            ;;
        'k')  # k key
            if [[ $MODE == "list" && $CURRENT_SELECTION -gt 0 ]]; then
                ((CURRENT_SELECTION--))
            fi
            ;;
        'j')  # j key
            if [[ $MODE == "list" && $CURRENT_SELECTION -lt $((${#DNA_FILES[@]} - 1)) ]]; then
                ((CURRENT_SELECTION++))
            fi
            ;;
        '')  # Enter key
            case "$MODE" in
                "list")
                    MODE="detail"
                    ;;
                "extract")
                    # Handle extraction
                    ;;
            esac
            ;;
        'd')  # Detail view
            if [[ $MODE == "list" ]]; then
                MODE="detail"
            fi
            ;;
        'p')  # Prompts view
            if [[ $MODE == "list" ]]; then
                MODE="prompts"
            fi
            ;;
        'f')  # Full view
            if [[ $MODE == "detail" && ${#DNA_FILES[@]} -gt 0 ]]; then
                clear
                "$SCRIPT_DIR/dna_inspector.sh" show "${DNA_FILES[$CURRENT_SELECTION]}"
                echo
                echo "Press any key to continue..."
                read -rsn1
            fi
            ;;
        'e')  # Extract mode
            MODE="extract"
            ;;
        'b')  # Back
            MODE="list"
            ;;
        'q')  # Quit
            return 1
            ;;
        '1'|'2'|'3'|'4'|'5'|'6')  # Extraction sets
            if [[ $MODE == "extract" ]]; then
                perform_extraction "$key"
            fi
            ;;
        'c')  # Custom extraction
            if [[ $MODE == "extract" ]]; then
                custom_extraction
            fi
            ;;
        'r')  # Random extraction
            if [[ $MODE == "extract" ]]; then
                random_extraction
            fi
            ;;
    esac
    
    return 0
}

# Perform extraction based on selection
perform_extraction() {
    local set="$1"
    local books=""
    
    case "$set" in
        "1") books="1342 1260 1513" ;;  # Classic Literature
        "2") books="345 84 43" ;;       # Gothic Horror  
        "3") books="120 215 1661" ;;    # Adventure
        "4") books="35 36 2701" ;;      # Science Fiction
        "5") books="1661 155 2147" ;;   # Mystery
        "6") books="76 2701 74" ;;      # American Literature
    esac
    
    if [[ -n "$books" ]]; then
        clear
        echo -e "${BLUE}Starting DNA extraction for set $set...${NC}"
        echo "Books: $books"
        echo
        
        # Run extraction
        "$SCRIPT_DIR/dna_tools.sh" extract $books
        
        echo
        echo "Extraction complete! Reloading DNA files..."
        sleep 2
        
        # Reload files
        load_dna_files
        MODE="list"
    fi
}

# Custom extraction
custom_extraction() {
    clear
    echo -e "${CYAN}Custom DNA Extraction${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo
    echo "Enter Project Gutenberg book IDs (space-separated):"
    echo "Example: 1342 11 84 174"
    echo
    read -p "Book IDs: " book_ids
    
    if [[ -n "$book_ids" ]]; then
        echo
        echo -e "${BLUE}Starting extraction for: $book_ids${NC}"
        "$SCRIPT_DIR/dna_tools.sh" extract $book_ids
        
        echo
        echo "Extraction complete! Reloading..."
        sleep 2
        load_dna_files
    fi
    
    MODE="list"
}

# Random extraction
random_extraction() {
    local random_books=(1342 11 1661 84 174 2701 345 76 105 1513 215 35)
    local selected_books=()
    
    # Randomly select 8 books
    for ((i=0; i<8; i++)); do
        local random_idx=$((RANDOM % ${#random_books[@]}))
        selected_books+=(${random_books[$random_idx]})
        # Remove selected book to avoid duplicates
        unset random_books[$random_idx]
        random_books=("${random_books[@]}")
    done
    
    clear
    echo -e "${BLUE}Random DNA extraction from 8 books...${NC}"
    echo "Selected: ${selected_books[*]}"
    echo
    
    "$SCRIPT_DIR/dna_tools.sh" extract "${selected_books[@]}"
    
    echo
    echo "Extraction complete! Reloading..."
    sleep 2
    load_dna_files
    MODE="list"
}

# Main loop
main_loop() {
    while true; do
        draw_interface
        
        if ! handle_input; then
            break
        fi
    done
}

# Main function
main() {
    if [[ "$1" == "help" || "$1" == "--help" || "$1" == "-h" ]]; then
        cat << EOF
DNA Navigator - Tab/Arrow navigable interface for DNA management

USAGE:
  $0              - Start interactive navigator

NAVIGATION:
  ↑/↓ or j/k      - Move through list
  Enter or d      - View detailed analysis
  p               - View transformation prompts
  e               - Extract new DNA
  f               - Full view (in detail mode)
  b               - Back to list
  q               - Quit

FEATURES:
  - Arrow key navigation through DNA files
  - Quick preview of selected DNA
  - Built-in extraction with book sets
  - No manual filepath entry required
  - Real-time confidence scores and characteristics

This interface is designed for productivity - quickly browse and identify
distinct DNA attributes for website launch preparation.
EOF
        exit 0
    fi
    
    # Initialize
    init_terminal
    load_dna_files
    
    if [[ ${#DNA_FILES[@]} -eq 0 ]]; then
        echo -e "${YELLOW}No DNA files found. Starting with extraction...${NC}"
        MODE="extract"
    fi
    
    # Start main loop
    main_loop
}

# Entry point
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi