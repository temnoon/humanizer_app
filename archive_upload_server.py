#!/usr/bin/env python3
"""
Simple Archive Upload Server
Provides /upload-archive endpoint for the Lighthouse UI
"""

import asyncio
import json
import base64
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from simple_archive_processor import SimpleArchiveProcessor, process_uploaded_archive
from hierarchical_chunker import process_content_hierarchically

# Pydantic models for request/response
class EmbeddingsRequest(BaseModel):
    conversation_ids: Optional[List[int]] = None
    batch_size: int = 10
    max_conversations: Optional[int] = None

class ChunkingRequest(BaseModel):
    content_ids: Optional[List[int]] = None
    max_content: Optional[int] = None
    include_summaries: bool = True

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/Users/tem/humanizer-lighthouse/archive_import.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("archive_import")

# Create FastAPI app with increased file limits
app = FastAPI(
    title="Archive Upload API",
    description="Large-scale archive upload and processing service",
    version="2.0.0"
)

# Configure large upload limits
from starlette.middleware import Middleware
from starlette.config import Config
from starlette.applications import Starlette

# Set environment variables for large uploads
import os
os.environ["STARLETTE_MAX_UPLOAD_SIZE"] = str(10 * 1024 * 1024 * 1024)  # 10GB max upload
os.environ["STARLETTE_MAX_FILES"] = "50000"  # Allow up to 50,000 files for Node Archive Browser

# Configure multipart form limits (handled in middleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware for large uploads
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request as StarletteRequest
from starlette.responses import Response

class LargeUploadMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: StarletteRequest, call_next):
        # Increase limits for multipart uploads
        if request.method == "POST" and "multipart/form-data" in request.headers.get("content-type", ""):
            # Override multipart limits for large archives
            import starlette.formparsers
            
            # Store original parser class
            original_multipart_parser = starlette.formparsers.MultiPartParser
            
            class HighLimitMultiPartParser(original_multipart_parser):
                def __init__(self, headers, stream, **kwargs):
                    # Force override the default limits with logging
                    logger.info(f"🔧 Creating parser with limits: files={kwargs.get('max_files', 'default')}, fields={kwargs.get('max_fields', 'default')}")
                    kwargs['max_files'] = 10000  # Try 10,000 instead of 50,000
                    kwargs['max_fields'] = 10000  # Try 10,000 instead of 50,000 
                    kwargs['max_part_size'] = 100 * 1024 * 1024  # 100MB per part
                    logger.info(f"🔧 Forcing parser limits to: files={kwargs['max_files']}, fields={kwargs['max_fields']}")
                    super().__init__(headers, stream, **kwargs)
            
            # Replace the parser class globally
            starlette.formparsers.MultiPartParser = HighLimitMultiPartParser
            logger.info("🔧 Replaced MultiPartParser with high-limit version")
        
        response = await call_next(request)
        
        # Don't restore - keep the high limit parser active
        # This ensures it stays active for all requests
        
        return response

app.add_middleware(LargeUploadMiddleware)

# Global storage for processing sessions
processing_sessions: Dict[str, SimpleArchiveProcessor] = {}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "archive_upload_server",
        "version": "1.0.0"
    }


@app.post("/upload-archive")
async def upload_archive(request: Request, background_tasks: BackgroundTasks):
    """Upload and process archive files"""
    try:
        logger.info("=== ARCHIVE UPLOAD STARTED ===")
        
        # Get form data to handle dynamic file fields from frontend
        try:
            form = await request.form()
        except Exception as form_error:
            if "Too many files" in str(form_error):
                logger.error(f"Upload has too many files: {form_error}")
                # Suggest folder-by-folder processing for Node Archive Browser exports
                raise HTTPException(
                    status_code=413, 
                    detail="Archive has too many files (Node Archive Browser format detected). Please use the 'Process Local Folder' option below instead of uploading files. This will process conversation folders one at a time to avoid file limits."
                )
            else:
                logger.error(f"Form parsing error: {form_error}")
                raise HTTPException(status_code=400, detail=f"Upload error: {form_error}")
        
        files_uploaded = []
        archive_info = {
            "files": [],
            "total_size": 0,
            "has_conversations_json": False
        }
        
        logger.info(f"Processing form with {len(form)} fields")
        
        # Process uploaded files
        file_count = 0
        for key, value in form.items():
            if key.startswith('file_'):
                file_index = key.split('_')[1]
                path_key = f"path_{file_index}"
                file_path = form.get(path_key, "unknown")
                
                if hasattr(value, 'filename') and hasattr(value, 'read'):
                    # It's a file upload
                    content = await value.read()
                    files_uploaded.append({
                        "filename": value.filename,
                        "path": file_path,
                        "size": len(content),
                        "content": content
                    })
                    archive_info["total_size"] += len(content)
                    file_count += 1
                    
                    if value.filename == "conversations.json":
                        archive_info["has_conversations_json"] = True
                        logger.info(f"Found conversations.json file: {len(content)} bytes")
                    
                    if file_count <= 10:  # Only log first 10 files to avoid spam
                        logger.info(f"Uploaded file: {value.filename} ({len(content)} bytes)")
                    elif file_count % 100 == 0:  # Log every 100th file
                        logger.info(f"Processed {file_count} files so far...")
        
        if not files_uploaded:
            logger.error("No files were uploaded")
            raise HTTPException(status_code=400, detail="No files uploaded")
        
        logger.info(f"Total files uploaded: {len(files_uploaded)}")
        logger.info(f"Total size: {archive_info['total_size'] / (1024*1024):.2f} MB")
        logger.info(f"Has conversations.json: {archive_info['has_conversations_json']}")
        
        # Create processor and start real processing
        processor = SimpleArchiveProcessor()
        processing_sessions[processor.session_id] = processor
        
        # Start background processing with real data
        background_tasks.add_task(
            run_real_archive_processing,
            processor.session_id,
            files_uploaded,
            archive_info
        )
        
        return {
            "status": "started",
            "archive_path": f"/tmp/archive_{processor.session_id}",
            "session_id": processor.session_id,
            "files_uploaded": len(files_uploaded),
            "total_size_mb": round(archive_info["total_size"] / (1024 * 1024), 2),
            "progress_url": f"/progress/{processor.session_id}",
            "message": "Archive upload started - processing in background"
        }
        
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def run_real_archive_processing(
    session_id: str,
    files_uploaded: List[Dict],
    archive_info: Dict
):
    """Run real archive processing with logging"""
    processor = processing_sessions.get(session_id)
    if not processor:
        logger.error(f"Processor not found for session {session_id}")
        return
    
    try:
        logger.info(f"=== PROCESSING SESSION {session_id} ===")
        
        # Step 1: Analysis
        processor.progress["current_step"] = "analyze"
        processor.progress["steps"]["analyze"]["status"] = "in_progress"
        logger.info("Step 1: Analyzing uploaded files...")
        
        conversations_found = 0
        conversations_data = None
        
        # Look for conversations.json and parse it
        for file_info in files_uploaded:
            if file_info["filename"] == "conversations.json":
                try:
                    content = file_info["content"]
                    if isinstance(content, bytes):
                        content = content.decode('utf-8')
                    conversations_data = json.loads(content)
                    
                    if isinstance(conversations_data, list):
                        conversations_found = len(conversations_data)
                        logger.info(f"Found OpenAI format: {conversations_found} conversations")
                    elif isinstance(conversations_data, dict):
                        if "conversations" in conversations_data:
                            conversations_found = len(conversations_data["conversations"])
                            logger.info(f"Found structured format: {conversations_found} conversations")
                        else:
                            conversations_found = len([k for k in conversations_data.keys() if k != "metadata"])
                            logger.info(f"Found Node Archive Browser format: {conversations_found} conversations")
                    
                    break
                except Exception as e:
                    logger.error(f"Failed to parse conversations.json: {e}")
        
        processor.progress["stats"]["conversations_found"] = conversations_found
        processor.progress["steps"]["analyze"]["status"] = "completed"
        processor.progress["steps"]["analyze"]["progress"] = 1.0
        logger.info(f"Analysis complete: {conversations_found} conversations found")
        
        # Step 2: Import Processing
        processor.progress["current_step"] = "import"
        processor.progress["steps"]["import"]["status"] = "in_progress"
        processor.progress["stats"]["start_time"] = datetime.now().isoformat()
        logger.info("Step 2: Processing conversations...")
        
        processed = 0
        failed = 0
        total_messages = 0
        total_media_files = 0
        large_messages = 0  # Track very large messages
        
        if conversations_data and conversations_found > 0:
            conversations = []
            if isinstance(conversations_data, list):
                conversations = conversations_data
            elif isinstance(conversations_data, dict):
                if "conversations" in conversations_data:
                    conversations = conversations_data["conversations"]
                else:
                    conversations = [{"id": k, "data": v} for k, v in conversations_data.items() if k != "metadata"]
            
            # Process in batches for memory efficiency with large archives
            batch_size = 100 if len(conversations) > 1000 else 50
            logger.info(f"Processing {len(conversations)} conversations in batches of {batch_size}")
            
            for batch_start in range(0, len(conversations), batch_size):
                batch_end = min(batch_start + batch_size, len(conversations))
                batch = conversations[batch_start:batch_end]
                
                logger.info(f"Processing batch {batch_start//batch_size + 1}: conversations {batch_start+1}-{batch_end}")
                
                for i, conversation in enumerate(batch):
                    actual_index = batch_start + i
                    try:
                        # Enhanced processing for Node Archive Browser format
                        message_count = 0
                        media_count = 0
                        conv_size = 0
                        
                        if isinstance(conversation, dict):
                            if "mapping" in conversation:
                                # OpenAI format
                                mapping = conversation.get("mapping", {})
                                for msg_id, msg_data in mapping.items():
                                    if msg_data.get("message") and msg_data.get("message", {}).get("content"):
                                        message_count += 1
                                        # Check for large messages (>1MB)
                                        content = str(msg_data.get("message", {}).get("content", ""))
                                        msg_size = len(content.encode('utf-8'))
                                        conv_size += msg_size
                                        if msg_size > 1024 * 1024:  # 1MB
                                            large_messages += 1
                                            logger.info(f"Large message found: {msg_size/1024/1024:.1f}MB in conversation {actual_index+1}")
                                        
                                        # Check for media attachments
                                        if "attachments" in msg_data.get("message", {}):
                                            media_count += len(msg_data["message"]["attachments"])
                                            
                            elif "data" in conversation:
                                # Node Archive Browser format - optimized for large conversations
                                conv_data = conversation["data"]
                                if isinstance(conv_data, dict):
                                    if "messages" in conv_data:
                                        messages = conv_data["messages"]
                                        message_count = len(messages)
                                        
                                        # Sample check for very large conversations (>1000 messages)
                                        if message_count > 1000:
                                            logger.info(f"Large conversation found: {message_count} messages in conversation {actual_index+1}")
                                            # For very large conversations, sample check message sizes
                                            sample_size = min(100, message_count)
                                            for j in range(0, message_count, message_count // sample_size):
                                                if j < len(messages):
                                                    msg = messages[j]
                                                    if isinstance(msg, dict) and "content" in msg:
                                                        content = str(msg["content"])
                                                        msg_size = len(content.encode('utf-8'))
                                                        conv_size += msg_size
                                                        if msg_size > 1024 * 1024:  # 1MB
                                                            large_messages += 1
                                        else:
                                            # For smaller conversations, check all messages
                                            for msg in messages:
                                                if isinstance(msg, dict) and "content" in msg:
                                                    content = str(msg["content"])
                                                    msg_size = len(content.encode('utf-8'))
                                                    conv_size += msg_size
                                                    if msg_size > 1024 * 1024:  # 1MB
                                                        large_messages += 1
                                    
                                    # Check for media files in Node Archive format
                                    if "media" in conv_data:
                                        media_count = len(conv_data["media"])
                                    elif "attachments" in conv_data:
                                        media_count = len(conv_data["attachments"])
                                        
                            elif "messages" in conversation:
                                # Direct messages format
                                messages = conversation["messages"]
                                message_count = len(messages)
                                for msg in messages:
                                    if isinstance(msg, dict) and "content" in msg:
                                        content = str(msg["content"])
                                        msg_size = len(content.encode('utf-8'))
                                        conv_size += msg_size
                                        if msg_size > 1024 * 1024:  # 1MB
                                            large_messages += 1
                        
                        total_messages += message_count
                        total_media_files += media_count
                        processed += 1
                        
                        # Log large conversations
                        if conv_size > 10 * 1024 * 1024:  # 10MB conversation
                            logger.info(f"Very large conversation: {conv_size/1024/1024:.1f}MB, {message_count} messages, {media_count} media files")
                        
                        # Update progress
                        progress = (actual_index + 1) / len(conversations)
                        processor.progress["steps"]["import"]["progress"] = progress
                        processor.progress["stats"]["conversations_processed"] = processed
                        processor.progress["stats"]["files_processed"] = actual_index + 1
                        
                        # Reduced logging frequency for large archives
                        log_frequency = 100 if len(conversations) > 1000 else 50
                        if (actual_index + 1) % log_frequency == 0:
                            logger.info(f"Processed {actual_index+1}/{len(conversations)} conversations")
                            logger.info(f"  📝 {total_messages:,} messages, 📎 {total_media_files:,} media files")
                            logger.info(f"  📏 {large_messages} large messages (>1MB)")
                        
                        # Small delay for very large archives to prevent overwhelming
                        if len(conversations) > 5000:
                            await asyncio.sleep(0.001)  # 1ms
                        elif len(conversations) > 1000:
                            await asyncio.sleep(0.005)  # 5ms
                        else:
                            await asyncio.sleep(0.01)   # 10ms
                        
                    except Exception as e:
                        failed += 1
                        logger.error(f"Failed to process conversation {actual_index+1}: {str(e)}")
                
                # Log batch completion for large archives
                if len(conversations) > 500:
                    logger.info(f"Completed batch {batch_start//batch_size + 1}/{(len(conversations)-1)//batch_size + 1}")
                    # Force garbage collection for memory management
                    import gc
                    gc.collect()
        
        processor.progress["steps"]["import"]["status"] = "completed"
        processor.progress["steps"]["import"]["progress"] = 1.0
        logger.info(f"Import complete: {processed} conversations, {total_messages:,} total messages, {total_media_files:,} media files, {failed} failed")
        logger.info(f"Large message analysis: {large_messages} messages >1MB found")
        
        # Step 3: Finalization
        processor.progress["current_step"] = "finalize"
        processor.progress["steps"]["finalize"]["status"] = "in_progress"
        logger.info("Step 3: Finalizing...")
        
        processor.progress["steps"]["finalize"]["status"] = "completed"
        processor.progress["steps"]["finalize"]["progress"] = 1.0
        processor.progress["status"] = "completed"
        
        final_results = {
            "conversations_processed": processed,
            "conversations_failed": failed,
            "total_messages": total_messages,
            "total_media_files": total_media_files,
            "large_messages": large_messages,
            "files_uploaded": len(files_uploaded),
            "processing_time": processor.calculate_processing_time(),
            "archive_scale": "large" if processed > 1000 else "medium" if processed > 100 else "small"
        }
        
        processor.progress["final_results"] = final_results
        
        logger.info(f"=== PROCESSING COMPLETE ===")
        logger.info(f"Session: {session_id}")
        logger.info(f"Results: {final_results}")
        
    except Exception as e:
        logger.error(f"Processing failed for session {session_id}: {str(e)}")
        processor.progress["status"] = "failed"
        processor.progress["error"] = str(e)


@app.get("/progress/sessions")
async def list_sessions():
    """List all processing sessions"""
    sessions = []
    for session_id, processor in processing_sessions.items():
        progress = processor.get_progress()
        sessions.append({
            "session_id": session_id,
            "status": progress["status"],
            "progress_percent": progress["progress_percent"],
            "conversations_found": progress["stats"]["conversations_found"],
            "conversations_processed": progress["stats"]["conversations_processed"]
        })
    
    return {
        "status": "success",
        "sessions": sessions,
        "total_sessions": len(sessions)
    }


@app.get("/progress/{session_id}")
async def get_progress(session_id: str):
    """Get processing progress for a session"""
    processor = processing_sessions.get(session_id)
    if not processor:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "status": "success",
        "progress": processor.get_progress()
    }


@app.delete("/progress/{session_id}")
async def cleanup_session(session_id: str):
    """Clean up a processing session"""
    if session_id in processing_sessions:
        del processing_sessions[session_id]
        return {
            "status": "success",
            "message": f"Session {session_id} cleaned up"
        }
    else:
        raise HTTPException(status_code=404, detail="Session not found")


@app.post("/smart-processing/start")
async def start_smart_processing(
    background_tasks: BackgroundTasks,
    archive_path: str = None,
    max_conversations: Optional[int] = None
):
    """Start smart processing (compatibility endpoint)"""
    # This is a compatibility endpoint for the frontend
    # In practice, processing is already handled in upload-archive
    processor = SimpleArchiveProcessor()
    processing_sessions[processor.session_id] = processor
    
    # Mark as completed since upload-archive already processed
    processor.progress["status"] = "completed"
    processor.progress["progress_percent"] = 100.0
    
    return {
        "status": "started",
        "session_id": processor.session_id,
        "websocket_url": f"/ws/progress/{processor.session_id}",
        "progress_url": f"/progress/{processor.session_id}",
        "message": "Processing already completed during upload"
    }


@app.get("/embeddings/statistics")
async def get_embedding_statistics():
    """Get embedding statistics from PostgreSQL"""
    try:
        import asyncpg
        
        conn = await asyncpg.connect(
            host="localhost", 
            database="humanizer_archive",
            user="tem"
        )
        
        # Get statistics from PostgreSQL
        stats = await conn.fetchrow("""
        SELECT 
            COUNT(*) as total_content,
            COUNT(*) FILTER (WHERE content_type = 'conversation') as conversations,
            COUNT(*) FILTER (WHERE content_type = 'message') as messages,
            COUNT(*) FILTER (WHERE semantic_vector IS NOT NULL) as embeddings,
            AVG(content_quality_score) as avg_quality
        FROM archived_content
        """)
        
        await conn.close()
        
        return {
            "status": "success",
            "total_chunks": stats["total_content"],
            "total_embeddings": stats["embeddings"],
            "vector_dimension": 768,
            "embedding_model": "nomic-embed-text (via Ollama)",
            "embedding_provider": "ollama", 
            "conversations_count": stats["conversations"],
            "messages_count": stats["messages"],
            "average_quality": float(stats["avg_quality"]) if stats["avg_quality"] else 0,
            "model_info": {
                "name": "nomic-embed-text",
                "dimensions": 768,
                "provider": "Ollama (Local)",
                "description": "Local embedding model via Ollama"
            }
        }
        
    except Exception as e:
        logger.error(f"Statistics failed: {str(e)}")
        return {
            "status": "success", 
            "total_chunks": 0,
            "total_embeddings": 0,
            "vector_dimension": 768,
            "embedding_model": "nomic-embed-text (via Ollama)",
            "embedding_provider": "ollama",
            "error": str(e)
        }


@app.post("/search")
async def search_archive(
    query: str = "",
    source_types: List[str] = None,
    author: str = None,
    date_from: str = None,
    date_to: str = None,
    limit: int = 50,
    semantic_search: bool = False
):
    """Search archive with PostgreSQL and pgvector support"""
    try:
        import asyncpg
        
        # Connect to PostgreSQL
        conn = await asyncpg.connect(
            host="localhost",
            database="humanizer_archive",
            user="tem"
        )
        
        # Build the search query
        where_conditions = []
        params = []
        param_count = 0
        
        if query:
            if semantic_search:
                # TODO: Implement semantic search with embeddings
                # For now, fall back to text search
                param_count += 1
                where_conditions.append(f"to_tsvector('english', COALESCE(title, '') || ' ' || COALESCE(body_text, '')) @@ plainto_tsquery('english', ${param_count})")
                params.append(query)
            else:
                # Full-text search
                param_count += 1
                where_conditions.append(f"to_tsvector('english', COALESCE(title, '') || ' ' || COALESCE(body_text, '')) @@ plainto_tsquery('english', ${param_count})")
                params.append(query)
        
        if source_types:
            param_count += 1
            where_conditions.append(f"source_type = ANY(${param_count})")
            params.append(source_types)
            
        if author:
            param_count += 1
            where_conditions.append(f"author ILIKE ${param_count}")
            params.append(f"%{author}%")
            
        if date_from:
            param_count += 1
            where_conditions.append(f"timestamp >= ${param_count}")
            params.append(date_from)
            
        if date_to:
            param_count += 1
            where_conditions.append(f"timestamp <= ${param_count}")
            params.append(date_to)
        
        # Build final query
        base_query = """
        SELECT 
            id, source_type, source_id, content_type, title, body_text,
            author, timestamp, content_quality_score, word_count
        FROM archived_content
        """
        
        if where_conditions:
            base_query += " WHERE " + " AND ".join(where_conditions)
            
        base_query += f" ORDER BY timestamp DESC LIMIT ${param_count + 1}"
        params.append(limit)
        
        # Execute query
        rows = await conn.fetch(base_query, *params)
        
        # Format results
        results = []
        for row in rows:
            results.append({
                "id": row["id"],
                "source_type": row["source_type"],
                "content_type": row["content_type"],
                "title": row["title"],
                "body_text": row["body_text"][:500] + "..." if len(row["body_text"] or "") > 500 else row["body_text"],
                "author": row["author"],
                "timestamp": row["timestamp"].isoformat() if row["timestamp"] else None,
                "content_quality_score": row["content_quality_score"],
                "word_count": row["word_count"]
            })
        
        await conn.close()
        
        return {
            "status": "success",
            "results": results,
            "total_found": len(results),
            "query_used": query,
            "search_type": "semantic" if semantic_search else "text"
        }
        
    except Exception as e:
        logger.error(f"Search failed: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
            "results": []
        }


@app.get("/logs/import")
async def get_import_logs(lines: int = 50):
    """Get recent import log entries"""
    try:
        log_file = "/Users/tem/humanizer-lighthouse/archive_import.log"
        with open(log_file, 'r') as f:
            all_lines = f.readlines()
        
        # Get the last N lines
        recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
        
        return {
            "status": "success",
            "log_entries": [line.strip() for line in recent_lines],
            "total_lines": len(all_lines),
            "showing_lines": len(recent_lines)
        }
    except FileNotFoundError:
        return {
            "status": "success",
            "log_entries": ["Log file not found - no imports yet"],
            "total_lines": 0,
            "showing_lines": 1
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "log_entries": [],
            "total_lines": 0,
            "showing_lines": 0
        }


@app.get("/conversations")
async def get_conversations(
    page: int = 1,
    limit: int = 50,
    sort_by: str = "timestamp",  # "timestamp", "title", "message_count", "word_count", "create_time"
    order: str = "desc",  # "asc", "desc"
    search: str = None,  # Search query for conversation titles
    min_words: int = None,  # Minimum word count filter
    max_words: int = None,  # Maximum word count filter
    min_messages: int = None,  # Minimum message count filter
    max_messages: int = None,  # Maximum message count filter
    date_from: str = None,  # Date range filter (ISO format)
    date_to: str = None,  # Date range filter (ISO format)
    author: str = None  # Author filter
):
    """Get paginated list of conversations with stats"""
    try:
        import asyncpg
        
        conn = await asyncpg.connect(
            host="localhost",
            database="humanizer_archive", 
            user="tem"
        )
        
        # Build ORDER BY clause
        order_direction = "DESC" if order.lower() == "desc" else "ASC"
        if sort_by == "message_count":
            order_clause = f"message_count {order_direction}"
        elif sort_by == "title":
            order_clause = f"title {order_direction}"
        elif sort_by == "word_count":
            order_clause = f"total_word_count {order_direction}"
        elif sort_by == "create_time":
            order_clause = f"c.timestamp {order_direction}"  # Using timestamp as create time
        else:  # default to timestamp
            order_clause = f"c.timestamp {order_direction}"
        
        # Build WHERE clause with all filters
        where_conditions = ["c.content_type = 'conversation'"]
        params = []
        param_count = 0
        
        # Search filter
        if search and search.strip():
            param_count += 1
            where_conditions.append(f"c.title ILIKE ${param_count}")
            params.append(f"%{search.strip()}%")
        
        # Author filter
        if author and author.strip():
            param_count += 1
            where_conditions.append(f"c.author ILIKE ${param_count}")
            params.append(f"%{author.strip()}%")
        
        # Date range filters
        if date_from:
            param_count += 1
            where_conditions.append(f"c.timestamp >= ${param_count}")
            params.append(date_from)
        
        if date_to:
            param_count += 1
            where_conditions.append(f"c.timestamp <= ${param_count}")
            params.append(date_to)
        
        where_clause = " AND ".join(where_conditions)
        
        # Build HAVING clause for aggregate filters (message count, word count)
        having_conditions = []
        
        if min_messages is not None:
            param_count += 1
            having_conditions.append(f"COUNT(m.id) >= ${param_count}")
            params.append(min_messages)
        
        if max_messages is not None:
            param_count += 1
            having_conditions.append(f"COUNT(m.id) <= ${param_count}")
            params.append(max_messages)
        
        if min_words is not None:
            param_count += 1
            having_conditions.append(f"COALESCE(SUM(m.word_count), c.word_count, 0) >= ${param_count}")
            params.append(min_words)
        
        if max_words is not None:
            param_count += 1
            having_conditions.append(f"COALESCE(SUM(m.word_count), c.word_count, 0) <= ${param_count}")
            params.append(max_words)
        
        having_clause = " AND ".join(having_conditions) if having_conditions else ""
        
        # Get conversations with message counts
        offset = (page - 1) * limit
        param_count += 1
        limit_param = param_count
        param_count += 1
        offset_param = param_count
        params.extend([limit, offset])
        
        query = f"""
            SELECT 
                c.id,
                c.title,
                c.source_id,
                c.timestamp,
                c.author,
                c.word_count as conversation_word_count,
                COUNT(m.id) as message_count,
                COALESCE(SUM(m.word_count), c.word_count, 0) as total_word_count,
                c.source_metadata
            FROM archived_content c
            LEFT JOIN archived_content m ON c.id = m.parent_id
            WHERE {where_clause}
            GROUP BY c.id, c.title, c.source_id, c.timestamp, c.author, c.word_count, c.source_metadata
            {f'HAVING {having_clause}' if having_clause else ''}
            ORDER BY {order_clause}
            LIMIT ${limit_param} OFFSET ${offset_param}
        """
        
        rows = await conn.fetch(query, *params)
        
        # Get total count with all filters
        count_params = params[:-2]  # Remove limit and offset
        count_query = f"""
            SELECT COUNT(*) FROM (
                SELECT c.id
                FROM archived_content c
                LEFT JOIN archived_content m ON c.id = m.parent_id
                WHERE {where_clause}
                GROUP BY c.id, c.title, c.source_id, c.timestamp, c.author, c.word_count, c.source_metadata
                {f'HAVING {having_clause}' if having_clause else ''}
            ) AS filtered_conversations
        """
        total_count = await conn.fetchval(count_query, *count_params)
        
        await conn.close()
        
        conversations = []
        for row in rows:
            # Handle source_metadata which might be JSON string or dict
            metadata = row["source_metadata"] or {}
            if isinstance(metadata, str):
                try:
                    metadata = json.loads(metadata)
                except (json.JSONDecodeError, TypeError):
                    metadata = {}
            conversations.append({
                "id": row["id"],
                "title": row["title"],
                "source_id": row["source_id"],
                "timestamp": row["timestamp"].isoformat() if row["timestamp"] else None,
                "author": row["author"],
                "message_count": row["message_count"],
                "total_word_count": row["total_word_count"] or 0,
                "has_media": False,  # TODO: Implement media detection
                "folder_name": metadata.get("folder_name", ""),
                "create_time": metadata.get("create_time"),
                "update_time": metadata.get("update_time")
            })
        
        return {
            "status": "success",
            "conversations": conversations,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total_count,
                "pages": (total_count + limit - 1) // limit
            }
        }
        
    except Exception as e:
        logger.error(f"Get conversations failed: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
            "conversations": []
        }


@app.get("/conversations/{conversation_id}/messages")
async def get_conversation_messages(conversation_id: int, page: int = 1, limit: int = 100):
    """Get messages for a specific conversation"""
    try:
        import asyncpg
        
        conn = await asyncpg.connect(
            host="localhost",
            database="humanizer_archive",
            user="tem"
        )
        
        # Get conversation info
        conversation = await conn.fetchrow("""
            SELECT id, title, source_id, timestamp, source_metadata
            FROM archived_content 
            WHERE id = $1 AND content_type = 'conversation'
        """, conversation_id)
        
        if not conversation:
            await conn.close()
            return {"status": "error", "message": "Conversation not found"}
        
        # Get messages with pagination
        offset = (page - 1) * limit
        messages = await conn.fetch("""
            SELECT id, source_id, body_text, author, timestamp, word_count, source_metadata
            FROM archived_content
            WHERE parent_id = $1 AND content_type = 'message'
            ORDER BY timestamp ASC
            LIMIT $2 OFFSET $3
        """, conversation_id, limit, offset)
        
        # Get total message count
        total_messages = await conn.fetchval("""
            SELECT COUNT(*) FROM archived_content 
            WHERE parent_id = $1 AND content_type = 'message'
        """, conversation_id)
        
        await conn.close()
        
        message_list = []
        for msg in messages:
            # Handle source_metadata which might be JSON string or dict
            metadata = msg["source_metadata"] or {}
            if isinstance(metadata, str):
                try:
                    metadata = json.loads(metadata)
                except (json.JSONDecodeError, TypeError):
                    metadata = {}
            message_list.append({
                "id": msg["id"],
                "source_id": msg["source_id"], 
                "body_text": msg["body_text"],
                "author": msg["author"],
                "timestamp": msg["timestamp"].isoformat() if msg["timestamp"] else None,
                "word_count": msg["word_count"],
                "role": metadata.get("role", msg["author"]),
                "create_time": metadata.get("create_time")
            })
        
        # Handle conversation metadata
        conv_metadata = conversation["source_metadata"] or {}
        if isinstance(conv_metadata, str):
            try:
                conv_metadata = json.loads(conv_metadata)
            except (json.JSONDecodeError, TypeError):
                conv_metadata = {}
        
        return {
            "status": "success",
            "conversation": {
                "id": conversation["id"],
                "title": conversation["title"],
                "source_id": conversation["source_id"],
                "timestamp": conversation["timestamp"].isoformat() if conversation["timestamp"] else None,
                "metadata": conv_metadata
            },
            "messages": message_list,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total_messages,
                "pages": (total_messages + limit - 1) // limit
            }
        }
        
    except Exception as e:
        logger.error(f"Get conversation messages failed: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }


@app.post("/generate-embeddings")
async def generate_embeddings(request: EmbeddingsRequest):
    """Generate embeddings for conversations using nomic-text-embed"""
    try:
        import asyncpg
        import asyncio
        from datetime import datetime
        import json
        
        conn = await asyncpg.connect(
            host="localhost",
            database="humanizer_archive",
            user="tem"
        )
        
        # Get conversations to process
        if request.conversation_ids:
            query = """
                SELECT id, title, body_text, word_count 
                FROM archived_content 
                WHERE id = ANY($1) AND content_type = 'conversation'
                ORDER BY id
            """
            conversations = await conn.fetch(query, request.conversation_ids)
        else:
            # Get all conversations without embeddings
            query = """
                SELECT id, title, body_text, word_count 
                FROM archived_content 
                WHERE content_type = 'conversation' 
                AND semantic_vector IS NULL
                ORDER BY word_count DESC
            """
            if request.max_conversations:
                query += f" LIMIT {request.max_conversations}"
            conversations = await conn.fetch(query)
        
        if not conversations:
            await conn.close()
            return {
                "status": "success",
                "message": "No conversations need embeddings",
                "processed": 0,
                "total": 0
            }
        
        # Process in batches
        total_conversations = len(conversations)
        processed = 0
        failed = 0
        
        logger.info(f"Starting embedding generation for {total_conversations} conversations")
        
        for i in range(0, total_conversations, request.batch_size):
            batch = conversations[i:i + request.batch_size]
            
            for conv in batch:
                try:
                    # Use the existing embedding generation logic
                    content = conv['body_text'] or conv['title'] or ""
                    if not content.strip():
                        continue
                    
                    # Generate embedding using ollama's nomic-embed-text
                    import requests
                    embed_response = requests.post(
                        "http://localhost:11434/api/embeddings",
                        json={
                            "model": "nomic-embed-text",
                            "prompt": content[:8000]  # Limit content length
                        },
                        timeout=30
                    )
                    
                    if embed_response.status_code == 200:
                        embedding_data = embed_response.json()
                        embedding = embedding_data.get("embedding", [])
                        
                        if embedding:
                            # Store embedding in database (convert list to pgvector format)
                            await conn.execute("""
                                UPDATE archived_content 
                                SET semantic_vector = $1::vector 
                                WHERE id = $2
                            """, str(embedding), conv['id'])
                            
                            processed += 1
                            
                            if processed % 10 == 0:
                                logger.info(f"Generated embeddings for {processed}/{total_conversations} conversations")
                    else:
                        failed += 1
                        logger.warning(f"Failed to generate embedding for conversation {conv['id']}: {embed_response.status_code}")
                        
                except Exception as e:
                    failed += 1
                    logger.error(f"Error processing conversation {conv['id']}: {str(e)}")
                
                # Small delay to avoid overwhelming the embedding service
                await asyncio.sleep(0.1)
        
        await conn.close()
        
        logger.info(f"Embedding generation complete: {processed} successful, {failed} failed")
        
        return {
            "status": "success",
            "message": f"Generated embeddings for {processed} conversations",
            "processed": processed,
            "failed": failed,
            "total": total_conversations
        }
        
    except Exception as e:
        logger.error(f"Embedding generation failed: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
            "processed": 0,
            "total": 0
        }


@app.post("/saved-searches")
async def save_search(
    name: str,
    query: str,
    search_type: str = "text",
    filters: dict = None
):
    """Save a search query for later use"""
    try:
        # For now, save to a simple JSON file - could be moved to database later
        import json
        from pathlib import Path
        
        saved_searches_file = Path("/Users/tem/humanizer-lighthouse/saved_searches.json")
        
        # Load existing searches
        if saved_searches_file.exists():
            with open(saved_searches_file, 'r') as f:
                searches = json.load(f)
        else:
            searches = {}
        
        # Add new search
        search_id = f"search_{len(searches) + 1}"
        searches[search_id] = {
            "id": search_id,
            "name": name,
            "query": query,
            "search_type": search_type,
            "filters": filters or {},
            "created_at": datetime.now().isoformat(),
            "last_used": datetime.now().isoformat()
        }
        
        # Save back to file
        with open(saved_searches_file, 'w') as f:
            json.dump(searches, f, indent=2)
        
        return {
            "status": "success",
            "search_id": search_id,
            "message": f"Search '{name}' saved successfully"
        }
        
    except Exception as e:
        logger.error(f"Save search failed: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }


@app.get("/saved-searches")
async def get_saved_searches():
    """Get all saved searches"""
    try:
        import json
        from pathlib import Path
        
        saved_searches_file = Path("/Users/tem/humanizer-lighthouse/saved_searches.json")
        
        if saved_searches_file.exists():
            with open(saved_searches_file, 'r') as f:
                searches = json.load(f)
            return {
                "status": "success",
                "searches": list(searches.values())
            }
        else:
            return {
                "status": "success", 
                "searches": []
            }
            
    except Exception as e:
        logger.error(f"Get saved searches failed: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
            "searches": []
        }


@app.post("/transformation-queue")
async def add_to_transformation_queue(
    content_ids: list,
    transformation_type: str,  # "humanize", "maieutic", "translate", etc.
    priority: str = "normal"  # "high", "normal", "low"
):
    """Add content to transformation processing queue"""
    try:
        import json
        from pathlib import Path
        
        queue_file = Path("/Users/tem/humanizer-lighthouse/transformation_queue.json")
        
        # Load existing queue
        if queue_file.exists():
            with open(queue_file, 'r') as f:
                queue = json.load(f)
        else:
            queue = {"items": [], "next_id": 1}
        
        # Add items to queue
        added_items = []
        for content_id in content_ids:
            item = {
                "id": queue["next_id"],
                "content_id": content_id,
                "transformation_type": transformation_type,
                "priority": priority,
                "status": "pending",
                "created_at": datetime.now().isoformat(),
                "started_at": None,
                "completed_at": None,
                "result": None,
                "error": None
            }
            queue["items"].append(item)
            added_items.append(item)
            queue["next_id"] += 1
        
        # Save queue
        with open(queue_file, 'w') as f:
            json.dump(queue, f, indent=2)
        
        return {
            "status": "success",
            "added_count": len(added_items),
            "queue_items": added_items
        }
        
    except Exception as e:
        logger.error(f"Add to transformation queue failed: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }


@app.get("/transformation-queue")
async def get_transformation_queue():
    """Get current transformation queue"""
    try:
        import json
        from pathlib import Path
        
        queue_file = Path("/Users/tem/humanizer-lighthouse/transformation_queue.json")
        
        if queue_file.exists():
            with open(queue_file, 'r') as f:
                queue = json.load(f)
            return {
                "status": "success",
                "queue": queue["items"],
                "pending_count": len([item for item in queue["items"] if item["status"] == "pending"]),
                "total_count": len(queue["items"])
            }
        else:
            return {
                "status": "success",
                "queue": [],
                "pending_count": 0,
                "total_count": 0
            }
            
    except Exception as e:
        logger.error(f"Get transformation queue failed: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }


@app.post("/process-local-folder")
async def process_local_folder(
    background_tasks: BackgroundTasks,
    folder_path: str = "/Users/tem/nab/exploded_archive_node",
    max_conversations: Optional[int] = None
):
    """Process a local Node Archive Browser folder one conversation at a time"""
    try:
        logger.info(f"=== FOLDER-BY-FOLDER PROCESSING STARTED ===")
        logger.info(f"📁 Processing folder: {folder_path}")
        
        # Import the folder processor
        import sys
        sys.path.append('/Users/tem/humanizer-lighthouse')
        from folder_by_folder_processor import FolderByFolderProcessor
        
        # Validate path
        if not os.path.exists(folder_path):
            raise HTTPException(
                status_code=404, 
                detail=f"Folder not found: {folder_path}"
            )
        
        # Create processor and session
        processor = FolderByFolderProcessor(folder_path)
        processing_sessions[processor.session_id] = SimpleArchiveProcessor()  # For compatibility
        
        # Start background processing
        background_tasks.add_task(
            run_folder_by_folder_processing,
            processor.session_id,
            folder_path,
            max_conversations
        )
        
        return {
            "status": "started",
            "session_id": processor.session_id,
            "folder_path": folder_path,
            "processing_approach": "folder_by_folder",
            "progress_url": f"/progress/{processor.session_id}",
            "message": "Folder-by-folder processing started - no file upload limits!"
        }
        
    except Exception as e:
        logger.error(f"Folder processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def run_folder_by_folder_processing(
    session_id: str,
    folder_path: str,
    max_conversations: Optional[int] = None
):
    """Run folder-by-folder processing with logging"""
    try:
        logger.info(f"=== FOLDER PROCESSING SESSION {session_id} ===")
        
        # Import the folder processor
        import sys
        sys.path.append('/Users/tem/humanizer-lighthouse')
        from folder_by_folder_processor import FolderByFolderProcessor
        
        # Create processor
        processor = FolderByFolderProcessor(folder_path)
        
        # Analysis phase
        logger.info("Step 1: Analyzing folder structure...")
        analysis = await processor.analyze_archive()
        logger.info(f"📊 Analysis complete: {analysis['conversation_folders']} folders found")
        
        # Processing phase
        logger.info("Step 2: Processing conversations folder by folder...")
        results = await processor.process_all_folders(max_conversations)
        
        logger.info(f"✅ Folder-by-folder processing complete!")
        logger.info(f"📈 Results: {results['stats']['processed_conversations']} conversations processed")
        logger.info(f"📝 Messages: {results['stats']['total_messages']:,}")
        logger.info(f"📎 Media files: {results['stats']['total_media_files']:,}")
        
    except Exception as e:
        logger.error(f"Folder processing failed for session {session_id}: {str(e)}")
        if session_id in processing_sessions:
            # Update session with error
            pass


@app.post("/generate-hierarchical-chunks")
async def generate_hierarchical_chunks(request: ChunkingRequest):
    """Generate hierarchical chunks and summaries for content"""
    try:
        import asyncpg
        
        conn = await asyncpg.connect(
            host="localhost",
            database="humanizer_archive", 
            user="tem"
        )
        
        # Get content to process
        if request.content_ids:
            query = """
                SELECT id, title, body_text, content_type
                FROM archived_content 
                WHERE id = ANY($1) AND body_text IS NOT NULL
                ORDER BY id
            """
            content_items = await conn.fetch(query, request.content_ids)
        else:
            # Get content without chunks
            query = """
                SELECT ac.id, ac.title, ac.body_text, ac.content_type
                FROM archived_content ac
                LEFT JOIN content_chunks cc ON ac.id = cc.source_content_id
                WHERE ac.body_text IS NOT NULL 
                AND cc.id IS NULL
                ORDER BY ac.word_count DESC
            """
            if request.max_content:
                query += f" LIMIT {request.max_content}"
            content_items = await conn.fetch(query)
        
        if not content_items:
            await conn.close()
            return {
                "status": "success",
                "message": "No content needs chunking",
                "processed": 0,
                "total": 0
            }
        
        total_items = len(content_items)
        processed = 0
        failed = 0
        
        logger.info(f"Starting hierarchical chunking for {total_items} content items")
        
        for item in content_items:
            try:
                content = item['body_text'] or item['title'] or ""
                if not content.strip() or len(content.split()) < 10:
                    continue
                
                # Generate hierarchical chunks
                chunks = await process_content_hierarchically(
                    content, 
                    str(item['id']),
                    item['content_type'] or 'conversation'
                )
                
                # Store chunks in database
                for chunk_data in chunks:
                    await conn.execute("""
                        INSERT INTO content_chunks 
                        (chunk_id, source_content_id, content, summary, chunk_type, 
                         level, parent_chunk_id, word_count, start_position, 
                         end_position, metadata)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                        ON CONFLICT (chunk_id) DO UPDATE SET
                        content = EXCLUDED.content,
                        summary = EXCLUDED.summary,
                        updated_at = NOW()
                    """, 
                    chunk_data["chunk_id"],
                    item['id'],
                    chunk_data["content"],
                    chunk_data["summary"],
                    chunk_data["chunk_type"],
                    chunk_data["level"],
                    chunk_data["parent_chunk_id"],
                    chunk_data["word_count"],
                    chunk_data["start_position"],
                    chunk_data["end_position"],
                    chunk_data["metadata"]
                    )
                
                processed += 1
                
                if processed % 10 == 0:
                    logger.info(f"Processed {processed}/{total_items} content items")
                    
            except Exception as e:
                logger.error(f"Error processing content {item['id']}: {e}")
                failed += 1
                continue
        
        await conn.close()
        
        logger.info(f"Hierarchical chunking complete: {processed} successful, {failed} failed")
        
        return {
            "status": "success",
            "message": f"Generated hierarchical chunks for {processed} content items",
            "processed": processed,
            "failed": failed,
            "total": total_items,
            "processing_time": "N/A"  # Add timing if needed
        }
        
    except Exception as e:
        logger.error(f"Error in hierarchical chunking: {e}")
        return {
            "status": "error",
            "message": str(e),
            "processed": 0,
            "total": 0
        }


if __name__ == "__main__":
    # Configure uvicorn for large uploads
    import uvicorn.config
    
    # Set large upload limits
    config = uvicorn.Config(
        app,
        host="127.0.0.1",
        port=7200,
        log_level="info",
        # Large upload configuration
        limit_max_requests=None,
        limit_concurrency=None,
        timeout_keep_alive=120,  # Longer timeout for large uploads
        timeout_graceful_shutdown=60,
        # HTTP configuration for large payloads
        h11_max_incomplete_event_size=100 * 1024 * 1024,  # 100MB for large messages
        access_log=True,
        # Worker configuration
        loop="asyncio",
        lifespan="on",
        # Try to override any uvicorn limits
        ws_max_size=100 * 1024 * 1024,  # 100MB websocket messages
        ws_ping_interval=20,
        ws_ping_timeout=20
    )
    
    server = uvicorn.Server(config)
    logger.info("🚀 Starting Large-Scale Archive Upload Server")
    logger.info("   📁 Max files: 10,000")
    logger.info("   💾 Max upload: 10GB")
    logger.info("   📝 Large message support: 100MB")
    
    server.run()