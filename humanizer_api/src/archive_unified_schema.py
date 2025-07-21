"""
Unified Archive Schema for PostgreSQL
Consolidates all archive sources into a single searchable database
"""

import os
import json
import logging
import asyncio
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any, Union
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum

# Setup logging
logger = logging.getLogger(__name__)

import asyncpg
import numpy as np
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, text, MetaData, Table, Column, BigInteger, String, Text, DateTime, Float, Boolean, JSON
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from pgvector.sqlalchemy import Vector

Base = declarative_base()

class SourceType(str, Enum):
    """Types of archive sources"""
    NODE_CONVERSATION = "node_conversation"
    TWITTER = "twitter"
    EMAIL = "email" 
    SLACK = "slack"
    DISCORD = "discord"
    TELEGRAM = "telegram"
    FILE_SYSTEM = "file_system"
    WEB_CONTENT = "web_content"
    SOCIAL_MEDIA = "social_media"

class ContentType(str, Enum):
    """Types of content within archives"""
    MESSAGE = "message"
    CONVERSATION = "conversation"
    THREAD = "thread"
    DOCUMENT = "document"
    MEDIA = "media"
    ANNOTATION = "annotation"

class ArchiveContentORM(Base):
    """SQLAlchemy ORM model for unified archive content"""
    __tablename__ = "archived_content"
    
    # Primary identification
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    source_type = Column(String(50), nullable=False, index=True)
    source_id = Column(String(255), nullable=False, index=True)
    parent_id = Column(BigInteger, nullable=True, index=True)  # For threading
    
    # Content classification
    content_type = Column(String(50), nullable=False, index=True)
    title = Column(Text, nullable=True)
    body_text = Column(Text, nullable=True)
    raw_content = Column(JSONB, nullable=True)
    
    # Metadata
    author = Column(String(255), nullable=True, index=True)
    participants = Column(ARRAY(String), nullable=True)
    timestamp = Column(DateTime(timezone=True), nullable=True, index=True)
    source_metadata = Column(JSONB, nullable=True)
    
    # AI Processing Results - Using pgvector for 768-dimensional nomic embeddings
    semantic_vector = Column(Vector(768), nullable=True)  # pgvector for efficient similarity search
    extracted_attributes = Column(JSONB, nullable=True)
    content_quality_score = Column(Float, nullable=True)
    processing_status = Column(String(50), default="pending")
    
    # Search and indexing
    search_terms = Column(ARRAY(String), nullable=True)
    language_detected = Column(String(10), nullable=True)
    word_count = Column(BigInteger, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    
    # Relationships and links
    related_content_ids = Column(ARRAY(BigInteger), nullable=True)
    external_links = Column(ARRAY(String), nullable=True)
    
    def __repr__(self):
        return f"<ArchiveContent(id={self.id}, source={self.source_type}, type={self.content_type})>"

@dataclass
class ArchiveContent:
    """Pydantic-style dataclass for archive content"""
    source_type: SourceType
    source_id: str
    content_type: ContentType
    body_text: Optional[str] = None
    title: Optional[str] = None
    raw_content: Optional[Dict[str, Any]] = None
    author: Optional[str] = None
    participants: List[str] = field(default_factory=list)
    timestamp: Optional[datetime] = None
    source_metadata: Dict[str, Any] = field(default_factory=dict)
    parent_id: Optional[int] = None
    
    # Auto-generated fields
    id: Optional[int] = None
    semantic_vector: Optional[List[float]] = None
    extracted_attributes: Dict[str, Any] = field(default_factory=dict)
    content_quality_score: Optional[float] = None
    processing_status: str = "pending"
    search_terms: List[str] = field(default_factory=list)
    language_detected: Optional[str] = None
    word_count: Optional[int] = None
    related_content_ids: List[int] = field(default_factory=list)
    external_links: List[str] = field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class UnifiedArchiveDB:
    """Database interface for unified archive operations"""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(bind=self.engine)
        
    async def create_tables(self):
        """Create all archive tables"""
        Base.metadata.create_all(bind=self.engine)
        
        # Create additional indexes for performance
        with self.engine.connect() as conn:
            # Full-text search index
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_archived_content_fts 
                ON archived_content USING gin(to_tsvector('english', coalesce(title, '') || ' ' || coalesce(body_text, '')))
            """))
            
            # Composite indexes for common queries
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_archived_content_source_timestamp 
                ON archived_content(source_type, timestamp DESC)
            """))
            
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_archived_content_author_timestamp 
                ON archived_content(author, timestamp DESC)
            """))
            
            # Vector similarity index (when we have vector support)
            try:
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_archived_content_vector 
                    ON archived_content USING ivfflat (semantic_vector vector_cosine_ops)
                """))
            except Exception:
                # Vector extension not available
                pass
            
            conn.commit()
    
    def insert_content(self, content: ArchiveContent) -> int:
        """Insert new archive content"""
        with self.SessionLocal() as session:
            # Convert to ORM object
            orm_content = ArchiveContentORM(
                source_type=content.source_type.value,
                source_id=content.source_id,
                parent_id=content.parent_id,
                content_type=content.content_type.value,
                title=content.title,
                body_text=content.body_text,
                raw_content=content.raw_content,
                author=content.author,
                participants=content.participants,
                timestamp=content.timestamp,
                source_metadata=content.source_metadata,
                semantic_vector=content.semantic_vector,
                extracted_attributes=content.extracted_attributes,
                content_quality_score=content.content_quality_score,
                processing_status=content.processing_status,
                search_terms=content.search_terms,
                language_detected=content.language_detected,
                word_count=len(content.body_text.split()) if content.body_text else None,
                related_content_ids=content.related_content_ids,
                external_links=content.external_links
            )
            
            session.add(orm_content)
            session.commit()
            session.refresh(orm_content)
            return orm_content.id
    
    def batch_insert_content(self, contents: List[ArchiveContent]) -> List[int]:
        """Batch insert multiple archive contents"""
        with self.SessionLocal() as session:
            orm_contents = []
            for content in contents:
                orm_content = ArchiveContentORM(
                    source_type=content.source_type.value,
                    source_id=content.source_id,
                    parent_id=content.parent_id,
                    content_type=content.content_type.value,
                    title=content.title,
                    body_text=content.body_text,
                    raw_content=content.raw_content,
                    author=content.author,
                    participants=content.participants,
                    timestamp=content.timestamp,
                    source_metadata=content.source_metadata,
                    word_count=len(content.body_text.split()) if content.body_text else None
                )
                orm_contents.append(orm_content)
            
            session.add_all(orm_contents)
            session.commit()
            
            return [content.id for content in orm_contents]
    
    def search_content(
        self, 
        query: str = None,
        source_types: List[SourceType] = None,
        content_types: List[ContentType] = None,
        author: str = None,
        date_from: datetime = None,
        date_to: datetime = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[ArchiveContent]:
        """Search archive content with various filters"""
        
        with self.SessionLocal() as session:
            query_obj = session.query(ArchiveContentORM)
            
            # Apply filters
            if source_types:
                query_obj = query_obj.filter(ArchiveContentORM.source_type.in_([st.value for st in source_types]))
            
            if content_types:
                query_obj = query_obj.filter(ArchiveContentORM.content_type.in_([ct.value for ct in content_types]))
            
            if author:
                query_obj = query_obj.filter(ArchiveContentORM.author.ilike(f"%{author}%"))
            
            if date_from:
                query_obj = query_obj.filter(ArchiveContentORM.timestamp >= date_from)
            
            if date_to:
                query_obj = query_obj.filter(ArchiveContentORM.timestamp <= date_to)
            
            # Full-text search
            if query:
                query_obj = query_obj.filter(
                    text("to_tsvector('english', coalesce(title, '') || ' ' || coalesce(body_text, '')) @@ plainto_tsquery(:search_query)")
                ).params(search_query=query)
            
            # Apply pagination and ordering
            results = query_obj.order_by(ArchiveContentORM.timestamp.desc()).offset(offset).limit(limit).all()
            
            # Convert back to dataclass
            return [self._orm_to_dataclass(result) for result in results]
    
    def get_conversation_thread(self, parent_id: int) -> List[ArchiveContent]:
        """Get all messages in a conversation thread"""
        with self.SessionLocal() as session:
            results = session.query(ArchiveContentORM).filter(
                ArchiveContentORM.parent_id == parent_id
            ).order_by(ArchiveContentORM.timestamp).all()
            
            return [self._orm_to_dataclass(result) for result in results]
    
    def update_processing_status(self, content_id: int, status: str, attributes: Dict[str, Any] = None, quality_score: float = None):
        """Update AI processing results"""
        with self.SessionLocal() as session:
            content = session.get(ArchiveContentORM, content_id)
            if content:
                content.processing_status = status
                if attributes:
                    content.extracted_attributes = attributes
                if quality_score is not None:
                    content.content_quality_score = quality_score
                content.updated_at = datetime.now(timezone.utc)
                session.commit()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get archive statistics"""
        with self.SessionLocal() as session:
            total_count = session.query(ArchiveContentORM).count()
            
            # Count by source type
            source_counts = session.query(
                ArchiveContentORM.source_type,
                session.query().count()
            ).group_by(ArchiveContentORM.source_type).all()
            
            # Count by content type
            content_counts = session.query(
                ArchiveContentORM.content_type,
                session.query().count()
            ).group_by(ArchiveContentORM.content_type).all()
            
            # Processing status
            processing_counts = session.query(
                ArchiveContentORM.processing_status,
                session.query().count()
            ).group_by(ArchiveContentORM.processing_status).all()
            
            return {
                "total_content": total_count,
                "by_source_type": dict(source_counts),
                "by_content_type": dict(content_counts),
                "by_processing_status": dict(processing_counts)
            }
    
    def _orm_to_dataclass(self, orm_obj: ArchiveContentORM) -> ArchiveContent:
        """Convert ORM object to dataclass"""
        return ArchiveContent(
            id=orm_obj.id,
            source_type=SourceType(orm_obj.source_type),
            source_id=orm_obj.source_id,
            parent_id=orm_obj.parent_id,
            content_type=ContentType(orm_obj.content_type),
            title=orm_obj.title,
            body_text=orm_obj.body_text,
            raw_content=orm_obj.raw_content or {},
            author=orm_obj.author,
            participants=orm_obj.participants or [],
            timestamp=orm_obj.timestamp,
            source_metadata=orm_obj.source_metadata or {},
            semantic_vector=list(orm_obj.semantic_vector) if orm_obj.semantic_vector else None,
            extracted_attributes=orm_obj.extracted_attributes or {},
            content_quality_score=orm_obj.content_quality_score,
            processing_status=orm_obj.processing_status,
            search_terms=orm_obj.search_terms or [],
            language_detected=orm_obj.language_detected,
            word_count=orm_obj.word_count,
            related_content_ids=orm_obj.related_content_ids or [],
            external_links=orm_obj.external_links or [],
            created_at=orm_obj.created_at,
            updated_at=orm_obj.updated_at
        )
    
    def get_content_by_id(self, content_id: int) -> Optional[ArchiveContent]:
        """Get specific content by ID"""
        try:
            with self.SessionLocal() as session:
                orm_obj = session.get(ArchiveContentORM, content_id)
                if orm_obj:
                    return self._orm_to_dataclass(orm_obj)
                return None
        except Exception as e:
            logger.error(f"Error getting content by ID {content_id}: {e}")
            return None

# SQL for manual table creation if needed
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS archived_content (
    id BIGSERIAL PRIMARY KEY,
    source_type VARCHAR(50) NOT NULL,
    source_id VARCHAR(255) NOT NULL,
    parent_id BIGINT,
    content_type VARCHAR(50) NOT NULL,
    title TEXT,
    body_text TEXT,
    raw_content JSONB,
    author VARCHAR(255),
    participants TEXT[],
    timestamp TIMESTAMPTZ,
    source_metadata JSONB,
    semantic_vector vector(768),  -- pgvector for nomic-text-embed
    extracted_attributes JSONB,
    content_quality_score FLOAT,
    processing_status VARCHAR(50) DEFAULT 'pending',
    search_terms TEXT[],
    language_detected VARCHAR(10),
    word_count BIGINT,
    related_content_ids BIGINT[],
    external_links TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_archived_content_source_type ON archived_content(source_type);
CREATE INDEX IF NOT EXISTS idx_archived_content_source_id ON archived_content(source_id);
CREATE INDEX IF NOT EXISTS idx_archived_content_parent_id ON archived_content(parent_id);
CREATE INDEX IF NOT EXISTS idx_archived_content_content_type ON archived_content(content_type);
CREATE INDEX IF NOT EXISTS idx_archived_content_author ON archived_content(author);
CREATE INDEX IF NOT EXISTS idx_archived_content_timestamp ON archived_content(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_archived_content_fts ON archived_content USING gin(to_tsvector('english', coalesce(title, '') || ' ' || coalesce(body_text, '')));
CREATE INDEX IF NOT EXISTS idx_archived_content_source_timestamp ON archived_content(source_type, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_archived_content_author_timestamp ON archived_content(author, timestamp DESC);
"""