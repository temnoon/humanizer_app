# Archive CLI Integration Guide

## Overview

The Archive CLI provides seamless integration between PostgreSQL conversation archives and the Humanizer transformation pipeline. This allows you to retrieve, select, and process archived conversations through the Lamish Projection Engine.

## Prerequisites

1. **PostgreSQL Archive Database**: `humanizer_archive` database with imported conversations
2. **Enhanced API Running**: The transformation API on port 8100
3. **Python Environment**: Virtual environment with required dependencies

## Setup

### 1. Activate Environment
```bash
cd /Users/tem/humanizer-lighthouse/humanizer_api/lighthouse
source venv/bin/activate
```

### 2. Verify Archive Access
```bash
# Check database connection
psql -d humanizer_archive -c "SELECT COUNT(*) FROM archived_content WHERE content_type = 'conversation';"

# Should show conversation count (e.g., 3846 conversations)
```

### 3. Verify API Status
```bash
# Check Enhanced API health
curl http://127.0.0.1:8100/health
```

## Archive CLI Commands

### List Conversations
```bash
# Basic listing (page 1, 20 results)
python archive_cli.py list

# Paginated listing
python archive_cli.py list --page 2 --limit 10

# Search conversations
python archive_cli.py list --search "quantum" --limit 5
```

**Example Output:**
```
================================================================================
ARCHIVED CONVERSATIONS:
================================================================================
ID: 265277 | Please give me the following content condensed ......
    Messages: 0 | Words: 0 | Author: unknown
    Created: 2025-07-09T19:21:47

ID: 228072 | Understanding Quantum Mechanics......
    Messages: 15 | Words: 2847 | Author: user
    Created: 2025-07-08T16:47:04
```

### Get Conversation Details
```bash
# View conversation with messages
python archive_cli.py get 203110

# Save conversation to file
python archive_cli.py get 203110 --output conversation.json
```

**Example Output:**
```
================================================================================
CONVERSATION: Introduction to GAT Formalisms
Author: unknown | Created: 2024-09-14T00:43:55
================================================================================
1. [user] (2024-09-14T00:43:55)
   Give me a gentle introduction to the formalisms of GAT...

2. [assistant] (2024-09-14T00:44:13)
   ### Introduction to General Agent Theory (GAT) Formalisms...
```

### Search Archive Content
```bash
# Full-text search across all content
python archive_cli.py search "phenomenology" --limit 10

# Save search results
python archive_cli.py search "quantum mechanics" --output search_results.json
```

### Transform Conversations
```bash
# Transform with default settings (philosophical_narrator)
python archive_cli.py transform 203110

# Custom transformation parameters
python archive_cli.py transform 203110 \
  --persona "scientific_researcher" \
  --namespace "quantum_physics" \
  --style "academic_prose"

# Save transformation result
python archive_cli.py transform 203110 --output transformed_conversation.json
```

**Transformation Output:**
- Original conversation messages combined
- Transformed narrative using LPE
- Reflection on the transformation process
- Processing metadata

## Workflow Examples

### 1. Content Discovery & Selection
```bash
# Find conversations about specific topics
python archive_cli.py search "machine learning" --limit 20

# Browse conversations by date/size
python archive_cli.py list --page 1 --limit 50

# Examine promising conversations
python archive_cli.py get 245123
```

### 2. Content Processing Pipeline
```bash
# Transform for different audiences
python archive_cli.py transform 245123 --persona "general_public" --output public_version.json
python archive_cli.py transform 245123 --persona "expert_researcher" --output expert_version.json

# Process multiple conversations
for id in 245123 203110 197199; do
  python archive_cli.py transform $id --output "transformed_$id.json"
done
```

### 3. Batch Processing with Unix Pipes
```bash
# Extract conversation IDs for processing
python archive_cli.py list --search "AI" --limit 100 | 
  grep "ID:" | 
  cut -d: -f2 | 
  cut -d'|' -f1 | 
  while read id; do
    echo "Processing conversation $id"
    python archive_cli.py transform $id --output "ai_transformed_$id.json"
  done
```

## Advanced Usage

### 1. Content Quality Filtering
```bash
# Find conversations with substantial content
psql -d humanizer_archive -c "
SELECT c.id, c.title, COUNT(m.id) as message_count
FROM archived_content c
LEFT JOIN archived_content m ON c.id = m.parent_id
WHERE c.content_type = 'conversation' 
GROUP BY c.id, c.title
HAVING COUNT(m.id) BETWEEN 5 AND 50
ORDER BY COUNT(m.id) DESC
LIMIT 20;
" | grep -E "^\s+[0-9]+" | while read id title count; do
  python archive_cli.py transform $id --output "quality_$id.json"
done
```

### 2. Thematic Processing
```bash
# Process all conversations about specific domains
THEMES=("quantum" "consciousness" "AI" "philosophy")

for theme in "${THEMES[@]}"; do
  echo "Processing theme: $theme"
  mkdir -p "processed_$theme"
  
  python archive_cli.py search "$theme" --limit 50 --output "$theme_search.json"
  
  # Extract conversation IDs and process
  grep '"id":' "$theme_search.json" | 
    sed 's/.*"id": *\([0-9]*\).*/\1/' | 
    while read conv_id; do
      python archive_cli.py transform $conv_id \
        --namespace "${theme}_studies" \
        --output "processed_$theme/conversation_$conv_id.json"
    done
done
```

### 3. Media Link Integration
For conversations with media attachments (future enhancement):
```bash
# Process conversations with media content
python archive_cli.py get 245123 | grep -q "media" && \
  python archive_cli.py transform 245123 --include-media --output rich_content.json
```

## File Output Formats

### JSON Output Structure
```json
{
  "conversation": {
    "id": 203110,
    "title": "Introduction to GAT Formalisms",
    "author": "unknown",
    "timestamp": "2024-09-14T00:43:55"
  },
  "original_messages": [...],
  "combined_content": "[user]: Give me a gentle introduction...",
  "transformation": {
    "original": {...},
    "projection": {
      "narrative": "The rain, it seemed, was but a whispered echo...",
      "reflection": "Okay, let's unpack this existential_philosophy version..."
    },
    "steps": [...]
  }
}
```

## Integration Points

### 1. With Humanizer CLI
```bash
# Use both CLIs together
python archive_cli.py get 203110 --output raw.json
python humanizer_cli.py transform --file raw.json --output enhanced.json
```

### 2. With PostgreSQL Queries
```bash
# Direct database integration
psql -d humanizer_archive -c "
  SELECT body_text FROM archived_content 
  WHERE parent_id = 203110 AND content_type = 'message'
  ORDER BY timestamp ASC
" | python humanizer_cli.py transform --persona scientific_researcher
```

### 3. With External Tools
```bash
# Export to various formats
python archive_cli.py transform 203110 --output result.json
jq '.transformation.projection.narrative' result.json > narrative.txt
pandoc narrative.txt -o narrative.pdf
```

## Performance Considerations

### 1. Database Optimization
- Use indexed searches when possible
- Limit result sets for large archives
- Consider conversation size for transformations

### 2. Transformation Efficiency
- Shorter conversations (3-20 messages) transform faster
- Very long conversations may timeout or use excessive tokens
- Batch processing with delays for rate limiting

### 3. Memory Management
- Save outputs to files for large transformations
- Clean up temporary files regularly
- Monitor disk space for batch operations

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   ```bash
   # Check PostgreSQL service
   brew services list | grep postgresql
   # Restart if needed
   brew services restart postgresql
   ```

2. **Enhanced API Not Responding**
   ```bash
   # Check if API is running
   lsof -ti:8100
   # Start if needed
   python api_enhanced.py
   ```

3. **Virtual Environment Issues**
   ```bash
   # Ensure correct environment
   source venv/bin/activate
   which python  # Should show venv path
   ```

4. **Transformation Timeouts**
   - Use shorter conversations for testing
   - Check API logs for errors
   - Verify LLM provider keys are configured

### Debug Commands
```bash
# Test database connectivity
python -c "from archive_cli import ArchiveCLI; cli = ArchiveCLI(); print(len(cli.list_conversations()))"

# Test API connectivity  
curl http://127.0.0.1:8100/health

# Check conversation data
python archive_cli.py get [conversation_id] | head -20
```

## Future Enhancements

1. **Media Link Support**: Process conversations with attachments
2. **Semantic Search**: Vector-based content discovery
3. **Batch Processing UI**: Web interface for large-scale processing
4. **Export Formats**: Direct export to PDF, EPUB, etc.
5. **Quality Metrics**: Content scoring and filtering
6. **Template System**: Custom transformation templates

This archive integration provides a complete pipeline from content discovery to narrative transformation, enabling powerful content curation and processing workflows.