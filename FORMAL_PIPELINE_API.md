# Formal Content Pipeline API System

## 🎯 Overview

The Formal Content Pipeline API provides a comprehensive, API-driven approach to content transformation and routing. Unlike the previous script-based approach, this system offers:

- **RESTful API interface** for all pipeline operations
- **Formal rule management** with persistent storage
- **Real-time execution monitoring** with progress tracking
- **Background processing** with status updates
- **Comprehensive statistics** and performance metrics
- **Professional CLI interface** built on API calls

## 🏗️ Architecture

### API-First Design
```
┌─────────────────────┐    HTTP API    ┌──────────────────────┐
│  Pipeline Manager   │ ←─────────────→ │   Pipeline API       │
│  CLI (Formal)       │                │   (Port 7204)        │
└─────────────────────┘                └──────────────────────┘
           │                                      │
           │                                      ├─ Rule Management
           └─ API Calls                           ├─ Execution Engine
                                                  ├─ Progress Monitoring
                                                  └─ Statistics & Reports
```

### Components

#### 1. Pipeline API Server (`pipeline_api.py`)
- **FastAPI-based REST API** on port 7204
- **Persistent rule storage** in PostgreSQL
- **Background task execution** with async processing
- **Real-time progress monitoring**
- **Comprehensive error handling**

#### 2. Pipeline Manager CLI (`pipeline_manager.py`)
- **Professional CLI interface** built on API calls
- **Interactive rule creation** with guided prompts
- **Real-time execution monitoring**
- **Comprehensive statistics display**
- **Dry-run capabilities** for safe testing

#### 3. Integration with HAW CLI
- **Seamless integration** with existing haw commands
- **API service management** (start/stop/restart)
- **Status monitoring** and health checks

## 🚀 Getting Started

### 1. Start the Pipeline API
```bash
# Start the API server
haw api start pipeline-api

# Verify it's running
curl http://127.0.0.1:7204/health
```

### 2. Create Your First Pipeline Rule
```bash
# Interactive rule creation
haw pipeline-mgr rules create "High Quality Book Content" \
  --min-quality 0.8 \
  --min-words 1000 \
  --description "Route exceptional content to book chapters"

# List all rules
haw pipeline-mgr rules list
```

### 3. Execute a Pipeline
```bash
# Dry run to preview what will be processed
haw pipeline-mgr execute --min-quality 0.8 --limit 5 --dry-run

# Execute with monitoring
haw pipeline-mgr execute --min-quality 0.8 --limit 5 --name "Test Run"

# Check execution status
haw pipeline-mgr executions list
```

## 📋 Rule Management

### Rule Structure
Pipeline rules define:
- **Conditions**: What content to process (quality, category, word count, etc.)
- **Transformations**: How to improve the content
- **Destinations**: Where to route the transformed content
- **Priority**: Rule execution order

### Creating Rules

#### Via CLI (Interactive)
```bash
haw pipeline-mgr rules create "Rule Name"
```
This launches an interactive prompt to select:
- Transformations (quality enhancement, structural improvement, etc.)
- Destinations (book chapters, blog posts, social media, etc.)
- Priority level (1-100)

#### Via API (Programmatic)
```bash
curl -X POST http://127.0.0.1:7204/rules \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Philosophical Content to Academic Papers",
    "description": "Route philosophical discussions to academic format",
    "conditions": {
      "category": "philosophical",
      "min_quality": 0.7,
      "min_words": 1000
    },
    "transformations": ["structural_improvement", "format_conversion"],
    "destinations": ["academic_paper", "discourse_post"],
    "priority": 80
  }'
```

### Rule Examples

#### High-Quality Content → Book Chapters
```yaml
name: "Exceptional Content to Books"
conditions:
  min_quality: 0.9
  min_words: 800
transformations:
  - quality_enhancement
  - structural_improvement
destinations:
  - book_chapter
priority: 100
```

#### Technical Content → Blog Posts
```yaml
name: "Technical Discussions to Blogs"
conditions:
  category: "technical"
  min_quality: 0.6
  min_words: 400
transformations:
  - quality_enhancement
  - audience_adaptation
destinations:
  - blog_post
  - discourse_post
priority: 70
```

#### Short Content → Social Media
```yaml
name: "Concise Insights to Social"
conditions:
  max_words: 300
  min_quality: 0.6
transformations:
  - length_optimization
  - format_conversion
destinations:
  - social_media
priority: 40
```

## 🔄 Pipeline Execution

### Execution Methods

#### 1. Auto-Selection Based on Filters
```bash
# Process content matching quality threshold
haw pipeline-mgr execute --min-quality 0.8 --limit 10

# Process by category
haw pipeline-mgr execute --category philosophical --min-quality 0.7

# Process by word count range
haw pipeline-mgr execute --min-words 1000 --max-words 3000
```

#### 2. Specific Conversation IDs
```bash
# Process specific conversations
haw pipeline-mgr execute --conversation-ids 12345 67890 13579
```

#### 3. Dry Run (Preview Mode)
```bash
# See what would be processed without executing
haw pipeline-mgr execute --min-quality 0.8 --dry-run
```

### Execution Monitoring

#### Real-Time Progress
The CLI automatically monitors execution progress:
```
📊 Monitoring execution: exec_a1b2c3d4
   Status: running - 7/10 completed, 0 failed
   Status: running - 8/10 completed, 0 failed
   Status: running - 10/10 completed, 0 failed
✅ Execution completed!
   Total processed: 10
   Successful: 9
   Failed: 1
```

#### Background Execution
All pipeline executions run in the background, allowing:
- **Non-blocking operations** - CLI returns immediately
- **Progress monitoring** - Check status anytime
- **Concurrent executions** - Multiple pipelines can run simultaneously

## 📊 Statistics & Monitoring

### System Statistics
```bash
haw pipeline-mgr stats
```

Shows:
- **Active rules count**
- **Current running executions**
- **Execution stats** (7-day window)
- **Destination breakdown** (where content is being routed)

### Execution History
```bash
# List recent executions
haw pipeline-mgr executions list

# Filter by status
haw pipeline-mgr executions list --status completed

# Show more results
haw pipeline-mgr executions list --limit 25
```

### API Health Monitoring
```bash
# Check API status through haw
haw status

# Direct API health check
curl http://127.0.0.1:7204/health
```

## 🌐 API Endpoints

### Rule Management
- `GET /rules` - List all pipeline rules
- `POST /rules` - Create new pipeline rule
- `GET /rules/{rule_id}` - Get specific rule
- `PUT /rules/{rule_id}` - Update rule
- `DELETE /rules/{rule_id}` - Delete rule

### Pipeline Execution
- `POST /execute` - Execute pipeline with parameters
- `GET /executions` - List executions
- `GET /executions/{execution_id}` - Get execution details
- `POST /executions/{execution_id}/cancel` - Cancel execution

### System Information
- `GET /health` - API health check
- `GET /stats` - System statistics

### API Documentation
Once the API is running, visit: http://127.0.0.1:7204/docs

## 🔧 Configuration

### Database Setup
The API automatically creates required database tables:
- `pipeline_rules` - Stores rule definitions
- `pipeline_executions` - Stores execution records
- `content_pipeline_records` - Stores processing results

### Environment Variables
```bash
# Database connection (optional, defaults to standard)
DATABASE_URL=postgresql://user:password@localhost/humanizer_archive

# API configuration (optional)
PIPELINE_API_HOST=127.0.0.1
PIPELINE_API_PORT=7204
```

## 🚦 Transformation Types

### Available Transformations
1. **quality_enhancement** - LLM-powered content improvement
2. **structural_improvement** - Better organization and flow
3. **tone_adjustment** - Adapt tone for target audience
4. **length_optimization** - Adjust length for platform requirements
5. **audience_adaptation** - Simplify or enhance for readers
6. **format_conversion** - Convert to destination-specific formats

### Destination Types
1. **humanizer_thread** - Platform-native format
2. **book_chapter** - Structured for book compilation
3. **discourse_post** - Community discussion format
4. **blog_post** - SEO-optimized web articles
5. **social_media** - Character-limited, engaging posts
6. **academic_paper** - Formal scholarly format
7. **newsletter** - Structured with sections and CTAs

## 🎯 Best Practices

### Rule Design
1. **Use specific conditions** - Avoid overly broad rules
2. **Set appropriate priorities** - Higher quality content gets higher priority
3. **Test with dry runs** - Always preview before executing
4. **Monitor execution results** - Check success rates and adjust rules

### Performance
1. **Reasonable batch sizes** - Start with 10-20 conversations
2. **Quality thresholds** - Focus on worthwhile content (>0.6 quality)
3. **Monitor system resources** - Check API health regularly
4. **Background processing** - Let executions complete naturally

### Maintenance
1. **Regular rule review** - Update rules based on results
2. **Execution cleanup** - Monitor and cancel stuck executions
3. **Statistics analysis** - Use stats to optimize pipeline performance
4. **API health monitoring** - Ensure service availability

## 🔄 Integration Workflows

### Daily Content Processing
```bash
# Morning routine: Start API and check system
haw api start pipeline-api
haw pipeline-mgr stats

# Process high-quality content
haw pipeline-mgr execute --min-quality 0.8 --limit 20

# Check results
haw pipeline-mgr executions list --limit 5
```

### Content Quality Enhancement
```bash
# Create enhancement rule
haw pipeline-mgr rules create "Quality Enhancement" \
  --min-quality 0.4 --max-quality 0.7

# Execute enhancement pipeline
haw pipeline-mgr execute --min-quality 0.4 --max-quality 0.7
```

### Multi-Format Publishing
```bash
# Create multi-destination rule for high-quality content
# (This requires API call or interactive creation)

# Execute for blog and book publishing
haw pipeline-mgr execute --min-quality 0.8 --category technical
```

## 🎉 Advantages Over Script-Based Approach

### Professional API Interface
- **RESTful endpoints** for all operations
- **Standardized responses** with proper error handling
- **API documentation** with interactive testing
- **Programmatic integration** capabilities

### Persistent State Management
- **Database-backed rules** that persist across restarts
- **Execution history** with detailed tracking
- **Progress monitoring** for long-running operations
- **Reliable error recovery**

### Background Processing
- **Non-blocking execution** - CLI returns immediately
- **Concurrent processing** - Multiple pipelines can run
- **Progress tracking** - Monitor status in real-time
- **Graceful cancellation** - Stop executions cleanly

### Formal Rule System
- **Priority-based execution** - Control rule application order
- **Condition-based routing** - Precise content targeting
- **Transformation chains** - Apply multiple improvements
- **Destination flexibility** - Route to multiple outputs

### Monitoring & Analytics
- **System statistics** - Track performance metrics
- **Execution analytics** - Success rates and timing
- **Destination tracking** - See where content goes
- **Health monitoring** - Ensure system reliability

**This formal pipeline system transforms content processing from ad-hoc scripts into a professional, scalable, and reliable content transformation engine!**