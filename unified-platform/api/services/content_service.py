"""
Content Service
Advanced content management with processing, validation, and optimization
"""
import asyncio
import hashlib
import logging
import mimetypes
import uuid
from typing import List, Dict, Any, Optional, Tuple, BinaryIO
from pathlib import Path
import tempfile
import os

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
import chromadb
from PIL import Image
import aiofiles

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from config import config
from models import Content, ContentInput, ContentType, ProcessingStatus, ContentMetadata
from .llm_service import LLMService

logger = logging.getLogger(__name__)


class ContentProcessor:
    """Process different content types into searchable text"""
    
    def __init__(self):
        self.processors = {
            ContentType.TEXT: self._process_text,
            ContentType.HTML: self._process_html,
            ContentType.MARKDOWN: self._process_markdown,
            ContentType.JSON: self._process_json,
            ContentType.PDF: self._process_pdf,
            ContentType.IMAGE: self._process_image,
            ContentType.VIDEO: self._process_video,
            ContentType.AUDIO: self._process_audio
        }
    
    async def process(self, content_data: bytes, content_type: ContentType, filename: Optional[str] = None) -> Tuple[str, Dict[str, Any]]:
        """Process content and return text + metadata"""
        
        processor = self.processors.get(content_type, self._process_text)
        return await processor(content_data, filename)
    
    async def _process_text(self, content_data: bytes, filename: Optional[str] = None) -> Tuple[str, Dict[str, Any]]:
        """Process plain text content"""
        
        try:
            text = content_data.decode('utf-8')
        except UnicodeDecodeError:
            # Try other encodings
            for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
                try:
                    text = content_data.decode(encoding)
                    break
                except UnicodeDecodeError:
                    continue
            else:
                text = content_data.decode('utf-8', errors='replace')
        
        metadata = {
            "character_count": len(text),
            "word_count": len(text.split()),
            "line_count": len(text.splitlines()),
            "encoding": "utf-8"
        }
        
        return text, metadata
    
    async def _process_html(self, content_data: bytes, filename: Optional[str] = None) -> Tuple[str, Dict[str, Any]]:
        """Process HTML content"""
        
        try:
            from bs4 import BeautifulSoup
            
            html_content = content_data.decode('utf-8', errors='replace')
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract text content
            text = soup.get_text()
            
            # Extract metadata
            title = soup.title.string if soup.title else None
            meta_description = ""
            meta_tag = soup.find('meta', attrs={'name': 'description'})
            if meta_tag:
                meta_description = meta_tag.get('content', '')
            
            # Extract links
            links = [a.get('href') for a in soup.find_all('a', href=True)]
            
            metadata = {
                "title": title,
                "description": meta_description,
                "links_count": len(links),
                "links": links[:10],  # Store first 10 links
                "has_images": len(soup.find_all('img')) > 0,
                "word_count": len(text.split())
            }
            
            return text, metadata
            
        except Exception as e:
            logger.error(f"HTML processing failed: {e}")
            # Fallback to plain text
            return await self._process_text(content_data, filename)
    
    async def _process_markdown(self, content_data: bytes, filename: Optional[str] = None) -> Tuple[str, Dict[str, Any]]:
        """Process Markdown content"""
        
        try:
            import markdown
            from markdown.extensions import toc, meta
            
            md_content = content_data.decode('utf-8', errors='replace')
            
            # Parse markdown with extensions
            md = markdown.Markdown(extensions=['meta', 'toc'])
            html = md.convert(md_content)
            
            # Extract plain text
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            text = soup.get_text()
            
            # Extract metadata
            metadata = {
                "markdown_meta": getattr(md, 'Meta', {}),
                "table_of_contents": getattr(md, 'toc', ''),
                "heading_count": len(soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])),
                "word_count": len(text.split()),
                "original_markdown": md_content[:1000]  # Store first 1000 chars
            }
            
            return text, metadata
            
        except Exception as e:
            logger.error(f"Markdown processing failed: {e}")
            # Fallback to plain text
            return await self._process_text(content_data, filename)
    
    async def _process_json(self, content_data: bytes, filename: Optional[str] = None) -> Tuple[str, Dict[str, Any]]:
        """Process JSON content"""
        
        try:
            import json
            
            json_str = content_data.decode('utf-8', errors='replace')
            json_data = json.loads(json_str)
            
            # Convert JSON to searchable text
            text = self._json_to_text(json_data)
            
            metadata = {
                "json_keys": list(json_data.keys()) if isinstance(json_data, dict) else [],
                "json_type": type(json_data).__name__,
                "json_size": len(json_str),
                "nested_levels": self._count_json_levels(json_data)
            }
            
            return text, metadata
            
        except Exception as e:
            logger.error(f"JSON processing failed: {e}")
            # Fallback to plain text
            return await self._process_text(content_data, filename)
    
    async def _process_pdf(self, content_data: bytes, filename: Optional[str] = None) -> Tuple[str, Dict[str, Any]]:
        """Process PDF content"""
        
        try:
            import PyPDF2
            from io import BytesIO
            
            pdf_reader = PyPDF2.PdfReader(BytesIO(content_data))
            
            # Extract text from all pages
            text_pages = []
            for page in pdf_reader.pages:
                text_pages.append(page.extract_text())
            
            text = "\n\n".join(text_pages)
            
            # Extract metadata
            pdf_info = pdf_reader.metadata or {}
            
            metadata = {
                "page_count": len(pdf_reader.pages),
                "title": pdf_info.get('/Title', ''),
                "author": pdf_info.get('/Author', ''),
                "subject": pdf_info.get('/Subject', ''),
                "creator": pdf_info.get('/Creator', ''),
                "word_count": len(text.split())
            }
            
            return text, metadata
            
        except Exception as e:
            logger.error(f"PDF processing failed: {e}")
            return f"PDF file: {filename or 'unknown'} (text extraction failed)", {"error": str(e)}
    
    async def _process_image(self, content_data: bytes, filename: Optional[str] = None) -> Tuple[str, Dict[str, Any]]:
        """Process image content with OCR and analysis"""
        
        try:
            # Save to temporary file for processing
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
                temp_file.write(content_data)
                temp_path = temp_file.name
            
            try:
                # Open image with PIL
                image = Image.open(temp_path)
                
                # Basic image metadata
                metadata = {
                    "format": image.format,
                    "mode": image.mode,
                    "size": image.size,
                    "width": image.width,
                    "height": image.height,
                    "file_size": len(content_data)
                }
                
                # Try OCR if available
                text = ""
                try:
                    import pytesseract
                    text = pytesseract.image_to_string(image)
                    metadata["ocr_available"] = True
                    metadata["ocr_text_length"] = len(text)
                except ImportError:
                    text = f"Image file: {filename or 'unknown'} ({image.width}x{image.height}, {image.format})"
                    metadata["ocr_available"] = False
                
                return text, metadata
                
            finally:
                # Clean up temp file
                os.unlink(temp_path)
                
        except Exception as e:
            logger.error(f"Image processing failed: {e}")
            return f"Image file: {filename or 'unknown'} (processing failed)", {"error": str(e)}
    
    async def _process_video(self, content_data: bytes, filename: Optional[str] = None) -> Tuple[str, Dict[str, Any]]:
        """Process video content (placeholder)"""
        
        # Video processing would require ffmpeg and transcription services
        metadata = {
            "file_size": len(content_data),
            "processing": "placeholder"
        }
        
        return f"Video file: {filename or 'unknown'} (video processing not implemented)", metadata
    
    async def _process_audio(self, content_data: bytes, filename: Optional[str] = None) -> Tuple[str, Dict[str, Any]]:
        """Process audio content (placeholder)"""
        
        # Audio processing would require speech-to-text services
        metadata = {
            "file_size": len(content_data),
            "processing": "placeholder"
        }
        
        return f"Audio file: {filename or 'unknown'} (audio processing not implemented)", metadata
    
    def _json_to_text(self, data: Any, prefix: str = "") -> str:
        """Convert JSON data to searchable text"""
        
        text_parts = []
        
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    text_parts.append(f"{prefix}{key}: {self._json_to_text(value, prefix + '  ')}")
                else:
                    text_parts.append(f"{prefix}{key}: {value}")
        elif isinstance(data, list):
            for i, item in enumerate(data):
                if isinstance(item, (dict, list)):
                    text_parts.append(f"{prefix}[{i}]: {self._json_to_text(item, prefix + '  ')}")
                else:
                    text_parts.append(f"{prefix}[{i}]: {item}")
        else:
            text_parts.append(str(data))
        
        return "\n".join(text_parts)
    
    def _count_json_levels(self, data: Any, level: int = 0) -> int:
        """Count nesting levels in JSON data"""
        
        max_level = level
        
        if isinstance(data, dict):
            for value in data.values():
                if isinstance(value, (dict, list)):
                    max_level = max(max_level, self._count_json_levels(value, level + 1))
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, (dict, list)):
                    max_level = max(max_level, self._count_json_levels(item, level + 1))
        
        return max_level


class ContentService:
    """Comprehensive content management service"""
    
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
        self.processor = ContentProcessor()
        
    async def ingest_content(
        self,
        content_input: ContentInput,
        db: AsyncSession,
        vectordb: chromadb.PersistentClient,
        user_id: Optional[uuid.UUID] = None
    ) -> Content:
        """Ingest and process content with full pipeline"""
        
        # Generate content ID
        content_id = uuid.uuid4()
        
        # Calculate checksum for deduplication
        if isinstance(content_input.data, str):
            content_bytes = content_input.data.encode('utf-8')
        else:
            content_bytes = content_input.data
        
        checksum = hashlib.sha256(content_bytes).hexdigest()
        
        # Check for duplicates
        existing_content = await self._check_duplicate(db, checksum)
        if existing_content:
            logger.info(f"Duplicate content detected: {checksum}")
            return existing_content
        
        # Process content
        processed_text, processing_metadata = await self.processor.process(
            content_bytes, 
            content_input.content_type,
            getattr(content_input, 'filename', None)
        )
        
        # Merge metadata
        combined_metadata = {
            **content_input.metadata.dict(),
            **processing_metadata
        }
        
        # Create content record
        content = Content(
            id=content_id,
            content_type=content_input.content_type,
            data=processed_text,
            metadata=combined_metadata,
            processing_status=ProcessingStatus.PROCESSING,
            file_size=len(content_bytes),
            checksum=checksum,
            created_by=user_id
        )
        
        # Save to database
        db.add(content)
        await db.flush()
        
        # Process asynchronously
        try:
            # Generate embedding
            embedding = await self.llm_service.embed(processed_text)
            content.embedding = embedding
            
            # Calculate quality score
            content.quality_score = await self._calculate_quality_score(processed_text)
            
            # Update status
            content.processing_status = ProcessingStatus.COMPLETED
            
            # Store in vector database
            await self._store_in_vectordb(content, vectordb)
            
        except Exception as e:
            logger.error(f"Content processing failed for {content_id}: {e}")
            content.processing_status = ProcessingStatus.FAILED
            content.metadata["error"] = str(e)
        
        await db.commit()
        
        logger.info(f"Content ingested successfully: {content_id}")
        return content
    
    async def update_content(
        self,
        content_id: uuid.UUID,
        updates: Dict[str, Any],
        db: AsyncSession,
        vectordb: chromadb.PersistentClient,
        user_id: Optional[uuid.UUID] = None
    ) -> Optional[Content]:
        """Update existing content"""
        
        # Get existing content
        result = await db.execute(
            select(Content).where(Content.id == content_id)
        )
        content = result.scalar_one_or_none()
        
        if not content:
            return None
        
        # Create version backup
        await self._create_content_version(content, db, user_id)
        
        # Apply updates
        for field, value in updates.items():
            if hasattr(content, field):
                setattr(content, field, value)
        
        # Reprocess if content data changed
        if "data" in updates:
            content.processing_status = ProcessingStatus.PROCESSING
            
            # Regenerate embedding
            try:
                embedding = await self.llm_service.embed(content.data)
                content.embedding = embedding
                content.processing_status = ProcessingStatus.COMPLETED
                
                # Update vector database
                await self._update_in_vectordb(content, vectordb)
                
            except Exception as e:
                logger.error(f"Content update processing failed: {e}")
                content.processing_status = ProcessingStatus.FAILED
        
        await db.commit()
        return content
    
    async def delete_content(
        self,
        content_id: uuid.UUID,
        db: AsyncSession,
        vectordb: chromadb.PersistentClient
    ) -> bool:
        """Delete content and cleanup related data"""
        
        try:
            # Delete from vector database
            collection = vectordb.get_collection(config.vectordb.collection_name)
            collection.delete(ids=[str(content_id)])
            
            # Delete from main database
            await db.execute(
                delete(Content).where(Content.id == content_id)
            )
            
            await db.commit()
            return True
            
        except Exception as e:
            logger.error(f"Content deletion failed: {e}")
            await db.rollback()
            return False
    
    async def bulk_import(
        self,
        content_inputs: List[ContentInput],
        db: AsyncSession,
        vectordb: chromadb.PersistentClient,
        user_id: Optional[uuid.UUID] = None,
        batch_size: int = None
    ) -> List[Content]:
        """Import multiple contents with batch processing"""
        
        if batch_size is None:
            batch_size = config.processing.batch_size
        
        results = []
        
        # Process in batches
        for i in range(0, len(content_inputs), batch_size):
            batch = content_inputs[i:i + batch_size]
            
            # Process batch concurrently
            batch_tasks = [
                self.ingest_content(content_input, db, vectordb, user_id)
                for content_input in batch
            ]
            
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            # Handle exceptions
            for result in batch_results:
                if isinstance(result, Exception):
                    logger.error(f"Batch import item failed: {result}")
                else:
                    results.append(result)
        
        return results
    
    async def get_content_stats(self, db: AsyncSession) -> Dict[str, Any]:
        """Get content statistics"""
        
        # Total counts by type
        type_stats = await db.execute(
            select(Content.content_type, func.count(Content.id))
            .group_by(Content.content_type)
        )
        
        content_by_type = {row[0].value: row[1] for row in type_stats}
        
        # Processing status counts
        status_stats = await db.execute(
            select(Content.processing_status, func.count(Content.id))
            .group_by(Content.processing_status)
        )
        
        content_by_status = {row[0].value: row[1] for row in status_stats}
        
        # Quality distribution
        quality_stats = await db.execute(
            select(
                func.avg(Content.quality_score),
                func.min(Content.quality_score),
                func.max(Content.quality_score)
            ).where(Content.quality_score.is_not(None))
        )
        
        quality_row = quality_stats.first()
        
        return {
            "total_content": sum(content_by_type.values()),
            "by_type": content_by_type,
            "by_status": content_by_status,
            "quality_stats": {
                "average": float(quality_row[0]) if quality_row[0] else None,
                "min": float(quality_row[1]) if quality_row[1] else None,
                "max": float(quality_row[2]) if quality_row[2] else None
            }
        }
    
    async def _check_duplicate(self, db: AsyncSession, checksum: str) -> Optional[Content]:
        """Check for duplicate content by checksum"""
        
        result = await db.execute(
            select(Content).where(Content.checksum == checksum)
        )
        
        return result.scalar_one_or_none()
    
    async def _calculate_quality_score(self, text: str) -> float:
        """Calculate content quality score"""
        
        # Basic quality metrics
        score = 0.5  # Base score
        
        # Length factor
        text_length = len(text)
        if config.processing.chunk_size <= text_length <= config.processing.max_text_length // 2:
            score += 0.2
        
        # Word count factor
        word_count = len(text.split())
        if 50 <= word_count <= 1000:
            score += 0.2
        
        # Character diversity
        unique_chars = len(set(text.lower()))
        if unique_chars > 20:
            score += 0.1
        
        # Sentence structure
        sentences = text.split('.')
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0
        if 10 <= avg_sentence_length <= 25:
            score += 0.1
        
        return min(1.0, score)
    
    async def _store_in_vectordb(self, content: Content, vectordb: chromadb.PersistentClient):
        """Store content in vector database"""
        
        if not content.embedding:
            return
        
        try:
            collection = vectordb.get_or_create_collection(
                name=config.vectordb.collection_name,
                metadata={"dimension": config.vectordb.embedding_dimension}
            )
            
            collection.add(
                embeddings=[content.embedding],
                documents=[content.data],
                metadatas=[{
                    "content_id": str(content.id),
                    "content_type": content.content_type.value,
                    "title": content.metadata.get("title", ""),
                    "source": content.metadata.get("source", ""),
                    "created_at": content.created_at.isoformat()
                }],
                ids=[str(content.id)]
            )
            
        except Exception as e:
            logger.error(f"Failed to store content in vector database: {e}")
    
    async def _update_in_vectordb(self, content: Content, vectordb: chromadb.PersistentClient):
        """Update content in vector database"""
        
        if not content.embedding:
            return
        
        try:
            collection = vectordb.get_collection(config.vectordb.collection_name)
            
            # Delete old entry
            collection.delete(ids=[str(content.id)])
            
            # Add updated entry
            collection.add(
                embeddings=[content.embedding],
                documents=[content.data],
                metadatas=[{
                    "content_id": str(content.id),
                    "content_type": content.content_type.value,
                    "title": content.metadata.get("title", ""),
                    "source": content.metadata.get("source", ""),
                    "updated_at": content.updated_at.isoformat() if content.updated_at else content.created_at.isoformat()
                }],
                ids=[str(content.id)]
            )
            
        except Exception as e:
            logger.error(f"Failed to update content in vector database: {e}")
    
    async def _create_content_version(self, content: Content, db: AsyncSession, user_id: Optional[uuid.UUID]):
        """Create a version backup of content before modification"""
        
        # This would create a record in the content_versions table
        # Implementation depends on the versioning strategy
        pass