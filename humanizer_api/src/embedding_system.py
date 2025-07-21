#!/usr/bin/env python3
"""
Advanced Embedding System for Humanizer Archive
Implements 240-word chunks with 50-word overlaps and multi-level summary chunking
"""

import asyncio
import logging
import re
import json
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import numpy as np
from datetime import datetime

import openai
import tiktoken
import httpx  # For Ollama API calls

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ContentChunk:
    """Represents a content chunk with metadata"""
    id: str
    content_id: int  # Original content ID from archived_content
    chunk_type: str  # "content", "summary_l1", "summary_l2", "summary_l3"
    text: str
    word_count: int
    token_count: int
    position: int  # Position in original content
    overlap_start: int  # Words overlapping with previous chunk
    overlap_end: int  # Words overlapping with next chunk
    summary_level: int  # 0=original, 1-3=summary levels
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = None
    created_at: datetime = None

@dataclass 
class EmbeddingStats:
    """Statistics about the embedding system"""
    total_chunks: int
    content_chunks: int
    summary_chunks: int
    total_embeddings: int
    vector_dimension: int
    avg_chunk_size: float
    overlap_efficiency: float
    summary_coverage: Dict[str, int]  # Level breakdown

class AdvancedEmbeddingSystem:
    """
    Advanced embedding system with multi-level chunking and semantic vectors
    
    Features:
    - 240-word chunks with 50-word overlaps
    - 3-level hierarchical summaries
    - Multiple embedding models support
    - Semantic similarity search
    - Big picture context matching
    """
    
    def __init__(self, database_url: str, embedding_model: str = "nomic-text-embed", ollama_host: str = "http://localhost:11434"):
        self.database_url = database_url
        self.embedding_model_name = embedding_model
        self.ollama_host = ollama_host
        
        # Configuration  
        self.chunk_size_words = 240
        self.overlap_size_words = 50
        self.max_summary_levels = 3
        self.min_chunk_size_words = 50  # Minimum viable chunk size
        
        # Initialize models
        self.ollama_client = None
        self.tokenizer = None
        self.openai_client = None
        
        # Statistics
        self.stats = EmbeddingStats(
            total_chunks=0,
            content_chunks=0, 
            summary_chunks=0,
            total_embeddings=0,
            vector_dimension=768,  # nomic-text-embed uses 768 dimensions
            avg_chunk_size=0.0,
            overlap_efficiency=0.0,
            summary_coverage={}
        )
        
    async def initialize(self):
        """Initialize embedding models and connections"""
        logger.info("Initializing Advanced Embedding System...")
        
        try:
            # Initialize Ollama client for nomic-text-embed
            self.ollama_client = httpx.AsyncClient(base_url=self.ollama_host, timeout=30.0)
            
            # Test Ollama connection and model availability
            try:
                response = await self.ollama_client.post("/api/embeddings", json={
                    "model": self.embedding_model_name,
                    "prompt": "test"
                })
                if response.status_code == 200:
                    logger.info(f"✅ Connected to Ollama with {self.embedding_model_name}")
                else:
                    logger.warning(f"Ollama model {self.embedding_model_name} not available, attempting to pull...")
                    # Try to pull the model
                    pull_response = await self.ollama_client.post("/api/pull", json={
                        "name": self.embedding_model_name
                    })
                    if pull_response.status_code == 200:
                        logger.info(f"✅ Successfully pulled {self.embedding_model_name}")
                    else:
                        raise Exception(f"Failed to pull model: {pull_response.text}")
                        
            except Exception as e:
                logger.error(f"Failed to connect to Ollama: {e}")
                raise
            
            # Initialize tokenizer for accurate token counting
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
            
            # Initialize OpenAI client for summaries (if API key available)
            try:
                openai_api_key = os.getenv("OPENAI_API_KEY")
                if openai_api_key:
                    self.openai_client = openai.AsyncOpenAI(api_key=openai_api_key)
                    logger.info("OpenAI client initialized for summary generation")
            except Exception as e:
                logger.warning(f"OpenAI not available for summaries: {e}")
            
            logger.info(f"✅ Embedding system initialized:")
            logger.info(f"   - Model: {self.embedding_model_name} via Ollama")
            logger.info(f"   - Vector dimension: {self.stats.vector_dimension}")
            logger.info(f"   - Chunk size: {self.chunk_size_words} words")
            logger.info(f"   - Overlap: {self.overlap_size_words} words")
            logger.info(f"   - Summary levels: {self.max_summary_levels}")
            
        except Exception as e:
            logger.error(f"Failed to initialize embedding system: {e}")
            raise
    
    def extract_chunks(self, text: str, content_id: int) -> List[ContentChunk]:
        """
        Extract 240-word chunks with 50-word overlaps from text
        
        Args:
            text: Source text to chunk
            content_id: ID of the original content
            
        Returns:
            List of ContentChunk objects
        """
        if not text or not text.strip():
            return []
        
        # Clean and normalize text
        text = self._clean_text(text)
        words = text.split()
        
        if len(words) < self.min_chunk_size_words:
            # Text too short, return as single chunk
            return [self._create_chunk(
                content_id=content_id,
                text=text,
                position=0,
                chunk_type="content",
                overlap_start=0,
                overlap_end=0
            )]
        
        chunks = []
        position = 0
        
        while position < len(words):
            # Calculate chunk boundaries
            chunk_end = min(position + self.chunk_size_words, len(words))
            
            # Extract chunk text
            chunk_words = words[position:chunk_end]
            chunk_text = " ".join(chunk_words)
            
            # Calculate overlaps
            overlap_start = min(self.overlap_size_words, position) if position > 0 else 0
            overlap_end = min(self.overlap_size_words, len(words) - chunk_end) if chunk_end < len(words) else 0
            
            # Create chunk
            chunk = self._create_chunk(
                content_id=content_id,
                text=chunk_text,
                position=len(chunks),
                chunk_type="content",
                overlap_start=overlap_start,
                overlap_end=overlap_end
            )
            
            chunks.append(chunk)
            
            # Move position forward (accounting for overlap)
            if chunk_end >= len(words):
                break
            position = chunk_end - self.overlap_size_words
            
            # Prevent infinite loops
            if position <= 0:
                position = chunk_end
        
        logger.debug(f"Extracted {len(chunks)} chunks from {len(words)} words")
        return chunks
    
    async def generate_summary_chunks(self, chunks: List[ContentChunk], content_id: int) -> List[ContentChunk]:
        """
        Generate multi-level summary chunks for big picture semantic matching
        
        Level 1: Combine 3-4 chunks into section summaries
        Level 2: Combine level 1 summaries into broader summaries  
        Level 3: Document-level summary
        
        Args:
            chunks: Original content chunks
            content_id: ID of the original content
            
        Returns:
            List of summary chunks at all levels
        """
        summary_chunks = []
        
        if not chunks or len(chunks) < 2:
            return summary_chunks
        
        try:
            # Level 1: Section summaries (combine 3-4 chunks)
            level1_chunks = await self._create_level_summaries(chunks, 1, content_id, 4)
            summary_chunks.extend(level1_chunks)
            
            # Level 2: Broader summaries (combine level 1 summaries)
            if len(level1_chunks) >= 2:
                level2_chunks = await self._create_level_summaries(level1_chunks, 2, content_id, 3)
                summary_chunks.extend(level2_chunks)
                
                # Level 3: Document summary (combine level 2 or all level 1)
                if len(level2_chunks) >= 2:
                    level3_chunks = await self._create_level_summaries(level2_chunks, 3, content_id, 10)
                else:
                    level3_chunks = await self._create_level_summaries(level1_chunks, 3, content_id, 10)
                summary_chunks.extend(level3_chunks)
            
            logger.info(f"Generated {len(summary_chunks)} summary chunks across {self.max_summary_levels} levels")
            
        except Exception as e:
            logger.error(f"Failed to generate summary chunks: {e}")
        
        return summary_chunks
    
    async def _create_level_summaries(self, source_chunks: List[ContentChunk], level: int, 
                                     content_id: int, group_size: int) -> List[ContentChunk]:
        """Create summary chunks at a specific level"""
        summaries = []
        
        # Group chunks
        for i in range(0, len(source_chunks), group_size):
            group = source_chunks[i:i + group_size]
            if not group:
                continue
            
            # Combine text from group
            combined_text = "\n\n".join([chunk.text for chunk in group])
            
            # Generate summary
            try:
                if self.openai_client:
                    summary_text = await self._openai_summarize(combined_text, level)
                else:
                    summary_text = self._extractive_summarize(combined_text, level)
                
                # Create summary chunk
                summary_chunk = self._create_chunk(
                    content_id=content_id,
                    text=summary_text,
                    position=len(summaries),
                    chunk_type=f"summary_l{level}",
                    overlap_start=0,
                    overlap_end=0,
                    summary_level=level
                )
                
                summaries.append(summary_chunk)
                
            except Exception as e:
                logger.warning(f"Failed to create level {level} summary for group {i}: {e}")
        
        return summaries
    
    async def _openai_summarize(self, text: str, level: int) -> str:
        """Generate summary using OpenAI API"""
        prompt_templates = {
            1: "Summarize this section focusing on key themes and main points:",
            2: "Create a broader summary capturing the main concepts and relationships:",
            3: "Provide a high-level summary capturing the essential meaning and overall purpose:"
        }
        
        prompt = prompt_templates.get(level, prompt_templates[1])
        
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that creates concise, meaningful summaries."},
                    {"role": "user", "content": f"{prompt}\n\n{text}"}
                ],
                max_tokens=150,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.warning(f"OpenAI summarization failed: {e}")
            return self._extractive_summarize(text, level)
    
    def _extractive_summarize(self, text: str, level: int) -> str:
        """Create extractive summary (fallback when OpenAI unavailable)"""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Select key sentences based on level
        if level == 1:
            # Take first and last few sentences
            selected = sentences[:2] + sentences[-1:] if len(sentences) > 3 else sentences
        elif level == 2:
            # Take key sentences spread throughout
            step = max(1, len(sentences) // 3)
            selected = sentences[::step][:3]
        else:
            # Take most central sentences
            mid = len(sentences) // 2
            selected = sentences[max(0, mid-1):mid+2]
        
        return ". ".join(selected) + "."
    
    async def generate_embeddings(self, chunks: List[ContentChunk]) -> List[ContentChunk]:
        """
        Generate embeddings for all chunks using nomic-text-embed via Ollama
        
        Args:
            chunks: List of chunks to embed
            
        Returns:
            Chunks with embeddings added
        """
        if not chunks or not self.ollama_client:
            return chunks
        
        try:
            logger.info(f"Generating embeddings for {len(chunks)} chunks using {self.embedding_model_name}")
            
            # Generate embeddings for each chunk (Ollama doesn't support batch yet)
            for i, chunk in enumerate(chunks):
                try:
                    response = await self.ollama_client.post("/api/embeddings", json={
                        "model": self.embedding_model_name,
                        "prompt": chunk.text
                    })
                    
                    if response.status_code == 200:
                        embedding_data = response.json()
                        chunk.embedding = embedding_data.get("embedding", [])
                        
                        # Verify dimension
                        if len(chunk.embedding) != 768:
                            logger.warning(f"Unexpected embedding dimension: {len(chunk.embedding)}, expected 768")
                    else:
                        logger.error(f"Failed to get embedding for chunk {i}: {response.text}")
                        
                except Exception as e:
                    logger.error(f"Error generating embedding for chunk {i}: {e}")
                
                # Progress logging
                if (i + 1) % 10 == 0:
                    logger.info(f"Generated embeddings for {i + 1}/{len(chunks)} chunks")
            
            successful_embeddings = len([c for c in chunks if c.embedding])
            logger.info(f"✅ Generated {successful_embeddings}/{len(chunks)} embeddings successfully")
            
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            
        return chunks
    
    def _create_chunk(self, content_id: int, text: str, position: int, 
                     chunk_type: str, overlap_start: int, overlap_end: int,
                     summary_level: int = 0) -> ContentChunk:
        """Create a ContentChunk with metadata"""
        words = text.split()
        tokens = len(self.tokenizer.encode(text)) if self.tokenizer else len(words)
        
        chunk_id = f"{content_id}_{chunk_type}_{position}_{summary_level}"
        
        return ContentChunk(
            id=chunk_id,
            content_id=content_id,
            chunk_type=chunk_type,
            text=text,
            word_count=len(words),
            token_count=tokens,
            position=position,
            overlap_start=overlap_start,
            overlap_end=overlap_end,
            summary_level=summary_level,
            metadata={
                "created_at": datetime.now().isoformat(),
                "model": self.embedding_model_name,
                "chunk_strategy": "240w_50overlap"
            },
            created_at=datetime.now()
        )
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text for chunking"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove markdown artifacts
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)  # Bold
        text = re.sub(r'\*(.+?)\*', r'\1', text)      # Italic
        text = re.sub(r'`(.+?)`', r'\1', text)        # Code
        
        # Clean up formatting
        text = text.replace('\\n', ' ').replace('\\t', ' ')
        text = text.strip()
        
        return text
    
    async def semantic_search(self, query: str, chunks: List[ContentChunk], 
                            top_k: int = 10, level_weights: Dict[int, float] = None) -> List[Tuple[ContentChunk, float]]:
        """
        Perform semantic search across chunks with level-aware scoring
        
        Args:
            query: Search query
            chunks: Chunks to search
            top_k: Number of results to return
            level_weights: Weights for different summary levels
            
        Returns:
            List of (chunk, score) tuples sorted by relevance
        """
        if not query or not chunks:
            return []
        
        # Default level weights (higher for summary levels for big picture matching)
        if level_weights is None:
            level_weights = {
                0: 1.0,    # Original content
                1: 1.2,    # Section summaries 
                2: 1.4,    # Broader summaries
                3: 1.6     # Document summaries
            }
        
        try:
            # Generate query embedding using Ollama
            if not self.ollama_client:
                logger.warning("Ollama client not available for semantic search")
                return []
                
            response = await self.ollama_client.post("/api/embeddings", json={
                "model": self.embedding_model_name,
                "prompt": query
            })
            
            if response.status_code != 200:
                logger.error(f"Failed to get query embedding: {response.text}")
                return []
                
            query_embedding = np.array(response.json().get("embedding", []))
            if len(query_embedding) == 0:
                logger.error("Empty query embedding received")
                return []
            
            # Calculate similarities
            results = []
            for chunk in chunks:
                if chunk.embedding is None or len(chunk.embedding) == 0:
                    continue
                
                # Calculate cosine similarity
                chunk_embedding = np.array(chunk.embedding)
                similarity = np.dot(query_embedding, chunk_embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(chunk_embedding)
                )
                
                # Apply level weighting
                level_weight = level_weights.get(chunk.summary_level, 1.0)
                weighted_score = similarity * level_weight
                
                results.append((chunk, weighted_score))
            
            # Sort by weighted score and return top_k
            results.sort(key=lambda x: x[1], reverse=True)
            return results[:top_k]
            
        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            return []
    
    async def process_content(self, content_id: int, text: str) -> Dict[str, Any]:
        """
        Process content through the complete embedding pipeline
        
        Args:
            content_id: ID of the content
            text: Content text to process
            
        Returns:
            Processing results and statistics
        """
        try:
            logger.info(f"Processing content {content_id} through embedding pipeline...")
            
            # Step 1: Extract content chunks
            content_chunks = self.extract_chunks(text, content_id)
            
            # Step 2: Generate summary chunks
            summary_chunks = await self.generate_summary_chunks(content_chunks, content_id)
            
            # Step 3: Combine all chunks
            all_chunks = content_chunks + summary_chunks
            
            # Step 4: Generate embeddings
            all_chunks = await self.generate_embeddings(all_chunks)
            
            # Update statistics
            self.stats.total_chunks += len(all_chunks)
            self.stats.content_chunks += len(content_chunks)
            self.stats.summary_chunks += len(summary_chunks)
            self.stats.total_embeddings += len([c for c in all_chunks if c.embedding])
            
            # Calculate efficiency metrics
            total_words = sum(chunk.word_count for chunk in content_chunks)
            overlap_words = sum(chunk.overlap_start + chunk.overlap_end for chunk in content_chunks)
            self.stats.overlap_efficiency = (overlap_words / total_words) if total_words > 0 else 0
            self.stats.avg_chunk_size = total_words / len(content_chunks) if content_chunks else 0
            
            # Summary level breakdown
            for chunk in summary_chunks:
                level_key = f"level_{chunk.summary_level}"
                self.stats.summary_coverage[level_key] = self.stats.summary_coverage.get(level_key, 0) + 1
            
            result = {
                "content_id": content_id,
                "total_chunks": len(all_chunks),
                "content_chunks": len(content_chunks),
                "summary_chunks": len(summary_chunks),
                "summary_levels": len(set(c.summary_level for c in summary_chunks if c.summary_level > 0)),
                "total_words": total_words,
                "avg_chunk_size": self.stats.avg_chunk_size,
                "overlap_efficiency": self.stats.overlap_efficiency,
                "chunks": [asdict(chunk) for chunk in all_chunks]
            }
            
            logger.info(f"✅ Processed content {content_id}: {len(content_chunks)} content chunks, {len(summary_chunks)} summary chunks")
            return result
            
        except Exception as e:
            logger.error(f"Failed to process content {content_id}: {e}")
            raise
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get current embedding system statistics"""
        return {
            "total_chunks": self.stats.total_chunks,
            "content_chunks": self.stats.content_chunks,
            "summary_chunks": self.stats.summary_chunks,
            "total_embeddings": self.stats.total_embeddings,
            "vector_dimension": self.stats.vector_dimension,
            "avg_chunk_size": round(self.stats.avg_chunk_size, 1),
            "overlap_efficiency": round(self.stats.overlap_efficiency, 3),
            "summary_coverage": self.stats.summary_coverage,
            "configuration": {
                "chunk_size_words": self.chunk_size_words,
                "overlap_size_words": self.overlap_size_words,
                "max_summary_levels": self.max_summary_levels,
                "embedding_model": self.embedding_model_name
            }
        }

# Example usage and testing
async def demo_embedding_system():
    """Demo the embedding system with sample content"""
    print("🧠 Advanced Embedding System Demo")
    print("=" * 50)
    
    # Initialize system
    embedding_system = AdvancedEmbeddingSystem("postgresql://demo")
    await embedding_system.initialize()
    
    # Sample content (from the Node Archive conversation we read earlier)
    sample_text = """
    Give me an article explaining the proof of Noether's theorem (not necessarily displaying the entire proof) and applying it to the example of the Dirac equation.
    
    Noether's theorem is a cornerstone of modern theoretical physics, forging a profound connection between the symmetries of a physical system and its conservation laws. In essence, it states that for every continuous symmetry of the action of a physical system, there is a corresponding conserved current and an associated conserved quantity. This result is foundational in classical and quantum field theories, providing a unifying framework for understanding why certain quantities remain invariant under time evolution.
    
    The link between symmetry and conservation laws was famously formalized by Emmy Noether in 1918. Prior to her work, conservation laws were understood empirically but lacked a unifying explanation. Noether's theorem bridges this gap by showing that each continuous symmetry of a system's action corresponds to a conserved quantity.
    """
    
    # Process content
    result = await embedding_system.process_content(content_id=1, text=sample_text)
    
    print(f"📊 Processing Results:")
    print(f"   • Total chunks: {result['total_chunks']}")
    print(f"   • Content chunks: {result['content_chunks']}")
    print(f"   • Summary chunks: {result['summary_chunks']}")
    print(f"   • Summary levels: {result['summary_levels']}")
    print(f"   • Avg chunk size: {result['avg_chunk_size']:.1f} words")
    print(f"   • Overlap efficiency: {result['overlap_efficiency']:.1%}")
    
    # Demo semantic search
    print(f"\n🔍 Semantic Search Demo:")
    all_chunks = [ContentChunk(**chunk_data) for chunk_data in result['chunks']]
    search_results = await embedding_system.semantic_search(
        query="symmetry conservation physics",
        chunks=all_chunks,
        top_k=3
    )
    
    for i, (chunk, score) in enumerate(search_results, 1):
        print(f"\n   {i}. Score: {score:.3f} (Level {chunk.summary_level})")
        print(f"      Type: {chunk.chunk_type}")
        print(f"      Text: {chunk.text[:100]}...")
    
    # Show statistics
    print(f"\n📈 System Statistics:")
    stats = embedding_system.get_statistics()
    for key, value in stats.items():
        if key != "configuration":
            print(f"   • {key}: {value}")

if __name__ == "__main__":
    import os
    asyncio.run(demo_embedding_system())