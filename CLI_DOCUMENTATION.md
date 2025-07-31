# Humanizer CLI - Comprehensive Documentation 📖

Complete user and administrator guide for the Humanizer CLI tool with API endpoint mappings.

## 📋 Table of Contents

1. [Installation & Setup](#installation--setup)
2. [CLI Architecture](#cli-architecture)
3. [User Guide](#user-guide)
4. [Administrator Guide](#administrator-guide)
5. [API Endpoint Mappings](#api-endpoint-mappings)
6. [Configuration Management](#configuration-management)
7. [Troubleshooting](#troubleshooting)
8. [Advanced Usage](#advanced-usage)

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.11+
- Active Humanizer API server (default: http://localhost:8100)
- Terminal/Command line access

### Installation Methods

#### Method 1: Automated Installation (Recommended)
```bash
cd unified-platform
./install_cli.sh
```

#### Method 2: Manual Installation
```bash
# 1. Copy CLI to system location
sudo cp unified-platform/cli/humanizer_standalone /usr/local/bin/humanizer
sudo chmod +x /usr/local/bin/humanizer

# 2. Verify installation
humanizer --help
```

### Initial Setup
```bash
# Verify connection to API
humanizer health

# Check provider status
humanizer providers

# View current configuration
humanizer config
```

---

## 🏗️ CLI Architecture

### Command Structure
```
humanizer [GLOBAL_OPTIONS] <COMMAND> [SUBCOMMAND] [OPTIONS] [ARGUMENTS]
```

### Global Options
- `--api-url <URL>` - Override default API endpoint (default: http://localhost:8100)
- `--verbose` - Enable verbose output for debugging
- `--help` - Show help information

### Command Categories
1. **System Management** - Health, status, configuration
2. **Narrative Analysis** - QNT analysis and transformations
3. **Gutenberg Integration** - Book search and analysis
4. **Attribute Management** - Save, organize, and analyze attributes
5. **Testing & Development** - Test suites and debugging

---

## 👤 User Guide

### 1. System Commands

#### `humanizer health`
**Purpose**: Check system health and API connectivity
**API Endpoint**: `GET /health`

```bash
# Basic health check
humanizer health

# With custom API URL
humanizer --api-url http://localhost:8100 health
```

**Example Output**:
```
✅ API Health Check
🔗 API URL: http://localhost:8100
⚡ Status: Healthy
🕐 Response Time: 12ms
🧠 LLM Provider: OllamaProvider
📊 System: Ready
```

#### `humanizer providers`
**Purpose**: Check LLM provider status and availability
**API Endpoint**: `GET /providers`

```bash
humanizer providers
```

**Example Output**:
```
🤖 LLM Provider Status
━━━━━━━━━━━━━━━━━━━━
Provider        Status      Models    Response Time
────────────────────────────────────────────────────
Ollama          ✅ Active   12        45ms
OpenAI          ❌ No Key   -         -
Anthropic       ❌ No Key   -         -
DeepSeek        ❌ No Key   -         -
```

#### `humanizer config`
**Purpose**: Display current configuration
**API Endpoint**: `GET /health` (includes config info)

```bash
humanizer config
```

---

### 2. Narrative Analysis Commands

#### `humanizer analyze <narrative> [OPTIONS]`
**Purpose**: Perform Quantum Narrative Theory analysis
**API Endpoint**: `POST /api/narrative-theory/analyze`

**Options**:
- `--depth <basic|standard|deep>` - Analysis depth (default: standard)
- `--quantum` - Include quantum state analysis
- `--vectors` - Include essence vectors
- `--format <table|json|summary>` - Output format (default: table)
- `--save <name>` - Save analysis with given name

```bash
# Basic analysis
humanizer analyze "To be or not to be, that is the question"

# Deep analysis with quantum state
humanizer analyze "The lighthouse stood sentinel against the storm" \
    --depth deep --quantum --format table

# Analysis with essence vectors in JSON format
humanizer analyze "In the beginning was the Word" \
    --vectors --format json

# Save analysis for later use
humanizer analyze "Once upon a time in a distant land" \
    --save "fairy_tale_sample" --depth standard
```

**Example Output (Table Format)**:
```
🧬 Quantum Narrative Theory Analysis
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Analysis ID: a1b2c3d4-e5f6-7890-1234-567890abcdef

🎭 Persona (Ψ)
  Name: philosophical contemplator
  Confidence: 87.5%
  Characteristics: introspective, existential, questioning
  Voice Indicators: rhetorical questions, metaphysical language

🌍 Namespace (Ω)  
  Name: renaissance drama
  Confidence: 92.1%
  Domain Markers: theatrical language, elizabethan context
  Cultural Context: 16th-17th century English drama
  Reality Layer: metaphorical

✍️ Style (Σ)
  Name: poetic/elevated
  Confidence: 89.3%
  Linguistic Features: iambic pentameter, formal diction
  Rhetorical Devices: antithesis, metaphor, soliloquy
  Tone: contemplative, serious, melancholic

💎 Essence (E)
  Core Meaning: Contemplation of existence versus non-existence
  Meaning Density: 85.7%
  Invariant Elements: choice, mortality, suffering, action
  Coherence Score: 91.2%
  Entropy Measure: 0.34

⚛️ Quantum State (Optional)
  Dimension: 8
  Purity: 0.73
  Entropy: 1.42
  Entanglement: 0.56
```

#### `humanizer transform <narrative> [OPTIONS]`
**Purpose**: Transform narrative using LPE
**API Endpoint**: `POST /transform`

```bash
# Basic transformation
humanizer transform "Hello world" \
    --persona academic --namespace scientific --style formal
```

---

### 3. Gutenberg Integration Commands

#### `humanizer gutenberg search [OPTIONS]`
**Purpose**: Search Project Gutenberg catalog
**API Endpoint**: `GET /gutenberg/search`

**Options**:
- `--query <text>` - Full-text search
- `--author <name>` - Search by author
- `--subject <category>` - Search by subject
- `--language <code>` - Language filter (default: en)
- `--limit <number>` - Maximum results (default: 10)

```bash
# Search by author
humanizer gutenberg search --author "shakespeare" --limit 5

# Search by subject
humanizer gutenberg search --subject "fiction" --limit 20

# Full-text search
humanizer gutenberg search --query "pride and prejudice"

# Combined search
humanizer gutenberg search --author "dickens" --subject "fiction" --limit 15
```

**Example Output**:
```
📚 Gutenberg Search Results
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Found 5 books matching: author="shakespeare"

ID     Title                           Author              Downloads
────────────────────────────────────────────────────────────────────
1513   Romeo and Juliet               William Shakespeare  45,234
1524   Hamlet                         William Shakespeare  52,891
1533   Macbeth                        William Shakespeare  38,156
1540   Othello                        William Shakespeare  29,834
1531   King Lear                      William Shakespeare  31,445
```

#### `humanizer gutenberg browse [OPTIONS]`
**Purpose**: Browse full Gutenberg catalog
**API Endpoint**: `GET /gutenberg/catalog/browse`

**Options**:
- `--offset <number>` - Starting position (default: 0)
- `--limit <number>` - Number of results (default: 50)
- `--sort <downloads|title|author>` - Sort criteria (default: downloads)
- `--language <code>` - Language filter (default: en)

```bash
# Browse popular books
humanizer gutenberg browse --sort downloads --limit 25

# Browse starting from position 100
humanizer gutenberg browse --offset 100 --limit 50
```

#### `humanizer gutenberg popular [OPTIONS]`
**Purpose**: Show most popular books
**API Endpoint**: `GET /gutenberg/catalog/popular`

```bash
humanizer gutenberg popular --limit 25
```

#### `humanizer gutenberg recent [OPTIONS]`
**Purpose**: Show recently added books
**API Endpoint**: `GET /gutenberg/catalog/recent`

```bash
humanizer gutenberg recent --limit 15
```

#### `humanizer gutenberg info`
**Purpose**: Show catalog information and statistics
**API Endpoint**: `GET /gutenberg/catalog/info`

```bash
humanizer gutenberg info
```

#### `humanizer gutenberg refresh`
**Purpose**: Force refresh of catalog cache
**API Endpoint**: `POST /gutenberg/catalog/refresh`

```bash
humanizer gutenberg refresh
```

#### `humanizer gutenberg analyze <book_ids> [OPTIONS]`
**Purpose**: Start analysis job for Gutenberg books
**API Endpoint**: `POST /gutenberg/analyze`

**Options**:
- `--type <sample|targeted|full>` - Analysis type (default: sample)

```bash
# Analyze specific books
humanizer gutenberg analyze 1342 74 2701 --type sample

# Full analysis of single book
humanizer gutenberg analyze 1513 --type full
```

#### `humanizer gutenberg jobs [OPTIONS]`
**Purpose**: Manage analysis jobs
**API Endpoints**: `GET /gutenberg/jobs`, `GET /gutenberg/jobs/{id}`, `DELETE /gutenberg/jobs/{id}`

**Options**:
- `--status` - Show all jobs with status
- `--job-id <id>` - Get specific job details
- `--results <id>` - Get job results
- `--cancel <id>` - Cancel running job

```bash
# List all jobs
humanizer gutenberg jobs --status

# Get specific job details
humanizer gutenberg jobs --job-id abc123def456

# Get job results
humanizer gutenberg jobs --results abc123def456

# Cancel a job
humanizer gutenberg jobs --cancel abc123def456
```

---

### 4. Attribute Management Commands

#### `humanizer attributes list [OPTIONS]`
**Purpose**: List saved attributes with filtering
**API Endpoint**: `GET /api/attributes/list`

**Options**:
- `--type <persona|namespace|style|essence>` - Filter by attribute type
- `--tags <tag1,tag2>` - Filter by tags (comma-separated)
- `--limit <number>` - Maximum results (default: 50)

```bash
# List all attributes
humanizer attributes list

# Filter by type
humanizer attributes list --type persona

# Filter by tags
humanizer attributes list --tags "classical,literature"

# Combined filtering
humanizer attributes list --type style --tags "poetry" --limit 25
```

**Example Output**:
```
💾 Saved Attributes (15 shown, 47 total)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ID        Name                Type       Confidence  Algorithm           Created
─────────────────────────────────────────────────────────────────────────────────
abc123... hamlet_persona      persona    87.5%      QNT_Persona_Ext... 01/15 14:32
def456... scientific_style    style      92.1%      QNT_Style_Extra... 01/15 13:45
ghi789... fantasy_namespace   namespace  89.3%      QNT_Namespace_E... 01/15 12:18
jkl012... love_letter_ess...  essence    85.7%      QNT_Essence_Ext... 01/15 11:55

💡 Showing first 50 attributes. Use --limit to see more.
```

#### `humanizer attributes show <attribute_id>`
**Purpose**: Show detailed attribute information
**API Endpoint**: `GET /api/attributes/{id}`

```bash
humanizer attributes show abc123def456
```

**Example Output**:
```
🔍 Attribute Details: hamlet_persona
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ID: abc123def456-7890-1234-5678-90abcdef1234
Type: persona
Value: philosophical contemplator
Confidence: 87.5%
Created: 2024-01-15T14:32:15.123Z
Tags: classical, shakespeare, philosophy

Algorithm Information:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Name: QNT_Persona_Extractor
Version: 2.0.0
LLM Provider: OllamaProvider

Processing Steps:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  1. Text preprocessing and normalization
  2. LLM prompt construction with template
  3. LLM inference with specified parameters
  4. Response parsing and validation
  5. Confidence scoring and thresholding
  6. Fallback handling if confidence too low

Algorithm Parameters:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  max_tokens: 300
  temperature: 0.3
  confidence_threshold: 0.6
```

#### `humanizer attributes delete <attribute_id> [OPTIONS]`
**Purpose**: Delete a saved attribute
**API Endpoint**: `DELETE /api/attributes/{id}`

**Options**:
- `--yes` - Skip confirmation prompt

```bash
# Delete with confirmation
humanizer attributes delete abc123def456

# Force delete without confirmation
humanizer attributes delete abc123def456 --yes
```

#### `humanizer attributes stats`
**Purpose**: Show attribute statistics
**API Endpoint**: `GET /api/attributes/stats`

```bash
humanizer attributes stats
```

**Example Output**:
```
📊 Attribute Statistics
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Attributes: 47
Storage Path: ./data/saved_attributes

By Type:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  persona: 12
  namespace: 15
  style: 11
  essence: 9

By Confidence Level:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  high: 32
  medium: 13
  low: 2

By Algorithm:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  QNT_Persona_Extractor: 12
  QNT_Namespace_Extractor: 15
  QNT_Style_Extractor: 11
  QNT_Essence_Extractor: 9
```

#### `humanizer attributes algorithm <algorithm_name>`
**Purpose**: Show algorithm details for transparency
**API Endpoint**: `GET /api/attributes/algorithms/{name}`

**Supported Algorithms**:
- `persona` - Persona extraction algorithm
- `namespace` - Namespace extraction algorithm  
- `style` - Style extraction algorithm
- `essence` - Essence extraction algorithm

```bash
# View persona algorithm details
humanizer attributes algorithm persona

# View style algorithm details
humanizer attributes algorithm style
```

---

### 5. Testing & Development Commands

#### `humanizer test [OPTIONS]`
**Purpose**: Run QNT test suite
**API Endpoint**: Uses multiple endpoints based on test cases

**Options**:
- `--category <name>` - Test specific category (classical, modern_literary, etc.)

```bash
# Run all tests
humanizer test

# Test specific category
humanizer test --category classical
humanizer test --category experimental
```

**Available Test Categories**:
- `classical` - Shakespeare, Dickens
- `modern_literary` - Hemingway, stream of consciousness
- `genre_fiction` - Sci-fi, fantasy
- `contemporary` - Social media, corporate
- `technical` - Academic, manuals
- `emotional` - Memoirs, love letters
- `cultural` - Indigenous wisdom, war correspondence
- `experimental` - Surreal, avant-garde
- `children` - Children's literature
- `philosophical` - Consciousness meditation

---

### 6. Batch Processing Commands

#### `humanizer batch monitor <job_id> [OPTIONS]`
**Purpose**: Monitor job progress with live updates
**API Endpoint**: `GET /gutenberg/jobs/{id}` (polled)

**Options**:
- `--refresh <seconds>` - Refresh interval (default: 5)

```bash
# Monitor job with default refresh
humanizer batch monitor abc123def456

# Monitor with custom refresh interval
humanizer batch monitor abc123def456 --refresh 3
```

**Example Output**:
```
📊 Live Job Monitor - abc123def456
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Status: running
Progress: 45.2%
Books: 5
Type: sample

🔄 Refreshing every 5 seconds... (Press Ctrl+C to stop)
```

---

## 🔧 Administrator Guide

### System Administration

#### Health Monitoring
```bash
# Continuous health monitoring
while true; do
    echo "$(date): $(humanizer health --format summary)"
    sleep 30
done
```

#### Provider Management
```bash
# Check all provider configurations
humanizer providers

# Test specific provider connectivity
humanizer --verbose providers
```

#### Performance Monitoring
```bash
# Monitor API response times
time humanizer health

# Monitor analysis performance
time humanizer analyze "test narrative" --format summary
```

### Bulk Operations

#### Batch Analysis Setup
```bash
# Create analysis jobs for multiple books
book_ids=(1342 74 2701 1513 5200)
for id in "${book_ids[@]}"; do
    humanizer gutenberg analyze $id --type sample
done

# Monitor all jobs
humanizer gutenberg jobs --status
```

#### Data Export/Import
```bash
# Export all attributes
humanizer attributes list --limit 1000 --format json > attributes_backup.json

# Export analysis results
for job_id in $(humanizer gutenberg jobs --format ids); do
    humanizer gutenberg jobs --results $job_id > "results_${job_id}.json"
done
```

### Configuration Management

#### Environment Setup
```bash
# Set custom API endpoint
export HUMANIZER_API_URL=http://production-server:8100

# Verify connection
humanizer --api-url $HUMANIZER_API_URL health
```

#### Maintenance Tasks
```bash
# Refresh catalog cache
humanizer gutenberg refresh

# Clean up old jobs (admin script needed)
# humanizer admin cleanup --older-than 30d

# Backup attribute data
cp -r ./data/saved_attributes ./backups/attributes_$(date +%Y%m%d)
```

---

## 🗺️ API Endpoint Mappings

### Complete CLI Command → API Endpoint Mapping

| CLI Command | HTTP Method | API Endpoint | Purpose |
|-------------|-------------|--------------|---------|
| `humanizer health` | GET | `/health` | System health check |
| `humanizer providers` | GET | `/providers` | LLM provider status |
| `humanizer analyze` | POST | `/api/narrative-theory/analyze` | QNT analysis |
| `humanizer transform` | POST | `/transform` | LPE transformation |
| `humanizer gutenberg search` | GET | `/gutenberg/search` | Search books |
| `humanizer gutenberg browse` | GET | `/gutenberg/catalog/browse` | Browse catalog |
| `humanizer gutenberg popular` | GET | `/gutenberg/catalog/popular` | Popular books |
| `humanizer gutenberg recent` | GET | `/gutenberg/catalog/recent` | Recent books |
| `humanizer gutenberg info` | GET | `/gutenberg/catalog/info` | Catalog info |
| `humanizer gutenberg refresh` | POST | `/gutenberg/catalog/refresh` | Refresh cache |
| `humanizer gutenberg analyze` | POST | `/gutenberg/analyze` | Start analysis job |
| `humanizer gutenberg jobs` (list) | GET | `/gutenberg/jobs` | List jobs |
| `humanizer gutenberg jobs` (details) | GET | `/gutenberg/jobs/{id}` | Job details |
| `humanizer gutenberg jobs` (results) | GET | `/gutenberg/jobs/{id}/results` | Job results |
| `humanizer gutenberg jobs` (cancel) | DELETE | `/gutenberg/jobs/{id}` | Cancel job |
| `humanizer attributes list` | GET | `/api/attributes/list` | List attributes |
| `humanizer attributes show` | GET | `/api/attributes/{id}` | Attribute details |
| `humanizer attributes delete` | DELETE | `/api/attributes/{id}` | Delete attribute |
| `humanizer attributes stats` | GET | `/api/attributes/stats` | Attribute statistics |
| `humanizer attributes algorithm` | GET | `/api/attributes/algorithms/{name}` | Algorithm details |
| `humanizer batch monitor` | GET | `/gutenberg/jobs/{id}` | Monitor job (polled) |

### Request/Response Patterns

#### Health Check
```bash
# CLI Command
humanizer health

# API Request
GET /health

# Response
{
  "status": "healthy",
  "version": "2.0.0",
  "llm_provider": "OllamaProvider",
  "response_time_ms": 12
}
```

#### Narrative Analysis
```bash
# CLI Command
humanizer analyze "To be or not to be" --depth deep --quantum

# API Request
POST /api/narrative-theory/analyze
{
  "narrative": "To be or not to be",
  "semantic_depth": "deep",
  "include_quantum_state": true,
  "include_essence_vectors": false
}

# Response
{
  "narrative_id": "abc123...",
  "original_narrative": "To be or not to be",
  "persona": { "name": "philosophical contemplator", "confidence": 0.875 },
  "namespace": { "name": "renaissance drama", "confidence": 0.921 },
  "style": { "name": "poetic/elevated", "confidence": 0.893 },
  "essence": { "core_meaning": "...", "meaning_density": 0.857 },
  "quantum_state": { "dimension": 8, "purity": 0.73 }
}
```

#### Gutenberg Search
```bash
# CLI Command
humanizer gutenberg search --author "shakespeare" --limit 5

# API Request
GET /gutenberg/search?author=shakespeare&limit=5

# Response
{
  "books": [
    {
      "gutenberg_id": 1513,
      "title": "Romeo and Juliet",
      "author": "William Shakespeare",
      "subjects": ["Drama", "Tragedy"],
      "download_url": "https://www.gutenberg.org/ebooks/1513.txt.utf-8"
    }
  ],
  "total_found": 37,
  "query_info": {
    "author": "shakespeare",
    "limit": 5
  }
}
```

---

## ⚙️ Configuration Management

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HUMANIZER_API_URL` | `http://localhost:8100` | Default API endpoint |
| `HUMANIZER_TIMEOUT` | `30` | Request timeout in seconds |
| `HUMANIZER_VERBOSE` | `false` | Enable verbose output |

### Configuration Files

#### User Configuration (~/.humanizer/config.json)
```json
{
  "api_url": "http://localhost:8100",
  "default_format": "table",
  "auto_refresh": true,
  "preferred_providers": ["ollama", "openai"],
  "analysis_defaults": {
    "depth": "standard",
    "include_quantum": false,
    "include_vectors": false
  }
}
```

#### System Configuration (/etc/humanizer/config.json)
```json
{
  "production_api_url": "https://api.humanizer.internal:8100",
  "rate_limits": {
    "requests_per_minute": 60,
    "analysis_per_hour": 100
  },
  "logging": {
    "level": "INFO",
    "file": "/var/log/humanizer-cli.log"
  }
}
```

---

## 🔍 Troubleshooting

### Common Issues and Solutions

#### 1. Connection Issues
```bash
# Problem: "Connection refused" error
humanizer health
# Error: Failed to connect to API at http://localhost:8100

# Solutions:
# Check if API server is running
curl http://localhost:8100/health

# Try with custom URL
humanizer --api-url http://127.0.0.1:8100 health

# Check network connectivity
ping localhost
```

#### 2. Authentication Issues
```bash
# Problem: "Unauthorized" error for certain commands
humanizer analyze "test"
# Error: 401 Unauthorized

# Solutions:
# Check provider status
humanizer providers

# Verify API keys are configured
# (Check API server configuration)
```

#### 3. Command Not Found
```bash
# Problem: "command not found" error
humanizer --help
# Error: command not found: humanizer

# Solutions:
# Reinstall CLI
cd unified-platform
./install_cli.sh

# Check PATH
echo $PATH | grep -q "/usr/local/bin" && echo "PATH OK" || echo "PATH issue"

# Manual check
ls -la /usr/local/bin/humanizer
```

#### 4. Slow Response Times
```bash
# Problem: Commands taking too long
time humanizer analyze "test text"
# Takes more than 30 seconds

# Diagnostics:
# Check API health
humanizer health

# Test with simpler commands
humanizer config

# Use verbose mode
humanizer --verbose analyze "test text"
```

#### 5. Output Formatting Issues
```bash
# Problem: Garbled or incorrect output formatting

# Solutions:
# Try different output formats
humanizer analyze "test" --format json
humanizer analyze "test" --format summary

# Check terminal encoding
echo $LANG

# Update terminal if needed
```

### Debug Mode Usage

#### Enable Verbose Output
```bash
# Global verbose flag
humanizer --verbose <any_command>

# Examples:
humanizer --verbose health
humanizer --verbose analyze "debug text"
humanizer --verbose gutenberg search --author "test"
```

#### API Request Debugging
```bash
# Monitor actual HTTP requests (requires additional tools)
# Install httpie or curl monitoring

# Using curl to test endpoints directly
curl -v http://localhost:8100/health
curl -v -X POST http://localhost:8100/api/narrative-theory/analyze \
  -H "Content-Type: application/json" \
  -d '{"narrative": "test", "semantic_depth": "standard"}'
```

### Log Analysis

#### CLI Logs
```bash
# Check system logs (if configured)
tail -f /var/log/humanizer-cli.log

# Check API server logs
tail -f humanizer_api/lighthouse/logs/api.log
```

#### Performance Monitoring
```bash
# Time all operations
time humanizer health
time humanizer analyze "performance test"
time humanizer gutenberg search --query "test"

# Monitor resource usage
top -p $(pgrep -f humanizer)
```

---

## 🚀 Advanced Usage

### Scripting and Automation

#### Batch Analysis Script
```bash
#!/bin/bash
# batch_analyze.sh - Analyze multiple texts

texts=(
    "To be or not to be, that is the question"
    "It was the best of times, it was the worst of times"
    "Call me Ishmael"
    "In the beginning was the Word"
)

for text in "${texts[@]}"; do
    echo "Analyzing: $text"
    humanizer analyze "$text" --format summary
    echo "---"
done
```

#### Gutenberg Bulk Download
```bash
#!/bin/bash
# bulk_gutenberg.sh - Analyze popular books

# Get popular book IDs
book_ids=$(humanizer gutenberg popular --limit 10 --format json | \
           jq -r '.books[].gutenberg_id')

# Start analysis jobs
for id in $book_ids; do
    echo "Starting analysis for book $id"
    humanizer gutenberg analyze $id --type sample
done

# Monitor all jobs
echo "Monitoring jobs..."
humanizer gutenberg jobs --status
```

#### Attribute Management Pipeline
```bash
#!/bin/bash
# attribute_pipeline.sh - Process and save attributes

# Analyze and save attributes for classic texts
classics=(
    "shakespeare:To be or not to be, that is the question"
    "dickens:It was the best of times, it was the worst of times"
    "melville:Call me Ishmael"
)

for classic in "${classics[@]}"; do
    author="${classic%%:*}"
    text="${classic#*:}"
    
    echo "Processing $author: $text"
    
    # Analyze text
    analysis_id=$(humanizer analyze "$text" --format json | jq -r '.narrative_id')
    
    # Save attributes with tags
    humanizer attributes save "$analysis_id" "${author}_classic" \
        --types persona,namespace,style,essence \
        --tags "classical,literature,$author"
done

# Show statistics
humanizer attributes stats
```

### Integration with Other Tools

#### JSON Processing with jq
```bash
# Extract specific data from analysis
humanizer analyze "sample text" --format json | \
    jq '.persona.name, .confidence'

# Filter attributes by confidence
humanizer attributes list --format json | \
    jq '.attributes[] | select(.confidence_score > 0.8)'

# Export high-confidence personas
humanizer attributes list --type persona --format json | \
    jq '.attributes[] | select(.confidence_score > 0.85) | .name'
```

#### CSV Export for Analysis
```bash
# Export attributes to CSV
{
    echo "ID,Name,Type,Confidence,Created"
    humanizer attributes list --format json | \
        jq -r '.attributes[] | [.attribute_id, .name, .attribute_type, .confidence_score, .created_at] | @csv'
} > attributes_export.csv
```

#### Monitoring and Alerting
```bash
#!/bin/bash
# monitor_health.sh - Health monitoring with alerts

check_health() {
    if ! humanizer health >/dev/null 2>&1; then
        echo "ALERT: Humanizer API is down!" | mail -s "API Alert" admin@example.com
        return 1
    fi
    return 0
}

# Run every 5 minutes
while true; do
    check_health
    sleep 300
done
```

### Performance Optimization

#### Batch Processing Optimization
```bash
# Process multiple analyses in parallel
texts=("text1" "text2" "text3" "text4")

# Sequential (slower)
for text in "${texts[@]}"; do
    humanizer analyze "$text" --format summary
done

# Parallel (faster)
for text in "${texts[@]}"; do
    humanizer analyze "$text" --format summary &
done
wait
```

#### Caching Strategies
```bash
# Cache frequently accessed data
mkdir -p ~/.humanizer/cache

# Cache popular books list
if [ ! -f ~/.humanizer/cache/popular_books.json ]; then
    humanizer gutenberg popular --limit 100 --format json > \
        ~/.humanizer/cache/popular_books.json
fi

# Use cached data
jq '.books[].title' ~/.humanizer/cache/popular_books.json
```

---

## 📚 Reference

### Exit Codes

| Code | Meaning | Example |
|------|---------|---------|
| 0 | Success | Command completed successfully |
| 1 | General error | Invalid arguments or API error |
| 2 | Connection error | Cannot connect to API |
| 3 | Authentication error | Invalid credentials or unauthorized |
| 4 | Not found | Resource not found (job, attribute, etc.) |
| 5 | Timeout | Request timed out |

### Output Formats

#### Table Format (Default)
- Human-readable formatted tables
- Rich text with colors and unicode symbols
- Best for interactive use

#### JSON Format
- Machine-readable structured data
- Complete API response data
- Best for scripting and integration

#### Summary Format
- Concise text output
- Key information only
- Best for quick checks and monitoring

### Version Information

```bash
# Check CLI version
humanizer --version

# Check API version
humanizer health | grep -i version

# Check compatibility
humanizer config
```

---

**📖 End of Documentation**

This comprehensive guide covers all aspects of using the Humanizer CLI tool. For additional support, API documentation, or to report issues, please refer to the main project documentation or contact the development team.

*Last updated: January 2024*