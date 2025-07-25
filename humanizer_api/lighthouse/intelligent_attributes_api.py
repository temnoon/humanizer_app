"""
Intelligent Attributes API Integration
=====================================

API endpoints for AI-guided attribute selection and dynamic attribute editing.
Integrates with the existing transformation pipeline.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
import logging
from attribute_intelligence import (
    AttributeIntelligenceEngine, 
    enhance_transformation_with_ai_attributes,
    create_attribute_editor_component_data
)

logger = logging.getLogger(__name__)

# Router for intelligent attributes
intelligent_attr_router = APIRouter(prefix="/api/intelligent-attributes", tags=["intelligent-attributes"])

# Pydantic models
class AttributeAnalysisRequest(BaseModel):
    narrative: str = Field(..., description="Text to analyze for optimal attributes")
    transformation_intent: str = Field(default="enhance", description="Intended transformation type")
    use_llm_analysis: bool = Field(default=True, description="Whether to use LLM for intelligent selection")

class AttributeAnalysisResponse(BaseModel):
    selected_attributes: Dict[str, str]
    confidence: float
    reasoning: str
    alternatives: List[Dict[str, str]]
    semantic_context: List[Any]  # Changed from Dict to List to match actual data
    quantum_analysis: Optional[Dict[str, Any]]
    pipeline_preview: Dict[str, Any]

class AttributeEditRequest(BaseModel):
    current_attributes: Dict[str, str]
    narrative: str
    edit_type: str = Field(..., description="'manual', 'suggest', or 'optimize'")
    target_attribute: Optional[str] = Field(None, description="Specific attribute to modify")
    target_value: Optional[str] = Field(None, description="New value for target attribute")

class AttributeEditResponse(BaseModel):
    updated_attributes: Dict[str, str]
    change_impact: Dict[str, Any]
    confidence: float
    suggestions: List[Dict[str, str]]

class PipelinePreviewRequest(BaseModel):
    attributes: Dict[str, str]
    narrative: str

class PipelinePreviewResponse(BaseModel):
    prompt_components: Dict[str, str]
    estimated_steps: List[Dict[str, Any]]
    processing_time_estimate: str
    quantum_coordinates: Optional[List[float]]
    transformation_trajectory: Dict[str, Any]

# Global engine instance
_ai_engine = None

def get_ai_engine():
    """Get or create the AI engine instance."""
    global _ai_engine
    if _ai_engine is None:
        try:
            # Import quantum engine if available
            quantum_engine = None
            try:
                from narrative_theory import QuantumNarrativeEngine
                quantum_engine = QuantumNarrativeEngine(semantic_dimension=8)
            except Exception as e:
                logger.warning(f"Quantum engine not available: {e}")
            
            _ai_engine = AttributeIntelligenceEngine(quantum_engine=quantum_engine)
            logger.info("Initialized Attribute Intelligence Engine")
        except Exception as e:
            logger.error(f"Failed to initialize AI engine: {e}")
            raise HTTPException(status_code=500, detail="AI engine initialization failed")
    
    return _ai_engine

@intelligent_attr_router.get("/status")
async def get_status():
    """Get status of the intelligent attributes system."""
    try:
        engine = get_ai_engine()
        return {
            "available": True,
            "embedding_model_loaded": engine.embedder is not None,
            "quantum_integration": engine.quantum_engine is not None,
            "semantic_anchors_count": len(engine.anchor_points),
            "attribute_taxonomy_size": {
                "personas": len(engine.attribute_taxonomy.get("persona", [])),
                "namespaces": len(engine.attribute_taxonomy.get("namespace", [])),
                "styles": len(engine.attribute_taxonomy.get("style", []))
            }
        }
    except Exception as e:
        return {
            "available": False,
            "error": str(e)
        }

@intelligent_attr_router.post("/analyze", response_model=AttributeAnalysisResponse)
async def analyze_narrative_for_attributes(request: AttributeAnalysisRequest):
    """
    Analyze narrative and recommend optimal attributes using AI.
    
    This is the main endpoint that replaces manual attribute selection.
    """
    try:
        engine = get_ai_engine()
        
        # Get LLM provider for intelligent analysis
        llm_provider = None
        if request.use_llm_analysis:
            try:
                from lpe_core.llm_provider import get_llm_provider
                llm_provider = get_llm_provider()
                # Create a simple async wrapper for the LLM provider
                class AsyncLLMWrapper:
                    def __init__(self, provider):
                        self.provider = provider
                    async def generate(self, prompt):
                        return self.provider.generate(prompt, max_tokens=500)
                llm_provider = AsyncLLMWrapper(llm_provider)
            except Exception as e:
                logger.warning(f"LLM provider not available: {e}")
        
        # Analyze narrative
        profile = await engine.analyze_narrative_for_attributes(
            request.narrative,
            request.transformation_intent,
            llm_provider
        )
        
        # Get insights for response
        insights = engine.get_attribute_insights(profile)
        
        return AttributeAnalysisResponse(
            selected_attributes={
                "persona": profile.persona,
                "namespace": profile.namespace,
                "style": profile.style
            },
            confidence=profile.confidence,
            reasoning=profile.reasoning,
            alternatives=insights["recommended_alternatives"],
            semantic_context=profile.semantic_neighborhood,
            quantum_analysis={"povm_coordinates": insights.get("quantum_coordinates")} if insights.get("quantum_coordinates") else None,
            pipeline_preview=insights
        )
        
    except Exception as e:
        logger.error(f"Attribute analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@intelligent_attr_router.post("/edit", response_model=AttributeEditResponse)
async def edit_attributes(request: AttributeEditRequest):
    """
    Edit attributes with AI assistance - suggests alternatives and impact analysis.
    """
    try:
        engine = get_ai_engine()
        
        if request.edit_type == "manual":
            # Manual edit - update specific attribute
            updated_attrs = request.current_attributes.copy()
            if request.target_attribute and request.target_value:
                updated_attrs[request.target_attribute] = request.target_value
            
            # Analyze impact of change
            original_profile = await engine.analyze_narrative_for_attributes(
                request.narrative, "current", None
            )
            
            # Re-analyze with new attributes to see impact
            modified_narrative = f"Transform with {updated_attrs['persona']} persona, {updated_attrs['namespace']} namespace, {updated_attrs['style']} style: {request.narrative}"
            new_profile = await engine.analyze_narrative_for_attributes(
                modified_narrative, "modified", None
            )
            
            change_impact = {
                "confidence_change": new_profile.confidence - original_profile.confidence,
                "semantic_shift": "computed_from_embeddings",
                "expected_outcome": "attribute_specific_transformation"
            }
            
        elif request.edit_type == "suggest":
            # AI suggests improvements to current selection
            profile = await engine.analyze_narrative_for_attributes(
                request.narrative, "optimize", None
            )
            updated_attrs = {
                "persona": profile.persona,
                "namespace": profile.namespace,
                "style": profile.style
            }
            change_impact = {
                "improvement_potential": profile.confidence,
                "reasoning": profile.reasoning
            }
            
        elif request.edit_type == "optimize":
            # Full AI optimization
            profile = await engine.analyze_narrative_for_attributes(
                request.narrative, "optimize", None
            )
            updated_attrs = {
                "persona": profile.persona,
                "namespace": profile.namespace,
                "style": profile.style
            }
            change_impact = {
                "optimization_score": profile.confidence,
                "semantic_anchors": len(profile.semantic_neighborhood)
            }
        
        # Get alternative suggestions
        insights = engine.get_attribute_insights(profile if 'profile' in locals() else original_profile)
        
        return AttributeEditResponse(
            updated_attributes=updated_attrs,
            change_impact=change_impact,
            confidence=profile.confidence if 'profile' in locals() else 0.5,
            suggestions=insights["recommended_alternatives"]
        )
        
    except Exception as e:
        logger.error(f"Attribute editing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Edit failed: {str(e)}")

@intelligent_attr_router.post("/pipeline-preview", response_model=PipelinePreviewResponse)
async def preview_transformation_pipeline(request: PipelinePreviewRequest):
    """
    Preview how the pipeline will process the narrative with given attributes.
    Shows prompt construction, steps, and quantum representation.
    """
    try:
        engine = get_ai_engine()
        
        # Generate embedding for quantum coordinates
        if engine.embedder:
            narrative_embedding = engine.embedder.encode(request.narrative)
            
            # Get quantum coordinates if available
            quantum_coords = None
            if engine.quantum_engine:
                povm_coords = engine._generate_povm_coordinates(narrative_embedding, request.attributes)
                quantum_coords = povm_coords.tolist() if povm_coords is not None else None
        else:
            quantum_coords = None
        
        # Construct prompt components (simulate pipeline preview)
        prompt_components = {
            "persona_prompt": f"Adopt the perspective of a {request.attributes['persona']}",
            "namespace_prompt": f"Frame within the {request.attributes['namespace']} domain",
            "style_prompt": f"Express in a {request.attributes['style']} manner",
            "full_system_prompt": f"You are a {request.attributes['persona']} working within the {request.attributes['namespace']} domain. Transform the following narrative while maintaining its essential meaning, expressing it in a {request.attributes['style']} manner."
        }
        
        # Estimated pipeline steps
        estimated_steps = [
            {"step": "Deconstructing narrative", "duration": "0.5-1.0s", "description": "Extract core narrative elements"},
            {"step": "Mapping to namespace", "duration": "0.8-1.2s", "description": f"Translate to {request.attributes['namespace']} context"},
            {"step": "Reconstructing allegory", "duration": "1.0-1.5s", "description": "Rebuild narrative structure"},
            {"step": "Applying style", "duration": "0.7-1.0s", "description": f"Express in {request.attributes['style']} voice"},
            {"step": "Generating reflection", "duration": "0.3-0.5s", "description": "Add contextual insights"}
        ]
        
        # Transformation trajectory in embedding space
        transformation_trajectory = {
            "source_space": "original_narrative_embedding",
            "target_space": f"{request.attributes['persona']}_{request.attributes['namespace']}_{request.attributes['style']}_space",
            "expected_preservation": "0.65-0.85",
            "semantic_drift": "0.25-0.45",
            "quantum_coherence": "maintained" if quantum_coords else "not_computed"
        }
        
        return PipelinePreviewResponse(
            prompt_components=prompt_components,
            estimated_steps=estimated_steps,
            processing_time_estimate="3-5 seconds",
            quantum_coordinates=quantum_coords,
            transformation_trajectory=transformation_trajectory
        )
        
    except Exception as e:
        logger.error(f"Pipeline preview failed: {e}")
        raise HTTPException(status_code=500, detail=f"Preview failed: {str(e)}")

@intelligent_attr_router.get("/taxonomy")
async def get_attribute_taxonomy():
    """Get the full attribute taxonomy with descriptions."""
    try:
        engine = get_ai_engine()
        
        # Add descriptions to the basic taxonomy
        enhanced_taxonomy = {
            "persona": {
                "philosopher": "Deep thinker exploring fundamental questions and wisdom",
                "scientist": "Empirical investigator using systematic analysis", 
                "artist": "Creative expressionist working with beauty and meaning",
                "teacher": "Patient guide sharing knowledge and understanding",
                "storyteller": "Narrative weaver connecting experiences through tales",
                "mystic": "Spiritual seeker exploring transcendent dimensions",
                # Add more as needed...
            },
            "namespace": {
                "philosophical": "Realm of fundamental questions and wisdom traditions",
                "scientific": "Domain of empirical investigation and systematic knowledge",
                "mythological": "Space of archetypal symbols and universal stories",
                "practical": "Context of real-world application and utility",
                "artistic": "Sphere of aesthetic expression and creative exploration",
                # Add more as needed...
            },
            "style": {
                "contemplative": "Thoughtful, reflective, meditative expression",
                "analytical": "Systematic, logical, precise communication",
                "poetic": "Lyrical, metaphorical, rhythmic language",
                "conversational": "Natural, accessible, dialogue-like tone",
                "formal": "Structured, academic, professional presentation",
                # Add more as needed...
            }
        }
        
        return {
            "taxonomy": enhanced_taxonomy,
            "total_combinations": len(enhanced_taxonomy["persona"]) * len(enhanced_taxonomy["namespace"]) * len(enhanced_taxonomy["style"]),
            "semantic_anchors": list(engine.anchor_points.keys()),
            "expansion_capability": "dynamic_via_llm_discovery"
        }
        
    except Exception as e:
        logger.error(f"Taxonomy request failed: {e}")
        raise HTTPException(status_code=500, detail=f"Taxonomy failed: {str(e)}")

@intelligent_attr_router.post("/record-outcome")
async def record_transformation_outcome(
    pattern_id: str,
    source_text: str,
    target_text: str,
    attributes: Dict[str, str],
    metrics: Dict[str, float],
    transformation_type: str = "balanced"
):
    """Record transformation outcome for learning and RAG improvement."""
    try:
        engine = get_ai_engine()
        
        engine.record_transformation_outcome(
            pattern_id, source_text, target_text, 
            attributes, metrics, transformation_type
        )
        
        return {
            "recorded": True,
            "pattern_id": pattern_id,
            "message": "Transformation outcome recorded for RAG learning"
        }
        
    except Exception as e:
        logger.error(f"Recording outcome failed: {e}")
        raise HTTPException(status_code=500, detail=f"Recording failed: {str(e)}")

# Integration helper for existing transformation pipeline
async def get_intelligent_attributes_for_transformation(narrative: str, 
                                                      transformation_intent: str = "enhance") -> Dict[str, str]:
    """
    Helper function to integrate with existing transformation pipeline.
    Returns attributes dict that can be used directly in place of manual selections.
    """
    try:
        engine = get_ai_engine()
        
        # Get LLM provider
        llm_provider = None
        try:
            from lpe_core.llm_provider import get_llm_provider
            llm_provider = get_llm_provider()
        except:
            pass
        
        # Analyze and get attributes
        profile = await engine.analyze_narrative_for_attributes(
            narrative, transformation_intent, llm_provider
        )
        
        return {
            "persona": profile.persona,
            "namespace": profile.namespace,
            "style": profile.style
        }
        
    except Exception as e:
        logger.error(f"Intelligent attribute selection failed: {e}")
        # Fallback to defaults
        return {
            "persona": "philosopher",
            "namespace": "philosophical", 
            "style": "contemplative"
        }