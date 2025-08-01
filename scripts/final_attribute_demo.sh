#!/bin/bash

# Final Attribute Discovery Demo
# Extracts usable attributes from QNT analysis for transformations

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORK_DIR="${SCRIPT_DIR}/final_demo_$(date +%H%M%S)"

echo "🚀 Final Attribute Discovery Demo"
echo "Extracting usable narrative attributes from classic literature"
echo

# Create workspace
mkdir -p "$WORK_DIR"

# Famous literature excerpts for analysis
declare -a excerpts=(
    "It is a truth universally acknowledged, that a single man in possession of a good fortune, must be in want of a wife."
    "To be or not to be, that is the question: Whether 'tis nobler in the mind to suffer the slings and arrows of outrageous fortune."
    "Call me Ishmael. Some years ago I thought I would sail about a little and see the watery part of the world."
    "It was the best of times, it was the worst of times, it was the age of wisdom, it was the age of foolishness."
    "In a hole in the ground there lived a hobbit. Not a nasty, dirty, wet hole filled with the ends of worms and an oozy smell."
)

declare -a sources=(
    "Pride and Prejudice - Jane Austen"
    "Hamlet - William Shakespeare"  
    "Moby Dick - Herman Melville"
    "A Tale of Two Cities - Charles Dickens"
    "The Hobbit - J.R.R. Tolkien"
)

# Initialize results
persona_list=()
namespace_list=()
style_list=()
essence_list=()

echo "Analyzing excerpts from classic literature..."
echo

# Process each excerpt
for i in "${!excerpts[@]}"; do
    text="${excerpts[$i]}"
    source="${sources[$i]}"
    
    echo "Analyzing: $source"
    echo "Text: \"$(echo "$text" | head -c 60)...\""
    
    # Get analysis in summary format (more reliable than JSON)
    output=$(humanizer analyze "$text" --format summary 2>/dev/null || echo "")
    
    if [ -n "$output" ]; then
        # Extract attributes using grep and sed
        persona=$(echo "$output" | grep "Persona:" | sed 's/.*Persona: \([^(]*\).*/\1/' | xargs)
        namespace=$(echo "$output" | grep "Namespace:" | sed 's/.*Namespace: \([^(]*\).*/\1/' | xargs)
        style=$(echo "$output" | grep "Style:" | sed 's/.*Style: \([^(]*\).*/\1/' | xargs)
        essence=$(echo "$output" | grep "Essence:" | sed 's/.*Essence: \(.*\)/\1/' | xargs)
        
        echo "  ✓ Persona: $persona"
        echo "  ✓ Namespace: $namespace"
        echo "  ✓ Style: $style"
        echo "  ✓ Essence: $essence"
        echo
        
        # Add to lists if not empty and not already present
        if [ -n "$persona" ]; then
            if [ ${#persona_list[@]} -eq 0 ] || [[ ! " ${persona_list[@]} " =~ " ${persona} " ]]; then
                persona_list+=("$persona")
            fi
        fi
        if [ -n "$namespace" ]; then
            if [ ${#namespace_list[@]} -eq 0 ] || [[ ! " ${namespace_list[@]} " =~ " ${namespace} " ]]; then
                namespace_list+=("$namespace")
            fi
        fi
        if [ -n "$style" ]; then
            if [ ${#style_list[@]} -eq 0 ] || [[ ! " ${style_list[@]} " =~ " ${style} " ]]; then
                style_list+=("$style")
            fi
        fi
        if [ -n "$essence" ]; then
            if [ ${#essence_list[@]} -eq 0 ] || [[ ! " ${essence_list[@]} " =~ " ${essence} " ]]; then
                essence_list+=("$essence")
            fi
        fi
        
        # Create individual analysis file
        cat > "$WORK_DIR/analysis_$(printf "%02d" $((i+1))).txt" <<EOF
Source: $source
Text: $text

EXTRACTED ATTRIBUTES:
Persona: $persona
Namespace: $namespace  
Style: $style
Essence: $essence
EOF
        
    else
        echo "  ❌ Analysis failed"
        echo
    fi
    
    # Rate limiting
    sleep 2
done

# Generate summary
echo "========================================"
echo "📋 ATTRIBUTE DISCOVERY RESULTS"
echo "========================================"
echo

echo "📊 DISCOVERED ATTRIBUTES:"
echo
echo "🎭 PERSONAS (${#persona_list[@]} unique):"
for persona in "${persona_list[@]}"; do
    echo "  • $persona"
done
echo

echo "🌍 NAMESPACES (${#namespace_list[@]} unique):"
for namespace in "${namespace_list[@]}"; do
    echo "  • $namespace"
done
echo

echo "✍️ STYLES (${#style_list[@]} unique):"
for style in "${style_list[@]}"; do
    echo "  • $style"
done
echo

echo "💎 ESSENCES (${#essence_list[@]} unique):"
for essence in "${essence_list[@]}"; do
    echo "  • $essence"
done
echo

# Create usable attribute lists
cat > "$WORK_DIR/discovered_personas.txt" <<EOF
# Discovered Personas
# Use with: humanizer transform "text" --persona "persona_name"
EOF

for persona in "${persona_list[@]}"; do
    echo "$persona" >> "$WORK_DIR/discovered_personas.txt"
done

cat > "$WORK_DIR/discovered_namespaces.txt" <<EOF
# Discovered Namespaces  
# Use with: humanizer transform "text" --namespace "namespace_name"
EOF

for namespace in "${namespace_list[@]}"; do
    echo "$namespace" >> "$WORK_DIR/discovered_namespaces.txt"
done

cat > "$WORK_DIR/discovered_styles.txt" <<EOF
# Discovered Styles
# Use with: humanizer transform "text" --style "style_name"
EOF

for style in "${style_list[@]}"; do
    echo "$style" >> "$WORK_DIR/discovered_styles.txt"
done

# Create usage examples
cat > "$WORK_DIR/usage_examples.sh" <<'EOF'
#!/bin/bash

echo "🎯 Transformation Examples using Discovered Attributes"
echo "======================================================"
echo

EOF

if [ ${#persona_list[@]} -gt 0 ]; then
    cat >> "$WORK_DIR/usage_examples.sh" <<EOF
echo "🎭 Using Discovered Personas:"
humanizer transform "The old wizard looked at the young apprentice." --persona "${persona_list[0]}"
echo
EOF
fi

if [ ${#namespace_list[@]} -gt 0 ]; then
    cat >> "$WORK_DIR/usage_examples.sh" <<EOF
echo "🌍 Using Discovered Namespaces:"
humanizer transform "The meeting will begin at nine o'clock." --namespace "${namespace_list[0]}"
echo
EOF
fi

if [ ${#style_list[@]} -gt 0 ]; then
    cat >> "$WORK_DIR/usage_examples.sh" <<EOF
echo "✍️ Using Discovered Styles:"
humanizer transform "She walked down the street slowly." --style "${style_list[0]}"
echo
EOF
fi

chmod +x "$WORK_DIR/usage_examples.sh"

echo "💾 FILES CREATED:"
echo "  • $WORK_DIR/discovered_personas.txt - List of usable personas"
echo "  • $WORK_DIR/discovered_namespaces.txt - List of usable namespaces"
echo "  • $WORK_DIR/discovered_styles.txt - List of usable styles"
echo "  • $WORK_DIR/usage_examples.sh - Transformation examples"
echo "  • $WORK_DIR/analysis_01.txt through analysis_05.txt - Individual analyses"
echo

echo "🎯 IMMEDIATE USAGE EXAMPLES:"
echo

if [ ${#persona_list[@]} -gt 0 ]; then
    echo "Transform using discovered persona:"
    echo "  humanizer transform \"Your text here\" --persona \"${persona_list[0]}\""
    echo
fi

if [ ${#style_list[@]} -gt 0 ]; then
    echo "Transform using discovered style:"
    echo "  humanizer transform \"Your text here\" --style \"${style_list[0]}\""
    echo
fi

if [ ${#namespace_list[@]} -gt 0 ]; then
    echo "Transform using discovered namespace:"
    echo "  humanizer transform \"Your text here\" --namespace \"${namespace_list[0]}\""
    echo
fi

echo "🧪 Test the examples:"
echo "  cd $WORK_DIR && ./usage_examples.sh"
echo

echo "🚀 For large-scale discovery from Gutenberg books:"
echo "  ./attribute_discovery_v2.sh"
echo

echo "✅ Attribute discovery complete!"
echo "📋 Check the files above for complete lists of usable attributes"