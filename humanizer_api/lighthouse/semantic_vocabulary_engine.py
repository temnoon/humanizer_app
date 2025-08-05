"""
Semantic Vocabulary Engine
==========================

Expandable vocabulary system for Persona, Namespace, and Style attributes.
Supports extraction from text, semantic vector guidance, and mathematical projections
between lexical spaces using density matrix transformations.

Core Principles:
- Code meaning can be conveyed in any P×N×S combination
- Vocabulary grows through use and extraction
- Semantic vectors guide transformations
- Mathematical projections between meaning spaces
"""

import json
import torch
import numpy as np
from typing import Dict, List, Set, Optional, Tuple, Any, Union
from pathlib import Path
from dataclasses import dataclass
from collections import defaultdict
import logging
from datetime import datetime

from embedding_config import get_embedding_manager, embed_text

logger = logging.getLogger(__name__)

@dataclass
class SemanticAttribute:
    """A semantic attribute with vector representation and metadata."""
    term: str
    category: str  # "persona", "namespace", "style"
    vector: torch.Tensor
    frequency: int = 1
    confidence: float = 1.0
    examples: List[str] = None
    created_at: datetime = None
    last_used: datetime = None
    
    def __post_init__(self):
        if self.examples is None:
            self.examples = []
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.last_used is None:
            self.last_used = datetime.now()

@dataclass
class ProjectionTarget:
    """Target for mathematical projection between lexical spaces."""
    persona_vector: Optional[torch.Tensor] = None
    namespace_vector: Optional[torch.Tensor] = None
    style_vector: Optional[torch.Tensor] = None
    guidance_words: List[str] = None
    guidance_symbols: List[str] = None
    target_intensity: float = 1.0
    
    def __post_init__(self):
        if self.guidance_words is None:
            self.guidance_words = []
        if self.guidance_symbols is None:
            self.guidance_symbols = []

class SemanticVocabularyEngine:
    """
    Expandable vocabulary engine for semantic attributes and projections.
    
    Manages a growing vocabulary of Persona, Namespace, and Style attributes
    with semantic vector representations for precise transformations.
    """
    
    def __init__(self, vocab_path: str = "./semantic_vocabulary.json"):
        """Initialize the vocabulary engine."""
        self.vocab_path = Path(vocab_path)
        self.embedding_manager = get_embedding_manager()
        
        # Core vocabulary storage
        self.attributes: Dict[str, Dict[str, SemanticAttribute]] = {
            "persona": {},
            "namespace": {},
            "style": {}
        }
        
        # Semantic relationships
        self.attribute_clusters: Dict[str, List[str]] = defaultdict(list)
        self.projection_history: List[Dict[str, Any]] = []
        
        # Load existing vocabulary
        self.load_vocabulary()
        
        # Initialize with core attributes if empty
        if not any(self.attributes.values()):
            self._initialize_core_vocabulary()
        
        logger.info(f"Semantic vocabulary engine initialized with {self.total_attributes()} attributes")
    
    def total_attributes(self) -> int:
        """Get total number of attributes across all categories."""
        return sum(len(attrs) for attrs in self.attributes.values())
    
    def _initialize_core_vocabulary(self):
        """Initialize with fundamental semantic attributes."""
        core_attributes = {
            "persona": [
                "analytical", "intuitive", "skeptical", "devotional", "empirical",
                "mystical", "rational", "emotional", "creative", "systematic",
                "contemplative", "pragmatic", "theoretical", "experiential"
            ],
            "namespace": [
                "scientific", "spiritual", "philosophical", "artistic", "mathematical",
                "psychological", "historical", "cultural", "technological", "natural",
                "social", "personal", "universal", "temporal", "spatial"
            ],
            "style": [
                "rigorous", "flowing", "questioning", "declarative", "poetic",
                "technical", "conversational", "formal", "metaphorical", "direct",
                "nuanced", "bold", "subtle", "comprehensive", "focused"
            ]
        }
        
        for category, terms in core_attributes.items():
            for term in terms:
                self.add_attribute(term, category, examples=[f"Core {category} attribute"])
        
        self.save_vocabulary()
        logger.info("Initialized core vocabulary with fundamental semantic attributes")
    
    def add_attribute(self, term: str, category: str, examples: List[str] = None, 
                     confidence: float = 1.0) -> SemanticAttribute:
        """Add or update a semantic attribute."""
        if category not in self.attributes:
            raise ValueError(f"Invalid category: {category}. Must be one of: persona, namespace, style")
        
        # Generate semantic vector
        try:
            embedding = embed_text(term)
            vector = torch.tensor(embedding, dtype=torch.float32)
        except Exception as e:
            logger.warning(f"Failed to generate embedding for '{term}': {e}")
            # Fallback to random vector (normalized) - use same dimension as configured embedding model
            embedding_dim = getattr(self.embedding_manager, 'active_model_dimensions', 768)
            vector = torch.randn(embedding_dim)
            vector = vector / torch.norm(vector)
        
        if term in self.attributes[category]:
            # Update existing attribute
            attr = self.attributes[category][term]
            attr.frequency += 1
            attr.confidence = max(attr.confidence, confidence)
            attr.last_used = datetime.now()
            if examples:
                attr.examples.extend(examples)
        else:
            # Create new attribute
            attr = SemanticAttribute(
                term=term,
                category=category,
                vector=vector,
                confidence=confidence,
                examples=examples or []
            )
            self.attributes[category][term] = attr
        
        logger.debug(f"Added/updated {category} attribute: {term}")
        return attr
    
    def extract_attributes_from_text(self, text: str, 
                                   extract_new: bool = True) -> Dict[str, List[str]]:
        """
        Extract semantic attributes from text using LLM analysis.
        
        Args:
            text: Text to analyze
            extract_new: Whether to add newly discovered attributes to vocabulary
            
        Returns:
            Dictionary with persona, namespace, style attributes found
        """
        try:
            # Use embedding similarity to find existing attributes
            text_embedding = embed_text(text)
            text_vector = torch.tensor(text_embedding, dtype=torch.float32)
            
            extracted = {"persona": [], "namespace": [], "style": []}
            
            for category, attrs in self.attributes.items():
                similarities = []
                
                for term, attr in attrs.items():
                    # Compute cosine similarity
                    similarity = torch.cosine_similarity(
                        text_vector.unsqueeze(0), 
                        attr.vector.unsqueeze(0)
                    ).item()
                    similarities.append((term, similarity))
                
                # Sort by similarity and take top matches above threshold
                similarities.sort(key=lambda x: x[1], reverse=True)
                threshold = 0.3  # Adjustable similarity threshold
                
                for term, sim in similarities:
                    if sim > threshold:
                        extracted[category].append(term)
                        # Update usage frequency
                        self.attributes[category][term].frequency += 1
                        self.attributes[category][term].last_used = datetime.now()
                    if len(extracted[category]) >= 5:  # Limit to top 5 per category
                        break
            
            # TODO: Add LLM-based extraction for new attributes if extract_new=True
            # This would analyze the text and suggest new semantic attributes
            
            logger.info(f"Extracted attributes from text: {extracted}")
            return extracted
            
        except Exception as e:
            logger.error(f"Attribute extraction failed: {e}")
            return {"persona": [], "namespace": [], "style": []}
    
    def find_similar_attributes(self, query: str, category: str = None, 
                               top_k: int = 10) -> List[Tuple[str, str, float]]:
        """
        Find attributes similar to a query term.
        
        Returns:
            List of (term, category, similarity_score) tuples
        """
        try:
            query_embedding = embed_text(query)
            query_vector = torch.tensor(query_embedding, dtype=torch.float32)
            
            similarities = []
            
            categories = [category] if category else ["persona", "namespace", "style"]
            
            for cat in categories:
                for term, attr in self.attributes[cat].items():
                    similarity = torch.cosine_similarity(
                        query_vector.unsqueeze(0),
                        attr.vector.unsqueeze(0)
                    ).item()
                    similarities.append((term, cat, similarity))
            
            # Sort by similarity and return top k
            similarities.sort(key=lambda x: x[2], reverse=True)
            return similarities[:top_k]
            
        except Exception as e:
            logger.error(f"Similarity search failed: {e}")
            return []
    
    def create_projection_target(self, 
                               persona_terms: List[str] = None,
                               namespace_terms: List[str] = None,
                               style_terms: List[str] = None,
                               guidance_words: List[str] = None,
                               guidance_symbols: List[str] = None,
                               target_intensity: float = 1.0) -> ProjectionTarget:
        """
        Create a projection target for density matrix transformations.
        
        This defines the target lexical space for mathematical projection.
        """
        target = ProjectionTarget(
            guidance_words=guidance_words or [],
            guidance_symbols=guidance_symbols or [],
            target_intensity=target_intensity
        )
        
        # Create composite vectors for each category
        def create_composite_vector(terms: List[str], category: str) -> Optional[torch.Tensor]:
            if not terms:
                return None
            
            vectors = []
            for term in terms:
                if term in self.attributes[category]:
                    vectors.append(self.attributes[category][term].vector)
                else:
                    # Create new attribute if it doesn't exist
                    attr = self.add_attribute(term, category, confidence=0.5)
                    vectors.append(attr.vector)
            
            if vectors:
                # Weighted average (could be more sophisticated)
                composite = torch.stack(vectors).mean(dim=0)
                return composite / torch.norm(composite)  # Normalize
            return None
        
        target.persona_vector = create_composite_vector(persona_terms or [], "persona")
        target.namespace_vector = create_composite_vector(namespace_terms or [], "namespace")
        target.style_vector = create_composite_vector(style_terms or [], "style")
        
        # Add guidance word vectors
        if guidance_words:
            guidance_vectors = []
            for word in guidance_words:
                try:
                    embedding = embed_text(word)
                    guidance_vectors.append(torch.tensor(embedding, dtype=torch.float32))
                except Exception as e:
                    logger.warning(f"Failed to embed guidance word '{word}': {e}")
            
            # Store guidance vectors for use in projection
            target.guidance_vectors = guidance_vectors
        
        logger.info(f"Created projection target with {len(persona_terms or [])} persona, "
                   f"{len(namespace_terms or [])} namespace, {len(style_terms or [])} style terms")
        
        return target
    
    def compute_lexical_projection(self, 
                                 source_vector: torch.Tensor,
                                 projection_target: ProjectionTarget) -> torch.Tensor:
        """
        Compute mathematical projection from source to target lexical space.
        
        This is the core projection operation that transforms the density matrix
        from one lexical space to another guided by semantic vectors.
        """
        # Start with source vector
        projected = source_vector.clone()
        source_dim = projected.shape[0]
        
        # Helper function to align dimensions
        def align_dimension(vector: torch.Tensor, target_dim: int) -> torch.Tensor:
            """Align vector to target dimension by padding or truncating."""
            if vector.shape[0] == target_dim:
                return vector
            elif vector.shape[0] < target_dim:
                # Pad with zeros
                padding = torch.zeros(target_dim - vector.shape[0], dtype=vector.dtype)
                return torch.cat([vector, padding])
            else:
                # Truncate to target dimension
                return vector[:target_dim]
        
        # Project toward each component of the target
        components = [
            ("persona", projection_target.persona_vector),
            ("namespace", projection_target.namespace_vector),
            ("style", projection_target.style_vector)
        ]
        
        projection_strength = projection_target.target_intensity
        
        for component_name, target_vector in components:
            if target_vector is not None:
                # Align dimensions
                aligned_target = align_dimension(target_vector, source_dim)
                
                # Compute projection: proj_v(u) = (u·v / |v|²) * v
                dot_product = torch.dot(projected, aligned_target)
                norm_squared = torch.dot(aligned_target, aligned_target)
                
                if norm_squared > 1e-8:  # Avoid division by zero
                    projection = (dot_product / norm_squared) * aligned_target
                    
                    # Blend with current vector based on projection strength
                    projected = (1 - projection_strength) * projected + projection_strength * projection
                    
                    logger.debug(f"Applied {component_name} projection with strength {projection_strength}")
        
        # Apply guidance word influence
        if hasattr(projection_target, 'guidance_vectors') and projection_target.guidance_vectors:
            # Align all guidance vectors to source dimension
            aligned_guidance = [align_dimension(gv, source_dim) for gv in projection_target.guidance_vectors]
            guidance_composite = torch.stack(aligned_guidance).mean(dim=0)
            guidance_composite = guidance_composite / torch.norm(guidance_composite)
            
            # Gentle influence from guidance words
            guidance_strength = 0.2  # Lighter influence than main components
            projected = (1 - guidance_strength) * projected + guidance_strength * guidance_composite
        
        # Normalize final result
        projected = projected / torch.norm(projected)
        
        return projected
    
    def get_vocabulary_summary(self) -> Dict[str, Any]:
        """Get summary of current vocabulary state."""
        summary = {
            "total_attributes": self.total_attributes(),
            "categories": {},
            "most_frequent": {},
            "recently_used": {}
        }
        
        for category, attrs in self.attributes.items():
            summary["categories"][category] = len(attrs)
            
            # Most frequent
            freq_sorted = sorted(attrs.items(), key=lambda x: x[1].frequency, reverse=True)
            summary["most_frequent"][category] = [
                {"term": term, "frequency": attr.frequency} 
                for term, attr in freq_sorted[:5]
            ]
            
            # Recently used
            recent_sorted = sorted(attrs.items(), key=lambda x: x[1].last_used, reverse=True)
            summary["recently_used"][category] = [
                {"term": term, "last_used": attr.last_used.isoformat()} 
                for term, attr in recent_sorted[:5]
            ]
        
        return summary
    
    def search_vocabulary(self, query: str, category: str = None) -> List[Dict[str, Any]]:
        """Search vocabulary with text matching and semantic similarity."""
        results = []
        
        # Text-based search
        categories = [category] if category else ["persona", "namespace", "style"]
        
        for cat in categories:
            for term, attr in self.attributes[cat].items():
                if query.lower() in term.lower():
                    results.append({
                        "term": term,
                        "category": cat,
                        "match_type": "text",
                        "frequency": attr.frequency,
                        "confidence": attr.confidence,
                        "examples": attr.examples[:3]  # Limit examples
                    })
        
        # Semantic similarity search
        similar = self.find_similar_attributes(query, category, top_k=5)
        for term, cat, similarity in similar:
            if similarity > 0.4:  # Only include reasonably similar terms
                # Avoid duplicates from text search
                if not any(r["term"] == term and r["category"] == cat for r in results):
                    attr = self.attributes[cat][term]
                    results.append({
                        "term": term,
                        "category": cat,
                        "match_type": "semantic",
                        "similarity": similarity,
                        "frequency": attr.frequency,
                        "confidence": attr.confidence,
                        "examples": attr.examples[:3]
                    })
        
        # Sort by relevance (text matches first, then by similarity/frequency)
        results.sort(key=lambda x: (
            x["match_type"] == "text",  # Text matches first
            x.get("similarity", 0),     # Then by similarity
            x["frequency"]              # Then by frequency
        ), reverse=True)
        
        return results
    
    def save_vocabulary(self):
        """Save vocabulary to persistent storage."""
        try:
            # Convert to serializable format
            vocab_data = {
                "metadata": {
                    "total_attributes": self.total_attributes(),
                    "saved_at": datetime.now().isoformat(),
                    "version": "1.0"
                },
                "attributes": {}
            }
            
            for category, attrs in self.attributes.items():
                vocab_data["attributes"][category] = {}
                for term, attr in attrs.items():
                    vocab_data["attributes"][category][term] = {
                        "term": attr.term,
                        "category": attr.category,
                        "vector": attr.vector.tolist(),
                        "frequency": attr.frequency,
                        "confidence": attr.confidence,
                        "examples": attr.examples,
                        "created_at": attr.created_at.isoformat(),
                        "last_used": attr.last_used.isoformat()
                    }
            
            with open(self.vocab_path, 'w') as f:
                json.dump(vocab_data, f, indent=2)
            
            logger.info(f"Vocabulary saved to {self.vocab_path}")
            
        except Exception as e:
            logger.error(f"Failed to save vocabulary: {e}")
    
    def load_vocabulary(self):
        """Load vocabulary from persistent storage."""
        if not self.vocab_path.exists():
            logger.info("No existing vocabulary file found, starting fresh")
            return
        
        try:
            with open(self.vocab_path, 'r') as f:
                vocab_data = json.load(f)
            
            for category, attrs in vocab_data.get("attributes", {}).items():
                self.attributes[category] = {}
                for term, attr_data in attrs.items():
                    attr = SemanticAttribute(
                        term=attr_data["term"],
                        category=attr_data["category"],
                        vector=torch.tensor(attr_data["vector"], dtype=torch.float32),
                        frequency=attr_data["frequency"],
                        confidence=attr_data["confidence"],
                        examples=attr_data["examples"],
                        created_at=datetime.fromisoformat(attr_data["created_at"]),
                        last_used=datetime.fromisoformat(attr_data["last_used"])
                    )
                    self.attributes[category][term] = attr
            
            logger.info(f"Loaded vocabulary with {self.total_attributes()} attributes")
            
        except Exception as e:
            logger.error(f"Failed to load vocabulary: {e}")
            # Initialize fresh if loading fails
            self.attributes = {"persona": {}, "namespace": {}, "style": {}}

# Global vocabulary engine instance
_vocab_engine = None

def get_vocabulary_engine() -> SemanticVocabularyEngine:
    """Get global vocabulary engine instance."""
    global _vocab_engine
    if _vocab_engine is None:
        _vocab_engine = SemanticVocabularyEngine()
    return _vocab_engine

# Example usage and testing
if __name__ == "__main__":
    # Initialize engine
    engine = SemanticVocabularyEngine()
    
    # Test attribute extraction
    text = "This analytical approach to quantum consciousness requires rigorous scientific methodology."
    extracted = engine.extract_attributes_from_text(text)
    print(f"Extracted attributes: {extracted}")
    
    # Test search
    results = engine.search_vocabulary("scientific")
    print(f"Search results for 'scientific': {[r['term'] for r in results[:5]]}")
    
    # Test projection target creation
    target = engine.create_projection_target(
        persona_terms=["analytical", "rigorous"],
        namespace_terms=["scientific", "quantum"],
        style_terms=["technical", "precise"],
        guidance_words=["consciousness", "methodology"]
    )
    print(f"Created projection target with guidance words: {target.guidance_words}")
    
    # Test vocabulary summary
    summary = engine.get_vocabulary_summary()
    print(f"Vocabulary summary: {summary['total_attributes']} total attributes")
    
    # Save vocabulary
    engine.save_vocabulary()
    print("Vocabulary saved successfully")