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

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
import httpx
from sentence_transformers import SentenceTransformer

# Import our unified archive components
from archive_unified_schema import (
    UnifiedArchiveDB, 
    ArchiveContent, 
    SourceType, 
    ContentType
)
from node_archive_importer import NodeArchiveImporter
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
embedding_model: Optional[SentenceTransformer] = None

@app.on_event("startup")
async def startup_event():
    """Initialize database and models on startup"""
    global archive_db, embedding_model
    
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
        
        # Initialize embedding model for semantic search
        try:
            embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("✅ Loaded embedding model for semantic search")
        except Exception as e:
            logger.warning(f"Could not load embedding model: {e}")
            embedding_model = None
        
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
        "embedding_model_loaded": embedding_model is not None,
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=config.api.archive_api_port,
        log_level="info"
    )