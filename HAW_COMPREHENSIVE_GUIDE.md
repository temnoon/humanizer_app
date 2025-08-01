# HAW - Comprehensive Humanizer Archive Wrapper

## 🎯 Overview

**HAW** (Humanizer Archive Wrapper) is a comprehensive command-line interface that integrates all humanizer functionality into a single, powerful, and flexible CLI tool. It provides unified access to:

- **Analysis Scripts** - Personal writing extraction, content assessment, embedding generation
- **API Services** - Archive, LPE, Lawyer, and Lighthouse APIs with service management
- **CLI Tools** - Archive browser, embedding management, allegory engine, and more
- **Pipeline Management** - Predefined workflows for complex multi-step operations
- **System Monitoring** - Health checks, process monitoring, and log management

## 🚀 Installation

HAW is already installed and ready to use:

```bash
# Verify installation
which haw

# Show all available commands
haw help
```

## 📋 Command Categories

### 📊 System Management

Monitor and manage your humanizer environment:

```bash
# Complete system health check
haw status

# Show active humanizer processes with resource usage
haw processes

# View recent log activity across all services
haw logs

# Setup/repair Python environment
haw setup
```

### 📝 Writing Analysis

Extract and analyze your personal writing style:

```bash
# Extract your authentic writing samples
haw extract-writing extract --limit 1000

# Custom filtering options
haw extract-writing extract --limit 500 --min-length 50 --max-length 1500

# Results saved to: personal_writing_analysis/
# - writing_samples_*.json (detailed samples)
# - style_profile_*.json (comprehensive profile)
# - style_report_*.md (human-readable summary)
```

### 🧠 Embedding & Search

Hierarchical semantic embedding system:

```bash
# Test embedding with small batches
haw embed embed --limit 50 --timeout 60

# Full archive embedding (comprehensive)
haw embed-full --batch-size 50 --timeout 120 --min-score 0.3

# Monitor embedding progress
haw monitor dashboard
haw monitor status
haw monitor stats
```

### 📊 Content Analysis

Comprehensive archive analysis tools:

```bash
# Quality assessment of conversations
haw assess --limit 1000

# Extract representative conversation samples
haw sample --limit 100

# Generate word clouds (removes duplicates and stop words)
haw wordcloud --conversations 1000

# Categorize content using local LLM
haw categorize --limit 500
```

### 📁 Archive Management

Direct access to specialized CLI tools:

```bash
# Archive browser and search
haw archive list
haw archive search "consciousness"
haw archive get 12345
haw archive stats

# Embedding corpus management
haw embedding-cli stats
haw embedding-cli search "narrative theory"

# Allegory transformation engine
haw allegory transform --text "sample text"

# Main humanizer interface
haw humanizer

# Integrated processing workflows
haw integrated

# Attribute analysis browser
haw attribute browse
```

### 🌐 API Service Management

Complete API lifecycle management:

```bash
# List available services
haw api list

# Start services
haw api start lighthouse-api
haw api start archive-api
haw api start lpe-api
haw api start lawyer-api

# Stop services
haw api stop lighthouse-api

# Restart services
haw api restart archive-api

# Available services:
# - lighthouse-api: Enhanced Lighthouse API (port 8100)
# - archive-api: Archive management API (port 7200)
# - lpe-api: Lamish Projection Engine API (port 7201)
# - lawyer-api: Content quality assessment API (port 7202)
# - simple-archive: Simple archive API (minimal dependencies)
```

### 🔄 Pipeline Management

Predefined workflows for complex operations:

```bash
# List available pipelines
haw pipeline list

# Pipeline status
haw pipeline status

# Run complete pipelines:

# 1. Full Analysis Pipeline
haw pipeline run full-analysis
# Runs: assess → categorize → wordcloud → embed-full

# 2. Personal Writing Profile Pipeline
haw pipeline run writing-profile
# Comprehensive writing style analysis

# 3. Content Quality Audit Pipeline
haw pipeline run content-audit
# Runs: assess → sample → categorize

# 4. Embedding Corpus Refresh Pipeline
haw pipeline run embedding-refresh
# Complete rebuild of embedding corpus
```

## 🎯 Common Workflows

### Quick System Check
```bash
haw status
haw processes
```

### Personal Writing Analysis
```bash
# Extract your writing style
haw extract-writing extract --limit 1000

# Or use the pipeline
haw pipeline run writing-profile
```

### Content Discovery & Analysis
```bash
# Find quality conversations
haw assess --limit 500
haw sample --limit 50

# Analyze themes
haw wordcloud --conversations 1000
haw categorize --limit 500
```

### Embedding & Search Setup
```bash
# Build searchable corpus
haw embed-full --batch-size 50

# Monitor progress
haw monitor dashboard

# Search when complete
haw embedding-cli search "consciousness and narrative"
```

### API Development Workflow
```bash
# Start development APIs
haw api start lighthouse-api
haw api start archive-api

# Check health
haw status

# Stop when done
haw api stop lighthouse-api
haw api stop archive-api
```

## 🔧 Advanced Features

### Flexible Parameter Control

All commands support extensive parameter customization:

```bash
# Embedding with custom parameters
haw embed-full \
  --batch-size 25 \
  --timeout 180 \
  --min-score 0.4 \
  --min-words 300

# Writing extraction with filters
haw extract-writing extract \
  --limit 2000 \
  --min-length 100 \
  --max-length 800

# Quality assessment with thresholds
haw assess \
  --limit 1000 \
  --min-score 0.2 \
  --include-duplicates
```

### Pipeline Customization

Pipelines can be interrupted and resumed:

```bash
# Start full analysis
haw pipeline run full-analysis

# If interrupted, run individual steps:
haw assess --limit 1000
haw categorize --limit 1000
haw wordcloud --conversations 1000
haw embed-full --batch-size 50
```

### Service Integration

APIs can be controlled programmatically:

```bash
# Start all services
for service in lighthouse-api archive-api lpe-api; do
  haw api start $service
done

# Health monitoring
haw status | grep "✅"

# Automatic restart on failure
haw api restart lighthouse-api
```

## 📊 Monitoring & Debugging

### Process Monitoring
```bash
# Real-time process monitoring
haw processes

# Shows:
# - Process IDs and resource usage
# - Current parameters (--limit, --batch-size, etc.)
# - Memory and CPU consumption
```

### Log Analysis
```bash
# View recent logs
haw logs

# Searches multiple log directories:
# - humanizer_api/lighthouse/logs/
# - humanizer_api/logs/
# - scripts/logs/
```

### Health Checks
```bash
# Comprehensive system status
haw status

# Checks:
# - Python environment (correct version and path)
# - PostgreSQL (running and accessible)
# - Ollama (running with API access)
# - All API services (ports and health endpoints)
```

## 🎯 Integration with Existing Tools

HAW seamlessly integrates all existing functionality:

### Original Scripts
All your existing scripts work through HAW:
- `personal_writing_extractor.py` → `haw extract-writing`
- `hierarchical_embedder.py` → `haw embed`
- `batch_conversation_assessor.py` → `haw assess`

### CLI Tools
Direct access to specialized interfaces:
- Archive CLI → `haw archive`
- Embedding CLI → `haw embedding-cli`
- Allegory CLI → `haw allegory`

### API Services
Complete lifecycle management:
- Start/stop/restart services
- Health monitoring
- Log aggregation

## 💡 Tips & Best Practices

### Performance Optimization
```bash
# For large operations, use appropriate batch sizes
haw embed-full --batch-size 25  # Conservative
haw embed-full --batch-size 50  # Balanced
haw embed-full --batch-size 75  # Aggressive

# Monitor resources during long operations
haw processes
```

### Error Recovery
```bash
# If embedding fails, check status and resume
haw monitor status
haw embed-full --batch-size 25 --timeout 180

# If API services fail, restart them
haw api restart lighthouse-api
```

### Development Workflow
```bash
# Daily development routine
haw status                    # Check system health
haw processes                 # Monitor active work
haw logs                      # Review recent activity

# Start development session
haw api start lighthouse-api
haw archive search "topic"    # Research

# End development session
haw api stop lighthouse-api
```

## 🚀 Future Extensions

HAW is designed for easy extension:

- **Custom Pipelines**: Add new predefined workflows
- **Additional APIs**: Integrate new service endpoints
- **Advanced Monitoring**: Enhanced process and resource tracking
- **Configuration Management**: Environment-specific settings
- **Batch Job Scheduling**: Automated pipeline execution

## 📞 Support

HAW provides comprehensive help:

```bash
# General help
haw help

# Command-specific help
haw extract-writing --help
haw embed-full --help
haw api --help
haw pipeline --help
```

**HAW unifies your entire humanizer toolkit into a single, powerful, and intuitive command-line interface!**