# API to UI Functionality Mapping

## Overview
This document maps the comprehensive Lamish Projection Engine (LPE) API ecosystem to the current UI implementation, showing what's available, what's implemented, and what functionality exists only in the API.

## Current API Status
✅ **APIs Discovered:** 6 distinct FastAPI services
✅ **Total Endpoints:** 50+ endpoints
✅ **API Key Storage:** macOS Keychain integration active
✅ **Real-time Features:** WebSocket support for live updates
✅ **Batch Processing:** Multiple batch endpoints available

## API Ecosystem Overview

### 1. **Enhanced Lighthouse API** (Primary - Port 8100)
**Base URL:** `http://127.0.0.1:8100`
**Status:** ✅ Active and fully functional

#### **Core Transformation Engine**
| Endpoint | Method | UI Implementation | Status |
|----------|--------|------------------|---------|
| `/health` | GET | ✅ Used in API Console | Available for testing |
| `/models` | GET | ✅ Header model selector | Fully implemented |
| `/configurations` | GET | ✅ All transform controls | Fully implemented |
| `/transform` | POST | ✅ Transform tab + Simple tab | Fully implemented |

#### **LLM Configuration & Security**
| Endpoint | Method | UI Implementation | Status |
|----------|--------|------------------|---------|
| `/api/llm/configurations` | GET/POST | ✅ LLM Config tab | Fully implemented |
| `/api/llm/status` | GET | ✅ Provider status display | Shows current keys |
| `/api/llm/keys/{provider}` | POST/DELETE | ✅ Key management UI | macOS Keychain active |
| `/api/llm/test/{provider}` | POST | ✅ Real-time testing | Works with stored keys |

**Current Key Status:**
- ✅ OpenAI: Valid key stored
- ✅ Anthropic: Valid key stored  
- ✅ Google: Valid key stored
- ✅ Hugging Face: Valid key stored
- ⚠️ Groq: Key stored but invalid (401 error)
- ❌ Together, Replicate, Cohere, Mistral: No keys stored
- ❌ Ollama: Module import error

#### **Maieutic Dialogue (Socratic Questioning)**
| Endpoint | Method | UI Implementation | Status |
|----------|--------|------------------|---------|
| `/maieutic/start` | POST | ✅ Maieutic tab | Fully implemented |
| `/maieutic/question` | POST | ✅ Interactive dialogue | Available in UI |
| `/maieutic/answer` | POST | ✅ Response handling | Available in UI |
| `/maieutic/complete` | POST | ✅ Session completion | Available in UI |
| `/ws/maieutic/{session_id}` | WebSocket | ✅ Real-time updates | Live functionality |

#### **Translation & Analysis**
| Endpoint | Method | UI Implementation | Status |
|----------|--------|------------------|---------|
| `/translation/roundtrip` | POST | ✅ Translation tab | Fully implemented |
| `/translation/stability` | POST | ✅ Multi-language analysis | Available in UI |

#### **Vision & Image Processing**
| Endpoint | Method | UI Implementation | Status |
|----------|--------|------------------|---------|
| `/vision/analyze` | POST | ✅ Vision tab | Fully implemented |
| `/vision/transcribe` | POST | ✅ Handwriting recognition | Available in UI |
| `/vision/redraw` | POST | ❌ Not in UI | **API ONLY** |
| `/image/generate` | POST | ❌ Not in UI | **API ONLY** |

#### **Knowledge Base & Analysis**
| Endpoint | Method | UI Implementation | Status |
|----------|--------|------------------|---------|
| `/lamish/analyze` | POST | ✅ Lamish tab | Fully implemented |
| `/lamish/concepts` | GET/POST/DELETE | ✅ Unified manager | CRUD operations |
| `/lamish/stats` | GET | ✅ Dashboard stats | Real-time metrics |
| `/lamish/extract-attributes` | POST | ✅ Attribute extraction | Available |
| `/lamish/inspect-prompts` | POST | ✅ Pipeline inspector | Debug interface |
| `/lamish/save-prompts` | POST | ❌ Not in UI | **API ONLY** |
| `/lamish/sync-system` | POST | ❌ Not in UI | **API ONLY** |

### 2. **Archive API** (Port 8080)
**Status:** 🔶 Available but not integrated in UI

| Endpoint | Method | UI Implementation | Status |
|----------|--------|------------------|---------|
| `/ingest` | POST | ❌ Not in UI | **API ONLY** |
| `/search` | POST | ❌ Not in UI | **API ONLY** |
| `/content/{id}` | GET/DELETE | ❌ Not in UI | **API ONLY** |
| `/sources` | GET | ❌ Not in UI | **API ONLY** |
| `/stats` | GET | ❌ Not in UI | **API ONLY** |

### 3. **LPE API** (Port 8081)
**Status:** 🔶 Available but not integrated in UI

| Endpoint | Method | UI Implementation | Status |
|----------|--------|------------------|---------|
| `/process` | POST | ❌ Not in UI | **API ONLY** |
| `/batch` | POST | ⚠️ Custom implementation | **Batch tab uses different approach** |
| `/processors` | GET | ❌ Not in UI | **API ONLY** |
| `/sessions` | GET | ❌ Not in UI | **API ONLY** |

### 4. **Lawyer API** (Port 8082)
**Status:** 🔶 Available but not integrated in UI

| Endpoint | Method | UI Implementation | Status |
|----------|--------|------------------|---------|
| `/assess` | POST | ❌ Not in UI | **API ONLY** |
| `/batch-assess` | POST | ❌ Not in UI | **API ONLY** |
| `/assessments` | GET | ❌ Not in UI | **API ONLY** |

## UI Tab Functionality

### ✅ **Fully Implemented Tabs**

#### **Simple Tab**
- Clean interface based on `/Users/tem/lpe_dev` style
- Archive system with narrative history
- Meaning vectors visualization
- Optimal expression suggestions
- **API Integration:** Uses `/transform`, `/configurations`

#### **Transform Tab**
- Complete 5-step LPE pipeline
- Real-time progress via WebSocket
- Transformation controls (persona/namespace/style)
- Step-by-step visualization
- Diff view for before/after comparison
- **API Integration:** Uses `/transform`, `/ws/transform/{id}`

#### **Lamish Tab**
- Unified Attribute Manager
- Master list of personas, namespaces, styles
- Quick processing widget
- System integration tracking
- **API Integration:** Uses `/lamish/*` endpoints

#### **LLM Config Tab**
- 11 LLM providers supported
- macOS Keychain security integration
- Per-task configuration
- Real-time API key testing
- Provider status monitoring
- **API Integration:** Uses `/api/llm/*` endpoints

#### **Batch Tab**
- Multi-narrative processing
- Transform, analyze, maieutic, translation modes
- Progress tracking with live updates
- Results export functionality
- Archive narrative selection
- **API Integration:** Uses `/transform`, `/lamish/analyze`, `/maieutic/start`

#### **API Console Tab**
- Interactive endpoint testing
- Live session logging
- Request/response inspection
- 50+ endpoint support
- Real-time execution tracking
- Export logs functionality
- **API Integration:** Direct testing of all endpoints

#### **Maieutic Tab**
- Socratic questioning interface
- Session management
- Real-time dialogue via WebSocket
- Insight generation and auto-configuration
- **API Integration:** Uses `/maieutic/*`, `/ws/maieutic/{id}`

#### **Translation Tab**
- Round-trip translation analysis
- Multi-language stability testing
- Cross-domain translation
- **API Integration:** Uses `/translation/*` endpoints

#### **Vision Tab**
- Image analysis with multiple models
- Handwriting transcription
- Comprehensive visual analysis
- **API Integration:** Uses `/vision/*` endpoints

## Missing UI Features (API-Only Functionality)

### 🔶 **Available in API but NOT in UI:**

#### **Image Generation**
- **Endpoint:** `POST /image/generate`
- **Capability:** OpenAI DALL-E integration
- **Status:** Fully functional API, no UI

#### **Archive Management**
- **Endpoints:** Archive API (Port 8080)
- **Capabilities:** Universal content ingestion, semantic search
- **Status:** Complete API ecosystem, no UI integration

#### **Advanced LPE Processing**
- **Endpoints:** LPE API (Port 8081)
- **Capabilities:** Multi-engine processing, session management
- **Status:** Sophisticated API, basic batch UI only

#### **Content Quality Assessment**
- **Endpoints:** Lawyer API (Port 8082)
- **Capabilities:** Content quality assessment, style review
- **Status:** Full assessment API, no UI

#### **Prompt Template Management**
- **Endpoints:** `/lamish/save-prompts`, `/lamish/sync-system`
- **Capabilities:** Save custom prompts, sync system attributes
- **Status:** API available, not exposed in UI

#### **Advanced Vision Features**
- **Endpoint:** `/vision/redraw`
- **Capability:** Artistic analysis for reinterpretation
- **Status:** API available, not in Vision tab

## Recommendations

### 🎯 **High Priority UI Additions:**

1. **Archive Integration Tab**
   - Connect to Archive API for content management
   - Semantic search interface
   - Content source management

2. **Image Generation Interface**
   - Add to Vision tab or create new tab
   - DALL-E integration with stored OpenAI key

3. **Quality Assessment Tab**
   - Connect to Lawyer API
   - Batch quality assessment
   - Style review interface

4. **Advanced Prompt Management**
   - Template editor in Lamish tab
   - Custom prompt saving/loading
   - System synchronization controls

### 🔧 **Medium Priority Enhancements:**

1. **Enhanced Batch Processing**
   - Connect to LPE API for advanced processing
   - Session management
   - Multi-engine pipeline support

2. **Archive Search Integration**
   - Add semantic search to existing tabs
   - Content discovery features
   - Cross-reference capabilities

3. **Advanced Configuration**
   - Provider switching per operation
   - Model selection granularity
   - Performance optimization settings

## Current System Health

### ✅ **Working Systems:**
- Enhanced Lighthouse API (Primary)
- macOS Keychain integration
- WebSocket real-time features
- 4/11 LLM providers with valid keys
- All major transformation pipelines
- Complete UI navigation

### ⚠️ **Issues to Address:**
- Groq API key invalid (401 error)
- Ollama module import error
- 4 providers need API keys (Together, Replicate, Cohere, Mistral)
- Archive API not integrated
- LPE API underutilized
- Lawyer API not exposed

### 🚀 **Next Steps:**
1. Fix Groq and Ollama connectivity
2. Add missing provider API keys
3. Integrate Archive API for content management
4. Add image generation interface
5. Implement quality assessment features
6. Enhance batch processing with LPE API

The system represents a remarkably comprehensive content transformation ecosystem with most functionality already exposed through an intuitive UI. The API-only features represent opportunities for future enhancement rather than missing core functionality.