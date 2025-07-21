"""
Balanced Transformation API for Humanizer Lighthouse

This module provides FastAPI endpoints for the advanced attribute balancing system,
allowing users to transform narratives with sophisticated template avoidance and
narrative DNA preservation.

Key endpoints:
- /api/balanced/analyze - Analyze attribute combinations for balance
- /api/balanced/transform - Transform with balanced attribute handling
- /api/balanced/extract-dna - Extract narrative DNA for analysis
- /api/balanced/compare - Compare transformation quality
- /api/balanced/stats - Get balancing performance statistics
"""

import json
import logging
import asyncio
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

from advanced_attribute_balancing import (
    AttributeBalancer,
    NarrativeDNAExtractor, 
    NarrativeDNA,
    BalancingResult,
    AttributeSignature,
    AttributeType
)
from balanced_llm_transformer import BalancedLLMTransformer, BalancedProjection

logger = logging.getLogger(__name__)

# Create router
balanced_router = APIRouter(prefix="/api/balanced", tags=["Balanced Transformation"])

# Global instances
balancer = AttributeBalancer()
dna_extractor = NarrativeDNAExtractor()
transformer_cache = {}  # Cache transformers by attribute combination

# Request/Response Models
class AnalyzeBalanceRequest(BaseModel):
    persona: str = Field(..., description="Persona attribute")
    namespace: str = Field(..., description="Namespace attribute") 
    style: str = Field(..., description="Style attribute")
    narrative: Optional[str] = Field(None, description="Optional narrative for context-aware analysis")

class BalanceAnalysisResponse(BaseModel):
    is_balanced: bool
    dominant_attributes: List[str] = []
    template_risk_score: float
    conflicts: List[str] = []
    recommended_adjustments: Dict[str, float] = {}
    preservation_score: float
    narrative_dna: Optional[Dict[str, Any]] = None
    suggestions: List[str] = []

class BalancedTransformRequest(BaseModel):
    narrative: str = Field(..., description="Source narrative to transform")
    persona: str = Field(..., description="Target persona")
    namespace: str = Field(..., description="Target namespace")
    style: str = Field(..., description="Target style")
    show_steps: bool = Field(True, description="Include transformation steps")
    apply_balancing: bool = Field(True, description="Apply balancing techniques")

class BalancedTransformResponse(BaseModel):
    transform_id: str
    original_narrative: str
    transformed_narrative: str
    target_persona: str
    target_namespace: str
    target_style: str
    processing_time_ms: int
    steps: List[Dict[str, Any]] = []
    source_dna: Dict[str, Any]
    final_dna: Dict[str, Any]
    overall_preservation_score: float
    balancing_analysis: Dict[str, Any]
    performance_metrics: Dict[str, Any]

class DNAExtractionRequest(BaseModel):
    narrative: str = Field(..., description="Narrative to analyze")
    include_embeddings: bool = Field(False, description="Include embedding vectors")

class DNAResponse(BaseModel):
    core_entities: List[str]
    relationship_patterns: List[str]
    causal_chains: List[str]
    emotional_trajectory: List[str]
    thematic_elements: List[str]
    narrative_structure: str
    semantic_density: float
    complexity_score: float
    analysis_metadata: Dict[str, Any]

class CompareTransformationsRequest(BaseModel):
    original_narrative: str
    transformation_a: str
    transformation_b: str
    attributes_a: Dict[str, str]
    attributes_b: Dict[str, str]

class ComparisonResponse(BaseModel):
    better_transformation: str  # "a" or "b" or "similar"
    comparison_metrics: Dict[str, float]
    detailed_analysis: Dict[str, Any]
    recommendations: List[str]

@balanced_router.post("/analyze", response_model=BalanceAnalysisResponse)
async def analyze_attribute_balance(request: AnalyzeBalanceRequest):
    """Analyze if attribute combination will produce balanced output."""
    try:
        # Perform balance analysis
        analysis = balancer.analyze_combination(
            request.persona, 
            request.namespace, 
            request.style, 
            request.narrative or ""
        )
        
        # Extract DNA if narrative provided
        narrative_dna_dict = None
        if request.narrative:
            dna = dna_extractor.extract_dna(request.narrative)
            narrative_dna_dict = {
                "core_entities": dna.core_entities,
                "relationship_patterns": dna.relationship_patterns,
                "causal_chains": dna.causal_chains,
                "emotional_trajectory": dna.emotional_trajectory,
                "thematic_elements": dna.thematic_elements,
                "narrative_structure": dna.narrative_structure,
                "semantic_density": dna.semantic_density,
                "complexity_score": dna.complexity_score
            }
        
        # Generate suggestions
        suggestions = _generate_balance_suggestions(analysis, request)
        
        return BalanceAnalysisResponse(
            is_balanced=analysis.is_balanced,
            dominant_attributes=analysis.dominant_attributes,
            template_risk_score=analysis.template_risk_score,
            conflicts=analysis.conflicts,
            recommended_adjustments=analysis.recommended_adjustments,
            preservation_score=analysis.preservation_score,
            narrative_dna=narrative_dna_dict,
            suggestions=suggestions
        )
        
    except Exception as e:
        logger.error(f"Error analyzing attribute balance: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@balanced_router.post("/transform", response_model=BalancedTransformResponse)
async def balanced_transform(request: BalancedTransformRequest):
    """Transform narrative with advanced attribute balancing."""
    try:
        import uuid
        transform_id = str(uuid.uuid4())
        
        logger.info(f"Starting balanced transformation {transform_id}")
        
        # Get or create transformer for this attribute combination
        attr_key = f"{request.persona}:{request.namespace}:{request.style}"
        
        if attr_key not in transformer_cache:
            # Would need to pass actual LLM provider here
            # For now, create with mock for demonstration
            from lpe_core.llm_provider import get_llm_provider
            llm_provider = get_llm_provider()
            
            transformer_cache[attr_key] = BalancedLLMTransformer(
                llm_provider=llm_provider,
                persona=request.persona,
                namespace=request.namespace,
                style=request.style
            )
        
        transformer = transformer_cache[attr_key]
        
        # Execute balanced transformation
        start_time = time.time()
        projection = transformer.transform_with_balancing(
            request.narrative,
            show_steps=request.show_steps
        )
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        # Convert steps to serializable format
        steps_data = []
        if request.show_steps:
            for step in projection.steps:
                step_data = {
                    "name": step.name,
                    "input_snapshot": step.input_snapshot,
                    "output_snapshot": step.output_snapshot,
                    "duration_ms": step.duration_ms,
                    "preservation_score": step.preservation_score,
                    "template_risk_score": step.template_risk_score,
                    "dna_drift_score": step.dna_drift_score,
                    "balancing_applied": step.balancing_applied,
                    "metadata": step.metadata or {}
                }
                steps_data.append(step_data)
        
        # Convert DNA to serializable format
        source_dna_dict = {
            "core_entities": projection.source_dna.core_entities,
            "relationship_patterns": projection.source_dna.relationship_patterns,
            "causal_chains": projection.source_dna.causal_chains,
            "emotional_trajectory": projection.source_dna.emotional_trajectory,
            "thematic_elements": projection.source_dna.thematic_elements,
            "narrative_structure": projection.source_dna.narrative_structure,
            "semantic_density": projection.source_dna.semantic_density,
            "complexity_score": projection.source_dna.complexity_score
        }
        
        final_dna_dict = {
            "core_entities": projection.final_dna.core_entities,
            "relationship_patterns": projection.final_dna.relationship_patterns,
            "causal_chains": projection.final_dna.causal_chains,
            "emotional_trajectory": projection.final_dna.emotional_trajectory,
            "thematic_elements": projection.final_dna.thematic_elements,
            "narrative_structure": projection.final_dna.narrative_structure,
            "semantic_density": projection.final_dna.semantic_density,
            "complexity_score": projection.final_dna.complexity_score
        }
        
        # Convert balancing analysis
        balancing_dict = {
            "is_balanced": projection.balancing_analysis.is_balanced,
            "dominant_attributes": projection.balancing_analysis.dominant_attributes,
            "template_risk_score": projection.balancing_analysis.template_risk_score,
            "conflicts": projection.balancing_analysis.conflicts,
            "recommended_adjustments": projection.balancing_analysis.recommended_adjustments,
            "preservation_score": projection.balancing_analysis.preservation_score
        }
        
        # Get performance metrics
        performance_metrics = transformer.get_performance_stats()
        
        return BalancedTransformResponse(
            transform_id=transform_id,
            original_narrative=request.narrative,
            transformed_narrative=projection.final_projection,
            target_persona=request.persona,
            target_namespace=request.namespace,
            target_style=request.style,
            processing_time_ms=processing_time_ms,
            steps=steps_data,
            source_dna=source_dna_dict,
            final_dna=final_dna_dict,
            overall_preservation_score=projection.overall_preservation_score,
            balancing_analysis=balancing_dict,
            performance_metrics=performance_metrics
        )
        
    except Exception as e:
        logger.error(f"Error in balanced transformation: {e}")
        raise HTTPException(status_code=500, detail=f"Transformation failed: {str(e)}")

@balanced_router.post("/extract-dna", response_model=DNAResponse)
async def extract_narrative_dna(request: DNAExtractionRequest):
    """Extract narrative DNA for analysis."""
    try:
        dna = dna_extractor.extract_dna(request.narrative)
        
        return DNAResponse(
            core_entities=dna.core_entities,
            relationship_patterns=dna.relationship_patterns,
            causal_chains=dna.causal_chains,
            emotional_trajectory=dna.emotional_trajectory,
            thematic_elements=dna.thematic_elements,
            narrative_structure=dna.narrative_structure,
            semantic_density=dna.semantic_density,
            complexity_score=dna.complexity_score,
            analysis_metadata={
                "word_count": len(request.narrative.split()),
                "sentence_count": len(request.narrative.split('.')),
                "paragraph_count": len(request.narrative.split('\n\n')),
                "timestamp": datetime.now().isoformat()
            }
        )
        
    except Exception as e:
        logger.error(f"Error extracting DNA: {e}")
        raise HTTPException(status_code=500, detail=f"DNA extraction failed: {str(e)}")

@balanced_router.post("/compare", response_model=ComparisonResponse)
async def compare_transformations(request: CompareTransformationsRequest):
    """Compare two transformations for quality and preservation."""
    try:
        # Extract DNA from all narratives
        original_dna = dna_extractor.extract_dna(request.original_narrative)
        dna_a = dna_extractor.extract_dna(request.transformation_a)
        dna_b = dna_extractor.extract_dna(request.transformation_b)
        
        # Calculate preservation scores
        preservation_a = _calculate_preservation_similarity(original_dna, dna_a)
        preservation_b = _calculate_preservation_similarity(original_dna, dna_b)
        
        # Analyze template risks
        template_risk_a = _calculate_template_risk(request.transformation_a, request.attributes_a)
        template_risk_b = _calculate_template_risk(request.transformation_b, request.attributes_b)
        
        # Calculate quality metrics
        quality_a = _calculate_narrative_quality(request.transformation_a)
        quality_b = _calculate_narrative_quality(request.transformation_b)
        
        # Determine better transformation
        score_a = preservation_a * 0.4 + (1 - template_risk_a) * 0.3 + quality_a * 0.3
        score_b = preservation_b * 0.4 + (1 - template_risk_b) * 0.3 + quality_b * 0.3
        
        better = "a" if score_a > score_b else "b" if score_b > score_a else "similar"
        
        # Generate recommendations
        recommendations = _generate_comparison_recommendations(
            preservation_a, preservation_b, template_risk_a, template_risk_b, 
            quality_a, quality_b, request.attributes_a, request.attributes_b
        )
        
        return ComparisonResponse(
            better_transformation=better,
            comparison_metrics={
                "preservation_score_a": preservation_a,
                "preservation_score_b": preservation_b,
                "template_risk_a": template_risk_a,
                "template_risk_b": template_risk_b,
                "quality_score_a": quality_a,
                "quality_score_b": quality_b,
                "overall_score_a": score_a,
                "overall_score_b": score_b
            },
            detailed_analysis={
                "original_complexity": original_dna.complexity_score,
                "original_semantic_density": original_dna.semantic_density,
                "transformation_a_complexity": dna_a.complexity_score,
                "transformation_b_complexity": dna_b.complexity_score,
                "entity_preservation_a": len(set(original_dna.core_entities).intersection(set(dna_a.core_entities))) / max(len(original_dna.core_entities), 1),
                "entity_preservation_b": len(set(original_dna.core_entities).intersection(set(dna_b.core_entities))) / max(len(original_dna.core_entities), 1),
                "theme_preservation_a": len(set(original_dna.thematic_elements).intersection(set(dna_a.thematic_elements))) / max(len(original_dna.thematic_elements), 1),
                "theme_preservation_b": len(set(original_dna.thematic_elements).intersection(set(dna_b.thematic_elements))) / max(len(original_dna.thematic_elements), 1)
            },
            recommendations=recommendations
        )
        
    except Exception as e:
        logger.error(f"Error comparing transformations: {e}")
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")

@balanced_router.get("/stats")
async def get_balancing_stats():
    """Get performance statistics for the balancing system."""
    try:
        stats = {
            "transformer_cache_size": len(transformer_cache),
            "total_registered_attributes": len(balancer.attribute_registry),
            "system_status": "operational",
            "timestamp": datetime.now().isoformat()
        }
        
        # Aggregate stats from cached transformers
        if transformer_cache:
            all_preservation_scores = []
            total_transformations = 0
            total_templates_detected = 0
            total_templates_avoided = 0
            
            for transformer in transformer_cache.values():
                transformer_stats = transformer.get_performance_stats()
                all_preservation_scores.extend(transformer_stats.get('preservation_scores', []))
                total_transformations += transformer_stats.get('total_transformations', 0)
                total_templates_detected += transformer_stats.get('templates_detected', 0)
                total_templates_avoided += transformer_stats.get('templates_avoided', 0)
            
            if all_preservation_scores:
                stats.update({
                    "total_transformations": total_transformations,
                    "avg_preservation_score": sum(all_preservation_scores) / len(all_preservation_scores),
                    "min_preservation_score": min(all_preservation_scores),
                    "max_preservation_score": max(all_preservation_scores),
                    "templates_detected": total_templates_detected,
                    "templates_avoided": total_templates_avoided,
                    "template_avoidance_rate": total_templates_avoided / max(total_templates_detected, 1)
                })
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=f"Stats retrieval failed: {str(e)}")

@balanced_router.post("/register-attribute")
async def register_custom_attribute(attribute_data: Dict[str, Any]):
    """Register a new custom attribute signature."""
    try:
        # Create AttributeSignature from data
        signature = AttributeSignature(
            name=attribute_data.get("name"),
            type=AttributeType(attribute_data.get("type")),
            semantic_markers=attribute_data.get("semantic_markers", []),
            syntactic_patterns=attribute_data.get("syntactic_patterns", []),
            lexical_preferences=attribute_data.get("lexical_preferences", []),
            template_phrases=attribute_data.get("template_phrases", []),
            influence_weight=attribute_data.get("influence_weight", 0.5),
            conflict_tags=set(attribute_data.get("conflict_tags", []))
        )
        
        # Register with balancer
        balancer.attribute_registry[signature.name] = signature
        
        logger.info(f"Registered custom attribute: {signature.name}")
        
        return {
            "status": "success",
            "message": f"Attribute '{signature.name}' registered successfully",
            "attribute_summary": {
                "name": signature.name,
                "type": signature.type.value,
                "influence_weight": signature.influence_weight,
                "template_phrases_count": len(signature.template_phrases),
                "conflict_tags": list(signature.conflict_tags)
            }
        }
        
    except Exception as e:
        logger.error(f"Error registering attribute: {e}")
        raise HTTPException(status_code=500, detail=f"Attribute registration failed: {str(e)}")

# Helper functions
def _generate_balance_suggestions(analysis: BalancingResult, request: AnalyzeBalanceRequest) -> List[str]:
    """Generate suggestions for improving attribute balance."""
    suggestions = []
    
    if analysis.template_risk_score > 0.7:
        suggestions.append("High template risk detected. Consider using more neutral or varied attributes.")
    
    if analysis.dominant_attributes:
        suggestions.append(f"Dominant attributes detected: {', '.join(analysis.dominant_attributes)}. Consider reducing their influence weight.")
    
    if analysis.conflicts:
        suggestions.append(f"Conflicting attributes detected: {', '.join(analysis.conflicts)}. These may produce inconsistent results.")
    
    if analysis.preservation_score < 0.6:
        suggestions.append("Low preservation score. This combination may significantly alter the original narrative.")
    
    if not suggestions:
        suggestions.append("Attribute combination appears well-balanced for transformation.")
    
    return suggestions

def _calculate_preservation_similarity(original_dna: NarrativeDNA, transformed_dna: NarrativeDNA) -> float:
    """Calculate preservation similarity between original and transformed DNA."""
    
    # Entity preservation
    original_entities = set(original_dna.core_entities)
    transformed_entities = set(transformed_dna.core_entities)
    entity_similarity = len(original_entities.intersection(transformed_entities)) / max(len(original_entities), 1)
    
    # Theme preservation
    original_themes = set(original_dna.thematic_elements)
    transformed_themes = set(transformed_dna.thematic_elements)
    theme_similarity = len(original_themes.intersection(transformed_themes)) / max(len(original_themes), 1)
    
    # Structural preservation
    structure_similarity = 1.0 if original_dna.narrative_structure == transformed_dna.narrative_structure else 0.7
    
    # Complexity preservation
    complexity_diff = abs(original_dna.complexity_score - transformed_dna.complexity_score)
    complexity_similarity = max(0.0, 1.0 - complexity_diff)
    
    # Weighted average
    return (entity_similarity * 0.3 + theme_similarity * 0.3 + structure_similarity * 0.2 + complexity_similarity * 0.2)

def _calculate_template_risk(narrative: str, attributes: Dict[str, str]) -> float:
    """Calculate template risk for a narrative given its attributes."""
    risk_score = 0.0
    
    # Check for known template phrases
    template_phrases = []
    for attr_name in attributes.values():
        if attr_name in balancer.attribute_registry:
            template_phrases.extend(balancer.attribute_registry[attr_name].template_phrases)
    
    narrative_lower = narrative.lower()
    for phrase in template_phrases:
        if phrase.lower() in narrative_lower:
            risk_score += 0.1
    
    return min(1.0, risk_score)

def _calculate_narrative_quality(narrative: str) -> float:
    """Calculate overall narrative quality score."""
    
    # Length appropriateness
    word_count = len(narrative.split())
    length_score = min(1.0, word_count / 100.0) if word_count < 100 else 1.0
    
    # Sentence variety
    sentences = narrative.split('.')
    if len(sentences) > 1:
        lengths = [len(s.split()) for s in sentences if s.strip()]
        if lengths:
            avg_length = sum(lengths) / len(lengths)
            variety_score = min(1.0, avg_length / 15.0)
        else:
            variety_score = 0.5
    else:
        variety_score = 0.3
    
    # Vocabulary richness
    words = narrative.lower().split()
    unique_words = len(set(words))
    vocab_richness = unique_words / max(len(words), 1)
    
    return (length_score * 0.3 + variety_score * 0.4 + vocab_richness * 0.3)

def _generate_comparison_recommendations(preservation_a: float, preservation_b: float,
                                       template_risk_a: float, template_risk_b: float,
                                       quality_a: float, quality_b: float,
                                       attributes_a: Dict[str, str], attributes_b: Dict[str, str]) -> List[str]:
    """Generate recommendations based on comparison results."""
    recommendations = []
    
    if preservation_a > preservation_b + 0.1:
        recommendations.append("Transformation A better preserves the original narrative structure and content.")
    elif preservation_b > preservation_a + 0.1:
        recommendations.append("Transformation B better preserves the original narrative structure and content.")
    
    if template_risk_a < template_risk_b - 0.1:
        recommendations.append("Transformation A shows less template risk and more natural language patterns.")
    elif template_risk_b < template_risk_a - 0.1:
        recommendations.append("Transformation B shows less template risk and more natural language patterns.")
    
    if quality_a > quality_b + 0.1:
        recommendations.append("Transformation A demonstrates better overall narrative quality.")
    elif quality_b > quality_a + 0.1:
        recommendations.append("Transformation B demonstrates better overall narrative quality.")
    
    if not recommendations:
        recommendations.append("Both transformations show similar quality. Choice may depend on specific use case preferences.")
    
    return recommendations

# Make router available for import
__all__ = ['balanced_router']