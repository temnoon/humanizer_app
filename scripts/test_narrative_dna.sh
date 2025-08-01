#!/bin/bash

# Test script for Narrative DNA extraction endpoints

set -euo pipefail

API_URL="http://localhost:8100"

echo "🧪 Testing Narrative DNA Extraction Endpoints"
echo "=============================================="
echo

# Test API connectivity
echo "1. Testing API connectivity..."
if curl -s "${API_URL}/health" > /dev/null; then
    echo "   ✅ API is reachable"
else
    echo "   ❌ Cannot reach API at $API_URL"
    exit 1
fi

# Test strategic sampling endpoint
echo
echo "2. Testing strategic sampling endpoint..."
echo "   Creating strategic sampling job for Pride and Prejudice (1342)..."

response=$(curl -s -X POST "${API_URL}/gutenberg/strategic-sample" \
    -H "Content-Type: application/json" \
    -d '{
        "gutenberg_id": 1342,
        "sample_count": 10,
        "min_length": 100,
        "max_length": 400,
        "avoid_first_last_percent": 0.15
    }')

echo "   Response: $response"

job_id=$(echo "$response" | jq -r '.data.job_id // empty')

if [ -n "$job_id" ]; then
    echo "   ✅ Strategic sampling job created: $job_id"
    
    # Wait a moment for job to complete
    echo "   ⏳ Waiting for job completion..."
    sleep 15
    
    # Check job status
    status_response=$(curl -s "${API_URL}/gutenberg/jobs/$job_id")
    status=$(echo "$status_response" | jq -r '.status // "unknown"')
    echo "   Job status: $status"
    
    if [ "$status" = "completed" ]; then
        echo "   ✅ Strategic sampling completed"
        
        # Get results
        results=$(curl -s "${API_URL}/gutenberg/jobs/$job_id/results")
        paragraph_count=$(echo "$results" | jq '.data.results.sampling_metadata.total_sampled // 0')
        echo "   📊 Extracted $paragraph_count strategic paragraphs"
        
        # Test composite analysis
        echo
        echo "3. Testing composite analysis endpoint..."
        composite_response=$(curl -s -X POST "${API_URL}/gutenberg/composite-analysis?job_id=$job_id")
        echo "   Response: $composite_response"
        
        composite_job_id=$(echo "$composite_response" | jq -r '.data.composite_job_id // empty')
        
        if [ -n "$composite_job_id" ]; then
            echo "   ✅ Composite analysis job created: $composite_job_id"
            
            # Wait for composite analysis
            echo "   ⏳ Waiting for composite analysis completion..."
            sleep 12
            
            # Check composite job status
            composite_status_response=$(curl -s "${API_URL}/gutenberg/jobs/$composite_job_id")
            composite_status=$(echo "$composite_status_response" | jq -r '.status // "unknown"')
            echo "   Composite job status: $composite_status"
            
            if [ "$composite_status" = "completed" ]; then
                echo "   ✅ Composite analysis completed"
                
                # Get narrative DNA results
                dna_results=$(curl -s "${API_URL}/gutenberg/jobs/$composite_job_id/results")
                
                # Extract key narrative DNA elements
                persona=$(echo "$dna_results" | jq -r '.data.results.narrative_dna.dominant_persona.name // "unknown"')
                namespace=$(echo "$dna_results" | jq -r '.data.results.narrative_dna.consistent_namespace.name // "unknown"')
                style=$(echo "$dna_results" | jq -r '.data.results.narrative_dna.predominant_style.name // "unknown"')
                
                echo
                echo "🧬 EXTRACTED NARRATIVE DNA:"
                echo "   🎭 Persona: $persona"
                echo "   🌍 Namespace: $namespace"
                echo "   ✍️ Style: $style"
                
                echo
                echo "✅ All tests passed! Narrative DNA extraction is working."
            else
                echo "   ⚠️ Composite analysis still running or failed: $composite_status"
            fi
        else
            echo "   ❌ Failed to create composite analysis job"
        fi
    else
        echo "   ⚠️ Strategic sampling still running or failed: $status"
    fi
else
    echo "   ❌ Failed to create strategic sampling job"
fi

echo
echo "🎯 Test complete! You can now run the full narrative DNA extractor:"
echo "   ./narrative_dna_extractor.sh"