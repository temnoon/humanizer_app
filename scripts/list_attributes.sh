#!/bin/bash

# List and Examine Narrative DNA Attributes
# Shows discovered personas, namespaces, styles from narrative DNA analysis

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
API_URL="http://localhost:8100"

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
BLUE='\033[0;34m'
NC='\033[0m'

# Find the most recent narrative DNA extraction directory
find_latest_dna_dir() {
    local latest_dir=$(find "$SCRIPT_DIR" -maxdepth 1 -type d -name "narrative_dna_*" | sort -r | head -1)
    if [ -z "$latest_dir" ]; then
        latest_dir=$(find "$SCRIPT_DIR" -maxdepth 1 -type d -name "expanded_attributes_*" | sort -r | head -1)
    fi
    echo "$latest_dir"
}

# Display detailed attribute information
show_attribute_details() {
    local dna_file=$1
    local book_title=$2
    
    if [ -f "$dna_file" ]; then
        echo -e "${CYAN}📖 $book_title${NC}"
        
        # Extract detailed information using jq
        local persona_name=$(jq -r '.data.results.narrative_dna.dominant_persona.name // "unknown"' "$dna_file")
        local persona_confidence=$(jq -r '.data.results.narrative_dna.dominant_persona.confidence // 0' "$dna_file")
        local persona_description=$(jq -r '.data.results.narrative_dna.dominant_persona.description // "No description"' "$dna_file")
        
        local namespace_name=$(jq -r '.data.results.narrative_dna.consistent_namespace.name // "unknown"' "$dna_file")
        local namespace_confidence=$(jq -r '.data.results.narrative_dna.consistent_namespace.confidence // 0' "$dna_file")
        local namespace_description=$(jq -r '.data.results.narrative_dna.consistent_namespace.description // "No description"' "$dna_file")
        
        local style_name=$(jq -r '.data.results.narrative_dna.predominant_style.name // "unknown"' "$dna_file")
        local style_confidence=$(jq -r '.data.results.narrative_dna.predominant_style.confidence // 0' "$dna_file")
        local style_description=$(jq -r '.data.results.narrative_dna.predominant_style.description // "No description"' "$dna_file")
        
        echo "   🎭 Persona: $persona_name (${persona_confidence}% confidence)"
        echo "      $persona_description"
        echo
        echo "   🌍 Namespace: $namespace_name (${namespace_confidence}% confidence)" 
        echo "      $namespace_description"
        echo
        echo "   ✍️ Style: $style_name (${style_confidence}% confidence)"
        echo "      $style_description"
        echo
    else
        echo "   ❌ DNA file not found: $dna_file"
    fi
}

# List all available attributes from API
list_api_attributes() {
    echo -e "${PURPLE}📊 QUERYING API FOR SAVED ATTRIBUTES${NC}"
    echo
    
    # Check if attributes endpoint exists
    local response=$(curl -s "${API_URL}/attributes/stats" 2>/dev/null || echo '{}')
    local total_attributes=$(echo "$response" | jq -r '.total_attributes // 0')
    
    if [ "$total_attributes" -gt 0 ]; then
        echo "✅ Found $total_attributes saved attributes in the system"
        echo
        
        # Get detailed attribute list
        local attr_list=$(curl -s "${API_URL}/attributes/list" 2>/dev/null || echo '{}')
        
        echo -e "${CYAN}🎭 Available Personas:${NC}"
        echo "$attr_list" | jq -r '.personas[]?.name // empty' | sort -u | sed 's/^/   • /'
        echo
        
        echo -e "${CYAN}🌍 Available Namespaces:${NC}"
        echo "$attr_list" | jq -r '.namespaces[]?.name // empty' | sort -u | sed 's/^/   • /'
        echo
        
        echo -e "${CYAN}✍️ Available Styles:${NC}"
        echo "$attr_list" | jq -r '.styles[]?.name // empty' | sort -u | sed 's/^/   • /'
        echo
    else
        echo "⚠️ No attributes found in API - may need to run narrative DNA extraction first"
    fi
}

# Main execution
main() {
    echo -e "${PURPLE}🔍 NARRATIVE DNA ATTRIBUTE BROWSER${NC}"
    echo -e "${CYAN}Examining discovered literary attributes and DNA patterns${NC}"
    echo
    
    # Test API connection
    if ! curl -s "${API_URL}/health" &> /dev/null; then
        echo "❌ Cannot connect to API at $API_URL"
        echo "   Please ensure the Lighthouse API is running:"
        echo "   cd humanizer_api/lighthouse && python api_enhanced.py"
        exit 1
    fi
    
    echo "✅ Connected to Lighthouse API"
    echo
    
    # Find latest extraction directory
    local latest_dir=$(find_latest_dna_dir)
    
    if [ -n "$latest_dir" ] && [ -d "$latest_dir" ]; then
        echo -e "${GREEN}📂 Found DNA extraction directory: $(basename "$latest_dir")${NC}"
        echo
        
        # Show catalog if available
        if [ -f "$latest_dir/attribute_catalog.txt" ]; then
            echo -e "${CYAN}📋 ATTRIBUTE CATALOG${NC}"
            echo
            
            while IFS='|' read -r id title author persona namespace style; do
                if [[ ! "$id" =~ ^# ]]; then
                    echo "   📖 $title by $author"
                    echo "      🎭 $persona | 🌍 $namespace | ✍️ $style"
                    echo
                fi
            done < "$latest_dir/attribute_catalog.txt"
        fi
        
        # Show detailed DNA analysis for each book
        echo -e "${GREEN}🧬 DETAILED NARRATIVE DNA ANALYSIS${NC}"
        echo
        
        # Look for narrative DNA files
        for dna_file in "$latest_dir"/narrative_dna_*.json; do
            if [ -f "$dna_file" ]; then
                local book_id=$(basename "$dna_file" .json | sed 's/narrative_dna_//')
                local book_title="Book ID $book_id"
                
                # Try to get title from catalog
                if [ -f "$latest_dir/attribute_catalog.txt" ]; then
                    book_title=$(grep "^$book_id|" "$latest_dir/attribute_catalog.txt" | cut -d'|' -f2 || echo "Book ID $book_id")
                fi
                
                show_attribute_details "$dna_file" "$book_title"
                echo "────────────────────────────────────"
                echo
            fi
        done
        
    else
        echo "⚠️ No narrative DNA extraction directory found"
        echo "   Run ./narrative_dna_extractor.sh first to extract DNA patterns"
        echo
    fi
    
    # Query API for saved attributes
    list_api_attributes
    
    echo -e "${YELLOW}💡 NEXT STEPS${NC}"
    echo "   • Run ./expand_attribute_collection.sh to add more books"
    echo "   • Use ./transform_with_dna.sh to apply attributes to text"
    echo "   • Check individual DNA files for detailed analysis"
    echo
}

# Execute
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi