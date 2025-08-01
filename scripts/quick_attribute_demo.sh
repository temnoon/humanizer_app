#!/bin/bash

# Quick Attribute Discovery Demo
# Shows the actual attribute extraction process with a small sample

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORK_DIR="${SCRIPT_DIR}/quick_demo_$(date +%H%M%S)"

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
NC='\033[0m'

echo -e "${PURPLE}🚀 Quick Attribute Discovery Demo${NC}"
echo -e "${CYAN}Extracting real QNT attributes from Gutenberg content${NC}"
echo

# Create workspace
mkdir -p "$WORK_DIR"

# Start a single analysis job for demonstration
echo -e "${YELLOW}Starting analysis job for Pride and Prejudice (Book 1342)...${NC}"
job_output=$(humanizer gutenberg analyze 1342 --type sample)
job_id=$(echo "$job_output" | grep -oE '[a-f0-9-]{36}' | head -1)

if [ -z "$job_id" ]; then
    echo "Failed to start analysis job"
    exit 1
fi

echo "Job ID: $job_id"

# Wait for completion
echo -e "${YELLOW}Waiting for job completion...${NC}"
sleep 15

# Get the results
echo -e "${YELLOW}Extracting paragraphs from analysis...${NC}"
results=$(curl -s "http://localhost:8100/gutenberg/jobs/$job_id/results")

# Extract first few paragraphs for QNT analysis
echo "$results" | jq '.data.results[0:3]' > "$WORK_DIR/sample_paragraphs.json"

# Show what we extracted
echo -e "${CYAN}Sample paragraphs extracted:${NC}"
echo "$results" | jq -r '.data.results[0:3][] | "• \(.paragraph_text[0:100])..."'
echo

# Perform QNT analysis on each paragraph
echo -e "${YELLOW}Performing QNT analysis on sample paragraphs...${NC}"
analyzed_attributes="[]"

for i in 0 1 2; do
    text=$(jq -r ".[$i].paragraph_text" "$WORK_DIR/sample_paragraphs.json")
    
    if [ -n "$text" ] && [ "$text" != "null" ]; then
        echo "Analyzing paragraph $((i+1))..."
        
        # Run QNT analysis
        analysis=$(humanizer analyze "$text" --format json 2>/dev/null || echo '{}')
        
        if [ "$analysis" != "{}" ]; then
            # Extract attributes
            # Clean text for JSON safety
            clean_text=$(echo "$text" | head -c 100 | tr -d '\n\r\t' | sed 's/"/\\"/g')
            
            attributes=$(echo "$analysis" | jq --arg text "$clean_text" '{
                persona: {
                    type: "persona",
                    name: .persona.name,
                    confidence: .persona.confidence,
                    characteristics: .persona.characteristics
                },
                namespace: {
                    type: "namespace", 
                    name: .namespace.name,
                    confidence: .namespace.confidence,
                    cultural_context: .namespace.cultural_context
                },
                style: {
                    type: "style",
                    name: .style.name,
                    confidence: .style.confidence,
                    tone: .style.tone
                },
                essence: {
                    type: "essence",
                    core_meaning: .essence.core_meaning,
                    confidence: .essence.meaning_density
                },
                source_text: ($text + "...")
            }')
            
            analyzed_attributes=$(echo "$analyzed_attributes" | jq ". + [$attributes]")
        fi
        
        sleep 2  # Rate limiting
    fi
done

# Save results
echo "$analyzed_attributes" > "$WORK_DIR/demo_attributes.json"

# Display results
echo
echo -e "${GREEN}✅ Attribute Discovery Complete!${NC}"
echo
echo -e "${CYAN}📊 Discovered Attributes:${NC}"
echo

# Show personas
echo -e "${YELLOW}Personas Discovered:${NC}"
echo "$analyzed_attributes" | jq -r '.[] | "  • \(.persona.name) (confidence: \(.persona.confidence // 0 | tostring | .[0:5]))"'
echo

# Show namespaces
echo -e "${YELLOW}Namespaces Discovered:${NC}"
echo "$analyzed_attributes" | jq -r '.[] | "  • \(.namespace.name) (confidence: \(.namespace.confidence // 0 | tostring | .[0:5]))"'
echo

# Show styles
echo -e "${YELLOW}Styles Discovered:${NC}"
echo "$analyzed_attributes" | jq -r '.[] | "  • \(.style.name) (confidence: \(.style.confidence // 0 | tostring | .[0:5]))"'
echo

# Show essences
echo -e "${YELLOW}Essences Discovered:${NC}"
echo "$analyzed_attributes" | jq -r '.[] | "  • \(.essence.core_meaning // "N/A") (confidence: \(.essence.confidence // 0 | tostring | .[0:5]))"'
echo

echo -e "${CYAN}💾 Results saved to: $WORK_DIR/demo_attributes.json${NC}"
echo
echo -e "${GREEN}🎯 Usage Examples:${NC}"

# Get first persona and style for examples
first_persona=$(echo "$analyzed_attributes" | jq -r '.[0].persona.name // "classical_narrator"')
first_style=$(echo "$analyzed_attributes" | jq -r '.[0].style.name // "literary_prose"')

echo -e "   ${YELLOW}Transform text using discovered persona:${NC}"
echo -e "   humanizer transform \"Your text here\" --persona \"$first_persona\""
echo
echo -e "   ${YELLOW}Transform text using discovered style:${NC}"
echo -e "   humanizer transform \"Your text here\" --style \"$first_style\""
echo

echo -e "${PURPLE}🚀 Run the full pipeline with: ./attribute_discovery_v2.sh${NC}"