#!/bin/bash
# Heart Sutra Science Article Generation
# Personal shell script for filtering and selecting content

echo "🧘 Heart Sutra Science Content Discovery"
echo "========================================"

# Heart Sutra Science related terms
FILTER_TERMS="heart sutra,quantum,consciousness,emptiness,sunyata,form is emptiness,quantum mechanics,observer effect,interdependence,non-dual,meditation,mindfulness,quantum field,void,physics"

# Search queries for different aspects
QUERIES=(
    "quantum consciousness and emptiness meditation practice"
    "observer effect and non-dual awareness" 
    "form is emptiness quantum field theory"
    "interdependence and quantum entanglement"
    "void consciousness and quantum vacuum"
    "mindfulness and quantum measurement"
    "meditation states and quantum coherence"
    "emptiness doctrine and quantum mechanics"
    "heart sutra physics consciousness"
    "sunyata and quantum reality"
)

echo "🔍 Running searches for Heart Sutra Science content..."
echo ""

# Create output directory
mkdir -p heart_sutra_results
cd heart_sutra_results

# Run searches and collect results
for i in "${!QUERIES[@]}"; do
    query="${QUERIES[$i]}"
    output_file="search_$((i+1)).json"
    
    echo "[$((i+1))/${#QUERIES[@]}] Searching: '$query'"
    
    python ../embedding_cli.py search "$query" \
        --filter-terms $FILTER_TERMS \
        --max-results 15 \
        --levels 0 1 2 \
        --output "$output_file"
    
    if [ -f "$output_file" ]; then
        echo "   ✅ Results saved to $output_file"
    else
        echo "   ❌ Search failed"
    fi
    echo ""
done

# Combine and deduplicate results
echo "🔄 Combining and analyzing results..."

python3 << 'EOF'
import json
import os
from collections import defaultdict

# Load all search results
all_results = []
result_files = [f for f in os.listdir('.') if f.startswith('search_') and f.endswith('.json')]

for file in result_files:
    try:
        with open(file, 'r') as f:
            results = json.load(f)
            if isinstance(results, list):
                all_results.extend(results)
    except:
        continue

print(f"📊 Total results collected: {len(all_results)}")

# Deduplicate by chunk_id
unique_results = {}
for result in all_results:
    chunk_id = result.get('chunk_id')
    if chunk_id:
        if chunk_id not in unique_results or result['relevance_score'] > unique_results[chunk_id]['relevance_score']:
            unique_results[chunk_id] = result

print(f"📊 Unique chunks after deduplication: {len(unique_results)}")

# Group by conversation and level
conv_groups = defaultdict(lambda: defaultdict(list))
for result in unique_results.values():
    conv_id = result['conversation_id']
    level = result['level']
    conv_groups[conv_id][level].append(result)

print(f"📊 Conversations with relevant content: {len(conv_groups)}")

# Sort by average relevance score per conversation
conv_scores = {}
for conv_id, levels in conv_groups.items():
    scores = []
    for level_results in levels.values():
        scores.extend([r['relevance_score'] for r in level_results])
    conv_scores[conv_id] = sum(scores) / len(scores) if scores else 0

# Get top conversations
top_conversations = sorted(conv_scores.items(), key=lambda x: x[1], reverse=True)[:10]

print(f"\n🎯 Top 10 Conversations for Heart Sutra Science:")
print("=" * 60)

for i, (conv_id, avg_score) in enumerate(top_conversations, 1):
    levels = conv_groups[conv_id]
    chunk_count = sum(len(chunks) for chunks in levels.values())
    
    print(f"{i:2}. Conversation {conv_id} | Score: {avg_score:.3f} | {chunk_count} chunks")
    
    # Show level distribution
    level_counts = {level: len(chunks) for level, chunks in levels.items()}
    level_str = ", ".join([f"L{level}: {count}" for level, count in sorted(level_counts.items())])
    print(f"    Levels: {level_str}")
    
    # Show top chunk from this conversation
    best_chunk = max(
        [chunk for chunks in levels.values() for chunk in chunks],
        key=lambda x: x['relevance_score']
    )
    content_preview = best_chunk['content'][:150] + "..." if len(best_chunk['content']) > 150 else best_chunk['content']
    print(f"    Best: {content_preview}")
    print()

# Save curated results
curated_results = []
for conv_id, _ in top_conversations:
    for level_results in conv_groups[conv_id].values():
        curated_results.extend(level_results)

with open('heart_sutra_curated.json', 'w') as f:
    json.dump(curated_results, f, indent=2)

print(f"💾 Curated results saved to heart_sutra_curated.json ({len(curated_results)} chunks)")
EOF

echo ""
echo "🎉 Heart Sutra Science content discovery complete!"
echo ""
echo "📁 Results in: $(pwd)"
echo "📄 Curated collection: heart_sutra_curated.json"
echo ""
echo "💡 Next steps:"
echo "   1. Review heart_sutra_curated.json for article material"
echo "   2. Use 'ha archive get [conversation_id]' to get full conversations"
echo "   3. Process selected content through transformation pipeline"