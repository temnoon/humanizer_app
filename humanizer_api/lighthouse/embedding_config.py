"""
Embedding Configuration System
=============================

Centralized configuration for embedding models across the entire system.
Supports multiple models (nomic-embed-text via Ollama, sentence-transformers, etc.)
with automatic dimension detection and consistent usage.

Author: Enhanced for multi-model embedding support
"""

import os
import numpy as np
import torch
from typing import Optional, Dict, Any, Union
from dataclasses import dataclass
import logging
import json

logger = logging.getLogger(__name__)

@dataclass
class EmbeddingModelConfig:
    """Configuration for a specific embedding model."""
    name: str
    provider: str  # 'ollama', 'sentence_transformers', 'openai', etc.
    dimensions: Optional[int] = None  # Auto-detected if None
    endpoint: Optional[str] = None  # For API-based models
    model_path: Optional[str] = None  # For local models
    max_tokens: int = 8192
    normalized: bool = True
    # PostgreSQL + pgvector integration
    pgvector_compatible: bool = True
    distance_metric: str = "cosine"  # cosine, l2, inner_product
    index_type: str = "ivfflat"  # ivfflat, hnsw

class EmbeddingManager:
    """
    Central manager for all embedding operations across the system.
    
    Automatically detects dimensions, manages different model types,
    and provides consistent embedding generation.
    """
    
    def __init__(self, config_path: str = "./embedding_config.json"):
        self.config_path = config_path
        self.models: Dict[str, EmbeddingModelConfig] = {}
        self.active_model: Optional[str] = None
        self._embedding_cache = {}
        
        # Load configuration
        self.load_config()
        
        # Initialize active model
        if not self.active_model and self.models:
            self.active_model = list(self.models.keys())[0]
            logger.info(f"Set default active model: {self.active_model}")
    
    def load_config(self):
        """Load embedding configuration from file or create defaults."""
        
        # Default configurations
        default_configs = {
            "nomic-embed-text": EmbeddingModelConfig(
                name="nomic-embed-text",
                provider="ollama",
                dimensions=768,  # Known dimension for nomic-embed-text
                endpoint="http://localhost:11434/api/embeddings",
                max_tokens=8192,
                normalized=True,
                pgvector_compatible=True,
                distance_metric="cosine",
                index_type="ivfflat"
            ),
            "all-MiniLM-L6-v2": EmbeddingModelConfig(
                name="all-MiniLM-L6-v2", 
                provider="sentence_transformers",
                dimensions=384,  # Known dimension
                max_tokens=512,
                normalized=True,
                pgvector_compatible=True,
                distance_metric="cosine",
                index_type="ivfflat"
            ),
            "text-embedding-ada-002": EmbeddingModelConfig(
                name="text-embedding-ada-002",
                provider="openai",
                dimensions=1536,
                max_tokens=8191,
                normalized=True,
                pgvector_compatible=True,
                distance_metric="cosine",
                index_type="hnsw"
            )
        }
        
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config_data = json.load(f)
                    
                # Convert to EmbeddingModelConfig objects
                for name, config in config_data.get('models', {}).items():
                    self.models[name] = EmbeddingModelConfig(**config)
                    
                self.active_model = config_data.get('active_model')
                
                logger.info(f"Loaded embedding config from {self.config_path}")
            else:
                # Use defaults
                self.models = default_configs
                self.active_model = "nomic-embed-text"  # Prefer nomic for consistency with archive
                self.save_config()
                
                logger.info("Created default embedding configuration")
                
        except Exception as e:
            logger.error(f"Error loading embedding config: {e}")
            self.models = default_configs
            self.active_model = "nomic-embed-text"
    
    def save_config(self):
        """Save current configuration to file."""
        try:
            config_data = {
                'active_model': self.active_model,
                'models': {
                    name: {
                        'name': model.name,
                        'provider': model.provider,
                        'dimensions': model.dimensions,
                        'endpoint': model.endpoint,
                        'model_path': model.model_path,
                        'max_tokens': model.max_tokens,
                        'normalized': model.normalized
                    }
                    for name, model in self.models.items()
                }
            }
            
            with open(self.config_path, 'w') as f:
                json.dump(config_data, f, indent=2)
                
            logger.info(f"Saved embedding config to {self.config_path}")
            
        except Exception as e:
            logger.error(f"Error saving embedding config: {e}")
    
    def set_active_model(self, model_name: str):
        """Set the active embedding model."""
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not configured. Available: {list(self.models.keys())}")
        
        self.active_model = model_name
        self.save_config()
        logger.info(f"Set active embedding model: {model_name}")
    
    def get_active_config(self) -> EmbeddingModelConfig:
        """Get configuration for the active model."""
        if not self.active_model:
            raise ValueError("No active embedding model set")
        
        return self.models[self.active_model]
    
    def auto_detect_dimensions(self, model_name: str) -> int:
        """Auto-detect embedding dimensions for a model."""
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not configured")
        
        config = self.models[model_name]
        
        # If dimensions already known, return them
        if config.dimensions:
            return config.dimensions
        
        try:
            # Generate a test embedding to detect dimensions
            test_embedding = self._generate_test_embedding(config)
            dimensions = len(test_embedding)
            
            # Update configuration
            config.dimensions = dimensions
            self.save_config()
            
            logger.info(f"Auto-detected {dimensions} dimensions for {model_name}")
            return dimensions
            
        except Exception as e:
            logger.error(f"Failed to auto-detect dimensions for {model_name}: {e}")
            # Fallback to common dimension
            fallback_dims = 768  # Common dimension
            config.dimensions = fallback_dims
            return fallback_dims
    
    def _generate_test_embedding(self, config: EmbeddingModelConfig) -> np.ndarray:
        """Generate a test embedding to detect dimensions."""
        test_text = "This is a test sentence for dimension detection."
        
        if config.provider == "ollama":
            return self._embed_ollama(test_text, config)
        elif config.provider == "sentence_transformers":
            return self._embed_sentence_transformers(test_text, config)
        elif config.provider == "openai":
            return self._embed_openai(test_text, config)
        else:
            raise ValueError(f"Unsupported provider: {config.provider}")
    
    def embed_text(self, text: str, model_name: Optional[str] = None) -> np.ndarray:
        """Generate embedding for text using specified or active model."""
        
        if model_name is None:
            model_name = self.active_model
        
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not configured")
        
        config = self.models[model_name]
        
        # Auto-detect dimensions if not known
        if config.dimensions is None:
            self.auto_detect_dimensions(model_name)
        
        # Generate embedding
        try:
            if config.provider == "ollama":
                embedding = self._embed_ollama(text, config)
            elif config.provider == "sentence_transformers":
                embedding = self._embed_sentence_transformers(text, config)
            elif config.provider == "openai":
                embedding = self._embed_openai(text, config)
            else:
                raise ValueError(f"Unsupported provider: {config.provider}")
            
            return embedding
            
        except Exception as e:
            logger.error(f"Embedding generation failed for {model_name}: {e}")
            raise
    
    def _embed_ollama(self, text: str, config: EmbeddingModelConfig) -> np.ndarray:
        """Generate embedding using Ollama."""
        try:
            import httpx
            
            response = httpx.post(
                config.endpoint,
                json={
                    "model": config.name,
                    "prompt": text
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                embedding = np.array(data["embedding"], dtype=np.float32)
                
                if config.normalized:
                    embedding = embedding / np.linalg.norm(embedding)
                
                return embedding
            else:
                raise Exception(f"Ollama API error: {response.status_code}")
                
        except ImportError:
            raise Exception("httpx required for Ollama embeddings")
    
    def _embed_sentence_transformers(self, text: str, config: EmbeddingModelConfig) -> np.ndarray:
        """Generate embedding using sentence-transformers."""
        try:
            from sentence_transformers import SentenceTransformer
            
            # Cache model instances
            cache_key = f"st_{config.name}"
            if cache_key not in self._embedding_cache:
                self._embedding_cache[cache_key] = SentenceTransformer(config.name)
            
            model = self._embedding_cache[cache_key]
            embedding = model.encode(text, convert_to_numpy=True)
            
            if config.normalized:
                embedding = embedding / np.linalg.norm(embedding)
            
            return embedding.astype(np.float32)
            
        except ImportError:
            raise Exception("sentence-transformers required for this provider")
    
    def _embed_openai(self, text: str, config: EmbeddingModelConfig) -> np.ndarray:
        """Generate embedding using OpenAI API."""
        try:
            import openai
            
            response = openai.embeddings.create(
                model=config.name,
                input=text
            )
            
            embedding = np.array(response.data[0].embedding, dtype=np.float32)
            
            if config.normalized:
                embedding = embedding / np.linalg.norm(embedding)
            
            return embedding
            
        except ImportError:
            raise Exception("openai package required for OpenAI embeddings")
    
    def get_dimensions(self, model_name: Optional[str] = None) -> int:
        """Get embedding dimensions for specified or active model."""
        if model_name is None:
            model_name = self.active_model
        
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not configured")
        
        config = self.models[model_name]
        
        if config.dimensions is None:
            return self.auto_detect_dimensions(model_name)
        
        return config.dimensions
    
    def list_models(self) -> Dict[str, Dict[str, Any]]:
        """List all configured models with their details."""
        return {
            name: {
                'provider': config.provider,
                'dimensions': config.dimensions,
                'active': (name == self.active_model)
            }
            for name, config in self.models.items()
        }
    
    def add_model(self, config: EmbeddingModelConfig):
        """Add a new embedding model configuration."""
        self.models[config.name] = config
        self.save_config()
        logger.info(f"Added embedding model: {config.name}")
    
    def test_model(self, model_name: str) -> Dict[str, Any]:
        """Test an embedding model and return details."""
        try:
            test_text = "This is a test sentence for embedding validation."
            embedding = self.embed_text(test_text, model_name)
            
            return {
                'model': model_name,
                'status': 'success',
                'dimensions': len(embedding),
                'sample_values': embedding[:5].tolist(),
                'norm': float(np.linalg.norm(embedding))
            }
            
        except Exception as e:
            return {
                'model': model_name,
                'status': 'error',
                'error': str(e)
            }
    
    def get_pgvector_config(self, model_name: Optional[str] = None) -> Dict[str, Any]:
        """Get PostgreSQL + pgvector configuration for a model."""
        if model_name is None:
            model_name = self.active_model
        
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not configured")
        
        config = self.models[model_name]
        
        return {
            'dimensions': config.dimensions or self.get_dimensions(model_name),
            'distance_metric': config.distance_metric,
            'index_type': config.index_type,
            'vector_type': f"vector({config.dimensions or self.get_dimensions(model_name)})",
            'similarity_function': self._get_pgvector_similarity_function(config.distance_metric),
            'index_options': self._get_pgvector_index_options(config.index_type, config.dimensions or self.get_dimensions(model_name))
        }
    
    def _get_pgvector_similarity_function(self, distance_metric: str) -> str:
        """Get the appropriate pgvector similarity function."""
        similarity_functions = {
            'cosine': '<=>',      # cosine distance (lower is more similar)
            'l2': '<->',          # L2/Euclidean distance  
            'inner_product': '<#>' # negative inner product
        }
        return similarity_functions.get(distance_metric, '<=>')
    
    def _get_pgvector_index_options(self, index_type: str, dimensions: int) -> Dict[str, Any]:
        """Get pgvector index creation options."""
        if index_type == "ivfflat":
            # Rule of thumb: lists = rows/1000, but clamp between 10-4096
            lists = max(10, min(4096, dimensions * 2))
            return {
                'type': 'ivfflat',
                'options': f"WITH (lists = {lists})"
            }
        elif index_type == "hnsw":
            # HNSW parameters for high-dimensional embeddings
            m = min(64, max(16, dimensions // 20))  # connections per layer
            ef_construction = min(400, max(200, dimensions // 2))
            return {
                'type': 'hnsw', 
                'options': f"WITH (m = {m}, ef_construction = {ef_construction})"
            }
        else:
            return {'type': 'ivfflat', 'options': 'WITH (lists = 100)'}
    
    def generate_pgvector_schema(self, model_name: Optional[str] = None, table_name: str = "embeddings") -> str:
        """Generate PostgreSQL schema for embedding storage with pgvector."""
        config = self.get_pgvector_config(model_name)
        
        schema = f"""
-- Schema for {model_name or self.active_model} embeddings
-- Dimensions: {config['dimensions']}, Distance: {config['distance_metric']}

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS {table_name} (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding {config['vector_type']} NOT NULL,
    metadata JSONB DEFAULT '{{}}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create pgvector index for similarity search
CREATE INDEX IF NOT EXISTS {table_name}_embedding_idx 
ON {table_name} USING {config['index_options']['type']} (embedding {config['index_options']['options']});

-- Example similarity search query:
-- SELECT content, (embedding {config['similarity_function']} $1::vector) as distance 
-- FROM {table_name} 
-- ORDER BY embedding {config['similarity_function']} $1::vector 
-- LIMIT 10;
"""
        return schema.strip()

    def validate_pgvector_compatibility(self, model_name: Optional[str] = None) -> Dict[str, Any]:
        """Validate that a model is compatible with existing pgvector setup."""
        if model_name is None:
            model_name = self.active_model
        
        config = self.models[model_name]
        validation = {
            'model': model_name,
            'compatible': True,
            'issues': [],
            'recommendations': []
        }
        
        # Check if dimensions match existing schema (768 for nomic-embed-text)
        expected_dims = 768  # Your existing setup
        actual_dims = config.dimensions or self.get_dimensions(model_name)
        
        if actual_dims != expected_dims:
            validation['compatible'] = False
            validation['issues'].append(
                f"Dimension mismatch: model produces {actual_dims}D, schema expects {expected_dims}D"
            )
            validation['recommendations'].append(
                f"Either use a {expected_dims}D model or update schema to vector({actual_dims})"
            )
        
        # Check if pgvector extension is available (would need DB connection to verify)
        validation['recommendations'].append(
            "Verify pgvector extension is installed: CREATE EXTENSION IF NOT EXISTS vector;"
        )
        
        return validation

# Global embedding manager instance
_embedding_manager = None

def get_embedding_manager() -> EmbeddingManager:
    """Get the global embedding manager instance."""
    global _embedding_manager
    if _embedding_manager is None:
        _embedding_manager = EmbeddingManager()
    return _embedding_manager

def embed_text(text: str, model_name: Optional[str] = None) -> np.ndarray:
    """Convenience function for text embedding."""
    return get_embedding_manager().embed_text(text, model_name)

def get_embedding_dimensions(model_name: Optional[str] = None) -> int:
    """Convenience function to get embedding dimensions."""
    return get_embedding_manager().get_dimensions(model_name)

def set_active_embedding_model(model_name: str):
    """Convenience function to set active model."""
    return get_embedding_manager().set_active_model(model_name)

# Example usage and testing
if __name__ == "__main__":
    # Initialize manager
    manager = EmbeddingManager()
    
    # List available models
    print("Available models:")
    for name, details in manager.list_models().items():
        print(f"  {name}: {details}")
    
    # Test active model
    print(f"\nTesting active model: {manager.active_model}")
    result = manager.test_model(manager.active_model)
    print(json.dumps(result, indent=2))