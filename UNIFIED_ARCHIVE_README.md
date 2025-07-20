# Unified Archive System

## 🎯 Overview

The Unified Archive System consolidates **ALL** archive sources into a single PostgreSQL database with powerful search and analysis capabilities. This replaces the fragmented approach with a comprehensive solution.

## 🏗️ Architecture

```
Node Archive Conversations ───┐
Social Media Archives ────────┤
Email/Message Archives ───────┼──► PostgreSQL ──► Archive API ──► Rails/Discourse
File System Content ──────────┤    (Unified)      (Universal)     (Publishing)
Web Content Archives ─────────┘
```

## 🚀 Quick Start

### 1. Setup Database and Import Node Archive

```bash
# Setup PostgreSQL unified archive and import Node conversations
python setup_unified_archive.py \
  --database-url "postgresql://user:pass@localhost/humanizer_archive" \
  --node-archive-path "/Users/tem/nab/exploded_archive_node" \
  --max-conversations 100

# This will:
# ✅ Create PostgreSQL schema with full-text search
# ✅ Run Rails migrations for ActiveRecord models  
# ✅ Import Node Archive Browser conversations
# ✅ Start Enhanced Archive API (port 7200)
# ✅ Start Rails API (port 3000)
```

### 2. Verify Setup

```bash
# Check Archive API
curl http://localhost:7200/health

# Check Rails API  
curl http://localhost:3000/api/v1/unified_archive/statistics

# Get archive statistics
curl http://localhost:3000/api/v1/unified_archive/statistics
```

## 📊 Database Schema

### Core Table: `archived_content`

```sql
CREATE TABLE archived_content (
  id BIGSERIAL PRIMARY KEY,
  source_type VARCHAR(50),     -- 'node_conversation', 'twitter', etc.
  source_id VARCHAR(255),      -- Original message/conversation ID  
  parent_id BIGINT,            -- For threading/conversation structure
  content_type VARCHAR(50),    -- 'message', 'conversation', 'thread'
  
  -- Content
  title TEXT,
  body_text TEXT,
  raw_content JSONB,           -- Original format preserved
  
  -- Metadata  
  author VARCHAR(255),
  participants TEXT[],         -- Array of conversation participants
  timestamp TIMESTAMPTZ,
  source_metadata JSONB,
  
  -- AI Processing
  semantic_vector TEXT,        -- Embedding for similarity search
  extracted_attributes JSONB,  -- LPE-generated attributes
  content_quality_score FLOAT, -- Lamish Lawyer assessment
  processing_status VARCHAR(50) DEFAULT 'pending',
  
  -- Search & Analysis
  search_terms TEXT[],
  word_count BIGINT,
  language_detected VARCHAR(10),
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

## 🔍 Search & Query APIs

### 1. Enhanced Archive API (Python/FastAPI)

**Base URL:** `http://localhost:7200`

```bash
# Unified search across all sources
curl -X POST http://localhost:7200/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "lighthouse navigation",
    "source_types": ["node_conversation", "twitter"],
    "content_types": ["message"],
    "author": "john",
    "date_from": "2024-01-01T00:00:00Z",
    "limit": 50
  }'

# Get conversation thread
curl http://localhost:7200/conversation/12345

# Import Node Archive 
curl -X POST http://localhost:7200/import/node-archive \
  -F "node_archive_path=/path/to/node/archive" \
  -F "max_conversations=100"
```

### 2. Rails API (Ruby/ActiveRecord)

**Base URL:** `http://localhost:3000/api/v1/unified_archive`

```bash
# Search with Rails API
curl "http://localhost:3000/api/v1/unified_archive/search?query=lighthouse&author=john"

# Get statistics
curl http://localhost:3000/api/v1/unified_archive/statistics

# Get conversation thread
curl http://localhost:3000/api/v1/unified_archive/123/thread

# List all sources
curl http://localhost:3000/api/v1/unified_archive/sources

# Export data
curl "http://localhost:3000/api/v1/unified_archive/export?format=json&source_types=node_conversation"
```

## 🤖 LPE Integration

### Enhance Content with AI

```bash
# Trigger LPE enhancement for specific content
curl -X POST http://localhost:3000/api/v1/unified_archive/123/enhance

# Update processing status
curl -X PUT http://localhost:7200/content/123/processing-status \
  -H "Content-Type: application/json" \
  -d '{
    "content_id": 123,
    "status": "completed",
    "attributes": {"persona": "philosopher", "namespace": "academic"},
    "quality_score": 0.85
  }'
```

## 💾 Rails ActiveRecord Usage

### In Rails Applications

```ruby
# Search across all archives
results = ArchivedContent.search_unified("lighthouse", {
  source_types: ["node_conversation"],
  author: "john",
  date_from: 1.month.ago
})

# Get conversation threads
conversation = ArchivedContent.find(123)
messages = conversation.conversation_thread

# Statistics
stats = ArchivedContent.statistics
# => {
#   total_content: 15420,
#   by_source_type: {"node_conversation" => 8500, "twitter" => 6920},
#   conversations_count: 1200,
#   average_quality_score: 0.76
# }

# Find related content
content = ArchivedContent.find(123)
related = content.related_content

# Export to WriteBook format
writebook_sections = content.to_writebook_section
```

## 📈 Import Sources

### Supported Import Types

1. **Node Archive Browser** ✅ Ready
   ```bash
   python -m node_archive_importer /path/to/node/archive --database-url postgresql://...
   ```

2. **Social Media Archives** 🔄 Coming Soon
   - Twitter/X exports
   - Facebook exports  
   - Instagram data
   - LinkedIn exports

3. **Email Archives** 🔄 Coming Soon
   - Mailbox files (.mbox)
   - Gmail exports
   - Outlook PST files

4. **Chat Platforms** 🔄 Coming Soon
   - Slack exports
   - Discord data
   - Telegram history

## 🎯 WriteBook & Discourse Integration

### WriteBook Publishing Pipeline

```ruby
# Convert archive content to WriteBook sections
archived_content = ArchivedContent.high_quality.recent.limit(10)
writebook = Writebook.create(title: "Archive Insights")

archived_content.each do |content|
  section_data = content.to_writebook_section
  writebook.writebook_sections.create(section_data)
end
```

### Discourse Integration Flow

```
Archive Content → Quality Assessment → LPE Enhancement → WriteBook → Discourse Publication
```

## 🔧 Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost/humanizer_archive

# API Services  
ARCHIVE_API_PORT=7200
LPE_API_PORT=7201
LAWYER_API_PORT=7202

# Node Archive Path
NODE_ARCHIVE_PATH=/Users/tem/lpe_dev

# LLM Configuration
OPENAI_API_KEY=your_key
DEEPSEEK_API_KEY=your_key
OLLAMA_HOST=http://localhost:11434
```

## 📊 Monitoring & Analytics

### Key Metrics Dashboard

```bash
# Get comprehensive statistics
curl http://localhost:3000/api/v1/unified_archive/statistics

# Response includes:
# - Total content count by source
# - Processing status distribution  
# - Quality score distribution
# - Top authors
# - Content timeline
# - Source health status
```

## 🚨 Troubleshooting

### Common Issues

1. **Database Connection**: Ensure PostgreSQL is running and accessible
2. **Import Failures**: Check Node archive path and permissions
3. **API Errors**: Verify services are running on correct ports
4. **Search Issues**: Check full-text search indexes are created

### Debug Commands

```bash
# Check database schema
psql $DATABASE_URL -c "\d archived_content"

# Test individual components
python -c "from archive_unified_schema import UnifiedArchiveDB; db = UnifiedArchiveDB('$DATABASE_URL'); print(db.get_statistics())"

# Check Rails models
rails console -e production
> ArchivedContent.count
> ArchivedContent.statistics
```

---

## 🎉 Result

**ONE UNIFIED SYSTEM** for searching, analyzing, and publishing from ALL your archive sources with:

- ✅ **Single Database**: PostgreSQL with full-text search + semantic vectors
- ✅ **Dual APIs**: FastAPI (Python) + Rails (Ruby) for maximum flexibility  
- ✅ **Smart Import**: Node Archive Browser → PostgreSQL with conversation threading
- ✅ **LPE Integration**: AI enhancement pipeline for content quality
- ✅ **WriteBook Ready**: Direct publishing to discourse platform
- ✅ **Scalable**: Designed for millions of messages across all sources

Ready to consolidate ALL your archives! 🚀