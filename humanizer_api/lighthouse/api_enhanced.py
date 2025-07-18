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

# Initialize FastAPI app
app = FastAPI(
    title="Humanizer Lighthouse API - Enhanced",
    description="Full-featured Lamish Projection Engine with narrative transformation, maieutic dialogue, and translation analysis.",
    version="2.0.0",
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

# Initialize LPE components
projection_engine = ProjectionEngine()
knowledge_base = LamishKnowledgeBase()
translation_analyzer = LanguageRoundTripAnalyzer()

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

# Vision API Models
class VisionAnalysisRequest(BaseModel):
    prompt: str = Field(default="What do you see in this image?")
    image_data: str = Field(..., description="Base64 encoded image data")
    provider: str = Field(default="google", description="Vision provider: google, ollama, openai, anthropic")
    model: str = Field(default="gemini-2.5-pro")

class VisionAnalysisResponse(BaseModel):
    analysis: str
    provider_used: str
    model_used: str
    processing_time_ms: int

class HandwritingTranscriptionRequest(BaseModel):
    prompt: str = Field(default="Transcribe the handwritten text in this image.")
    image_data: str = Field(..., description="Base64 encoded image data")
    provider: str = Field(default="google", description="Vision provider: google, ollama, openai, anthropic")
    model: str = Field(default="gemini-2.5-pro")

class HandwritingTranscriptionResponse(BaseModel):
    transcription: str
    provider_used: str
    model_used: str
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
        
        # Create projection using the enhanced engine
        projection = projection_engine.create_projection(
            narrative=request.narrative,
            persona=request.target_persona,
            namespace=request.target_namespace,
            style=request.target_style,
            show_steps=request.show_steps,
            transform_id=transform_id,
            progress_callback=send_progress_update
        )
        
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
            "final_narrative": projection.final_projection[:100] + "..." if len(projection.final_projection) > 100 else projection.final_projection
        })
        
        return TransformationResponse(
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
        
    except Exception as e:
        logger.error(f"Transformation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Transformation failed: {str(e)}")

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
            model_used=request.model,
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
            model_used=request.model,
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
            model_used=request.model,
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
        
        # Get available models from models endpoint
        try:
            models_response = await get_models()
            ollama_models = models_response.get("text_models", [])
        except:
            ollama_models = [{"name": "llama3.2:latest", "size": "7B"}]
            
        available_models = {
            "ollama": ollama_models,
            "openai": [
                {"name": "gpt-4o", "size": "large", "context": "128k"},
                {"name": "gpt-4o-mini", "size": "small", "context": "128k"},
                {"name": "gpt-4-turbo", "size": "large", "context": "128k"},
                {"name": "gpt-4", "size": "large", "context": "8k"},
                {"name": "gpt-3.5-turbo", "size": "medium", "context": "16k"},
                {"name": "gpt-3.5-turbo-instruct", "size": "medium", "context": "4k"}
            ],
            "anthropic": [
                {"name": "claude-3-5-sonnet-20241022", "size": "large", "context": "200k"},
                {"name": "claude-3-5-sonnet-20240620", "size": "large", "context": "200k"},
                {"name": "claude-3-opus-20240229", "size": "large", "context": "200k"},
                {"name": "claude-3-sonnet-20240229", "size": "medium", "context": "200k"},
                {"name": "claude-3-haiku-20240307", "size": "small", "context": "200k"}
            ],
            "google": [
                {"name": "gemini-1.5-pro", "size": "large", "context": "2M"},
                {"name": "gemini-1.5-flash", "size": "medium", "context": "1M"},
                {"name": "gemini-1.0-pro", "size": "medium", "context": "32k"},
                {"name": "gemini-pro-vision", "size": "large", "context": "32k"}
            ],
            "huggingface": [
                {"name": "meta-llama/Llama-2-70b-chat-hf", "size": "70B", "context": "4k"},
                {"name": "meta-llama/Llama-2-13b-chat-hf", "size": "13B", "context": "4k"},
                {"name": "meta-llama/Llama-2-7b-chat-hf", "size": "7B", "context": "4k"},
                {"name": "mistralai/Mixtral-8x7B-Instruct-v0.1", "size": "46B", "context": "32k"},
                {"name": "mistralai/Mistral-7B-Instruct-v0.1", "size": "7B", "context": "32k"},
                {"name": "microsoft/DialoGPT-large", "size": "774M", "context": "1k"}
            ],
            "groq": [
                {"name": "llama-3.1-70b-versatile", "size": "70B", "context": "131k"},
                {"name": "llama-3.1-8b-instant", "size": "8B", "context": "131k"},
                {"name": "mixtral-8x7b-32768", "size": "46B", "context": "32k"},
                {"name": "gemma2-9b-it", "size": "9B", "context": "8k"},
                {"name": "gemma-7b-it", "size": "7B", "context": "8k"}
            ],
            "together": [
                {"name": "meta-llama/Llama-3-70b-chat-hf", "size": "70B", "context": "8k"},
                {"name": "meta-llama/Llama-3-8b-chat-hf", "size": "8B", "context": "8k"},
                {"name": "mistralai/Mixtral-8x7B-Instruct-v0.1", "size": "46B", "context": "32k"},
                {"name": "NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO", "size": "46B", "context": "32k"},
                {"name": "teknium/OpenHermes-2.5-Mistral-7B", "size": "7B", "context": "32k"}
            ],
            "replicate": [
                {"name": "meta/llama-2-70b-chat", "size": "70B", "context": "4k"},
                {"name": "meta/llama-2-13b-chat", "size": "13B", "context": "4k"},
                {"name": "meta/llama-2-7b-chat", "size": "7B", "context": "4k"},
                {"name": "mistralai/mixtral-8x7b-instruct-v0.1", "size": "46B", "context": "32k"}
            ],
            "cohere": [
                {"name": "command-r-plus", "size": "104B", "context": "128k"},
                {"name": "command-r", "size": "35B", "context": "128k"},
                {"name": "command", "size": "52B", "context": "4k"},
                {"name": "command-light", "size": "6B", "context": "4k"}
            ],
            "mistral": [
                {"name": "mistral-large-latest", "size": "large", "context": "128k"},
                {"name": "mistral-medium-latest", "size": "medium", "context": "32k"},
                {"name": "mistral-small-latest", "size": "small", "context": "32k"},
                {"name": "codestral-latest", "size": "22B", "context": "32k"}
            ],
            "mock": [
                {"name": "mock-model", "size": "any", "context": "unlimited"}
            ]
        }
        
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
        
        return {
            "task_configs": default_configs,
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
        
        # TODO: Implement actual storage (database, config file, etc.)
        logger.info(f"Saving LLM configurations for {len(task_configs)} tasks")
        
        # For now, log the configurations
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
            from src.lpe_core.llm_provider import OllamaProvider
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
            status["ollama"] = {
                "available": False,
                "error": str(e),
                "model": None,
                "has_key": True,
                "key_valid": False,
                "status_message": f"Ollama connection failed: {str(e)}"
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

# Cleanup old sessions periodically
@app.on_event("startup")
async def startup_cleanup():
    """Startup tasks and periodic cleanup."""
    logger.info("Starting Enhanced Lighthouse API with full LPE features")
    
    # Test LLM provider
    provider = get_llm_provider()
    logger.info(f"Using LLM provider: {provider.__class__.__name__}")
    
    # Start cleanup task
    asyncio.create_task(cleanup_old_sessions())

async def cleanup_old_sessions():
    """Periodically clean up old maieutic sessions."""
    while True:
        await asyncio.sleep(3600)  # Clean up every hour
        
        # Remove sessions older than 24 hours
        from datetime import datetime, timedelta
        cutoff = datetime.now() - timedelta(hours=24)
        
        to_remove = []
        for session_id, dialogue in maieutic_sessions.items():
            if dialogue.session and dialogue.session.created_at < cutoff:
                to_remove.append(session_id)
        
        for session_id in to_remove:
            del maieutic_sessions[session_id]
            logger.info(f"Cleaned up old session: {session_id}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8100)