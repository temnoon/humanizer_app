# Claude Code Context - Humanizer API Project

## 🎯 Project Overview
The Humanizer API is a complete ecosystem for content ingestion, transformation, and curation designed to support the vision of recreating thoughtful discourse quality (like VAX Notes era) with modern AI assistance. This is the foundation for humanizer.com - a discourse platform with AI-powered content curation.

## 📍 Current Status: **PHASE 1 COMPLETE** 
✅ **Archive API and LPE API are fully implemented and ready**

### What's Working Now:
- **Archive API** (Port 7200) - Universal content ingestion with semantic search
- **LPE API** (Port 7201) - Multi-engine content transformation 
- **Smart Startup System** - Handles dependency issues gracefully
- **Production Configuration** - Multi-provider LLM support with fallbacks
- **Database Integration** - SQLite/PostgreSQL + ChromaDB for vectors

## 🚀 How to Start the System

### Quick Start (Always Works):
```bash
cd /Users/tem/humanizer_api
python smart_start.py
```

### Alternative Options:
```bash
# Simple mode (minimal dependencies)
python src/simple_archive_api.py

# Full mode (after installing dependencies)
source venv/bin/activate
pip install httpx rich pydantic-settings
python test_setup.py archive
```

### Service URLs:
- Archive API: http://localhost:7200/docs
- LPE API: http://localhost:7201/docs
- Health: http://localhost:7200/health

## 🎯 Next Phase: **LAMISH LAWYER API** (Content Quality Assessment)

### What Claude Code Should Build Next:
The **Lamish Lawyer API** (Port 7202) - Content quality assessment and style review that acts as a gatekeeper before content goes to the Pulse Controller.

### Key Features Needed:
1. **Content Quality Scoring** - Analyze writing quality, coherence, factual accuracy
2. **Style Assessment** - Ensure content meets discourse standards
3. **Tone Analysis** - Detect inflammatory, toxic, or unconstructive content
4. **Citation Verification** - Check claims and sources when possible
5. **Improvement Suggestions** - Provide specific feedback for enhancement
6. **Integration Points** - Work with Archive API output and feed to Pulse Controller

### Architecture Context:
```
Content → Archive API → LPE API → [Lamish Lawyer API] → [Pulse Controller] → Discourse
```

## 📋 Project Structure
```
/Users/tem/humanizer_api/
├── src/
│   ├── archive_api.py          # ✅ Universal content ingestion
│   ├── lpe_api.py             # ✅ Multi-engine transformation  
│   ├── simple_archive_api.py  # ✅ Minimal dependency version
│   ├── config.py              # ✅ Centralized configuration
│   └── [NEXT: lawyer_api.py]  # 🎯 Content quality assessment
├── smart_start.py             # ✅ Intelligent startup script
├── test_setup.py              # ✅ Dependency testing
├── requirements.txt           # ✅ Complete dependencies
├── .env                       # Configuration variables
└── STATUS.md                  # Current status overview
```

## 🔧 Configuration 
The system uses environment variables and supports multiple LLM providers:

```env
# API Ports (avoiding conflicts)
ARCHIVE_API_PORT=7200
LPE_API_PORT=7201
LAWYER_API_PORT=7202  # Next to implement

# LLM Configuration
LLM_PREFERRED_PROVIDER=deepseek  # Cost-effective
DEEPSEEK_API_KEY=your_key_here
OLLAMA_HOST=http://localhost:11434  # Local privacy

# Database
CHROMADB_PATH=./chromadb_data
SQLITE_PATH=./data/humanizer.db
```

## 🧠 ChromaDB Memory Integration
The project integrates with ChromaDB Memory server to:
- Learn from content patterns and user feedback
- Store best practices and configuration insights
- Track bug investigations and resolutions
- Remember successful transformation strategies

### Key Memory Tags:
- `humanizer-api` - General project updates
- `archive-api` - Content ingestion insights  
- `lpe-api` - Transformation patterns
- `configuration` - Setup and deployment lessons
- `production-ready` - Deployment status updates

## 🎯 Development Priorities

### Immediate (Next Session):
1. **Implement Lamish Lawyer API** - Content quality assessment
2. **Quality Scoring Engine** - Multi-dimensional content evaluation
3. **Integration Testing** - End-to-end pipeline validation

### Medium Term:
1. **Lamish Pulse Controller** - Publication decision making
2. **Browser Plugin** - Local content processing
3. **Discourse Integration** - Platform connectivity

### Long Term:
1. **AI-Curated Community Platform** - Complete discourse system
2. **Advanced Analytics** - Content quality trends
3. **User Feedback Loop** - Continuous improvement

## 💡 Key Insights for Claude Code

### 1. **Multi-Mode Architecture**
The system is designed to work in multiple modes:
- **Full Mode**: All features with complete dependencies
- **Simple Mode**: Core functionality with minimal requirements
- **CLI Mode**: Text-based testing interface

### 2. **Provider Agnostic Design** 
LLM integration supports multiple providers with intelligent fallback:
- DeepSeek (cost-effective)
- Ollama (privacy/local)
- OpenAI/Anthropic (premium quality)

### 3. **Production Considerations**
- Port management to avoid conflicts
- Dependency graceful degradation  
- Comprehensive error handling
- Health monitoring and stats
- Database migration support

### 4. **Vision Alignment**
Every component serves the larger goal of creating a thoughtful discourse platform that combines:
- Human agency and choice
- AI assistance without replacement
- Quality content curation
- Community-driven moderation
- "True humanization" - preserving meaning while improving expression

## 🔍 Current Issues & Solutions

### ✅ Resolved:
- Port conflicts (moved to 7200/7201)
- Missing dependencies (smart_start.py handles gracefully)
- Configuration complexity (centralized in config.py)
- Startup reliability (multiple fallback options)

### 🎯 Focus Areas:
- Content quality assessment algorithms
- Multi-dimensional scoring systems
- Integration between APIs
- Performance optimization for large content volumes

## 📚 Resources for Claude Code

### Essential Files to Review:
1. `src/config.py` - Understand configuration system
2. `src/archive_api.py` - See content ingestion patterns
3. `src/lpe_api.py` - Understand transformation architecture
4. `smart_start.py` - Learn startup and dependency handling

### API Documentation:
- Archive API: http://localhost:7200/docs (when running)
- LPE API: http://localhost:7201/docs (when running)

### Testing Endpoints:
```bash
# Test Archive API
curl -X POST "http://localhost:7200/ingest" \
  -F "content_type=text" \
  -F "source=test" \
  -F "data=Sample content for testing"

# Search content
curl -X POST "http://localhost:7200/search" \
  -F "query=sample"

# Check health
curl "http://localhost:7200/health"
```

---

**Ready for Claude Code to implement the Lamish Lawyer API and continue building toward the complete discourse platform vision! 🚀**
