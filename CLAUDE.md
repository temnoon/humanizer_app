# Claude Code Context - Humanizer Lighthouse Platform

## 🎯 Project Overview
**Humanizer Lighthouse** is a full-stack content transformation platform combining:
- **Python FastAPI Backend** - Enhanced Lighthouse API with Lamish Projection Engine (LPE)
- **React Frontend** - Modern UI with 9 specialized tabs for content transformation
- **Multi-LLM Integration** - 11+ providers with secure key management
- **Real-time Processing** - WebSocket-enabled live updates and monitoring
- **🆕 Advanced Book Generation** - Sophisticated semantic clustering and automated book creation from personal insights
- **🆕 Thematic Content Discovery** - AI-powered tools to find forgotten ideas and organize them coherently
- **🆕 Universal Content Processing** - Works with any content source (notebooks, conversations, files)

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
        ├─ Book Generation Interface                  ├─ WebSocket Support
        └─ Batch Processing Interface                 └─ Advanced Semantic Analysis Engine
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

## 📱 HAW CLI - Comprehensive Command-Line Interface

### Overview
The **HAW (Humanizer Archive Wrapper)** CLI provides complete access to all platform features through a unified command-line interface. Use `./haw help` to see all available commands.

### System Management
```bash
haw status                    # Complete system health check
haw processes                 # Show active humanizer processes  
haw logs                      # View recent log activity
haw setup                     # Setup/repair Python environment
```

### 🆕 Book Generation Commands
The platform now includes sophisticated book generation capabilities:

#### **Content Discovery & Analysis**
```bash
# Discover handwritten notebook transcripts
haw browse-notebooks browse        # Interactive browsing
haw browse-notebooks list          # List all conversations
haw browse-notebooks analyze 123   # Analyze specific conversation

# Extract and analyze writing patterns
haw extract-writing extract --limit 1000
haw browse-writing summary
haw browse-wordclouds search consciousness

# Thematic clustering overview
haw curate-book analyze           # Quick thematic analysis
haw explore-themes               # System capabilities overview
```

#### **Advanced Book Generation (Recommended)**
Sophisticated semantic clustering with highest quality output:
```bash
# Generate high-quality books with advanced algorithms
haw advanced-books --min-quality 0.4 --max-books 3

# Preview without generating files
haw advanced-books --analyze-only

# Custom quality threshold
haw advanced-books --min-quality 0.6 --max-books 2
```

#### **Universal Book Generator**
General-purpose generator that works with any content source:
```bash
# From notebook transcripts (default)
haw universal-books --source-type notebooks --min-quality 0.4

# From any conversation type
haw universal-books --source-type conversations --gizmo-id g-XXXXX

# From files on disk
haw universal-books --source-type files --file-path /content/directory
```

#### **AI Editorial Assistant**
```bash
# Refine generated books with AI analysis
haw book-editor                    # Process all books
haw book-editor --book filename.md # Edit specific book
```

#### **Complete Pipeline**
End-to-end automation with AI editorial refinement:
```bash
# Full automated pipeline
haw book-pipeline --quality-threshold 0.3

# Test the complete workflow
haw book-pipeline --dry-run
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

### 🆕 Advanced Book Generation Philosophy
- **Quality over Quantity**: Sophisticated filtering produces fewer, higher-quality insights
- **Semantic Coherence**: 8-dimensional concept hierarchies ensure meaningful thematic clustering
- **Natural Progression**: Content organized from simple to complex for optimal learning flow
- **Philosophical Depth**: Multi-dimensional scoring prioritizes abstract thinking and fundamental questions
- **Universal Adaptability**: Pluggable architecture works with any content source

### Multi-Provider LLM Strategy
- **Primary**: DeepSeek (cost-effective)
- **Privacy**: Ollama (local models)
- **Premium**: OpenAI/Anthropic (high quality)

### Graceful Degradation
- Simple modes when dependencies unavailable
- Fallback options for all services
- Comprehensive error handling
- Progressive quality filtering with adjustable thresholds

## Future Development

### 🆕 Book Generation Roadmap
1. **Multi-language Support** - Generate books in multiple languages
2. **Advanced Template System** - Custom book themes and structures for different domains
3. **Collaborative Editing** - Multi-user book refinement with version control
4. **Publication Integration** - Direct export to ePub, PDF, print-ready formats
5. **Visual Content Integration** - Automatic diagram and chart generation
6. **Cross-reference System** - Intelligent linking between related concepts across books
7. **LLM-Powered Editorial Agent** - Full AI editor with human-level refinement capabilities

### Core Platform Priorities
1. **Lamish Lawyer API** - Content quality assessment and style review
2. **Enhanced UI features** - Book generation interface integration
3. **Performance optimization** - Semantic embedding caching and async processing
4. **Real-time Collaboration** - Shared book editing and analysis sessions

### Long-term Vision
- **AI-Curated Publishing Platform** - End-to-end book creation and publication
- **Discourse Integration** - Community-driven content curation and book collaboration
- **Advanced Analytics** - Content quality trends and thematic evolution tracking
- **Browser Plugin** - Local content processing and book generation from web content
- **Neural Architecture Search** - Automated optimization of book generation algorithms

## Best Practices

### 🆕 Book Generation Best Practices

#### **Content Preparation**
- **Use high-quality source content**: Book generation works best with thoughtful, reflective writing
- **Maintain content diversity**: Mix different complexity levels and emotional tones for rich books
- **Regular content curation**: Periodically review and clean your content archive

#### **Quality Threshold Selection**
- **Start with 0.4**: Good balance between quality and quantity for most content
- **Use 0.6+ for premium books**: Higher threshold for publication-ready content
- **Test with --analyze-only**: Preview results before generating files

#### **Workflow Optimization**
```bash
# Recommended workflow
1. haw browse-notebooks list          # Explore available content
2. haw curate-book analyze           # Quick thematic overview
3. haw advanced-books --analyze-only # Preview book potential
4. haw advanced-books --min-quality 0.4 --max-books 3
5. haw book-editor                   # AI-assisted refinement
```

#### **Content Source Selection**
- **Notebooks**: Best for philosophical and reflective content
- **Conversations**: Good for dialogic and exploratory content  
- **Files**: Useful for existing written content and documents

### Development Best Practices

#### **Environment Management**
- **Always use lighthouse venv**: Critical for proper dependency resolution
- **Install spaCy model**: Required for advanced semantic analysis
- **Database connection**: Ensure PostgreSQL is running and accessible

#### **Testing and Debugging**
- Use `--analyze-only` flags for safe testing
- Check `haw status` before running generation commands
- Monitor logs in `humanizer_api/lighthouse/logs/`
- Test with smaller datasets first (`--max-books 1`)

## Troubleshooting

### 🆕 Book Generation Issues

#### **No Content Found**
```bash
# Check content availability
haw browse-notebooks list
haw browse-notebooks browse

# Verify database connection
haw status
pg_isready
```

#### **Low Quality Results**
```bash
# Lower quality threshold
haw advanced-books --min-quality 0.2 --analyze-only

# Check content quality
haw curate-book analyze

# Use universal generator with different source
haw universal-books --source-type files --file-path /path/to/content
```

#### **Generation Errors**
```bash
# Test with analysis only
haw advanced-books --analyze-only

# Check dependencies
pip install -r requirements.txt
python -m spacy download en_core_web_trf

# Verify Python environment
cd humanizer_api/lighthouse
source venv/bin/activate
python --version  # Should be 3.11.11
```

### Common Issues
1. **Missing spaCy model**: Run `python -m spacy download en_core_web_trf`
2. **Port conflicts**: Check configured ports in environment variables
3. **Missing API keys**: Verify `.env` files contain required LLM provider keys
4. **Dependencies**: Use `smart_start.py` for intelligent dependency handling
5. **🆕 Missing NLP dependencies**: Install additional packages for book generation
6. **🆕 Database connection issues**: Ensure PostgreSQL service is running
7. **🆕 Memory issues**: Reduce batch sizes for large content volumes

### Development Tips
- Use the `/docs` endpoints for interactive API testing
- Check logs in `humanizer_api/logs/` for debugging
- The `smart_start.py` script handles most dependency issues automatically
- Frontend hot-reloading works via Vite for rapid development
- **🆕 Use `haw status`** for comprehensive system health checks
- **🆕 Start with `--analyze-only`** to preview book generation results
- **🆕 Test book generation** with small datasets first (`--max-books 1`)