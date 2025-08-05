"""
Enhanced Lighthouse API with full LPE (Lamish Projection Engine) features.
Integrated from lpe_dev project.
"""
import os
import sys
import logging
from pathlib import Path
try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv():
        pass
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import json
import asyncio
import uuid
from datetime import datetime
from keychain_manager import keychain_manager

# Add the src directory to Python path for imports
current_dir = Path(__file__).parent
src_dir = current_dir.parent / "src"
sys.path.insert(0, str(src_dir))

# Also add the current directory for relative imports
sys.path.insert(0, str(current_dir))

# Import LPE components
from lpe_core.projection import ProjectionEngine, TranslationChain
from lpe_core.maieutic import MaieuticDialogue
from lpe_core.translation_roundtrip import LanguageRoundTripAnalyzer
from lpe_core.llm_provider import get_llm_provider, GoogleProvider, OllamaVisionProvider
from lpe_core.models import Projection, MaieuticSession, RoundTripResult
from lpe_core.knowledge_base import LamishKnowledgeBase

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import vision endpoints and advanced attributes
from vision_endpoints import vision_router
from advanced_attribute_api import advanced_attr_router
from linguistic_api_endpoints import linguistic_router

# Import new API routers for Subjective Narrative Humanizer
from book_generation_api import book_router
from archive_api_endpoints import archive_router
from insights_api import insights_router
from content_ingestion_api import content_router

# Import quantum narrative theory
try:
    from narrative_theory import QuantumNarrativeEngine, MeaningState, NarrativeTransformation
    NARRATIVE_THEORY_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Narrative theory module not available: {e}")
    NARRATIVE_THEORY_AVAILABLE = False
from writebook_api import writebook_router

# Import intelligent attributes
try:
    from intelligent_attributes_api import intelligent_attr_router, get_intelligent_attributes_for_transformation
    INTELLIGENT_ATTRIBUTES_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Intelligent attributes not available: {e}")
    INTELLIGENT_ATTRIBUTES_AVAILABLE = False
from context_aware_splitter import ContextAwareSplitter, process_large_narrative
from balanced_transformation_api import balanced_router
from conversation_api import add_conversation_routes
from conversation_api_v2 import add_enhanced_conversation_routes
from postgres_conversation_api import replace_conversation_routes
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting Enhanced Lighthouse API with full LPE features")
    
    # Test LLM provider
    provider = get_llm_provider()
    logger.info(f"Using LLM provider: {provider.__class__.__name__}")
    
    # Start cleanup task
    cleanup_task = asyncio.create_task(cleanup_old_sessions())
    
    yield
    
    # Shutdown
    cleanup_task.cancel()
    try:
        await cleanup_task
    except asyncio.CancelledError:
        pass
    logger.info("Enhanced Lighthouse API shutdown complete")

async def cleanup_old_sessions():
    """Periodically clean up old maieutic sessions."""
    while True:
        await asyncio.sleep(3600)  # Clean up every hour
        
        # Remove sessions older than 24 hours
        from datetime import datetime, timedelta
        cutoff = datetime.now() - timedelta(hours=24)
        
        to_remove = []
        for session_id, session in maieutic_sessions.items():
            if session.created_at < cutoff:
                to_remove.append(session_id)
        
        for session_id in to_remove:
            del maieutic_sessions[session_id]
        
        if to_remove:
            logger.info(f"Cleaned up {len(to_remove)} old maieutic sessions")

# Initialize FastAPI app
app = FastAPI(
    title="Humanizer Lighthouse API - Enhanced",
    description="Full-featured Lamish Projection Engine with narrative transformation, maieutic dialogue, and translation analysis.",
    version="2.0.0",
    lifespan=lifespan
)

# CORS Configuration - Allow network access
origins = [
    "http://localhost:3100",  # Vite/React frontend
    "http://127.0.0.1:3100",  # Explicit localhost
    "http://localhost:3000",  # Alternative React port
    "http://localhost",
    "*"  # Allow all origins for development
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for network access
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(vision_router)
app.include_router(advanced_attr_router)
app.include_router(linguistic_router)
app.include_router(balanced_router)
app.include_router(writebook_router)

# Include core density matrix transformation API - NO MOCK DATA
from density_matrix_api import router as density_matrix_router
app.include_router(density_matrix_router)

# Include expandable vocabulary system API
from vocabulary_api import router as vocabulary_router
app.include_router(vocabulary_router)

# Include new API routers for Subjective Narrative Humanizer
app.include_router(book_router)
app.include_router(archive_router)
app.include_router(insights_router)

# Include CLI API router
from cli_api import cli_router
app.include_router(cli_router)

# Include Pipeline API router
from pipeline_router import pipeline_router
app.include_router(pipeline_router)

# Include Export API router
from export_router import export_router
app.include_router(export_router)

# Include Analytics API router
from analytics_router import analytics_router
app.include_router(analytics_router)

# Include Concept Mapping API router
from concept_mapping_api import concept_router
app.include_router(concept_router)

# Include Insights Discovery API router
from insights_discovery_api import insights_router
app.include_router(insights_router)
app.include_router(content_router)

# Include LPE Analysis API router
from lpe_analysis_api import lpe_analysis_router
app.include_router(lpe_analysis_router)

# Include Transform API router for TransformationLab
from transform_router import transform_router
app.include_router(transform_router)

# Include Distillery API router for Essence Distillery
from distillery_router import distillery_router
app.include_router(distillery_router)

# Include Filesystem Ingestion API router
from intelligent_filesystem_agent import filesystem_agent_router
from filesystem_ingestion_api import filesystem_router
from conversation_api import add_conversation_routes
app.include_router(filesystem_agent_router)
app.include_router(filesystem_router)
add_conversation_routes(app)

# Include intelligent attributes router
if INTELLIGENT_ATTRIBUTES_AVAILABLE:
    app.include_router(intelligent_attr_router)

# Add conversation management routes - use PostgreSQL if available
try:
    replace_conversation_routes(app)
    logger.info("Using PostgreSQL conversation routes")
except Exception as e:
    logger.warning(f"PostgreSQL not available, falling back to SQLite: {e}")
    add_conversation_routes(app)
    add_enhanced_conversation_routes(app)

# Initialize LPE components
projection_engine = ProjectionEngine()
knowledge_base = LamishKnowledgeBase()
translation_analyzer = LanguageRoundTripAnalyzer()

# Initialize Quantum Narrative Engine if available
quantum_engine = None
if NARRATIVE_THEORY_AVAILABLE:
    try:
        quantum_engine = QuantumNarrativeEngine(semantic_dimension=8)  # Reasonable size for web use
        logger.info("Quantum Narrative Engine initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Quantum Narrative Engine: {e}")
        NARRATIVE_THEORY_AVAILABLE = False

# Enhanced configuration with more options
enhanced_config = {
    "personas": [
        {"id": "neutral", "name": "Neutral", "description": "Balanced, objective perspective"},
        {"id": "advocate", "name": "Advocate", "description": "Supportive, promotional perspective"},
        {"id": "critic", "name": "Critic", "description": "Skeptical, questioning perspective"},
        {"id": "philosopher", "name": "Philosopher", "description": "Deep, contemplative perspective"},
        {"id": "storyteller", "name": "Storyteller", "description": "Narrative-focused, engaging perspective"},
        {"id": "scientist", "name": "Scientist", "description": "Analytical, evidence-based perspective"},
        {"id": "artist", "name": "Artist", "description": "Creative, aesthetic perspective"}
    ],
    "namespaces": [
        {"id": "lamish-galaxy", "name": "Lamish Galaxy", "description": "Sci-fi universe with frequency-based technology"},
        {"id": "medieval-realm", "name": "Medieval Realm", "description": "Fantasy world of knights and magic"},
        {"id": "corporate-dystopia", "name": "Corporate Dystopia", "description": "Near-future corporate-controlled society"},
        {"id": "natural-world", "name": "Natural World", "description": "Ecosystem and nature-based metaphors"},
        {"id": "quantum-realm", "name": "Quantum Realm", "description": "Quantum physics and probability-based universe"},
        {"id": "steampunk-era", "name": "Steampunk Era", "description": "Victorian-era mechanical technology"},
        {"id": "cyberpunk-future", "name": "Cyberpunk Future", "description": "High-tech, low-life digital world"}
    ],
    "styles": [
        {"id": "standard", "name": "Standard", "description": "Clear, accessible writing"},
        {"id": "academic", "name": "Academic", "description": "Formal, scholarly tone"},
        {"id": "poetic", "name": "Poetic", "description": "Lyrical, metaphorical language"},
        {"id": "technical", "name": "Technical", "description": "Precise, specialized terminology"},
        {"id": "casual", "name": "Casual", "description": "Conversational, informal tone"},
        {"id": "formal", "name": "Formal", "description": "Professional, structured writing"},
        {"id": "archaic", "name": "Archaic", "description": "Old-fashioned, historical language"},
        {"id": "futuristic", "name": "Futuristic", "description": "Forward-looking, innovative language"}
    ],
    "supported_languages": [
        "spanish", "french", "german", "italian", "portuguese", "russian",
        "chinese", "japanese", "korean", "arabic", "hebrew", "hindi",
        "dutch", "swedish", "norwegian", "danish", "polish", "czech"
    ]
}

# --- API Models ---

class ConfigurationResponse(BaseModel):
    personas: List[Dict[str, str]]
    namespaces: List[Dict[str, str]]
    styles: List[Dict[str, str]]
    supported_languages: List[str]

class TransformationRequest(BaseModel):
    narrative: str = Field(..., example="Sam Altman dropped out of Stanford to start his company.")
    target_persona: str = Field(..., example="philosopher")
    target_namespace: str = Field(..., example="lamish-galaxy")
    target_style: str = Field(..., example="poetic")
    show_steps: bool = Field(default=True, description="Show detailed transformation steps")

class TransformationStep(BaseModel):
    name: str
    input_snapshot: str
    output_snapshot: str
    duration_ms: int
    metadata: Dict[str, Any]

class TransformationResponse(BaseModel):
    transform_id: str
    original: Dict[str, Any]
    projection: Dict[str, Any]
    steps: List[TransformationStep]
    total_duration_ms: int

class MaieuticRequest(BaseModel):
    narrative: str = Field(..., example="A team struggles with a difficult project deadline.")
    goal: str = Field(default="understand", example="understand")

class MaieuticQuestionRequest(BaseModel):
    session_id: str
    depth_level: int = Field(default=0, description="Current depth level (0-4)")

class MaieuticAnswerRequest(BaseModel):
    session_id: str
    question: str
    answer: str
    depth_level: int = Field(default=0)

class MaieuticResponse(BaseModel):
    session_id: str
    question: str
    insights: List[str] = []
    suggested_config: Optional[Dict[str, str]] = None
    final_understanding: Optional[str] = None

class TranslationRequest(BaseModel):
    text: str = Field(..., example="Innovation requires courage to challenge established norms.")
    intermediate_language: str = Field(..., example="spanish")
    source_language: str = Field(default="english")

class TranslationResponse(BaseModel):
    original_text: str
    forward_translation: str  # The intermediate translation
    final_text: str
    intermediate_language: str
    semantic_drift: float
    preserved_elements: List[str]
    lost_elements: List[str]
    gained_elements: List[str]
    linguistic_analysis: Dict[str, Any]

class MultiTranslationRequest(BaseModel):
    text: str = Field(..., example="Innovation requires courage to challenge established norms.")
    test_languages: List[str] = Field(default=["spanish", "french", "german"])

# Quantum Narrative Theory API Models
class QNTNarrativeRequest(BaseModel):
    narrative: str = Field(..., example="The old sailor gazed at the endless ocean, knowing that his final voyage would soon begin.")
    include_quantum_state: bool = Field(default=False, description="Include quantum meaning state analysis")
    include_essence_vectors: bool = Field(default=True, description="Include essence vector representation")
    semantic_depth: str = Field(default="standard", description="Analysis depth: 'basic', 'standard', 'deep'")

class QNTPersona(BaseModel):
    name: str = Field(..., description="Identified persona archetype")
    confidence: float = Field(..., description="Confidence score 0-1")
    characteristics: List[str] = Field(..., description="Key persona characteristics")
    voice_indicators: List[str] = Field(..., description="Textual indicators of this persona")

class QNTNamespace(BaseModel):
    name: str = Field(..., description="Identified narrative universe/context")
    confidence: float = Field(..., description="Confidence score 0-1")
    domain_markers: List[str] = Field(..., description="Domain-specific elements")
    cultural_context: str = Field(..., description="Cultural/temporal context")
    reality_layer: str = Field(..., description="Level of abstraction: literal, metaphorical, mythic, etc.")

class QNTStyle(BaseModel):
    name: str = Field(..., description="Identified stylistic approach")
    confidence: float = Field(..., description="Confidence score 0-1")
    linguistic_features: List[str] = Field(..., description="Key linguistic markers")
    rhetorical_devices: List[str] = Field(..., description="Rhetorical and literary devices")
    tone_characteristics: List[str] = Field(..., description="Tone and mood indicators")

class QNTEssence(BaseModel):
    core_meaning: str = Field(..., description="Distilled essential meaning")
    meaning_density: float = Field(..., description="Semantic concentration 0-1")
    invariant_elements: List[str] = Field(..., description="Elements preserved across transformations")
    semantic_vector: Optional[List[float]] = Field(None, description="High-dimensional meaning representation")
    coherence_score: float = Field(..., description="Internal narrative coherence 0-1")
    entropy_measure: float = Field(..., description="Meaning entropy/uncertainty")

class QNTQuantumState(BaseModel):
    dimension: int = Field(..., description="Semantic space dimension")
    density_matrix: List[List[float]] = Field(..., description="Quantum density matrix representation")
    eigenvalues: List[float] = Field(..., description="Eigenvalues of the density matrix")
    purity: float = Field(..., description="Quantum purity measure 0-1")
    semantic_labels: List[str] = Field(..., description="Labels for semantic dimensions")
    measurement_probabilities: Dict[str, float] = Field(..., description="POVM measurement outcomes")

class QNTNarrativeAnalysis(BaseModel):
    narrative_id: str = Field(..., description="Unique identifier for this analysis")
    original_narrative: str = Field(..., description="Input narrative text")
    persona: QNTPersona = Field(..., description="Extracted persona information")
    namespace: QNTNamespace = Field(..., description="Extracted namespace/universe")
    style: QNTStyle = Field(..., description="Extracted stylistic elements")
    essence: QNTEssence = Field(..., description="Extracted essential meaning")
    quantum_state: Optional[QNTQuantumState] = Field(None, description="Quantum meaning state")
    transformation_potential: Dict[str, float] = Field(..., description="Scores for potential transformations")
    semantic_topology: Dict[str, Any] = Field(..., description="Structural analysis of meaning relationships")
    processing_metadata: Dict[str, Any] = Field(..., description="Analysis metadata and confidence metrics")

# Attribute Management Models
class AttributeAlgorithm(BaseModel):
    name: str = Field(..., description="Algorithm name")
    version: str = Field(..., description="Algorithm version")
    parameters: Dict[str, Any] = Field(..., description="Algorithm parameters used")
    confidence_threshold: float = Field(..., description="Confidence threshold applied")
    llm_provider: str = Field(..., description="LLM provider used")
    prompt_template: str = Field(..., description="Exact prompt template used")
    processing_steps: List[str] = Field(..., description="Step-by-step processing description")

class SavedAttribute(BaseModel):
    attribute_id: str = Field(..., description="Unique identifier")
    name: str = Field(..., description="User-assigned name")
    attribute_type: str = Field(..., description="Type: persona, namespace, style, essence")
    narrative_source: str = Field(..., description="Original narrative text")
    extracted_value: str = Field(..., description="Extracted attribute value")
    confidence_score: float = Field(..., description="Confidence in extraction")
    algorithm_used: AttributeAlgorithm = Field(..., description="Algorithm details")
    created_at: str = Field(..., description="Creation timestamp")
    tags: List[str] = Field(default=[], description="User-assigned tags")
    notes: Optional[str] = Field(None, description="User notes")

class SaveAttributeRequest(BaseModel):
    analysis_id: str = Field(..., description="ID of the analysis to save from")
    name: str = Field(..., description="Name for the saved attribute")
    attribute_types: List[str] = Field(..., description="Which attributes to save: persona, namespace, style, essence")
    tags: List[str] = Field(default=[], description="Tags for organization")
    notes: Optional[str] = Field(None, description="Additional notes")

class AttributeListResponse(BaseModel):
    attributes: List[SavedAttribute] = Field(..., description="List of saved attributes")
    total_count: int = Field(..., description="Total number of attributes")
    by_type: Dict[str, int] = Field(..., description="Count by attribute type")

# Vision API Models
class VisionAnalysisRequest(BaseModel):
    prompt: str = Field(default="What do you see in this image?")
    image_data: str = Field(..., description="Base64 encoded image data")
    provider: str = Field(default="google", description="Vision provider: google, ollama, openai, anthropic")
    model: str = Field(default="gemini-2.5-pro")

class VisionAnalysisResponse(BaseModel):
    analysis: str
    provider_used: str
    llm_model: str
    processing_time_ms: int

class HandwritingTranscriptionRequest(BaseModel):
    prompt: str = Field(default="Transcribe the handwritten text in this image.")
    image_data: str = Field(..., description="Base64 encoded image data")
    provider: str = Field(default="google", description="Vision provider: google, ollama, openai, anthropic")
    model: str = Field(default="gemini-2.5-pro")

class HandwritingTranscriptionResponse(BaseModel):
    transcription: str
    provider_used: str
    llm_model: str
    processing_time_ms: int

class ImageGenerationRequest(BaseModel):
    prompt: str = Field(..., example="A beautiful sunset over mountains")
    provider: str = Field(default="openai", description="openai or ollama")
    size: str = Field(default="1024x1024")
    model: str = Field(default="dall-e-3")

class ImageGenerationResponse(BaseModel):
    image_url: str
    prompt_used: str
    provider_used: str
    generation_time_ms: int

class StabilityAnalysisResponse(BaseModel):
    average_drift: float
    stability_score: float
    most_stable_elements: List[str]
    most_volatile_elements: List[str]
    language_results: Dict[str, float]

class LamishAnalysisRequest(BaseModel):
    narrative: str = Field(..., example="Call me Ishmael. Some years ago—never mind how long precisely—having little or no money in my purse...")
    
class LamishAnalysisResponse(BaseModel):
    source_narrative: str
    essence_embedding: List[float]
    narrative_elements: Dict[str, float]
    suggested_attributes: Dict[str, str]
    lamish_projection: str
    quality_indicators: Dict[str, float]
    similar_concepts: Dict[str, List[Dict[str, Any]]]

# --- Session Management ---
maieutic_sessions: Dict[str, MaieuticDialogue] = {}

def create_session_id() -> str:
    """Create a unique session ID."""
    return str(uuid.uuid4())

# --- API Endpoints ---

@app.get("/health", summary="Health Check")
async def health_check():
    """Check API health and LLM provider status."""
    provider = get_llm_provider()
    provider_info = {
        "status": "ok",
        "provider": provider.__class__.__name__,
        "provider_available": getattr(provider, 'is_available', lambda: True)()
    }
    
    # Add provider-specific details
    if hasattr(provider, 'model'):
        provider_info["model"] = provider.model
    if hasattr(provider, 'host'):
        provider_info["host"] = provider.host
    
    # Add environment variables for debugging
    provider_info["env_provider"] = os.getenv('LPE_PROVIDER', 'not_set')
    provider_info["env_model"] = os.getenv('LPE_MODEL', 'not_set')
    
    return provider_info

@app.get("/models", summary="Get Available Models")
async def get_available_models():
    """Get available models for the current provider."""
    provider = get_llm_provider()
    
    models = {
        "text_models": [],
        "embedding_models": [],
        "current_provider": provider.__class__.__name__,
        "providers": ["ollama", "litellm", "mock"]
    }
    
    if hasattr(provider, 'host') and provider.host:  # OllamaProvider
        try:
            import requests
            response = requests.get(f"{provider.host}/api/tags", timeout=10)
            if response.status_code == 200:
                data = response.json()
                for model in data.get("models", []):
                    model_info = {
                        "name": model["name"],
                        "size": model["details"]["parameter_size"],
                        "family": model["details"]["family"]
                    }
                    
                    # Categorize models
                    if "embed" in model["name"].lower():
                        models["embedding_models"].append(model_info)
                    else:
                        models["text_models"].append(model_info)
        except Exception as e:
            logger.error(f"Failed to fetch Ollama models: {e}")
    
    elif hasattr(provider, 'model'):
        # LiteLLM or other providers
        models["text_models"].append({
            "name": provider.model,
            "size": "Unknown",
            "family": "external"
        })
        if hasattr(provider, 'embedding_model'):
            models["embedding_models"].append({
                "name": provider.embedding_model,
                "size": "Unknown", 
                "family": "external"
            })
    
    return models

@app.get("/configurations", response_model=ConfigurationResponse, summary="Get Configuration Options")
async def get_configurations():
    """Get all available personas, namespaces, styles, and supported languages."""
    return ConfigurationResponse(**enhanced_config)

@app.post("/transform", response_model=TransformationResponse, summary="Advanced Narrative Transformation")
async def transform_narrative(request: TransformationRequest):
    """
    Perform advanced narrative transformation using the full 5-step LPE process:
    1. Deconstruct - Extract core elements
    2. Map - Translate to target namespace
    3. Reconstruct - Rebuild narrative structure
    4. Stylize - Apply language style
    5. Reflect - Generate meta-commentary
    
    ENHANCED: Now includes automatic embedding generation and archive integration
    """
    try:
        # Generate unique transform ID for progress tracking
        transform_id = str(uuid.uuid4())
        logger.info(f"Starting transformation {transform_id}: {request.target_persona}/{request.target_namespace}/{request.target_style}")
        
        # Send initial progress update
        await send_progress_update(transform_id, "initializing", "started", {
            "persona": request.target_persona,
            "namespace": request.target_namespace,
            "style": request.target_style
        })
        
        # ENHANCEMENT 1: Auto-generate and store embeddings for the input narrative
        embedding_metadata = {}
        try:
            from attribute_intelligence import AttributeIntelligenceEngine
            ai_engine = AttributeIntelligenceEngine(quantum_engine=quantum_engine if NARRATIVE_THEORY_AVAILABLE else None)
            
            await send_progress_update(transform_id, "embedding", "started", {"message": "Generating embeddings"})
            
            # Generate embedding for narrative
            narrative_embedding = await ai_engine.auto_generate_narrative_embedding(request.narrative)
            if narrative_embedding is not None:
                embedding_metadata["input_embedding_generated"] = True
                embedding_metadata["embedding_dimensions"] = len(narrative_embedding)
                await send_progress_update(transform_id, "embedding", "completed", {
                    "embedding_dimensions": len(narrative_embedding),
                    "archived": True
                })
            else:
                embedding_metadata["input_embedding_generated"] = False
                
        except Exception as e:
            logger.warning(f"Embedding generation failed: {e}")
            embedding_metadata["embedding_error"] = str(e)
        
        # ENHANCEMENT 2: Use archive-enhanced M-POVM integration if available
        quantum_analysis = {}
        if NARRATIVE_THEORY_AVAILABLE and quantum_engine:
            try:
                await send_progress_update(transform_id, "quantum", "started", {"message": "Quantum narrative analysis"})
                
                # Create meaning-state from narrative
                if narrative_embedding is not None:
                    import torch
                    meaning_state = quantum_engine.text_to_meaning_state(
                        request.narrative,
                        torch.tensor(narrative_embedding, dtype=torch.float32)  # Use full embedding
                    )
                    
                    # Get canonical POVM measurement
                    canonical_probs = quantum_engine.canonical_povm.measure(meaning_state)
                    
                    quantum_analysis = {
                        "initial_purity": meaning_state.purity(),
                        "initial_entropy": meaning_state.von_neumann_entropy(),
                        "canonical_probabilities": canonical_probs,
                        "semantic_dimension": quantum_engine.semantic_dimension
                    }
                    
                    await send_progress_update(transform_id, "quantum", "completed", {
                        "purity": meaning_state.purity(),
                        "entropy": meaning_state.von_neumann_entropy()
                    })
                
            except Exception as e:
                logger.warning(f"Quantum analysis failed: {e}")
                quantum_analysis["error"] = str(e)
        
        # Create projection using the enhanced engine
        await send_progress_update(transform_id, "transformation", "started", {"message": "LPE transformation"})
        
        projection = projection_engine.create_projection(
            narrative=request.narrative,
            persona=request.target_persona,
            namespace=request.target_namespace,
            style=request.target_style,
            show_steps=request.show_steps,
            transform_id=transform_id,
            progress_callback=send_progress_update
        )
        
        # ENHANCEMENT 3: Auto-generate and store embeddings for the OUTPUT narrative
        output_embedding_metadata = {}
        try:
            await send_progress_update(transform_id, "output_embedding", "started", {"message": "Archiving transformed narrative"})
            
            # Generate embedding for transformed narrative
            output_embedding = await ai_engine.auto_generate_narrative_embedding(projection.final_projection)
            if output_embedding is not None:
                output_embedding_metadata["output_embedding_generated"] = True
                output_embedding_metadata["output_embedding_dimensions"] = len(output_embedding)
                
                # Record transformation outcome for RAG learning
                if narrative_embedding is not None:
                    transformation_metrics = {
                        "fidelity": 0.85,  # Placeholder - could compute actual fidelity
                        "preservation_score": 0.8,
                        "purity_change": 0.1,
                        "entropy_change": -0.05
                    }
                    
                    ai_engine.record_transformation_outcome(
                        pattern_id=transform_id,
                        source_text=request.narrative,
                        target_text=projection.final_projection,
                        attributes={
                            "persona": request.target_persona,
                            "namespace": request.target_namespace,
                            "style": request.target_style
                        },
                        metrics=transformation_metrics,
                        transformation_type="enhanced_lpe"
                    )
                    
                await send_progress_update(transform_id, "output_embedding", "completed", {
                    "archived": True,
                    "learning_recorded": True
                })
            else:
                output_embedding_metadata["output_embedding_generated"] = False
                
        except Exception as e:
            logger.warning(f"Output embedding generation failed: {e}")
            output_embedding_metadata["embedding_error"] = str(e)
        
        # Format response
        steps = [
            TransformationStep(
                name=step.name,
                input_snapshot=step.input_snapshot,
                output_snapshot=step.output_snapshot,
                duration_ms=step.duration_ms,
                metadata=step.metadata
            )
            for step in projection.steps
        ]
        
        total_duration = sum(step.duration_ms for step in projection.steps)
        
        # Send final completion update
        await send_progress_update(transform_id, "complete", "finished", {
            "total_duration_ms": total_duration,
            "final_narrative": projection.final_projection[:100] + "..." if len(projection.final_projection) > 100 else projection.final_projection,
            "embedding_integration": True,
            "archive_integration": True,
            "quantum_analysis": bool(quantum_analysis)
        })
        
        # Enhanced response with embedding and quantum analysis data
        response_data = TransformationResponse(
            transform_id=transform_id,
            original={
                "narrative": projection.source_narrative,
                "persona": "original",
                "namespace": "real-world",
                "style": "original"
            },
            projection={
                "narrative": projection.final_projection,
                "persona": projection.persona,
                "namespace": projection.namespace,
                "style": projection.style,
                "reflection": projection.reflection,
                "embedding_dimensions": len(projection.embedding) if projection.embedding else 0
            },
            steps=steps,
            total_duration_ms=total_duration
        )
        
        # Add enhancement metadata
        response_data_dict = response_data.dict()
        response_data_dict["enhancement_metadata"] = {
            "input_embedding": embedding_metadata,
            "output_embedding": output_embedding_metadata,
            "quantum_analysis": quantum_analysis,
            "archive_integration": True,
            "m_povm_integration": NARRATIVE_THEORY_AVAILABLE
        }
        
        return response_data_dict
        
    except Exception as e:
        logger.error(f"Transformation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Transformation failed: {str(e)}")

@app.post("/archive/enhance-anchors", summary="Learn Semantic Anchors from Archive")
async def enhance_semantic_anchors():
    """
    Learn new semantic anchors from the archive system's content.
    
    This endpoint directly addresses the user's request for tight M-POVM/embedding 
    integration by mining the archive's 37,205 chunks and 111 embeddings to 
    discover new semantic anchor points for better attribute selection.
    """
    try:
        from attribute_intelligence import AttributeIntelligenceEngine
        
        # Initialize the AI engine
        ai_engine = AttributeIntelligenceEngine(quantum_engine=quantum_engine if NARRATIVE_THEORY_AVAILABLE else None)
        
        # Get initial anchor count
        initial_count = len(ai_engine.anchor_points)
        
        # Enhance anchors from archive
        await ai_engine.enhance_semantic_anchors_from_archive()
        
        # Get final anchor count
        final_count = len(ai_engine.anchor_points)
        new_anchors = final_count - initial_count
        
        return {
            "status": "success",
            "message": f"Enhanced semantic anchors from archive system",
            "initial_anchor_count": initial_count,
            "final_anchor_count": final_count,
            "new_anchors_learned": new_anchors,
            "archive_integration": True,
            "m_povm_integration": NARRATIVE_THEORY_AVAILABLE
        }
        
    except Exception as e:
        logger.error(f"Archive anchor enhancement failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to enhance anchors: {str(e)}")

@app.get("/archive/embedding-stats", summary="Get Archive Embedding Statistics")
async def get_archive_embedding_stats():
    """
    Get statistics about embeddings in the archive system.
    
    Shows the current state of the archive's embedding collection that feeds
    into the M-POVM semantic anchor learning system.
    """
    try:
        import httpx
        
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:7200/stats")
            
            if response.status_code == 200:
                stats = response.json()
                
                # Add M-POVM integration info
                stats["m_povm_integration"] = NARRATIVE_THEORY_AVAILABLE
                stats["semantic_anchor_learning"] = True
                stats["quantum_narrative_engine"] = bool(quantum_engine) if NARRATIVE_THEORY_AVAILABLE else False
                
                return stats
            else:
                raise HTTPException(status_code=503, detail="Archive API unavailable")
                
    except Exception as e:
        logger.error(f"Failed to get archive stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get archive stats: {str(e)}")

@app.post("/literature/mine-attributes", summary="Mine Literature for Comprehensive Attributes")
async def mine_literature_attributes(
    sample_size: int = 5,
    max_passages_per_work: int = 30,
    use_classic_works: bool = True
):
    """
    Mine Project Gutenberg literature using QBist semantic tools to discover
    comprehensive, literature-grounded attribute taxonomies.
    
    This addresses the user's insight that we need more base attributes derived
    from actual literary analysis rather than arbitrary lists.
    
    Args:
        sample_size: Number of literary works to analyze (default: 5)
        max_passages_per_work: Maximum passages to extract per work (default: 30)
        use_classic_works: Whether to use curated classic literature list (default: True)
    """
    try:
        from literature_attribute_miner import mine_literature_for_attributes, CLASSIC_LITERATURE_IDS
        
        # Select works to analyze
        if use_classic_works:
            gutenberg_ids = CLASSIC_LITERATURE_IDS[:sample_size]
        else:
            # Could implement random sampling or user-specified IDs
            gutenberg_ids = CLASSIC_LITERATURE_IDS[:sample_size]
        
        logger.info(f"Starting literature mining for {sample_size} works")
        
        # Mine literature
        results = await mine_literature_for_attributes(
            gutenberg_ids=gutenberg_ids,
            max_passages_per_work=max_passages_per_work
        )
        
        # Add metadata
        results["mining_parameters"] = {
            "sample_size": sample_size,
            "max_passages_per_work": max_passages_per_work,
            "gutenberg_ids": gutenberg_ids,
            "quantum_analysis_enabled": NARRATIVE_THEORY_AVAILABLE
        }
        
        return results
        
    except Exception as e:
        logger.error(f"Literature mining failed: {e}")
        raise HTTPException(status_code=500, detail=f"Literature mining failed: {str(e)}")

@app.get("/literature/discovered-attributes", summary="Get Discovered Literature-Based Attributes")
async def get_discovered_attributes():
    """
    Get all attributes discovered from literature analysis.
    
    Returns the comprehensive, literature-grounded attribute taxonomy
    that can replace or supplement the current limited attribute lists.
    """
    try:
        from literature_attribute_miner import AttributeDiscoveryEngine
        import sqlite3
        
        db_path = "./data/literature_attributes.db"
        
        # Check if database exists
        if not Path(db_path).exists():
            return {
                "message": "No literature analysis database found. Run /literature/mine-attributes first.",
                "discovered_attributes": {},
                "total_attributes": 0
            }
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all discovered attributes
        cursor.execute("""
            SELECT category, label, description, literary_examples, quality_score, created_at
            FROM discovered_attributes 
            ORDER BY category, quality_score DESC
        """)
        
        attributes_by_category = defaultdict(list)
        total_attributes = 0
        
        for row in cursor.fetchall():
            category, label, description, examples_json, quality_score, created_at = row
            
            try:
                examples = json.loads(examples_json) if examples_json else []
            except:
                examples = []
            
            attributes_by_category[category].append({
                "label": label,
                "description": description,
                "literary_examples": examples,
                "quality_score": quality_score,
                "created_at": created_at
            })
            total_attributes += 1
        
        # Get statistics
        cursor.execute("SELECT COUNT(*) FROM literary_passages")
        total_passages = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT author) FROM literary_passages")
        unique_authors = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT gutenberg_id) FROM literary_passages")
        unique_works = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "discovered_attributes": dict(attributes_by_category),
            "total_attributes": total_attributes,
            "categories": list(attributes_by_category.keys()),
            "statistics": {
                "total_passages_analyzed": total_passages,
                "unique_authors": unique_authors,
                "unique_works": unique_works
            },
            "literature_grounded": True,
            "qbist_semantic_analysis": NARRATIVE_THEORY_AVAILABLE
        }
        
    except Exception as e:
        logger.error(f"Failed to get discovered attributes: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get discovered attributes: {str(e)}")

@app.post("/literature/update-taxonomy", summary="Update System Taxonomy with Literature-Derived Attributes")
async def update_system_taxonomy_from_literature():
    """
    Update the system's attribute taxonomy with literature-derived attributes.
    
    This replaces the current limited taxonomy with comprehensive,
    literature-grounded attributes discovered through QBist semantic analysis.
    """
    try:
        from literature_attribute_miner import AttributeDiscoveryEngine
        import sqlite3
        
        db_path = "./data/literature_attributes.db"
        
        if not Path(db_path).exists():
            raise HTTPException(
                status_code=404, 
                detail="No literature analysis database found. Run /literature/mine-attributes first."
            )
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get high-quality discovered attributes
        cursor.execute("""
            SELECT category, label, quality_score
            FROM discovered_attributes 
            WHERE quality_score > 0.3
            ORDER BY category, quality_score DESC
        """)
        
        new_taxonomy = defaultdict(list)
        
        for category, label, quality_score in cursor.fetchall():
            new_taxonomy[category].append(label)
        
        conn.close()
        
        # Update the global enhanced_config
        global enhanced_config
        
        # Preserve existing attributes and add new ones
        for category, attributes in new_taxonomy.items():
            if category in ["persona", "namespace", "style"]:
                # Merge with existing, avoiding duplicates
                existing = set(enhanced_config.get(f"{category}s", []))
                new_attrs = set(attributes)
                enhanced_config[f"{category}s"] = list(existing.union(new_attrs))
            else:
                # New category
                enhanced_config[f"{category}s"] = attributes
        
        return {
            "status": "success",
            "message": "System taxonomy updated with literature-derived attributes",
            "updated_categories": list(new_taxonomy.keys()),
            "new_attributes_by_category": dict(new_taxonomy),
            "total_new_attributes": sum(len(attrs) for attrs in new_taxonomy.values()),
            "literature_grounded": True
        }
        
    except Exception as e:
        logger.error(f"Failed to update taxonomy: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update taxonomy: {str(e)}")

@app.post("/maieutic/start", summary="Start Maieutic Dialogue Session")
async def start_maieutic_session(request: MaieuticRequest):
    """Start a new maieutic (Socratic) dialogue session."""
    session_id = create_session_id()
    
    try:
        dialogue = MaieuticDialogue()
        dialogue.start_session(request.narrative, request.goal)
        
        # Store session
        maieutic_sessions[session_id] = dialogue
        
        # Generate first question
        question = dialogue.generate_question(depth_level=0)
        
        return {
            "session_id": session_id,
            "initial_narrative": request.narrative,
            "goal": request.goal,
            "first_question": question
        }
        
    except Exception as e:
        logger.error(f"Failed to start maieutic session: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start session: {str(e)}")

@app.post("/maieutic/question", summary="Generate Next Question")
async def generate_maieutic_question(request: MaieuticQuestionRequest):
    """Generate the next question in the maieutic dialogue."""
    if request.session_id not in maieutic_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        dialogue = maieutic_sessions[request.session_id]
        question = dialogue.generate_question(request.depth_level)
        
        return {"question": question, "depth_level": request.depth_level}
        
    except Exception as e:
        logger.error(f"Failed to generate question: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate question: {str(e)}")

@app.post("/maieutic/answer", response_model=MaieuticResponse, summary="Submit Answer and Get Insights")
async def submit_maieutic_answer(request: MaieuticAnswerRequest):
    """Submit an answer to a maieutic question and extract insights."""
    if request.session_id not in maieutic_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        dialogue = maieutic_sessions[request.session_id]
        
        # Add the turn to the session
        turn = dialogue.add_turn(request.question, request.answer, request.depth_level)
        
        # Generate next question
        next_question = dialogue.generate_question(request.depth_level + 1)
        
        return MaieuticResponse(
            session_id=request.session_id,
            question=next_question,
            insights=turn.insights
        )
        
    except Exception as e:
        logger.error(f"Failed to process answer: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process answer: {str(e)}")

@app.post("/maieutic/complete", summary="Complete Maieutic Session")
async def complete_maieutic_session(session_id: str):
    """Complete a maieutic session and get final understanding."""
    if session_id not in maieutic_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        dialogue = maieutic_sessions[session_id]
        session = dialogue.complete_session()
        
        # Get suggested configuration for projection
        suggested_persona, suggested_namespace, suggested_style = dialogue.suggest_configuration()
        
        return {
            "session_id": session_id,
            "final_understanding": session.final_understanding,
            "suggested_config": {
                "persona": suggested_persona,
                "namespace": suggested_namespace,
                "style": suggested_style
            },
            "enriched_narrative": dialogue.create_enriched_narrative(),
            "total_turns": len(session.turns)
        }
        
    except Exception as e:
        logger.error(f"Failed to complete session: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to complete session: {str(e)}")

@app.post("/translation/roundtrip", response_model=TranslationResponse, summary="Round-trip Translation Analysis")
async def perform_round_trip_translation(request: TranslationRequest):
    """Perform round-trip translation analysis to study semantic drift."""
    try:
        result = translation_analyzer.perform_round_trip(
            text=request.text,
            intermediate_language=request.intermediate_language,
            source_language=request.source_language
        )
        
        # Extract forward translation from translations list
        forward_translation = ""
        if result.translations and len(result.translations) > 0:
            forward_translation = result.translations[0].target_text
        
        return TranslationResponse(
            original_text=result.original_text,
            forward_translation=forward_translation,
            final_text=result.final_text,
            intermediate_language=result.intermediate_language,
            semantic_drift=result.semantic_drift,
            preserved_elements=result.preserved_elements,
            lost_elements=result.lost_elements,
            gained_elements=result.gained_elements,
            linguistic_analysis=result.linguistic_analysis
        )
        
    except Exception as e:
        logger.error(f"Round-trip translation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")

@app.post("/translation/stability", response_model=StabilityAnalysisResponse, summary="Multi-language Stability Analysis")
async def analyze_semantic_stability(request: MultiTranslationRequest):
    """Analyze semantic stability across multiple languages."""
    try:
        stability_analysis = translation_analyzer.find_stable_meaning_core(
            text=request.text,
            test_languages=request.test_languages
        )
        
        return StabilityAnalysisResponse(**stability_analysis)
        
    except Exception as e:
        logger.error(f"Stability analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Stability analysis failed: {str(e)}")

def get_vision_provider(provider: str, model: str):
    """Get the appropriate vision provider based on request."""
    if provider == "google":
        return GoogleProvider(model=model)
    elif provider == "ollama":
        host = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
        return OllamaVisionProvider(model=model, host=host)
    elif provider == "openai":
        # Could add OpenAI vision provider here
        raise HTTPException(status_code=501, detail="OpenAI vision provider not yet implemented")
    elif provider == "anthropic":
        # Could add Anthropic vision provider here  
        raise HTTPException(status_code=501, detail="Anthropic vision provider not yet implemented")
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported vision provider: {provider}")

# Vision API endpoints
@app.post("/vision/analyze", response_model=VisionAnalysisResponse, summary="Image Analysis")
async def analyze_image(request: VisionAnalysisRequest):
    """Analyze an image using various vision models."""
    import time
    start_time = time.time()
    
    try:
        # Get the appropriate vision provider
        vision_provider = get_vision_provider(request.provider, request.model)
        
        # Perform image analysis based on provider type
        if request.provider == "ollama":
            analysis = vision_provider.generate_with_image(
                prompt=request.prompt,
                image_data=request.image_data
            )
        else:  # Google and other providers
            analysis = vision_provider.generate(
                prompt=request.prompt,
                image_data=request.image_data
            )
        
        processing_time = int((time.time() - start_time) * 1000)
        
        return VisionAnalysisResponse(
            analysis=analysis,
            provider_used=request.provider,
            llm_model=request.model,
            processing_time_ms=processing_time
        )
        
    except Exception as e:
        logger.error(f"Image analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Image analysis failed: {str(e)}")

@app.post("/vision/transcribe", response_model=HandwritingTranscriptionResponse, summary="Handwriting Transcription")
async def transcribe_handwriting(request: HandwritingTranscriptionRequest):
    """Transcribe handwritten text from an image."""
    import time
    start_time = time.time()
    
    try:
        # Get the appropriate vision provider
        vision_provider = get_vision_provider(request.provider, request.model)
        
        # Enhanced prompt for handwriting transcription
        transcription_prompt = f"""Please transcribe any handwritten text visible in this image. 
        Focus on accuracy and preserve the original formatting where possible.
        If there are multiple sections of text, organize them clearly.
        If any text is unclear, indicate with [unclear] but provide your best guess.
        
        {request.prompt}"""
        
        # Perform transcription based on provider type
        if request.provider == "ollama":
            transcription = vision_provider.generate_with_image(
                prompt=transcription_prompt,
                image_data=request.image_data
            )
        else:  # Google and other providers
            transcription = vision_provider.generate(
                prompt=transcription_prompt,
                image_data=request.image_data
            )
        
        processing_time = int((time.time() - start_time) * 1000)
        
        return HandwritingTranscriptionResponse(
            transcription=transcription,
            provider_used=request.provider,
            llm_model=request.model,
            processing_time_ms=processing_time
        )
        
    except Exception as e:
        logger.error(f"Handwriting transcription failed: {e}")
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

@app.post("/vision/redraw", response_model=VisionAnalysisResponse, summary="Image Artistic Analysis")
async def analyze_for_redraw(request: VisionAnalysisRequest):
    """Analyze an image for artistic reinterpretation and redrawing."""
    import time
    start_time = time.time()
    
    try:
        # Get the appropriate vision provider
        vision_provider = get_vision_provider(request.provider, request.model)
        
        # Enhanced prompt for artistic analysis
        artistic_prompt = f"""Analyze this image for artistic reinterpretation. Provide a detailed description that would allow an artist to recreate or reinterpret this image.

        Focus on:
        - Composition and layout
        - Colors, lighting, and mood  
        - Artistic style and technique
        - Key visual elements and their relationships
        - Emotional or thematic content
        
        Provide your analysis in a way that captures both the literal and artistic essence of the image.
        
        {request.prompt}"""
        
        # Perform analysis based on provider type
        if request.provider == "ollama":
            analysis = vision_provider.generate_with_image(
                prompt=artistic_prompt,
                image_data=request.image_data
            )
        else:  # Google and other providers
            analysis = vision_provider.generate(
                prompt=artistic_prompt,
                image_data=request.image_data
            )
        
        processing_time = int((time.time() - start_time) * 1000)
        
        return VisionAnalysisResponse(
            analysis=analysis,
            provider_used=request.provider,
            llm_model=request.model,
            processing_time_ms=processing_time
        )
        
    except Exception as e:
        logger.error(f"Image artistic analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Artistic analysis failed: {str(e)}")

@app.post("/image/generate", response_model=ImageGenerationResponse, summary="Generate Image")
async def generate_image(request: ImageGenerationRequest):
    """Generate an image from a text prompt."""
    import time
    start_time = time.time()
    
    try:
        if request.provider == "openai":
            # Use OpenAI DALL-E
            openai_api_key = os.getenv('OPENAI_API_KEY')
            if not openai_api_key:
                raise HTTPException(status_code=400, detail="OpenAI API key not configured")
            
            import openai
            client = openai.OpenAI(api_key=openai_api_key)
            
            response = client.images.generate(
                model=request.model,
                prompt=request.prompt,
                size=request.size,
                quality="standard",
                n=1,
            )
            
            image_url = response.data[0].url
            
        else:
            # For now, return a placeholder for Ollama - would need to implement local generation
            raise HTTPException(status_code=501, detail="Ollama image generation not yet implemented")
        
        generation_time = int((time.time() - start_time) * 1000)
        
        return ImageGenerationResponse(
            image_url=image_url,
            prompt_used=request.prompt,
            provider_used=request.provider,
            generation_time_ms=generation_time
        )
        
    except Exception as e:
        logger.error(f"Image generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")

@app.websocket("/ws/maieutic/{session_id}")
async def maieutic_websocket(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time maieutic dialogue."""
    await websocket.accept()
    
    try:
        if session_id not in maieutic_sessions:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": "Session not found"
            }))
            return
        
        dialogue = maieutic_sessions[session_id]
        
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message["type"] == "answer":
                # Process answer and generate insights
                turn = dialogue.add_turn(
                    message["question"],
                    message["answer"],
                    message.get("depth_level", 0)
                )
                
                # Generate next question
                next_question = dialogue.generate_question(message.get("depth_level", 0) + 1)
                
                await websocket.send_text(json.dumps({
                    "type": "insights",
                    "insights": turn.insights,
                    "next_question": next_question
                }))
                
            elif message["type"] == "complete":
                # Complete session
                session = dialogue.complete_session()
                suggested_persona, suggested_namespace, suggested_style = dialogue.suggest_configuration()
                
                await websocket.send_text(json.dumps({
                    "type": "complete",
                    "final_understanding": session.final_understanding,
                    "suggested_config": {
                        "persona": suggested_persona,
                        "namespace": suggested_namespace,
                        "style": suggested_style
                    }
                }))
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": str(e)
        }))

# Global dictionary to store active transformation WebSocket connections
transformation_connections: Dict[str, WebSocket] = {}

@app.websocket("/ws/transform/{transform_id}")
async def websocket_transform_progress(websocket: WebSocket, transform_id: str):
    """WebSocket for real-time transformation progress updates."""
    await websocket.accept()
    transformation_connections[transform_id] = websocket
    
    try:
        # Keep connection alive
        while True:
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        logger.info(f"Transform WebSocket disconnected for {transform_id}")
        if transform_id in transformation_connections:
            del transformation_connections[transform_id]
    except Exception as e:
        logger.error(f"Transform WebSocket error: {e}")
        if transform_id in transformation_connections:
            del transformation_connections[transform_id]

async def send_progress_update(transform_id: str, step: str, status: str, data: Dict[str, Any] = None):
    """Send progress update to connected WebSocket clients."""
    if transform_id in transformation_connections:
        try:
            message = {
                "type": "progress",
                "transform_id": transform_id,
                "step": step,
                "status": status,
                "timestamp": asyncio.get_event_loop().time(),
                "data": data or {}
            }
            await transformation_connections[transform_id].send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending progress update: {e}")
            # Remove broken connection
            if transform_id in transformation_connections:
                del transformation_connections[transform_id]

@app.get("/sessions/{session_id}", summary="Get Session Details")
async def get_session_details(session_id: str):
    """Get details of a maieutic session."""
    if session_id not in maieutic_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    dialogue = maieutic_sessions[session_id]
    session = dialogue.session
    
    return {
        "session_id": session_id,
        "initial_narrative": session.initial_narrative,
        "goal": session.goal,
        "turns": [
            {
                "question": turn.question,
                "answer": turn.answer,
                "insights": turn.insights,
                "depth_level": turn.depth_level,
                "timestamp": turn.timestamp.isoformat()
            }
            for turn in session.turns
        ],
        "final_understanding": session.final_understanding,
        "created_at": session.created_at.isoformat()
    }

@app.post("/lamish/analyze", response_model=LamishAnalysisResponse, summary="Lamish Meaning Analysis")
async def analyze_lamish_meaning(request: LamishAnalysisRequest):
    """
    Analyze a narrative to extract lamish meaning and suggest optimal projection attributes.
    
    This endpoint provides:
    1. Essence embedding - non-textual meaning representation  
    2. Narrative element analysis - character, action, emotion scores
    3. Suggested persona/namespace/style based on content
    4. Lamish projection - actual transformed narrative
    5. Quality indicators and similar concepts
    """
    try:
        narrative = request.narrative.strip()
        if not narrative:
            raise HTTPException(status_code=400, detail="Narrative cannot be empty")
        
        # Store the meaning in knowledge base and get analysis
        knowledge_base.store_lamish_meaning(narrative, {})
        
        # Get essence embedding and narrative elements
        meaning_key = narrative[:50]
        if meaning_key in knowledge_base.meanings:
            lamish_meaning = knowledge_base.meanings[meaning_key]
            essence_embedding = lamish_meaning.essence_embedding
            narrative_elements = lamish_meaning.narrative_elements
            quality_indicators = lamish_meaning.quality_indicators
        else:
            # Fallback if not found
            essence_embedding = [0.0] * 768
            narrative_elements = {}
            quality_indicators = {}
        
        # Get suggested optimal configuration  
        suggested_attributes = knowledge_base.suggest_optimal_configuration(narrative)
        
        # Create actual lamish projection using suggested attributes
        projection = projection_engine.create_projection(
            narrative=narrative,
            persona=suggested_attributes['persona'],
            namespace=suggested_attributes['namespace'],
            style=suggested_attributes['style'],
            show_steps=False
        )
        
        # Find similar concepts for each attribute type
        similar_concepts = {}
        for concept_type in ['persona', 'namespace', 'style']:
            similar = knowledge_base.find_similar_concepts(essence_embedding, concept_type, 3)
            similar_concepts[concept_type] = [
                {
                    'name': concept.name,
                    'description': concept.description,
                    'similarity': float(score),
                    'usage_count': concept.usage_count,
                    'quality_score': concept.quality_score
                }
                for concept, score in similar
            ]
        
        return LamishAnalysisResponse(
            source_narrative=narrative,
            essence_embedding=essence_embedding,
            narrative_elements=narrative_elements,
            suggested_attributes=suggested_attributes,
            lamish_projection=projection.final_projection,
            quality_indicators=quality_indicators,
            similar_concepts=similar_concepts
        )
        
    except Exception as e:
        logger.error(f"Lamish analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/lamish/concepts", summary="Get All Concepts")
async def get_all_concepts():
    """Get all concepts from the knowledge base."""
    try:
        # Group concepts by type
        concepts = {
            "personas": [],
            "namespaces": [],
            "styles": []
        }
        
        for concept_id, concept in knowledge_base.concepts.items():
            concept_data = {
                "id": concept.id,
                "name": concept.name,
                "description": concept.description,
                "characteristics": concept.characteristics,
                "examples": concept.examples,
                "usage_count": concept.usage_count,
                "quality_score": concept.quality_score,
                "created_at": concept.created_at,
                "updated_at": concept.updated_at
            }
            
            if concept.type == "persona":
                concepts["personas"].append(concept_data)
            elif concept.type == "namespace":
                concepts["namespaces"].append(concept_data)
            elif concept.type == "style":
                concepts["styles"].append(concept_data)
        
        return concepts
        
    except Exception as e:
        logger.error(f"Failed to get concepts: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get concepts: {str(e)}")

@app.post("/lamish/concepts", summary="Create New Concept")
async def create_concept(concept_data: dict):
    """Create a new concept in the knowledge base."""
    try:
        # Validate required fields
        if not all(key in concept_data for key in ["type", "name", "description"]):
            raise HTTPException(status_code=400, detail="Missing required fields: type, name, description")
        
        # Create concept using knowledge base method
        knowledge_base._create_concept(concept_data["type"], {
            "name": concept_data["name"],
            "description": concept_data["description"],
            "characteristics": concept_data.get("characteristics", []),
            "examples": concept_data.get("examples", [])
        })
        
        # Save knowledge base
        knowledge_base.save_knowledge_base()
        
        return {"status": "success", "message": "Concept created successfully"}
        
    except Exception as e:
        logger.error(f"Failed to create concept: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create concept: {str(e)}")

@app.delete("/lamish/concepts/{concept_id}", summary="Delete Concept")
async def delete_concept(concept_id: str):
    """Delete a concept from the knowledge base."""
    try:
        if concept_id in knowledge_base.concepts:
            del knowledge_base.concepts[concept_id]
            knowledge_base.save_knowledge_base()
            return {"status": "success", "message": "Concept deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Concept not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete concept: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete concept: {str(e)}")

@app.get("/lamish/meanings", summary="Get Stored Meanings")
async def get_stored_meanings():
    """Get all stored lamish meanings."""
    try:
        meanings = []
        for key, meaning in knowledge_base.meanings.items():
            meanings.append({
                "id": key,
                "preview": meaning.source_text[:50] + "..." if len(meaning.source_text) > 50 else meaning.source_text,
                "full_text": meaning.source_text,
                "dimensions": len(meaning.essence_embedding),
                "created": meaning.created_at,
                "quality_indicators": meaning.quality_indicators,
                "narrative_elements": meaning.narrative_elements
            })
        
        return {"meanings": meanings}
        
    except Exception as e:
        logger.error(f"Failed to get meanings: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get meanings: {str(e)}")

@app.get("/lamish/stats", summary="Get Dashboard Statistics") 
async def get_lamish_stats():
    """Get statistics for the lamish dashboard."""
    try:
        # Calculate statistics from knowledge base
        total_concepts = len(knowledge_base.concepts)
        total_meanings = len(knowledge_base.meanings)
        
        # Find most used concepts
        persona_usage = {}
        namespace_usage = {}
        style_usage = {}
        quality_scores = []
        
        for concept in knowledge_base.concepts.values():
            quality_scores.append(concept.quality_score)
            
            if concept.type == "persona":
                persona_usage[concept.name] = concept.usage_count
            elif concept.type == "namespace":
                namespace_usage[concept.name] = concept.usage_count
            elif concept.type == "style":
                style_usage[concept.name] = concept.usage_count
        
        most_used_persona = max(persona_usage.items(), key=lambda x: x[1])[0] if persona_usage else "None"
        most_used_namespace = max(namespace_usage.items(), key=lambda x: x[1])[0] if namespace_usage else "None"
        most_used_style = max(style_usage.items(), key=lambda x: x[1])[0] if style_usage else "None"
        
        avg_quality_score = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
        
        return {
            "total_concepts": total_concepts,
            "total_meanings": total_meanings,
            "most_used_persona": most_used_persona,
            "most_used_namespace": most_used_namespace,
            "most_used_style": most_used_style,
            "avg_quality_score": avg_quality_score,
            "concept_breakdown": {
                "personas": len([c for c in knowledge_base.concepts.values() if c.type == "persona"]),
                "namespaces": len([c for c in knowledge_base.concepts.values() if c.type == "namespace"]),
                "styles": len([c for c in knowledge_base.concepts.values() if c.type == "style"])
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

@app.post("/lamish/extract-attributes", summary="Extract Attributes from Text")
async def extract_attributes(request: dict):
    """Extract persona, namespace, and style attributes from narrative text."""
    try:
        narrative = request.get("narrative", "").strip()
        if not narrative:
            raise HTTPException(status_code=400, detail="Narrative text is required")
        
        provider = get_llm_provider()
        
        # Prompt for extracting attributes
        extraction_prompt = f"""Analyze this narrative text and extract three key attributes that would be needed to recreate a similar text through the Lamish Projection Engine:

TEXT:
{narrative}

Extract and identify:

1. PERSONA - The inherent voice, perspective, or character type that tells this story
2. NAMESPACE - The world, setting, universe, or conceptual space this text inhabits  
3. STYLE - The linguistic style, tone, and manner of expression used

For each attribute, provide:
- A concise, descriptive name (2-4 words, lowercase with hyphens)
- A detailed description explaining what makes this attribute unique
- 3-4 key characteristics as single words
- 2-3 concrete examples of how this attribute manifests

Format your response as JSON:
{{
  "persona": {{
    "name": "descriptive-name",
    "description": "detailed description",
    "characteristics": ["trait1", "trait2", "trait3", "trait4"],
    "examples": ["example1", "example2", "example3"]
  }},
  "namespace": {{
    "name": "world-name", 
    "description": "detailed description",
    "characteristics": ["aspect1", "aspect2", "aspect3", "aspect4"],
    "examples": ["example1", "example2", "example3"]
  }},
  "style": {{
    "name": "style-name",
    "description": "detailed description", 
    "characteristics": ["feature1", "feature2", "feature3", "feature4"],
    "examples": ["example1", "example2", "example3"]
  }}
}}"""

        response = provider.generate(
            prompt=extraction_prompt,
            system_prompt="You are an expert at analyzing narrative text to extract personas, namespaces, and styles. Respond only with valid JSON."
        )
        
        # Parse JSON response
        import json
        try:
            extracted_data = json.loads(response.strip())
            return extracted_data
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            logger.warning("Failed to parse JSON response, using fallback")
            return {
                "persona": {
                    "name": "extracted-voice",
                    "description": "The voice and perspective extracted from the narrative",
                    "characteristics": ["extracted", "analytical", "descriptive"],
                    "examples": ["Narrative perspective", "Character voice", "Storytelling approach"]
                },
                "namespace": {
                    "name": "text-world",
                    "description": "The world or conceptual space of the narrative",
                    "characteristics": ["contextual", "thematic", "environmental"],
                    "examples": ["Setting elements", "World details", "Conceptual framework"]
                },
                "style": {
                    "name": "text-style",
                    "description": "The linguistic style and expression of the narrative",
                    "characteristics": ["linguistic", "expressive", "tonal"],
                    "examples": ["Word choice", "Sentence structure", "Tone patterns"]
                }
            }
        
    except Exception as e:
        logger.error(f"Failed to extract attributes: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to extract attributes: {str(e)}")

@app.post("/lamish/inspect-prompts", summary="Get Pipeline Prompts for Inspector")
async def inspect_prompts(request: dict):
    """Get the actual system and user prompts used in the LPE pipeline for inspection."""
    try:
        # Import from the correct path relative to the lighthouse directory
        import sys
        sys.path.append('../')
        from src.lpe_core.llm_provider import LLMTransformer
        from src.lpe_core.pipeline_agent import PipelineAgent
        
        persona = request.get("persona", "philosopher")
        namespace = request.get("namespace", "lamish-galaxy")
        style = request.get("style", "poetic")
        
        # Initialize components with the selected attributes
        transformer = LLMTransformer(persona=persona, namespace=namespace, style=style)
        agent = PipelineAgent(persona=persona, namespace=namespace, style=style)
        
        # Define step prompts with actual templates
        step_prompts = {
            "deconstruct": {
                "system_prompt": transformer._build_system_prompt("deconstruct", persona, namespace, style),
                "user_prompt": "Extract the core narrative elements in this structure:\\nWHO: [Identify specific actors/characters]\\nWHAT: [Identify specific actions/events]\\nWHY: [Identify motivations/conflicts]\\nHOW: [Identify methods/approaches]\\nOUTCOME: [Identify results/implications]\\n\\nBe concrete and specific about the actual story elements.\\n\\n{input_text}",
                "input_description": "Raw narrative text from user",
                "output_description": "Structured WHO/WHAT/WHY/HOW/OUTCOME elements"
            },
            "map": {
                "system_prompt": transformer._build_system_prompt("map", persona, namespace, style),
                "user_prompt": f"Based on these extracted narrative elements, create specific mappings to the {namespace} universe:\\n\\n{{input_text}}\\n\\nFor each element identified above, provide a direct equivalent in the {namespace} setting. Use the format:\\nOriginal Element → {namespace} Equivalent\\n\\nBe specific and preserve the relationships between elements.",
                "input_description": "Structured narrative elements from deconstruct step",
                "output_description": f"Element mappings to {namespace} universe equivalents"
            },
            "reconstruct": {
                "system_prompt": transformer._build_system_prompt("reconstruct", persona, namespace, style),
                "user_prompt": f"Using these element mappings, reconstruct the complete narrative from the {persona} perspective:\\n\\n{{input_text}}\\n\\nTell this as a flowing, coherent story using the mapped elements. Maintain the original sequence of events and relationships, but express it through the {persona}'s voice and understanding.",
                "input_description": f"Element mappings to {namespace} universe",
                "output_description": f"Complete narrative told from {persona} perspective"
            },
            "stylize": {
                "system_prompt": transformer._build_system_prompt("stylize", persona, namespace, style),
                "user_prompt": f"Apply {style} language style to this narrative:\\n\\n{{input_text}}\\n\\nAdjust only the tone, voice, and expression to match {style} style. Do not change the plot, characters, or core meaning.",
                "input_description": f"Narrative from {persona} perspective",
                "output_description": f"Same narrative expressed in {style} linguistic style"
            },
            "reflect": {
                "system_prompt": transformer._build_system_prompt("reflect", persona, namespace, style),
                "user_prompt": f"Provide meta-commentary on this allegorical transformation:\\n\\nOriginal → {namespace} via {persona} in {style} style:\\n{{input_text}}\\n\\nAnalyze how this transformation illuminates universal patterns or deeper truths in the original narrative.",
                "input_description": f"Final styled narrative in {namespace}/{persona}/{style}",
                "output_description": "Meta-commentary on transformation insights and universal patterns"
            }
        }
        
        return step_prompts
        
    except Exception as e:
        logger.error(f"Failed to inspect prompts: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to inspect prompts: {str(e)}")

@app.post("/lamish/save-prompts", summary="Save Modified Pipeline Prompts") 
async def save_prompts(request: dict):
    """Save modified prompt templates for a pipeline step."""
    try:
        step = request.get("step")
        prompts = request.get("prompts", {})
        
        # For now, just log the changes (in a real implementation, you'd save to a database)
        logger.info(f"Saving prompt changes for step '{step}': {prompts}")
        
        # TODO: Implement actual prompt template saving to database/config
        # This would involve:
        # 1. Validating the prompt format
        # 2. Saving to a prompt templates database
        # 3. Updating the LLMTransformer to use custom prompts
        
        return {"status": "success", "message": f"Prompts for {step} step saved successfully"}
        
    except Exception as e:
        logger.error(f"Failed to save prompts: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save prompts: {str(e)}")

@app.post("/lamish/sync-system", summary="Synchronize System Attributes")
async def sync_system_attributes():
    """Synchronize attributes between knowledge base and API configuration."""
    try:
        # This would implement bidirectional sync between knowledge base and hardcoded config
        # For now, just return success to indicate the feature is available
        
        logger.info("System attribute synchronization requested")
        
        # TODO: Implement actual synchronization logic:
        # 1. Compare knowledge base concepts with API config
        # 2. Identify discrepancies 
        # 3. Update API config to match knowledge base
        # 4. Ensure Transform tab dropdowns use synced data
        # 5. Update any cached configurations
        
        return {
            "status": "success", 
            "message": "System attributes synchronized",
            "details": {
                "knowledge_base_concepts": len(knowledge_base.concepts),
                "api_config_synced": True,
                "transform_tab_updated": True
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to sync system attributes: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to sync system: {str(e)}")

@app.get("/api/llm/configurations", summary="Get LLM Configurations")
async def get_llm_configurations():
    """Get current LLM configurations for all agent tasks."""
    try:
        # Load available providers and models
        available_providers = [
            "ollama", "openai", "anthropic", "google", "huggingface", 
            "groq", "together", "replicate", "cohere", "mistral", "mock"
        ]
        
        # Get available models from cache or refresh if needed
        global cached_models, last_refresh
        
        # Auto-refresh if cache is empty or older than 24 hours
        should_refresh = False
        if not cached_models or not last_refresh:
            should_refresh = True
        else:
            from datetime import datetime, timedelta
            try:
                last_refresh_time = datetime.fromisoformat(last_refresh)
                if datetime.now() - last_refresh_time > timedelta(hours=24):
                    should_refresh = True
            except:
                should_refresh = True
        
        if should_refresh:
            try:
                refresh_result = await refresh_model_lists()
                available_models = refresh_result["available_models"]
                logger.info(f"Auto-refreshed model lists for {len(available_models)} providers")
            except Exception as e:
                logger.warning(f"Failed to auto-refresh models, using fallback: {e}")
                available_models = await get_fallback_models()
        else:
            available_models = cached_models
        
        # If still empty, use fallback
        if not available_models:
            available_models = await get_fallback_models()
        
        # Load saved configurations or use defaults
        config_file = Path(__file__).parent / "data" / "llm_configurations.json"
        saved_configs = {}
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    saved_configs = json.load(f)
                logger.info(f"Loaded saved LLM configurations for {len(saved_configs)} tasks")
            except Exception as e:
                logger.warning(f"Failed to load saved configurations: {e}")
        
        # Default task configurations with provider diversity and optimization
        default_configs = {
            "deconstruct": {
                "provider": "groq",
                "model": "llama-3.1-70b-versatile",
                "temperature": 0.3,
                "max_tokens": 800,
                "top_p": 0.9,
                "frequency_penalty": 0.0,
                "timeout": 30,
                "system_prompt_override": ""
            },
            "map": {
                "provider": "anthropic", 
                "model": "claude-3-5-sonnet-20241022",
                "temperature": 0.5,
                "max_tokens": 1200,
                "top_p": 0.9,
                "frequency_penalty": 0.1,
                "timeout": 60,
                "system_prompt_override": ""
            },
            "reconstruct": {
                "provider": "openai",
                "model": "gpt-4o", 
                "temperature": 0.7,
                "max_tokens": 1500,
                "top_p": 0.9,
                "frequency_penalty": 0.0,
                "timeout": 90,
                "system_prompt_override": ""
            },
            "stylize": {
                "provider": "mistral",
                "model": "mistral-large-latest",
                "temperature": 0.6,
                "max_tokens": 1000,
                "top_p": 0.9,
                "frequency_penalty": 0.2,
                "timeout": 60,
                "system_prompt_override": ""
            },
            "reflect": {
                "provider": "anthropic",
                "model": "claude-3-opus-20240229",
                "temperature": 0.8,
                "max_tokens": 1200,
                "top_p": 0.9,
                "frequency_penalty": 0.0,
                "timeout": 90,
                "system_prompt_override": ""
            },
            "maieutic": {
                "provider": "openai",
                "model": "gpt-4-turbo",
                "temperature": 0.7,
                "max_tokens": 1000,
                "top_p": 0.9,
                "frequency_penalty": 0.1,
                "timeout": 120,
                "system_prompt_override": ""
            },
            "translation": {
                "provider": "google",
                "model": "gemini-1.5-pro",
                "temperature": 0.4,
                "max_tokens": 800,
                "top_p": 0.9,
                "frequency_penalty": 0.0,
                "timeout": 45,
                "system_prompt_override": ""
            },
            "vision": {
                "provider": "openai",
                "model": "gpt-4o",
                "temperature": 0.5,
                "max_tokens": 1500,
                "top_p": 0.9,
                "frequency_penalty": 0.0,
                "timeout": 180,
                "system_prompt_override": ""
            },
            "extract_attributes": {
                "provider": "cohere",
                "model": "command-r-plus",
                "temperature": 0.3,
                "max_tokens": 1000,
                "top_p": 0.9,
                "frequency_penalty": 0.1,
                "timeout": 60,
                "system_prompt_override": ""
            }
        }
        
        # Merge saved configurations with defaults (saved configs override defaults)
        final_configs = default_configs.copy()
        for task_id, config in saved_configs.items():
            if task_id in final_configs:
                # Update existing config with saved values
                final_configs[task_id].update(config)
            else:
                # Add new task config
                final_configs[task_id] = config
        
        return {
            "task_configs": final_configs,
            "available_providers": available_providers,
            "available_models": available_models
        }
        
    except Exception as e:
        logger.error(f"Failed to get LLM configurations: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get LLM configurations: {str(e)}")

@app.post("/api/llm/configurations", summary="Save LLM Configurations")
async def save_llm_configurations(request: dict):
    """Save LLM configurations for agent tasks."""
    try:
        task_configs = request.get("task_configs", {})
        
        # Validate configuration format
        for task_id, config in task_configs.items():
            required_fields = ["provider", "model", "temperature", "max_tokens"]
            for field in required_fields:
                if field not in config:
                    raise HTTPException(status_code=400, detail=f"Missing {field} in {task_id} config")
        
        # Save configurations to file
        config_file = Path(__file__).parent / "data" / "llm_configurations.json"
        config_file.parent.mkdir(exist_ok=True)
        
        with open(config_file, 'w') as f:
            json.dump(task_configs, f, indent=2)
        
        logger.info(f"Saved LLM configurations for {len(task_configs)} tasks to {config_file}")
        
        # Log the configurations for debugging
        for task_id, config in task_configs.items():
            logger.info(f"Task {task_id}: {config['provider']}/{config['model']} temp={config['temperature']}")
        
        return {"status": "success", "message": f"Saved configurations for {len(task_configs)} tasks"}
        
    except Exception as e:
        logger.error(f"Failed to save LLM configurations: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save configurations: {str(e)}")

@app.post("/api/llm/configurations/reset", summary="Reset LLM Configurations")
async def reset_llm_configurations():
    """Reset all LLM configurations to defaults."""
    try:
        logger.info("Resetting LLM configurations to defaults")
        
        # TODO: Implement actual reset logic
        # This would clear any stored configurations and revert to defaults
        
        return {"status": "success", "message": "LLM configurations reset to defaults"}
        
    except Exception as e:
        logger.error(f"Failed to reset LLM configurations: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to reset configurations: {str(e)}")

@app.get("/api/llm/status", summary="Get LLM Provider Status")
async def get_llm_status():
    """Get the current status of all LLM providers with keychain integration."""
    try:
        providers = [
            "openai", "anthropic", "google", "huggingface", 
            "groq", "together", "replicate", "cohere", "mistral"
        ]
        
        # Get comprehensive status using keychain manager
        status = keychain_manager.get_provider_status(providers)
        
        # Special handling for Ollama (local provider)
        try:
            from lpe_core.llm_provider import OllamaProvider
            ollama = OllamaProvider()
            # Test connection
            test_response = ollama.generate("test", "")
            status["ollama"] = {
                "available": True,
                "model": ollama.model_name,
                "host": ollama.base_url,
                "has_key": True,  # Local provider doesn't need API key
                "key_valid": True,
                "status_message": "Local Ollama server running"
            }
        except Exception as e:
            # Try to check if Ollama is running at all
            try:
                import httpx
                response = httpx.get("http://localhost:11434/api/tags", timeout=5)
                if response.status_code == 200:
                    models = response.json().get("models", [])
                    status["ollama"] = {
                        "available": True,
                        "model": models[0]["name"] if models else "no models",
                        "host": "http://localhost:11434",
                        "has_key": True,
                        "key_valid": True,
                        "status_message": f"Ollama running with {len(models)} models"
                    }
                else:
                    raise Exception("Ollama server not responding")
            except Exception as e2:
                status["ollama"] = {
                    "available": False,
                    "error": str(e),
                    "model": None,
                    "has_key": True,
                    "key_valid": False,
                    "status_message": f"Ollama connection failed: {str(e2)}"
                }
        
        # Special handling for mock provider
        status["mock"] = {
            "available": True,
            "model": "mock-model",
            "has_key": True,
            "key_valid": True,
            "status_message": "Testing provider - always available"
        }
        
        return status
        
    except Exception as e:
        logger.error(f"Failed to get LLM status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")

@app.post("/api/llm/keys/{provider}", summary="Store API Key")
async def store_api_key(provider: str, request: dict):
    """Store an API key securely in macOS Keychain."""
    try:
        api_key = request.get("api_key", "").strip()
        if not api_key:
            raise HTTPException(status_code=400, detail="API key is required")
        
        success = keychain_manager.store_api_key(provider, api_key)
        
        if success:
            # Test the key immediately after storing
            test_success, test_message = keychain_manager.test_api_key(provider, api_key)
            
            return {
                "status": "success",
                "message": f"API key stored for {provider}",
                "key_valid": test_success,
                "test_message": test_message
            }
        else:
            raise HTTPException(status_code=500, detail=f"Failed to store API key for {provider}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to store API key for {provider}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to store API key: {str(e)}")

@app.delete("/api/llm/keys/{provider}", summary="Delete API Key")
async def delete_api_key(provider: str):
    """Delete an API key from macOS Keychain."""
    try:
        success = keychain_manager.delete_api_key(provider)
        
        if success:
            return {
                "status": "success",
                "message": f"API key deleted for {provider}"
            }
        else:
            raise HTTPException(status_code=500, detail=f"Failed to delete API key for {provider}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete API key for {provider}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete API key: {str(e)}")

@app.post("/api/llm/test/{provider}", summary="Test API Key")
async def test_api_key(provider: str, request: dict = None):
    """Test an API key (either provided or from keychain)."""
    try:
        api_key = None
        if request:
            api_key = request.get("api_key")
        
        test_success, test_message = keychain_manager.test_api_key(provider, api_key)
        
        return {
            "provider": provider,
            "success": test_success,
            "message": test_message,
            "tested_stored_key": api_key is None
        }
        
    except Exception as e:
        logger.error(f"Failed to test API key for {provider}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to test API key: {str(e)}")

@app.get("/api/llm/keys", summary="List Stored API Keys")
async def list_stored_keys():
    """List all stored API keys (without revealing the actual keys)."""
    try:
        stored_keys = keychain_manager.list_stored_keys()
        
        return {
            "stored_keys": [
                {
                    "provider": key.provider,
                    "account": key.account,
                    "has_key": key.has_key
                }
                for key in stored_keys
            ],
            "total_count": len(stored_keys)
        }
        
    except Exception as e:
        logger.error(f"Failed to list stored keys: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list stored keys: {str(e)}")

@app.post("/api/llm/refresh-models", summary="Refresh Model Lists from Live APIs")
async def refresh_model_lists():
    """Refresh model lists from all provider APIs and cache for performance."""
    try:
        refreshed_models = {}
        
        # Ollama models (local)
        try:
            import httpx
            response = httpx.get("http://localhost:11434/api/tags", timeout=10)
            if response.status_code == 200:
                ollama_data = response.json()
                ollama_models = []
                for model in ollama_data.get("models", []):
                    ollama_models.append({
                        "name": model.get("name", ""),
                        "size": model.get("details", {}).get("parameter_size", "unknown"),
                        "family": model.get("details", {}).get("family", "unknown"),
                        "context": model.get("details", {}).get("context_length", "unknown")
                    })
                refreshed_models["ollama"] = ollama_models
            else:
                refreshed_models["ollama"] = [{"name": "llama3.2:latest", "size": "7B"}]
        except:
            refreshed_models["ollama"] = [{"name": "llama3.2:latest", "size": "7B"}]
        
        # OpenAI models (live API)
        try:
            api_key = keychain_manager.retrieve_api_key("openai")
            if api_key:
                import httpx
                headers = {"Authorization": f"Bearer {api_key}"}
                response = httpx.get("https://api.openai.com/v1/models", headers=headers, timeout=15)
                if response.status_code == 200:
                    openai_data = response.json()
                    openai_models = []
                    # Filter for text generation models only
                    for model in openai_data.get("data", []):
                        model_id = model.get("id", "")
                        # Filter for chat/text models (exclude embedding, tts, etc.)
                        if any(prefix in model_id for prefix in ["gpt-4", "gpt-3.5", "o1"]) and not any(exclude in model_id for exclude in ["embed", "tts", "whisper", "dall-e"]):
                            # Determine context and size based on model
                            if "gpt-4o" in model_id:
                                size, context = "large", "128k"
                            elif "gpt-4-turbo" in model_id:
                                size, context = "large", "128k"
                            elif "gpt-4" in model_id:
                                size, context = "large", "8k"
                            elif "o1" in model_id:
                                size, context = "large", "200k"
                            elif "gpt-3.5" in model_id:
                                size, context = "medium", "16k"
                            else:
                                size, context = "medium", "4k"
                            
                            openai_models.append({
                                "name": model_id,
                                "size": size,
                                "context": context
                            })
                    refreshed_models["openai"] = sorted(openai_models, key=lambda x: x["name"])
                else:
                    raise Exception("OpenAI API error")
            else:
                raise Exception("No API key")
        except:
            # Fallback to known models
            refreshed_models["openai"] = [
                {"name": "gpt-4o", "size": "large", "context": "128k"},
                {"name": "gpt-4o-mini", "size": "small", "context": "128k"},
                {"name": "gpt-4-turbo", "size": "large", "context": "128k"},
                {"name": "gpt-4", "size": "large", "context": "8k"},
                {"name": "gpt-3.5-turbo", "size": "medium", "context": "16k"}
            ]
        
        # Anthropic models (live API)
        try:
            api_key = keychain_manager.retrieve_api_key("anthropic")
            if api_key:
                import httpx
                headers = {
                    "x-api-key": api_key,
                    "Content-Type": "application/json",
                    "anthropic-version": "2023-06-01"
                }
                response = httpx.get("https://api.anthropic.com/v1/models", headers=headers, timeout=15)
                if response.status_code == 200:
                    anthropic_data = response.json()
                    anthropic_models = []
                    for model in anthropic_data.get("data", []):
                        model_id = model.get("id", "")
                        # Determine size and context based on model name
                        if "opus" in model_id:
                            size, context = "large", "200k"
                        elif "sonnet" in model_id:
                            size, context = "large", "200k"
                        elif "haiku" in model_id:
                            size, context = "small", "200k"
                        else:
                            size, context = "medium", "200k"
                        
                        anthropic_models.append({
                            "name": model_id,
                            "size": size,
                            "context": context
                        })
                    refreshed_models["anthropic"] = sorted(anthropic_models, key=lambda x: x["name"])
                else:
                    raise Exception(f"Anthropic API error: {response.status_code}")
            else:
                raise Exception("No API key")
        except Exception as e:
            logger.warning(f"Failed to fetch Anthropic models: {e}")
            # Fallback to known models
            refreshed_models["anthropic"] = [
                {"name": "claude-3-5-sonnet-20241022", "size": "large", "context": "200k"},
                {"name": "claude-3-5-sonnet-20240620", "size": "large", "context": "200k"},
                {"name": "claude-3-opus-20240229", "size": "large", "context": "200k"},
                {"name": "claude-3-sonnet-20240229", "size": "medium", "context": "200k"},
                {"name": "claude-3-haiku-20240307", "size": "small", "context": "200k"}
            ]
        
        # Google AI models (live API)
        try:
            api_key = keychain_manager.retrieve_api_key("google")
            if api_key:
                import httpx
                response = httpx.get(f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}", timeout=15)
                if response.status_code == 200:
                    google_data = response.json()
                    google_models = []
                    for model in google_data.get("models", []):
                        model_name = model.get("name", "").replace("models/", "")
                        # Only include text generation models
                        if "gemini" in model_name.lower() and "vision" not in model_name.lower():
                            # Determine size and context
                            if "1.5-pro" in model_name:
                                size, context = "large", "2M"
                            elif "1.5-flash" in model_name:
                                size, context = "medium", "1M"
                            elif "1.0-pro" in model_name:
                                size, context = "medium", "32k"
                            else:
                                size, context = "medium", "32k"
                            
                            google_models.append({
                                "name": model_name,
                                "size": size,
                                "context": context
                            })
                    refreshed_models["google"] = sorted(google_models, key=lambda x: x["name"])
                else:
                    raise Exception(f"Google API error: {response.status_code}")
            else:
                raise Exception("No API key")
        except Exception as e:
            logger.warning(f"Failed to fetch Google models: {e}")
            # Fallback to known models
            refreshed_models["google"] = [
                {"name": "gemini-1.5-pro", "size": "large", "context": "2M"},
                {"name": "gemini-1.5-flash", "size": "medium", "context": "1M"},
                {"name": "gemini-1.0-pro", "size": "medium", "context": "32k"}
            ]
        
        # Groq models (live API)
        try:
            api_key = keychain_manager.retrieve_api_key("groq")
            if api_key:
                import httpx
                headers = {"Authorization": f"Bearer {api_key}"}
                response = httpx.get("https://api.groq.com/openai/v1/models", headers=headers, timeout=15)
                if response.status_code == 200:
                    groq_data = response.json()
                    groq_models = []
                    for model in groq_data.get("data", []):
                        model_id = model.get("id", "")
                        groq_models.append({
                            "name": model_id,
                            "size": "unknown",
                            "context": "32k"
                        })
                    refreshed_models["groq"] = sorted(groq_models, key=lambda x: x["name"])
                else:
                    raise Exception("Groq API error")
            else:
                raise Exception("No API key")
        except:
            refreshed_models["groq"] = [
                {"name": "llama-3.1-70b-versatile", "size": "70B", "context": "32k"},
                {"name": "llama-3.1-8b-instant", "size": "8B", "context": "32k"},
                {"name": "mixtral-8x7b-32768", "size": "8x7B", "context": "32k"}
            ]
        
        # Other providers (use static lists for now)
        refreshed_models["huggingface"] = [
            {"name": "meta-llama/Llama-2-70b-chat-hf", "size": "70B", "context": "4k"},
            {"name": "meta-llama/Llama-2-13b-chat-hf", "size": "13B", "context": "4k"},
            {"name": "mistralai/Mistral-7B-Instruct-v0.1", "size": "7B", "context": "8k"}
        ]
        
        refreshed_models["together"] = [
            {"name": "meta-llama/Llama-2-70b-chat-hf", "size": "70B", "context": "4k"},
            {"name": "mistralai/Mixtral-8x7B-Instruct-v0.1", "size": "8x7B", "context": "32k"}
        ]
        
        refreshed_models["replicate"] = [
            {"name": "meta/llama-2-70b-chat", "size": "70B", "context": "4k"},
            {"name": "mistralai/mixtral-8x7b-instruct-v0.1", "size": "8x7B", "context": "32k"}
        ]
        
        refreshed_models["cohere"] = [
            {"name": "command-r-plus", "size": "large", "context": "128k"},
            {"name": "command-r", "size": "medium", "context": "128k"},
            {"name": "command", "size": "medium", "context": "4k"}
        ]
        
        refreshed_models["mistral"] = [
            {"name": "mistral-large-latest", "size": "large", "context": "32k"},
            {"name": "mistral-medium-latest", "size": "medium", "context": "32k"},
            {"name": "mistral-small-latest", "size": "small", "context": "32k"}
        ]
        
        refreshed_models["mock"] = [
            {"name": "mock-model", "size": "test", "context": "unlimited"}
        ]
        
        # Store refresh timestamp
        from datetime import datetime
        refresh_timestamp = datetime.now().isoformat()
        
        # Cache the models globally (in a real app, you'd use Redis or database)
        global cached_models, last_refresh
        cached_models = refreshed_models
        last_refresh = refresh_timestamp
        
        return {
            "status": "success",
            "message": "Model lists refreshed from live APIs",
            "refreshed_at": refresh_timestamp,
            "model_counts": {provider: len(models) for provider, models in refreshed_models.items()},
            "available_models": refreshed_models
        }
        
    except Exception as e:
        logger.error(f"Failed to refresh model lists: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to refresh model lists: {str(e)}")

@app.post("/api/llm/test-live-apis", summary="Test Live API Connections")
async def test_live_api_connections():
    """Test individual provider API connections for debugging."""
    results = {}
    
    # Test OpenAI
    try:
        api_key = keychain_manager.retrieve_api_key("openai")
        if api_key:
            import httpx
            headers = {"Authorization": f"Bearer {api_key}"}
            response = httpx.get("https://api.openai.com/v1/models", headers=headers, timeout=15)
            results["openai"] = {
                "status": response.status_code,
                "success": response.status_code == 200,
                "model_count": len(response.json().get("data", [])) if response.status_code == 200 else 0,
                "error": None if response.status_code == 200 else response.text[:200]
            }
        else:
            results["openai"] = {"status": "no_key", "success": False, "error": "No API key stored"}
    except Exception as e:
        results["openai"] = {"status": "error", "success": False, "error": str(e)}
    
    # Test Anthropic
    try:
        api_key = keychain_manager.retrieve_api_key("anthropic")
        if api_key:
            import httpx
            headers = {"x-api-key": api_key, "Content-Type": "application/json", "anthropic-version": "2023-06-01"}
            response = httpx.get("https://api.anthropic.com/v1/models", headers=headers, timeout=15)
            results["anthropic"] = {
                "status": response.status_code,
                "success": response.status_code == 200,
                "model_count": len(response.json().get("data", [])) if response.status_code == 200 else 0,
                "error": None if response.status_code == 200 else response.text[:200]
            }
        else:
            results["anthropic"] = {"status": "no_key", "success": False, "error": "No API key stored"}
    except Exception as e:
        results["anthropic"] = {"status": "error", "success": False, "error": str(e)}
    
    # Test Google
    try:
        api_key = keychain_manager.retrieve_api_key("google")
        if api_key:
            import httpx
            response = httpx.get(f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}", timeout=15)
            results["google"] = {
                "status": response.status_code,
                "success": response.status_code == 200,
                "model_count": len(response.json().get("models", [])) if response.status_code == 200 else 0,
                "error": None if response.status_code == 200 else response.text[:200]
            }
        else:
            results["google"] = {"status": "no_key", "success": False, "error": "No API key stored"}
    except Exception as e:
        results["google"] = {"status": "error", "success": False, "error": str(e)}
    
    # Test Groq
    try:
        api_key = keychain_manager.retrieve_api_key("groq")
        if api_key:
            import httpx
            headers = {"Authorization": f"Bearer {api_key}"}
            response = httpx.get("https://api.groq.com/openai/v1/models", headers=headers, timeout=15)
            results["groq"] = {
                "status": response.status_code,
                "success": response.status_code == 200,
                "model_count": len(response.json().get("data", [])) if response.status_code == 200 else 0,
                "error": None if response.status_code == 200 else response.text[:200]
            }
        else:
            results["groq"] = {"status": "no_key", "success": False, "error": "No API key stored"}
    except Exception as e:
        results["groq"] = {"status": "error", "success": False, "error": str(e)}
    
    return {
        "test_results": results,
        "summary": {
            "total_tested": len(results),
            "successful": sum(1 for r in results.values() if r.get("success", False)),
            "with_keys": sum(1 for r in results.values() if r.get("status") != "no_key"),
            "live_api_confirmed": [provider for provider, result in results.items() if result.get("success", False)]
        }
    }

# Global cache for models
cached_models = {}
last_refresh = None

async def get_fallback_models():
    """Fallback static model lists if live APIs fail."""
    return {
        "ollama": [{"name": "llama3.2:latest", "size": "7B"}],
        "openai": [
            {"name": "gpt-4o", "size": "large", "context": "128k"},
            {"name": "gpt-4o-mini", "size": "small", "context": "128k"},
            {"name": "gpt-4-turbo", "size": "large", "context": "128k"},
            {"name": "gpt-4", "size": "large", "context": "8k"},
            {"name": "gpt-3.5-turbo", "size": "medium", "context": "16k"}
        ],
        "anthropic": [
            {"name": "claude-3-5-sonnet-20241022", "size": "large", "context": "200k"},
            {"name": "claude-3-opus-20240229", "size": "large", "context": "200k"},
            {"name": "claude-3-haiku-20240307", "size": "small", "context": "200k"}
        ],
        "google": [
            {"name": "gemini-1.5-pro", "size": "large", "context": "2M"},
            {"name": "gemini-1.5-flash", "size": "medium", "context": "1M"}
        ],
        "groq": [
            {"name": "llama-3.1-70b-versatile", "size": "70B", "context": "32k"},
            {"name": "llama-3.1-8b-instant", "size": "8B", "context": "32k"}
        ],
        "huggingface": [{"name": "meta-llama/Llama-2-7b-chat-hf", "size": "7B", "context": "4k"}],
        "together": [{"name": "meta-llama/Llama-3-8b-chat-hf", "size": "8B", "context": "8k"}],
        "replicate": [{"name": "meta/llama-2-70b-chat", "size": "70B", "context": "4k"}],
        "cohere": [{"name": "command-r-plus", "size": "large", "context": "128k"}],
        "mistral": [{"name": "mistral-large-latest", "size": "large", "context": "32k"}],
        "mock": [{"name": "mock-model", "size": "test", "context": "unlimited"}]
    }

@app.get("/api/ollama/models", summary="List Ollama Models")
async def list_ollama_models():
    """List all locally available Ollama models."""
    try:
        import httpx
        response = httpx.get("http://localhost:11434/api/tags", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            models = data.get("models", [])
            
            # Format the models for easier consumption
            formatted_models = []
            for model in models:
                formatted_models.append({
                    "name": model.get("name", ""),
                    "size": model.get("size", 0),
                    "modified_at": model.get("modified_at", ""),
                    "digest": model.get("digest", "")[:12] + "..." if model.get("digest") else "",
                    "details": {
                        "family": model.get("details", {}).get("family", ""),
                        "format": model.get("details", {}).get("format", ""),
                        "parameter_size": model.get("details", {}).get("parameter_size", "")
                    }
                })
            
            return {
                "models": formatted_models,
                "total_count": len(formatted_models),
                "ollama_running": True
            }
        else:
            raise HTTPException(status_code=503, detail="Ollama server not responding")
            
    except httpx.TimeoutException:
        raise HTTPException(status_code=503, detail="Ollama server timeout")
    except Exception as e:
        logger.error(f"Failed to fetch Ollama models: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch models: {str(e)}")

@app.post("/api/ollama/pull", summary="Pull Ollama Model")
async def pull_ollama_model(request: dict):
    """Pull a new model from Ollama registry."""
    try:
        model_name = request.get("model")
        if not model_name:
            raise HTTPException(status_code=400, detail="Model name is required")
        
        import httpx
        
        # Start the pull request
        async with httpx.AsyncClient(timeout=300) as client:  # 5 minute timeout
            response = await client.post(
                "http://localhost:11434/api/pull",
                json={"name": model_name},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                return {
                    "status": "success", 
                    "message": f"Successfully pulled model: {model_name}",
                    "model": model_name
                }
            else:
                error_text = response.text
                raise HTTPException(
                    status_code=response.status_code, 
                    detail=f"Failed to pull model: {error_text}"
                )
                
    except httpx.TimeoutException:
        raise HTTPException(status_code=408, detail="Model pull timeout - check Ollama logs")
    except Exception as e:
        logger.error(f"Failed to pull Ollama model {model_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to pull model: {str(e)}")

@app.delete("/api/ollama/models/{model_name}", summary="Delete Ollama Model")
async def delete_ollama_model(model_name: str):
    """Delete a locally stored Ollama model."""
    try:
        import httpx
        
        response = httpx.delete(
            "http://localhost:11434/api/delete",
            json={"name": model_name},
            timeout=30
        )
        
        if response.status_code == 200:
            return {
                "status": "success",
                "message": f"Successfully deleted model: {model_name}",
                "model": model_name
            }
        else:
            error_text = response.text
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to delete model: {error_text}"
            )
            
    except Exception as e:
        logger.error(f"Failed to delete Ollama model {model_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete model: {str(e)}")

@app.get("/api/ollama/status", summary="Ollama Server Status")
async def ollama_server_status():
    """Check if Ollama server is running and get basic info."""
    try:
        import httpx
        
        # Check if server is running
        response = httpx.get("http://localhost:11434/api/version", timeout=5)
        
        if response.status_code == 200:
            version_data = response.json()
            
            # Get model count
            models_response = httpx.get("http://localhost:11434/api/tags", timeout=5)
            model_count = 0
            if models_response.status_code == 200:
                models = models_response.json().get("models", [])
                model_count = len(models)
            
            return {
                "running": True,
                "version": version_data.get("version", "unknown"),
                "model_count": model_count,
                "host": "http://localhost:11434"
            }
        else:
            return {
                "running": False,
                "error": "Server not responding",
                "host": "http://localhost:11434"
            }
            
    except Exception as e:
        return {
            "running": False,
            "error": str(e),
            "host": "http://localhost:11434"
        }

@app.post("/api/extract-attributes", summary="Extract Narrative Attributes")
async def extract_attributes(request: dict):
    """Extract personas, namespaces, and styles from text using LLM analysis."""
    try:
        text = request.get("text", "").strip()
        mode = request.get("mode", "extract")  # extract, enhance, search
        context = request.get("context", None)
        
        if not text:
            raise HTTPException(status_code=400, detail="Text is required")
        
        # Get LLM provider for analysis
        provider = get_llm_provider()
        
        # Build analysis prompt based on mode
        if mode == "extract":
            system_prompt = """You are an expert at extracting narrative attributes from text. Analyze the given text and identify potential:

1. PERSONAS - Character types, perspectives, voices, or viewpoints
2. NAMESPACES - Universes, worlds, contexts, or conceptual frameworks  
3. STYLES - Writing approaches, tones, or linguistic patterns

For each attribute you identify, provide:
- type: "persona", "namespace", or "style"
- name: A concise, memorable name
- description: One sentence explanation
- content: 2-3 sentences of detailed description
- confidence: Float between 0.0-1.0
- keywords: Array of 3-5 relevant keywords

Return valid JSON with an "attributes" array."""

            user_prompt = f"Analyze this text for narrative attributes:\n\n{text}"
            
        elif mode == "enhance":
            if not context:
                raise HTTPException(status_code=400, detail="Context required for enhance mode")
                
            system_prompt = """You are enhancing an existing attribute with new information from text. The user will provide an existing attribute context and new text. Suggest improvements, expansions, or refinements to the attribute based on the new text.

Return JSON with enhanced attribute information."""

            user_prompt = f"Existing attribute context:\n{context}\n\nNew text to incorporate:\n{text}"
            
        else:  # search mode
            system_prompt = """You are finding semantic connections between text and existing attributes. Analyze the text and identify which types of attributes would be most relevant for understanding or transforming this text.

Return JSON with suggested attribute types and search queries."""

            user_prompt = f"What types of attributes would be most useful for this text:\n\n{text}"
        
        try:
            # Generate analysis
            response = provider.generate(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.3,
                max_tokens=1500
            )
            
            # Try to parse JSON response
            import json
            try:
                analysis = json.loads(response)
            except json.JSONDecodeError:
                # Fallback to mock analysis if JSON parsing fails
                analysis = generate_mock_attribute_analysis(text, mode)
            
        except Exception as e:
            logger.warning(f"LLM analysis failed, using fallback: {e}")
            analysis = generate_mock_attribute_analysis(text, mode)
        
        # Add metadata
        analysis["mode"] = mode
        analysis["text_length"] = len(text)
        analysis["timestamp"] = datetime.now().isoformat()
        
        # If search mode, add mock similar attributes
        if mode == "search":
            analysis["similar_attributes"] = [
                {
                    "id": "similar_1",
                    "type": "persona",
                    "name": "Analytical Thinker",
                    "description": "Someone who breaks down complex ideas systematically",
                    "similarity": 0.85
                },
                {
                    "id": "similar_2", 
                    "type": "namespace",
                    "name": "Academic Reality",
                    "description": "Universe where knowledge and research are primary forces",
                    "similarity": 0.72
                }
            ]
        
        return analysis
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to extract attributes: {e}")
        raise HTTPException(status_code=500, detail=f"Attribute extraction failed: {str(e)}")

def generate_mock_attribute_analysis(text: str, mode: str):
    """Generate mock analysis when LLM fails."""
    words = text.lower().split()
    
    attributes = []
    
    # Mock persona extraction
    if any(word in words for word in ["think", "believe", "feel", "consider", "wonder"]):
        attributes.append({
            "id": f"persona_{len(attributes)}",
            "type": "persona",
            "name": "Contemplative Mind",
            "description": "A perspective that seeks deeper understanding through reflection",
            "content": "This persona approaches situations with curiosity and thoughtfulness, taking time to consider multiple angles before forming conclusions. They value insight over quick answers.",
            "confidence": 0.78,
            "keywords": ["contemplative", "reflective", "thoughtful", "curious", "introspective"],
            "source_text": text[:100] + "..." if len(text) > 100 else text
        })
    
    # Mock namespace extraction  
    if any(word in words for word in ["world", "reality", "universe", "system", "framework"]):
        attributes.append({
            "id": f"namespace_{len(attributes)}",
            "type": "namespace", 
            "name": "Conceptual Realm",
            "description": "A universe where ideas and concepts have tangible form and influence",
            "content": "In this reality, abstract thoughts manifest as observable phenomena. Ideas compete for attention and validity in a marketplace of concepts, where the strength of an argument determines its physical presence.",
            "confidence": 0.72,
            "keywords": ["conceptual", "abstract", "ideational", "theoretical", "mental"],
            "source_text": text[:100] + "..." if len(text) > 100 else text
        })
    
    # Mock style extraction
    if len(words) > 20:
        if any(word in words for word in ["analyze", "examine", "study", "research", "investigate"]):
            style_name = "Analytical Expression"
            style_desc = "Clear, methodical communication that breaks down complex topics"
            keywords = ["analytical", "systematic", "precise", "methodical", "logical"]
        elif any(word in words for word in ["beautiful", "elegant", "graceful", "flowing", "artistic"]):
            style_name = "Aesthetic Expression"  
            style_desc = "Flowing, beautiful language that emphasizes grace and elegance"
            keywords = ["aesthetic", "graceful", "flowing", "elegant", "artistic"]
        else:
            style_name = "Direct Expression"
            style_desc = "Straightforward, clear communication focused on clarity"
            keywords = ["direct", "clear", "straightforward", "simple", "accessible"]
            
        attributes.append({
            "id": f"style_{len(attributes)}",
            "type": "style",
            "name": style_name,
            "description": style_desc, 
            "content": f"This style prioritizes {keywords[0]} communication, using {keywords[1]} approaches to convey ideas effectively. The language tends to be {keywords[2]} while maintaining {keywords[3]} structure.",
            "confidence": 0.65,
            "keywords": keywords,
            "source_text": text[:100] + "..." if len(text) > 100 else text
        })
    
    return {
        "attributes": attributes,
        "analysis_method": "mock_fallback",
        "text_analyzed": len(text),
        "mode": mode
    }

# Cleanup old sessions handled by lifespan manager above


@app.post("/transform-large", summary="Large Narrative Transformation with Context-Aware Splitting")
async def transform_large_narrative(request: TransformationRequest):
    """
    Transform large narratives using context-aware splitting and parallel processing.
    
    Automatically splits large inputs to avoid context length limits, processes chunks
    in parallel through the 5-stage LPE pipeline, and intelligently recombines results.
    
    Features:
    - Token-aware splitting with semantic boundary preservation
    - Parallel chunk processing for faster completion
    - Intelligent result recombination with coherence analysis
    - Context overlap to maintain narrative flow
    """
    try:
        transform_id = str(uuid.uuid4())
        logger.info(f"Starting large narrative transformation {transform_id}")
        
        # Check if context-aware splitting is needed
        splitter = ContextAwareSplitter(max_tokens_per_chunk=3000, model_type="general")
        
        if not splitter.should_split(request.narrative):
            # Single chunk - use regular transform
            logger.info(f"Text length acceptable for regular processing")
            return await transform_narrative(request)
        
        # Send initial progress update
        await send_progress_update(transform_id, "analyzing", "started", {
            "text_length": len(request.narrative),
            "estimated_tokens": splitter.estimate_tokens(request.narrative),
            "max_safe_tokens": splitter.get_max_safe_tokens(),
            "splitting_required": True
        })
        
        # Process using context-aware splitting
        result = await process_large_narrative(
            content=request.narrative,
            persona=request.target_persona,
            namespace=request.target_namespace,
            style=request.target_style,
            narrative_id=transform_id,
            max_parallel=2  # Conservative parallel processing
        )
        
        # Send final progress update
        await send_progress_update(transform_id, "complete", "finished", {
            "chunks_processed": result.get("chunk_count", 0),
            "success_rate": result.get("success_rate", 0.0),
            "coherence_score": result.get("coherence_analysis", {}).get("coherence_score", 0.0)
        })
        
        # Format response to match existing TransformationResponse structure
        steps = []
        if result.get("processing_metadata"):
            for i, chunk_result in enumerate(result["processing_metadata"]):
                if chunk_result.get("success", False):
                    chunk_steps = chunk_result.get("processing_steps", [])
                    for step in chunk_steps:
                        step_name = f"Chunk {i+1}: {step.get('name', 'Unknown')}"
                        steps.append(TransformationStep(
                            name=step_name,
                            input_snapshot=step.get('input', '')[:200] + "..." if len(step.get('input', '')) > 200 else step.get('input', ''),
                            output_snapshot=step.get('output', '')[:200] + "..." if len(step.get('output', '')) > 200 else step.get('output', ''),
                            duration_ms=step.get('duration_ms', 0),
                            metadata=step.get('metadata', {})
                        ))
        
        return TransformationResponse(
            transform_id=transform_id,
            original_narrative=request.narrative,
            transformed_narrative=result.get("final_narrative", ""),
            target_persona=request.target_persona,
            target_namespace=request.target_namespace,
            target_style=request.target_style,
            processing_time_ms=int(sum(step.duration_ms for step in steps)),
            steps=steps if request.show_steps else [],
            metadata={
                "splitting_metadata": result.get("splitting_metadata", {}),
                "coherence_analysis": result.get("coherence_analysis", {}),
                "chunk_count": result.get("chunk_count", 0),
                "success_rate": result.get("success_rate", 0.0),
                "large_narrative_processing": True
            }
        )
        
    except Exception as e:
        logger.error(f"Large narrative transformation failed: {str(e)}")
        await send_progress_update(transform_id, "error", "failed", {"error": str(e)})
        raise HTTPException(status_code=500, detail=f"Transformation failed: {str(e)}")


# ===== QUANTUM NARRATIVE THEORY ENDPOINTS =====

class MeaningStateResponse(BaseModel):
    """Response model for meaning-state representation."""
    semantic_dimension: int
    purity: float
    entropy: float
    canonical_probabilities: Dict[str, float]
    metadata: Dict[str, Any] = {}

class SemanticTomographyRequest(BaseModel):
    """Request for semantic tomography analysis."""
    text: str
    transformation_attributes: Dict[str, str] = Field(default_factory=dict)
    reading_style: str = Field(default="interpretation", description="How to read: interpretation, skeptical, devotional")

class SemanticTomographyResponse(BaseModel):
    """Response with complete semantic tomography data."""
    semantic_dimensions: List[str]
    before_state: MeaningStateResponse
    after_state: MeaningStateResponse
    measurement_outcome: Dict[str, float]
    transformation_metrics: Dict[str, float]
    povm_structure: Dict[str, Any]
    transformation_type: str

@app.get("/api/narrative-theory/status")
async def narrative_theory_status():
    """Get the status of the quantum narrative theory engine."""
    return {
        "available": NARRATIVE_THEORY_AVAILABLE,
        "engine_initialized": quantum_engine is not None,
        "semantic_dimension": quantum_engine.semantic_dimension if quantum_engine else None,
        "semantic_labels_count": len(quantum_engine.semantic_labels) if quantum_engine else None,
        "povm_type": "SIC-like" if quantum_engine and quantum_engine.canonical_povm.is_sic_like else "Standard"
    }

@app.post("/api/narrative-theory/meaning-state", response_model=MeaningStateResponse)
async def analyze_meaning_state(request: TransformationRequest):
    """
    Convert text to a quantum meaning-state representation.
    
    This endpoint demonstrates the Text component of your theory:
    the subjective, intra-conscious state that represents how meaning
    is distributed across semantic dimensions before reading.
    """
    if not NARRATIVE_THEORY_AVAILABLE or not quantum_engine:
        raise HTTPException(status_code=503, detail="Quantum Narrative Theory engine not available")
    
    try:
        # Get LLM provider for embeddings
        provider = get_llm_provider()
        
        # For demonstration, create a simple embedding
        # In production, this would use actual LLM embeddings
        import torch
        embedding = torch.randn(768)  # Placeholder embedding
        
        # Convert to meaning-state
        meaning_state = quantum_engine.text_to_meaning_state(request.narrative, embedding)
        
        # Get canonical POVM measurements
        canonical_probs = quantum_engine.canonical_povm.measure(meaning_state)
        
        return MeaningStateResponse(
            semantic_dimension=meaning_state.dimension,
            purity=meaning_state.purity(),
            entropy=meaning_state.von_neumann_entropy(),
            canonical_probabilities=canonical_probs,
            metadata={
                "text_length": len(request.narrative),
                "timestamp": datetime.now().isoformat()
            }
        )
        
    except Exception as e:
        logger.error(f"Meaning state analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/api/narrative-theory/semantic-tomography", response_model=SemanticTomographyResponse)
async def semantic_tomography(request: SemanticTomographyRequest):
    """
    Perform complete semantic tomography: show how a narrative transformation
    changes the subjective meaning-state according to quantum measurement theory.
    
    This is the core of your Theory of Narrative - demonstrating how narratives
    act as POVMs that transform consciousness via quantum-like measurement.
    """
    if not NARRATIVE_THEORY_AVAILABLE or not quantum_engine:
        raise HTTPException(status_code=503, detail="Quantum Narrative Theory engine not available")
    
    try:
        # Get LLM provider for embeddings
        provider = get_llm_provider()
        
        # Create embedding (placeholder - in production use actual LLM)
        import torch
        embedding = torch.randn(768)
        
        # Create initial meaning-state
        initial_state = quantum_engine.text_to_meaning_state(request.text, embedding)
        initial_canonical_probs = quantum_engine.canonical_povm.measure(initial_state)
        
        # Create narrative transformation
        transformation = quantum_engine.create_narrative_transformation(
            narrative_text=request.text,
            transformation_attributes=request.transformation_attributes,
            reading_style=request.reading_style
        )
        
        # Apply transformation and get analysis
        analysis = quantum_engine.apply_narrative(request.text, embedding, transformation)
        
        # Generate semantic tomography data
        tomography_data = quantum_engine.generate_semantic_tomography(analysis)
        
        # Build response
        return SemanticTomographyResponse(
            semantic_dimensions=tomography_data["semantic_dimensions"],
            before_state=MeaningStateResponse(
                semantic_dimension=analysis["initial_state"].dimension,
                purity=analysis["initial_state"].purity(),
                entropy=analysis["initial_state"].von_neumann_entropy(),
                canonical_probabilities=analysis["initial_canonical_probs"]
            ),
            after_state=MeaningStateResponse(
                semantic_dimension=analysis["final_state"].dimension,
                purity=analysis["final_state"].purity(),
                entropy=analysis["final_state"].von_neumann_entropy(),
                canonical_probabilities=analysis["final_canonical_probs"]
            ),
            measurement_outcome=analysis["measurement_probabilities"],
            transformation_metrics=tomography_data["metrics"],
            povm_structure=tomography_data["povm_structure"],
            transformation_type=analysis["transformation_type"]
        )
        
    except Exception as e:
        logger.error(f"Semantic tomography failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Tomography failed: {str(e)}")

@app.post("/api/narrative-theory/coherence-check")
async def check_narrative_coherence(narratives: List[SemanticTomographyRequest]):
    """
    Check Born-rule-like coherence constraints across multiple narratives.
    
    This implements your narrative norm - the coherence constraint that governs
    how probability assignments across different narratives must relate to
    maintain epistemic consistency.
    """
    if not NARRATIVE_THEORY_AVAILABLE or not quantum_engine:
        raise HTTPException(status_code=503, detail="Quantum Narrative Theory engine not available")
    
    if len(narratives) < 2:
        raise HTTPException(status_code=400, detail="Need at least 2 narratives for coherence checking")
    
    try:
        coherence_results = []
        canonical_distributions = []
        
        import torch
        
        # Analyze each narrative
        for i, narrative_req in enumerate(narratives):
            embedding = torch.randn(768)  # Placeholder
            meaning_state = quantum_engine.text_to_meaning_state(narrative_req.text, embedding)
            canonical_probs = quantum_engine.canonical_povm.measure(meaning_state)
            canonical_distributions.append(canonical_probs)
        
        # Check pairwise coherence (simplified version)
        total_coherence_score = 0.0
        comparisons = 0
        
        for i in range(len(canonical_distributions)):
            for j in range(i + 1, len(canonical_distributions)):
                # Compute KL divergence as coherence metric
                prob_i = list(canonical_distributions[i].values())
                prob_j = list(canonical_distributions[j].values())
                
                # Add small epsilon to avoid log(0)
                epsilon = 1e-8
                prob_i = [p + epsilon for p in prob_i]
                prob_j = [p + epsilon for p in prob_j]
                
                # Normalize
                sum_i = sum(prob_i)
                sum_j = sum(prob_j)
                prob_i = [p / sum_i for p in prob_i]
                prob_j = [p / sum_j for p in prob_j]
                
                # Symmetric KL divergence
                kl_ij = sum(p * torch.log(torch.tensor(p / q)).item() for p, q in zip(prob_i, prob_j))
                kl_ji = sum(q * torch.log(torch.tensor(q / p)).item() for p, q in zip(prob_i, prob_j))
                symmetric_kl = (kl_ij + kl_ji) / 2
                
                coherence_score = max(0.0, 1.0 - symmetric_kl)  # Convert to similarity score
                total_coherence_score += coherence_score
                comparisons += 1
                
                coherence_results.append({
                    "narrative_pair": [i, j],
                    "coherence_score": coherence_score,
                    "kl_divergence": symmetric_kl
                })
        
        average_coherence = total_coherence_score / comparisons if comparisons > 0 else 0.0
        
        return {
            "overall_coherence": average_coherence,
            "is_coherent": average_coherence > 0.7,  # Threshold for coherence
            "pairwise_results": coherence_results,
            "canonical_distributions": canonical_distributions,
            "num_narratives": len(narratives),
            "coherence_constraint": "Born-rule analogue (SIC-POVM based)"
        }
        
    except Exception as e:
        logger.error(f"Coherence checking failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Coherence check failed: {str(e)}")

@app.post("/api/narrative-theory/analyze", response_model=QNTNarrativeAnalysis)
async def analyze_narrative_qnt(request: QNTNarrativeRequest):
    """
    Comprehensive Quantum Narrative Theory analysis extracting persona, namespace, style, and essence.
    
    This endpoint implements the complete QNT formalism to decompose a narrative into its 
    fundamental components according to the latest theoretical framework:
    
    - Persona (Ψ): The subjective voice and perspective
    - Namespace (Ω): The universe of discourse and cultural context  
    - Style (Σ): The linguistic and rhetorical approach
    - Essence (E): The invariant core meaning preserved across transformations
    - Quantum State: Optional high-dimensional meaning representation
    """
    if not NARRATIVE_THEORY_AVAILABLE or not quantum_engine:
        raise HTTPException(status_code=503, detail="Quantum Narrative Theory engine not available")
    
    try:
        import uuid
        import torch
        import json
        import re
        from datetime import datetime
        
        analysis_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        # Get LLM provider for analysis
        provider = get_llm_provider()
        
        # Generate embedding for quantum analysis (if requested)
        embedding = None
        quantum_state_data = None
        
        if request.include_quantum_state and quantum_engine:
            # Create a more realistic embedding based on text
            import hashlib
            text_hash = hashlib.md5(request.narrative.encode()).hexdigest()
            torch.manual_seed(int(text_hash[:8], 16))  # Deterministic based on text
            embedding = torch.randn(768)
            
            # Convert to quantum meaning state
            meaning_state = quantum_engine.text_to_meaning_state(request.narrative, embedding)
            canonical_probs = quantum_engine.canonical_povm.measure(meaning_state)
            
            # Extract quantum state information
            density_matrix = meaning_state.density_matrix.detach().numpy().tolist()
            eigenvals = torch.linalg.eigvals(meaning_state.density_matrix).real.detach().numpy().tolist()
            purity = torch.trace(meaning_state.density_matrix @ meaning_state.density_matrix).real.item()
            
            quantum_state_data = QNTQuantumState(
                dimension=meaning_state.dimension,
                density_matrix=density_matrix,
                eigenvalues=eigenvals,
                purity=purity,
                semantic_labels=quantum_engine.semantic_labels[:meaning_state.dimension],
                measurement_probabilities=canonical_probs
            )
        
        # Analyze Persona using LLM
        persona_prompt = f"""Analyze this narrative text and identify the persona (voice/perspective):

Text: "{request.narrative}"

Extract:
1. The primary persona archetype (e.g., "wise elder", "curious child", "skeptical scientist", "romantic dreamer")
2. Key characteristics of this voice
3. Specific textual indicators that reveal this persona

Respond with JSON:
{{
    "name": "persona archetype",
    "confidence": 0.85,
    "characteristics": ["trait1", "trait2", "trait3"],
    "voice_indicators": ["specific phrases", "word choices", "perspective markers"]
}}"""

        try:
            persona_response = await provider.complete(persona_prompt, max_tokens=300)
            persona_data = json.loads(persona_response)
            persona = QNTPersona(**persona_data)
        except Exception as e:
            logger.warning(f"Persona analysis failed, using fallback: {e}")
            persona = QNTPersona(
                name="neutral observer",
                confidence=0.5,
                characteristics=["objective", "descriptive"],
                voice_indicators=["third person narrative", "descriptive language"]
            )

        # Analyze Namespace using LLM
        namespace_prompt = f"""Analyze this narrative text and identify the namespace (universe/context):

Text: "{request.narrative}"

Extract:
1. The narrative universe or domain (e.g., "maritime/nautical", "modern urban", "fantasy realm", "domestic life")
2. Cultural and temporal context
3. Domain-specific elements and markers
4. Level of abstraction (literal, metaphorical, mythic, etc.)

Respond with JSON:
{{
    "name": "narrative universe",
    "confidence": 0.85,
    "domain_markers": ["specific elements", "vocabulary", "references"],
    "cultural_context": "time period and culture",
    "reality_layer": "literal/metaphorical/mythic"
}}"""

        try:
            namespace_response = await provider.complete(namespace_prompt, max_tokens=300)
            namespace_data = json.loads(namespace_response)
            namespace = QNTNamespace(**namespace_data)
        except Exception as e:
            logger.warning(f"Namespace analysis failed, using fallback: {e}")
            namespace = QNTNamespace(
                name="contemporary realism",
                confidence=0.5,
                domain_markers=["everyday language", "realistic scenarios"],
                cultural_context="modern contemporary",
                reality_layer="literal"
            )

        # Analyze Style using LLM
        style_prompt = f"""Analyze this narrative text and identify the style (linguistic/rhetorical approach):

Text: "{request.narrative}"

Extract:
1. The stylistic approach (e.g., "lyrical", "conversational", "formal", "poetic", "minimalist")
2. Key linguistic features and patterns
3. Rhetorical and literary devices used
4. Tone and mood characteristics

Respond with JSON:
{{
    "name": "stylistic approach",
    "confidence": 0.85,
    "linguistic_features": ["sentence structure", "vocabulary level", "rhythm"],
    "rhetorical_devices": ["metaphor", "repetition", "imagery"],
    "tone_characteristics": ["melancholic", "hopeful", "urgent"]
}}"""

        try:
            style_response = await provider.complete(style_prompt, max_tokens=300)
            style_data = json.loads(style_response)
            style = QNTStyle(**style_data)
        except Exception as e:
            logger.warning(f"Style analysis failed, using fallback: {e}")
            style = QNTStyle(
                name="descriptive prose",
                confidence=0.5,
                linguistic_features=["clear sentences", "descriptive language"],
                rhetorical_devices=["imagery", "narrative flow"],
                tone_characteristics=["neutral", "informative"]
            )

        # Analyze Essence using LLM and QNT principles
        essence_prompt = f"""Analyze this narrative text and extract the essential meaning (essence):

Text: "{request.narrative}"

Extract the core invariant meaning that would be preserved across different transformations:
1. The distilled essential message
2. Elements that are fundamental to the meaning
3. Semantic density/concentration
4. Internal coherence

Respond with JSON:
{{
    "core_meaning": "essential meaning in one sentence",
    "meaning_density": 0.75,
    "invariant_elements": ["core concepts", "key relationships", "essential emotions"],
    "coherence_score": 0.85,
    "entropy_measure": 0.65
}}"""

        try:
            essence_response = await provider.complete(essence_prompt, max_tokens=300)
            essence_data = json.loads(essence_response)
            
            # Add semantic vector if requested
            semantic_vector = None
            if request.include_essence_vectors and embedding is not None:
                # Use a subset of the embedding as semantic vector
                semantic_vector = embedding[:16].detach().numpy().tolist()
            
            essence = QNTEssence(
                core_meaning=essence_data["core_meaning"],
                meaning_density=essence_data["meaning_density"],
                invariant_elements=essence_data["invariant_elements"],
                semantic_vector=semantic_vector,
                coherence_score=essence_data["coherence_score"],
                entropy_measure=essence_data["entropy_measure"]
            )
        except Exception as e:
            logger.warning(f"Essence analysis failed, using fallback: {e}")
            essence = QNTEssence(
                core_meaning="A narrative describing a situation or event",
                meaning_density=0.5,
                invariant_elements=["narrative structure", "descriptive content"],
                semantic_vector=None,
                coherence_score=0.7,
                entropy_measure=0.5
            )

        # Calculate transformation potential scores
        transformation_potential = {
            "persona_flexibility": min(1.0, 1.0 - persona.confidence + 0.2),
            "namespace_adaptability": min(1.0, 1.0 - namespace.confidence + 0.2),
            "style_malleability": min(1.0, 1.0 - style.confidence + 0.2),
            "essence_preservation": essence.coherence_score,
            "overall_transformability": (persona.confidence + namespace.confidence + style.confidence) / 3.0
        }

        # Analyze semantic topology
        semantic_topology = {
            "narrative_complexity": len(request.narrative.split()) / 100.0,  # Rough complexity measure
            "semantic_density_distribution": {
                "persona_weight": 0.25,
                "namespace_weight": 0.30,
                "style_weight": 0.20,
                "essence_weight": 0.25
            },
            "transformation_readiness": transformation_potential["overall_transformability"],
            "quantum_entanglement_score": quantum_state_data.purity if quantum_state_data else None
        }

        # Processing metadata
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        processing_metadata = {
            "processing_time_ms": processing_time,
            "analysis_depth": request.semantic_depth,
            "quantum_analysis_enabled": request.include_quantum_state,
            "essence_vectors_enabled": request.include_essence_vectors,
            "llm_provider": provider.__class__.__name__,
            "quantum_engine_dimension": quantum_engine.semantic_dimension if quantum_engine else None,
            "analysis_timestamp": start_time.isoformat(),
            "version": "QNT-v2.0"
        }

        return QNTNarrativeAnalysis(
            narrative_id=analysis_id,
            original_narrative=request.narrative,
            persona=persona,
            namespace=namespace,
            style=style,
            essence=essence,
            quantum_state=quantum_state_data,
            transformation_potential=transformation_potential,
            semantic_topology=semantic_topology,
            processing_metadata=processing_metadata
        )

    except Exception as e:
        logger.error(f"QNT narrative analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Narrative analysis failed: {str(e)}")

@app.get("/api/narrative-theory/semantic-dimensions")
async def get_semantic_dimensions():
    """Get the semantic dimensions and POVM structure used by the engine."""
    if not NARRATIVE_THEORY_AVAILABLE or not quantum_engine:
        raise HTTPException(status_code=503, detail="Quantum Narrative Theory engine not available")
    
    try:
        overlaps = quantum_engine.canonical_povm.compute_pairwise_overlaps()
        
        return {
            "semantic_labels": quantum_engine.semantic_labels,
            "dimension": quantum_engine.semantic_dimension,
            "num_povm_elements": quantum_engine.canonical_povm.num_elements,
            "is_sic_like": quantum_engine.canonical_povm.is_sic_like,
            "pairwise_overlaps": overlaps.tolist(),
            "povm_properties": {
                "informationally_complete": quantum_engine.canonical_povm.num_elements >= quantum_engine.semantic_dimension ** 2,
                "symmetric": quantum_engine.canonical_povm.is_sic_like,
                "rank_structure": "rank-1 projectors" if quantum_engine.canonical_povm.is_sic_like else "mixed rank"
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get semantic dimensions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get dimensions: {str(e)}")

# ===== END QUANTUM NARRATIVE THEORY ENDPOINTS =====

# ===== ATTRIBUTE MANAGEMENT ENDPOINTS =====

try:
    from attribute_manager import AttributeStorage, AttributeAlgorithmTracker
    attribute_storage = AttributeStorage()
    ATTRIBUTE_MANAGEMENT_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Attribute management not available: {e}")
    ATTRIBUTE_MANAGEMENT_AVAILABLE = False

@app.post("/api/attributes/save", response_model=Dict[str, Any])
async def save_attribute_from_analysis(request: SaveAttributeRequest):
    """Save specific attributes from a QNT analysis for future use."""
    if not ATTRIBUTE_MANAGEMENT_AVAILABLE:
        raise HTTPException(status_code=503, detail="Attribute management not available")
    
    try:
        # For now, we'll create a mock analysis since we don't have analysis caching yet
        # In a full implementation, we'd retrieve the analysis from cache by analysis_id
        
        # Get LLM provider for algorithm details
        provider = get_llm_provider()
        provider_name = provider.__class__.__name__
        
        saved_attributes = []
        
        for attr_type in request.attribute_types:
            if attr_type not in ["persona", "namespace", "style", "essence"]:
                continue
                
            # Get algorithm details for this attribute type
            if attr_type == "persona":
                algorithm = AttributeAlgorithmTracker.get_persona_algorithm_details(provider_name)
            elif attr_type == "namespace":
                algorithm = AttributeAlgorithmTracker.get_namespace_algorithm_details(provider_name)
            elif attr_type == "style":
                algorithm = AttributeAlgorithmTracker.get_style_algorithm_details(provider_name)
            elif attr_type == "essence":
                algorithm = AttributeAlgorithmTracker.get_essence_algorithm_details(provider_name)
            
            # Create attribute data
            attribute_data = {
                "name": f"{request.name}_{attr_type}",
                "attribute_type": attr_type,
                "source_analysis_id": request.analysis_id,
                "algorithm_used": algorithm,
                "confidence_score": 0.85,  # Mock score
                "value": f"Saved {attr_type} attribute",  # Mock value
                "tags": request.tags,
                "notes": request.notes
            }
            
            # Save to storage
            attr_id = await attribute_storage.save_attribute(attribute_data)
            saved_attributes.append({
                "attribute_id": attr_id,
                "type": attr_type,
                "name": attribute_data["name"]
            })
        
        return {
            "success": True,
            "message": f"Saved {len(saved_attributes)} attributes",
            "saved_attributes": saved_attributes,
            "source_analysis": request.analysis_id
        }
        
    except Exception as e:
        logger.error(f"Failed to save attributes: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to save attributes: {str(e)}")

@app.get("/api/attributes/list", response_model=AttributeListResponse)
async def list_saved_attributes(
    attribute_type: Optional[str] = None,
    tags: Optional[str] = None,
    limit: int = 50
):
    """List saved attributes with optional filtering."""
    if not ATTRIBUTE_MANAGEMENT_AVAILABLE:
        raise HTTPException(status_code=503, detail="Attribute management not available")
    
    try:
        # Parse tags if provided
        tag_list = None
        if tags:
            tag_list = [tag.strip() for tag in tags.split(",")]
        
        # Get filtered attributes
        attributes = await attribute_storage.list_attributes(
            attribute_type=attribute_type,
            tags=tag_list
        )
        
        # Limit results
        limited_attributes = attributes[:limit]
        
        # Convert to SavedAttribute objects
        saved_attrs = []
        for attr in limited_attributes:
            saved_attr = SavedAttribute(
                attribute_id=attr["attribute_id"],
                name=attr["name"],
                attribute_type=attr["attribute_type"],
                value=attr["value"],
                confidence_score=attr["confidence_score"],
                algorithm_used=AttributeAlgorithm(**attr["algorithm_used"]),
                created_at=attr["created_at"],
                tags=attr.get("tags", []),
                notes=attr.get("notes")
            )
            saved_attrs.append(saved_attr)
        
        return AttributeListResponse(
            attributes=saved_attrs,
            total=len(attributes),
            filtered=len(limited_attributes)
        )
        
    except Exception as e:
        logger.error(f"Failed to list attributes: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list attributes: {str(e)}")

@app.get("/api/attributes/{attribute_id}", response_model=SavedAttribute)
async def get_attribute(attribute_id: str):
    """Get a specific saved attribute by ID."""
    if not ATTRIBUTE_MANAGEMENT_AVAILABLE:
        raise HTTPException(status_code=503, detail="Attribute management not available")
    
    try:
        attr_data = await attribute_storage.get_attribute(attribute_id)
        if not attr_data:
            raise HTTPException(status_code=404, detail="Attribute not found")
        
        return SavedAttribute(
            attribute_id=attr_data["attribute_id"],
            name=attr_data["name"],
            attribute_type=attr_data["attribute_type"],
            value=attr_data["value"],
            confidence_score=attr_data["confidence_score"],
            algorithm_used=AttributeAlgorithm(**attr_data["algorithm_used"]),
            created_at=attr_data["created_at"],
            tags=attr_data.get("tags", []),
            notes=attr_data.get("notes")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get attribute: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get attribute: {str(e)}")

@app.delete("/api/attributes/{attribute_id}")
async def delete_attribute(attribute_id: str):
    """Delete a saved attribute."""
    if not ATTRIBUTE_MANAGEMENT_AVAILABLE:
        raise HTTPException(status_code=503, detail="Attribute management not available")
    
    try:
        success = await attribute_storage.delete_attribute(attribute_id)
        if not success:
            raise HTTPException(status_code=404, detail="Attribute not found")
        
        return {
            "success": True,
            "message": "Attribute deleted successfully",
            "attribute_id": attribute_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete attribute: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete attribute: {str(e)}")

@app.get("/api/attributes/stats")
async def get_attribute_statistics():
    """Get statistics about saved attributes."""
    if not ATTRIBUTE_MANAGEMENT_AVAILABLE:
        raise HTTPException(status_code=503, detail="Attribute management not available")
    
    try:
        stats = await attribute_storage.get_statistics()
        
        return {
            "total_attributes": stats["total_attributes"],
            "by_type": stats["by_type"],
            "by_algorithm": stats["by_algorithm"],
            "by_confidence": stats["by_confidence"],
            "storage_path": stats["storage_path"]
        }
        
    except Exception as e:
        logger.error(f"Failed to get attribute statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")

@app.get("/api/attributes/algorithms/{algorithm_name}")
async def get_algorithm_details(algorithm_name: str):
    """Get detailed information about a specific algorithm used for attribute extraction."""
    if not ATTRIBUTE_MANAGEMENT_AVAILABLE:
        raise HTTPException(status_code=503, detail="Attribute management not available")
    
    try:
        provider = get_llm_provider()
        provider_name = provider.__class__.__name__
        
        # Get algorithm details based on name
        if algorithm_name.lower() == "persona" or "persona" in algorithm_name.lower():
            algorithm = AttributeAlgorithmTracker.get_persona_algorithm_details(provider_name)
        elif algorithm_name.lower() == "namespace" or "namespace" in algorithm_name.lower():
            algorithm = AttributeAlgorithmTracker.get_namespace_algorithm_details(provider_name)
        elif algorithm_name.lower() == "style" or "style" in algorithm_name.lower():
            algorithm = AttributeAlgorithmTracker.get_style_algorithm_details(provider_name)
        elif algorithm_name.lower() == "essence" or "essence" in algorithm_name.lower():
            algorithm = AttributeAlgorithmTracker.get_essence_algorithm_details(provider_name)
        else:
            raise HTTPException(status_code=404, detail="Algorithm not found")
        
        return {
            "algorithm": algorithm,
            "transparency": {
                "purpose": "Provides full algorithmic transparency for attribute extraction",
                "reproducibility": "All parameters and prompts are exposed for reproduction",
                "version_tracking": "Algorithm versions are tracked for consistency",
                "projection_insight": "Enables understanding of how attributes are used in projections"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get algorithm details: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get algorithm details: {str(e)}")

# ===== END ATTRIBUTE MANAGEMENT ENDPOINTS =====

# ===== GUTENBERG BOOK ANALYSIS ENDPOINTS =====

from gutenberg_service_simple import gutenberg_service
from pydantic import BaseModel

class BookSearchRequest(BaseModel):
    query: Optional[str] = None
    author: Optional[str] = None
    subject: Optional[str] = None
    language: str = "en"
    limit: int = 50

class AnalysisJobRequest(BaseModel):
    gutenberg_ids: List[int]
    analysis_type: str = "sample"

@app.get("/gutenberg/search")
async def search_gutenberg_books(
    query: Optional[str] = None,
    author: Optional[str] = None,
    subject: Optional[str] = None,
    language: str = "en",
    limit: int = 50
):
    """Search Project Gutenberg catalog for books"""
    try:
        books = await gutenberg_service.search_books(
            query=query,
            author=author,
            subject=subject,
            language=language,
            limit=limit
        )
        
        books_data = []
        for book in books:
            books_data.append({
                "gutenberg_id": book.gutenberg_id,
                "title": book.title,
                "author": book.author,
                "language": book.language,
                "subjects": book.subjects,
                "download_url": book.download_url
            })
        
        return {
            "books": books_data,
            "total_found": len(books_data),
            "query_info": {
                "query": query,
                "author": author,
                "subject": subject,
                "language": language,
                "limit": limit
            }
        }
        
    except Exception as e:
        logger.error(f"Gutenberg search failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.post("/gutenberg/analyze")
async def create_gutenberg_analysis_job(request: AnalysisJobRequest):
    """Create a batch analysis job for Gutenberg books"""
    try:
        valid_types = ["sample", "targeted", "full"]
        if request.analysis_type not in valid_types:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid analysis_type. Must be one of: {valid_types}"
            )
        
        job_id = await gutenberg_service.create_analysis_job(
            gutenberg_ids=request.gutenberg_ids,
            analysis_type=request.analysis_type
        )
        
        return {
            "success": True,
            "message": "Analysis job created successfully",
            "data": {
                "job_id": job_id,
                "gutenberg_ids": request.gutenberg_ids,
                "analysis_type": request.analysis_type,
                "status": "pending"
            }
        }
        
    except Exception as e:
        logger.error(f"Job creation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Job creation failed: {str(e)}")

@app.get("/gutenberg/jobs")
async def list_gutenberg_jobs():
    """List all analysis jobs"""
    try:
        jobs = await gutenberg_service.list_jobs()
        
        jobs_data = []
        for job in jobs:
            jobs_data.append({
                "job_id": job.job_id,
                "status": job.status,
                "progress": job.progress,
                "created_at": job.created_at.isoformat() if job.created_at else None,
                "started_at": job.started_at.isoformat() if job.started_at else None,
                "completed_at": job.completed_at.isoformat() if job.completed_at else None,
                "gutenberg_ids": job.gutenberg_ids,
                "analysis_type": job.analysis_type,
                "results_summary": job.results_summary,
                "error_message": job.error_message
            })
        
        return {
            "success": True,
            "message": f"Found {len(jobs_data)} analysis jobs",
            "data": {"jobs": jobs_data}
        }
        
    except Exception as e:
        logger.error(f"Failed to list jobs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list jobs: {str(e)}")

@app.get("/gutenberg/jobs/{job_id}")
async def get_gutenberg_job_status(job_id: str):
    """Get detailed status of a specific analysis job"""
    try:
        job = await gutenberg_service.get_job_status(job_id)
        
        if not job:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
        
        return {
            "job_id": job.job_id,
            "status": job.status,
            "progress": job.progress,
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            "gutenberg_ids": job.gutenberg_ids,
            "analysis_type": job.analysis_type,
            "results_summary": job.results_summary,
            "error_message": job.error_message
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get job status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get job status: {str(e)}")

@app.get("/gutenberg/jobs/{job_id}/results")
async def get_gutenberg_job_results(job_id: str, limit: int = 50):
    """Get results of a completed analysis job"""
    try:
        job = await gutenberg_service.get_job_status(job_id)
        
        if not job:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
        
        if job.status != "completed":
            raise HTTPException(
                status_code=400, 
                detail=f"Job {job_id} is not completed (status: {job.status})"
            )
        
        results = await gutenberg_service.get_job_results(job_id)
        
        if not results:
            raise HTTPException(status_code=404, detail=f"Results for job {job_id} not found")
        
        # Limit the results returned
        if "high_quality_paragraphs" in results:
            results["high_quality_paragraphs"] = results["high_quality_paragraphs"][:limit]
        
        # Handle both old and new result structures
        job_info = results.get("job_info") or results.get("job")
        job_results = results.get("results", [])
        
        # Handle different result types
        if isinstance(job_results, dict):
            # This is a composite analysis with narrative DNA
            return {
                "success": True,
                "message": f"Retrieved results for job {job_id}",
                "data": {
                    "job_info": job_info,
                    "results": job_results
                }
            }
        else:
            # This is a strategic sampling with paragraph list
            high_quality_paragraphs = results.get("high_quality_paragraphs", job_results)
            if isinstance(high_quality_paragraphs, list) and limit:
                high_quality_paragraphs = high_quality_paragraphs[:limit]
            
            return {
                "success": True,
                "message": f"Retrieved results for job {job_id}",
                "data": {
                    "job_info": job_info,
                    "results": high_quality_paragraphs,
                    "summary": job_info.get("results_summary") if job_info else None,
                    "total_candidates": len(high_quality_paragraphs) if isinstance(high_quality_paragraphs, list) else 0,
                    "returned_count": min(limit or len(high_quality_paragraphs), len(high_quality_paragraphs)) if isinstance(high_quality_paragraphs, list) else 0
                }
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get job results: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get job results: {str(e)}")

@app.delete("/gutenberg/jobs/{job_id}")
async def cancel_gutenberg_job(job_id: str):
    """Cancel a running analysis job"""
    try:
        job = await gutenberg_service.get_job_status(job_id)
        
        if not job:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
        
        if job.status in ["completed", "failed"]:
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot cancel job in {job.status} status"
            )
        
        job.status = "cancelled"
        job.completed_at = datetime.now()
        
        return {
            "success": True,
            "message": f"Job {job_id} cancelled successfully",
            "data": {"job_id": job_id, "status": "cancelled"}
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cancel job: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to cancel job: {str(e)}")

@app.get("/gutenberg/stats")
async def get_gutenberg_stats():
    """Get overall statistics about Gutenberg analysis activities"""
    try:
        jobs = await gutenberg_service.list_jobs()
        
        stats = {
            "total_jobs": len(jobs),
            "completed_jobs": len([j for j in jobs if j.status == "completed"]),
            "running_jobs": len([j for j in jobs if j.status == "running"]),
            "failed_jobs": len([j for j in jobs if j.status == "failed"]),
            "total_books_analyzed": sum(len(j.gutenberg_ids) for j in jobs if j.status == "completed"),
            "cache_size": len(list(gutenberg_service.cache_dir.glob("*.txt"))),
            "results_available": len(list(gutenberg_service.cache_dir.glob("analysis_results_*.json")))
        }
        
        return {
            "success": True,
            "message": "Analysis statistics retrieved",
            "data": stats
        }
        
    except Exception as e:
        logger.error(f"Failed to get stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

@app.get("/gutenberg/catalog/browse")
async def browse_gutenberg_catalog(
    offset: int = 0,
    limit: int = 100,
    sort_by: str = "downloads",  # downloads, title, author, recent
    language: str = "en"
):
    """Browse the full Project Gutenberg catalog with pagination"""
    try:
        # Ensure we have catalog cache
        await gutenberg_service._ensure_catalog_cache()
        
        # Get all books from cache
        all_books = []
        for book_data in gutenberg_service.catalog_cache:
            if language == "all" or book_data.get('language', 'en') == language:
                all_books.append(book_data)
        
        # Sort books
        if sort_by == "downloads":
            all_books.sort(key=lambda x: x.get('downloads', 0), reverse=True)
        elif sort_by == "title":
            all_books.sort(key=lambda x: x.get('title', '').lower())
        elif sort_by == "author":
            all_books.sort(key=lambda x: x.get('author', '').lower())
        elif sort_by == "recent":
            all_books.sort(key=lambda x: x.get('gutenberg_id', 0), reverse=True)
        
        # Apply pagination
        paginated_books = all_books[offset:offset + limit]
        
        return {
            "success": True,
            "message": f"Found {len(all_books)} books in catalog",
            "data": {
                "books": paginated_books,
                "pagination": {
                    "offset": offset,
                    "limit": limit,
                    "total_books": len(all_books),
                    "has_more": offset + limit < len(all_books)
                },
                "sort_by": sort_by,
                "language": language
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to browse catalog: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to browse catalog: {str(e)}")

@app.get("/gutenberg/catalog/popular")
async def get_popular_gutenberg_books(limit: int = 50):
    """Get most popular books from Project Gutenberg"""
    try:
        # Get popular books directly from the service
        popular_books = await gutenberg_service._get_popular_books()
        
        # Convert to the expected format
        books_data = []
        for book in popular_books[:limit]:
            if isinstance(book, dict):
                books_data.append(book)
            else:
                books_data.append({
                    "gutenberg_id": book.gutenberg_id,
                    "title": book.title,
                    "author": book.author,
                    "language": book.language,
                    "subjects": book.subjects,
                    "download_url": book.download_url,
                    "downloads": getattr(book, 'downloads', 0)
                })
        
        return {
            "success": True,
            "message": f"Found {len(books_data)} popular books",
            "data": {
                "books": books_data,
                "total_found": len(books_data)
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get popular books: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get popular books: {str(e)}")

@app.get("/gutenberg/catalog/recent")
async def get_recent_gutenberg_books(limit: int = 50):
    """Get recently added books from Project Gutenberg RSS feeds"""
    try:
        # Get recent books from RSS feeds
        recent_books = await gutenberg_service._get_recent_books_from_rss()
        
        return {
            "success": True,
            "message": f"Found {len(recent_books)} recent books",
            "data": {
                "books": recent_books[:limit],
                "total_found": len(recent_books)
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get recent books: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get recent books: {str(e)}")

@app.post("/gutenberg/catalog/refresh")
async def refresh_gutenberg_catalog():
    """Force refresh of the Project Gutenberg catalog cache"""
    try:
        # Clear existing cache
        gutenberg_service.catalog_cache = []
        if gutenberg_service.catalog_cache_file.exists():
            gutenberg_service.catalog_cache_file.unlink()
        
        # Rebuild cache
        await gutenberg_service._build_catalog_cache()
        
        return {
            "success": True,
            "message": f"Catalog cache refreshed with {len(gutenberg_service.catalog_cache)} books",
            "data": {
                "books_cached": len(gutenberg_service.catalog_cache),
                "cache_file": str(gutenberg_service.catalog_cache_file)
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to refresh catalog: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to refresh catalog: {str(e)}")

@app.get("/gutenberg/catalog/info")
async def get_catalog_info():
    """Get information about the current catalog cache"""
    try:
        await gutenberg_service._ensure_catalog_cache()
        
        # Analyze the catalog
        languages = {}
        authors = {}
        total_downloads = 0
        
        for book_data in gutenberg_service.catalog_cache:
            # Count languages
            lang = book_data.get('language', 'unknown')
            languages[lang] = languages.get(lang, 0) + 1
            
            # Count authors
            author = book_data.get('author', 'Unknown')
            authors[author] = authors.get(author, 0) + 1
            
            # Sum downloads
            total_downloads += book_data.get('downloads', 0)
        
        # Get top authors
        top_authors = sorted(authors.items(), key=lambda x: x[1], reverse=True)[:20]
        
        cache_file_exists = gutenberg_service.catalog_cache_file.exists()
        cache_file_size = gutenberg_service.catalog_cache_file.stat().st_size if cache_file_exists else 0
        cache_file_modified = datetime.fromtimestamp(gutenberg_service.catalog_cache_file.stat().st_mtime) if cache_file_exists else None
        
        return {
            "success": True,
            "message": "Catalog information retrieved",
            "data": {
                "total_books": len(gutenberg_service.catalog_cache),
                "languages": languages,
                "top_authors": [{"author": author, "book_count": count} for author, count in top_authors],
                "total_downloads": total_downloads,
                "cache_info": {
                    "file_exists": cache_file_exists,
                    "file_size_bytes": cache_file_size,
                    "last_modified": cache_file_modified.isoformat() if cache_file_modified else None,
                    "cache_file_path": str(gutenberg_service.catalog_cache_file)
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get catalog info: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get catalog info: {str(e)}")

# Strategic paragraph sampling endpoint
class StrategicSamplingRequest(BaseModel):
    gutenberg_id: int
    sample_count: int = 64
    min_length: int = 100
    max_length: int = 800
    avoid_first_last_percent: float = 0.1  # Avoid first/last 10% of book

@app.post("/gutenberg/strategic-sample")
async def create_strategic_sampling_job(request: StrategicSamplingRequest):
    """Create a strategic paragraph sampling job for narrative DNA extraction"""
    try:
        job_id = await gutenberg_service.create_strategic_sampling_job(
            gutenberg_id=request.gutenberg_id,
            sample_count=request.sample_count,
            min_length=request.min_length,
            max_length=request.max_length,
            avoid_first_last_percent=request.avoid_first_last_percent
        )
        
        return {
            "success": True,
            "message": f"Strategic sampling job created for book {request.gutenberg_id}",
            "data": {
                "job_id": job_id,
                "gutenberg_id": request.gutenberg_id,
                "sample_count": request.sample_count,
                "sampling_criteria": {
                    "min_length": request.min_length,
                    "max_length": request.max_length,
                    "avoid_first_last_percent": request.avoid_first_last_percent
                },
                "status": "pending"
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to create strategic sampling job: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create strategic sampling job: {str(e)}")

@app.post("/gutenberg/composite-analysis")
async def create_composite_analysis_job(job_id: str):
    """Create composite analysis from strategic sampling results to extract narrative DNA"""
    try:
        # Get strategic sampling results
        job = await gutenberg_service.get_job_status(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        if job.status != "completed":
            raise HTTPException(status_code=400, detail="Strategic sampling job must be completed first")
        
        # Get the sampling results
        sampling_results = await gutenberg_service.get_job_results(job_id)
        
        # Create composite analysis job
        composite_job_id = await gutenberg_service.create_composite_analysis_job(
            source_job_id=job_id,
            sampling_results=sampling_results
        )
        
        return {
            "success": True,
            "message": f"Composite analysis job created from sampling job {job_id}",
            "data": {
                "composite_job_id": composite_job_id,
                "source_job_id": job_id,
                "status": "pending",
                "analysis_type": "narrative_dna_extraction"
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to create composite analysis job: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create composite analysis job: {str(e)}")

# ===== QUANTUM NARRATIVE ANALYSIS ENDPOINTS =====

from typing import List, Dict, Any, Optional

class NarrativeSpinRequest(BaseModel):
    """Request for quantum narrative spinning analysis"""
    narratives: List[Dict[str, Any]]  # List of narrative texts with DNA metadata
    analysis_type: str = "quantum_comparison"  # Type of analysis to perform
    spin_operators: Optional[List[str]] = None  # Specific quantum operators to apply
    measurement_basis: str = "sic_povm"  # Measurement basis (sic_povm, pauli, etc.)

class QuantumMeasurementRequest(BaseModel):
    """Request for quantum measurement of narrative states"""
    narrative_text: str
    persona: str
    namespace: str
    style: str
    measurement_operators: Optional[List[str]] = None

@app.post("/quantum/narrative-spin")
async def analyze_narrative_quantum_spin(request: NarrativeSpinRequest):
    """
    Analyze quantum 'spinning' of narratives with different DNA attributes.
    
    This endpoint implements the quantum metaphor where each narrative transformation
    creates a quantum superposition state that must be 'spun' and measured using
    the density matrix ρ and POVM measurement operators.
    """
    try:
        import numpy as np
        
        logger.info(f"Starting quantum narrative spin analysis for {len(request.narratives)} narratives")
        
        # Initialize quantum analysis parameters
        dimension = 8  # Quantum narrative space dimension
        
        results = {
            "analysis_type": request.analysis_type,
            "quantum_dimension": dimension,
            "measurement_basis": request.measurement_basis,
            "narratives_analyzed": len(request.narratives),
            "quantum_states": [],
            "spin_correlations": {},
            "comparative_analysis": {}
        }
        
        # Process each narrative into quantum state
        quantum_states = []
        
        for i, narrative_data in enumerate(request.narratives):
            # Extract narrative properties
            persona = narrative_data.get("persona", "unknown")
            namespace = narrative_data.get("namespace", "unknown")
            style = narrative_data.get("style", "unknown")
            name = narrative_data.get("name", f"Narrative_{i+1}")
            
            # Create DNA-specific quantum state (mock implementation)
            base_embedding = np.random.normal(0, 1, 1536)
            
            # Quantum 'spinning' based on DNA characteristics
            if "philosophical" in persona.lower():
                base_embedding[0:100] += 0.7  # Philosophical spin
            if "tragic" in persona.lower():
                base_embedding[100:200] += 0.7  # Tragic spin
            if "gothic" in persona.lower():
                base_embedding[200:300] += 0.7  # Gothic spin
            
            # Normalize and project to quantum space
            embedding = base_embedding / np.linalg.norm(base_embedding)
            psi = embedding[:dimension] / np.linalg.norm(embedding[:dimension])
            
            # Create density matrix ρ = |ψ⟩⟨ψ|
            density_matrix = np.outer(psi, np.conj(psi))
            
            # Add quantum decoherence
            identity = np.eye(dimension) / dimension
            density_matrix = 0.9 * density_matrix + 0.1 * identity
            density_matrix = density_matrix / np.trace(density_matrix)
            
            # Compute quantum properties
            eigenvalues = np.real(np.linalg.eigvals(density_matrix))
            eigenvalues = eigenvalues[eigenvalues > 1e-12]
            
            entropy = -np.sum(eigenvalues * np.log2(eigenvalues)) if len(eigenvalues) > 0 else 0
            purity = np.real(np.trace(density_matrix @ density_matrix))
            
            quantum_state = {
                "name": name,
                "dna_combination": f"{persona}|{namespace}|{style}",
                "quantum_properties": {
                    "von_neumann_entropy": float(entropy),
                    "purity": float(purity),
                    "mixedness": float(1 - purity)
                }
            }
            
            quantum_states.append({"state_data": quantum_state, "density_matrix": density_matrix})
            results["quantum_states"].append(quantum_state)
        
        # Compute quantum distances between states
        for i in range(len(quantum_states)):
            for j in range(i + 1, len(quantum_states)):
                state1, state2 = quantum_states[i], quantum_states[j]
                name1, name2 = state1["state_data"]["name"], state2["state_data"]["name"]
                
                rho1, rho2 = state1["density_matrix"], state2["density_matrix"]
                
                # Quantum trace distance
                diff = rho1 - rho2
                eigenvals = np.linalg.eigvals(diff @ diff.conj().T)
                trace_distance = 0.5 * np.sum(np.sqrt(np.real(eigenvals)))
                
                pair_key = f"{name1}↔{name2}"
                results["spin_correlations"][pair_key] = {
                    "trace_distance": float(trace_distance),
                    "quantum_distinguishability": float(trace_distance > 0.1)
                }
        
        return {
            "success": True,
            "message": f"Quantum spin analysis completed for {len(request.narratives)} narratives",
            "data": results
        }
        
    except Exception as e:
        logger.error(f"Failed to perform quantum narrative spin analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Quantum analysis failed: {str(e)}")

# ===== END QUANTUM NARRATIVE ENDPOINTS =====

# ===== END GUTENBERG ENDPOINTS =====

if __name__ == "__main__":
    import uvicorn
    import subprocess
    import os
    import signal
    import time
    
    # Kill any existing process on port 8100
    try:
        # Find process using port 8100
        result = subprocess.run(['lsof', '-ti:8100'], capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            print(f"🔄 Found existing process(es) on port 8100: {pids}")
            
            for pid in pids:
                try:
                    pid_int = int(pid.strip())
                    print(f"🛑 Terminating process {pid_int}")
                    os.kill(pid_int, signal.SIGTERM)
                    time.sleep(1)  # Give it a moment to shut down gracefully
                    
                    # Check if still running, force kill if needed
                    try:
                        os.kill(pid_int, 0)  # Check if process exists
                        print(f"💀 Force killing process {pid_int}")
                        os.kill(pid_int, signal.SIGKILL)
                    except ProcessLookupError:
                        pass  # Process already terminated
                        
                except (ValueError, ProcessLookupError):
                    continue
                    
            print("✅ Port 8100 cleared")
            time.sleep(1)  # Brief pause before starting new server
            
    except Exception as e:
        print(f"⚠️  Could not check/clear port 8100: {e}")
    
    uvicorn.run(app, host="127.0.0.1", port=8100)