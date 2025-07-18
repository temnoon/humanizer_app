# Humanizer Lighthouse - Full-Stack LLM Content Transformation Platform

A comprehensive content transformation platform with React frontend and FastAPI backend, featuring the Lamish Projection Engine (LPE) for narrative transformation, multi-provider LLM support, and real-time processing.

## 🏗️ Project Structure

```
humanizer-lighthouse/
├── humanizer_api/           # 🐍 Python Backend (FastAPI)
│   ├── lighthouse/          # Main API with full LPE features
│   │   ├── venv/           # Python 3.11.11 virtual environment ⚠️ USE THIS
│   │   ├── api_enhanced.py # Enhanced Lighthouse API (main server)
│   │   └── requirements.txt
│   ├── src/                # Additional API services
│   └── venv/               # ❌ Legacy venv (path issues)
│
├── lighthouse-ui/          # ⚛️ React Frontend (Vite)
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── SimpleTransformApp.jsx  # Clean simple interface
│   │   └── App.jsx         # Main application with all tabs
│   ├── package.json
│   └── vite.config.js      # Proxy configuration
│
└── README.md               # This file
```

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.11+ 
- Node.js 16+
- npm or yarn

### 1. Start Backend (Port 8100)
```bash
cd humanizer_api/lighthouse
source venv/bin/activate              # ⚠️ CRITICAL: Use lighthouse/venv
python api_enhanced.py
```

**Expected Output:**
```
INFO: Started server process [XXXXX]
INFO: Enhanced Lighthouse API with full LPE features
INFO: Using LLM provider: OllamaProvider
INFO: Uvicorn running on http://127.0.0.1:8100
```

### 2. Start Frontend (Port 3100/3101)
```bash
cd lighthouse-ui
npm install                            # First time only
npm run dev
```

**Expected Output:**
```
VITE v5.4.19 ready in XXXms
➜ Local: http://127.0.0.1:3100/       # Or 3101 if 3100 is busy
```

### 3. Access Application
- **Frontend UI**: http://127.0.0.1:3100 (or 3101)
- **Backend API**: http://127.0.0.1:8100
- **API Docs**: http://127.0.0.1:8100/docs

## 🛑 Shutdown Procedures

### Stop Frontend
- Press `Ctrl+C` in the terminal running `npm run dev`

### Stop Backend  
- Press `Ctrl+C` in the terminal running `python api_enhanced.py`

### Force Kill (if needed)
```bash
# Kill backend on port 8100
lsof -ti:8100 | xargs kill -9

# Kill frontend on port 3100/3101  
lsof -ti:3100 | xargs kill -9
lsof -ti:3101 | xargs kill -9
```

## 🎯 Key Features

### Frontend Tabs
- **Simple**: Clean interface with archive and meaning vectors
- **Transform**: 5-step LPE pipeline with real-time progress
- **Lamish**: Unified attribute management (personas, namespaces, styles)
- **LLM Config**: 11+ provider configuration with secure key management
- **Batch**: Multi-narrative processing with progress tracking
- **API Console**: Live endpoint testing with session logging
- **Maieutic**: Socratic questioning interface
- **Translation**: Cross-language analysis
- **Vision**: Image analysis and transcription

### Backend Capabilities
- **50+ API Endpoints** across multiple services
- **11 LLM Providers**: OpenAI, Anthropic, Google, Ollama, Groq, etc.
- **macOS Keychain Integration** for secure API key storage
- **WebSocket Support** for real-time updates
- **Batch Processing** for multiple narratives
- **Vector Database** with ChromaDB
- **Content Archive** with semantic search

## 🔧 Environment Setup

### Python Environment (Backend)
**CRITICAL**: Use the lighthouse venv, not the root venv!

```bash
cd humanizer_api/lighthouse
source venv/bin/activate
python --version  # Should show Python 3.11.11
pip list | grep fastapi  # Should show fastapi 0.116.1
```

### Node Environment (Frontend)
```bash
cd lighthouse-ui  
node --version  # Should be 16+
npm --version
```

## 🔑 LLM Configuration

The system supports multiple LLM providers with secure key storage:

### Working Providers (Keys Already Configured)
- ✅ **OpenAI**: Valid key, GPT-4 models available
- ✅ **Anthropic**: Valid key, Claude models available  
- ✅ **Google**: Valid key, Gemini models available
- ✅ **Hugging Face**: Valid key, transformers available

### Providers Needing Setup
- ⚠️ **Groq**: Key stored but invalid (401 error)
- ❌ **Ollama**: Connection issues (module import error)
- ❌ **Together, Replicate, Cohere, Mistral**: No keys stored

### Add API Keys
Use the LLM Config tab in the UI or API endpoints:
```bash
curl -X POST "http://127.0.0.1:8100/api/llm/keys/openai" \
  -H "Content-Type: application/json" \
  -d '{"api_key": "your-key-here"}'
```

## 🚨 Common Issues & Solutions

### Backend Won't Start
1. **Wrong Python Environment**
   ```bash
   # ❌ Wrong: using root venv or system Python
   source venv/bin/activate  # from root directory
   
   # ✅ Correct: using lighthouse venv  
   cd lighthouse && source venv/bin/activate
   ```

2. **Missing Dependencies**
   ```bash
   cd lighthouse && source venv/bin/activate
   pip install fastapi uvicorn pydantic httpx
   ```

3. **Port Already in Use**
   ```bash
   lsof -ti:8100 | xargs kill -9  # Kill existing process
   ```

### Frontend Won't Connect
1. **Backend Not Running**: Start backend first
2. **Wrong Port**: Check if frontend is on 3100 or 3101
3. **Proxy Issues**: Backend must be on port 8100

### SSL/Certificate Errors
- Usually indicates wrong Python environment
- Use the lighthouse venv with Python 3.11.11

## 📋 Development Workflow

### Daily Startup
```bash
# Terminal 1: Backend
cd humanizer_api/lighthouse
source venv/bin/activate
python api_enhanced.py

# Terminal 2: Frontend  
cd lighthouse-ui
npm run dev
```

### Testing Changes
- **Backend**: Changes require restart (`Ctrl+C` + `python api_enhanced.py`)
- **Frontend**: Hot reload automatic with Vite

### Adding New Features
1. **Backend**: Add endpoints to `api_enhanced.py`
2. **Frontend**: Add components to `src/components/`
3. **Integration**: Update proxy in `vite.config.js` if needed

## 📦 For Claude Code Assistants

### Critical Information
- **Always use** `humanizer_api/lighthouse/venv` (Python 3.11.11)
- **Never use** `humanizer_api/venv` (has path issues)
- **Backend runs on** port 8100 (fixed)
- **Frontend runs on** port 3100/3101 (auto-assigned)
- **Proxy configured** in `vite.config.js` to connect frontend→backend

### Quick Commands
```bash
# Check if services are running
curl http://127.0.0.1:8100/health    # Backend health
curl http://127.0.0.1:3100/           # Frontend (or 3101)

# Check Python environment  
cd humanizer_api/lighthouse && source venv/bin/activate && python --version

# Emergency restart
pkill -f "python api_enhanced.py" && pkill -f "npm run dev"
```

### Project Status
- ✅ **Full-featured backend** with 50+ endpoints
- ✅ **Complete React frontend** with 9 functional tabs  
- ✅ **LLM integration** with 4 working providers
- ✅ **Real-time features** via WebSockets
- ✅ **Secure key management** via macOS Keychain
- ✅ **Batch processing** for multiple narratives
- ✅ **API testing console** with live logging

---

## 🆘 Emergency Contacts
If you encounter issues:
1. Check this README first
2. Verify you're using the correct Python environment
3. Ensure both services are running on correct ports
4. Check the console logs for specific error messages

**This is a production-ready, full-featured content transformation platform.** 🚀