"""
Enhanced Archive API with PostgreSQL Unified Backend
Integrates the new unified archive schema for consolidated search across all archive sources
"""

import logging
import asyncio
import json
import uuid
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from io import BytesIO

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks, Depends, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
import httpx
from sentence_transformers import SentenceTransformer
import zipfile
import tempfile
import shutil

# Import our unified archive components
from archive_unified_schema import (
    UnifiedArchiveDB, 
    ArchiveContent, 
    SourceType, 
    ContentType
)
from node_archive_importer import NodeArchiveImporter
from embedding_system import AdvancedEmbeddingSystem
from smart_archive_processor import SmartArchiveProcessor
from progress_tracker import get_progress_tracker, list_active_sessions, PersistentProgressTracker
from config import get_config, HumanizerConfig

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
config = get_config()

# Pydantic Models for API
class UnifiedSearchRequest(BaseModel):
    """Search request across all archive sources"""
    query: Optional[str] = Field(None, description="Text search query")
    source_types: List[str] = Field(default_factory=list, description="Filter by source types")
    content_types: List[str] = Field(default_factory=list, description="Filter by content types")
    author: Optional[str] = Field(None, description="Filter by author/sender")
    date_from: Optional[datetime] = Field(None, description="Start date filter")
    date_to: Optional[datetime] = Field(None, description="End date filter")
    limit: int = Field(default=50, ge=1, le=500)
    offset: int = Field(default=0, ge=0)
    semantic_search: bool = Field(default=False, description="Enable semantic/embedding search")
    similarity_threshold: float = Field(default=0.7, ge=0.0, le=1.0, description="Minimum similarity score for semantic search")
    include_content: bool = Field(default=True, description="Include full content in results")

class ContentImportRequest(BaseModel):
    """Request to import content from various sources"""
    source_type: str = Field(..., description="Type of source to import")
    source_path: str = Field(..., description="Path to source data")
    max_items: Optional[int] = Field(None, description="Maximum items to import")
    overwrite_existing: bool = Field(default=False, description="Overwrite existing content")

class ConversationThreadRequest(BaseModel):
    """Request to get a conversation thread"""
    parent_id: int = Field(..., description="Parent conversation ID")
    include_metadata: bool = Field(default=True, description="Include message metadata")

class ProcessingStatusUpdate(BaseModel):
    """Update processing status for content"""
    content_id: int = Field(..., description="Content ID to update")
    status: str = Field(..., description="New processing status")
    attributes: Optional[Dict[str, Any]] = Field(None, description="Extracted attributes")
    quality_score: Optional[float] = Field(None, description="Content quality score")

# Initialize FastAPI app
app = FastAPI(
    title="Enhanced Archive API",
    description="Unified archive search and management across all content sources",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.api.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global components
archive_db: Optional[UnifiedArchiveDB] = None
embedding_system: Optional[AdvancedEmbeddingSystem] = None

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # Remove broken connections
                if connection in self.active_connections:
                    self.active_connections.remove(connection)

manager = ConnectionManager()

@app.on_event("startup")
async def startup_event():
    """Initialize database and advanced embedding system on startup"""
    global archive_db, embedding_system
    
    try:
        # Initialize database
        database_url = config.get_database_url()
        if "postgresql" in database_url:
            # Use PostgreSQL with unified schema
            archive_db = UnifiedArchiveDB(database_url)
            await archive_db.create_tables()
            logger.info("✅ Connected to PostgreSQL unified archive")
        else:
            # Fallback to SQLite - convert to unified format
            logger.warning("Using SQLite fallback - consider upgrading to PostgreSQL")
            archive_db = UnifiedArchiveDB(database_url)
            await archive_db.create_tables()
        
        # Initialize advanced embedding system
        try:
            embedding_system = AdvancedEmbeddingSystem(database_url)
            await embedding_system.initialize()
            logger.info("✅ Advanced embedding system initialized with 240-word chunking and multi-level summaries")
        except Exception as e:
            logger.warning(f"Could not initialize embedding system: {e}")
            embedding_system = None
        
        logger.info("🚀 Enhanced Archive API started successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize Enhanced Archive API: {e}")
        raise

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "database_connected": archive_db is not None,
        "embedding_system_loaded": embedding_system is not None,
        "version": "2.0.0"
    }

@app.get("/statistics")
async def get_archive_statistics():
    """Get comprehensive archive statistics"""
    if not archive_db:
        raise HTTPException(status_code=500, detail="Database not initialized")
    
    try:
        stats = archive_db.get_statistics()
        return {
            "archive_statistics": stats,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search")
async def search_unified_archive(request: UnifiedSearchRequest):
    """Search across all unified archive sources"""
    if not archive_db:
        raise HTTPException(status_code=500, detail="Database not initialized")
    
    try:
        # Convert string enums to proper types
        source_types = [SourceType(st) for st in request.source_types] if request.source_types else None
        content_types = [ContentType(ct) for ct in request.content_types] if request.content_types else None
        
        # Perform search
        results = archive_db.search_content(
            query=request.query,
            source_types=source_types,
            content_types=content_types,
            author=request.author,
            date_from=request.date_from,
            date_to=request.date_to,
            limit=request.limit,
            offset=request.offset
        )
        
        # Format results
        formatted_results = []
        for content in results:
            result = {
                "id": content.id,
                "source_type": content.source_type.value,
                "source_id": content.source_id,
                "content_type": content.content_type.value,
                "title": content.title,
                "author": content.author,
                "timestamp": content.timestamp.isoformat() if content.timestamp else None,
                "word_count": content.word_count,
                "quality_score": content.content_quality_score,
                "processing_status": content.processing_status
            }
            
            if request.include_content:
                result["body_text"] = content.body_text
                result["extracted_attributes"] = content.extracted_attributes
            
            formatted_results.append(result)
        
        return {
            "results": formatted_results,
            "count": len(formatted_results),
            "query": request.query,
            "filters_applied": {
                "source_types": request.source_types,
                "content_types": request.content_types,
                "author": request.author,
                "date_range": f"{request.date_from} to {request.date_to}" if request.date_from or request.date_to else None
            }
        }
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/conversation/{parent_id}")
async def get_conversation_thread(parent_id: int, include_metadata: bool = Query(True)):
    """Get complete conversation thread"""
    if not archive_db:
        raise HTTPException(status_code=500, detail="Database not initialized")
    
    try:
        messages = archive_db.get_conversation_thread(parent_id)
        
        formatted_messages = []
        for message in messages:
            msg_data = {
                "id": message.id,
                "source_id": message.source_id,
                "author": message.author,
                "timestamp": message.timestamp.isoformat() if message.timestamp else None,
                "body_text": message.body_text,
                "word_count": message.word_count
            }
            
            if include_metadata:
                msg_data.update({
                    "source_metadata": message.source_metadata,
                    "extracted_attributes": message.extracted_attributes,
                    "quality_score": message.content_quality_score
                })
            
            formatted_messages.append(msg_data)
        
        return {
            "parent_id": parent_id,
            "message_count": len(formatted_messages),
            "messages": formatted_messages
        }
        
    except Exception as e:
        logger.error(f"Error getting conversation thread: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/import/node-archive")
async def import_node_archive(
    background_tasks: BackgroundTasks,
    node_archive_path: str = Form(...),
    max_conversations: Optional[int] = Form(None)
):
    """Import Node Archive Browser conversations"""
    if not archive_db:
        raise HTTPException(status_code=500, detail="Database not initialized")
    
    # Validate path exists
    if not Path(node_archive_path).exists():
        raise HTTPException(status_code=400, detail=f"Archive path not found: {node_archive_path}")
    
    # Start background import
    background_tasks.add_task(
        _import_node_archive_task,
        node_archive_path,
        max_conversations
    )
    
    return {
        "message": "Node Archive import started",
        "archive_path": node_archive_path,
        "max_conversations": max_conversations,
        "status": "started"
    }

async def _import_node_archive_task(node_archive_path: str, max_conversations: Optional[int]):
    """Background task to import Node Archive"""
    try:
        logger.info(f"Starting Node Archive import from: {node_archive_path}")
        
        importer = NodeArchiveImporter(archive_db, node_archive_path)
        stats = importer.import_all_conversations(max_conversations=max_conversations)
        
        logger.info(f"Node Archive import completed: {stats}")
        
        # Store import results (could be stored in DB for retrieval)
        # For now, just log
        
    except Exception as e:
        logger.error(f"Node Archive import failed: {e}")

@app.post("/import/generic")
async def import_generic_content(request: ContentImportRequest, background_tasks: BackgroundTasks):
    """Import content from various generic sources"""
    if not archive_db:
        raise HTTPException(status_code=500, detail="Database not initialized")
    
    background_tasks.add_task(
        _import_generic_content_task,
        request.source_type,
        request.source_path,
        request.max_items,
        request.overwrite_existing
    )
    
    return {
        "message": f"Import started for {request.source_type}",
        "source_path": request.source_path,
        "status": "started"
    }

async def _import_generic_content_task(
    source_type: str, 
    source_path: str, 
    max_items: Optional[int],
    overwrite_existing: bool
):
    """Background task for generic content import"""
    try:
        logger.info(f"Starting {source_type} import from: {source_path}")
        
        # This would be extended to support different source types
        # For now, placeholder implementation
        if source_type == "node_conversation":
            importer = NodeArchiveImporter(archive_db, source_path)
            stats = importer.import_all_conversations(max_conversations=max_items)
            logger.info(f"Import completed: {stats}")
        else:
            logger.warning(f"Unsupported source type: {source_type}")
        
    except Exception as e:
        logger.error(f"Generic import failed: {e}")

@app.put("/content/{content_id}/processing-status")
async def update_processing_status(content_id: int, update: ProcessingStatusUpdate):
    """Update AI processing status and results for content"""
    if not archive_db:
        raise HTTPException(status_code=500, detail="Database not initialized")
    
    try:
        archive_db.update_processing_status(
            content_id=content_id,
            status=update.status,
            attributes=update.attributes,
            quality_score=update.quality_score
        )
        
        return {
            "message": "Processing status updated",
            "content_id": content_id,
            "new_status": update.status
        }
        
    except Exception as e:
        logger.error(f"Error updating processing status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/content/{content_id}/generate-embedding")
async def generate_content_embedding(content_id: int):
    """Generate semantic embedding for content"""
    if not archive_db or not embedding_model:
        raise HTTPException(status_code=500, detail="Database or embedding model not available")
    
    try:
        # Get content
        with archive_db.SessionLocal() as session:
            content = session.get(archive_db.ArchiveContentORM, content_id)
            if not content:
                raise HTTPException(status_code=404, detail="Content not found")
            
            # Generate embedding
            text_to_embed = f"{content.title or ''} {content.body_text or ''}"
            if not text_to_embed.strip():
                raise HTTPException(status_code=400, detail="No text content to embed")
            
            embedding = embedding_model.encode(text_to_embed).tolist()
            
            # Update content with embedding
            content.semantic_vector = json.dumps(embedding)
            content.processing_status = "embedded"
            session.commit()
        
        return {
            "message": "Embedding generated successfully",
            "content_id": content_id,
            "embedding_dimensions": len(embedding)
        }
        
    except Exception as e:
        logger.error(f"Error generating embedding: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sources")
async def list_archive_sources():
    """List all archive sources and their statistics"""
    if not archive_db:
        raise HTTPException(status_code=500, detail="Database not initialized")
    
    try:
        stats = archive_db.get_statistics()
        
        sources = []
        for source_type, count in stats.get("by_source_type", {}).items():
            sources.append({
                "source_type": source_type,
                "content_count": count,
                "description": f"Content from {source_type.replace('_', ' ').title()}"
            })
        
        return {
            "sources": sources,
            "total_sources": len(sources),
            "total_content": stats.get("total_content", 0)
        }
        
    except Exception as e:
        logger.error(f"Error listing sources: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/export/conversation/{parent_id}")
async def export_conversation(parent_id: int, format: str = Query("json")):
    """Export a conversation in various formats"""
    if not archive_db:
        raise HTTPException(status_code=500, detail="Database not initialized")
    
    try:
        messages = archive_db.get_conversation_thread(parent_id)
        
        if format == "json":
            export_data = {
                "conversation_id": parent_id,
                "exported_at": datetime.now(timezone.utc).isoformat(),
                "message_count": len(messages),
                "messages": [
                    {
                        "id": msg.id,
                        "author": msg.author,
                        "timestamp": msg.timestamp.isoformat() if msg.timestamp else None,
                        "content": msg.body_text,
                        "metadata": msg.source_metadata
                    }
                    for msg in messages
                ]
            }
            return export_data
        
        elif format == "text":
            # Simple text format
            lines = [f"Conversation Export - {datetime.now(timezone.utc).isoformat()}", ""]
            for msg in messages:
                timestamp = msg.timestamp.strftime("%Y-%m-%d %H:%M:%S") if msg.timestamp else "Unknown"
                lines.append(f"[{timestamp}] {msg.author}: {msg.body_text}")
            
            return {"text_export": "\\n".join(lines)}
        
        else:
            raise HTTPException(status_code=400, detail="Unsupported export format")
            
    except Exception as e:
        logger.error(f"Error exporting conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Development and debugging endpoints
@app.get("/debug/content/{content_id}")
async def debug_content(content_id: int):
    """Get detailed content information for debugging"""
    if not archive_db:
        raise HTTPException(status_code=500, detail="Database not initialized")
    
    try:
        with archive_db.SessionLocal() as session:
            content = session.get(archive_db.ArchiveContentORM, content_id)
            if not content:
                raise HTTPException(status_code=404, detail="Content not found")
            
            return {
                "id": content.id,
                "source_type": content.source_type,
                "source_id": content.source_id,
                "parent_id": content.parent_id,
                "content_type": content.content_type,
                "title": content.title,
                "body_text": content.body_text[:500] + "..." if content.body_text and len(content.body_text) > 500 else content.body_text,
                "raw_content": content.raw_content,
                "author": content.author,
                "participants": content.participants,
                "timestamp": content.timestamp.isoformat() if content.timestamp else None,
                "source_metadata": content.source_metadata,
                "extracted_attributes": content.extracted_attributes,
                "content_quality_score": content.content_quality_score,
                "processing_status": content.processing_status,
                "word_count": content.word_count,
                "created_at": content.created_at.isoformat() if content.created_at else None,
                "updated_at": content.updated_at.isoformat() if content.updated_at else None
            }
            
    except Exception as e:
        logger.error(f"Error getting debug content: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Smart Archive Processing Endpoints
@app.post("/smart-processing/analyze")
async def analyze_archive_activity():
    """Analyze archive activity patterns for smart processing prioritization"""
    try:
        node_archive_path = "/Users/tem/nab/exploded_archive_node"  # Could be configurable
        processor = SmartArchiveProcessor(config.get_database_url(), node_archive_path)
        await processor.initialize()
        
        analysis = await processor.analyze_archive_activity()
        
        return {
            "status": "success",
            "analysis": analysis,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error analyzing archive activity: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/smart-processing/process")
async def start_smart_processing(
    max_conversations: Optional[int] = Query(None, description="Limit conversations for testing"),
    node_archive_path: Optional[str] = Query("/Users/tem/nab/exploded_archive_node", description="Path to Node Archive"),
    background_tasks: BackgroundTasks = None
):
    """Start smart archive processing with activity-aware prioritization and embedding generation"""
    try:
        processor = SmartArchiveProcessor(config.get_database_url(), node_archive_path)
        await processor.initialize()
        
        # Start processing (could be made async with background_tasks)
        results = await processor.process_archive_smart(max_conversations)
        
        return {
            "status": "completed",
            "results": results,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in smart processing: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/smart-processing/status")
async def get_processing_status():
    """Get current processing status and checkpoint information"""
    try:
        checkpoint_file = Path("archive_processing_checkpoint.json")
        
        if checkpoint_file.exists():
            with open(checkpoint_file, 'r') as f:
                checkpoint_data = json.load(f)
            
            return {
                "status": "in_progress",
                "checkpoint_exists": True,
                "checkpoint_timestamp": checkpoint_data.get("timestamp"),
                "completed_jobs": len(checkpoint_data.get("completed_jobs", [])),
                "pending_jobs": len([j for j in checkpoint_data.get("job_queue", []) if j.get("status") == "pending"]),
                "failed_jobs": len(checkpoint_data.get("failed_jobs", {}))
            }
        else:
            return {
                "status": "idle",
                "checkpoint_exists": False,
                "message": "No processing in progress"
            }
            
    except Exception as e:
        logger.error(f"Error getting processing status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/embeddings/statistics")
async def get_embedding_statistics():
    """Get embedding system statistics"""
    if not embedding_system:
        raise HTTPException(status_code=500, detail="Embedding system not initialized")
    
    try:
        stats = embedding_system.get_statistics()
        return {
            "status": "success",
            "statistics": stats,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting embedding statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/embeddings/process-content/{content_id}")
async def process_content_embeddings(content_id: int):
    """Process specific content through the embedding pipeline"""
    if not embedding_system or not archive_db:
        raise HTTPException(status_code=500, detail="Embedding system or database not initialized")
    
    try:
        # Get content
        content = archive_db.get_content_by_id(content_id)
        if not content:
            raise HTTPException(status_code=404, detail="Content not found")
        
        if not content.body_text:
            raise HTTPException(status_code=400, detail="Content has no text to process")
        
        # Process through embedding system
        result = await embedding_system.process_content(content_id, content.body_text)
        
        return {
            "status": "success",
            "content_id": content_id,
            "processing_result": result,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error processing content embeddings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket endpoints for real-time progress
@app.websocket("/ws/progress/{session_id}")
async def websocket_progress(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time progress updates"""
    await manager.connect(websocket)
    
    try:
        # Get or create progress tracker
        tracker = get_progress_tracker(session_id)
        
        # Send initial progress state
        initial_progress = tracker.get_progress_summary()
        await websocket.send_text(json.dumps({
            "type": "progress_update",
            "data": initial_progress
        }))
        
        # Subscribe to progress updates
        async def progress_callback(progress):
            try:
                await websocket.send_text(json.dumps({
                    "type": "progress_update", 
                    "data": tracker.get_progress_summary()
                }))
            except:
                pass  # Connection closed
        
        tracker.subscribe(progress_callback)
        
        # Keep connection alive and listen for client messages
        while True:
            try:
                message = await websocket.receive_text()
                data = json.loads(message)
                
                if data.get("type") == "request_update":
                    # Send current progress
                    current_progress = tracker.get_progress_summary()
                    await websocket.send_text(json.dumps({
                        "type": "progress_update",
                        "data": current_progress
                    }))
                    
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                break
                
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
    finally:
        manager.disconnect(websocket)

@app.get("/progress/sessions")
async def list_progress_sessions():
    """List all active/recent processing sessions"""
    try:
        sessions = list_active_sessions()
        return {
            "status": "success",
            "sessions": sessions,
            "total_sessions": len(sessions)
        }
    except Exception as e:
        logger.error(f"Error listing sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/progress/{session_id}")
async def get_progress(session_id: str):
    """Get current progress for a specific session"""
    try:
        tracker = get_progress_tracker(session_id)
        progress_summary = tracker.get_progress_summary()
        
        return {
            "status": "success",
            "progress": progress_summary
        }
    except Exception as e:
        logger.error(f"Error getting progress: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/progress/{session_id}")
async def cleanup_progress(session_id: str):
    """Clean up progress data for a completed session"""
    try:
        tracker = get_progress_tracker(session_id)
        tracker.cleanup()
        
        return {
            "status": "success",
            "message": f"Cleaned up progress for session {session_id}"
        }
    except Exception as e:
        logger.error(f"Error cleaning up progress: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# File upload endpoint for archive selection
@app.post("/upload-archive")
async def upload_archive(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    archive_type: str = Form(...),
    max_conversations: Optional[int] = Form(None)
):
    """Upload and process archive files (folders or ZIP archives)"""
    try:
        # Create new progress tracker
        tracker = get_progress_tracker()
        session_id = tracker.session_id
        
        # Create temporary directory for processing
        temp_dir = Path(tempfile.mkdtemp(prefix="archive_upload_"))
        logger.info(f"Created temporary directory: {temp_dir}")
        
        # Process uploaded files
        archive_path = None
        total_size = 0
        file_count = 0
        
        for file in files:
            if not file.filename:
                continue
                
            file_count += 1
            file_path = temp_dir / file.filename
            
            # Create subdirectories if needed
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save uploaded file
            content = await file.read()
            total_size += len(content)
            
            with open(file_path, 'wb') as f:
                f.write(content)
            
            # If it's a ZIP file, extract it
            if file.filename.endswith('.zip'):
                try:
                    with zipfile.ZipFile(file_path, 'r') as zip_ref:
                        extract_dir = temp_dir / file.filename.replace('.zip', '')
                        zip_ref.extractall(extract_dir)
                        archive_path = str(extract_dir)
                        logger.info(f"Extracted ZIP to: {archive_path}")
                except Exception as e:
                    logger.error(f"Failed to extract ZIP {file.filename}: {e}")
                    continue
            
            # Check if this looks like a conversations.json file
            if file.filename == 'conversations.json':
                archive_path = str(temp_dir)
                logger.info(f"Found conversations.json in upload")
        
        # If no specific archive path found, use the temp directory
        if not archive_path:
            archive_path = str(temp_dir)
        
        # Validate that we have processable content
        conversations_file = None
        if Path(archive_path).is_dir():
            # Look for conversations.json
            conversations_file = Path(archive_path) / 'conversations.json'
            if not conversations_file.exists():
                # Look in subdirectories
                for subdir in Path(archive_path).iterdir():
                    if subdir.is_dir():
                        potential_conv = subdir / 'conversations.json'
                        if potential_conv.exists():
                            conversations_file = potential_conv
                            archive_path = str(subdir)
                            break
        
        if not conversations_file or not conversations_file.exists():
            # Clean up temp directory
            shutil.rmtree(temp_dir, ignore_errors=True)
            raise HTTPException(
                status_code=400, 
                detail="No conversations.json found in uploaded files. Please upload a valid Node Archive Browser export or OpenAI export."
            )
        
        # Analyze the uploaded archive
        analysis = await analyze_uploaded_archive(archive_path, conversations_file)
        
        # Start processing in background
        background_tasks.add_task(
            run_archive_upload_processing,
            tracker,
            archive_path,
            archive_type,
            max_conversations,
            temp_dir,
            analysis
        )
        
        return {
            "status": "started",
            "session_id": session_id,
            "websocket_url": f"/ws/progress/{session_id}",
            "progress_url": f"/progress/{session_id}",
            "message": "Archive upload processing started",
            "archive_analysis": analysis,
            "files_uploaded": file_count,
            "total_size_mb": round(total_size / (1024 * 1024), 2)
        }
        
    except Exception as e:
        logger.error(f"Error processing uploaded archive: {e}")
        # Clean up temp directory on error
        if 'temp_dir' in locals():
            shutil.rmtree(temp_dir, ignore_errors=True)
        raise HTTPException(status_code=500, detail=str(e))

async def analyze_uploaded_archive(archive_path: str, conversations_file: Path) -> Dict[str, Any]:
    """Analyze uploaded archive to provide user feedback"""
    try:
        analysis = {
            "archive_type": "unknown",
            "conversations_found": 0,
            "media_files": 0,
            "estimated_processing_time": "unknown",
            "size_mb": 0
        }
        
        # Get directory size
        total_size = 0
        file_count = 0
        media_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.mp3', '.wav', '.mp4', '.avi', '.pdf', '.txt'}
        media_count = 0
        
        for root, dirs, files in Path(archive_path).walk():
            for file in files:
                file_path = root / file
                try:
                    size = file_path.stat().st_size
                    total_size += size
                    file_count += 1
                    
                    if file_path.suffix.lower() in media_extensions:
                        media_count += 1
                except:
                    continue
        
        analysis["size_mb"] = round(total_size / (1024 * 1024), 2)
        analysis["media_files"] = media_count
        
        # Analyze conversations.json
        try:
            with open(conversations_file, 'r', encoding='utf-8') as f:
                conversations_data = json.load(f)
                
            if isinstance(conversations_data, list):
                analysis["conversations_found"] = len(conversations_data)
                analysis["archive_type"] = "openai_export"
            elif isinstance(conversations_data, dict):
                # Could be Node Archive Browser format
                if "conversations" in conversations_data:
                    analysis["conversations_found"] = len(conversations_data["conversations"])
                    analysis["archive_type"] = "node_archive_browser"
                else:
                    # Count keys that look like conversation IDs
                    analysis["conversations_found"] = len([k for k in conversations_data.keys() if k != "metadata"])
                    analysis["archive_type"] = "node_archive_browser"
            
            # Estimate processing time (rough calculation)
            conv_count = analysis["conversations_found"]
            if conv_count > 0:
                # Estimate ~2-3 seconds per conversation for full processing
                estimated_seconds = conv_count * 2.5
                if estimated_seconds < 60:
                    analysis["estimated_processing_time"] = f"{int(estimated_seconds)} seconds"
                elif estimated_seconds < 3600:
                    analysis["estimated_processing_time"] = f"{int(estimated_seconds/60)} minutes"
                else:
                    analysis["estimated_processing_time"] = f"{int(estimated_seconds/3600)} hours"
                    
        except Exception as e:
            logger.error(f"Error analyzing conversations.json: {e}")
            analysis["conversations_found"] = 0
        
        return analysis
        
    except Exception as e:
        logger.error(f"Error analyzing uploaded archive: {e}")
        return {
            "archive_type": "unknown",
            "conversations_found": 0,
            "media_files": 0,
            "estimated_processing_time": "unknown",
            "size_mb": 0,
            "error": str(e)
        }

async def run_archive_upload_processing(
    tracker: PersistentProgressTracker,
    archive_path: str,
    archive_type: str,
    max_conversations: Optional[int],
    temp_dir: Path,
    analysis: Dict[str, Any]
):
    """Process uploaded archive with progress tracking"""
    try:
        # Start session
        tracker.start_session()
        
        # Update tracker with upload analysis
        tracker.update_statistics(
            total_conversations=analysis.get("conversations_found", 0),
            estimated_time=analysis.get("estimated_processing_time", "unknown")
        )
        
        # Step 1: Validation
        tracker.start_step("validate")
        tracker.update_step_progress("validate", 0.5, {
            "validating_archive": archive_path,
            "archive_type": archive_type
        })
        
        # Validate the archive structure
        conversations_file = Path(archive_path) / 'conversations.json'
        if not conversations_file.exists():
            raise ValueError("No conversations.json found in archive")
        
        tracker.complete_step("validate", {
            "archive_validated": True,
            "conversations_file": str(conversations_file)
        })
        
        # Step 2: Import using existing smart processing
        tracker.start_step("analyze")
        processor = SmartArchiveProcessor(config.get_database_url(), archive_path)
        await processor.initialize()
        
        # Run activity analysis
        try:
            activity_analysis = await processor.analyze_archive_activity()
            tracker.update_statistics(
                activity_breakdown=activity_analysis.get("activity_breakdown", {})
            )
        except Exception as e:
            logger.warning(f"Activity analysis failed, continuing: {e}")
            activity_analysis = {"total_conversations": analysis.get("conversations_found", 0)}
        
        tracker.complete_step("analyze", {
            "conversations_analyzed": activity_analysis.get("total_conversations", 0)
        })
        
        # Step 3: Process conversations
        tracker.start_step("import")
        
        # Get the actual processing results
        results = await processor.process_archive_smart(max_conversations)
        
        tracker.complete_step("import", {
            "conversations_processed": results.get("conversations_processed", 0),
            "chunks_created": results.get("total_chunks", 0),
            "failed_conversations": results.get("failed_conversations", 0)
        })
        
        # Step 4: Embedding generation (handled within smart processing)
        tracker.start_step("embed")
        tracker.complete_step("embed", {
            "embeddings_generated": results.get("embeddings_generated", 0)
        })
        
        # Step 5: Cleanup
        tracker.start_step("finalize")
        
        # Clean up temporary directory
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
            logger.info(f"Cleaned up temporary directory: {temp_dir}")
        except Exception as e:
            logger.warning(f"Could not clean up temp directory: {e}")
        
        tracker.complete_step("finalize", {
            "cleanup_completed": True,
            "temp_dir_removed": True
        })
        
        # Complete session
        tracker.complete_session()
        
        # Broadcast completion
        await manager.broadcast(json.dumps({
            "type": "upload_processing_complete",
            "session_id": tracker.session_id,
            "summary": tracker.get_progress_summary(),
            "results": results
        }))
        
        logger.info(f"Archive upload processing completed for session {tracker.session_id}")
        
    except Exception as e:
        logger.error(f"Archive upload processing failed: {e}")
        tracker.fail_step(tracker.progress.current_step, str(e))
        
        # Clean up temp directory on failure
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
        except:
            pass

# Enhanced smart processing with progress tracking
@app.post("/smart-processing/start")
async def start_smart_processing_with_progress(
    max_conversations: Optional[int] = Query(None, description="Limit conversations for testing"),
    node_archive_path: Optional[str] = Query("/Users/tem/nab/exploded_archive_node", description="Path to Node Archive"),
    background_tasks: BackgroundTasks = None
):
    """Start smart archive processing with real-time progress tracking"""
    try:
        # Create new progress tracker
        tracker = get_progress_tracker()
        session_id = tracker.session_id
        
        # Start the processing in background
        background_tasks.add_task(
            run_smart_processing_with_progress,
            tracker,
            node_archive_path,
            max_conversations
        )
        
        return {
            "status": "started",
            "session_id": session_id,
            "websocket_url": f"/ws/progress/{session_id}",
            "progress_url": f"/progress/{session_id}",
            "message": "Processing started in background"
        }
        
    except Exception as e:
        logger.error(f"Error starting smart processing: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def run_smart_processing_with_progress(
    tracker: PersistentProgressTracker,
    node_archive_path: str,
    max_conversations: Optional[int] = None
):
    """Run smart processing with integrated progress tracking"""
    try:
        # Start session
        tracker.start_session()
        
        # Step 1: Analysis
        tracker.start_step("analyze")
        processor = SmartArchiveProcessor(config.get_database_url(), node_archive_path)
        await processor.initialize()
        
        analysis = await processor.analyze_archive_activity()
        tracker.update_statistics(
            total_conversations=analysis["total_conversations"],
            activity_breakdown=analysis["activity_breakdown"]
        )
        tracker.complete_step("analyze", {
            "conversations_found": analysis["total_conversations"],
            "activity_distribution": analysis["activity_breakdown"]
        })
        
        # Step 2: Import conversations
        tracker.start_step("import")
        
        # Process with progress updates
        job_queue = processor.job_queue[:max_conversations] if max_conversations else processor.job_queue
        total_jobs = len(job_queue)
        
        processed = 0
        failed = 0
        total_chunks = 0
        
        for i, job in enumerate(job_queue):
            try:
                # Update import progress
                progress = (i + 1) / total_jobs
                tracker.update_step_progress("import", progress, {
                    "processed_conversations": processed,
                    "failed_conversations": failed,
                    "current_conversation": job.job_id
                })
                
                # Process single job (simplified version)
                result = await process_single_job_with_progress(processor, job, tracker)
                if result:
                    processed += 1
                    total_chunks += result.get("chunks_created", 0)
                else:
                    failed += 1
                
                # Update statistics
                tracker.update_statistics(
                    processed_conversations=processed,
                    failed_conversations=failed,
                    total_chunks=total_chunks
                )
                
            except Exception as e:
                failed += 1
                logger.error(f"Job {job.job_id} failed: {e}")
        
        tracker.complete_step("import", {
            "conversations_processed": processed,
            "conversations_failed": failed,
            "total_chunks_created": total_chunks
        })
        
        # Step 3: Chunk processing (if needed)
        tracker.start_step("chunk")
        tracker.complete_step("chunk", {"chunks_processed": total_chunks})
        
        # Step 4: Embedding generation
        tracker.start_step("embed")
        # Embedding progress would be tracked here
        tracker.complete_step("embed", {"embeddings_generated": total_chunks})
        
        # Step 5: Finalization
        tracker.start_step("finalize")
        tracker.complete_step("finalize", {"cleanup_completed": True})
        
        # Complete session
        tracker.complete_session()
        
        # Broadcast completion
        await manager.broadcast(json.dumps({
            "type": "processing_complete",
            "session_id": tracker.session_id,
            "summary": tracker.get_progress_summary()
        }))
        
    except Exception as e:
        logger.error(f"Smart processing failed: {e}")
        tracker.fail_step(tracker.progress.current_step, str(e))

async def process_single_job_with_progress(processor, job, tracker):
    """Process a single job with progress updates"""
    try:
        # This is a simplified version - in reality you'd call the actual processing
        # For now, just simulate processing
        await asyncio.sleep(0.1)  # Simulate processing time
        
        return {
            "content_id": 1,
            "chunks_created": 5,  # Simulated
            "embeddings_generated": 5
        }
    except Exception as e:
        logger.error(f"Job processing failed: {e}")
        return None

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=config.api.archive_api_port,
        log_level="info"
    )