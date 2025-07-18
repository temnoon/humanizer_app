# Humanizer API - Project Structure Overview

```
humanizer_api/
├── README.md                      # Complete project documentation
├── requirements.txt               # Python dependencies
├── .env                          # Environment configuration (create from .env.example)
├── .gitignore                    # Git ignore patterns
│
├── setup.sh                      # Initial project setup
├── start_humanizer_api.sh        # Start all services
├── stop_humanizer_api.sh         # Stop all services  
├── main.py                       # Main launcher & dashboard
│
├── src/                          # Source code
│   ├── config.py                 # Centralized configuration
│   ├── archive_api.py            # Archive API implementation
│   └── lpe_api.py                # LPE API implementation
│
├── logs/                         # Service logs (auto-created)
│   ├── archive_api.log
│   ├── lpe_api.log
│   ├── archive_api.pid
│   └── lpe_api.pid
│
├── data/                         # Data storage (auto-created)
│   └── humanizer.db              # SQLite database
│
├── chromadb_data/                # ChromaDB vector storage
│
└── venv/                         # Python virtual environment
```

## Quick Start Commands

```bash
# Initial setup
./setup.sh

# Start all services
./start_humanizer_api.sh

# Check status
python main.py status

# Real-time dashboard
python main.py dashboard

# Stop all services
./stop_humanizer_api.sh
```

## Service URLs

- **Archive API**: http://localhost:8001
  - Documentation: http://localhost:8001/docs
  - Health: http://localhost:8001/health

- **LPE API**: http://localhost:8002
  - Documentation: http://localhost:8002/docs  
  - Health: http://localhost:8002/health

## Key Features Implemented

### Archive API
✅ Universal content ingestion (files, text, URLs)
✅ Semantic search with ChromaDB vector storage
✅ Full-text search with database queries
✅ Content deduplication and source management
✅ Statistics and analytics endpoints

### LPE API  
✅ Multi-engine processing (Projection, Analysis, Maieutic)
✅ Multi-provider LLM support (DeepSeek, Ollama)
✅ Session management and operation tracking
✅ Background task processing
✅ Health monitoring and fallback handling

### Infrastructure
✅ Centralized configuration management
✅ Database abstraction (PostgreSQL/SQLite)
✅ Logging and monitoring
✅ Service orchestration scripts
✅ Real-time status dashboard

## Next Phase: Content Review Pipeline

The foundation is now ready for implementing:

1. **Lamish Lawyer API (Port 8003)** - Content quality assessment
2. **Lamish Pulse Controller API (Port 8004)** - Publication gatekeeper
3. **Browser Plugin** - Local processing with cloud sync
4. **Discourse Integration** - Final publication platform

## Architecture Benefits

- **API-First Design**: Clean separation enables browser plugin development
- **Media-Agnostic**: Handles any content type through unified interface
- **Multi-Provider LLM**: Cost optimization and reliability through fallback
- **Session Management**: Processing chains and iteration support
- **ChromaDB Integration**: Learning and knowledge management
- **Production Ready**: Logging, monitoring, error handling, health checks

This foundation provides everything needed for the complete humanizer.com discourse platform vision while maintaining the local processing privacy and AI curation quality standards.
