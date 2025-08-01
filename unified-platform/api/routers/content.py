"""
Content Management Router
Handles content ingestion, storage, and retrieval with comprehensive validation
"""
import logging
import uuid
import asyncio
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from config import config
from models import (
    Content, ContentInput, ContentMetadata, ContentType, ProcessingStatus,
    SuccessResponse, ErrorResponse, User
)
from core.dependencies import (
    get_database, get_vector_db, get_llm_service, get_cache_service,
    get_current_user, CacheService, LLMService
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/ingest", response_model=SuccessResponse)
async def ingest_content(
    content_type: ContentType = Form(...),
    source: str = Form(..., min_length=1, max_length=255),
    title: Optional[str] = Form(None, max_length=500),
    author: Optional[str] = Form(None, max_length=255),
    language: str = Form("en", regex=r"^[a-z]{2}$"),
    tags: str = Form("", description="Comma-separated tags"),
    file: Optional[UploadFile] = File(None),
    text_data: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_database),
    vectordb = Depends(get_vector_db),
    llm_service: LLMService = Depends(get_llm_service),
    cache: CacheService = Depends(get_cache_service),
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Ingest content with automatic processing and embedding generation
    Supports both file upload and direct text input
    """
    
    # Validate input
    if not file and not text_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either file or text_data must be provided"
        )
    
    if file and text_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot provide both file and text_data"
        )
    
    try:
        # Process content data
        if file:
            # Validate file size
            content_size = 0
            content_data = b""
            
            while chunk := await file.read(8192):  # Read in 8KB chunks
                content_data += chunk
                content_size += len(chunk)
                
                if content_size > config.security.max_file_size_mb * 1024 * 1024:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"File too large (max {config.security.max_file_size_mb}MB)"
                    )
            
            # Convert to text based on content type
            processed_text = await _process_file_content(content_data, content_type, file.filename)
            
        else:
            # Direct text input
            if len(text_data) > config.processing.max_text_length:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"Text too long (max {config.processing.max_text_length} characters)"
                )
            processed_text = text_data
        
        # Parse tags
        tag_list = [tag.strip().lower() for tag in tags.split(",") if tag.strip()] if tags else []
        
        # Create metadata
        metadata = ContentMetadata(
            source=source,
            title=title,
            author=author,
            language=language,
            tags=tag_list
        )
        
        # Create content record
        content_id = uuid.uuid4()
        content = Content(
            id=content_id,
            content_type=content_type,
            data=processed_text,
            metadata=metadata,
            processing_status=ProcessingStatus.PROCESSING
        )
        
        # Save to database
        db.add(content)
        await db.flush()  # Get the ID without committing
        
        # Generate embedding asynchronously
        try:
            embedding = await llm_service.embed(processed_text)
            content.embedding = embedding
        except Exception as e:
            logger.warning(f"Failed to generate embedding for content {content_id}: {e}")
            content.embedding = None
        
        # Calculate quality score (placeholder implementation)
        content.quality_score = await _calculate_quality_score(processed_text)
        
        # Update processing status
        content.processing_status = ProcessingStatus.COMPLETED
        
        # Commit to database
        await db.commit()
        
        # Store in vector database if embedding was successful
        if content.embedding:
            try:
                collection = vectordb.get_or_create_collection(
                    name=config.vectordb.collection_name,
                    metadata={"dimension": config.vectordb.embedding_dimension}
                )
                
                collection.add(
                    embeddings=[content.embedding],
                    documents=[processed_text],
                    metadatas=[{
                        "content_id": str(content_id),
                        "title": title or "",
                        "source": source,
                        "content_type": content_type.value,
                        "created_at": datetime.utcnow().isoformat()
                    }],
                    ids=[str(content_id)]
                )
                
                logger.info(f"Added content {content_id} to vector database")
                
            except Exception as e:
                logger.error(f"Failed to add content {content_id} to vector database: {e}")
        
        # Cache the content for quick retrieval
        cache_key = f"content:{content_id}"
        await cache.set(cache_key, content.data, ttl=config.cache.redis_ttl_seconds)
        
        logger.info(f"Successfully ingested content {content_id} from {source}")
        
        return SuccessResponse(
            message="Content ingested successfully",
            data={
                "content_id": str(content_id),
                "processing_status": content.processing_status.value,
                "quality_score": content.quality_score,
                "has_embedding": content.embedding is not None,
                "text_length": len(processed_text)
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to ingest content: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process content"
        )


@router.get("/content/{content_id}", response_model=Content)
async def get_content(
    content_id: uuid.UUID,
    db: AsyncSession = Depends(get_database),
    cache: CacheService = Depends(get_cache_service),
    current_user: Optional[User] = Depends(get_current_user)
):
    """Retrieve content by ID with caching"""
    
    # Try cache first
    cache_key = f"content:{content_id}"
    cached_content = await cache.get(cache_key)
    
    if not cached_content:
        # Query database
        result = await db.execute(
            select(Content).where(Content.id == content_id)
        )
        content = result.scalar_one_or_none()
        
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content not found"
            )
        
        # Cache for future requests
        await cache.set(cache_key, content.data)
        
    else:
        # For cached content, we still need the full record from DB
        result = await db.execute(
            select(Content).where(Content.id == content_id)
        )
        content = result.scalar_one_or_none()
        
        if not content:
            # Cache inconsistency, remove from cache
            await cache.delete(cache_key)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content not found"
            )
    
    return content


@router.get("/content", response_model=List[Content])
async def list_content(
    skip: int = 0,
    limit: int = 20,
    content_type: Optional[ContentType] = None,
    source: Optional[str] = None,
    db: AsyncSession = Depends(get_database),
    current_user: Optional[User] = Depends(get_current_user)
):
    """List content with filtering and pagination"""
    
    # Validate pagination parameters
    if limit > 100:
        limit = 100
    if skip < 0:
        skip = 0
    
    # Build query
    query = select(Content)
    
    if content_type:
        query = query.where(Content.content_type == content_type)
    
    if source:
        query = query.where(Content.metadata["source"].astext == source)
    
    # Add pagination and ordering
    query = query.offset(skip).limit(limit).order_by(Content.created_at.desc())
    
    # Execute query
    result = await db.execute(query)
    content_list = result.scalars().all()
    
    return content_list


@router.delete("/content/{content_id}", response_model=SuccessResponse)
async def delete_content(
    content_id: uuid.UUID,
    db: AsyncSession = Depends(get_database),
    vectordb = Depends(get_vector_db),
    cache: CacheService = Depends(get_cache_service),
    current_user: User = Depends(get_current_user)  # Require authentication for deletion
):
    """Delete content and clean up related data"""
    
    # Check if content exists
    result = await db.execute(
        select(Content).where(Content.id == content_id)
    )
    content = result.scalar_one_or_none()
    
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    try:
        # Delete from database
        await db.execute(
            delete(Content).where(Content.id == content_id)
        )
        
        # Delete from vector database
        try:
            collection = vectordb.get_collection(config.vectordb.collection_name)
            collection.delete(ids=[str(content_id)])
            logger.info(f"Deleted content {content_id} from vector database")
        except Exception as e:
            logger.warning(f"Failed to delete content {content_id} from vector database: {e}")
        
        # Delete from cache
        cache_key = f"content:{content_id}"
        await cache.delete(cache_key)
        
        await db.commit()
        
        logger.info(f"Successfully deleted content {content_id}")
        
        return SuccessResponse(
            message="Content deleted successfully",
            data={"content_id": str(content_id)}
        )
        
    except Exception as e:
        logger.error(f"Failed to delete content {content_id}: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete content"
        )


# Helper functions
async def _process_file_content(content_data: bytes, content_type: ContentType, filename: str) -> str:
    """Process uploaded file content based on type"""
    
    if content_type == ContentType.TEXT:
        return content_data.decode('utf-8', errors='replace')
    
    elif content_type == ContentType.HTML:
        # Convert HTML to text (simplified)
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(content_data, 'html.parser')
        return soup.get_text()
    
    elif content_type == ContentType.MARKDOWN:
        return content_data.decode('utf-8', errors='replace')
    
    elif content_type == ContentType.PDF:
        # PDF processing would require additional libraries
        # For now, return placeholder
        return f"PDF content from {filename} (processing not implemented)"
    
    elif content_type in [ContentType.IMAGE, ContentType.VIDEO, ContentType.AUDIO]:
        # Media files would require different processing
        return f"Media file: {filename} ({content_type.value})"
    
    else:
        # Try to decode as text
        try:
            return content_data.decode('utf-8', errors='replace')
        except Exception:
            return f"Binary content from {filename}"


async def _calculate_quality_score(text: str) -> float:
    """Calculate content quality score (placeholder implementation)"""
    
    # Simple quality metrics
    score = 0.5  # Base score
    
    # Length factor
    if config.processing.chunk_size <= len(text) <= config.processing.max_text_length // 2:
        score += 0.2
    
    # Word count factor
    word_count = len(text.split())
    if 50 <= word_count <= 1000:
        score += 0.2
    
    # Character diversity
    unique_chars = len(set(text.lower()))
    if unique_chars > 20:
        score += 0.1
    
    return min(1.0, score)