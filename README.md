# Humanizer Lighthouse Platform 🚀

A comprehensive AI-powered content transformation and analysis platform implementing Quantum Narrative Theory (QNT) for intelligent text processing, Project Gutenberg integration, advanced attribute management, and **automated book generation from personal insights**.

## 🎯 Overview

The Humanizer Lighthouse Platform combines cutting-edge AI research with practical content transformation tools. Built around the **Lamish Projection Engine (LPE)** and **Quantum Narrative Theory**, it provides:

- **Narrative Analysis & Transformation** - Multi-dimensional text analysis using QNT formalism
- **Project Gutenberg Integration** - Real-time access to 70,000+ classic texts
- **Attribute Management** - Transparent algorithm tracking for projection insights
- **Multi-LLM Support** - 11+ providers with intelligent fallbacks
- **Real-time Processing** - WebSocket-enabled live updates
- **CLI & API Access** - Both programmatic and command-line interfaces
- **🆕 Automated Book Generation** - Transform personal insights into publication-ready books
- **🆕 Thematic Clustering** - Advanced semantic analysis for content discovery
- **🆕 AI Editorial Assistant** - Sophisticated content refinement and quality enhancement

## 🏗️ Architecture

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
        └─ Batch Processing Interface                 └─ Semantic Analysis Engine
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+ 
- Node.js 16+ (for frontend)
- PostgreSQL (for content storage)
- Git

### Installation

#### 1. Clone Repository
```bash
git clone <repository-url>
cd humanizer-lighthouse
```

#### 2. Backend Setup
```bash
cd humanizer_api/lighthouse
python3 -m venv venv
source venv/bin/activate  # Use LIGHTHOUSE venv (critical!)
pip install -r requirements.txt
python -m spacy download en_core_web_trf
python api_enhanced.py
```

#### 3. Frontend Setup (Optional)
```bash
cd lighthouse-ui
npm install
npm run dev
```

#### 4. CLI Access Setup
The platform includes the powerful `haw` (Humanizer Archive Wrapper) CLI:
```bash
# From project root
./haw status  # Check system health
./haw help    # See all available commands
```

### Environment Configuration
Create `.env` file in `humanizer_api/lighthouse/`:

```env
# LLM Providers
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
DEEPSEEK_API_KEY=your_key_here

# Local LLM (optional)
OLLAMA_HOST=http://localhost:11434

# Database
DATABASE_URL=postgresql://user@localhost/humanizer_archive

# API Configuration
LIGHTHOUSE_API_PORT=8100
```

## 📱 HAW CLI User Guide

The `haw` (Humanizer Archive Wrapper) CLI provides comprehensive access to all platform features, including the new book generation capabilities.

### System Management
```bash
# System health and status
haw status                    # Complete system status check
haw processes                 # Show active humanizer processes  
haw logs                      # View recent log activity
haw setup                     # Setup/repair Python environment
```

### 📝 Writing Analysis & Book Generation

#### Content Discovery & Analysis
```bash
# Extract and analyze personal writing style
haw extract-writing extract --limit 1000 --min-length 200

# Browse and explore writing analysis results
haw browse-writing browse
haw browse-writing summary
haw browse-writing samples

# Explore searchable word clouds and frequency patterns
haw browse-wordclouds browse
haw browse-wordclouds search consciousness
haw browse-wordclouds trending

# Discover handwritten notebook transcripts
haw browse-notebooks browse
haw browse-notebooks list
haw browse-notebooks analyze 225015
haw browse-notebooks export 225015
```

#### Thematic Clustering & Book Curation
```bash
# Quick thematic analysis
haw curate-book analyze              # Fast overview of themes and clusters

# Interactive book curation with AI assistance
haw curate-book curate              # Full interactive curation process

# Explore system capabilities
haw explore-themes                  # See what clustering tools are available
```

#### Automated Book Generation

##### **Advanced Book Generation (Recommended)**
Sophisticated semantic clustering with high-quality output:
```bash
# Generate high-quality books with advanced algorithms
haw advanced-books --min-quality 0.4 --max-books 3

# Analysis only (preview without generating files)
haw advanced-books --analyze-only

# Custom quality threshold
haw advanced-books --min-quality 0.6 --max-books 2
```

##### **Universal Book Generator**
General-purpose generator that works with any content source:
```bash
# From notebook transcripts (default)
haw universal-books --source-type notebooks --min-quality 0.4

# From any conversation type
haw universal-books --source-type conversations --gizmo-id g-XXXXX

# From files on disk
haw universal-books --source-type files --file-path /content/directory

# Custom configuration
haw universal-books --source-type notebooks --min-quality 0.5 --max-books 2
```

##### **Basic Book Factory**
Simple automated generation:
```bash
# Generate 7 books automatically
haw book-factory --quality-threshold 0.3

# Preview mode
haw book-factory --dry-run
```

##### **Complete Pipeline**
End-to-end automation with AI editorial refinement:
```bash
# Full automated pipeline
haw book-pipeline --quality-threshold 0.3

# Test the complete workflow
haw book-pipeline --dry-run
```

#### AI Editorial Assistant
```bash
# Refine generated books with AI analysis
haw book-editor                    # Process all books

# Edit specific book
haw book-editor --book filename.md

# View auto-refined versions and editorial recommendations
```

### 🧠 Embedding & Search
```bash
# Hierarchical embedding (test batches)
haw embed --limit 1000 --timeout 120

# Full archive embedding
haw embed-full --batch-size 50 --timeout 180

# Monitor embedding progress
haw monitor dashboard
haw monitor status
```

### 📊 Content Analysis
```bash
# Batch conversation quality assessment
haw assess --limit 1000

# Extract representative samples
haw sample --limit 50

# Generate archive word clouds
haw wordcloud --conversations 1000

# Content categorization
haw categorize --limit 1000
```

### 📁 Archive Management
```bash
# Archive CLI with semantic search
haw archive list
haw archive search "consciousness"
haw archive get 123456

# Embedding corpus management
haw embedding-cli

# Allegory engine CLI  
haw allegory

# Integrated processing CLI
haw integrated

# Attribute browser CLI
haw attribute
```

### 🔍 Metadata & Intelligence
```bash
# Interactive metadata browser
haw browse browse
haw browse overview
haw browse search --filters

# Explore semantic chunks and summaries
haw browse-chunks browse
haw browse-chunks explore conv_id
haw browse-chunks search term

# Intelligent content assessment
haw agentic assess gem_detection --min-quality 0.6
haw agentic results --filters

# Content transformation pipeline
haw pipeline process --min-quality 0.8
haw pipeline status

# Formal pipeline API management
haw pipeline-mgr rules list
haw pipeline-mgr execute --min-quality 0.8 --dry-run
```

### 🌐 API Services
```bash
# Start/stop API services
haw api start lighthouse-api
haw api stop archive-api
haw api restart lpe-api
haw api list                       # Show available services
```

### 🔄 Pipeline Management
```bash
# Run predefined pipelines
haw pipeline run full-analysis
haw pipeline run writing-profile
haw pipeline run gem-discovery
haw pipeline run content-transformation

# List and status
haw pipeline list
haw pipeline status
```

## 🔧 API Endpoints

### 🆕 Book Generation APIs
- `POST /api/books/generate` - Generate books from content
- `GET /api/books/themes` - Available book themes
- `POST /api/books/analyze` - Analyze content for book potential
- `GET /api/books/clusters` - Thematic clusters
- `POST /api/books/refine` - AI editorial refinement

### Narrative Analysis
- `POST /api/narrative-theory/analyze` - QNT analysis
- `GET /api/narrative-theory/semantic-dimensions` - POVM structure

### Gutenberg Integration  
- `GET /gutenberg/search` - Search books
- `POST /gutenberg/analyze` - Create analysis job
- `GET /gutenberg/jobs` - List jobs
- `GET /gutenberg/catalog/browse` - Browse catalog
- `GET /gutenberg/catalog/popular` - Popular books

### Attribute Management
- `POST /api/attributes/save` - Save attributes
- `GET /api/attributes/list` - List attributes
- `GET /api/attributes/{id}` - Get attribute details
- `DELETE /api/attributes/{id}` - Delete attribute
- `GET /api/attributes/stats` - Statistics
- `GET /api/attributes/algorithms/{name}` - Algorithm details

### Core Platform
- `GET /health` - Health check
- `GET /providers` - LLM provider status
- `POST /transform` - Text transformation
- `POST /maieutic/*` - Maieutic dialogue
- `POST /translation/*` - Translation analysis

## 🧬 Quantum Narrative Theory (QNT)

Our implementation of QNT provides comprehensive narrative analysis:

### Core Components

**🎭 Persona (Ψ)** - The subjective voice and perspective
- Archetype identification (wise elder, curious child, etc.)
- Voice characteristics and indicators
- Confidence scoring

**🌍 Namespace (Ω)** - Universe of discourse and cultural context
- Domain markers and vocabulary
- Cultural and temporal context
- Reality layer classification

**✍️ Style (Σ)** - Linguistic and rhetorical approach  
- Stylistic features and patterns
- Rhetorical devices and tone
- Linguistic complexity analysis

**💎 Essence (E)** - Invariant core meaning
- Distilled essential message
- Semantic density and coherence
- Transformation invariants

## 🆕 Advanced Book Generation System

### Sophisticated Semantic Analysis
The platform includes three levels of book generation sophistication:

#### **Level 1: Advanced Books** - Highest Quality
- **8-dimensional concept hierarchies** for philosophical analysis
- **Multi-dimensional quality scoring** (content + depth + concepts + complexity)
- **Intelligent content filtering** removes noise and irrelevant content
- **Unique chapter generation** with context-aware titles
- **Natural narrative progression** from simple to complex concepts

#### **Level 2: Universal Generator** - Maximum Flexibility  
- **Pluggable content extractors** for any data source
- **Customizable theme templates** for different domains
- **Configurable quality thresholds** and parameters
- **Multi-source compatibility** (databases, files, APIs)

#### **Level 3: Complete Pipeline** - Full Automation
- **End-to-end workflow** from raw content to refined books
- **AI editorial integration** with improvement recommendations
- **Production-ready output** with quality metrics
- **Batch processing** capabilities

### Content Sources Supported
- **Notebook Transcripts** - Handwritten insights from Journal Recognizer OCR
- **Conversation Archives** - Any conversation data with flexible filtering
- **File Systems** - Markdown, text files, and documents
- **Database Content** - Direct database integration with custom queries

### Quality Metrics & Analysis
- **Philosophical Depth Scoring** - Measures abstract thinking and fundamental questions
- **Concept Diversity Index** - Tracks variety of philosophical concepts
- **Thematic Coherence** - Measures how well content clusters around themes
- **Narrative Flow Assessment** - Evaluates logical progression through content
- **Complexity Progression** - Ensures natural learning curve in generated books

## 📊 Book Generation Examples

### Quick Start - Generate Books from Your Writing
```bash
# 1. Explore what content you have
haw explore-themes

# 2. Quick thematic analysis
haw curate-book analyze

# 3. Generate high-quality books
haw advanced-books --min-quality 0.4 --max-books 3

# 4. Refine with AI editor
haw book-editor
```

### Advanced Workflow
```bash
# 1. Extract and analyze your writing patterns
haw extract-writing extract --limit 2000

# 2. Run comprehensive content analysis
haw browse-writing summary

# 3. Generate books with custom parameters
haw universal-books --source-type notebooks --min-quality 0.5 --max-books 2

# 4. Complete pipeline with AI refinement
haw book-pipeline --quality-threshold 0.4
```

### Expected Output
The system generates publication-ready books with:
- **Sophisticated titles** and subtitles based on content analysis
- **Quality metrics** showing philosophical depth and coherence scores
- **Unique chapter structures** with meaningful progression
- **Editorial recommendations** for further improvement
- **Export formats** ready for publication (Markdown → PDF/ePub)

## 🔒 Security & Best Practices

- **Environment Isolation** - Separate lighthouse venv
- **Key Management** - Secure credential storage
- **Input Validation** - Comprehensive request validation
- **Rate Limiting** - API protection
- **Error Handling** - Graceful degradation
- **Logging** - Comprehensive audit trails
- **Content Privacy** - Local processing options with Ollama

## 🛠️ Development

### Dependencies
The platform requires additional dependencies for book generation:
```bash
# Core ML and NLP
pip install numpy scipy scikit-learn
pip install spacy transformers
python -m spacy download en_core_web_trf

# Database and processing
pip install psycopg2-binary sqlalchemy
pip install pandas matplotlib seaborn

# Advanced text processing
pip install nltk textstat
pip install sentence-transformers

# Content analysis
pip install wordcloud networkx
```

### Local Development
```bash
# Backend development
cd humanizer_api/lighthouse
source venv/bin/activate
python api_enhanced.py

# Test book generation
haw advanced-books --analyze-only

# Frontend development  
cd lighthouse-ui
npm run dev

# CLI development and testing
./haw status
./haw advanced-books --help
```

### Testing
```bash
# Test book generation system
haw advanced-books --analyze-only
haw universal-books --source-type files --file-path ./test_content

# API health checks
curl http://localhost:8100/health

# Full system test
haw status && echo "All systems operational"
```

## 📈 Performance & Scaling

- **Async Processing** - Non-blocking operations
- **Batch Jobs** - Efficient bulk processing  
- **Intelligent Caching** - Content analysis results cached
- **Semantic Embeddings** - Vector similarity for fast clustering
- **Progressive Quality Filtering** - Multi-stage content refinement
- **Memory Optimization** - Efficient handling of large content volumes

## 🔍 Troubleshooting

### Book Generation Issues
```bash
# Check content availability
haw browse-notebooks list

# Verify database connection
haw status

# Test with analysis-only mode
haw advanced-books --analyze-only

# Check quality thresholds
haw advanced-books --min-quality 0.2 --analyze-only
```

### Common Issues

**Environment Problems:**
```bash
# Always use lighthouse venv
cd humanizer_api/lighthouse
source venv/bin/activate
python --version  # Should be 3.11.11
```

**Missing NLP Models:**
```bash
# Install spaCy model
python -m spacy download en_core_web_trf

# Verify installation
python -c "import spacy; nlp = spacy.load('en_core_web_trf'); print('✅ spaCy model ready')"
```

**Database Connection Issues:**
```bash
# Test database connection
haw browse-notebooks list

# Check PostgreSQL status
pg_isready
```

## 🌟 Features Roadmap

### Book Generation Enhancements
- [ ] **Multi-language Book Generation** - Support for non-English content
- [ ] **Advanced Template System** - Custom book themes and structures
- [ ] **Collaborative Editing** - Multi-user book refinement
- [ ] **Publication Integration** - Direct export to ePub, PDF, print formats
- [ ] **Visual Content Integration** - Diagrams, charts, and illustrations
- [ ] **Cross-reference System** - Automatic linking between related concepts

### Core Platform
- [ ] **Neural Architecture Search** - Automated algorithm optimization
- [ ] **Real-time Collaboration** - Shared analysis sessions
- [ ] **Plugin System** - Custom algorithm extensions
- [ ] **Performance Analytics** - Algorithm efficiency metrics
- [ ] **Advanced Visualization** - Interactive content exploration
- [ ] **API Rate Limiting** - Enhanced security and usage controls

## 📚 Documentation

- **API Docs** - http://localhost:8100/docs (when running)
- **CLI Help** - `haw help` or `haw <command> --help`
- **Book Generation Guide** - See `COMPLETE_BOOK_GENERATION_SOLUTION.md`
- **QNT Theory** - See `narrative_theory.py` 
- **Test Examples** - See `qnt_test_dataset.py`

## 🎮 Complete Workflow Examples

### Discover and Transform Your Ideas into Books
```bash
# 1. System health check
haw status

# 2. Explore your existing content
haw explore-themes
haw browse-notebooks list

# 3. Quick thematic analysis
haw curate-book analyze

# 4. Generate high-quality books
haw advanced-books --min-quality 0.4 --max-books 3

# 5. Review and refine with AI
haw book-editor

# 6. Check the generated books
ls humanizer_api/lighthouse/advanced_books/
```

### Content Analysis Pipeline
```bash
# Extract writing patterns
haw extract-writing extract --limit 1000

# Analyze word frequency patterns  
haw browse-wordclouds browse

# Generate comprehensive word clouds
haw wordcloud --conversations 500

# Run quality assessment
haw assess --limit 1000

# Create thematic clusters
haw curate-book curate
```

### Full Archive Processing
```bash
# Complete archive analysis
haw pipeline run full-analysis

# Writing profile extraction
haw pipeline run writing-profile

# Gem discovery for publication
haw pipeline run gem-discovery

# Content transformation pipeline
haw pipeline run content-transformation
```

## 📄 License

[Your License Here]

## 🤝 Support

- **GitHub Issues** - Bug reports and feature requests
- **Documentation** - Comprehensive guides and examples
- **CLI Help** - `haw help` for complete command reference

---

**Built with ❤️ by the Humanizer Team**

*Combining quantum theory, classical literature, modern AI, and advanced book generation to create the future of content discovery and publication.*