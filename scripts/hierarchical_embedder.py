#!/usr/bin/env python3
"""
Hierarchical Semantic Embedder
Creates multi-level chunks and embeddings for deep archive analysis
"""

import os
import sys
import json
import re
import hashlib
import argparse
import sqlite3
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import statistics
import numpy as np
import time

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False
    print("❌ PostgreSQL support not available. Install with: pip install psycopg2-binary")
    sys.exit(1)

try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    print("❌ SentenceTransformers not available. Install with: pip install sentence-transformers")

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("❌ Requests not available for LLM summarization")

@dataclass
class SemanticChunk:
    """Represents a semantic chunk at any hierarchy level"""
    chunk_id: str
    level: str  # 'chunk', 'message', 'section', 'conversation'
    parent_id: Optional[str]
    content: str
    summary: Optional[str]
    word_count: int
    embedding: Optional[np.ndarray]
    metadata: Dict[str, Any]
    children: List[str]  # IDs of child chunks

class HierarchicalEmbedder:
    """Creates hierarchical semantic embeddings for archive content"""
    
    def __init__(self, database_url: str = "postgresql://tem@localhost/humanizer_archive",
                 ollama_host: str = "http://localhost:11434",
                 batch_db_path: str = "./hierarchical_embeddings_batch.db",
                 enable_logging: bool = True):
        self.database_url = database_url
        self.ollama_host = ollama_host
        self.model_name = "llama3.2"
        self.batch_db_path = batch_db_path
        
        # Setup logging
        if enable_logging:
            self.setup_logging()
        
        # Use Ollama for embeddings (Nomic Embed Text)
        self.embedding_model = None  # Will use Ollama API
        self.embedding_dim = 768  # Nomic embed text dimensions
        print("✅ Using Ollama Nomic Embed Text (768 dimensions)")
        
        # Initialize batch tracking
        self.setup_batch_tracking()
        
        # Chunking parameters
        self.chunk_sizes = {
            'chunk': 200,      # Base semantic chunks (words)
            'message': None,   # Full messages (no chunking)
            'section': 1000,   # Message groups (words)
            'conversation': None  # Full conversations (no chunking)
        }
        
        # Overlap for better context preservation
        self.chunk_overlap = 50  # words
        
        # Summarization templates
        self.summary_prompts = {
            'chunk': "Summarize this text chunk in 1-2 sentences focusing on key concepts:\n\n{content}",
            'message': "Summarize this message in 1-2 sentences focusing on main ideas:\n\n{content}",
            'section': "Summarize this section of conversation in 2-3 sentences focusing on themes:\n\n{content}",
            'conversation': "Summarize this entire conversation in 3-4 sentences focusing on main topics and conclusions:\n\n{content}"
        }
    
    def setup_logging(self):
        """Setup detailed logging for batch processing"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"hierarchical_embedding_{timestamp}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"🚀 Hierarchical Embedder initialized - Logging to: {log_file}")
    
    def setup_batch_tracking(self):
        """Setup SQLite database for batch job tracking"""
        conn = sqlite3.connect(self.batch_db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS embedding_jobs (
                job_id TEXT PRIMARY KEY,
                conversation_id INTEGER,
                priority INTEGER DEFAULT 5,
                status TEXT DEFAULT 'pending',
                created_at TEXT,
                started_at TEXT,
                completed_at TEXT,
                chunks_created INTEGER DEFAULT 0,
                processing_time_seconds REAL,
                error_message TEXT,
                retry_count INTEGER DEFAULT 0
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS batch_stats (
                batch_id TEXT PRIMARY KEY,
                total_conversations INTEGER,
                conversations_processed INTEGER DEFAULT 0,
                conversations_failed INTEGER DEFAULT 0,
                total_chunks_created INTEGER DEFAULT 0,
                started_at TEXT,
                completed_at TEXT,
                status TEXT DEFAULT 'running'
            )
        ''')
        
        conn.commit()
        conn.close()
        
        print(f"✅ Batch tracking database initialized: {self.batch_db_path}")
    
    def get_connection(self):
        """Get PostgreSQL connection"""
        return psycopg2.connect(self.database_url, cursor_factory=RealDictCursor)
    
    def ensure_embeddings_tables_exist(self):
        """Create tables for hierarchical embeddings"""
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Create chunks table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS semantic_chunks (
                    chunk_id TEXT PRIMARY KEY,
                    level TEXT NOT NULL,
                    parent_id TEXT,
                    conversation_id BIGINT,
                    content TEXT NOT NULL,
                    summary TEXT,
                    word_count INTEGER,
                    embedding vector(768),  -- Using pgvector for Nomic embeddings
                    metadata JSONB,
                    children TEXT[],
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                );
            """)
            
            # Create indexes for efficient querying
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_chunks_level ON semantic_chunks(level);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_chunks_parent ON semantic_chunks(parent_id);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_chunks_conversation ON semantic_chunks(conversation_id);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_chunks_embedding ON semantic_chunks USING ivfflat (embedding vector_cosine_ops);")
            
            conn.commit()
            print("✅ Semantic chunks tables created/verified")
    
    def text_to_semantic_chunks(self, text: str, chunk_size: int = 200, overlap: int = 50) -> List[str]:
        """Split text into semantic chunks with overlap"""
        
        # Split into sentences first
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return [text]
        
        chunks = []
        current_chunk = []
        current_word_count = 0
        
        for sentence in sentences:
            sentence_words = len(sentence.split())
            
            # If adding this sentence would exceed chunk size, finalize current chunk
            if current_word_count + sentence_words > chunk_size and current_chunk:
                chunk_text = '. '.join(current_chunk) + '.'
                chunks.append(chunk_text)
                
                # Start new chunk with overlap
                overlap_sentences = []
                overlap_words = 0
                for prev_sentence in reversed(current_chunk):
                    sentence_word_count = len(prev_sentence.split())
                    if overlap_words + sentence_word_count <= overlap:
                        overlap_sentences.insert(0, prev_sentence)
                        overlap_words += sentence_word_count
                    else:
                        break
                
                current_chunk = overlap_sentences
                current_word_count = overlap_words
            
            current_chunk.append(sentence)
            current_word_count += sentence_words
        
        # Add final chunk
        if current_chunk:
            chunk_text = '. '.join(current_chunk) + '.'
            chunks.append(chunk_text)
        
        return chunks if chunks else [text]
    
    def generate_summary_with_llm(self, content: str, level: str) -> Optional[str]:
        """Generate summary using local LLM with timeout handling"""
        
        if not REQUESTS_AVAILABLE:
            return None
        
        # Skip summaries for now to avoid timeouts - we can add them back later
        return None
        
        prompt = self.summary_prompts.get(level, self.summary_prompts['chunk']).format(content=content[:1000])
        
        try:
            response = requests.post(
                f"{self.ollama_host}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "num_predict": 50  # Reduced for speed
                    }
                },
                timeout=10  # Reduced timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                summary = result.get('response', '').strip()
                
                # Clean up the summary
                summary = re.sub(r'^(summary|here is|this is|the text)', '', summary, flags=re.IGNORECASE).strip()
                summary = summary.strip('.:')
                
                return summary if summary else None
            
        except Exception as e:
            print(f"⚠️  LLM summarization failed: {e}")
            return None
    
    def generate_embedding(self, text: str) -> Optional[np.ndarray]:
        """Generate embedding using Ollama Nomic Embed Text with timeout handling"""
        
        if not REQUESTS_AVAILABLE:
            return None
        
        try:
            # Truncate text if too long (be more aggressive for speed)
            if len(text.split()) > 1000:
                text = ' '.join(text.split()[:1000])
            
            # Skip very short text to avoid noise
            if len(text.strip()) < 20:
                return None
            
            response = requests.post(
                f"{self.ollama_host}/api/embeddings",
                json={
                    "model": "nomic-embed-text",
                    "prompt": text
                },
                timeout=15  # Reduced timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                embedding = result.get('embedding')
                if embedding and len(embedding) == 768:  # Verify correct dimensions
                    return np.array(embedding, dtype=np.float32)
            
            return None
            
        except Exception as e:
            print(f"⚠️  Embedding generation failed: {e}")
            return None
    
    def create_chunk_id(self, content: str, level: str, parent_id: Optional[str] = None) -> str:
        """Generate unique chunk ID"""
        content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()[:12]
        parent_hash = hashlib.md5(parent_id.encode('utf-8')).hexdigest()[:6] if parent_id else "root"
        return f"{level}_{parent_hash}_{content_hash}"
    
    def process_conversation_hierarchically(self, conversation_id: int) -> List[SemanticChunk]:
        """Process a single conversation into hierarchical chunks"""
        
        print(f"  📝 Processing conversation {conversation_id}")
        
        # Get conversation messages
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, body_text, author, timestamp, word_count
                FROM archived_content
                WHERE parent_id = %s AND content_type = 'message'
                    AND body_text IS NOT NULL AND word_count > 10
                ORDER BY timestamp
            """, (conversation_id,))
            
            messages = cursor.fetchall()
        
        if not messages:
            return []
        
        all_chunks = []
        
        # Level 1: Base chunks from messages
        message_chunks = {}  # message_id -> list of chunk objects
        
        for message in messages:
            message_id = message['id']
            message_text = message['body_text']
            
            # Create base chunks for this message
            text_chunks = self.text_to_semantic_chunks(
                message_text, 
                self.chunk_sizes['chunk'], 
                self.chunk_overlap
            )
            
            message_chunk_objects = []
            for i, chunk_text in enumerate(text_chunks):
                chunk_id = self.create_chunk_id(chunk_text, 'chunk', str(message_id))
                
                # Generate summary and embedding
                summary = self.generate_summary_with_llm(chunk_text, 'chunk')
                embedding = self.generate_embedding(chunk_text)
                
                chunk = SemanticChunk(
                    chunk_id=chunk_id,
                    level='chunk',
                    parent_id=str(message_id),
                    content=chunk_text,
                    summary=summary,
                    word_count=len(chunk_text.split()),
                    embedding=embedding,
                    metadata={
                        'conversation_id': conversation_id,
                        'message_id': message_id,
                        'author': message['author'],
                        'timestamp': message['timestamp'].isoformat() if message['timestamp'] else None,
                        'chunk_index': i,
                        'total_chunks': len(text_chunks)
                    },
                    children=[]
                )
                
                message_chunk_objects.append(chunk)
                all_chunks.append(chunk)
            
            message_chunks[message_id] = message_chunk_objects
        
        # Level 2: Message-level chunks (full messages)
        conversation_message_objects = []
        
        for message in messages:
            message_id = message['id']
            message_text = message['body_text']
            
            message_chunk_id = self.create_chunk_id(message_text, 'message', str(conversation_id))
            
            # Get child chunk IDs
            child_chunk_ids = [chunk.chunk_id for chunk in message_chunks.get(message_id, [])]
            
            # Generate summary and embedding for full message
            summary = self.generate_summary_with_llm(message_text, 'message')
            embedding = self.generate_embedding(message_text)
            
            message_chunk = SemanticChunk(
                chunk_id=message_chunk_id,
                level='message',
                parent_id=str(conversation_id),
                content=message_text,
                summary=summary,
                word_count=message['word_count'] or len(message_text.split()),
                embedding=embedding,
                metadata={
                    'conversation_id': conversation_id,
                    'message_id': message_id,
                    'author': message['author'],
                    'timestamp': message['timestamp'].isoformat() if message['timestamp'] else None,
                    'child_count': len(child_chunk_ids)
                },
                children=child_chunk_ids
            )
            
            conversation_message_objects.append(message_chunk)
            all_chunks.append(message_chunk)
        
        # Level 3: Section-level chunks (groups of related messages)
        # For now, we'll create sections based on author changes or time gaps
        sections = self.group_messages_into_sections(messages)
        conversation_section_objects = []
        
        for section_idx, section_messages in enumerate(sections):
            section_text = '\n\n'.join([msg['body_text'] for msg in section_messages])
            section_id = self.create_chunk_id(section_text, 'section', str(conversation_id))
            
            # Get child message chunk IDs
            child_message_ids = [
                chunk.chunk_id for chunk in conversation_message_objects
                if chunk.metadata['message_id'] in [msg['id'] for msg in section_messages]
            ]
            
            summary = self.generate_summary_with_llm(section_text, 'section')
            embedding = self.generate_embedding(section_text)
            
            section_chunk = SemanticChunk(
                chunk_id=section_id,
                level='section',
                parent_id=str(conversation_id),
                content=section_text,
                summary=summary,
                word_count=sum(msg['word_count'] or 0 for msg in section_messages),
                embedding=embedding,
                metadata={
                    'conversation_id': conversation_id,
                    'section_index': section_idx,
                    'message_count': len(section_messages),
                    'authors': list(set(msg['author'] for msg in section_messages if msg['author'])),
                    'time_span': {
                        'start': min(msg['timestamp'] for msg in section_messages if msg['timestamp']).isoformat(),
                        'end': max(msg['timestamp'] for msg in section_messages if msg['timestamp']).isoformat()
                    } if any(msg['timestamp'] for msg in section_messages) else None
                },
                children=child_message_ids
            )
            
            conversation_section_objects.append(section_chunk)
            all_chunks.append(section_chunk)
        
        # Level 4: Conversation-level chunk (entire conversation)
        conversation_text = '\n\n'.join([msg['body_text'] for msg in messages])
        conversation_chunk_id = self.create_chunk_id(conversation_text, 'conversation')
        
        # Get child section IDs
        child_section_ids = [chunk.chunk_id for chunk in conversation_section_objects]
        
        summary = self.generate_summary_with_llm(conversation_text, 'conversation')
        embedding = self.generate_embedding(summary or conversation_text[:2000])  # Use summary or truncated text
        
        conversation_chunk = SemanticChunk(
            chunk_id=conversation_chunk_id,
            level='conversation',
            parent_id=None,
            content=conversation_text,
            summary=summary,
            word_count=sum(msg['word_count'] or 0 for msg in messages),
            embedding=embedding,
            metadata={
                'conversation_id': conversation_id,
                'message_count': len(messages),
                'section_count': len(sections),
                'authors': list(set(msg['author'] for msg in messages if msg['author'])),
                'time_span': {
                    'start': min(msg['timestamp'] for msg in messages if msg['timestamp']).isoformat(),
                    'end': max(msg['timestamp'] for msg in messages if msg['timestamp']).isoformat()
                } if any(msg['timestamp'] for msg in messages) else None,
                'total_chunks': len([c for c in all_chunks if c.level == 'chunk'])
            },
            children=child_section_ids
        )
        
        all_chunks.append(conversation_chunk)
        
        print(f"    ✅ Created {len(all_chunks)} chunks across 4 levels")
        return all_chunks
    
    def group_messages_into_sections(self, messages: List[Dict]) -> List[List[Dict]]:
        """Group messages into thematic sections"""
        
        if not messages:
            return []
        
        sections = []
        current_section = [messages[0]]
        
        for i in range(1, len(messages)):
            current_msg = messages[i]
            prev_msg = messages[i-1]
            
            # Start new section if:
            # 1. Author changes AND previous message was substantial
            # 2. Large time gap (>1 hour)
            # 3. Current section gets too long (>1500 words)
            
            start_new_section = False
            
            # Author change with substantial previous message
            if (current_msg.get('author') != prev_msg.get('author') and 
                prev_msg.get('word_count', 0) > 30):
                start_new_section = True
            
            # Time gap check
            if (current_msg.get('timestamp') and prev_msg.get('timestamp')):
                time_diff = current_msg['timestamp'] - prev_msg['timestamp']
                if time_diff.total_seconds() > 3600:  # 1 hour
                    start_new_section = True
            
            # Section length check
            section_word_count = sum(msg.get('word_count', 0) for msg in current_section)
            if section_word_count > 1500:
                start_new_section = True
            
            if start_new_section:
                sections.append(current_section)
                current_section = [current_msg]
            else:
                current_section.append(current_msg)
        
        # Add final section
        if current_section:
            sections.append(current_section)
        
        return sections
    
    def store_chunks(self, chunks: List[SemanticChunk]) -> int:
        """Store chunks in database"""
        
        stored_count = 0
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            for chunk in chunks:
                try:
                    # Convert embedding to list for JSON storage
                    embedding_list = chunk.embedding.tolist() if chunk.embedding is not None else None
                    
                    cursor.execute("""
                        INSERT INTO semantic_chunks 
                        (chunk_id, level, parent_id, conversation_id, content, summary, 
                         word_count, embedding, metadata, children)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (chunk_id) DO UPDATE SET
                            content = EXCLUDED.content,
                            summary = EXCLUDED.summary,
                            word_count = EXCLUDED.word_count,
                            embedding = EXCLUDED.embedding,
                            metadata = EXCLUDED.metadata,
                            children = EXCLUDED.children,
                            updated_at = NOW()
                    """, (
                        chunk.chunk_id,
                        chunk.level,
                        chunk.parent_id,
                        chunk.metadata.get('conversation_id'),
                        chunk.content,
                        chunk.summary,
                        chunk.word_count,
                        embedding_list,
                        json.dumps(chunk.metadata),
                        chunk.children
                    ))
                    
                    stored_count += 1
                    
                except Exception as e:
                    print(f"⚠️  Error storing chunk {chunk.chunk_id}: {e}")
                    continue
            
            conn.commit()
        
        return stored_count
    
    def semantic_search(self, query: str, level: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """Perform semantic search across chunks"""
        
        print(f"🔍 Generating embedding for query: '{query}'")
        
        # Generate query embedding using Ollama
        query_embedding = self.generate_embedding(query)
        if query_embedding is None:
            print("❌ Failed to generate query embedding")
            return []
        
        print(f"✅ Generated embedding with {len(query_embedding)} dimensions")
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Build query with optional level filter
            embedding_str = '[' + ','.join(map(str, query_embedding.tolist())) + ']'
            
            if level:
                query_sql = """
                    SELECT chunk_id, level, content, summary, word_count, metadata,
                           embedding <-> %s::vector as similarity
                    FROM semantic_chunks 
                    WHERE embedding IS NOT NULL AND level = %s
                    ORDER BY embedding <-> %s::vector
                    LIMIT %s
                """
                params = [embedding_str, level, embedding_str, limit]
            else:
                query_sql = """
                    SELECT chunk_id, level, content, summary, word_count, metadata,
                           embedding <-> %s::vector as similarity
                    FROM semantic_chunks 
                    WHERE embedding IS NOT NULL
                    ORDER BY embedding <-> %s::vector
                    LIMIT %s
                """
                params = [embedding_str, embedding_str, limit]
            
            cursor.execute(query_sql, params)
            results = cursor.fetchall()
            
            return [dict(row) for row in results]
    
    def test_single_conversation(self, conversation_id: Optional[int] = None) -> Dict[str, Any]:
        """Test hierarchical embedding on a single conversation"""
        
        print(f"🧪 TESTING SINGLE CONVERSATION EMBEDDING")
        
        # Ensure tables exist
        self.ensure_embeddings_tables_exist()
        
        # Get a specific conversation or the top one
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if conversation_id:
                cursor.execute("""
                    SELECT conversation_id, composite_score, category, word_count
                    FROM conversation_quality_assessments
                    WHERE conversation_id = %s AND is_duplicate = FALSE
                """, (conversation_id,))
            else:
                cursor.execute("""
                    SELECT conversation_id, composite_score, category, word_count
                    FROM conversation_quality_assessments
                    WHERE is_duplicate = FALSE 
                        AND composite_score > 0.5
                        AND word_count > 500
                    ORDER BY composite_score DESC
                    LIMIT 1
                """)
            
            conversation = cursor.fetchone()
        
        if not conversation:
            print("❌ No suitable conversation found")
            return {}
        
        conv_id = conversation['conversation_id']
        score = conversation['composite_score']
        category = conversation['category']
        word_count = conversation['word_count']
        
        print(f"📊 Testing Conv {conv_id} ({category}, score: {score:.3f}, words: {word_count})")
        
        try:
            start_time = datetime.now()
            chunks = self.process_conversation_hierarchically(conv_id)
            stored_count = self.store_chunks(chunks)
            processing_time = (datetime.now() - start_time).total_seconds()
            
            results = {
                'conversation_id': conv_id,
                'conversation_score': float(score),
                'category': category,
                'word_count': word_count,
                'chunks_created': stored_count,
                'processing_time_seconds': processing_time,
                'timestamp': datetime.now().isoformat()
            }
            
            print(f"✅ Success! Created {stored_count} chunks in {processing_time:.1f}s")
            
            # Show chunk distribution
            chunk_levels = {}
            for chunk in chunks:
                level = chunk.level
                chunk_levels[level] = chunk_levels.get(level, 0) + 1
            
            print(f"📈 Chunk distribution: {dict(chunk_levels)}")
            
            return results
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return {'error': str(e)}

    def create_batch_job(self, conversation_id: int, priority: int = 5) -> str:
        """Create a new batch job for conversation embedding"""
        job_id = f"embed_{conversation_id}_{int(time.time())}"
        
        conn = sqlite3.connect(self.batch_db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO embedding_jobs (job_id, conversation_id, priority, status, created_at)
            VALUES (?, ?, ?, 'pending', ?)
        ''', (job_id, conversation_id, priority, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        return job_id
    
    def update_job_status(self, job_id: str, status: str, **kwargs):
        """Update batch job status"""
        conn = sqlite3.connect(self.batch_db_path)
        cursor = conn.cursor()
        
        updates = []
        values = []
        
        updates.append("status = ?")
        values.append(status)
        
        if status == 'processing':
            updates.append("started_at = ?")
            values.append(datetime.now().isoformat())
        elif status in ['completed', 'failed']:
            updates.append("completed_at = ?")
            values.append(datetime.now().isoformat())
        
        for key, value in kwargs.items():
            updates.append(f"{key} = ?")
            values.append(value)
        
        values.append(job_id)
        
        cursor.execute(f'''
            UPDATE embedding_jobs 
            SET {', '.join(updates)}
            WHERE job_id = ?
        ''', values)
        
        conn.commit()
        conn.close()
    
    def run_hierarchical_embedding(self, conversation_limit: int = 50, timeout_minutes: int = 30) -> Dict[str, Any]:
        """Run hierarchical embedding on top conversations with batch tracking"""
        
        batch_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        if hasattr(self, 'logger'):
            self.logger.info(f"🚀 Starting hierarchical embedding batch: {batch_id}")
            self.logger.info(f"   Processing up to {conversation_limit} conversations")
            self.logger.info(f"   Timeout set to {timeout_minutes} minutes")
        
        print(f"🚀 HIERARCHICAL SEMANTIC EMBEDDING - Batch {batch_id}")
        print(f"   Processing up to {conversation_limit} conversations")
        print(f"   Timeout: {timeout_minutes} minutes")
        print(f"   Live logs: logs/hierarchical_embedding_*.log")
        
        # Start batch tracking
        conn = sqlite3.connect(self.batch_db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO batch_stats (batch_id, total_conversations, started_at)
            VALUES (?, ?, ?)
        ''', (batch_id, conversation_limit, datetime.now().isoformat()))
        conn.commit()
        conn.close()
        
        # Ensure tables exist
        self.ensure_embeddings_tables_exist()
        
        # Get top quality conversations
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT conversation_id, composite_score, category, word_count
                FROM conversation_quality_assessments
                WHERE is_duplicate = FALSE 
                    AND composite_score > 0.5
                    AND word_count > 500
                ORDER BY composite_score DESC
                LIMIT %s
            """, (conversation_limit,))
            
            conversations = cursor.fetchall()
        
        if not conversations:
            error_msg = "No suitable conversations found"
            if hasattr(self, 'logger'):
                self.logger.error(f"❌ {error_msg}")
            print(f"❌ {error_msg}")
            return {}
        
        if hasattr(self, 'logger'):
            self.logger.info(f"📊 Found {len(conversations)} conversations to process")
        print(f"📊 Processing {len(conversations)} conversations...")
        
        # Create batch jobs
        job_ids = []
        for conv in conversations:
            job_id = self.create_batch_job(conv['conversation_id'])
            job_ids.append(job_id)
        
        if hasattr(self, 'logger'):
            self.logger.info(f"📋 Created {len(job_ids)} batch jobs")
        
        # Process conversations with timeout
        start_time = datetime.now()
        timeout_seconds = timeout_minutes * 60
        total_chunks = 0
        processed_conversations = 0
        failed_conversations = []
        
        for i, conv in enumerate(conversations, 1):
            # Check timeout
            elapsed = (datetime.now() - start_time).total_seconds()
            if elapsed > timeout_seconds:
                if hasattr(self, 'logger'):
                    self.logger.warning(f"⏰ Timeout reached after {timeout_minutes} minutes")
                print(f"⏰ Timeout reached after {timeout_minutes} minutes - stopping processing")
                break
            
            conv_id = conv['conversation_id']
            score = conv['composite_score']
            category = conv['category']
            job_id = job_ids[i-1]
            
            progress_msg = f"   {i:3d}/{len(conversations)}: Conv {conv_id} ({category}, score: {score:.3f})"
            print(progress_msg)
            if hasattr(self, 'logger'):
                self.logger.info(progress_msg)
            
            # Update job to processing
            self.update_job_status(job_id, 'processing')
            
            try:
                conv_start_time = datetime.now()
                chunks = self.process_conversation_hierarchically(conv_id)
                stored_count = self.store_chunks(chunks)
                processing_time = (datetime.now() - conv_start_time).total_seconds()
                
                total_chunks += stored_count
                processed_conversations += 1
                
                # Update job to completed
                self.update_job_status(job_id, 'completed', 
                                     chunks_created=stored_count,
                                     processing_time_seconds=processing_time)
                
                success_msg = f"      ✅ Stored {stored_count} chunks in {processing_time:.1f}s"
                print(success_msg)
                if hasattr(self, 'logger'):
                    self.logger.info(success_msg)
                
                # Brief pause to avoid overwhelming the system
                time.sleep(0.1)
                
            except Exception as e:
                error_msg = f"Error processing conversation {conv_id}: {str(e)}"
                print(f"      ❌ {error_msg}")
                if hasattr(self, 'logger'):
                    self.logger.error(error_msg)
                
                failed_conversations.append((conv_id, str(e)))
                
                # Update job to failed
                self.update_job_status(job_id, 'failed', error_message=str(e))
                continue
        
        # Update batch stats
        conn = sqlite3.connect(self.batch_db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE batch_stats 
            SET conversations_processed = ?, conversations_failed = ?, 
                total_chunks_created = ?, completed_at = ?, status = 'completed'
            WHERE batch_id = ?
        ''', (processed_conversations, len(failed_conversations), total_chunks, 
              datetime.now().isoformat(), batch_id))
        conn.commit()
        conn.close()
        
        results = {
            'batch_id': batch_id,
            'processed_conversations': processed_conversations,
            'failed_conversations': len(failed_conversations),
            'total_chunks_created': total_chunks,
            'average_chunks_per_conversation': total_chunks / processed_conversations if processed_conversations > 0 else 0,
            'failed_conversation_details': failed_conversations,
            'processing_time_minutes': (datetime.now() - start_time).total_seconds() / 60,
            'timestamp': datetime.now().isoformat()
        }
        
        summary = f"\n{'='*80}\n🎉 HIERARCHICAL EMBEDDING COMPLETE - Batch {batch_id}\n{'='*80}"
        summary += f"\n📊 Conversations processed: {processed_conversations}"
        summary += f"\n❌ Conversations failed: {len(failed_conversations)}" 
        summary += f"\n📝 Total chunks created: {total_chunks}"
        summary += f"\n📈 Average chunks per conversation: {results['average_chunks_per_conversation']:.1f}"
        summary += f"\n⏱️ Total processing time: {results['processing_time_minutes']:.1f} minutes"
        summary += f"\n📊 Batch database: {self.batch_db_path}"
        
        print(summary)
        if hasattr(self, 'logger'):
            self.logger.info(summary)
        
        return results


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(
        description="Hierarchical Semantic Embedder - Create multi-level embeddings for archive analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test with single conversation
  python hierarchical_embedder.py test

  # Test specific conversation
  python hierarchical_embedder.py test --conv-id 217431

  # Process top 20 conversations
  python hierarchical_embedder.py embed --limit 20

  # Search across all chunk levels
  python hierarchical_embedder.py search "consciousness and phenomenology"

  # Search only conversation-level summaries
  python hierarchical_embedder.py search "quantum mechanics" --level conversation

  # Search only base chunks
  python hierarchical_embedder.py search "database design" --level chunk
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Test hierarchical embedding on single conversation')
    test_parser.add_argument('--conv-id', type=int, help='Specific conversation ID to test')
    
    # Embedding command
    embed_parser = subparsers.add_parser('embed', help='Create hierarchical embeddings')
    embed_parser.add_argument('--limit', type=int, default=50, help='Max conversations to process')
    embed_parser.add_argument('--timeout', type=int, default=30, help='Timeout in minutes')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Semantic search across chunks')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('--level', choices=['chunk', 'message', 'section', 'conversation'], 
                              help='Limit search to specific chunk level')
    search_parser.add_argument('--limit', type=int, default=10, help='Max results to return')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    embedder = HierarchicalEmbedder()
    
    if args.command == 'test':
        results = embedder.test_single_conversation(args.conv_id)
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"test_runs/single_conversation_test_{timestamp}.json"
        Path("test_runs").mkdir(exist_ok=True)
        
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"📄 Results saved to: {results_file}")
    
    elif args.command == 'embed':
        results = embedder.run_hierarchical_embedding(args.limit, args.timeout)
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"test_runs/hierarchical_embedding_{timestamp}.json"
        Path("test_runs").mkdir(exist_ok=True)
        
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"📄 Results saved to: {results_file}")
    
    elif args.command == 'search':
        print(f"🔍 Searching for: '{args.query}'")
        if args.level:
            print(f"   Limiting to level: {args.level}")
        
        results = embedder.semantic_search(args.query, args.level, args.limit)
        
        if not results:
            print("❌ No results found")
            return
        
        print(f"\n📊 Found {len(results)} results:")
        print("="*80)
        
        for i, result in enumerate(results, 1):
            similarity = 1 - result['similarity']  # Convert distance to similarity
            level = result['level']
            content = result['content'][:200] + "..." if len(result['content']) > 200 else result['content']
            summary = result.get('summary', 'No summary')
            
            print(f"{i:2d}. [{level.upper()}] Similarity: {similarity:.3f}")
            print(f"    Summary: {summary}")
            print(f"    Content: {content}")
            print(f"    Words: {result['word_count']}")
            print()


if __name__ == "__main__":
    main()