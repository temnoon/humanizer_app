#!/usr/bin/env python3
"""
Hierarchical Content Chunking and Summarization

This module implements multi-level content chunking and summarization to enable:
1. Large article retrieval with context
2. Small relevant snippet matching
3. Semantic relationship mapping across different content levels

Key features:
- Adaptive chunk sizing based on content type and length
- Multiple summary levels (sentence, paragraph, section, document)
- Context-aware splitting that preserves semantic boundaries
- LLM integration for intelligent summarization
"""

import re
import asyncio
import json
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@dataclass
class ContentChunk:
    """Represents a chunk of content with hierarchical metadata"""
    id: str
    content: str
    chunk_type: str  # 'sentence', 'paragraph', 'section', 'document'
    level: int  # 0=sentence, 1=paragraph, 2=section, 3=document
    parent_id: Optional[str] = None
    children_ids: List[str] = None
    summary: Optional[str] = None
    word_count: int = 0
    start_position: int = 0
    end_position: int = 0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.children_ids is None:
            self.children_ids = []
        if self.metadata is None:
            self.metadata = {}
        if self.word_count == 0:
            self.word_count = len(self.content.split())

class HierarchicalChunker:
    """
    Implements smart content chunking with hierarchical structure
    """
    
    def __init__(self, 
                 min_chunk_size: int = 50,
                 max_chunk_size: int = 1000,
                 overlap_size: int = 25,
                 summary_levels: int = 3):
        self.min_chunk_size = min_chunk_size
        self.max_chunk_size = max_chunk_size
        self.overlap_size = overlap_size
        self.summary_levels = summary_levels
        
    def chunk_content(self, content: str, content_id: str, content_type: str = "conversation") -> List[ContentChunk]:
        """
        Create hierarchical chunks from content
        
        Returns chunks at multiple levels:
        - Level 0: Sentences/small units (50-200 words)
        - Level 1: Paragraphs/medium units (200-500 words)  
        - Level 2: Sections/large units (500-1000 words)
        - Level 3: Document summary (entire content)
        """
        chunks = []
        
        # Level 3: Document level (entire content)
        doc_chunk = ContentChunk(
            id=f"{content_id}_doc",
            content=content,
            chunk_type="document",
            level=3,
            word_count=len(content.split()),
            start_position=0,
            end_position=len(content),
            metadata={"content_type": content_type, "source_id": content_id}
        )
        chunks.append(doc_chunk)
        
        # Level 2: Section level (500-1000 words)
        sections = self._split_into_sections(content, content_id)
        for section in sections:
            doc_chunk.children_ids.append(section.id)
            section.parent_id = doc_chunk.id
            chunks.append(section)
            
            # Level 1: Paragraph level (200-500 words)
            paragraphs = self._split_into_paragraphs(section.content, section.id, 
                                                   section.start_position)
            for paragraph in paragraphs:
                section.children_ids.append(paragraph.id)
                paragraph.parent_id = section.id
                chunks.append(paragraph)
                
                # Level 0: Sentence level (50-200 words)
                sentences = self._split_into_sentences(paragraph.content, paragraph.id,
                                                     paragraph.start_position)
                for sentence in sentences:
                    paragraph.children_ids.append(sentence.id)
                    sentence.parent_id = paragraph.id
                    chunks.append(sentence)
        
        return chunks
    
    def _split_into_sections(self, content: str, parent_id: str) -> List[ContentChunk]:
        """Split content into section-level chunks (500-1000 words)"""
        words = content.split()
        sections = []
        section_num = 0
        
        i = 0
        while i < len(words):
            # Determine section size based on remaining content
            remaining_words = len(words) - i
            if remaining_words <= self.max_chunk_size * 1.2:
                # Take all remaining words for last section
                section_size = remaining_words
            else:
                section_size = self.max_chunk_size
            
            # Extract section content
            section_words = words[i:i + section_size]
            section_content = " ".join(section_words)
            
            # Find natural break points (double newlines, etc.)
            section_content = self._find_natural_break(section_content, 
                                                     " ".join(words[max(0, i-50):i + section_size + 50]))
            
            start_pos = len(" ".join(words[:i]))
            end_pos = start_pos + len(section_content)
            
            section_chunk = ContentChunk(
                id=f"{parent_id}_sec_{section_num}",
                content=section_content,
                chunk_type="section", 
                level=2,
                word_count=len(section_content.split()),
                start_position=start_pos,
                end_position=end_pos
            )
            
            sections.append(section_chunk)
            section_num += 1
            
            # Move to next section with overlap
            actual_words_used = len(section_content.split())
            i += max(actual_words_used - self.overlap_size, self.min_chunk_size)
            
        return sections
    
    def _split_into_paragraphs(self, content: str, parent_id: str, base_position: int) -> List[ContentChunk]:
        """Split section content into paragraph-level chunks (200-500 words)"""
        # Split on double newlines first (natural paragraphs)
        natural_paragraphs = re.split(r'\n\s*\n', content)
        paragraphs = []
        paragraph_num = 0
        position = base_position
        
        current_para = ""
        for natural_para in natural_paragraphs:
            natural_para = natural_para.strip()
            if not natural_para:
                continue
                
            # Check if adding this natural paragraph exceeds our target size
            combined = (current_para + "\n\n" + natural_para) if current_para else natural_para
            combined_words = len(combined.split())
            
            if combined_words <= 500 and current_para:  # Target paragraph size
                current_para = combined
            else:
                # Save current paragraph if it exists and has content
                if current_para and len(current_para.split()) >= self.min_chunk_size:
                    para_chunk = ContentChunk(
                        id=f"{parent_id}_para_{paragraph_num}",
                        content=current_para,
                        chunk_type="paragraph",
                        level=1,
                        word_count=len(current_para.split()),
                        start_position=position,
                        end_position=position + len(current_para)
                    )
                    paragraphs.append(para_chunk)
                    paragraph_num += 1
                    position += len(current_para)
                
                # Start new paragraph
                current_para = natural_para
        
        # Don't forget the last paragraph
        if current_para and len(current_para.split()) >= self.min_chunk_size:
            para_chunk = ContentChunk(
                id=f"{parent_id}_para_{paragraph_num}",
                content=current_para,
                chunk_type="paragraph",
                level=1,
                word_count=len(current_para.split()),
                start_position=position,
                end_position=position + len(current_para)
            )
            paragraphs.append(para_chunk)
        
        return paragraphs
    
    def _split_into_sentences(self, content: str, parent_id: str, base_position: int) -> List[ContentChunk]:
        """Split paragraph content into sentence-level chunks (50-200 words)"""
        # Split on sentence boundaries
        sentences = re.split(r'[.!?]+\s+', content)
        chunks = []
        chunk_num = 0
        position = base_position
        
        current_chunk = ""
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # Add sentence to current chunk
            combined = (current_chunk + ". " + sentence) if current_chunk else sentence
            combined_words = len(combined.split())
            
            if combined_words <= 200:  # Target sentence chunk size
                current_chunk = combined
            else:
                # Save current chunk if it has enough content
                if current_chunk and len(current_chunk.split()) >= self.min_chunk_size:
                    sent_chunk = ContentChunk(
                        id=f"{parent_id}_sent_{chunk_num}",
                        content=current_chunk,
                        chunk_type="sentence",
                        level=0,
                        word_count=len(current_chunk.split()),
                        start_position=position,
                        end_position=position + len(current_chunk)
                    )
                    chunks.append(sent_chunk)
                    chunk_num += 1
                    position += len(current_chunk)
                
                # Start new chunk
                current_chunk = sentence
        
        # Don't forget the last chunk
        if current_chunk and len(current_chunk.split()) >= self.min_chunk_size:
            sent_chunk = ContentChunk(
                id=f"{parent_id}_sent_{chunk_num}",
                content=current_chunk,
                chunk_type="sentence",
                level=0,
                word_count=len(current_chunk.split()),
                start_position=position,
                end_position=position + len(current_chunk)
            )
            chunks.append(sent_chunk)
        
        return chunks
    
    def _find_natural_break(self, content: str, extended_content: str) -> str:
        """Find natural breaking points like paragraph boundaries"""
        # Look for double newlines within reasonable range
        for i in range(len(content) - 100, len(content)):
            if i > 0 and content[i:i+2] == '\n\n':
                return content[:i]
        
        # Look for single newlines
        for i in range(len(content) - 50, len(content)):
            if i > 0 and content[i] == '\n':
                return content[:i]
        
        # Look for sentence endings
        for i in range(len(content) - 20, len(content)):
            if i > 0 and content[i] in '.!?' and i + 1 < len(content) and content[i+1] == ' ':
                return content[:i+1]
        
        return content

class ContentSummarizer:
    """
    Generates intelligent summaries for different content levels
    """
    
    def __init__(self, llm_provider=None):
        self.llm_provider = llm_provider
        
    async def generate_summaries(self, chunks: List[ContentChunk]) -> List[ContentChunk]:
        """Generate summaries for all chunks that need them"""
        
        # Process chunks by level (bottom-up: sentences -> paragraphs -> sections -> document)
        for level in range(4):  # 0, 1, 2, 3
            level_chunks = [chunk for chunk in chunks if chunk.level == level and not chunk.summary]
            
            for chunk in level_chunks:
                if level == 0:  # Sentence level - extract key phrases
                    chunk.summary = self._extract_key_phrases(chunk.content)
                elif level == 1:  # Paragraph level - brief summary
                    chunk.summary = await self._summarize_paragraph(chunk, chunks)
                elif level == 2:  # Section level - structured summary
                    chunk.summary = await self._summarize_section(chunk, chunks)
                elif level == 3:  # Document level - comprehensive summary
                    chunk.summary = await self._summarize_document(chunk, chunks)
        
        return chunks
    
    def _extract_key_phrases(self, content: str) -> str:
        """Extract key phrases from sentence-level content"""
        # Simple keyword extraction (can be enhanced with NLP)
        words = content.split()
        
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'}
        
        key_words = [word for word in words if word.lower() not in stop_words and len(word) > 3]
        
        # Take first 10 words as key phrases
        return " • ".join(key_words[:10])
    
    async def _summarize_paragraph(self, chunk: ContentChunk, all_chunks: List[ContentChunk]) -> str:
        """Generate summary for paragraph-level content"""
        if not self.llm_provider:
            return chunk.content[:100] + "..."
        
        # Use LLM to summarize paragraph
        prompt = f"""
        Summarize the following paragraph in 1-2 sentences, capturing the main idea:
        
        {chunk.content}
        
        Summary:"""
        
        try:
            response = await self.llm_provider.generate(prompt, max_tokens=100)
            return response.strip()
        except Exception as e:
            logger.error(f"Failed to summarize paragraph {chunk.id}: {e}")
            return chunk.content[:100] + "..."
    
    async def _summarize_section(self, chunk: ContentChunk, all_chunks: List[ContentChunk]) -> str:
        """Generate summary for section-level content"""
        if not self.llm_provider:
            return chunk.content[:200] + "..."
        
        # Get summaries of child paragraphs
        child_summaries = []
        for child_id in chunk.children_ids:
            child = next((c for c in all_chunks if c.id == child_id), None)
            if child and child.summary:
                child_summaries.append(child.summary)
        
        if child_summaries:
            combined_summaries = "\n".join(child_summaries)
            prompt = f"""
            Create a cohesive summary of this section based on its paragraph summaries:
            
            {combined_summaries}
            
            Section Summary (2-3 sentences):"""
        else:
            prompt = f"""
            Summarize the following section in 2-3 sentences:
            
            {chunk.content[:1000]}...
            
            Summary:"""
        
        try:
            response = await self.llm_provider.generate(prompt, max_tokens=150)
            return response.strip()
        except Exception as e:
            logger.error(f"Failed to summarize section {chunk.id}: {e}")
            return chunk.content[:200] + "..."
    
    async def _summarize_document(self, chunk: ContentChunk, all_chunks: List[ContentChunk]) -> str:
        """Generate comprehensive summary for document-level content"""
        if not self.llm_provider:
            return chunk.content[:300] + "..."
        
        # Get summaries of child sections
        child_summaries = []
        for child_id in chunk.children_ids:
            child = next((c for c in all_chunks if c.id == child_id), None)
            if child and child.summary:
                child_summaries.append(f"Section: {child.summary}")
        
        if child_summaries:
            combined_summaries = "\n".join(child_summaries)
            prompt = f"""
            Create a comprehensive document summary based on section summaries:
            
            {combined_summaries}
            
            Document Summary (3-4 sentences covering main themes):"""
        else:
            prompt = f"""
            Create a comprehensive summary of this document in 3-4 sentences:
            
            {chunk.content[:2000]}...
            
            Summary:"""
        
        try:
            response = await self.llm_provider.generate(prompt, max_tokens=200)
            return response.strip()
        except Exception as e:
            logger.error(f"Failed to summarize document {chunk.id}: {e}")
            return chunk.content[:300] + "..."

# Integration function for the main system
async def process_content_hierarchically(content: str, content_id: str, 
                                       content_type: str = "conversation",
                                       llm_provider=None) -> List[Dict[str, Any]]:
    """
    Process content through hierarchical chunking and summarization
    
    Returns list of chunk dictionaries ready for database storage
    """
    chunker = HierarchicalChunker()
    summarizer = ContentSummarizer(llm_provider)
    
    # Create hierarchical chunks
    chunks = chunker.chunk_content(content, content_id, content_type)
    
    # Generate summaries
    chunks = await summarizer.generate_summaries(chunks)
    
    # Convert to database format
    db_chunks = []
    for chunk in chunks:
        db_chunk = {
            "chunk_id": chunk.id,
            "content": chunk.content,
            "summary": chunk.summary,
            "chunk_type": chunk.chunk_type,
            "level": chunk.level,
            "parent_chunk_id": chunk.parent_id,
            "word_count": chunk.word_count,
            "start_position": chunk.start_position,
            "end_position": chunk.end_position,
            "metadata": json.dumps(chunk.metadata),
            "source_content_id": content_id
        }
        db_chunks.append(db_chunk)
    
    return db_chunks

if __name__ == "__main__":
    # Test the hierarchical chunker
    test_content = """
    This is a test document with multiple paragraphs and sections to demonstrate hierarchical chunking.
    
    The first section discusses the importance of content chunking in information retrieval systems. When dealing with large documents, it becomes crucial to break them down into manageable pieces that can be processed and searched efficiently.
    
    Modern search systems need to balance between providing comprehensive context and delivering precise results. This is where hierarchical chunking becomes particularly valuable.
    
    The second section explores different chunking strategies. Simple word-based chunking often breaks semantic boundaries, while sentence-based chunking can create chunks that are too small to be meaningful.
    
    Paragraph-based chunking provides a good middle ground, preserving semantic coherence while maintaining reasonable chunk sizes for processing.
    
    The final section discusses implementation considerations. Memory usage, processing time, and storage requirements all need to be balanced when implementing a hierarchical chunking system.
    """
    
    async def test_chunking():
        chunks = await process_content_hierarchically(test_content, "test_doc_1", "article")
        
        print(f"Generated {len(chunks)} chunks:")
        for chunk in chunks:
            print(f"- {chunk['chunk_id']}: {chunk['chunk_type']} (Level {chunk['level']}) - {chunk['word_count']} words")
            if chunk['summary']:
                print(f"  Summary: {chunk['summary'][:100]}...")
            print()
    
    asyncio.run(test_chunking())