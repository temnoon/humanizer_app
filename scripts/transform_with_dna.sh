#!/bin/bash

# Transform Text Using Narrative DNA
# Demonstrates how to apply extracted literary DNA to transform sample paragraphs

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
RED='\033[0;31m'
NC='\033[0m'

# Sample text for transformation testing
SAMPLE_TEXT="The old man walked slowly down the street. He had been thinking about his past for hours, remembering the choices he had made and the paths he had taken. The city around him buzzed with activity, but he felt disconnected from it all. Each step brought him closer to a decision he had been avoiding for years."

# Find the most recent narrative DNA extraction directory
find_latest_dna_dir() {
    local latest_dir=$(find "$SCRIPT_DIR" -maxdepth 1 -type d -name "narrative_dna_*" | sort -r | head -1)
    if [ -z "$latest_dir" ]; then
        latest_dir=$(find "$SCRIPT_DIR" -maxdepth 1 -type d -name "expanded_attributes_*" | sort -r | head -1)
    fi
    echo "$latest_dir"
}

# Extract DNA components from a file
extract_dna_components() {
    local dna_file=$1
    
    if [ ! -f "$dna_file" ]; then
        echo ""
        return 1
    fi
    
    local persona=$(jq -r '.data.results.narrative_dna.dominant_persona.name // "unknown"' "$dna_file")
    local namespace=$(jq -r '.data.results.narrative_dna.consistent_namespace.name // "unknown"' "$dna_file")
    local style=$(jq -r '.data.results.narrative_dna.predominant_style.name // "unknown"' "$dna_file")
    
    echo "$persona|$namespace|$style"
}

# Transform text using the Lighthouse API
transform_text() {
    local text="$1"
    local persona="$2"
    local namespace="$3"
    local style="$4"
    local title="$5"
    
    echo -e "${CYAN}🔄 Transforming with: $title${NC}"
    echo "   🎭 Persona: $persona"
    echo "   🌍 Namespace: $namespace"
    echo "   ✍️ Style: $style"
    echo
    
    # Create transformation request
    local request_body=$(jq -n \
        --arg text "$text" \
        --arg persona "$persona" \
        --arg namespace "$namespace" \
        --arg style "$style" \
        '{
            text: $text,
            persona: $persona,
            namespace: $namespace,
            style: $style,
            preserve_essence: true,
            transformation_strength: 0.8
        }')
    
    echo "📤 Sending transformation request..."
    
    # Send transformation request
    local response=$(curl -s -X POST "${API_URL}/transform" \
        -H "Content-Type: application/json" \
        -d "$request_body" || echo '{"error": "Failed to connect"}')
    
    # Check for errors
    if echo "$response" | jq -e '.error' > /dev/null; then
        local error_msg=$(echo "$response" | jq -r '.error // "Unknown error"')
        echo "   ❌ Transformation failed: $error_msg"
        return 1
    fi
    
    # Extract transformed text
    local transformed_text=$(echo "$response" | jq -r '.transformed_text // .data.transformed_text // "No transformed text found"')
    
    if [ "$transformed_text" != "No transformed text found" ]; then
        echo "✅ Transformation successful!"
        echo
        echo -e "${GREEN}📝 TRANSFORMED TEXT:${NC}"
        echo "────────────────────────────────────────────────────────────────"
        echo "$transformed_text"
        echo "────────────────────────────────────────────────────────────────"
        echo
        
        # Show comparison
        echo -e "${YELLOW}📊 COMPARISON:${NC}"
        echo -e "${BLUE}Original length:${NC} $(echo "$text" | wc -c) characters"
        echo -e "${BLUE}Transformed length:${NC} $(echo "$transformed_text" | wc -c) characters"
        echo
    else
        echo "   ⚠️ Transformation completed but no text returned"
        echo "   Raw response: $response"
    fi
    
    return 0
}

# Interactive mode for custom text transformation
interactive_transform() {
    local latest_dir=$1
    
    echo -e "${PURPLE}🎮 INTERACTIVE TRANSFORMATION MODE${NC}"
    echo
    
    # Get available DNA patterns
    local dna_files=($(find "$latest_dir" -name "narrative_dna_*.json" | sort))
    
    if [ ${#dna_files[@]} -eq 0 ]; then
        echo "❌ No DNA patterns found in $latest_dir"
        return 1
    fi
    
    echo "Available DNA patterns:"
    local i=1
    declare -a dna_options
    
    for dna_file in "${dna_files[@]}"; do
        local book_id=$(basename "$dna_file" .json | sed 's/narrative_dna_//')
        local book_title="Book ID $book_id"
        
        # Try to get title from catalog
        if [ -f "$latest_dir/attribute_catalog.txt" ]; then
            book_title=$(grep "^$book_id|" "$latest_dir/attribute_catalog.txt" | cut -d'|' -f2 || echo "Book ID $book_id")
        fi
        
        local dna_components=$(extract_dna_components "$dna_file")
        if [ -n "$dna_components" ]; then
            echo "   $i. $book_title"
            dna_options[$i]="$dna_file|$book_title"
            i=$((i + 1))
        fi
    done
    
    echo
    read -p "Choose a DNA pattern (1-$((i-1))): " choice
    
    if [[ "$choice" =~ ^[0-9]+$ ]] && [ "$choice" -ge 1 ] && [ "$choice" -lt "$i" ]; then
        local selected_option="${dna_options[$choice]}"
        local selected_file=$(echo "$selected_option" | cut -d'|' -f1)
        local selected_title=$(echo "$selected_option" | cut -d'|' -f2)
        
        echo
        echo -e "${CYAN}🧬 Selected: $selected_title${NC}"
        echo
        
        echo "Enter your text to transform (press Enter twice when done):"
        echo "────────────────────────────────────────────────────────────────"
        
        local user_text=""
        local line
        local empty_lines=0
        
        while IFS= read -r line; do
            if [ -z "$line" ]; then
                empty_lines=$((empty_lines + 1))
                if [ $empty_lines -ge 2 ]; then
                    break
                fi
                user_text="$user_text\n"
            else
                empty_lines=0
                user_text="$user_text$line\n"
            fi
        done
        
        user_text=$(echo -e "$user_text" | sed 's/\\n$//')
        
        if [ -n "$user_text" ]; then
            echo
            echo -e "${YELLOW}📝 Original text:${NC}"
            echo "$user_text"
            echo
            
            # Extract DNA components and transform
            local dna_components=$(extract_dna_components "$selected_file")
            if [ -n "$dna_components" ]; then
                IFS='|' read -r persona namespace style <<< "$dna_components"
                transform_text "$user_text" "$persona" "$namespace" "$style" "$selected_title"
            else
                echo "❌ Failed to extract DNA components from $selected_file"
            fi
        else
            echo "❌ No text provided"
        fi
    else
        echo "❌ Invalid choice"
    fi
}

# Main execution
main() {
    echo -e "${PURPLE}🧬 NARRATIVE DNA TRANSFORMATION DEMO${NC}"
    echo -e "${CYAN}Transform text using extracted literary DNA patterns${NC}"
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
    
    if [ -z "$latest_dir" ] || [ ! -d "$latest_dir" ]; then
        echo "❌ No narrative DNA extraction directory found"
        echo "   Run ./narrative_dna_extractor.sh first to extract DNA patterns"
        exit 1
    fi
    
    echo -e "${GREEN}📂 Using DNA from: $(basename "$latest_dir")${NC}"
    echo
    
    # Show sample transformations first
    echo -e "${YELLOW}🎭 SAMPLE TRANSFORMATIONS${NC}"
    echo "Using sample text to demonstrate different narrative DNA patterns:"
    echo
    echo -e "${BLUE}Original Sample Text:${NC}"
    echo "────────────────────────────────────────────────────────────────"
    echo "$SAMPLE_TEXT"
    echo "────────────────────────────────────────────────────────────────"
    echo
    
    # Transform using each available DNA pattern
    local transform_count=0
    for dna_file in "$latest_dir"/narrative_dna_*.json; do
        if [ -f "$dna_file" ] && [ $transform_count -lt 3 ]; then
            local book_id=$(basename "$dna_file" .json | sed 's/narrative_dna_//')
            local book_title="Book ID $book_id"
            
            # Try to get title from catalog
            if [ -f "$latest_dir/attribute_catalog.txt" ]; then
                book_title=$(grep "^$book_id|" "$latest_dir/attribute_catalog.txt" | cut -d'|' -f2 || echo "Book ID $book_id")
            fi
            
            local dna_components=$(extract_dna_components "$dna_file")
            if [ -n "$dna_components" ]; then
                IFS='|' read -r persona namespace style <<< "$dna_components"
                
                if transform_text "$SAMPLE_TEXT" "$persona" "$namespace" "$style" "$book_title"; then
                    transform_count=$((transform_count + 1))
                    echo "═══════════════════════════════════════════════════════════════════"
                    echo
                    sleep 2  # Rate limiting
                fi
            fi
        fi
    done
    
    if [ $transform_count -eq 0 ]; then
        echo "⚠️ No transformations were successful"
        echo "   This may indicate API issues or missing DNA patterns"
        echo
    fi
    
    # Offer interactive mode
    echo -e "${CYAN}🎮 INTERACTIVE MODE AVAILABLE${NC}"
    echo "Would you like to transform your own text? (y/n)"
    read -r response
    
    if [[ "$response" =~ ^[Yy] ]]; then
        echo
        interactive_transform "$latest_dir"
    fi
    
    echo
    echo -e "${GREEN}✨ TRANSFORMATION DEMO COMPLETE${NC}"
    echo -e "${YELLOW}💡 Tips:${NC}"
    echo "   • Each DNA pattern preserves the narrative essence while applying its style"
    echo "   • Transformation strength can be adjusted (0.1-1.0) for subtlety"
    echo "   • DNA patterns work best on narrative text rather than technical content"
    echo "   • Combine multiple DNA elements for complex transformations"
    echo
}

# Execute
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi