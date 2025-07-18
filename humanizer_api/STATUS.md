# Humanizer API - Current Status & Quick Start Guide

## 🎯 Project Status
The Humanizer API ecosystem is **ready to use** with multiple startup options depending on your dependency situation.

## 🚀 Quick Start Options

### Option 1: Smart Start (Recommended)
```bash
cd /Users/tem/humanizer_api
python smart_start.py
```
This automatically detects your dependencies and starts either full or simple mode.

### Option 2: Manual Dependency Fix
```bash
cd /Users/tem/humanizer_api
source venv/bin/activate
pip install httpx==0.25.2 rich==13.7.0 pydantic-settings==2.0.3
python test_setup.py archive
```

### Option 3: Simple Mode (Works with minimal dependencies)
```bash
cd /Users/tem/humanizer_api
python src/simple_archive_api.py
```

## 📊 What You Have

### ✅ Complete Architecture
- **Archive API** (Port 7200) - Universal content ingestion and semantic search
- **LPE API** (Port 7201) - Multi-engine content transformation  
- **Configuration System** - Environment-aware with multi-provider LLM support
- **Database Integration** - SQLite/PostgreSQL with ChromaDB for vectors
- **Service Management** - Start/stop scripts with health monitoring

### ✅ Production-Ready Features
- Multi-provider LLM support (DeepSeek, OpenAI, Anthropic, Ollama)
- Intelligent fallback and error handling
- Session management with database persistence
- Content deduplication and metadata management
- Semantic search with vector embeddings
- RESTful API with automatic documentation

### ✅ Flexible Deployment
- **Full Mode**: All features with dependencies
- **Simple Mode**: Core functionality with minimal dependencies
- **CLI Mode**: Text-based interface for testing

## 🔗 Service URLs (When Running)

### Archive API (Port 7200)
- **API Base**: http://localhost:7200
- **Documentation**: http://localhost:7200/docs
- **Health Check**: http://localhost:7200/health

### LPE API (Port 7201)  
- **API Base**: http://localhost:7201
- **Documentation**: http://localhost:7201/docs
- **Health Check**: http://localhost:7201/health

## 📋 Core API Endpoints

### Archive API
- `POST /ingest` - Add content (files, text, URLs)
- `POST /search` - Semantic and full-text search
- `GET /content/{id}` - Retrieve specific content
- `GET /sources` - List all content sources
- `GET /stats` - Archive statistics
- `DELETE /content/{id}` - Remove content

### LPE API
- `POST /transform` - Content transformation
- `POST /session` - Create transformation session
- `GET /engines` - List available LLM engines
- `GET /session/{id}` - Session status
- `POST /batch` - Batch processing

## 🛠️ Configuration

The system uses environment variables (`.env` file):

```env
# Ports (avoiding conflicts)
ARCHIVE_API_PORT=7200
LPE_API_PORT=7201

# LLM Configuration
LLM_PREFERRED_PROVIDER=deepseek
DEEPSEEK_API_KEY=your_key_here
OLLAMA_HOST=http://localhost:11434

# Database
CHROMADB_PATH=./chromadb_data
SQLITE_PATH=./data/humanizer.db
```

## 🎯 Next Steps for Complete Vision

### Immediate (Working Now)
1. ✅ Archive API - Content ingestion and search
2. ✅ LPE API - Content transformation
3. ✅ Simple Mode - Basic functionality

### Next Phase  
1. **Lamish Lawyer API** - Content quality assessment
2. **Lamish Pulse Controller** - Publication gatekeeper
3. **Browser Plugin** - Local processing with cloud sync
4. **Discourse Integration** - AI-curated community platform

## 🔧 Troubleshooting

### Missing Dependencies
```bash
source venv/bin/activate
pip install httpx rich pydantic-settings python-dotenv
```

### Port Conflicts
Edit `.env` file to change ports:
```env
ARCHIVE_API_PORT=7300
LPE_API_PORT=7301
```

### Database Issues
```bash
rm -rf data/ chromadb_data/  # Reset databases
python smart_start.py        # Restart
```

## 💡 Architecture Highlights

### Content Pipeline
```
Local Files → Archive API → Vector Embeddings → Semantic Search
          ↓
     LPE API → Transformations → [Future: Lamish Lawyer] → [Future: Pulse Controller] → Discourse
```

### Multi-Provider LLM Support
- **DeepSeek**: Cost-effective for production
- **Ollama**: Privacy-focused local processing  
- **OpenAI/Anthropic**: Premium quality when needed
- **Intelligent Fallback**: Automatic provider switching

### Data Storage
- **SQLite**: Simple deployment, file-based
- **PostgreSQL**: Production scalability
- **ChromaDB**: Vector embeddings for semantic search
- **Memory Integration**: Learning and best practices

## 🎉 Ready to Use!

Your Humanizer API foundation is complete and ready for the vision of recreating thoughtful discourse quality with modern AI curation. The API-first architecture supports everything from local browser plugins to cloud-scale discourse platforms.

Start with: `python smart_start.py`
