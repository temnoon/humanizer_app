# Overnight Embeddings Setup Guide

This guide will help you set up and run full embeddings processing for your archive content overnight.

## 🎯 What This Does

The overnight embeddings system:
- Processes all archive content into semantic chunks
- Generates 768-dimensional embeddings using nomic-text-embed
- Stores everything in PostgreSQL with pgvector for fast similarity search
- Provides activity-aware prioritization (recent content first)
- Supports restartable processing with session management
- Tracks progress and provides completion statistics

## 🚀 Quick Start

### 1. Run Setup
```bash
cd /Users/tem/humanizer-lighthouse
python setup_embeddings.py
```

This will:
- ✅ Check all dependencies
- ✅ Set up database schema with pgvector
- ✅ Verify Ollama is running
- ✅ Download nomic-text-embed model if needed
- ✅ Test embedding generation
- ✅ Show current database statistics

### 2. Preview What Will Be Processed
```bash
python overnight_embeddings.py --dry-run
```

### 3. Start Processing (overnight)
```bash
# Start processing (will run until complete)
python overnight_embeddings.py

# Or with custom config
python overnight_embeddings.py --config embedding_config.json
```

## 📋 Prerequisites

### Required Software
- **PostgreSQL** with **pgvector extension**
- **Ollama** running locally
- **Python 3.8+** with required packages

### Required Python Packages
```bash
pip install asyncpg httpx rich sentence-transformers
```

### Database Setup
Your PostgreSQL database needs:
1. The `vector` extension enabled
2. The archive schema (from `setup_complete_archive.py`)
3. The embeddings schema extension (applied automatically)

## ⚙️ Configuration

The setup creates `embedding_config.json` with these settings:

```json
{
  "database": {
    "host": "localhost",
    "port": 5432,
    "user": "postgres", 
    "password": "",
    "database": "humanizer"
  },
  "embedding": {
    "ollama_host": "http://localhost:11434",
    "model_name": "nomic-text-embed",
    "chunk_size": 240,
    "chunk_overlap": 50
  },
  "processor": {
    "batch_size": 10,
    "max_concurrent": 3,
    "retry_attempts": 2,
    "delay_seconds": 0.5
  },
  "batch_limit": 1000
}
```

Edit this file to match your setup.

## 🏗️ Architecture

### Database Schema
The system adds these tables to your existing archive database:

- **`content_chunks`** - Stores text chunks with embeddings
- **`embedding_jobs`** - Tracks individual processing jobs
- **`embedding_sessions`** - Tracks overnight batch runs

### Processing Pipeline
```
Content → Smart Chunking → Summarization → Embedding → Database Storage
         (240 words)      (3 levels)     (768-dim)   (pgvector)
```

### Chunk Types
- **content** - Original text chunks (240 words, 50 word overlap)
- **summary_l1** - First-level summaries
- **summary_l2** - Second-level summaries  
- **summary_l3** - Third-level summaries

## 📊 Monitoring Progress

### Real-time Progress
The overnight script shows:
- Progress bars with completion percentage
- Batch processing statistics
- Processing rate and time estimates
- Error counts and details

### Database Views
Check progress with SQL:

```sql
-- Overall embedding statistics
SELECT * FROM embedding_stats LIMIT 10;

-- Session progress
SELECT * FROM session_progress ORDER BY started_at DESC LIMIT 5;

-- Content needing processing
SELECT * FROM get_content_needing_embeddings(20);
```

### Log Files
Processing logs are saved to:
```
logs/overnight_embeddings_[session_id].log
```

## 🔧 Troubleshooting

### Common Issues

#### "pgvector extension not found"
```bash
# Install pgvector (macOS with Homebrew)
brew install pgvector

# Or follow: https://github.com/pgvector/pgvector
```

#### "Ollama connection failed"
```bash
# Install and start Ollama
curl -fsSL https://ollama.ai/install.sh | sh
ollama serve

# Test connection
curl http://localhost:11434/api/version
```

#### "nomic-text-embed model not found"
```bash
# Download the model
ollama pull nomic-text-embed

# Or the setup script will offer to do this for you
```

#### "Database connection failed"
- Check PostgreSQL is running
- Verify credentials in `embedding_config.json`
- Ensure database exists: `createdb humanizer`

### Performance Tuning

#### For Faster Processing
```json
{
  "processor": {
    "batch_size": 20,        // Process more items at once
    "max_concurrent": 5,     // More parallel embeddings
    "delay_seconds": 0.1     // Less delay between items
  }
}
```

#### For System Stability
```json
{
  "processor": {
    "batch_size": 5,         // Smaller batches
    "max_concurrent": 2,     // Less parallelism
    "delay_seconds": 1.0     // More delay
  }
}
```

## 🎛️ Advanced Usage

### Resume Interrupted Processing
```bash
# Sessions are automatically resumable - just restart
python overnight_embeddings.py
```

### Process Specific Content
Modify the SQL in `get_content_needing_embeddings()` to filter:
```sql
-- Only process content from last week
WHERE ac.timestamp > NOW() - INTERVAL '7 days'

-- Only process specific content types
WHERE ac.content_type = 'conversation'

-- Only process large content
WHERE LENGTH(ac.content) > 1000
```

### Custom Chunk Settings
```json
{
  "embedding": {
    "chunk_size": 400,       // Larger chunks
    "chunk_overlap": 100     // More overlap for context
  }
}
```

## 🔍 After Processing

### Test Semantic Search
```python
# Example search query
import asyncpg
import asyncio

async def test_search():
    conn = await asyncpg.connect("postgresql://user:pass@host/db")
    
    # You would generate an embedding for your query first
    # query_embedding = await generate_embedding("your search query")
    
    results = await conn.fetch("""
        SELECT content_title, chunk_text, similarity_score
        FROM search_content_semantic($1, 0.7, 10)
    """, query_embedding)
    
    for row in results:
        print(f"{row['similarity_score']:.3f}: {row['content_title']}")
        print(f"  {row['chunk_text'][:100]}...")
    
    await conn.close()
```

### Monitor Database Size
```sql
-- Check table sizes
SELECT 
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE tablename IN ('content_chunks', 'archived_content')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

## 📈 Expected Performance

### Processing Rates
- **Small content** (< 1KB): ~2-5 items/second
- **Medium content** (1-10KB): ~1-2 items/second  
- **Large content** (> 10KB): ~0.5-1 items/second

### Storage Requirements
- **Text chunks**: ~2-5x original content size
- **Embeddings**: ~3KB per chunk (768 float32 values)
- **Total**: Expect ~10-20x original content size

### Example: 1000 conversations
- Original: 50MB
- Processed: ~500MB-1GB total
- Time: 2-8 hours (depending on content size)

## ✅ Success Checklist

Before running overnight:
- [ ] PostgreSQL with pgvector is running
- [ ] Ollama with nomic-text-embed is available  
- [ ] `python setup_embeddings.py` completes successfully
- [ ] `python overnight_embeddings.py --dry-run` shows expected content
- [ ] You have sufficient disk space (10-20x content size)
- [ ] Database backup is current (recommended)

## 🎉 Ready to Go!

Once setup is complete, you can:

1. **Run overnight**: `python overnight_embeddings.py`
2. **Monitor progress**: Check logs and database views
3. **Use semantic search**: Query the `content_chunks` table
4. **Integrate with apps**: Use the embeddings for smart content discovery

The system is designed to be robust and resumable, so you can start it running overnight and check the results in the morning!