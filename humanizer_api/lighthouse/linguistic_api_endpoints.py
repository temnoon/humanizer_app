# API endpoints for the Linguistic Transformation Engine
# Exposing sophisticated namespace/persona/style framework

from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import json
import logging
from datetime import datetime

from linguistic_transformation_engine import (
    LinguisticTransformationEngine,
    LinguisticTransformationManifest,
    NamespaceManifest,
    PersonaManifest,
    StyleManifest,
    PhonotacticAnalyzer,
    StylometricAnalyzer,
    TransformationInference
)

logger = logging.getLogger(__name__)

# Create router
linguistic_router = APIRouter(prefix="/api/linguistic", tags=["Linguistic Transformation"])

# Initialize the engine
engine = LinguisticTransformationEngine()

# Request/Response models
class ManifestCreationRequest(BaseModel):
    original_texts: List[str] = Field(..., description="Original texts before transformation")
    transformed_texts: List[str] = Field(..., description="Texts after transformation")
    manifest_id: str = Field(..., description="Unique identifier for the manifest")
    description: str = Field("", description="Description of the transformation")

class TextAnalysisRequest(BaseModel):
    text: str = Field(..., description="Text to analyze")
    include_stylometrics: bool = Field(True, description="Include detailed stylometric analysis")

class NameGenerationRequest(BaseModel):
    manifest_id: str = Field(..., description="Manifest ID to use for generation")
    count: int = Field(1, description="Number of names to generate", ge=1, le=50)

class ManifestImportRequest(BaseModel):
    manifest_json: str = Field(..., description="JSON string of the manifest to import")

class PhonotacticAnalysisRequest(BaseModel):
    names: List[str] = Field(..., description="List of names to analyze for patterns")

@linguistic_router.post("/manifests/create-from-examples", summary="Create Transformation Manifest from Examples")
async def create_manifest_from_examples(request: ManifestCreationRequest):
    """
    Create a complete linguistic transformation manifest by analyzing examples.
    This implements the reverse-engineering approach described in the theoretical framework.
    """
    try:
        logger.info(f"Creating manifest {request.manifest_id} from {len(request.transformed_texts)} examples")
        
        manifest = engine.create_manifest_from_examples(
            original_texts=request.original_texts,
            transformed_texts=request.transformed_texts,
            manifest_id=request.manifest_id,
            description=request.description
        )
        
        # Return the complete manifest as JSON
        manifest_json = engine.export_manifest_json(request.manifest_id)
        
        return {
            "success": True,
            "manifest_id": request.manifest_id,
            "manifest": json.loads(manifest_json),
            "summary": engine.get_manifest_summary(request.manifest_id),
            "message": f"Successfully created manifest from {len(request.transformed_texts)} examples"
        }
        
    except Exception as e:
        logger.error(f"Failed to create manifest: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create manifest: {str(e)}")

@linguistic_router.get("/manifests", summary="List All Transformation Manifests")
async def list_manifests():
    """Get list of all stored transformation manifests with summaries."""
    try:
        manifest_ids = engine.get_all_manifest_ids()
        manifests = []
        
        for manifest_id in manifest_ids:
            summary = engine.get_manifest_summary(manifest_id)
            manifests.append(summary)
        
        return {
            "success": True,
            "count": len(manifests),
            "manifests": manifests
        }
        
    except Exception as e:
        logger.error(f"Failed to list manifests: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list manifests: {str(e)}")

@linguistic_router.get("/manifests/{manifest_id}", summary="Get Specific Transformation Manifest")
async def get_manifest(manifest_id: str):
    """Get complete details of a specific transformation manifest."""
    try:
        if manifest_id not in engine.manifests:
            raise HTTPException(status_code=404, detail=f"Manifest {manifest_id} not found")
        
        manifest_json = engine.export_manifest_json(manifest_id)
        summary = engine.get_manifest_summary(manifest_id)
        
        return {
            "success": True,
            "manifest_id": manifest_id,
            "manifest": json.loads(manifest_json),
            "summary": summary
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get manifest {manifest_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get manifest: {str(e)}")

@linguistic_router.post("/manifests/import", summary="Import Transformation Manifest from JSON")
async def import_manifest(request: ManifestImportRequest):
    """Import a transformation manifest from JSON data."""
    try:
        manifest_id = engine.import_manifest_json(request.manifest_json)
        summary = engine.get_manifest_summary(manifest_id)
        
        return {
            "success": True,
            "manifest_id": manifest_id,
            "summary": summary,
            "message": f"Successfully imported manifest as {manifest_id}"
        }
        
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON format: {str(e)}")
    except Exception as e:
        logger.error(f"Failed to import manifest: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to import manifest: {str(e)}")

@linguistic_router.post("/manifests/{manifest_id}/export", summary="Export Transformation Manifest as JSON")
async def export_manifest(manifest_id: str):
    """Export a transformation manifest as JSON string."""
    try:
        if manifest_id not in engine.manifests:
            raise HTTPException(status_code=404, detail=f"Manifest {manifest_id} not found")
        
        manifest_json = engine.export_manifest_json(manifest_id)
        
        return {
            "success": True,
            "manifest_id": manifest_id,
            "manifest_json": manifest_json,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to export manifest {manifest_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to export manifest: {str(e)}")

@linguistic_router.post("/analysis/stylometrics", summary="Analyze Text Stylometric Features")
async def analyze_text_stylometrics(request: TextAnalysisRequest):
    """
    Perform comprehensive stylometric analysis of text.
    Returns quantified features for persona and style inference.
    """
    try:
        logger.info(f"Analyzing {len(request.text)} characters of text")
        
        # Perform stylometric analysis
        analysis = engine.analyze_text_stylometrics(request.text)
        
        if request.include_stylometrics:
            # Also infer potential persona and style manifests
            persona = TransformationInference.infer_persona_from_examples([request.text])
            style = TransformationInference.infer_style_from_examples([request.text])
            
            return {
                "success": True,
                "text_length": len(request.text),
                "analysis": analysis,
                "inferred_persona": {
                    "pronoun_usage": persona.pronoun_usage,
                    "modality_usage": persona.modality_usage,
                    "register": persona.register
                },
                "inferred_style": {
                    "avg_sentence_length": style.avg_sentence_length,
                    "formality_score": style.formality_score,
                    "rhetorical_devices": style.rhetorical_devices,
                    "device_frequencies": style.device_frequencies
                }
            }
        else:
            return {
                "success": True,
                "text_length": len(request.text),
                "analysis": analysis
            }
        
    except Exception as e:
        logger.error(f"Failed to analyze text: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze text: {str(e)}")

@linguistic_router.post("/phonotactics/analyze", summary="Analyze Phonotactic Patterns")
async def analyze_phonotactic_patterns(request: PhonotacticAnalysisRequest):
    """
    Analyze a list of names to extract phonotactic patterns and frequencies.
    """
    try:
        logger.info(f"Analyzing phonotactic patterns from {len(request.names)} names")
        
        # Extract phonotactic pattern
        pattern = PhonotacticAnalyzer.extract_pattern(request.names)
        
        # Analyze phoneme frequencies
        phoneme_freqs = PhonotacticAnalyzer.analyze_phoneme_frequencies(request.names)
        
        # Generate example names following the pattern
        example_names = []
        for _ in range(5):
            try:
                name = PhonotacticAnalyzer.generate_name(pattern, phoneme_freqs)
                example_names.append(name)
            except:
                pass
        
        return {
            "success": True,
            "input_names": request.names,
            "phonotactic_pattern": pattern,
            "phoneme_frequencies": phoneme_freqs,
            "example_generated_names": example_names,
            "pattern_analysis": {
                "total_names": len(request.names),
                "unique_phonemes": len(phoneme_freqs),
                "pattern_complexity": len(pattern) if pattern else 0
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to analyze phonotactic patterns: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze patterns: {str(e)}")

@linguistic_router.post("/manifests/{manifest_id}/generate-names", summary="Generate Names Using Manifest")
async def generate_names(manifest_id: str, request: NameGenerationRequest):
    """
    Generate new names following the phonotactic patterns of a specific manifest.
    """
    try:
        if manifest_id not in engine.manifests:
            raise HTTPException(status_code=404, detail=f"Manifest {manifest_id} not found")
        
        logger.info(f"Generating {request.count} names using manifest {manifest_id}")
        
        generated_names = []
        for _ in range(request.count):
            name = engine.generate_name_for_namespace(manifest_id)
            generated_names.append(name)
        
        manifest_summary = engine.get_manifest_summary(manifest_id)
        
        return {
            "success": True,
            "manifest_id": manifest_id,
            "generated_names": generated_names,
            "count": len(generated_names),
            "namespace_info": {
                "phonotactic_pattern": engine.manifests[manifest_id].namespace.phonotactic_pattern,
                "lexicon_seed_size": len(engine.manifests[manifest_id].namespace.lexicon_seed),
                "description": engine.manifests[manifest_id].namespace.description
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate names for manifest {manifest_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate names: {str(e)}")

@linguistic_router.post("/inference/namespace", summary="Infer Namespace from Examples")
async def infer_namespace_from_examples(request: ManifestCreationRequest):
    """
    Infer only the namespace component from transformation examples.
    Useful for focused namespace development.
    """
    try:
        logger.info(f"Inferring namespace from {len(request.transformed_texts)} examples")
        
        namespace = TransformationInference.infer_namespace_from_examples(
            request.original_texts, request.transformed_texts
        )
        namespace.id = request.manifest_id
        namespace.description = request.description
        
        return {
            "success": True,
            "namespace": {
                "id": namespace.id,
                "description": namespace.description,
                "lexicon_seed": namespace.lexicon_seed,
                "phonotactic_pattern": namespace.phonotactic_pattern,
                "mapping_policy": namespace.mapping_policy,
                "phoneme_frequencies": namespace.phoneme_frequencies
            },
            "analysis": {
                "lexicon_size": len(namespace.lexicon_seed),
                "pattern_complexity": len(namespace.phonotactic_pattern),
                "unique_phonemes": len(namespace.phoneme_frequencies)
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to infer namespace: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to infer namespace: {str(e)}")

@linguistic_router.post("/inference/persona", summary="Infer Persona from Examples")
async def infer_persona_from_examples(request: TextAnalysisRequest):
    """
    Infer persona characteristics from text examples.
    """
    try:
        logger.info(f"Inferring persona from text")
        
        persona = TransformationInference.infer_persona_from_examples([request.text])
        
        return {
            "success": True,
            "persona": {
                "label": persona.label,
                "perspective": persona.perspective,
                "register": persona.register,
                "emotional_tone": persona.emotional_tone,
                "pronoun_usage": persona.pronoun_usage,
                "modality_usage": persona.modality_usage,
                "stylistic_markers": persona.stylistic_markers
            },
            "text_length": len(request.text)
        }
        
    except Exception as e:
        logger.error(f"Failed to infer persona: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to infer persona: {str(e)}")

@linguistic_router.post("/inference/style", summary="Infer Style from Examples") 
async def infer_style_from_examples(request: TextAnalysisRequest):
    """
    Infer style characteristics from text examples.
    """
    try:
        logger.info(f"Inferring style from text")
        
        style = TransformationInference.infer_style_from_examples([request.text])
        
        return {
            "success": True,
            "style": {
                "avg_sentence_length": style.avg_sentence_length,
                "sentence_length_std": style.sentence_length_std,
                "rhetorical_devices": style.rhetorical_devices,
                "formality_score": style.formality_score,
                "lexical_sophistication": style.lexical_sophistication,
                "punctuation_density": style.punctuation_density,
                "device_frequencies": style.device_frequencies
            },
            "text_length": len(request.text)
        }
        
    except Exception as e:
        logger.error(f"Failed to infer style: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to infer style: {str(e)}")

@linguistic_router.get("/health", summary="Health Check for Linguistic Engine")
async def health_check():
    """Health check endpoint for the linguistic transformation engine."""
    try:
        # Test basic functionality
        test_analysis = StylometricAnalyzer.analyze_text("This is a test sentence.")
        
        return {
            "status": "healthy",
            "engine_status": "operational",
            "manifest_count": len(engine.manifests),
            "nlp_available": test_analysis.get("error") is None,
            "timestamp": datetime.now().isoformat(),
            "capabilities": [
                "phonotactic_analysis",
                "stylometric_analysis", 
                "manifest_creation",
                "transformation_inference",
                "name_generation"
            ]
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "degraded",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }