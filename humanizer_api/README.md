# Humanizer API - Content Curation Ecosystem

🎯 **Status: Phase 1 Complete - Archive & LPE APIs Ready**

A complete API ecosystem for content ingestion, transformation, and quality assessment designed to support thoughtful discourse platforms. This is the foundation for humanizer.com - recreating the quality of VAX Notes era discussions with modern AI assistance.

## 🚀 Quick Start

```bash
cd /Users/tem/humanizer_api
python smart_start.py
```

**Service URLs:**
- Archive API: http://localhost:7200/docs
- LPE API: http://localhost:7201/docs
- Health Checks: http://localhost:7200/health

## 🎯 Vision & Current Status

## Architecture Overview

The Humanizer API provides a complete content processing pipeline that flows from local archive management through AI-powered transformation and review to final publication on the humanizer.com Discourse platform.

```
┌─────────────────────────────────────────────────────────────────────┐
│                        LOCAL PROCESSING                            │
├─────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐    │
│  │   Archive API   │  │    LPE API      │  │  ChromaDB       │    │
│  │                 │  │                 │  │  Memory         │    │
│  │ • Universal     │  │ • Projection    │  │                 │    │
│  │   Ingestion     │  │ • Analysis      │  │ • Knowledge     │    │
│  │ • Search        │  │ • Maieutic      │  │   Management    │    │
│  │ • Organization  │  │ • Translation   │  │ • Learning      │    │
│  │                 │  │ • Synthesis     │  │ • Insights      │    │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     CONTENT REVIEW PIPELINE                        │
├─────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐                    ┌─────────────────┐         │
│  │ Lamish Lawyer   │                    │ Lamish Pulse    │         │
│  │                 │                    │ Controller      │         │
│  │ • Quality Check │ ────────────────► │                 │         │
│  │ • Style Review  │                    │ • Final Gate    │         │
│  │ • Fact Verify   │                    │ • Publishing    │         │
│  │ • Tone Analysis │                    │ • Group Routing │         │
│  └─────────────────┘                    └─────────────────┘         │
└─────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    HUMANIZER.COM DISCOURSE                         │
├─────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐    │
│  │ Curated Groups  │  │ AI Moderation   │  │ Quality Metrics │    │
│  │                 │  │                 │  │                 │    │
│  │ • Topic-based   │  │ • Real-time     │  │ • Engagement    │    │
│  │ • Skill-based   │  │   Guidance      │  │ • Quality Score │    │
│  │ • Interest-based│  │ • Conflict      │  │ • Learning      │    │
│  │                 │  │   Resolution    │  │   Outcomes      │    │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
```

## Services

### 1. Archive API (Port 8001)
- **Universal Content Ingestion**: Files, text, URLs, social media exports
- **Semantic Search**: Vector embeddings + full-text search
- **Source Management**: Organize by origin, metadata, tags
- **Export/Import**: Multiple formats, backup/restore

### 2. LPE API (Port 8002)
- **Projection Engine**: Transform through persona/namespace/style
- **Analysis Engine**: Extract inherent characteristics
- **Maieutic Engine**: Generate Socratic questions
- **Translation Engine**: Cross-domain and language translation
- **Synthesis Engine**: Combine multiple content pieces

### 3. Lamish Lawyer API (Port 8003)
- **Quality Assessment**: Content quality scoring
- **Style Consistency**: Maintain discourse standards
- **Fact Verification**: Basic accuracy checking
- **Tone Analysis**: Ensure constructive discourse
- **Recommendation Engine**: Suggest improvements

### 4. Lamish Pulse Controller API (Port 8004)
- **Final Review**: Gate-keeping for publication
- **Group Routing**: Direct to appropriate discourse groups
- **Publishing Pipeline**: Automated posting to Discourse
- **Metrics Collection**: Track success rates and quality

### 5. ChromaDB Memory Integration
- **Knowledge Management**: Store insights and learnings
- **Best Practices**: Track successful patterns
- **Bug Tracking**: Document and resolve issues
- **Package Management**: Monitor dependency updates

## Quick Start

```bash
# Start all working services
python smart_start.py

# Or individual services
python test_setup.py archive    # Archive API (Port 7200)
python test_setup.py lpe        # LPE API (Port 7201)

# Check status
python main.py status

# Full dashboard (if dependencies available)
python main.py dashboard
```

## API Endpoints

### Archive API (7200) ✅ WORKING
```
POST /ingest          # Upload content
GET  /search          # Search content
GET  /content/{id}    # Get specific content
GET  /sources         # List sources
GET  /stats           # Archive statistics
```

### LPE API (7201) ✅ WORKING
```
POST /process         # Transform content
GET  /processors      # List engines
GET  /sessions/{id}   # Session history
POST /batch           # Batch processing
```

### Lamish Lawyer API (7202) 🎯 NEXT PHASE
```
POST /review          # Review content quality
POST /verify          # Fact verification
GET  /standards       # Quality standards
POST /improve         # Suggest improvements
```

### Lamish Pulse Controller API (7203) 🔮 FUTURE
```
POST /submit          # Submit for publication
GET  /queue           # Review publication queue
POST /publish         # Publish to Discourse
GET  /metrics         # Success metrics
```

## Development Workflow

1. **Local Development**: All APIs run locally for development
2. **Content Creation**: Use Archive API to manage content sources
3. **Content Processing**: Transform content through LPE API
4. **Quality Review**: Submit to Lamish Lawyer for assessment
5. **Publication**: Send approved content through Pulse Controller
6. **Knowledge Capture**: All insights stored in ChromaDB Memory

## Configuration

Environment variables:
```bash
# API Ports (Updated to avoid conflicts)
ARCHIVE_API_PORT=7200
LPE_API_PORT=7201
LAWYER_API_PORT=7202
PULSE_API_PORT=7203

# Database
CHROMADB_PATH=./chromadb_data
POSTGRES_URL=postgresql://user:pass@localhost/humanizer

# LLM Providers
OPENAI_API_KEY=your_key
ANTHROPIC_API_KEY=your_key
DEEPSEEK_API_KEY=your_key

# Discourse Integration
DISCOURSE_URL=https://humanizer.com
DISCOURSE_API_KEY=your_discourse_key
DISCOURSE_USERNAME=api_user
```

## License

MIT License - Built for thoughtful discourse and AI-human collaboration.
