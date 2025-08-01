#!/usr/bin/env python3
"""
Hierarchical Embedding Engine for Humanizer Archive
Multi-level content distillation with adaptive chunking and provenance tracking
"""

import os
import json
import sqlite3
import hashlib
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict
import re

import tiktoken
import numpy as np
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings

# LLM integration for summarization
from litellm import completion

@dataclass
class ChunkProvenance:
    """Track the origin and lineage of each chunk"""
    conversation_id: int
    message_id: Optional[int]
    chunk_id: str
    parent_chunk_ids: List[str]
    level: int  # 0=original, 1=first summary, 2=second summary, etc.
    token_count: int
    chunk_type: str  # 'original', 'adaptive', 'summary', 'distillation'
    created_at: str
    summarizes: List[str]  # IDs of chunks this summarizes
    source_range: Tuple[int, int]  # Start, end positions in original text

@dataclass
class EmbeddedChunk:
    """A chunk with its embedding and metadata"""
    id: str
    content: str
    embedding: List[float]
    provenance: ChunkProvenance
    metadata: Dict[str, Any]

class AdaptiveChunker:
    """Intelligently split text into meaningful, overlapping chunks"""
    
    def __init__(self, min_tokens=200, max_tokens=500, overlap_ratio=0.15):
        self.min_tokens = min_tokens
        self.max_tokens = max_tokens
        self.overlap_ratio = overlap_ratio
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
        
        # Sentence and paragraph boundaries for smart splitting
        self.sentence_endings = re.compile(r'[.!?]+\s+')
        self.paragraph_boundaries = re.compile(r'\n\s*\n')
        
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        return len(self.tokenizer.encode(text))
    
    def find_best_split_point(self, text: str, target_pos: int) -> int:
        """Find the best place to split text near target position"""
        # Look for paragraph boundary first (within 100 chars)
        para_matches = list(self.paragraph_boundaries.finditer(text))
        for match in para_matches:
            if abs(match.start() - target_pos) < 100:
                return match.end()
        
        # Look for sentence boundary (within 50 chars)
        sent_matches = list(self.sentence_endings.finditer(text))
        for match in sent_matches:
            if abs(match.start() - target_pos) < 50:
                return match.end()
        
        # Fallback: split at word boundary
        while target_pos > 0 and text[target_pos] != ' ':
            target_pos -= 1
        return target_pos
    
    def adaptive_chunk(self, text: str, conversation_id: int, message_id: Optional[int] = None) -> List[ChunkProvenance]:
        """Split text into adaptive, overlapping chunks with provenance"""
        chunks = []
        text_len = len(text)
        
        if self.count_tokens(text) <= self.max_tokens:
            # Text is small enough to be one chunk
            chunk_id = self._generate_chunk_id(text, 0)
            provenance = ChunkProvenance(
                conversation_id=conversation_id,
                message_id=message_id,
                chunk_id=chunk_id,
                parent_chunk_ids=[],
                level=0,
                token_count=self.count_tokens(text),
                chunk_type='original',
                created_at=datetime.now().isoformat(),
                summarizes=[],
                source_range=(0, text_len)
            )
            chunks.append(provenance)
            return chunks
        
        # Split into overlapping chunks
        start = 0
        chunk_num = 0
        
        while start < text_len:
            # Calculate end position
            end = min(start + self._estimate_char_for_tokens(self.max_tokens), text_len)
            
            # Adjust end to good split point
            if end < text_len:
                end = self.find_best_split_point(text, end)
            
            chunk_text = text[start:end]
            
            # Skip if too small (unless it's the last chunk)
            if self.count_tokens(chunk_text) < self.min_tokens and end < text_len:
                start = end
                continue
            
            chunk_id = self._generate_chunk_id(chunk_text, chunk_num)
            provenance = ChunkProvenance(
                conversation_id=conversation_id,
                message_id=message_id,
                chunk_id=chunk_id,
                parent_chunk_ids=[],
                level=0,
                token_count=self.count_tokens(chunk_text),
                chunk_type='adaptive',
                created_at=datetime.now().isoformat(),
                summarizes=[],
                source_range=(start, end)
            )
            chunks.append(provenance)
            
            # Calculate next start with overlap
            overlap_chars = int((end - start) * self.overlap_ratio)
            start = max(start + 1, end - overlap_chars)
            chunk_num += 1
        
        return chunks
    
    def _estimate_char_for_tokens(self, token_count: int) -> int:
        """Rough estimate of characters needed for token count"""
        return int(token_count * 4)  # Rough average
    
    def _generate_chunk_id(self, text: str, chunk_num: int) -> str:
        """Generate unique chunk ID"""
        content_hash = hashlib.md5(text.encode()).hexdigest()[:12]
        return f"chunk_{content_hash}_{chunk_num}"

class HierarchicalSummarizer:
    """Create multi-level summaries maintaining essence while reducing size"""
    
    def __init__(self, model_name="deepseek/deepseek-chat"):
        self.model_name = model_name
        self.max_input_tokens = 8000
        
    def summarize_chunks(self, chunks: List[Tuple[str, ChunkProvenance]], 
                        target_level: int, 
                        summarization_prompt: str = None) -> List[Tuple[str, ChunkProvenance]]:
        """Summarize a group of chunks into higher-level abstractions"""
        
        if not summarization_prompt:
            summarization_prompt = self._get_default_summary_prompt(target_level)
        
        # Group chunks that can be summarized together
        summary_groups = self._group_chunks_for_summarization(chunks)
        summarized_chunks = []
        
        for group in summary_groups:
            try:
                # Combine chunks for summarization
                combined_text = "\n\n---\n\n".join([chunk[0] for chunk in group])
                source_provenances = [chunk[1] for chunk in group]
                
                # Generate summary
                summary = self._generate_summary(combined_text, summarization_prompt)
                
                # Create new provenance for summary
                summary_provenance = self._create_summary_provenance(
                    source_provenances, target_level, summary
                )
                
                summarized_chunks.append((summary, summary_provenance))
                
            except Exception as e:
                logging.error(f"Summarization failed for group: {e}")
                # Fall back to keeping original chunks
                summarized_chunks.extend(group)
        
        return summarized_chunks
    
    def _get_default_summary_prompt(self, level: int) -> str:
        """Generate appropriate summary prompt for the level"""
        if level == 1:
            return """Summarize the following content while preserving key insights, concepts, and essential details. 
            Maintain the core meaning but reduce verbosity. Focus on actionable insights and important ideas."""
        elif level == 2:
            return """Create a high-level distillation of the following content. Extract the essential themes, 
            core concepts, and most important insights. This should capture the essence while being significantly more concise."""
        else:
            return """Distill the following content to its absolute essence. Capture only the most fundamental 
            insights, key principles, and critical concepts. This should be a highly concentrated representation."""
    
    def _group_chunks_for_summarization(self, chunks: List[Tuple[str, ChunkProvenance]]) -> List[List[Tuple[str, ChunkProvenance]]]:
        """Group chunks that should be summarized together"""
        groups = []
        current_group = []
        current_tokens = 0
        
        for chunk_text, provenance in chunks:
            chunk_tokens = provenance.token_count
            
            # Start new group if adding this chunk would exceed limits
            if current_tokens + chunk_tokens > self.max_input_tokens and current_group:
                groups.append(current_group)
                current_group = [(chunk_text, provenance)]
                current_tokens = chunk_tokens
            else:
                current_group.append((chunk_text, provenance))
                current_tokens += chunk_tokens
        
        if current_group:
            groups.append(current_group)
        
        return groups
    
    def _generate_summary(self, text: str, prompt: str) -> str:
        """Generate summary using LLM"""
        try:
            response = completion(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": text}
                ],
                max_tokens=800,
                temperature=0.3
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logging.error(f"LLM summarization failed: {e}")
            # Fallback: simple truncation
            return text[:1000] + "..." if len(text) > 1000 else text
    
    def _create_summary_provenance(self, source_provenances: List[ChunkProvenance], 
                                 level: int, summary_text: str) -> ChunkProvenance:
        """Create provenance for a summary chunk"""
        # Use first chunk's conversation/message info
        base_provenance = source_provenances[0]
        
        chunk_id = hashlib.md5(summary_text.encode()).hexdigest()[:16]
        
        return ChunkProvenance(
            conversation_id=base_provenance.conversation_id,
            message_id=base_provenance.message_id,
            chunk_id=f"summary_{level}_{chunk_id}",
            parent_chunk_ids=[p.chunk_id for p in source_provenances],
            level=level,
            token_count=len(tiktoken.get_encoding("cl100k_base").encode(summary_text)),
            chunk_type='summary' if level == 1 else 'distillation',
            created_at=datetime.now().isoformat(),
            summarizes=[p.chunk_id for p in source_provenances],
            source_range=(
                min(p.source_range[0] for p in source_provenances),
                max(p.source_range[1] for p in source_provenances)
            )
        )

class HierarchicalEmbeddingEngine:
    """Main engine coordinating chunking, summarization, and embedding"""
    
    def __init__(self, 
                 embedding_model="all-MiniLM-L6-v2",
                 chromadb_path="./hierarchical_embeddings",
                 database_path="./data/hierarchical_corpus.db"):
        
        self.chunker = AdaptiveChunker()
        self.summarizer = HierarchicalSummarizer()
        
        # Embedding model
        self.embedding_model = SentenceTransformer(embedding_model)
        
        # ChromaDB for vector storage
        self.chroma_client = chromadb.PersistentClient(
            path=chromadb_path,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # SQLite for metadata and provenance
        self.db_path = database_path
        self._init_database()
        
        # Collections for different levels
        self.collections = {}
        self._init_collections()
        
    def _init_database(self):
        """Initialize SQLite database for provenance tracking"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS chunk_provenance (
                    chunk_id TEXT PRIMARY KEY,
                    conversation_id INTEGER,
                    message_id INTEGER,
                    parent_chunk_ids TEXT,
                    level INTEGER,
                    token_count INTEGER,
                    chunk_type TEXT,
                    created_at TEXT,
                    summarizes TEXT,
                    source_range_start INTEGER,
                    source_range_end INTEGER,
                    metadata TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS processing_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id INTEGER,
                    processing_stage TEXT,
                    chunks_created INTEGER,
                    timestamp TEXT,
                    notes TEXT
                )
            """)
    
    def _init_collections(self):
        """Initialize ChromaDB collections for each level"""
        level_names = ["original", "summary_1", "summary_2", "distillation"]
        
        for level, name in enumerate(level_names):
            try:
                collection = self.chroma_client.get_collection(name=name)
            except:
                collection = self.chroma_client.create_collection(
                    name=name,
                    metadata={"description": f"Level {level} embeddings"}
                )
            self.collections[level] = collection
    
    def process_conversation(self, conversation_id: int, 
                           conversation_text: str, 
                           messages: List[Dict] = None,
                           max_levels: int = 3) -> Dict[str, Any]:
        """Process entire conversation through hierarchical embedding pipeline"""
        
        logging.info(f"Processing conversation {conversation_id}")
        
        # Stage 1: Chunk the conversation and individual messages
        all_chunks = []
        
        # Chunk full conversation
        conv_chunks = self.chunker.adaptive_chunk(conversation_text, conversation_id)
        all_chunks.extend([(conversation_text[p.source_range[0]:p.source_range[1]], p) 
                          for p in conv_chunks])
        
        # Chunk individual messages if provided
        if messages:
            for msg in messages:
                msg_chunks = self.chunker.adaptive_chunk(
                    msg['content'], conversation_id, msg.get('id')
                )
                all_chunks.extend([(msg['content'][p.source_range[0]:p.source_range[1]], p) 
                                  for p in msg_chunks])
        
        # Stage 2: Create embeddings and store level 0
        level_chunks = {0: all_chunks}
        self._embed_and_store_chunks(all_chunks, 0)
        
        # Stage 3: Create summary levels
        current_chunks = all_chunks
        for level in range(1, max_levels + 1):
            if len(current_chunks) <= 1:
                break  # No need for further summarization
                
            summary_chunks = self.summarizer.summarize_chunks(current_chunks, level)
            level_chunks[level] = summary_chunks
            self._embed_and_store_chunks(summary_chunks, level)
            current_chunks = summary_chunks
        
        # Log processing
        self._log_processing(conversation_id, level_chunks)
        
        return {
            "conversation_id": conversation_id,
            "levels_created": list(level_chunks.keys()),
            "total_chunks": sum(len(chunks) for chunks in level_chunks.values()),
            "processing_time": datetime.now().isoformat()
        }
    
    def _embed_and_store_chunks(self, chunks: List[Tuple[str, ChunkProvenance]], level: int):
        """Generate embeddings and store in both ChromaDB and SQLite"""
        
        if not chunks:
            return
            
        texts = [chunk[0] for chunk in chunks]
        provenances = [chunk[1] for chunk in chunks]
        
        # Generate embeddings
        embeddings = self.embedding_model.encode(texts).tolist()
        
        # Store in ChromaDB
        collection = self.collections[level]
        ids = [p.chunk_id for p in provenances]
        metadatas = [self._provenance_to_metadata(p) for p in provenances]
        
        collection.add(
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
        
        # Store provenance in SQLite
        with sqlite3.connect(self.db_path) as conn:
            for provenance in provenances:
                conn.execute("""
                    INSERT OR REPLACE INTO chunk_provenance 
                    (chunk_id, conversation_id, message_id, parent_chunk_ids, level, 
                     token_count, chunk_type, created_at, summarizes, source_range_start, 
                     source_range_end, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    provenance.chunk_id,
                    provenance.conversation_id,
                    provenance.message_id,
                    json.dumps(provenance.parent_chunk_ids),
                    provenance.level,
                    provenance.token_count,
                    provenance.chunk_type,
                    provenance.created_at,
                    json.dumps(provenance.summarizes),
                    provenance.source_range[0],
                    provenance.source_range[1],
                    json.dumps(asdict(provenance))
                ))
    
    def _provenance_to_metadata(self, provenance: ChunkProvenance) -> Dict[str, Any]:
        """Convert provenance to ChromaDB metadata format"""
        return {
            "conversation_id": provenance.conversation_id,
            "message_id": provenance.message_id or -1,
            "level": provenance.level,
            "chunk_type": provenance.chunk_type,
            "token_count": provenance.token_count,
            "created_at": provenance.created_at
        }
    
    def _log_processing(self, conversation_id: int, level_chunks: Dict[int, List]):
        """Log processing results"""
        with sqlite3.connect(self.db_path) as conn:
            for level, chunks in level_chunks.items():
                conn.execute("""
                    INSERT INTO processing_log 
                    (conversation_id, processing_stage, chunks_created, timestamp, notes)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    conversation_id,
                    f"level_{level}",
                    len(chunks),
                    datetime.now().isoformat(),
                    f"Created {len(chunks)} chunks at level {level}"
                ))
    
    def search_semantic(self, query: str, 
                       max_results: int = 50,
                       levels: List[int] = None,
                       min_relevance: float = 0.7,
                       filter_terms: List[str] = None,
                       boost_factor: float = 0.1) -> List[Dict[str, Any]]:
        """Search for content across hierarchical levels with optional term boosting"""
        
        if levels is None:
            levels = [0, 1, 2, 3]
        
        all_results = []
        
        for level in levels:
            if level not in self.collections:
                continue
                
            collection = self.collections[level]
            
            # Search with embedding similarity
            results = collection.query(
                query_texts=[query],
                n_results=max_results,
                where={"level": level}
            )
            
            # Process results
            for i, (doc, metadata, distance) in enumerate(zip(
                results['documents'][0], 
                results['metadatas'][0], 
                results['distances'][0]
            )):
                # Calculate relevance score
                relevance = 1 - distance  # Convert distance to similarity
                
                # Apply term boosting if specified
                if filter_terms:
                    content_lower = doc.lower()
                    term_boost = sum(1 for term in filter_terms if term in content_lower)
                    relevance += term_boost * boost_factor
                
                if relevance >= min_relevance:
                    all_results.append({
                        "content": doc,
                        "relevance_score": relevance,
                        "level": level,
                        "metadata": metadata,
                        "conversation_id": metadata["conversation_id"],
                        "chunk_id": results['ids'][0][i]
                    })
        
        # Sort by relevance and return top results
        all_results.sort(key=lambda x: x["relevance_score"], reverse=True)
        return all_results[:max_results]
    
    def get_chunk_lineage(self, chunk_id: str) -> Dict[str, Any]:
        """Get the full lineage of a chunk (parents, children, siblings)"""
        with sqlite3.connect(self.db_path) as conn:
            # Get chunk info
            cursor = conn.execute(
                "SELECT * FROM chunk_provenance WHERE chunk_id = ?", 
                (chunk_id,)
            )
            chunk_row = cursor.fetchone()
            
            if not chunk_row:
                return None
            
            # Get parent chunks
            parent_ids = json.loads(chunk_row[3]) if chunk_row[3] else []
            parents = []
            for parent_id in parent_ids:
                parent_cursor = conn.execute(
                    "SELECT * FROM chunk_provenance WHERE chunk_id = ?", 
                    (parent_id,)
                )
                parent_row = parent_cursor.fetchone()
                if parent_row:
                    parents.append(dict(zip([d[0] for d in parent_cursor.description], parent_row)))
            
            # Get child chunks
            children_cursor = conn.execute(
                "SELECT * FROM chunk_provenance WHERE parent_chunk_ids LIKE ?", 
                (f'%"{chunk_id}"%',)
            )
            children = [dict(zip([d[0] for d in children_cursor.description], row)) 
                       for row in children_cursor.fetchall()]
            
            return {
                "chunk": dict(zip([d[0] for d in cursor.description], chunk_row)),
                "parents": parents,
                "children": children,
                "lineage_depth": len(parents) + 1 + len(children)
            }

def main():
    """Example usage of the hierarchical embedding system"""
    
    # Initialize the engine
    engine = HierarchicalEmbeddingEngine()
    
    print("🧠 Hierarchical Embedding Engine - Example Usage")
    print("=" * 50)
    
    # Example: Search for any topic
    search_query = "consciousness and quantum mechanics"
    print(f"🔍 Searching for: '{search_query}'")
    
    # Search across all levels
    results = engine.search_semantic(
        query=search_query,
        max_results=20,
        levels=[0, 1, 2]  # Search original, first summary, and distillation levels
    )
    
    print(f"Found {len(results)} relevant chunks")
    
    # Group by conversation for analysis
    conv_groups = defaultdict(list)
    for result in results:
        conv_groups[result["conversation_id"]].append(result)
    
    print(f"Spanning {len(conv_groups)} conversations")
    
    # Show top results for each level
    for level in [0, 1, 2]:
        level_results = [r for r in results if r["level"] == level]
        if level_results:
            print(f"\n📊 Level {level} results ({len(level_results)} chunks):")
            for result in level_results[:3]:
                print(f"  Score: {result['relevance_score']:.3f}")
                print(f"  Content: {result['content'][:100]}...")
                print()

if __name__ == "__main__":
    main()