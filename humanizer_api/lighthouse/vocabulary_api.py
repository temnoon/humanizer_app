"""
Vocabulary API Router
====================

API endpoints for the expandable semantic vocabulary system.
Supports attribute extraction, search, projection target creation,
and vocabulary management.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
import logging

from semantic_vocabulary_engine import get_vocabulary_engine, ProjectionTarget

logger = logging.getLogger(__name__)

# Pydantic models for API
class AttributeExtractionRequest(BaseModel):
    """Request to extract attributes from text."""
    text: str = Field(..., min_length=1, max_length=10000)
    extract_new: bool = Field(default=True, description="Whether to add new attributes to vocabulary")
    categories: Optional[List[str]] = Field(default=None, description="Limit to specific categories")

class AttributeExtractionResponse(BaseModel):
    """Response with extracted attributes."""
    persona: List[str]
    namespace: List[str]
    style: List[str]
    total_extracted: int
    new_attributes_added: int

class VocabularySearchRequest(BaseModel):
    """Request to search vocabulary."""
    query: str = Field(..., min_length=1, max_length=100)
    category: Optional[str] = Field(default=None, pattern="^(persona|namespace|style)$")
    max_results: int = Field(default=20, ge=1, le=100)

class AttributeInfo(BaseModel):
    """Information about a semantic attribute."""
    term: str
    category: str
    match_type: Optional[str] = None
    similarity: Optional[float] = None
    frequency: int
    confidence: float
    examples: List[str]

class VocabularySearchResponse(BaseModel):
    """Response with search results."""
    query: str
    results: List[AttributeInfo]
    total_results: int

class ProjectionTargetRequest(BaseModel):
    """Request to create a projection target."""
    persona_terms: Optional[List[str]] = Field(default=None)
    namespace_terms: Optional[List[str]] = Field(default=None)
    style_terms: Optional[List[str]] = Field(default=None)
    guidance_words: Optional[List[str]] = Field(default=None)
    guidance_symbols: Optional[List[str]] = Field(default=None)
    target_intensity: float = Field(default=1.0, ge=0.0, le=2.0)

class ProjectionTargetResponse(BaseModel):
    """Response with projection target information."""
    target_id: str
    persona_terms: List[str]
    namespace_terms: List[str] 
    style_terms: List[str]
    guidance_words: List[str]
    guidance_symbols: List[str]
    target_intensity: float
    has_persona_vector: bool
    has_namespace_vector: bool
    has_style_vector: bool

class AddAttributeRequest(BaseModel):
    """Request to add a new attribute."""
    term: str = Field(..., min_length=1, max_length=50)
    category: str = Field(..., pattern="^(persona|namespace|style)$")
    examples: Optional[List[str]] = Field(default=None)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)

class VocabularySummaryResponse(BaseModel):
    """Response with vocabulary summary."""
    total_attributes: int
    persona_count: int
    namespace_count: int
    style_count: int
    most_frequent: Dict[str, List[Dict[str, Any]]]
    recently_used: Dict[str, List[Dict[str, Any]]]

class SimilaritySearchRequest(BaseModel):
    """Request for semantic similarity search."""
    query: str = Field(..., min_length=1, max_length=100)
    category: Optional[str] = Field(default=None, pattern="^(persona|namespace|style)$")
    top_k: int = Field(default=10, ge=1, le=50)
    min_similarity: float = Field(default=0.3, ge=0.0, le=1.0)

class SimilarityResult(BaseModel):
    """Similarity search result."""
    term: str
    category: str
    similarity: float

class SimilaritySearchResponse(BaseModel):
    """Response with similarity search results."""
    query: str
    results: List[SimilarityResult]

# Create router
router = APIRouter(prefix="/api/vocabulary", tags=["Semantic Vocabulary"])

@router.post("/extract", response_model=AttributeExtractionResponse)
async def extract_attributes(request: AttributeExtractionRequest, background_tasks: BackgroundTasks):
    """
    Extract semantic attributes from text.
    
    Analyzes text to identify Persona, Namespace, and Style attributes,
    optionally adding new discoveries to the vocabulary.
    """
    try:
        engine = get_vocabulary_engine()
        
        # Extract attributes
        extracted = engine.extract_attributes_from_text(
            text=request.text,
            extract_new=request.extract_new
        )
        
        # Filter by categories if specified
        if request.categories:
            filtered = {}
            for category in request.categories:
                if category in extracted:
                    filtered[category] = extracted[category]
                else:
                    filtered[category] = []
            extracted = filtered
        
        # Count totals
        total_extracted = sum(len(attrs) for attrs in extracted.values())
        
        # Save vocabulary in background if new attributes were added
        if request.extract_new:
            background_tasks.add_task(engine.save_vocabulary)
        
        return AttributeExtractionResponse(
            persona=extracted.get("persona", []),
            namespace=extracted.get("namespace", []),
            style=extracted.get("style", []),
            total_extracted=total_extracted,
            new_attributes_added=0  # TODO: Track new additions
        )
        
    except Exception as e:
        logger.error(f"Attribute extraction failed: {e}")
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")

@router.post("/search", response_model=VocabularySearchResponse)
async def search_vocabulary(request: VocabularySearchRequest):
    """
    Search the semantic vocabulary.
    
    Supports both text matching and semantic similarity search
    across Persona, Namespace, and Style categories.
    """
    try:
        engine = get_vocabulary_engine()
        
        # Perform search
        results = engine.search_vocabulary(
            query=request.query,
            category=request.category
        )
        
        # Limit results
        results = results[:request.max_results]
        
        # Convert to response format
        attribute_results = []
        for result in results:
            attribute_results.append(AttributeInfo(
                term=result["term"],
                category=result["category"],
                match_type=result.get("match_type"),
                similarity=result.get("similarity"),
                frequency=result["frequency"],
                confidence=result["confidence"],
                examples=result["examples"]
            ))
        
        return VocabularySearchResponse(
            query=request.query,
            results=attribute_results,
            total_results=len(attribute_results)
        )
        
    except Exception as e:
        logger.error(f"Vocabulary search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.post("/projection-target", response_model=ProjectionTargetResponse)
async def create_projection_target(request: ProjectionTargetRequest):
    """
    Create a projection target for density matrix transformations.
    
    Defines the target lexical space for mathematical projection,
    combining Persona, Namespace, Style attributes with guidance words/symbols.
    """
    try:
        engine = get_vocabulary_engine()
        
        # Create projection target
        target = engine.create_projection_target(
            persona_terms=request.persona_terms,
            namespace_terms=request.namespace_terms,
            style_terms=request.style_terms,
            guidance_words=request.guidance_words,
            guidance_symbols=request.guidance_symbols,
            target_intensity=request.target_intensity
        )
        
        # Generate unique ID for this target
        import uuid
        target_id = str(uuid.uuid4())
        
        return ProjectionTargetResponse(
            target_id=target_id,
            persona_terms=request.persona_terms or [],
            namespace_terms=request.namespace_terms or [],
            style_terms=request.style_terms or [],
            guidance_words=request.guidance_words or [],
            guidance_symbols=request.guidance_symbols or [],
            target_intensity=request.target_intensity,
            has_persona_vector=target.persona_vector is not None,
            has_namespace_vector=target.namespace_vector is not None,
            has_style_vector=target.style_vector is not None
        )
        
    except Exception as e:
        logger.error(f"Projection target creation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Target creation failed: {str(e)}")

@router.post("/add-attribute")
async def add_attribute(request: AddAttributeRequest, background_tasks: BackgroundTasks):
    """
    Add a new semantic attribute to the vocabulary.
    
    Expands the vocabulary with user-defined attributes.
    """
    try:
        engine = get_vocabulary_engine()
        
        # Add attribute
        attribute = engine.add_attribute(
            term=request.term,
            category=request.category,
            examples=request.examples,
            confidence=request.confidence
        )
        
        # Save vocabulary in background
        background_tasks.add_task(engine.save_vocabulary)
        
        return {
            "success": True,
            "message": f"Added {request.category} attribute: {request.term}",
            "attribute": {
                "term": attribute.term,
                "category": attribute.category,
                "frequency": attribute.frequency,
                "confidence": attribute.confidence
            }
        }
        
    except Exception as e:
        logger.error(f"Add attribute failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to add attribute: {str(e)}")

@router.get("/summary", response_model=VocabularySummaryResponse)
async def get_vocabulary_summary():
    """
    Get summary of current vocabulary state.
    
    Returns statistics and frequently used attributes.
    """
    try:
        engine = get_vocabulary_engine()
        summary = engine.get_vocabulary_summary()
        
        return VocabularySummaryResponse(
            total_attributes=summary["total_attributes"],
            persona_count=summary["categories"]["persona"],
            namespace_count=summary["categories"]["namespace"],
            style_count=summary["categories"]["style"],
            most_frequent=summary["most_frequent"],
            recently_used=summary["recently_used"]
        )
        
    except Exception as e:
        logger.error(f"Vocabulary summary failed: {e}")
        raise HTTPException(status_code=500, detail=f"Summary failed: {str(e)}")

@router.post("/similarity", response_model=SimilaritySearchResponse)
async def find_similar_attributes(request: SimilaritySearchRequest):
    """
    Find attributes similar to a query using semantic similarity.
    
    Uses embedding similarity to discover related concepts.
    """
    try:
        engine = get_vocabulary_engine()
        
        # Find similar attributes
        similar = engine.find_similar_attributes(
            query=request.query,
            category=request.category,
            top_k=request.top_k
        )
        
        # Filter by minimum similarity
        results = []
        for term, category, similarity in similar:
            if similarity >= request.min_similarity:
                results.append(SimilarityResult(
                    term=term,
                    category=category,
                    similarity=similarity
                ))
        
        return SimilaritySearchResponse(
            query=request.query,
            results=results
        )
        
    except Exception as e:
        logger.error(f"Similarity search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Similarity search failed: {str(e)}")

@router.get("/categories")
async def get_categories():
    """Get all available attribute categories."""
    return {
        "categories": ["persona", "namespace", "style"],
        "descriptions": {
            "persona": "Subjective perspective or viewpoint (analytical, mystical, skeptical, etc.)",
            "namespace": "Domain or context of meaning (scientific, spiritual, artistic, etc.)",
            "style": "Linguistic or expressive approach (rigorous, flowing, poetic, etc.)"
        }
    }

@router.get("/health")
async def vocabulary_health():
    """Check vocabulary system health."""
    try:
        engine = get_vocabulary_engine()
        summary = engine.get_vocabulary_summary()
        
        return {
            "status": "healthy",
            "total_attributes": summary["total_attributes"],
            "embedding_manager_available": True,
            "vocabulary_file_exists": engine.vocab_path.exists()
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "total_attributes": 0,
            "embedding_manager_available": False
        }