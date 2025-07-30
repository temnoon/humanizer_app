# Humanizer CLI Usage Guide

## Overview
The `humanizer_cli.py` is a minimal command-line interface for the Enhanced Humanizer API. It provides access to all core functionality with file output support and Unix pipe compatibility.

## Prerequisites
- Enhanced API server running on port 8100
- Valid API keys stored in macOS keychain (for cloud providers)
- Python environment with requests library

## Quick Start

### 1. Check API Status
```bash
python humanizer_cli.py status
```

### 2. Transform Text
```bash
# Basic transformation
echo "Hello world" | python humanizer_cli.py transform

# With custom parameters
python humanizer_cli.py transform \
  --text "The quick brown fox" \
  --persona "dramatic_voice" \
  --namespace "literary_realism" \
  --style "lyrical_prose"

# From file with output
python humanizer_cli.py transform \
  --file input.txt \
  --output transformed.txt
```

### 3. Extract Attributes
```bash
# Extract narrative DNA
python humanizer_cli.py attributes \
  --text "She walked through the moonlit garden" \
  --output attributes.json

# From stdin
echo "The storm raged violently" | python humanizer_cli.py attributes
```

### 4. Analyze Meaning
```bash
# Lamish meaning analysis
python humanizer_cli.py analyze \
  --file document.txt \
  --output analysis.json

# Quantum narrative theory
python humanizer_cli.py quantum \
  --text "Time flows like a river" \
  --output quantum_analysis.json
```

## Command Reference

### Commands
- `transform` - Narrative transformation with persona/namespace/style
- `attributes` - Extract narrative attributes (persona, style, themes)
- `analyze` - Lamish meaning analysis
- `quantum` - Quantum narrative theory analysis
- `status` - Show LLM provider status and API health

### Options
- `--text, -t` - Input text directly
- `--file, -f` - Read from input file
- `--output, -o` - Output file (.json for JSON, other for formatted text)
- `--persona, -p` - Target persona (default: philosophical_narrator)
- `--namespace, -n` - Target namespace (default: existential_philosophy)
- `--style, -s` - Target style (default: contemplative_prose)
- `--api-base` - API base URL (default: http://127.0.0.1:8100)

### Input Methods
1. **Command line**: `--text "your text here"`
2. **File**: `--file path/to/file.txt`
3. **Stdin**: `echo "text" | python humanizer_cli.py command`
4. **Interactive**: Run command without input, then type/paste text

### Output Formats
- **No --output**: Display results in terminal
- **--output file.json**: Save full JSON response
- **--output file.txt**: Save formatted text summary

## Usage Examples

### Batch Processing
```bash
# Process multiple files
for file in docs/*.txt; do
  python humanizer_cli.py transform \
    --file "$file" \
    --output "transformed/$(basename "$file")"
done

# Pipeline processing
cat input.txt | \
  python humanizer_cli.py transform \
    --persona "analytical_observer" | \
  python humanizer_cli.py attributes > analysis.txt
```

### Integration with Unix Tools
```bash
# Count words in transformed text
echo "Original text" | \
  python humanizer_cli.py transform | \
  wc -w

# Search for patterns
python humanizer_cli.py transform \
  --file document.txt | \
  grep -i "existence"

# Compare transformations
diff <(echo "Text" | python humanizer_cli.py transform --persona "narrator1") \
     <(echo "Text" | python humanizer_cli.py transform --persona "narrator2")
```

### Configuration Profiles
```bash
# Create aliases for common configurations
alias transform_academic="python humanizer_cli.py transform --persona analytical_observer --namespace academic_discourse --style formal_literary"
alias transform_creative="python humanizer_cli.py transform --persona poetic_speaker --namespace literary_fiction --style lyrical_prose"

# Use aliases
echo "Sample text" | transform_academic
echo "Sample text" | transform_creative
```

## Available Personas
- `philosophical_narrator` - Contemplative, existential perspective
- `analytical_observer` - Scientific, methodical approach
- `dramatic_voice` - Emotional, theatrical expression
- `conversational_voice` - Casual, accessible tone
- `authoritative_narrator` - Formal, decisive presentation
- `intimate_storyteller` - Personal, warm communication
- `poetic_speaker` - Artistic, metaphorical language
- `omniscient_voice` - All-knowing, objective perspective
- `reflective_narrator` - Thoughtful, introspective approach

## Available Namespaces
- `existential_philosophy` - Questions of being and meaning
- `moral_philosophy` - Ethics and values
- `psychological_narrative` - Mental and emotional processes
- `literary_realism` - Realistic, grounded storytelling
- `social_commentary` - Cultural and political analysis
- `historical_fiction` - Period-appropriate context
- `academic_discourse` - Scholarly communication
- `literary_fiction` - Creative, artistic expression

## Available Styles
- `contemplative_prose` - Thoughtful, reflective writing
- `stream_of_consciousness` - Free-flowing, unstructured
- `lyrical_prose` - Musical, poetic language
- `analytical_writing` - Logical, structured argument
- `formal_literary` - Traditional, elevated language
- `descriptive_prose` - Rich, detailed imagery
- `dialogue_heavy` - Conversation-focused narrative
- `dramatic_narrative` - Tension and conflict emphasis

## Error Handling
- **API Connection**: CLI checks API health before processing
- **File Not Found**: Clear error message with file path
- **Invalid Parameters**: Helpful usage information
- **API Errors**: Displays server error messages
- **Timeout**: 120-second timeout for transform operations

## Performance Notes
- **Transform**: 30-120 seconds depending on text length and complexity
- **Attributes**: Usually under 5 seconds
- **Analysis**: 10-60 seconds for comprehensive analysis
- **Status**: Near-instantaneous

## Existing CLI Tools (Preserved)
The new CLI coexists with existing specialized tools:
- `allegory_cli.py` - Allegory-specific transformations
- `attribute_browser_cli.py` - Browse attribute collections
- `conversation_browser.py` - Conversation data exploration
- Various test scripts for specific functionality

## Database Integration
The Enhanced API uses hybrid database architecture:
- **PostgreSQL**: Conversation archive (`humanizer_archive`)
- **SQLite**: Metadata and job queues
- **ChromaDB**: Vector embeddings for semantic search
- **FAISS**: High-performance vector operations
- **File Storage**: Content-addressed blobs

All processing is handled by the API server; the CLI is purely a client interface with no direct database access.

## Troubleshooting

### CLI Won't Connect
```bash
# Check if API server is running
curl http://127.0.0.1:8100/health

# Start API server
python api_enhanced.py
```

### Slow Performance
- Check provider status: `python humanizer_cli.py status`
- Use local Ollama models for faster processing
- Reduce text length for initial testing

### Authentication Issues
- API uses keychain-stored keys automatically
- Check key validity in status output
- Store new keys via API endpoints if needed

The CLI provides a clean, scriptable interface to the full Humanizer transformation pipeline while keeping all business logic in the API server.