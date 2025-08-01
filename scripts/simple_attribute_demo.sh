#!/bin/bash

# Simple Attribute Discovery Demo - Clean output without color conflicts

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORK_DIR="${SCRIPT_DIR}/simple_demo_$(date +%H%M%S)"

echo "🚀 Simple Attribute Discovery Demo"
echo "Extracting real QNT attributes from Gutenberg content"
echo

# Create workspace
mkdir -p "$WORK_DIR"

# Start analysis job
echo "Starting analysis job for Pride and Prejudice (Book 1342)..."
job_output=$(humanizer gutenberg analyze 1342 --type sample)
job_id=$(echo "$job_output" | grep -oE '[a-f0-9-]{36}' | head -1)

if [ -z "$job_id" ]; then
    echo "Failed to start analysis job"
    exit 1
fi

echo "Job ID: $job_id"

# Wait for completion
echo "Waiting for job completion..."
sleep 15

# Get results and extract one paragraph for analysis
echo "Extracting paragraph for QNT analysis..."
first_paragraph=$(curl -s "http://localhost:8100/gutenberg/jobs/$job_id/results" | jq -r '.data.results[0].paragraph_text')

echo "Sample paragraph:"
echo "\"$(echo "$first_paragraph" | head -c 200)...\""
echo

# Perform QNT analysis
echo "Performing QNT analysis..."
analysis=$(humanizer analyze "$first_paragraph" --format json 2>/dev/null || echo '{}')

if [ "$analysis" != "{}" ]; then
    # Save the analysis
    echo "$analysis" > "$WORK_DIR/qnt_analysis.json"
    
    # Extract and display attributes
    echo "📊 DISCOVERED ATTRIBUTES:"
    echo
    
    echo "PERSONA:"
    persona_name=$(echo "$analysis" | jq -r '.persona.name // "unknown"')
    persona_conf=$(echo "$analysis" | jq -r '.persona.confidence // 0')
    echo "  • Name: $persona_name"
    echo "  • Confidence: $persona_conf"
    echo "  • Characteristics: $(echo "$analysis" | jq -r '.persona.characteristics // [] | join(", ")')"
    echo
    
    echo "NAMESPACE:"
    namespace_name=$(echo "$analysis" | jq -r '.namespace.name // "unknown"')
    namespace_conf=$(echo "$analysis" | jq -r '.namespace.confidence // 0')
    echo "  • Name: $namespace_name"
    echo "  • Confidence: $namespace_conf"
    echo "  • Cultural Context: $(echo "$analysis" | jq -r '.namespace.cultural_context // "unknown"')"
    echo
    
    echo "STYLE:"
    style_name=$(echo "$analysis" | jq -r '.style.name // "unknown"')
    style_conf=$(echo "$analysis" | jq -r '.style.confidence // 0')
    echo "  • Name: $style_name"
    echo "  • Confidence: $style_conf"
    echo "  • Tone: $(echo "$analysis" | jq -r '.style.tone // "unknown"')"
    echo
    
    echo "ESSENCE:"
    essence_meaning=$(echo "$analysis" | jq -r '.essence.core_meaning // "unknown"')
    essence_conf=$(echo "$analysis" | jq -r '.essence.meaning_density // 0')
    echo "  • Core Meaning: $essence_meaning"
    echo "  • Confidence: $essence_conf"
    echo
    
    # Create usable attribute file
    cat > "$WORK_DIR/extracted_attributes.json" <<EOF
{
  "persona": {
    "name": "$persona_name",
    "confidence": $persona_conf,
    "type": "persona"
  },
  "namespace": {
    "name": "$namespace_name", 
    "confidence": $namespace_conf,
    "type": "namespace"
  },
  "style": {
    "name": "$style_name",
    "confidence": $style_conf,
    "type": "style"
  },
  "essence": {
    "core_meaning": "$essence_meaning",
    "confidence": $essence_conf,
    "type": "essence"
  }
}
EOF
    
    echo "💾 Results saved to: $WORK_DIR/"
    echo "   • qnt_analysis.json - Full QNT analysis"
    echo "   • extracted_attributes.json - Clean attribute data"
    echo
    
    echo "🎯 USAGE EXAMPLES:"
    echo
    echo "Transform using discovered persona:"
    echo "   humanizer transform \"Your text here\" --persona \"$persona_name\""
    echo
    echo "Transform using discovered style:"
    echo "   humanizer transform \"Your text here\" --style \"$style_name\""
    echo
    echo "Transform using discovered namespace:"
    echo "   humanizer transform \"Your text here\" --namespace \"$namespace_name\""
    echo
    
    echo "✅ Attribute discovery complete!"
    echo "🚀 Run the full pipeline with: ./attribute_discovery_v2.sh"
else
    echo "❌ QNT analysis failed"
fi