#!/bin/bash

# Simple DNA Browser - Functional CLI interface for DNA management
# No fancy UI - just working commands

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

# Find DNA directories
find_dna_dirs() {
    find "$SCRIPT_DIR" -name "expanded_attributes_*" -type d 2>/dev/null | sort -r
}

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

# List all DNA files with simple index
list_all_dna() {
    echo -e "${CYAN}All Available DNA Files:${NC}"
    echo "========================"
    
    local index=1
    for dir in $(find_dna_dirs); do
        echo -e "${YELLOW}$(basename "$dir"):${NC}"
        for file in "$dir"/narrative_dna_*.json; do
            if [[ -f "$file" ]]; then
                local book_id=$(basename "$file" .json | sed 's/narrative_dna_//')
                local title=$(get_book_title "$book_id")
                echo "  [$index] $title"
                echo "      File: $file"
                ((index++))
            fi
        done
        echo
    done
}

# Menu-driven interface
main_menu() {
    while true; do
        echo -e "${WHITE}=== DNA Browser Main Menu ===${NC}"
        echo "1. List all DNA files"
        echo "2. Show detailed DNA analysis"
        echo "3. Show transformation prompts"
        echo "4. Compare DNA files"
        echo "5. Search by book title"
        echo "6. System status"
        echo "7. Quick extract new DNA"
        echo "0. Exit"
        echo
        
        read -p "Choose option [0-7]: " choice
        echo
        
        case "$choice" in
            1) list_all_dna ;;
            2) detailed_analysis_menu ;;
            3) prompts_menu ;;
            4) compare_menu ;;
            5) search_menu ;;
            6) system_status ;;
            7) quick_extract ;;
            0) echo "Goodbye!"; exit 0 ;;
            *) echo -e "${RED}Invalid choice${NC}" ;;
        esac
        
        echo
        read -p "Press Enter to continue..."
        clear
    done
}

# Detailed analysis menu
detailed_analysis_menu() {
    echo -e "${CYAN}=== Detailed DNA Analysis ===${NC}"
    echo "Enter the full path to a DNA file, or:"
    echo "- 'list' to see all files"
    echo "- 'back' to return to main menu"
    echo
    
    read -p "File path or command: " input
    
    case "$input" in
        "list")
            list_all_dna
            return
            ;;
        "back")
            return
            ;;
        *)
            if [[ -f "$input" ]]; then
                "$SCRIPT_DIR/dna_inspector.sh" show "$input"
            else
                echo -e "${RED}File not found: $input${NC}"
            fi
            ;;
    esac
}

# Prompts menu
prompts_menu() {
    echo -e "${CYAN}=== Transformation Prompts ===${NC}"
    echo "Enter the full path to a DNA file:"
    echo
    
    read -p "File path: " file_path
    
    if [[ -f "$file_path" ]]; then
        "$SCRIPT_DIR/dna_inspector.sh" prompts "$file_path"
    else
        echo -e "${RED}File not found: $file_path${NC}"
    fi
}

# Compare menu
compare_menu() {
    echo -e "${CYAN}=== Compare DNA Files ===${NC}"
    echo "Enter paths to DNA files (space-separated):"
    echo
    
    read -p "File paths: " file_paths
    
    if [[ -n "$file_paths" ]]; then
        "$SCRIPT_DIR/dna_inspector.sh" compare $file_paths
    else
        echo -e "${RED}No files specified${NC}"
    fi
}

# Search menu
search_menu() {
    echo -e "${CYAN}=== Search by Book Title ===${NC}"
    echo "Enter part of a book title to search:"
    echo
    
    read -p "Search term: " search_term
    
    if [[ -n "$search_term" ]]; then
        echo -e "${YELLOW}Searching for: $search_term${NC}"
        echo
        
        local found=0
        for dir in $(find_dna_dirs); do
            for file in "$dir"/narrative_dna_*.json; do
                if [[ -f "$file" ]]; then
                    local book_id=$(basename "$file" .json | sed 's/narrative_dna_//')
                    local title=$(get_book_title "$book_id")
                    
                    if [[ "$title" =~ .*"$search_term".* ]]; then
                        echo -e "${GREEN}Found: $title${NC}"
                        echo "File: $file"
                        echo
                        ((found++))
                    fi
                fi
            done
        done
        
        if [[ $found -eq 0 ]]; then
            echo -e "${YELLOW}No matches found${NC}"
        fi
    fi
}

# System status
system_status() {
    echo -e "${CYAN}=== System Status ===${NC}"
    
    # API status
    if curl -s "$API_URL/health" > /dev/null 2>&1; then
        echo -e "🟢 ${GREEN}API Server: ONLINE${NC} ($API_URL)"
    else
        echo -e "🔴 ${RED}API Server: OFFLINE${NC}"
    fi
    
    # Job daemon status
    if [[ -f "$SCRIPT_DIR/job_daemon.pid" ]]; then
        local pid=$(cat "$SCRIPT_DIR/job_daemon.pid")
        if ps -p "$pid" > /dev/null 2>&1; then
            echo -e "🟢 ${GREEN}Job Daemon: RUNNING${NC} (PID: $pid)"
        else
            echo -e "🔴 ${RED}Job Daemon: STOPPED${NC}"
        fi
    else
        echo -e "🔴 ${RED}Job Daemon: NOT STARTED${NC}"
    fi
    
    # Count DNA files
    local total_files=0
    local total_dirs=0
    
    for dir in $(find_dna_dirs); do
        ((total_dirs++))
        local dir_files=$(find "$dir" -name "narrative_dna_*.json" | wc -l)
        total_files=$((total_files + dir_files))
    done
    
    echo -e "📚 ${BLUE}DNA Extractions: $total_dirs directories, $total_files files${NC}"
    
    # Disk usage
    if [[ -d "$SCRIPT_DIR/results" ]]; then
        local results_size=$(du -sh "$SCRIPT_DIR/results" 2>/dev/null | cut -f1)
        echo -e "💾 ${BLUE}Results Directory: $results_size${NC}"
    fi
    
    if [[ -d "$SCRIPT_DIR/logs" ]]; then
        local logs_size=$(du -sh "$SCRIPT_DIR/logs" 2>/dev/null | cut -f1)
        echo -e "📝 ${BLUE}Logs Directory: $logs_size${NC}"
    fi
}

# Quick extract
quick_extract() {
    echo -e "${CYAN}=== Quick DNA Extraction ===${NC}"
    echo "Enter book IDs (space-separated) or press Enter for default set:"
    echo "Default: 1342 11 1661 84 174 2701 345 76"
    echo
    
    read -p "Book IDs: " book_ids
    
    if [[ -z "$book_ids" ]]; then
        book_ids="1342 11 1661 84 174 2701 345 76"
    fi
    
    echo -e "${BLUE}Starting DNA extraction for books: $book_ids${NC}"
    "$SCRIPT_DIR/dna_tools.sh" extract $book_ids
}

# File picker helper
file_picker() {
    local prompt="$1"
    echo -e "${CYAN}Available DNA files:${NC}"
    
    local files=()
    local index=1
    
    for dir in $(find_dna_dirs); do
        for file in "$dir"/narrative_dna_*.json; do
            if [[ -f "$file" ]]; then
                local book_id=$(basename "$file" .json | sed 's/narrative_dna_//')
                local title=$(get_book_title "$book_id")
                echo "  [$index] $title"
                files[$index]="$file"
                ((index++))
            fi
        done
    done
    
    echo
    read -p "$prompt (enter number or full path): " selection
    
    if [[ "$selection" =~ ^[0-9]+$ ]] && [[ -n "${files[$selection]}" ]]; then
        echo "${files[$selection]}"
    elif [[ -f "$selection" ]]; then
        echo "$selection"
    else
        echo ""
    fi
}

# Show help
show_help() {
    cat << EOF
Simple DNA Browser - Functional CLI interface for DNA management

This is a menu-driven interface that actually works, unlike the broken
"windows commander" style interface.

USAGE:
  $0              - Start interactive menu
  $0 help         - Show this help

FEATURES:
  - List all available DNA files
  - Show detailed DNA analysis
  - View transformation prompts
  - Compare multiple DNA files
  - Search by book title
  - System status monitoring
  - Quick DNA extraction

INTEGRATION:
  Works with dna_inspector.sh and dna_tools.sh for full functionality.

The interface uses simple menus and text input instead of broken
keyboard navigation.
EOF
}

# Main entry point
main() {
    if [[ "$1" == "help" || "$1" == "--help" || "$1" == "-h" ]]; then
        show_help
        exit 0
    fi
    
    clear
    echo -e "${WHITE}Simple DNA Browser${NC}"
    echo -e "${GRAY}Functional CLI interface for narrative DNA management${NC}"
    echo
    
    main_menu
}

# Entry point
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi