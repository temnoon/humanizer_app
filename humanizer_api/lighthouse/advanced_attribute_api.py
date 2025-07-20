"""
Advanced Attribute API Endpoints
Provides sophisticated attribute generation with negative scoping and batch processing.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Dict, Set, Optional, Any
import asyncio
import logging
from datetime import datetime
import json

from advanced_attribute_system import (
    AdvancedAttributeGenerator, AdvancedAttribute, AttributeType, 
    ScopeType, SemanticConstraint, NoeticPattern
)
from content_scraper import (
    BatchAttributeProcessor, ContentSource, get_default_content_sources
)

# Configure logging
logger = logging.getLogger(__name__)

# Create router
advanced_attr_router = APIRouter(prefix="/api/advanced-attributes", tags=["Advanced Attributes"])

# Request/Response Models
class AttributeGenerationRequest(BaseModel):
    content: str = Field(..., description="Content to analyze for attribute generation")
    target_namespace: Optional[str] = Field(None, description="Target namespace for filtering")
    negative_scope: Optional[List[str]] = Field(None, description="Concepts to exclude/filter")
    include_noetic_analysis: bool = Field(True, description="Include consciousness mapping analysis")
    sophistication_level: int = Field(3, ge=1, le=5, description="Attribute sophistication level (1-5)")

class BatchProcessingRequest(BaseModel):
    sources: Optional[List[str]] = Field(None, description="Content source names to process")
    custom_sources: Optional[List[Dict[str, Any]]] = Field(None, description="Custom content sources")
    negative_scope: Optional[List[str]] = Field(None, description="Concepts to exclude/filter")
    target_namespace: str = Field("Filtered Reality", description="Target namespace name")
    max_content_pieces: int = Field(50, ge=1, le=200, description="Maximum content pieces to process")
    quality_threshold: float = Field(0.7, ge=0.1, le=1.0, description="Minimum content quality threshold")

class NameGenerationRequest(BaseModel):
    concepts: List[str] = Field(..., description="Concepts to generate proxy names for")
    semantic_category: str = Field("neutral", description="Semantic category for name generation")
    avoid_patterns: Optional[List[str]] = Field(None, description="Patterns to avoid in generated names")

class AttributeFilterRequest(BaseModel):
    attributes: List[Dict[str, Any]] = Field(..., description="Attributes to filter")
    negative_scope: List[str] = Field(..., description="Concepts to filter out")
    generate_proxies: bool = Field(True, description="Generate proxy names for filtered concepts")

class NoeticAnalysisRequest(BaseModel):
    content: str = Field(..., description="Content to analyze for consciousness patterns")
    depth_threshold: int = Field(2, ge=1, le=5, description="Minimum consciousness depth to report")

# Global instances
attribute_generator = AdvancedAttributeGenerator()
batch_processor = BatchAttributeProcessor()

# Background task tracking
active_batch_jobs = {}

@advanced_attr_router.post("/generate", summary="Generate Advanced Attributes")
async def generate_advanced_attributes(request: AttributeGenerationRequest):
    """Generate sophisticated attributes with negative scoping and noetic analysis."""
    
    try:
        logger.info(f"Generating advanced attributes for content of length {len(request.content)}")
        
        # Convert negative scope to set
        negative_scope = set(request.negative_scope) if request.negative_scope else set()
        
        # Generate attributes
        attributes = await attribute_generator.generate_from_content(
            content=request.content,
            target_namespace=request.target_namespace,
            negative_scope=negative_scope
        )
        
        # Convert to serializable format
        serializable_attributes = []
        for attr in attributes:
            attr_dict = {
                "id": attr.id,
                "name": attr.name,
                "type": attr.type.value,
                "description": attr.description,
                "content": attr.content,
                "semantic_vector": attr.semantic_vector,
                "conceptual_density": attr.conceptual_density,
                "abstraction_level": attr.abstraction_level,
                "scope_type": attr.scope_type.value,
                "filtered_concepts": list(attr.filtered_concepts),
                "proxy_mappings": attr.proxy_mappings,
                "confidence_score": attr.confidence_score,
                "validation_status": attr.validation_status,
                "created": attr.created,
                "last_refined": attr.last_refined
            }
            
            # Include noetic analysis if requested
            if request.include_noetic_analysis and attr.noetic_patterns:
                attr_dict["noetic_analysis"] = {
                    "consciousness_coherence": attr.consciousness_coherence,
                    "intentional_clarity": attr.intentional_clarity,
                    "pattern_count": len(attr.noetic_patterns),
                    "patterns": [
                        {
                            "intentional_weight": p.intentional_weight,
                            "consciousness_depth": p.consciousness_depth,
                            "meaning_coherence": p.meaning_coherence,
                            "intersubjective_markers": p.intersubjective_markers,
                            "phenomenological_anchors": p.phenomenological_anchors
                        }
                        for p in attr.noetic_patterns
                    ]
                }
            
            serializable_attributes.append(attr_dict)
        
        return {
            "attributes": serializable_attributes,
            "generation_metadata": {
                "content_length": len(request.content),
                "target_namespace": request.target_namespace,
                "negative_scope_size": len(negative_scope),
                "sophistication_level": request.sophistication_level,
                "total_attributes": len(attributes),
                "types_generated": list(set(attr.type.value for attr in attributes)),
                "average_confidence": sum(attr.confidence_score for attr in attributes) / len(attributes) if attributes else 0,
                "generated_at": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error generating advanced attributes: {e}")
        raise HTTPException(status_code=500, detail=f"Attribute generation failed: {str(e)}")

@advanced_attr_router.post("/batch-process", summary="Start Batch Content Processing")
async def start_batch_processing(request: BatchProcessingRequest, background_tasks: BackgroundTasks):
    """Start batch processing of content sources for attribute generation."""
    
    try:
        # Generate unique job ID
        job_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(str(request)) % 10000}"
        
        # Prepare content sources
        if request.custom_sources:
            sources = []
            for custom_source in request.custom_sources:
                source = ContentSource(
                    name=custom_source.get("name", "custom"),
                    base_url=custom_source.get("base_url", ""),
                    content_patterns=custom_source.get("content_patterns", []),
                    quality_threshold=custom_source.get("quality_threshold", request.quality_threshold),
                    rate_limit_delay=custom_source.get("rate_limit_delay", 1.0)
                )
                sources.append(source)
        else:
            # Use default sources
            all_sources = get_default_content_sources()
            if request.sources:
                sources = [s for s in all_sources if s.name in request.sources]
            else:
                sources = all_sources[:2]  # Limit to first 2 sources for safety
        
        # Initialize job tracking
        active_batch_jobs[job_id] = {
            "status": "starting",
            "progress": 0,
            "total_sources": len(sources),
            "processed_sources": 0,
            "attributes_generated": 0,
            "errors": [],
            "started_at": datetime.now().isoformat()
        }
        
        # Start background processing
        background_tasks.add_task(
            process_batch_job,
            job_id,
            sources,
            set(request.negative_scope) if request.negative_scope else set(),
            request.target_namespace,
            request.max_content_pieces
        )
        
        return {
            "job_id": job_id,
            "status": "started",
            "message": f"Batch processing started for {len(sources)} sources",
            "estimated_duration_minutes": len(sources) * 5,  # Rough estimate
            "sources": [s.name for s in sources]
        }
        
    except Exception as e:
        logger.error(f"Error starting batch processing: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start batch processing: {str(e)}")

@advanced_attr_router.get("/batch-status/{job_id}", summary="Get Batch Processing Status")
async def get_batch_status(job_id: str):
    """Get the status of a batch processing job."""
    
    if job_id not in active_batch_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job_info = active_batch_jobs[job_id]
    
    return {
        "job_id": job_id,
        "status": job_info["status"],
        "progress_percentage": job_info["progress"],
        "sources_processed": job_info["processed_sources"],
        "total_sources": job_info["total_sources"],
        "attributes_generated": job_info["attributes_generated"],
        "errors_count": len(job_info["errors"]),
        "started_at": job_info["started_at"],
        "last_updated": datetime.now().isoformat()
    }

@advanced_attr_router.get("/batch-results/{job_id}", summary="Get Batch Processing Results")
async def get_batch_results(job_id: str):
    """Get the results of a completed batch processing job."""
    
    if job_id not in active_batch_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job_info = active_batch_jobs[job_id]
    
    if job_info["status"] != "completed":
        raise HTTPException(status_code=400, detail="Job not yet completed")
    
    return job_info.get("results", {"error": "No results available"})

@advanced_attr_router.post("/generate-names", summary="Generate Semantic Proxy Names")
async def generate_proxy_names(request: NameGenerationRequest):
    """Generate pronounceable proxy names for concepts, avoiding real-world references."""
    
    try:
        name_generator = attribute_generator.name_generator
        
        generated_names = {}
        validation_results = {}
        
        for concept in request.concepts:
            # Generate proxy name
            proxy_name = name_generator.generate_proxy_name(concept, request.semantic_category)
            
            # Validate safety
            is_safe, issues = name_generator.validate_name_safety(proxy_name)
            
            generated_names[concept] = proxy_name
            validation_results[concept] = {
                "is_safe": is_safe,
                "issues": issues,
                "semantic_category": request.semantic_category
            }
        
        return {
            "generated_names": generated_names,
            "validation_results": validation_results,
            "generation_metadata": {
                "semantic_category": request.semantic_category,
                "concepts_processed": len(request.concepts),
                "successful_generations": len([v for v in validation_results.values() if v["is_safe"]]),
                "generated_at": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error generating proxy names: {e}")
        raise HTTPException(status_code=500, detail=f"Name generation failed: {str(e)}")

@advanced_attr_router.post("/filter-attributes", summary="Apply Negative Scoping to Attributes")
async def filter_attributes(request: AttributeFilterRequest):
    """Apply negative scoping and filtering to existing attributes."""
    
    try:
        filtered_attributes = []
        filtering_stats = {
            "total_input": len(request.attributes),
            "concepts_filtered": 0,
            "proxy_names_generated": 0,
            "attributes_modified": 0
        }
        
        for attr_data in request.attributes:
            # Convert to AdvancedAttribute object for processing
            attr = AdvancedAttribute(
                id=attr_data.get("id", ""),
                name=attr_data.get("name", ""),
                type=AttributeType(attr_data.get("type", "persona")),
                description=attr_data.get("description", ""),
                content=attr_data.get("content", "")
            )
            
            # Apply negative scoping
            filtered_attrs = attribute_generator._apply_negative_scoping([attr], set(request.negative_scope))
            
            if filtered_attrs:
                filtered_attr = filtered_attrs[0]
                
                # Check if modifications were made
                if filtered_attr.proxy_mappings:
                    filtering_stats["attributes_modified"] += 1
                    filtering_stats["proxy_names_generated"] += len(filtered_attr.proxy_mappings)
                    filtering_stats["concepts_filtered"] += len(filtered_attr.filtered_concepts)
                
                # Convert back to dict format
                filtered_attr_dict = {
                    "id": filtered_attr.id,
                    "name": filtered_attr.name,
                    "type": filtered_attr.type.value,
                    "description": filtered_attr.description,
                    "content": filtered_attr.content,
                    "scope_type": filtered_attr.scope_type.value,
                    "filtered_concepts": list(filtered_attr.filtered_concepts),
                    "proxy_mappings": filtered_attr.proxy_mappings,
                    "was_modified": bool(filtered_attr.proxy_mappings)
                }
                
                filtered_attributes.append(filtered_attr_dict)
        
        return {
            "filtered_attributes": filtered_attributes,
            "filtering_statistics": filtering_stats,
            "negative_scope": request.negative_scope,
            "processed_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error filtering attributes: {e}")
        raise HTTPException(status_code=500, detail=f"Attribute filtering failed: {str(e)}")

@advanced_attr_router.post("/analyze-noetic", summary="Analyze Consciousness Patterns")
async def analyze_noetic_patterns(request: NoeticAnalysisRequest):
    """Analyze content for consciousness patterns and intentional structures."""
    
    try:
        noetic_analyzer = attribute_generator.noetic_analyzer
        
        # Analyze patterns
        patterns = noetic_analyzer.analyze_noetic_patterns(request.content)
        
        # Filter by depth threshold
        filtered_patterns = [p for p in patterns if p.consciousness_depth >= request.depth_threshold]
        
        # Calculate summary statistics
        if filtered_patterns:
            avg_intentional_weight = sum(p.intentional_weight for p in filtered_patterns) / len(filtered_patterns)
            avg_consciousness_depth = sum(p.consciousness_depth for p in filtered_patterns) / len(filtered_patterns)
            avg_meaning_coherence = sum(p.meaning_coherence for p in filtered_patterns) / len(filtered_patterns)
        else:
            avg_intentional_weight = avg_consciousness_depth = avg_meaning_coherence = 0.0
        
        # Convert patterns to serializable format
        serializable_patterns = []
        for pattern in filtered_patterns:
            serializable_patterns.append({
                "intentional_weight": pattern.intentional_weight,
                "consciousness_depth": pattern.consciousness_depth,
                "meaning_coherence": pattern.meaning_coherence,
                "projection_vector": pattern.projection_vector,
                "intersubjective_markers": pattern.intersubjective_markers,
                "phenomenological_anchors": pattern.phenomenological_anchors
            })
        
        return {
            "noetic_patterns": serializable_patterns,
            "analysis_summary": {
                "total_patterns_detected": len(patterns),
                "patterns_above_threshold": len(filtered_patterns),
                "depth_threshold": request.depth_threshold,
                "average_intentional_weight": avg_intentional_weight,
                "average_consciousness_depth": avg_consciousness_depth,
                "average_meaning_coherence": avg_meaning_coherence,
                "content_length": len(request.content)
            },
            "consciousness_insights": {
                "has_metacognitive_awareness": any(p.consciousness_depth >= 4 for p in filtered_patterns),
                "shows_phenomenological_grounding": any(p.phenomenological_anchors for p in filtered_patterns),
                "demonstrates_intersubjectivity": any(p.intersubjective_markers for p in filtered_patterns),
                "intentional_clarity_level": "high" if avg_intentional_weight > 0.7 else "medium" if avg_intentional_weight > 0.3 else "low"
            },
            "analyzed_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error analyzing noetic patterns: {e}")
        raise HTTPException(status_code=500, detail=f"Noetic analysis failed: {str(e)}")

@advanced_attr_router.get("/sources", summary="Get Available Content Sources")
async def get_content_sources():
    """Get list of available content sources for batch processing."""
    
    sources = get_default_content_sources()
    
    return {
        "sources": [
            {
                "name": source.name,
                "base_url": source.base_url,
                "quality_threshold": source.quality_threshold,
                "rate_limit_delay": source.rate_limit_delay,
                "description": f"High-quality content source for {source.name.replace('_', ' ')}"
            }
            for source in sources
        ],
        "total_sources": len(sources),
        "usage_note": "Sources are rate-limited and respect robots.txt"
    }

# Background task function
async def process_batch_job(job_id: str, sources: List[ContentSource], 
                          negative_scope: Set[str], target_namespace: str, 
                          max_content_pieces: int):
    """Background task to process batch content generation."""
    
    try:
        # Update job status
        active_batch_jobs[job_id]["status"] = "processing"
        
        # Process content
        results = await batch_processor.process_content_batch(
            sources=sources,
            negative_scope=negative_scope,
            target_namespace=target_namespace
        )
        
        # Convert attributes to serializable format
        serializable_attributes = []
        for attr in results["attributes"]:
            serializable_attributes.append({
                "id": attr.id,
                "name": attr.name,
                "type": attr.type.value,
                "description": attr.description,
                "content": attr.content,
                "scope_type": attr.scope_type.value,
                "filtered_concepts": list(attr.filtered_concepts),
                "proxy_mappings": attr.proxy_mappings,
                "confidence_score": attr.confidence_score,
                "source_metadata": attr.usage_contexts,
                "noetic_analysis": {
                    "consciousness_coherence": attr.consciousness_coherence,
                    "intentional_clarity": attr.intentional_clarity,
                    "pattern_count": len(attr.noetic_patterns)
                } if attr.noetic_patterns else None
            })
        
        # Update job with results
        active_batch_jobs[job_id].update({
            "status": "completed",
            "progress": 100,
            "processed_sources": len(sources),
            "attributes_generated": len(results["attributes"]),
            "completed_at": datetime.now().isoformat(),
            "results": {
                "attributes": serializable_attributes,
                "statistics": results["statistics"],
                "report": results["report"],
                "content_summary": {
                    "total_content_pieces": len(results["content"]),
                    "average_quality_score": sum(c.quality_score for c in results["content"]) / len(results["content"]) if results["content"] else 0,
                    "total_word_count": sum(c.word_count for c in results["content"])
                }
            }
        })
        
        logger.info(f"Batch job {job_id} completed successfully with {len(results['attributes'])} attributes")
        
    except Exception as e:
        error_msg = f"Batch job {job_id} failed: {str(e)}"
        logger.error(error_msg)
        
        active_batch_jobs[job_id].update({
            "status": "failed",
            "error": error_msg,
            "failed_at": datetime.now().isoformat()
        })

# Cleanup endpoint for managing job history
@advanced_attr_router.delete("/batch-jobs/{job_id}", summary="Clean Up Batch Job")
async def cleanup_batch_job(job_id: str):
    """Remove a batch job from active tracking."""
    
    if job_id in active_batch_jobs:
        del active_batch_jobs[job_id]
        return {"message": f"Job {job_id} cleaned up successfully"}
    else:
        raise HTTPException(status_code=404, detail="Job not found")

@advanced_attr_router.get("/batch-jobs", summary="List Active Batch Jobs")
async def list_batch_jobs():
    """Get list of all active batch jobs."""
    
    return {
        "active_jobs": list(active_batch_jobs.keys()),
        "job_details": {
            job_id: {
                "status": job_info["status"],
                "progress": job_info["progress"],
                "started_at": job_info["started_at"]
            }
            for job_id, job_info in active_batch_jobs.items()
        },
        "total_active": len(active_batch_jobs)
    }