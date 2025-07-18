# Claude Code Context - Humanizer Lighthouse Platform

## 🎯 Project Overview
**Humanizer Lighthouse** is a full-stack content transformation platform combining:
- **Python FastAPI Backend** - Enhanced Lighthouse API with Lamish Projection Engine (LPE)
- **React Frontend** - Modern UI with 9 specialized tabs for content transformation
- **Multi-LLM Integration** - 11+ providers with secure key management
- **Real-time Processing** - WebSocket-enabled live updates and monitoring

## 🏗️ Architecture Summary

### Two-Service Architecture
```
┌─────────────────────┐    HTTP/WebSocket    ┌──────────────────────┐
│   React Frontend    │ ←─────────────────→ │   Python Backend    │
│   (lighthouse-ui)   │                     │   (humanizer_api)    │
│   Port 3100/3101    │                     │   Port 8100          │
└─────────────────────┘                     └──────────────────────┘
        │                                              │
        ├─ 9 Specialized Tabs                         ├─ 50+ API Endpoints
        ├─ Real-time UI Updates                       ├─ 11 LLM Providers  
        ├─ API Console & Testing                      ├─ Secure Key Storage
        └─ Batch Processing Interface                 └─ WebSocket Support
```

## 🚨 CRITICAL: Environment Management

### ⚠️ Python Environment Rules
**ALWAYS use the lighthouse venv - NEVER the root venv!**

```bash
# ✅ CORRECT Environment
cd humanizer_api/lighthouse
source venv/bin/activate  
python --version          # Python 3.11.11
which python             # /path/to/lighthouse/venv/bin/python

# ❌ WRONG Environment  
cd humanizer_api
source venv/bin/activate  # Has path issues & SSL problems
python --version          # Python 3.9.12 (wrong)
```

### Why This Matters
- **Root venv**: Points to wrong paths, SSL issues, missing dependencies
- **Lighthouse venv**: Proper Python 3.11.11, all packages installed, correct paths

## 🚀 Startup Procedures (EXACT COMMANDS)

### Backend Startup
```bash
cd /Users/tem/humanizer-lighthouse/humanizer_api/lighthouse
source venv/bin/activate
python api_enhanced.py
```

**Expected Success Output:**
```
INFO: Started server process [XXXXX]
INFO: Enhanced Lighthouse API with full LPE features  
INFO: Using LLM provider: OllamaProvider
INFO: Uvicorn running on http://127.0.0.1:8100
```

### Frontend Startup  
```bash
cd /Users/tem/humanizer-lighthouse/lighthouse-ui
npm run dev
```

**Expected Success Output:**
```
VITE v5.4.19 ready in XXXms
➜ Local: http://127.0.0.1:3100/
```

## 🛑 Shutdown Procedures

### Graceful Shutdown
1. **Frontend**: `Ctrl+C` in npm terminal
2. **Backend**: `Ctrl+C` in python terminal

### Force Kill (Emergency)
```bash
# Kill backend
lsof -ti:8100 | xargs kill -9

# Kill frontend  
lsof -ti:3100 | xargs kill -9
lsof -ti:3101 | xargs kill -9
```

#### Humanizer API Services
```bash
cd humanizer_api
python smart_start.py       # Intelligent startup with dependency handling
python src/simple_archive_api.py  # Simple archive API (minimal deps)
python test_setup.py archive      # Test archive API setup
```

### Service Ports
- **Lighthouse UI**: 3100 (Vite dev server with enhanced tabbed interface)
- **Enhanced Lighthouse API**: 8100 (FastAPI with full LPE features)
- **Archive API**: 7200 (FastAPI)
- **LPE API**: 7201 (FastAPI)
- **Planned APIs**: 7202 (Lawyer), 7203 (Pulse Controller)

### Enhanced API Features
- **Advanced transformation**: `/api/transform` with 5-step pipeline
- **Maieutic dialogue**: `/api/maieutic/*` endpoints for Socratic exploration
- **Translation analysis**: `/api/translation/*` endpoints for semantic stability
- **WebSocket support**: `/ws/maieutic/{session_id}` for real-time interaction

## Architecture Overview

### Lighthouse (Current Focus)
A viral web application demonstrating narrative transformation through the Lamish Projection Engine:

```
Frontend (React/Vite)        Backend (FastAPI)
┌─────────────────────┐     ┌─────────────────────┐
│ • Narrative Input   │ ←→  │ • Text Processing   │
│ • Transformation    │     │ • LLM Integration   │
│ • Visual Results    │     │ • NLP Analysis      │
│ • Diff Viewer       │     │ • spaCy Model       │
└─────────────────────┘     └─────────────────────┘
```

### Humanizer API (Background System)
Multi-service architecture for content curation:

```
Archive API → LPE API → [Lawyer API] → [Pulse Controller] → Discourse
```

## Key Components

### Frontend (lighthouse-ui/src/)
- **App.jsx** - Main application component with theme switching
- **components/NarrativeInput.jsx** - Text input with transformation controls
- **components/DeconstructionView.jsx** - Shows narrative deconstruction
- **components/ProjectionView.jsx** - Displays transformed results
- **components/TransformationControls.jsx** - Persona/namespace/style selectors
- **components/LighthouseBeacon.jsx** - Animated lighthouse icon

### Backend (humanizer_api/lighthouse/)
- **api.py** - FastAPI application with transformation endpoints
- **requirements.txt** - Python dependencies including spaCy and LiteLLM
- **start.sh** - Service startup script

### Humanizer API (humanizer_api/src/)
- **archive_api.py** - Universal content ingestion with semantic search
- **lpe_api.py** - Multi-engine content transformation
- **simple_archive_api.py** - Minimal dependency version
- **config.py** - Centralized configuration management

## Development Workflow

### For Lighthouse Features
1. **Frontend changes**: Edit React components in `lighthouse-ui/src/`
2. **API changes**: Modify `humanizer_api/lighthouse/api.py`
3. **Test locally**: Use `./start_lighthouse.sh`
4. **Dependencies**: Frontend uses Vite+React, backend uses FastAPI+LiteLLM

### For Humanizer API Features
1. **Start services**: Use `python smart_start.py`
2. **Test endpoints**: Access `/docs` for each API (e.g., http://localhost:7200/docs)
3. **Add new APIs**: Follow the pattern in `src/` directory

## Environment Configuration

### Required Environment Variables
```bash
# LLM Provider Keys (add to .env files)
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
DEEPSEEK_API_KEY=your_key_here    # Cost-effective option

# API Ports (configured to avoid conflicts)
ARCHIVE_API_PORT=7200
LPE_API_PORT=7201
LAWYER_API_PORT=7202
PULSE_API_PORT=7203

# Database Configuration
CHROMADB_PATH=./chromadb_data
SQLITE_PATH=./data/humanizer.db
```

## Key Technologies

### Frontend Stack
- **React 18** - UI framework
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Styling framework
- **Framer Motion** - Animation library
- **React Diff Viewer** - Code comparison display

### Backend Stack
- **FastAPI** - Python web framework
- **LiteLLM** - Multi-provider LLM integration
- **spaCy** - NLP processing (requires `en_core_web_trf` model)
- **ChromaDB** - Vector database for semantic search
- **SQLAlchemy** - Database ORM

## API Endpoints

### Lighthouse API (Port 8100)
- `GET /health` - Health check
- `GET /configurations` - Available personas, namespaces, styles
- `POST /transform` - Transform narrative text

### Archive API (Port 7200)
- `POST /ingest` - Upload and process content
- `GET /search` - Semantic search
- `GET /content/{id}` - Retrieve specific content

### LPE API (Port 7201)
- `POST /process` - Content transformation
- `GET /processors` - Available engines
- `POST /batch` - Batch processing

## Testing and Development

### Frontend Testing
```bash
cd lighthouse-ui
npm run dev      # Start development server
# Open http://localhost:3100
```

### Backend Testing
```bash
cd humanizer_api
python test_setup.py archive    # Test archive API
python test_setup.py lpe        # Test LPE API
curl http://localhost:7200/health  # Health check
```

### Dependencies Management
- **Frontend**: `package.json` and `package-lock.json`
- **Backend**: `requirements.txt` with pinned versions
- **Python Environment**: Virtual environments in each service directory

## Philosophy and Design Principles

### Lamish Projection Engine
Based on phenomenological principles with three-layer subjectivity:
- **Essence (N_E)**: Core facts and relationships
- **Persona (Ψ)**: Worldview and perspective
- **Namespace (Ω)**: Universe of references
- **Style (Σ)**: Linguistic approach

### Multi-Provider LLM Strategy
- **Primary**: DeepSeek (cost-effective)
- **Privacy**: Ollama (local models)
- **Premium**: OpenAI/Anthropic (high quality)

### Graceful Degradation
- Simple modes when dependencies unavailable
- Fallback options for all services
- Comprehensive error handling

## Future Development

### Immediate Priorities
1. **Lamish Lawyer API** - Content quality assessment
2. **Enhanced UI features** - More transformation options
3. **Performance optimization** - Caching and async processing

### Long-term Vision
- Integration with Discourse platform
- Community-driven content curation
- Advanced analytics and feedback loops
- Browser plugin for local processing

## Troubleshooting

### Common Issues
1. **Missing spaCy model**: Run `python -m spacy download en_core_web_trf`
2. **Port conflicts**: Check configured ports in environment variables
3. **Missing API keys**: Verify `.env` files contain required LLM provider keys
4. **Dependencies**: Use `smart_start.py` for intelligent dependency handling

### Development Tips
- Use the `/docs` endpoints for interactive API testing
- Check logs in `humanizer_api/logs/` for debugging
- The `smart_start.py` script handles most dependency issues automatically
- Frontend hot-reloading works via Vite for rapid development