#!/usr/bin/env python3
"""
Real Embedding Service with sentence-transformers and FAISS
Quantum-aware vector operations for the unified API
"""

import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional, Any, Tuple
import pickle
import json
from pathlib import Path
import logging
import hashlib
from datetime import datetime

logger = logging.getLogger(__name__)

class EmbeddingService:
    """Local-first embedding service with FAISS integration"""
    
    def __init__(self, 
                 model_name: str = "all-mpnet-base-v2",
                 index_path: str = "faiss_index",
                 metadata_path: str = "faiss_metadata.json"):
        """
        Initialize embedding service
        
        Args:
            model_name: HuggingFace model name for sentence-transformers
            index_path: Path to store FAISS index
            metadata_path: Path to store chunk metadata
        """
        self.model_name = model_name
        self.index_path = Path(index_path)
        self.metadata_path = Path(metadata_path)
        
        # Initialize sentence transformer
        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        
        # Initialize FAISS index
        self.index = None
        self.metadata = {}  # Maps faiss_id -> chunk metadata
        self.chunk_id_to_faiss_id = {}  # Maps chunk_id -> faiss_id
        self.next_faiss_id = 0
        
        self._load_or_create_index()
    
    def _load_or_create_index(self):
        """Load existing FAISS index or create new one"""
        if self.index_path.exists():
            logger.info(f"Loading existing FAISS index from {self.index_path}")
            self.index = faiss.read_index(str(self.index_path))
            
            # Load metadata
            if self.metadata_path.exists():
                with open(self.metadata_path, 'r') as f:
                    data = json.load(f)
                    self.metadata = data.get('metadata', {})
                    self.chunk_id_to_faiss_id = data.get('chunk_id_to_faiss_id', {})
                    self.next_faiss_id = data.get('next_faiss_id', 0)
            
            logger.info(f"Loaded index with {self.index.ntotal} vectors")
        else:
            logger.info(f"Creating new FAISS index (dim={self.embedding_dim})")
            # Create L2 (Euclidean) index for similarity search
            self.index = faiss.IndexFlatL2(self.embedding_dim)
            self._save_index()
    
    def _save_index(self):
        """Save FAISS index and metadata to disk"""
        self.index_path.parent.mkdir(exist_ok=True)
        faiss.write_index(self.index, str(self.index_path))
        
        # Save metadata
        metadata_data = {
            'metadata': self.metadata,
            'chunk_id_to_faiss_id': self.chunk_id_to_faiss_id,
            'next_faiss_id': self.next_faiss_id,
            'model_name': self.model_name,
            'embedding_dim': self.embedding_dim,
            'last_updated': datetime.now().isoformat()
        }
        
        with open(self.metadata_path, 'w') as f:
            json.dump(metadata_data, f, indent=2)
    
    def embed_text(self, text: str) -> np.ndarray:
        """Generate embedding for a single text"""
        embedding = self.model.encode([text])[0]
        return embedding.astype(np.float32)
    
    def embed_batch(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for a batch of texts"""
        embeddings = self.model.encode(texts, show_progress_bar=True)
        return embeddings.astype(np.float32)
    
    def add_chunk_embedding(self, 
                           chunk_id: str, 
                           text: str, 
                           doc_id: str,
                           section_ref: Optional[str] = None,
                           metadata: Optional[Dict[str, Any]] = None) -> int:
        """
        Add chunk embedding to FAISS index
        
        Returns:
            faiss_id: Index ID for the added vector
        """
        # Check if chunk already exists
        if chunk_id in self.chunk_id_to_faiss_id:
            logger.warning(f"Chunk {chunk_id} already exists in index")
            return self.chunk_id_to_faiss_id[chunk_id]
        
        # Generate embedding
        embedding = self.embed_text(text)
        
        # Add to FAISS index
        faiss_id = self.next_faiss_id
        self.index.add(embedding.reshape(1, -1))
        
        # Store metadata
        chunk_metadata = {
            'chunk_id': chunk_id,
            'doc_id': doc_id,
            'section_ref': section_ref,
            'text_preview': text[:200] + "..." if len(text) > 200 else text,
            'embedding_model': self.model_name,
            'embedding_dim': self.embedding_dim,
            'added_at': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        
        self.metadata[str(faiss_id)] = chunk_metadata
        self.chunk_id_to_faiss_id[chunk_id] = faiss_id
        self.next_faiss_id += 1
        
        # Save to disk
        self._save_index()
        
        logger.info(f"Added chunk {chunk_id} to FAISS index with ID {faiss_id}")
        return faiss_id
    
    def add_batch_embeddings(self, 
                           chunks: List[Dict[str, Any]]) -> List[int]:
        """
        Add multiple chunk embeddings in batch
        
        Args:
            chunks: List of dicts with keys: chunk_id, text, doc_id, section_ref, metadata
            
        Returns:
            List of faiss_ids
        """
        # Filter out existing chunks
        new_chunks = []
        faiss_ids = []
        
        for chunk in chunks:
            chunk_id = chunk['chunk_id']
            if chunk_id in self.chunk_id_to_faiss_id:
                faiss_ids.append(self.chunk_id_to_faiss_id[chunk_id])
            else:
                new_chunks.append(chunk)
        
        if not new_chunks:
            return faiss_ids
        
        # Generate embeddings in batch
        texts = [chunk['text'] for chunk in new_chunks]
        embeddings = self.embed_batch(texts)
        
        # Add to FAISS index
        start_faiss_id = self.next_faiss_id
        self.index.add(embeddings)
        
        # Store metadata for new chunks
        for i, chunk in enumerate(new_chunks):
            faiss_id = start_faiss_id + i
            
            chunk_metadata = {
                'chunk_id': chunk['chunk_id'],
                'doc_id': chunk['doc_id'],
                'section_ref': chunk.get('section_ref'),
                'text_preview': chunk['text'][:200] + "..." if len(chunk['text']) > 200 else chunk['text'],
                'embedding_model': self.model_name,
                'embedding_dim': self.embedding_dim,
                'added_at': datetime.now().isoformat(),
                'metadata': chunk.get('metadata', {})
            }
            
            self.metadata[str(faiss_id)] = chunk_metadata
            self.chunk_id_to_faiss_id[chunk['chunk_id']] = faiss_id
            faiss_ids.append(faiss_id)
        
        self.next_faiss_id += len(new_chunks)
        self._save_index()
        
        logger.info(f"Added {len(new_chunks)} chunks to FAISS index")
        return faiss_ids
    
    def search_similar(self, 
                      query: str, 
                      k: int = 10,
                      return_embeddings: bool = False) -> List[Dict[str, Any]]:
        """
        Search for similar chunks using text query
        
        Args:
            query: Text query to search for
            k: Number of results to return
            return_embeddings: Whether to include embedding vectors
            
        Returns:
            List of search results with metadata and similarity scores
        """
        if self.index.ntotal == 0:
            return []
        
        # Generate query embedding
        query_embedding = self.embed_text(query)
        
        # Search FAISS index
        distances, indices = self.index.search(query_embedding.reshape(1, -1), k)
        
        results = []
        for i, (distance, faiss_id) in enumerate(zip(distances[0], indices[0])):
            if faiss_id == -1:  # FAISS returns -1 for invalid results
                continue
                
            metadata = self.metadata.get(str(faiss_id), {})
            
            result = {
                'rank': i + 1,
                'faiss_id': int(faiss_id),
                'chunk_id': metadata.get('chunk_id'),
                'doc_id': metadata.get('doc_id'),
                'section_ref': metadata.get('section_ref'),
                'text_preview': metadata.get('text_preview'),
                'similarity_score': float(1 / (1 + distance)),  # Convert L2 distance to similarity
                'l2_distance': float(distance),
                'metadata': metadata.get('metadata', {})
            }
            
            if return_embeddings:
                # Retrieve embedding from index
                embedding = self.index.reconstruct(faiss_id)
                result['embedding'] = embedding.tolist()
            
            results.append(result)
        
        return results
    
    def search_by_embedding(self,
                          embedding: np.ndarray,
                          k: int = 10,
                          return_embeddings: bool = False) -> List[Dict[str, Any]]:
        """Search using a pre-computed embedding vector"""
        if self.index.ntotal == 0:
            return []
        
        embedding = embedding.astype(np.float32)
        distances, indices = self.index.search(embedding.reshape(1, -1), k)
        
        results = []
        for i, (distance, faiss_id) in enumerate(zip(distances[0], indices[0])):
            if faiss_id == -1:
                continue
                
            metadata = self.metadata.get(str(faiss_id), {})
            
            result = {
                'rank': i + 1,
                'faiss_id': int(faiss_id),
                'chunk_id': metadata.get('chunk_id'),
                'doc_id': metadata.get('doc_id'),
                'section_ref': metadata.get('section_ref'),
                'text_preview': metadata.get('text_preview'),
                'similarity_score': float(1 / (1 + distance)),
                'l2_distance': float(distance),
                'metadata': metadata.get('metadata', {})
            }
            
            if return_embeddings:
                embedding_vec = self.index.reconstruct(faiss_id)
                result['embedding'] = embedding_vec.tolist()
            
            results.append(result)
        
        return results
    
    def get_chunk_embedding(self, chunk_id: str) -> Optional[np.ndarray]:
        """Retrieve embedding for a specific chunk"""
        faiss_id = self.chunk_id_to_faiss_id.get(chunk_id)
        if faiss_id is None:
            return None
        
        return self.index.reconstruct(faiss_id)
    
    def get_chunk_metadata(self, chunk_id: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a specific chunk"""
        faiss_id = self.chunk_id_to_faiss_id.get(chunk_id)
        if faiss_id is None:
            return None
        
        return self.metadata.get(str(faiss_id))
    
    def compute_centroid(self, chunk_ids: List[str]) -> Optional[np.ndarray]:
        """Compute centroid embedding for a set of chunks (for kernels)"""
        embeddings = []
        
        for chunk_id in chunk_ids:
            embedding = self.get_chunk_embedding(chunk_id)
            if embedding is not None:
                embeddings.append(embedding)
        
        if not embeddings:
            return None
        
        # Compute weighted centroid (equal weights for now)
        centroid = np.mean(embeddings, axis=0)
        # Normalize to unit length
        centroid = centroid / np.linalg.norm(centroid)
        
        return centroid
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the embedding service"""
        return {
            'model_name': self.model_name,
            'embedding_dim': self.embedding_dim,
            'total_vectors': self.index.ntotal if self.index else 0,
            'total_chunks': len(self.chunk_id_to_faiss_id),
            'index_size_mb': self.index_path.stat().st_size / (1024 * 1024) if self.index_path.exists() else 0,
            'metadata_entries': len(self.metadata)
        }
    
    def clear_index(self):
        """Clear all vectors and metadata (for testing)"""
        logger.warning("Clearing all vectors and metadata")
        self.index = faiss.IndexFlatL2(self.embedding_dim)
        self.metadata = {}
        self.chunk_id_to_faiss_id = {}
        self.next_faiss_id = 0
        self._save_index()

# Global embedding service instance
_embedding_service = None

def get_embedding_service() -> EmbeddingService:
    """Get or create global embedding service instance"""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service

def test_embedding_service():
    """Test the embedding service with sample data"""
    logger.info("Testing embedding service...")
    
    service = get_embedding_service()
    
    # Test sample chunks
    test_chunks = [
        {
            'chunk_id': 'test_chunk_1',
            'text': 'The quick brown fox jumps over the lazy dog.',
            'doc_id': 'test_doc_1',
            'section_ref': 'intro'
        },
        {
            'chunk_id': 'test_chunk_2', 
            'text': 'Machine learning and artificial intelligence are transforming technology.',
            'doc_id': 'test_doc_1',
            'section_ref': 'content'
        },
        {
            'chunk_id': 'test_chunk_3',
            'text': 'Natural language processing enables computers to understand human text.',
            'doc_id': 'test_doc_2',
            'section_ref': 'content'
        }
    ]
    
    # Add embeddings
    faiss_ids = service.add_batch_embeddings(test_chunks)
    logger.info(f"Added test chunks with FAISS IDs: {faiss_ids}")
    
    # Test search
    results = service.search_similar("artificial intelligence machine learning", k=3)
    logger.info(f"Search results:")
    for result in results:
        logger.info(f"  Rank {result['rank']}: {result['chunk_id']} (score: {result['similarity_score']:.3f})")
        logger.info(f"    Text: {result['text_preview']}")
    
    # Test centroid computation
    centroid = service.compute_centroid(['test_chunk_2', 'test_chunk_3'])
    if centroid is not None:
        logger.info(f"Computed centroid with norm: {np.linalg.norm(centroid):.3f}")
    
    # Stats
    stats = service.get_stats()
    logger.info(f"Service stats: {stats}")
    
    return service

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_embedding_service()