# 🏗️ Complete Archive System Setup Guide

## 🎯 Overview

This guide will help you set up the complete Humanizer Archive system with:

- ✅ **PostgreSQL + pgvector** for 768-dimensional vector storage
- ✅ **Ollama + nomic-text-embed** for local embeddings  
- ✅ **Smart Archive Processing** with activity-aware prioritization
- ✅ **Real-time Progress Tracking** that persists across page refreshes
- ✅ **Beautiful Archive UI** with semantic search capabilities

## 🚀 Quick Start (Automated)

### Option 1: Complete Setup Script

```bash
# Run the complete setup (handles everything automatically)
python3 setup_complete_archive.py

# Start the system
./start_archive_system.sh
```

### Option 2: Manual Setup

If you prefer to set up components manually:

## 📋 Prerequisites

### 1. Install PostgreSQL
```bash
# macOS
brew install postgresql
brew services start postgresql

# Ubuntu
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

### 2. Install pgvector Extension
```bash
# macOS
brew install pgvector

# Ubuntu  
sudo apt install postgresql-15-pgvector

# Test installation
psql -d postgres -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

### 3. Install Ollama
```bash
# macOS
brew install ollama

# Linux - visit https://ollama.ai/download
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama
ollama serve
```

### 4. Pull Embedding Model
```bash
# Pull the nomic-text-embed model (768 dimensions)
ollama pull nomic-embed-text
```

### 5. Install Python Dependencies
```bash
pip3 install pgvector asyncpg httpx sentence-transformers numpy tiktoken fastapi uvicorn
```

### 6. Install UI Dependencies
```bash
cd lighthouse-ui
npm install
```

## 🎛️ Manual System Startup

### 1. Create Database
```bash
createdb humanizer_archive
psql -d humanizer_archive -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

### 2. Start Archive API
```bash
cd humanizer_api/src
python3 archive_api_enhanced.py
```

### 3. Start Lighthouse UI
```bash
cd lighthouse-ui
npm run dev
```

## 🎨 Using the Archive System

### 1. Access the Archive Tab

1. Open **http://localhost:3100** in your browser
2. Click the **"Archive"** tab
3. You'll see the Archive Explorer interface

### 2. Import Your Node Archive

1. Click **"Start Import"** button
2. Watch the **real-time progress** with step-by-step visualization:
   - 📊 **Analyze Archive Activity** - Prioritizes by recency and engagement
   - 📥 **Import Conversations** - Processes 1923 conversations
   - 🧩 **Generate Chunks** - Creates 240-word chunks with overlaps
   - 🧠 **Create Embeddings** - Generates 768-dim vectors via Ollama
   - ✅ **Finalize** - Cleanup and indexing

### 3. Progress Tracking Features

- **Persistent Progress**: Survives page refreshes and browser restarts
- **Real-time Updates**: WebSocket-powered live progress
- **Step Visualization**: See each phase with progress bars
- **Statistics**: Live counts of processed conversations, chunks, embeddings
- **Time Estimates**: Estimated completion time based on current progress
- **Activity Breakdown**: Shows today/week/month/older distribution

### 4. Search Your Archive

Once imported, you can:

- **Text Search**: Traditional full-text search across all content
- **Semantic Search**: Toggle to enable AI-powered similarity matching
- **Activity Filters**: Filter by today/this week/this month
- **Conversation Threading**: View complete conversation threads
- **Multi-level Matching**: Search across chunks, sections, and documents

## 🔧 System Architecture

```
┌─────────────────────┐    WebSocket     ┌─────────────────────┐
│   Lighthouse UI     │ ←──────────────→ │   Archive API       │
│   (localhost:3100)  │                  │   (localhost:7200)  │
│                     │                  │                     │
│ • Archive Tab       │     HTTP/REST    │ • Smart Processing  │
│ • Real-time Progress│ ←──────────────→ │ • Progress Tracking │
│ • Search Interface  │                  │ • WebSocket Server  │
└─────────────────────┘                  └─────────────────────┘
                                                      │
                                                      ▼
┌─────────────────────┐                  ┌─────────────────────┐
│   PostgreSQL        │ ←──────────────→ │   Ollama            │
│   (localhost:5432)  │                  │   (localhost:11434) │
│                     │                  │                     │
│ • pgvector          │                  │ • nomic-text-embed  │
│ • Full-text Search  │                  │ • 768-dim Vectors   │
│ • Archive Tables    │                  │ • Local Processing  │
└─────────────────────┘                  └─────────────────────┘
```

## 📊 What Gets Processed

From your **1923 Node Archive conversations**:

### Import Process
1. **Activity Analysis**: 
   - Conversations categorized by recency (today → week → month → older)
   - Engagement scoring based on message count, vocabulary richness, participants
   - Priority queue creation for smart processing order

2. **Content Processing**:
   - **240-word chunks** with **50-word overlaps** for granular search
   - **3-level hierarchical summaries** for big picture semantic matching
   - **768-dimensional embeddings** using nomic-text-embed via Ollama

3. **Database Storage**:
   - PostgreSQL with pgvector for efficient similarity search
   - Full-text search indexes for traditional keyword search
   - Conversation threading preservation

### Search Capabilities
- **Semantic Search**: Find conceptually similar content across all conversations
- **Traditional Search**: Keyword-based search with ranking
- **Activity-Aware Results**: Recent conversations boosted in relevance
- **Multi-Granularity**: Search at chunk, section, and document levels

## 🛠️ Troubleshooting

### Common Issues

1. **PostgreSQL not starting**
   ```bash
   # macOS
   brew services restart postgresql
   
   # Linux
   sudo systemctl restart postgresql
   ```

2. **pgvector not found**
   ```bash
   # Check if extension exists
   psql -d postgres -c "SELECT * FROM pg_available_extensions WHERE name='vector';"
   
   # Install if missing (see Prerequisites)
   ```

3. **Ollama model not found**
   ```bash
   # Check available models
   ollama list
   
   # Pull if missing
   ollama pull nomic-embed-text
   ```

4. **API not responding**
   ```bash
   # Check if services are running
   curl http://localhost:7200/health
   curl http://localhost:3100
   
   # Check logs
   tail -f archive_api.log
   tail -f lighthouse_ui.log
   ```

### Service Management

```bash
# Start everything
./start_archive_system.sh

# Stop everything  
./stop_archive_system.sh

# Check status
curl http://localhost:7200/health
curl http://localhost:7200/progress/sessions
```

## 📈 Performance Expectations

Based on your **1923 conversations**:

- **Analysis Phase**: ~30 seconds
- **Import Phase**: ~5-10 minutes (depends on conversation size)
- **Chunking Phase**: ~2-5 minutes  
- **Embedding Phase**: ~10-20 minutes (depends on Ollama performance)
- **Total Time**: ~20-35 minutes for complete processing

**Progress Tracking** provides real-time estimates based on actual processing speed.

## 🎯 Next Steps After Setup

1. **Start with Small Test**: Use `max_conversations=10` for initial testing
2. **Monitor Progress**: Watch the real-time progress updates
3. **Explore Search**: Try both text and semantic search modes
4. **Activity Filtering**: Explore today/week/month filters
5. **Full Processing**: Process all 1923 conversations

## 🔒 Privacy & Security

- **Local Processing**: All embeddings generated locally via Ollama
- **No Data Sent**: Your conversations never leave your machine
- **PostgreSQL**: Local database storage only
- **Open Source**: All components are open source

## 🎉 Success Indicators

You'll know everything is working when:

1. ✅ Archive API responds at http://localhost:7200/health
2. ✅ Lighthouse UI loads at http://localhost:3100  
3. ✅ Archive tab shows embedding system panel
4. ✅ "Start Import" button initiates progress tracking
5. ✅ Real-time progress updates show in the UI
6. ✅ Search returns results from your imported conversations

---

## 🚀 Ready to Explore Your Archive!

Your 1923 Node Archive conversations will be fully searchable with both traditional keyword search and AI-powered semantic similarity. The system prioritizes recent activity while making everything accessible through multiple search modalities.

**Happy Exploring!** 🎯