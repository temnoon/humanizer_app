"""
Filesystem Document Ingestion API
Treats documents as hybrid conversation-message entities with hierarchical chunking and embeddings
"""

import os
import hashlib
import mimetypes
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import asyncio
import logging

from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks
from pydantic import BaseModel, Field
import psycopg2
from psycopg2.extras import RealDictCursor, execute_values
import numpy as np

# Import existing embedding and processing components
from embedding_config import get_embedding_manager, embed_text, get_embedding_dimensions
import psycopg2
from psycopg2.extras import RealDictCursor
import os

logger = logging.getLogger(__name__)

class SimplePostgreSQLConnection:
    """Simple PostgreSQL connection manager."""
    
    def __init__(self):
        self.connection_params = {
            'host': os.getenv('POSTGRES_HOST', 'localhost'),
            'port': os.getenv('POSTGRES_PORT', '5432'),
            'database': os.getenv('POSTGRES_DB', 'humanizer_db'),
            'user': os.getenv('POSTGRES_USER', 'humanizer_app'),
            'password': os.getenv('POSTGRES_PASSWORD', 'development_password')
        }
    
    def get_connection(self):
        """Get a new database connection."""
        return psycopg2.connect(**self.connection_params)

filesystem_router = APIRouter(prefix="/api/filesystem", tags=["Filesystem Ingestion"])

# Models

class FolderPermission(BaseModel):
    folder_path: str = Field(..., description="Absolute path to folder")
    is_accessible: bool = Field(default=True, description="Whether folder is accessible")
    access_level: str = Field(default="read", description="Access level: read, write, admin")

class DocumentInfo(BaseModel):
    title: str
    file_path: str
    file_size: int
    file_type: str
    file_owner: str
    file_created_at: datetime
    file_modified_at: datetime
    folder_path: str
    content_preview: str

class DocumentChunk(BaseModel):
    chunk_index: int
    chunk_type: str = Field(default="content", description="content, summary, title")
    level: int = Field(default=0, description="Hierarchy level, 0=leaf chunks")
    chunk_text: str
    chunk_size: int
    start_offset: Optional[int] = None
    end_offset: Optional[int] = None
    quality_score: Optional[float] = None
    summary_of_chunks: Optional[List[int]] = None

class IngestionJob(BaseModel):
    job_type: str
    folder_path: Optional[str] = None
    file_path: Optional[str] = None
    status: str = "pending"
    progress: float = 0.0
    total_files: int = 0
    processed_files: int = 0
    error_message: Optional[str] = None

class IngestionRequest(BaseModel):
    folder_paths: List[str] = Field(..., description="Paths to folders to ingest")
    file_types: List[str] = Field(default=["txt", "md", "py", "js", "json", "yaml", "xml"], description="File extensions to process")
    chunk_size: int = Field(default=1000, description="Characters per chunk")
    overlap_size: int = Field(default=200, description="Overlap between chunks")
    generate_summaries: bool = Field(default=True, description="Generate hierarchical summaries")
    max_summary_levels: int = Field(default=3, description="Maximum summary hierarchy levels")
    force_reprocess: bool = Field(default=False, description="Reprocess existing files")

class FolderScanResult(BaseModel):
    folder_path: str
    total_files: int
    processable_files: int
    total_size: int
    file_types: Dict[str, int]
    preview_files: List[DocumentInfo]

# Core Ingestion Engine

class FilesystemIngestionEngine:
    """Core engine for ingesting filesystem documents into PostgreSQL with hierarchical embeddings"""
    
    def __init__(self):
        self.db_connection = SimplePostgreSQLConnection()
        self.embedding_manager = get_embedding_manager()
        
        # Supported file types and their text extraction methods
        self.text_extractors = {
            '.txt': self._extract_plain_text,
            '.md': self._extract_markdown,
            '.py': self._extract_python,
            '.js': self._extract_javascript,
            '.json': self._extract_json,
            '.yaml': self._extract_yaml,
            '.yml': self._extract_yaml,
            '.xml': self._extract_xml,
            '.html': self._extract_html,
            '.css': self._extract_css,
            '.sql': self._extract_sql,
            '.sh': self._extract_shell,
            '.log': self._extract_log,
            '.pdf': self._extract_pdf_to_markdown,
            '.odt': self._extract_odt_to_markdown
        }
    
    async def scan_folder(self, folder_path: str, file_types: List[str]) -> FolderScanResult:
        """Scan a folder and return statistics about processable files"""
        
        if not os.path.exists(folder_path):
            raise HTTPException(status_code=404, detail=f"Folder not found: {folder_path}")
        
        if not os.path.isdir(folder_path):
            raise HTTPException(status_code=400, detail=f"Path is not a directory: {folder_path}")
        
        # Check if folder is accessible
        if not await self._is_folder_accessible(folder_path):
            raise HTTPException(status_code=403, detail=f"Folder not accessible: {folder_path}")
        
        total_files = 0
        processable_files = 0
        total_size = 0
        file_type_counts = {}
        preview_files = []
        
        try:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    total_files += 1
                    
                    # Get file extension
                    _, ext = os.path.splitext(file)
                    ext = ext.lower().lstrip('.')
                    
                    # Count file types
                    file_type_counts[ext] = file_type_counts.get(ext, 0) + 1
                    
                    # Check if processable
                    if ext in file_types:
                        processable_files += 1
                        file_size = os.path.getsize(file_path)
                        total_size += file_size
                        
                        # Add to preview if we haven't reached limit
                        if len(preview_files) < 10:
                            try:
                                stat = os.stat(file_path)
                                preview_files.append(DocumentInfo(
                                    title=file,
                                    file_path=file_path,
                                    file_size=file_size,
                                    file_type=ext,
                                    file_owner=str(stat.st_uid),  # Could be enhanced with actual user names
                                    file_created_at=datetime.fromtimestamp(stat.st_ctime),
                                    file_modified_at=datetime.fromtimestamp(stat.st_mtime),
                                    folder_path=root,
                                    content_preview=await self._get_file_preview(file_path, ext)
                                ))
                            except Exception as e:
                                logger.warning(f"Failed to get info for {file_path}: {e}")
        
        except PermissionError:
            raise HTTPException(status_code=403, detail=f"Permission denied accessing folder: {folder_path}")
        
        return FolderScanResult(
            folder_path=folder_path,
            total_files=total_files,
            processable_files=processable_files,
            total_size=total_size,
            file_types=file_type_counts,
            preview_files=preview_files
        )
    
    async def ingest_documents(self, request: IngestionRequest) -> str:
        """Start document ingestion job and return job ID"""
        
        # Create processing job
        job_id = await self._create_processing_job("import", request.dict())
        
        # Start background processing
        asyncio.create_task(self._process_ingestion_job(job_id, request))
        
        return job_id
    
    async def _process_ingestion_job(self, job_id: str, request: IngestionRequest):
        """Process ingestion job in background"""
        
        try:
            await self._update_job_status(job_id, "processing", 0.0)
            
            total_files = 0
            processed_files = 0
            
            # Count total files first
            for folder_path in request.folder_paths:
                scan_result = await self.scan_folder(folder_path, request.file_types)
                total_files += scan_result.processable_files
            
            await self._update_job_progress(job_id, 0.0, total_files, 0)
            
            # Process each folder
            for folder_path in request.folder_paths:
                processed_files = await self._process_folder(
                    folder_path, request, job_id, processed_files, total_files
                )
            
            await self._update_job_status(job_id, "completed", 100.0)
            logger.info(f"Ingestion job {job_id} completed: {processed_files}/{total_files} files")
            
        except Exception as e:
            logger.error(f"Ingestion job {job_id} failed: {e}")
            await self._update_job_status(job_id, "failed", 0.0, str(e))
    
    async def _process_folder(self, folder_path: str, request: IngestionRequest, 
                            job_id: str, processed_files: int, total_files: int) -> int:
        """Process all files in a folder"""
        
        try:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    _, ext = os.path.splitext(file)
                    ext = ext.lower().lstrip('.')
                    
                    if ext in request.file_types:
                        try:
                            await self._process_single_file(file_path, request)
                            processed_files += 1
                            
                            # Update progress
                            progress = (processed_files / total_files) * 100
                            await self._update_job_progress(job_id, progress, total_files, processed_files)
                            
                        except Exception as e:
                            logger.warning(f"Failed to process {file_path}: {e}")
                            
        except Exception as e:
            logger.error(f"Failed to process folder {folder_path}: {e}")
            
        return processed_files
    
    async def _process_single_file(self, file_path: str, request: IngestionRequest):
        """Process a single file into document chunks with embeddings"""
        
        # Get file metadata
        stat = os.stat(file_path)
        file_hash = await self._calculate_file_hash(file_path)
        
        # Check if file already exists and skip if not force reprocessing
        if not request.force_reprocess:
            existing_doc = await self._get_existing_document(file_path, file_hash)
            if existing_doc:
                logger.info(f"Skipping existing file: {file_path}")
                return existing_doc['id']
        
        # Extract text content
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        if ext not in self.text_extractors:
            raise ValueError(f"Unsupported file type: {ext}")
        
        content = await self.text_extractors[ext](file_path)
        
        if not content or len(content.strip()) < 10:
            logger.warning(f"No meaningful content in {file_path}")
            return None
        
        # Create document conversation
        conversation_id = await self._create_document_conversation(file_path, stat, file_hash, content)
        
        # Create content chunks
        chunks = await self._create_content_chunks(content, request.chunk_size, request.overlap_size)
        
        # Store chunks with embeddings
        chunk_ids = await self._store_chunks(conversation_id, chunks)
        
        # Generate hierarchical summaries if requested
        if request.generate_summaries:
            await self._generate_hierarchical_summaries(
                conversation_id, chunk_ids, request.max_summary_levels
            )
        
        logger.info(f"Processed {file_path}: {len(chunks)} chunks, conversation {conversation_id}")
        return conversation_id
    
    async def _create_document_conversation(self, file_path: str, stat: os.stat_result, 
                                          file_hash: str, content: str) -> int:
        """Create a conversation entry for the document"""
        
        filename = os.path.basename(file_path)
        folder_path = os.path.dirname(file_path)
        _, ext = os.path.splitext(filename)
        ext = ext.lower().lstrip('.')
        
        # Create title from filename
        title = os.path.splitext(filename)[0].replace('_', ' ').replace('-', ' ').title()
        
        # Create conversation
        query = """
        INSERT INTO conversations (
            title, source, is_document, file_path, file_size, file_hash,
            file_owner, file_created_at, file_modified_at, file_type,
            import_source, folder_path, created_at
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        ) RETURNING id
        """
        
        values = (
            title, 'filesystem', True, file_path, stat.st_size, file_hash,
            str(stat.st_uid), datetime.fromtimestamp(stat.st_ctime),
            datetime.fromtimestamp(stat.st_mtime), ext, 'filesystem_ingestion',
            folder_path, datetime.now()
        )
        
        with self.db_connection.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, values)
                conversation_id = cursor.fetchone()[0]
                conn.commit()
                
        return conversation_id
    
    async def _create_content_chunks(self, content: str, chunk_size: int, overlap_size: int) -> List[DocumentChunk]:
        """Create overlapping chunks from content"""
        
        chunks = []
        start = 0
        chunk_index = 0
        
        while start < len(content):
            end = min(start + chunk_size, len(content))
            chunk_text = content[start:end]
            
            # Try to break on word boundaries if possible
            if end < len(content) and not content[end].isspace():
                # Find the last space before the end
                last_space = chunk_text.rfind(' ')
                if last_space > chunk_size * 0.8:  # Only if we don't lose too much
                    end = start + last_space
                    chunk_text = content[start:end]
            
            chunk = DocumentChunk(
                chunk_index=chunk_index,
                chunk_type="content",
                level=0,
                chunk_text=chunk_text.strip(),
                chunk_size=len(chunk_text),
                start_offset=start,
                end_offset=end,
                quality_score=await self._calculate_chunk_quality(chunk_text)
            )
            
            chunks.append(chunk)
            chunk_index += 1
            
            # Move start position with overlap
            start = end - overlap_size
            if start >= len(content):
                break
                
        return chunks
    
    async def _store_chunks(self, conversation_id: int, chunks: List[DocumentChunk]) -> List[int]:
        """Store chunks with embeddings in database"""
        
        chunk_ids = []
        
        with self.db_connection.get_connection() as conn:
            with conn.cursor() as cursor:
                for chunk in chunks:
                    # Generate embedding
                    embedding = embed_text(chunk.chunk_text)
                    
                    # Insert chunk
                    query = """
                    INSERT INTO document_chunks (
                        conversation_id, chunk_index, chunk_type, level, chunk_text,
                        chunk_size, start_offset, end_offset, embedding, 
                        embedding_model, quality_score, created_at
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    ) RETURNING id
                    """
                    
                    values = (
                        conversation_id, chunk.chunk_index, chunk.chunk_type,
                        chunk.level, chunk.chunk_text, chunk.chunk_size,
                        chunk.start_offset, chunk.end_offset, embedding.tolist(),
                        'nomic-embed-text', chunk.quality_score, datetime.now()
                    )
                    
                    cursor.execute(query, values)
                    chunk_id = cursor.fetchone()[0]
                    chunk_ids.append(chunk_id)
                
                conn.commit()
                
        return chunk_ids
    
    async def _generate_hierarchical_summaries(self, conversation_id: int, 
                                             chunk_ids: List[int], max_levels: int):
        """Generate hierarchical summaries of chunks"""
        
        current_level = 0
        current_chunk_ids = chunk_ids
        
        while current_level < max_levels and len(current_chunk_ids) > 1:
            # Group chunks for summarization (e.g., 5 chunks per summary)
            group_size = 5
            summary_chunk_ids = []
            
            for i in range(0, len(current_chunk_ids), group_size):
                group_chunk_ids = current_chunk_ids[i:i + group_size]
                
                # Get chunk texts
                chunk_texts = await self._get_chunk_texts(group_chunk_ids)
                
                # Generate summary
                summary_text = await self._generate_summary(chunk_texts)
                
                if summary_text:
                    # Store summary chunk
                    summary_chunk_id = await self._store_summary_chunk(
                        conversation_id, current_level + 1, summary_text, group_chunk_ids
                    )
                    summary_chunk_ids.append(summary_chunk_id)
            
            # Update hierarchy tracking
            await self._update_document_hierarchy(conversation_id, current_level + 1, 
                                                len(summary_chunk_ids), summary_chunk_ids)
            
            current_chunk_ids = summary_chunk_ids
            current_level += 1
            
            logger.info(f"Generated level {current_level} summaries: {len(summary_chunk_ids)} chunks")
    
    # Text extraction methods
    
    async def _extract_plain_text(self, file_path: str) -> str:
        """Extract plain text content"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to read {file_path}: {e}")
            return ""
    
    async def _extract_markdown(self, file_path: str) -> str:
        """Extract markdown content"""
        return await self._extract_plain_text(file_path)
    
    async def _extract_python(self, file_path: str) -> str:
        """Extract Python code with structure preservation"""
        content = await self._extract_plain_text(file_path)
        # Could add syntax analysis, docstring extraction, etc.
        return content
    
    async def _extract_javascript(self, file_path: str) -> str:
        """Extract JavaScript code"""
        return await self._extract_plain_text(file_path)
    
    async def _extract_json(self, file_path: str) -> str:
        """Extract JSON content with formatting"""
        try:
            import json
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return json.dumps(data, indent=2)
        except Exception:
            return await self._extract_plain_text(file_path)
    
    async def _extract_yaml(self, file_path: str) -> str:
        """Extract YAML content"""
        return await self._extract_plain_text(file_path)
    
    async def _extract_xml(self, file_path: str) -> str:
        """Extract XML content"""
        return await self._extract_plain_text(file_path)
    
    async def _extract_html(self, file_path: str) -> str:
        """Extract HTML content"""
        try:
            from bs4 import BeautifulSoup
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
                return soup.get_text(separator='\n', strip=True)
        except ImportError:
            return await self._extract_plain_text(file_path)
        except Exception:
            return await self._extract_plain_text(file_path)
    
    async def _extract_css(self, file_path: str) -> str:
        """Extract CSS content"""
        return await self._extract_plain_text(file_path)
    
    async def _extract_sql(self, file_path: str) -> str:
        """Extract SQL content"""
        return await self._extract_plain_text(file_path)
    
    async def _extract_shell(self, file_path: str) -> str:
        """Extract shell script content"""
        return await self._extract_plain_text(file_path)
    
    async def _extract_log(self, file_path: str) -> str:
        """Extract log file content (with potential truncation for large files)"""
        try:
            file_size = os.path.getsize(file_path)
            if file_size > 10 * 1024 * 1024:  # 10MB limit
                # Read last 5MB for large log files
                with open(file_path, 'rb') as f:
                    f.seek(-5 * 1024 * 1024, 2)
                    content = f.read().decode('utf-8', errors='ignore')
                    return f"[Log file truncated - showing last 5MB]\n\n{content}"
            else:
                return await self._extract_plain_text(file_path)
        except Exception:
            return await self._extract_plain_text(file_path)
    
    # Utility methods
    
    async def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of file"""
        hash_sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            logger.error(f"Failed to calculate hash for {file_path}: {e}")
            return ""
    
    async def _get_file_preview(self, file_path: str, file_type: str) -> str:
        """Get a preview of file content"""
        try:
            if file_type in ['txt', 'md', 'py', 'js']:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(500)  # First 500 characters
                    return content + "..." if len(content) == 500 else content
            return f"[{file_type.upper()} file]"
        except Exception:
            return "[Preview unavailable]"
    
    async def _calculate_chunk_quality(self, text: str) -> float:
        """Calculate quality score for a chunk based on content characteristics"""
        if not text.strip():
            return 0.0
        
        # Basic quality metrics
        length_score = min(1.0, len(text) / 500)  # Prefer chunks with reasonable length
        word_count = len(text.split())
        word_score = min(1.0, word_count / 50)  # Prefer chunks with good word count
        
        # Penalize chunks that are mostly whitespace or repeated characters
        unique_chars = len(set(text.lower()))
        diversity_score = min(1.0, unique_chars / 20)
        
        # Simple sentence structure check
        sentence_count = text.count('.') + text.count('!') + text.count('?')
        structure_score = min(1.0, sentence_count / 3) if sentence_count > 0 else 0.5
        
        # Combined quality score
        quality = (length_score * 0.3 + word_score * 0.3 + 
                  diversity_score * 0.2 + structure_score * 0.2)
        
        return round(quality, 3)
    
    # Database utility methods
    
    async def _is_folder_accessible(self, folder_path: str) -> bool:
        """Check if folder is marked as accessible"""
        query = "SELECT is_accessible FROM folder_permissions WHERE folder_path = %s"
        
        try:
            with self.db_connection.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (folder_path,))
                    result = cursor.fetchone()
                    return result[0] if result else True  # Default to accessible
        except Exception as e:
            logger.error(f"Failed to check folder accessibility: {e}")
            return True  # Default to accessible on error
    
    async def _get_existing_document(self, file_path: str, file_hash: str) -> Optional[Dict]:
        """Check if document already exists"""
        query = """
        SELECT id, file_hash FROM conversations 
        WHERE file_path = %s AND is_document = TRUE
        """
        
        try:
            with self.db_connection.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(query, (file_path,))
                    result = cursor.fetchone()
                    if result and result['file_hash'] == file_hash:
                        return dict(result)
        except Exception as e:
            logger.error(f"Failed to check existing document: {e}")
        
        return None
    
    async def _create_processing_job(self, job_type: str, params: Dict) -> str:
        """Create a processing job and return job ID"""
        import uuid
        job_id = str(uuid.uuid4())
        
        query = """
        INSERT INTO document_processing_jobs (id, job_type, folder_path, status, created_at)
        VALUES (%s, %s, %s, %s, %s)
        """
        
        folder_paths = params.get('folder_paths', [])
        folder_path = folder_paths[0] if folder_paths else None
        
        try:
            with self.db_connection.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (job_id, job_type, folder_path, 'pending', datetime.now()))
                    conn.commit()
        except Exception as e:
            logger.error(f"Failed to create processing job: {e}")
            raise
        
        return job_id
    
    async def _update_job_status(self, job_id: str, status: str, progress: float, error: str = None):
        """Update job status"""
        query = """
        UPDATE document_processing_jobs 
        SET status = %s, progress = %s, error_message = %s, 
            started_at = CASE WHEN status = 'pending' AND %s = 'processing' THEN %s ELSE started_at END,
            completed_at = CASE WHEN %s IN ('completed', 'failed') THEN %s ELSE completed_at END
        WHERE id = %s
        """
        
        now = datetime.now()
        
        try:
            with self.db_connection.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (status, progress, error, status, now, status, now, job_id))
                    conn.commit()
        except Exception as e:
            logger.error(f"Failed to update job status: {e}")
    
    async def _update_job_progress(self, job_id: str, progress: float, total_files: int, processed_files: int):
        """Update job progress"""
        query = """
        UPDATE document_processing_jobs 
        SET progress = %s, total_files = %s, processed_files = %s
        WHERE id = %s
        """
        
        try:
            with self.db_connection.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (progress, total_files, processed_files, job_id))
                    conn.commit()
        except Exception as e:
            logger.error(f"Failed to update job progress: {e}")
    
    async def _get_chunk_texts(self, chunk_ids: List[int]) -> List[str]:
        """Get text content for chunk IDs"""
        if not chunk_ids:
            return []
        
        placeholders = ','.join(['%s'] * len(chunk_ids))
        query = f"SELECT chunk_text FROM document_chunks WHERE id IN ({placeholders}) ORDER BY id"
        
        try:
            with self.db_connection.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, chunk_ids)
                    return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to get chunk texts: {e}")
            return []
    
    async def _generate_summary(self, chunk_texts: List[str]) -> str:
        """Generate summary of multiple text chunks using LLM"""
        if not chunk_texts:
            return ""
        
        combined_text = "\n\n".join(chunk_texts)
        
        # Simple extractive summary for now - could be enhanced with LLM
        # Take first and last sentences from each chunk
        summary_parts = []
        for text in chunk_texts:
            sentences = text.split('.')
            if len(sentences) > 2:
                summary_parts.append(sentences[0] + '.')
                if len(sentences) > 3:
                    summary_parts.append(sentences[-2] + '.')
            else:
                summary_parts.append(text[:200] + '...' if len(text) > 200 else text)
        
        return " ".join(summary_parts)
    
    async def _store_summary_chunk(self, conversation_id: int, level: int, 
                                 summary_text: str, source_chunk_ids: List[int]) -> int:
        """Store a summary chunk"""
        # Generate embedding for summary
        embedding = embed_text(summary_text)
        
        query = """
        INSERT INTO document_chunks (
            conversation_id, chunk_index, chunk_type, level, chunk_text,
            chunk_size, embedding, embedding_model, summary_of_chunks, created_at
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        ) RETURNING id
        """
        
        values = (
            conversation_id, 0, 'summary', level, summary_text,
            len(summary_text), embedding.tolist(), 'nomic-embed-text',
            source_chunk_ids, datetime.now()
        )
        
        try:
            with self.db_connection.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, values)
                    chunk_id = cursor.fetchone()[0]
                    conn.commit()
                    return chunk_id
        except Exception as e:
            logger.error(f"Failed to store summary chunk: {e}")
            return None
    
    async def _update_document_hierarchy(self, conversation_id: int, level: int, 
                                       chunk_count: int, summary_chunk_ids: List[int]):
        """Update document hierarchy tracking"""
        for chunk_id in summary_chunk_ids:
            query = """
            INSERT INTO document_hierarchy (
                conversation_id, level, chunk_count, summary_chunk_id, created_at
            ) VALUES (%s, %s, %s, %s, %s)
            """
            
            try:
                with self.db_connection.get_connection() as conn:
                    with conn.cursor() as cursor:
                        cursor.execute(query, (conversation_id, level, chunk_count, chunk_id, datetime.now()))
                        conn.commit()
            except Exception as e:
                logger.error(f"Failed to update document hierarchy: {e}")

    async def _extract_pdf_to_markdown(self, file_path: str) -> str:
        """Extract PDF content and convert to markdown format"""
        try:
            import PyPDF2
            import fitz  # PyMuPDF for better text extraction
            
            # Try PyMuPDF first (better text extraction)
            try:
                doc = fitz.open(file_path)
                markdown_content = []
                
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    text = page.get_text()
                    
                    if text.strip():
                        markdown_content.append(f"## Page {page_num + 1}\n\n{text.strip()}\n")
                
                doc.close()
                
                if markdown_content:
                    filename = os.path.basename(file_path)
                    header = f"# {filename}\n\n*Original format: PDF*\n*File path: {file_path}*\n\n---\n\n"
                    return header + "\n".join(markdown_content)
                    
            except ImportError:
                logger.warning("PyMuPDF not available, falling back to PyPDF2")
                
            # Fallback to PyPDF2
            markdown_content = []
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num, page in enumerate(pdf_reader.pages):
                    text = page.extract_text()
                    if text.strip():
                        markdown_content.append(f"## Page {page_num + 1}\n\n{text.strip()}\n")
            
            if markdown_content:
                filename = os.path.basename(file_path)
                header = f"# {filename}\n\n*Original format: PDF*\n*File path: {file_path}*\n\n---\n\n"
                return header + "\n".join(markdown_content)
            else:
                return f"# {os.path.basename(file_path)}\n\n*PDF file with no extractable text content*"
                
        except Exception as e:
            logger.error(f"Failed to extract PDF {file_path}: {e}")
            return f"# {os.path.basename(file_path)}\n\n*Error extracting PDF content: {str(e)}*"
    
    async def _extract_odt_to_markdown(self, file_path: str) -> str:
        """Extract ODT content and convert to markdown format"""
        try:
            from odf import text, teletype
            from odf.opendocument import load
            
            # Load ODT document
            doc = load(file_path)
            
            # Extract all text content
            content_parts = []
            
            # Extract paragraphs and headings
            for paragraph in doc.getElementsByType(text.P):
                para_text = teletype.extractText(paragraph)
                if para_text.strip():
                    content_parts.append(para_text.strip())
            
            # Extract headings specifically
            for heading in doc.getElementsByType(text.H):
                heading_text = teletype.extractText(heading)
                if heading_text.strip():
                    # Determine heading level (ODT outlinelevel attribute)
                    level = heading.getAttribute('outlinelevel') or '1'
                    try:
                        level_num = int(level)
                        heading_markup = '#' * min(level_num, 6)
                    except (ValueError, TypeError):
                        heading_markup = '##'
                    
                    content_parts.append(f"{heading_markup} {heading_text.strip()}")
            
            if content_parts:
                filename = os.path.basename(file_path)
                header = f"# {filename}\n\n*Original format: ODT (OpenDocument Text)*\n*File path: {file_path}*\n\n---\n\n"
                
                # Combine content with proper spacing
                markdown_content = "\n\n".join(content_parts)
                return header + markdown_content
            else:
                return f"# {os.path.basename(file_path)}\n\n*ODT file with no extractable text content*"
                
        except ImportError as e:
            logger.error(f"ODT extraction dependencies not available: {e}")
            return f"# {os.path.basename(file_path)}\n\n*ODT extraction requires odfpy library: pip install odfpy*"
        except Exception as e:
            logger.error(f"Failed to extract ODT {file_path}: {e}")
            return f"# {os.path.basename(file_path)}\n\n*Error extracting ODT content: {str(e)}*"

# Initialize the ingestion engine
ingestion_engine = FilesystemIngestionEngine()

# API Endpoints

@filesystem_router.post("/permissions/folder")
async def add_folder_permission(permission: FolderPermission):
    """Add or update folder access permissions"""
    
    if not os.path.exists(permission.folder_path):
        raise HTTPException(status_code=404, detail="Folder does not exist")
    
    if not os.path.isdir(permission.folder_path):
        raise HTTPException(status_code=400, detail="Path is not a directory")
    
    # Normalize path
    folder_path = os.path.abspath(permission.folder_path)
    
    query = """
    INSERT INTO folder_permissions (folder_path, is_accessible, access_level, added_at)
    VALUES (%s, %s, %s, %s)
    ON CONFLICT (folder_path) 
    DO UPDATE SET is_accessible = EXCLUDED.is_accessible, 
                  access_level = EXCLUDED.access_level,
                  added_at = EXCLUDED.added_at
    """
    
    try:
        with ingestion_engine.db_connection.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (folder_path, permission.is_accessible, 
                                     permission.access_level, datetime.now()))
                conn.commit()
                
        return {"status": "success", "folder_path": folder_path}
        
    except Exception as e:
        logger.error(f"Failed to add folder permission: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@filesystem_router.get("/permissions/folders")
async def get_folder_permissions():
    """Get all folder permissions"""
    
    query = """
    SELECT folder_path, is_accessible, access_level, added_at, 
           last_scanned_at, file_count, total_size
    FROM folder_permissions 
    ORDER BY added_at DESC
    """
    
    try:
        with ingestion_engine.db_connection.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query)
                return [dict(row) for row in cursor.fetchall()]
                
    except Exception as e:
        logger.error(f"Failed to get folder permissions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@filesystem_router.post("/scan")
async def scan_folder(folder_path: str, file_types: List[str] = None):
    """Scan a folder and return information about processable files"""
    
    if file_types is None:
        file_types = ["txt", "md", "py", "js", "json", "yaml", "xml"]
    
    try:
        result = await ingestion_engine.scan_folder(folder_path, file_types)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to scan folder: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@filesystem_router.post("/ingest")
async def ingest_documents(request: IngestionRequest, background_tasks: BackgroundTasks):
    """Start document ingestion process"""
    
    try:
        job_id = await ingestion_engine.ingest_documents(request)
        return {"status": "started", "job_id": job_id}
        
    except Exception as e:
        logger.error(f"Failed to start ingestion: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@filesystem_router.get("/jobs/{job_id}")
async def get_job_status(job_id: str):
    """Get status of a processing job"""
    
    query = """
    SELECT job_type, folder_path, status, progress, total_files, processed_files,
           error_message, started_at, completed_at, created_at
    FROM document_processing_jobs 
    WHERE id = %s
    """
    
    try:
        with ingestion_engine.db_connection.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, (job_id,))
                result = cursor.fetchone()
                
                if not result:
                    raise HTTPException(status_code=404, detail="Job not found")
                
                return dict(result)
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get job status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@filesystem_router.get("/jobs")
async def get_recent_jobs(limit: int = 20):
    """Get recent processing jobs"""
    
    query = """
    SELECT id, job_type, folder_path, status, progress, total_files, processed_files,
           started_at, completed_at, created_at
    FROM document_processing_jobs 
    ORDER BY created_at DESC 
    LIMIT %s
    """
    
    try:
        with ingestion_engine.db_connection.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, (limit,))
                return [dict(row) for row in cursor.fetchall()]
                
    except Exception as e:
        logger.error(f"Failed to get recent jobs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@filesystem_router.get("/documents")
async def get_documents(limit: int = 50, offset: int = 0, folder_path: str = None):
    """Get ingested documents with statistics"""
    
    base_query = """
    SELECT * FROM document_overview
    """
    
    conditions = []
    params = []
    
    if folder_path:
        conditions.append("folder_path LIKE %s")
        params.append(f"{folder_path}%")
    
    if conditions:
        base_query += " WHERE " + " AND ".join(conditions)
    
    base_query += " ORDER BY file_modified_at DESC LIMIT %s OFFSET %s"
    params.extend([limit, offset])
    
    try:
        with ingestion_engine.db_connection.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(base_query, params)
                return [dict(row) for row in cursor.fetchall()]
                
    except Exception as e:
        logger.error(f"Failed to get documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@filesystem_router.get("/documents/{document_id}/chunks")
async def get_document_chunks(document_id: int, level: int = None, chunk_type: str = None):
    """Get chunks for a specific document"""
    
    base_query = """
    SELECT id, chunk_index, chunk_type, level, chunk_text, chunk_size,
           start_offset, end_offset, quality_score, summary_of_chunks, created_at
    FROM document_chunks 
    WHERE conversation_id = %s
    """
    
    conditions = []
    params = [document_id]
    
    if level is not None:
        conditions.append("level = %s")
        params.append(level)
    
    if chunk_type:
        conditions.append("chunk_type = %s")
        params.append(chunk_type)
    
    if conditions:
        base_query += " AND " + " AND ".join(conditions)
    
    base_query += " ORDER BY level, chunk_index"
    
    try:
        with ingestion_engine.db_connection.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(base_query, params)
                return [dict(row) for row in cursor.fetchall()]
                
    except Exception as e:
        logger.error(f"Failed to get document chunks: {e}")
        raise HTTPException(status_code=500, detail=str(e))