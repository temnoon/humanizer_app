# Humanizer Database Architecture

## Overview
The Humanizer system uses a **hybrid database architecture** combining multiple storage technologies for different data types and use cases.

## Database Technologies

### 1. **SQLite** (Primary Structured Data)
- **Usage**: Metadata, job queues, attribute catalogs, system configuration
- **Location**: Various `.db` files in project directories
- **Key Tables**:
  - `unified_catalog.db` (Unified API v1): Sources, Documents, Chunks, Attributes, Kernels, Projections
  - `batch_jobs.db`: Processing job queue and status
  - `attributes.db`: Extracted narrative attributes catalog

### 2. **PostgreSQL** (Conversation Archive)
- **Usage**: Large-scale conversation data storage
- **Database**: `humanizer_archive`
- **Key Tables**:
  - `archived_content`: Message storage with metadata
  - `conversations`: Grouped conversation threads
  - `message_analysis`: AI analysis results
- **Connection**: `postgresql://tem@localhost/humanizer_archive`

### 3. **ChromaDB** (Vector Embeddings)
- **Usage**: Semantic search, similarity matching
- **Location**: `./chromadb_data/` directory
- **Collections**:
  - Document embeddings
  - Conversation embeddings  
  - Attribute embeddings
- **Models**: Uses sentence-transformers for embedding generation

### 4. **FAISS** (High-Performance Vector Search)
- **Usage**: Fast similarity search, clustering
- **Files**: 
  - `faiss_index.faiss`: Vector index
  - `faiss_metadata.json`: Chunk mappings
- **Integration**: Unified API v1 embedding service

### 5. **File-Based Storage** (Content Blobs)
- **Usage**: Raw content, cached data, processing results
- **Directories**:
  - `content_blobs/`: Content-addressed file storage
  - `data/imported_conversations/`: Conversation JSON files
  - `mass_attributes/`: Bulk attribute extraction results
  - `discovered_attributes/`: Literature-derived attributes

## Data Flow Architecture

```
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐
│   Input Data    │───▶│  Processing  │───▶│   Storage       │
│                 │    │  Pipeline    │    │                 │
│ • Conversations │    │              │    │ • SQLite (meta) │
│ • Documents     │    │ • Chunking   │    │ • PostgreSQL    │
│ • Literature    │    │ • Embedding  │    │ • ChromaDB      │
│ • Web Content   │    │ • Analysis   │    │ • FAISS         │
└─────────────────┘    └──────────────┘    └─────────────────┘
```

## API Database Mappings

### Enhanced API (Port 8100)
```python
# PostgreSQL for conversations
POSTGRES_URL = 'postgresql://tem@localhost/humanizer_archive'

# ChromaDB for semantic search
chromadb_client = chromadb.Client()

# SQLite for job tracking
batch_db = sqlite3.connect('batch_jobs.db')
```

### Unified API v1 (Port 8101)
```python
# SQLite catalog
catalog_db = sqlite3.connect('unified_catalog.db')

# FAISS for vectors
faiss_index = faiss.IndexFlatL2(embedding_dim)

# Content-addressed blobs
content_store = './content_blobs/{blake3_hash}'
```

## Database Schemas

### SQLite Unified Catalog
```sql
-- Core content entities
CREATE TABLE sources (
    source_id TEXT PRIMARY KEY,
    kind TEXT,           -- file|conversation|web|transcript
    provenance TEXT,     -- JSON metadata
    hash TEXT,          -- Blake3 content hash
    size_bytes INTEGER
);

CREATE TABLE documents (
    doc_id TEXT PRIMARY KEY,
    source_ids TEXT,     -- JSON array
    mime TEXT,
    structure TEXT,      -- JSON document structure
    content_hash TEXT    -- Points to content blob
);

CREATE TABLE chunks (
    chunk_id TEXT PRIMARY KEY,
    doc_id TEXT,
    span_start INTEGER,
    span_end INTEGER,
    text TEXT,
    faiss_id INTEGER,    -- Links to FAISS index
    embedding_model TEXT
);

CREATE TABLE attributes (
    attribute_id TEXT PRIMARY KEY,
    chunk_id TEXT,
    type TEXT,           -- persona|style|namespace|theme
    value TEXT,
    confidence REAL,
    method TEXT,         -- JSON extraction method
    evidence TEXT        -- JSON evidence span
);

CREATE TABLE kernels (
    kernel_id TEXT PRIMARY KEY,
    scope TEXT,          -- JSON chunk references
    meaning TEXT,        -- JSON embedding centroids
    attribute_posteriors TEXT,  -- JSON probability distributions
    lineage TEXT         -- JSON parent relationships
);
```

### PostgreSQL Archive Schema
```sql
-- Conversation data (existing)
CREATE TABLE archived_content (
    id SERIAL PRIMARY KEY,
    parent_id TEXT,
    type TEXT,
    title TEXT,
    body_text TEXT,
    metadata JSONB,
    timestamp TIMESTAMP,
    source_platform TEXT
);

CREATE TABLE message_analysis (
    id SERIAL PRIMARY KEY,
    content_id INTEGER REFERENCES archived_content(id),
    analysis_type TEXT,
    results JSONB,
    confidence REAL,
    created_at TIMESTAMP
);
```

## Performance Characteristics

### Query Patterns
- **Fast Text Search**: PostgreSQL full-text search + GIN indexes
- **Semantic Search**: ChromaDB/FAISS vector similarity
- **Metadata Queries**: SQLite with proper indexes
- **Content Retrieval**: Direct file system access via content hash

### Scaling Considerations
- **SQLite**: Suitable for single-user, moderate data volumes
- **PostgreSQL**: Handles large conversation archives efficiently  
- **ChromaDB**: Scales to millions of embeddings
- **FAISS**: Optimized for high-performance vector search

## Backup and Recovery

### Critical Data
1. **PostgreSQL database** - Full conversations archive
2. **SQLite catalogs** - Processing metadata and job queues
3. **ChromaDB data** - Semantic embeddings
4. **Content blobs** - Original content files

### Backup Strategy
```bash
# PostgreSQL backup
pg_dump humanizer_archive > backup_$(date +%Y%m%d).sql

# SQLite backup
cp *.db backups/

# ChromaDB backup  
tar -czf chromadb_backup.tar.gz chromadb_data/

# Content blobs
rsync -av content_blobs/ backups/content_blobs/
```

## Current Database Status

### Enhanced API Connections
- ✅ PostgreSQL: `humanizer_archive` database active
- ✅ ChromaDB: Embedding collections initialized
- ✅ SQLite: Job queues and metadata tables created

### Data Volumes (Approximate)
- **Conversations**: ~1000s archived in PostgreSQL
- **Attributes**: ~450+ literature-derived samples  
- **Embeddings**: Various collections in ChromaDB
- **Content Blobs**: Gigabytes of processed literature

## Development Notes

### Database Initialization
Most databases are auto-created on first API startup. Critical tables are created via migration scripts in the API initialization code.

### Environment Variables
```bash
POSTGRES_URL=postgresql://tem@localhost/humanizer_archive
CHROMADB_PATH=./chromadb_data
SQLITE_PATH=./data/humanizer.db
```

### Connection Pooling
- PostgreSQL: Uses psycopg2 with connection pooling
- SQLite: Direct connections (suitable for single-user)
- ChromaDB: Client-based connections
- FAISS: Memory-mapped index files

The architecture prioritizes **hybrid storage** - using the right database technology for each data type and access pattern, ensuring both performance and data integrity across the full narrative processing pipeline.