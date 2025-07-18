"""
Archive API - Universal Content Ingestion and Semantic Search

Enhanced version incorporating insights from lpe_dev, lpe, and lpe_api versions.
Features:
- Universal content ingestion (files, text, URLs, social media)
- Semantic search with vector embeddings
- Source management and organization
- ChromaDB Memory integration for learning
- PostgreSQL/SQLite dual database support
"""

import logging
import asyncio
import json
import uuid
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from io import BytesIO

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
import httpx
from sqlalchemy import create_engine, Column, String, DateTime, Integer, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import chromadb
from sentence_transformers import SentenceTransformer

# Import our configuration
from config import get_config, HumanizerConfig

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
config = get_config()

# Database Models
Base = declarative_base()

class ArchivedContent(Base):
    __tablename__ = "archived_content"
    
    id = Column(String, primary_key=True)
    content_type = Column(String, nullable=False)
    source = Column(String, nullable=False)
    title = Column(String)
    content_hash = Column(String, unique=True, nullable=False)
    content_data = Column(Text, nullable=False)
    metadata = Column(JSON, default={})
    tags = Column(JSON, default=[])
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    file_size = Column(Integer, default=0)
    embedding_status = Column(String, default="pending")  # pending, completed, failed

class ContentSource(Base):
    __tablename__ = "content_sources"
    
    id = Column(String, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    source_type = Column(String, nullable=False)  # file, url, social, email, manual
    description = Column(Text)
    metadata = Column(JSON, default={})
    content_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow)

# Pydantic Models
class ContentIngestionRequest(BaseModel):
    content_type: str = Field(..., description="Type of content: text, image, document, url")
    source: str = Field(..., description="Source identifier")
    title: Optional[str] = Field(None, description="Content title")
    data: Optional[str] = Field(None, description="Text content")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
    
    @validator('content_type')
    def validate_content_type(cls, v):
        valid_types = ['text', 'image', 'document', 'url', 'json', 'audio', 'video']
        if v not in valid_types:
            raise ValueError(f'Content type must be one of {valid_types}')
        return v

class SearchRequest(BaseModel):
    query: str = Field(..., description="Search query")
    content_type: Optional[str] = Field(None, description="Filter by content type")
    source: Optional[str] = Field(None, description="Filter by source")
    tags: List[str] = Field(default_factory=list, description="Filter by tags")
    limit: int = Field(default=50, ge=1, le=500)
    offset: int = Field(default=0, ge=0)
    search_type: str = Field(default="hybrid", description="Search type: semantic, fulltext, hybrid")
    min_similarity: float = Field(default=0.3, ge=0.0, le=1.0)

class ArchiveStatsResponse(BaseModel):
    total_items: int
    content_types: Dict[str, int]
    sources: Dict[str, int]
    tags: Dict[str, int]
    total_size_bytes: int
    embedding_status: Dict[str, int]
    recent_activity: List[Dict[str, Any]]

# Archive API Class
class ArchiveAPI:
    def __init__(self):
        self.app = FastAPI(
            title="Humanizer Archive API",
            description="Universal content ingestion and semantic search",
            version="1.0.0"
        )
        
        self.config = config
        self.setup_middleware()
        self.setup_database()
        self.setup_embedding_model()
        self.setup_chromadb()
        self.setup_routes()
        
        # HTTP client for URL processing
        self.http_client = httpx.AsyncClient(timeout=30.0)
    
    def setup_middleware(self):
        """Setup CORS and other middleware"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=self.config.api.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    def setup_database(self):
        """Setup database connection"""
        database_url = self.config.get_database_url()
        self.engine = create_engine(database_url)
        Base.metadata.create_all(bind=self.engine)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        logger.info(f"Database initialized: {database_url}")
    
    def setup_embedding_model(self):
        """Setup sentence transformer model for embeddings"""
        try:
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Embedding model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            self.embedding_model = None
    
    def setup_chromadb(self):
        """Setup ChromaDB for vector storage"""
        try:
            self.chroma_client = chromadb.PersistentClient(path=self.config.database.chromadb_path)
            self.chroma_collection = self.chroma_client.get_or_create_collection(
                name="archived_content",
                metadata={"description": "Humanizer archived content with embeddings"}
            )
            logger.info("ChromaDB initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            self.chroma_client = None
            self.chroma_collection = None
    
    def get_db(self):
        """Database dependency"""
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    def setup_routes(self):
        """Setup API routes"""
        
        @self.app.post("/ingest")
        async def ingest_content(
            background_tasks: BackgroundTasks,
            content_type: str = Form(...),
            source: str = Form(...),
            title: Optional[str] = Form(None),
            data: Optional[str] = Form(None),
            metadata: str = Form("{}"),
            tags: str = Form("[]"),
            file: Optional[UploadFile] = File(None),
            db: Session = Depends(self.get_db)
        ):
            """Ingest content from various sources"""
            try:
                # Parse metadata and tags
                parsed_metadata = json.loads(metadata) if metadata else {}
                parsed_tags = json.loads(tags) if tags else []
                
                # Process content based on type
                content_data = ""
                file_size = 0
                
                if file:
                    # Handle file upload
                    file_content = await file.read()
                    file_size = len(file_content)
                    content_data = await self._process_file(file, file_content)
                    
                    # Update metadata with file info
                    parsed_metadata.update({
                        "filename": file.filename,
                        "content_type": file.content_type,
                        "file_size": file_size,
                        "upload_method": "file"
                    })
                elif data:
                    # Handle text/data input
                    content_data = data
                    file_size = len(data.encode('utf-8'))
                    parsed_metadata["upload_method"] = "text"
                else:
                    raise HTTPException(status_code=400, detail="Either file or data must be provided")
                
                # Create content hash for deduplication
                content_hash = hashlib.sha256(content_data.encode('utf-8')).hexdigest()
                
                # Check for duplicates
                existing = db.query(ArchivedContent).filter(
                    ArchivedContent.content_hash == content_hash
                ).first()
                
                if existing:
                    return {
                        "status": "duplicate",
                        "content_id": existing.id,
                        "message": "Content already exists in archive"
                    }
                
                # Create new content record
                content_id = str(uuid.uuid4())
                archived_content = ArchivedContent(
                    id=content_id,
                    content_type=content_type,
                    source=source,
                    title=title or f"Content {content_id[:8]}",
                    content_hash=content_hash,
                    content_data=content_data,
                    metadata=parsed_metadata,
                    tags=parsed_tags,
                    file_size=file_size
                )
                
                db.add(archived_content)
                
                # Update or create source record
                await self._update_source_record(db, source, content_type, parsed_metadata)
                
                db.commit()
                
                # Schedule background embedding generation
                background_tasks.add_task(self._generate_embedding, content_id, content_data)
                
                # Log to ChromaDB Memory
                await self._log_to_memory(
                    f"Content ingested: {content_type} from {source}",
                    {"content_id": content_id, "source": source, "type": content_type}
                )
                
                return {
                    "status": "ingested",
                    "content_id": content_id,
                    "content_type": content_type,
                    "source": source,
                    "metadata": {
                        "size": file_size,
                        "hash": content_hash,
                        "embedding_status": "pending"
                    }
                }
                
            except Exception as e:
                logger.error(f"Ingestion error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/search")
        async def search_content(
            request: SearchRequest,
            db: Session = Depends(self.get_db)
        ):
            """Search content with semantic and full-text capabilities"""
            try:
                results = []
                
                if request.search_type in ["semantic", "hybrid"] and self.chroma_collection:
                    # Semantic search
                    semantic_results = await self._semantic_search(request)
                    results.extend(semantic_results)
                
                if request.search_type in ["fulltext", "hybrid"]:
                    # Full-text search
                    fulltext_results = await self._fulltext_search(request, db)
                    results.extend(fulltext_results)
                
                # Remove duplicates and sort by relevance
                seen_ids = set()
                unique_results = []
                for result in results:
                    if result["content_id"] not in seen_ids:
                        seen_ids.add(result["content_id"])
                        unique_results.append(result)
                
                # Sort by relevance score
                unique_results.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
                
                # Apply pagination
                paginated_results = unique_results[request.offset:request.offset + request.limit]
                
                return {
                    "query": request.query,
                    "search_type": request.search_type,
                    "total_results": len(unique_results),
                    "returned_results": len(paginated_results),
                    "results": paginated_results
                }
                
            except Exception as e:
                logger.error(f"Search error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/content/{content_id}")
        async def get_content(content_id: str, db: Session = Depends(self.get_db)):
            """Retrieve specific content by ID"""
            content = db.query(ArchivedContent).filter(ArchivedContent.id == content_id).first()
            
            if not content:
                raise HTTPException(status_code=404, detail="Content not found")
            
            return {
                "content_id": content.id,
                "content_type": content.content_type,
                "source": content.source,
                "title": content.title,
                "content_data": content.content_data,
                "metadata": content.metadata,
                "tags": content.tags,
                "created_at": content.created_at.isoformat(),
                "file_size": content.file_size,
                "embedding_status": content.embedding_status
            }
        
        @self.app.get("/sources")
        async def list_sources(db: Session = Depends(self.get_db)):
            """List all content sources"""
            sources = db.query(ContentSource).all()
            
            return {
                "sources": [
                    {
                        "id": source.id,
                        "name": source.name,
                        "source_type": source.source_type,
                        "description": source.description,
                        "content_count": source.content_count,
                        "created_at": source.created_at.isoformat(),
                        "last_updated": source.last_updated.isoformat()
                    }
                    for source in sources
                ],
                "total_sources": len(sources)
            }
        
        @self.app.get("/stats", response_model=ArchiveStatsResponse)
        async def get_archive_stats(db: Session = Depends(self.get_db)):
            """Get comprehensive archive statistics"""
            
            # Basic counts
            total_items = db.query(ArchivedContent).count()
            
            # Content type distribution
            content_types = {}
            type_results = db.execute(
                "SELECT content_type, COUNT(*) FROM archived_content GROUP BY content_type"
            ).fetchall()
            for content_type, count in type_results:
                content_types[content_type] = count
            
            # Source distribution
            sources = {}
            source_results = db.execute(
                "SELECT source, COUNT(*) FROM archived_content GROUP BY source"
            ).fetchall()
            for source, count in source_results:
                sources[source] = count
            
            # Tag distribution (top 10)
            tags = {}
            all_content = db.query(ArchivedContent).all()
            tag_counts = {}
            for content in all_content:
                for tag in content.tags:
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1
            tags = dict(sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10])
            
            # Total size
            total_size = db.execute(
                "SELECT SUM(file_size) FROM archived_content"
            ).scalar() or 0
            
            # Embedding status
            embedding_status = {}
            status_results = db.execute(
                "SELECT embedding_status, COUNT(*) FROM archived_content GROUP BY embedding_status"
            ).fetchall()
            for status, count in status_results:
                embedding_status[status] = count
            
            # Recent activity (last 10 items)
            recent_content = db.query(ArchivedContent).order_by(
                ArchivedContent.created_at.desc()
            ).limit(10).all()
            
            recent_activity = [
                {
                    "content_id": content.id,
                    "content_type": content.content_type,
                    "source": content.source,
                    "title": content.title,
                    "created_at": content.created_at.isoformat()
                }
                for content in recent_content
            ]
            
            return ArchiveStatsResponse(
                total_items=total_items,
                content_types=content_types,
                sources=sources,
                tags=tags,
                total_size_bytes=total_size,
                embedding_status=embedding_status,
                recent_activity=recent_activity
            )
        
        @self.app.delete("/content/{content_id}")
        async def delete_content(content_id: str, db: Session = Depends(self.get_db)):
            """Delete specific content"""
            content = db.query(ArchivedContent).filter(ArchivedContent.id == content_id).first()
            
            if not content:
                raise HTTPException(status_code=404, detail="Content not found")
            
            # Remove from ChromaDB if it exists
            if self.chroma_collection:
                try:
                    self.chroma_collection.delete(ids=[content_id])
                except Exception as e:
                    logger.warning(f"Failed to delete from ChromaDB: {e}")
            
            # Remove from database
            db.delete(content)
            db.commit()
            
            return {"status": "deleted", "content_id": content_id}
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            status = {
                "status": "healthy",
                "database": "connected",
                "embedding_model": "loaded" if self.embedding_model else "failed",
                "chromadb": "connected" if self.chroma_collection else "failed",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return status
    
    async def _process_file(self, file: UploadFile, content: bytes) -> str:
        """Process uploaded file based on type"""
        try:
            if file.content_type.startswith('text/'):
                return content.decode('utf-8')
            elif file.content_type == 'application/json':
                return content.decode('utf-8')
            elif file.content_type.startswith('image/'):
                # For images, return metadata description
                return f"[IMAGE: {file.filename}, size: {len(content)} bytes, type: {file.content_type}]"
            elif file.content_type == 'application/pdf':
                # For PDFs, return metadata (future: extract text)
                return f"[PDF: {file.filename}, size: {len(content)} bytes]"
            else:
                return f"[FILE: {file.filename}, type: {file.content_type}, size: {len(content)} bytes]"
        except UnicodeDecodeError:
            return f"[BINARY FILE: {file.filename}, type: {file.content_type}, size: {len(content)} bytes]"
    
    async def _update_source_record(self, db: Session, source_name: str, content_type: str, metadata: Dict):
        """Update or create source record"""
        source = db.query(ContentSource).filter(ContentSource.name == source_name).first()
        
        if source:
            source.content_count += 1
            source.last_updated = datetime.utcnow()
        else:
            source = ContentSource(
                id=str(uuid.uuid4()),
                name=source_name,
                source_type=content_type,
                description=f"Source for {content_type} content",
                content_count=1,
                metadata=metadata
            )
            db.add(source)
    
    async def _generate_embedding(self, content_id: str, content_data: str):
        """Generate embedding for content (background task)"""
        if not self.embedding_model or not self.chroma_collection:
            return
        
        try:
            # Generate embedding
            embedding = self.embedding_model.encode(content_data).tolist()
            
            # Store in ChromaDB
            self.chroma_collection.add(
                embeddings=[embedding],
                documents=[content_data],
                ids=[content_id]
            )
            
            # Update database status
            db = self.SessionLocal()
            try:
                content = db.query(ArchivedContent).filter(ArchivedContent.id == content_id).first()
                if content:
                    content.embedding_status = "completed"
                    db.commit()
            finally:
                db.close()
            
            logger.info(f"Generated embedding for content {content_id}")
            
        except Exception as e:
            logger.error(f"Failed to generate embedding for {content_id}: {e}")
            
            # Update status to failed
            db = self.SessionLocal()
            try:
                content = db.query(ArchivedContent).filter(ArchivedContent.id == content_id).first()
                if content:
                    content.embedding_status = "failed"
                    db.commit()
            finally:
                db.close()
    
    async def _semantic_search(self, request: SearchRequest) -> List[Dict]:
        """Perform semantic search using ChromaDB"""
        if not self.chroma_collection or not self.embedding_model:
            return []
        
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(request.query).tolist()
            
            # Search ChromaDB
            results = self.chroma_collection.query(
                query_embeddings=[query_embedding],
                n_results=request.limit * 2,  # Get more results for filtering
                include=['documents', 'distances', 'metadatas']
            )
            
            semantic_results = []
            for i, (doc, distance, metadata) in enumerate(zip(
                results['documents'][0],
                results['distances'][0], 
                results['metadatas'][0] or [{}] * len(results['documents'][0])
            )):
                # Convert distance to similarity score
                similarity_score = 1.0 - distance
                
                if similarity_score >= request.min_similarity:
                    semantic_results.append({
                        "content_id": results['ids'][0][i],
                        "content_snippet": doc[:200] + "..." if len(doc) > 200 else doc,
                        "relevance_score": similarity_score,
                        "search_method": "semantic",
                        "metadata": metadata
                    })
            
            return semantic_results
            
        except Exception as e:
            logger.error(f"Semantic search error: {e}")
            return []
    
    async def _fulltext_search(self, request: SearchRequest, db: Session) -> List[Dict]:
        """Perform full-text search using database"""
        try:
            query = db.query(ArchivedContent)
            
            # Apply filters
            if request.content_type:
                query = query.filter(ArchivedContent.content_type == request.content_type)
            
            if request.source:
                query = query.filter(ArchivedContent.source == request.source)
            
            if request.tags:
                # Filter by tags (PostgreSQL JSON contains, SQLite text search)
                for tag in request.tags:
                    query = query.filter(ArchivedContent.tags.contains([tag]))
            
            # Simple text search (improve with FTS in production)
            query = query.filter(
                ArchivedContent.content_data.contains(request.query) |
                ArchivedContent.title.contains(request.query)
            )
            
            results = query.limit(request.limit).offset(request.offset).all()
            
            fulltext_results = []
            for content in results:
                # Simple relevance scoring
                relevance_score = 0.5  # Base score for text match
                if request.query.lower() in content.title.lower():
                    relevance_score += 0.3
                
                fulltext_results.append({
                    "content_id": content.id,
                    "content_snippet": content.content_data[:200] + "..." if len(content.content_data) > 200 else content.content_data,
                    "title": content.title,
                    "source": content.source,
                    "content_type": content.content_type,
                    "tags": content.tags,
                    "relevance_score": relevance_score,
                    "search_method": "fulltext",
                    "created_at": content.created_at.isoformat()
                })
            
            return fulltext_results
            
        except Exception as e:
            logger.error(f"Full-text search error: {e}")
            return []
    
    async def _log_to_memory(self, content: str, metadata: Dict):
        """Log insights to ChromaDB Memory"""
        try:
            # This would integrate with your ChromaDB Memory MCP server
            # For now, just log locally
            logger.info(f"Memory log: {content} | {metadata}")
        except Exception as e:
            logger.error(f"Failed to log to memory: {e}")

# Create and configure the Archive API
def create_archive_api() -> FastAPI:
    """Factory function to create the Archive API"""
    archive_api = ArchiveAPI()
    return archive_api.app

# For direct running
if __name__ == "__main__":
    import uvicorn
    
    config = get_config()
    app = create_archive_api()
    
    logger.info(f"Starting Archive API on port {config.api.archive_api_port}")
    uvicorn.run(
        app,
        host=config.api.host,
        port=config.api.archive_api_port,
        log_level=config.logging.level.lower()
    )
