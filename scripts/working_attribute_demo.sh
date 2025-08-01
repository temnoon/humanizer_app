#!/bin/bash

# Working Attribute Discovery Demo
# Shows real QNT attribute extraction from classic literature

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORK_DIR="${SCRIPT_DIR}/working_demo_$(date +%H%M%S)"

echo "🚀 Working Attribute Discovery Demo"
echo "Extracting real QNT attributes from classic literature"
echo

# Create workspace
mkdir -p "$WORK_DIR"

# Use actual famous quotes from classic literature for demonstration
declare -a classic_quotes=(
    "It is a truth universally acknowledged, that a single man in possession of a good fortune, must be in want of a wife."
    "To be or not to be, that is the question."
    "Call me Ishmael. Some years ago—never mind how long precisely—having little or no money in my purse, and nothing particular to interest me on shore, I thought I would sail about a little and see the watery part of the world."
    "It was the best of times, it was the worst of times, it was the age of wisdom, it was the age of foolishness."
    "In the beginning was the Word, and the Word was with God, and the Word was God."
)

declare -a sources=(
    "Pride and Prejudice by Jane Austen"
    "Hamlet by William Shakespeare"
    "Moby Dick by Herman Melville"
    "A Tale of Two Cities by Charles Dickens"
    "The Gospel of John (King James Bible)"
)

echo "Analyzing 5 classic literature excerpts for attribute discovery..."
echo

all_attributes="[]"

for i in "${!classic_quotes[@]}"; do
    quote="${classic_quotes[$i]}"
    source="${sources[$i]}"
    
    echo "Analyzing: $source"
    echo "Text: \"$(echo "$quote" | head -c 80)...\""
    echo
    
    # Perform QNT analysis
    analysis=$(humanizer analyze "$quote" --format json 2>/dev/null || echo '{}')
    
    if [ "$analysis" != "{}" ]; then
        # Extract core attributes
        persona_name=$(echo "$analysis" | jq -r '.persona.name // "unknown"')
        persona_conf=$(echo "$analysis" | jq -r '.persona.confidence // 0')
        
        namespace_name=$(echo "$analysis" | jq -r '.namespace.name // "unknown"')
        namespace_conf=$(echo "$analysis" | jq -r '.namespace.confidence // 0')
        
        style_name=$(echo "$analysis" | jq -r '.style.name // "unknown"')
        style_conf=$(echo "$analysis" | jq -r '.style.confidence // 0')
        
        essence_meaning=$(echo "$analysis" | jq -r '.essence.core_meaning // "unknown"')
        essence_conf=$(echo "$analysis" | jq -r '.essence.meaning_density // 0')
        
        echo "  📊 EXTRACTED ATTRIBUTES:"
        echo "    Persona: $persona_name (conf: $persona_conf)"
        echo "    Namespace: $namespace_name (conf: $namespace_conf)"
        echo "    Style: $style_name (conf: $style_conf)"
        echo "    Essence: $essence_meaning (conf: $essence_conf)"
        echo
        
        # Create attribute object using jq to properly escape JSON
        attribute_set=$(jq -n \
            --arg source "$source" \
            --arg text "$quote" \
            --arg persona_name "$persona_name" \
            --argjson persona_conf "$persona_conf" \
            --arg namespace_name "$namespace_name" \
            --argjson namespace_conf "$namespace_conf" \
            --arg style_name "$style_name" \
            --argjson style_conf "$style_conf" \
            --arg essence_meaning "$essence_meaning" \
            --argjson essence_conf "$essence_conf" \
            '{
                source: $source,
                text: $text,
                attributes: {
                    persona: {
                        name: $persona_name,
                        confidence: $persona_conf,
                        type: "persona"
                    },
                    namespace: {
                        name: $namespace_name,
                        confidence: $namespace_conf,
                        type: "namespace"
                    },
                    style: {
                        name: $style_name,
                        confidence: $style_conf,
                        type: "style"
                    },
                    essence: {
                        core_meaning: $essence_meaning,
                        confidence: $essence_conf,
                        type: "essence"
                    }
                }
            }'
        )
        
        # Add to collection
        all_attributes=$(echo "$all_attributes" | jq ". + [$attribute_set]")
        
        # Rate limiting
        sleep 2
    else
        echo "  ❌ Analysis failed for this text"
        echo
    fi
done

# Save results
echo "$all_attributes" > "$WORK_DIR/discovered_attributes.json"

# Generate summary report
echo "========================================"
echo "📋 ATTRIBUTE DISCOVERY SUMMARY"
echo "========================================"
echo

# Count unique attributes by type
unique_personas=$(echo "$all_attributes" | jq -r '.[].attributes.persona.name' | sort -u | wc -l)
unique_namespaces=$(echo "$all_attributes" | jq -r '.[].attributes.namespace.name' | sort -u | wc -l)
unique_styles=$(echo "$all_attributes" | jq -r '.[].attributes.style.name' | sort -u | wc -l)

echo "📊 STATISTICS:"
echo "  Total excerpts analyzed: $(echo "$all_attributes" | jq 'length')"
echo "  Unique personas discovered: $unique_personas"
echo "  Unique namespaces discovered: $unique_namespaces"
echo "  Unique styles discovered: $unique_styles"
echo

echo "🎭 DISCOVERED PERSONAS:"
echo "$all_attributes" | jq -r '.[].attributes.persona | "  • \(.name) (confidence: \(.confidence))"' | sort -u
echo

echo "🌍 DISCOVERED NAMESPACES:"
echo "$all_attributes" | jq -r '.[].attributes.namespace | "  • \(.name) (confidence: \(.confidence))"' | sort -u
echo

echo "✍️ DISCOVERED STYLES:"
echo "$all_attributes" | jq -r '.[].attributes.style | "  • \(.name) (confidence: \(.confidence))"' | sort -u
echo

echo "💎 DISCOVERED ESSENCES:"
echo "$all_attributes" | jq -r '.[].attributes.essence | "  • \(.core_meaning) (confidence: \(.confidence))"' | sort -u
echo

# Create usable attribute list for transformations
echo "📝 CREATING USABLE ATTRIBUTE LIST..."

# Extract unique high-confidence attributes
personas=$(echo "$all_attributes" | jq -r '.[].attributes.persona | select(.confidence > 0.6) | .name' | sort -u)
namespaces=$(echo "$all_attributes" | jq -r '.[].attributes.namespace | select(.confidence > 0.6) | .name' | sort -u)
styles=$(echo "$all_attributes" | jq -r '.[].attributes.style | select(.confidence > 0.6) | .name' | sort -u)

# Create usage file
cat > "$WORK_DIR/usage_examples.sh" <<'EOF'
#!/bin/bash

# Usage Examples for Discovered Attributes
# Run these commands to use the discovered attributes in transformations

echo "🎯 TRANSFORMATION EXAMPLES using discovered attributes:"
echo
EOF

if [ -n "$personas" ]; then
    first_persona=$(echo "$personas" | head -1)
    echo "echo \"📝 Using persona: $first_persona\"" >> "$WORK_DIR/usage_examples.sh"
    echo "humanizer transform \"Your text here\" --persona \"$first_persona\"" >> "$WORK_DIR/usage_examples.sh"
    echo "echo" >> "$WORK_DIR/usage_examples.sh"
fi

if [ -n "$namespaces" ]; then
    first_namespace=$(echo "$namespaces" | head -1)
    echo "echo \"🌍 Using namespace: $first_namespace\"" >> "$WORK_DIR/usage_examples.sh"
    echo "humanizer transform \"Your text here\" --namespace \"$first_namespace\"" >> "$WORK_DIR/usage_examples.sh"
    echo "echo" >> "$WORK_DIR/usage_examples.sh"
fi

if [ -n "$styles" ]; then
    first_style=$(echo "$styles" | head -1)
    echo "echo \"✍️ Using style: $first_style\"" >> "$WORK_DIR/usage_examples.sh"
    echo "humanizer transform \"Your text here\" --style \"$first_style\"" >> "$WORK_DIR/usage_examples.sh"
    echo "echo" >> "$WORK_DIR/usage_examples.sh"
fi

chmod +x "$WORK_DIR/usage_examples.sh"

echo "💾 FILES CREATED:"
echo "  • $WORK_DIR/discovered_attributes.json - Complete attribute data"
echo "  • $WORK_DIR/usage_examples.sh - Ready-to-use transformation commands"
echo

echo "🎯 IMMEDIATE USAGE EXAMPLES:"
echo

if [ -n "$personas" ]; then
    first_persona=$(echo "$personas" | head -1)
    echo "Transform using discovered persona:"
    echo "  humanizer transform \"Your text here\" --persona \"$first_persona\""
    echo
fi

if [ -n "$styles" ]; then
    first_style=$(echo "$styles" | head -1)
    echo "Transform using discovered style:"
    echo "  humanizer transform \"Your text here\" --style \"$first_style\""
    echo
fi

if [ -n "$namespaces" ]; then
    first_namespace=$(echo "$namespaces" | head -1)
    echo "Transform using discovered namespace:"
    echo "  humanizer transform \"Your text here\" --namespace \"$first_namespace\""
    echo
fi

echo "🚀 For large-scale discovery, run: ./attribute_discovery_v2.sh"
echo "✅ Attribute discovery demo complete!"