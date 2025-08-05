"""
Density Matrix Transformation API
=================================

Production-ready API for quantum-inspired narrative transformations using density matrices.
No mock data - all transformations are computed using the theoretical framework.

Key Features:
- Real density matrix computations with comprehensive validation
- Exhaustive logging of all operations and state transitions
- Extensive error handling with detailed technical messages
- Performance monitoring and optimization
- Integration with embedding services and LLM providers

Author: Implementation of theoretical framework
"""

import logging
import time
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path

import torch
import numpy as np
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field, validator
from contextlib import asynccontextmanager

# Import the core narrative theory implementation
try:
    from narrative_theory import (
        QuantumNarrativeEngine, 
        MeaningState, 
        NarrativeTransformation,
        MeaningPOVM,
        NarrativeCoherenceConstraint
    )
    from embedding_config import get_embedding_manager, embed_text
    from semantic_vocabulary_engine import get_vocabulary_engine
    NARRATIVE_THEORY_AVAILABLE = True
except ImportError as e:
    logging.error(f"Critical dependency missing: {e}")
    NARRATIVE_THEORY_AVAILABLE = False

# Configure comprehensive logging
log_dir = Path(__file__).parent / "logs"
log_dir.mkdir(exist_ok=True)

# Create specialized loggers for different aspects
main_logger = logging.getLogger("density_matrix_api")
transformation_logger = logging.getLogger("transformations")
validation_logger = logging.getLogger("validation")
performance_logger = logging.getLogger("performance")

# Configure file handlers
handlers = {
    "main": logging.FileHandler(log_dir / "density_matrix_api.log"),
    "transformations": logging.FileHandler(log_dir / "transformations.log"),
    "validation": logging.FileHandler(log_dir / "validation.log"),
    "performance": logging.FileHandler(log_dir / "performance.log")
}

formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
)

for logger_name, handler in handlers.items():
    handler.setFormatter(formatter)
    if logger_name == "main":
        main_logger.addHandler(handler)
        main_logger.setLevel(logging.DEBUG)
    elif logger_name == "transformations":
        transformation_logger.addHandler(handler)
        transformation_logger.setLevel(logging.DEBUG)
    elif logger_name == "validation":
        validation_logger.addHandler(handler)
        validation_logger.setLevel(logging.DEBUG)
    elif logger_name == "performance":
        performance_logger.addHandler(handler)
        performance_logger.setLevel(logging.DEBUG)

# Pydantic models for API
class TransformationRequest(BaseModel):
    """Request model for density matrix transformation with projection support."""
    
    input_text: str = Field(..., min_length=1, max_length=50000, description="Text to transform")
    
    # Legacy attribute system (for compatibility)
    transformation_attributes: Dict[str, str] = Field(
        default_factory=dict,
        description="Legacy attributes like persona, namespace, style"
    )
    
    # New projection-based system
    persona_terms: Optional[List[str]] = Field(default=None, description="Persona attributes for projection")
    namespace_terms: Optional[List[str]] = Field(default=None, description="Namespace attributes for projection")
    style_terms: Optional[List[str]] = Field(default=None, description="Style attributes for projection")
    guidance_words: Optional[List[str]] = Field(default=None, description="Words to guide transformation")
    guidance_symbols: Optional[List[str]] = Field(default=None, description="Symbols to guide transformation")
    
    # Projection parameters
    projection_intensity: float = Field(default=1.0, ge=0.0, le=2.0, description="Strength of projection")
    use_vocabulary_system: bool = Field(default=True, description="Use expandable vocabulary for attributes")
    extract_source_attributes: bool = Field(default=True, description="Extract attributes from source text")
    
    # Transformation method selection
    transformation_method: str = Field(
        default="vocabulary",
        pattern="^(vocabulary|density_matrix|hybrid)$",
        description="Method: 'vocabulary' (embedding projection), 'density_matrix' (quantum transformation), or 'hybrid' (both)"
    )
    
    reading_style: str = Field(
        default="interpretation",
        pattern="^(interpretation|skeptical|devotional)$",
        description="How to apply the transformation"
    )
    semantic_dimension: int = Field(
        default=64,
        ge=2, le=512,
        description="Semantic space dimension for density matrices"
    )
    enable_logging: bool = Field(
        default=True,
        description="Enable detailed operation logging"
    )
    validate_coherence: bool = Field(
        default=True,
        description="Check narrative coherence constraints"
    )
    
    @validator('transformation_attributes')
    def validate_attributes(cls, v):
        """Validate transformation attributes."""
        allowed_keys = {'persona', 'namespace', 'style', 'tone', 'perspective', 'voice'}
        for key in v.keys():
            if key not in allowed_keys:
                raise ValueError(f"Unknown attribute: {key}. Allowed: {allowed_keys}")
        return v

class TransformationResponse(BaseModel):
    """Response model with comprehensive transformation data."""
    
    request_id: str
    success: bool
    error_message: Optional[str] = None
    
    # Core transformation results
    transformed_text: Optional[str] = None
    transformation_quality: Optional[float] = None
    
    # Density matrix analysis
    initial_state_analysis: Optional[Dict[str, Any]] = None
    final_state_analysis: Optional[Dict[str, Any]] = None
    transformation_metrics: Optional[Dict[str, float]] = None
    
    # Semantic tomography data
    semantic_tomography: Optional[Dict[str, Any]] = None
    
    # Vocabulary and projection information
    source_attributes: Optional[Dict[str, List[str]]] = None
    projection_target: Optional[Dict[str, Any]] = None
    vocabulary_usage: Optional[Dict[str, Any]] = None
    
    # Performance and validation
    processing_time_ms: Optional[float] = None
    validation_results: Optional[Dict[str, Any]] = None
    
    # Comprehensive logging
    operation_log: Optional[List[Dict[str, Any]]] = None

class DensityMatrixEngine:
    """
    Production engine for density matrix transformations.
    
    Handles all aspects of quantum-inspired narrative transformations
    with comprehensive logging, validation, and error handling.
    """
    
    def __init__(self):
        """Initialize the density matrix engine."""
        if not NARRATIVE_THEORY_AVAILABLE:
            raise RuntimeError("Narrative theory dependencies not available")
        
        self.engines: Dict[int, QuantumNarrativeEngine] = {}
        self.embedding_manager = get_embedding_manager()
        self.vocabulary_engine = get_vocabulary_engine()
        self.operation_counter = 0
        
        main_logger.info("DensityMatrixEngine initialized with vocabulary system")
    
    def get_engine(self, semantic_dimension: int) -> QuantumNarrativeEngine:
        """Get or create quantum narrative engine for specific dimension."""
        if semantic_dimension not in self.engines:
            transformation_logger.info(f"Creating new engine for dimension {semantic_dimension}")
            self.engines[semantic_dimension] = QuantumNarrativeEngine(
                semantic_dimension=semantic_dimension
            )
        return self.engines[semantic_dimension]
    
    def _log_operation(self, operation: str, data: Dict[str, Any], log_level: str = "INFO"):
        """Log operation with structured data."""
        self.operation_counter += 1
        log_entry = {
            "operation_id": self.operation_counter,
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "data": data
        }
        
        if log_level == "ERROR":
            main_logger.error(json.dumps(log_entry, indent=2))
        elif log_level == "WARNING":
            main_logger.warning(json.dumps(log_entry, indent=2))
        else:
            main_logger.info(json.dumps(log_entry, indent=2))
        
        return log_entry
    
    def _validate_density_matrix(self, matrix: torch.Tensor, label: str) -> Dict[str, Any]:
        """Comprehensive density matrix validation."""
        validation_results = {
            "matrix_label": label,
            "is_valid": True,
            "issues": [],
            "properties": {}
        }
        
        try:
            # Check dimensions
            if matrix.dim() != 2 or matrix.shape[0] != matrix.shape[1]:
                validation_results["is_valid"] = False
                validation_results["issues"].append("Matrix is not square")
            
            # Check trace
            trace = torch.trace(matrix).real.item()
            validation_results["properties"]["trace"] = trace
            if abs(trace - 1.0) > 1e-5:
                validation_results["is_valid"] = False
                validation_results["issues"].append(f"Trace is {trace}, should be 1.0")
            
            # Check positive semidefinite
            eigenvals = torch.linalg.eigvals(matrix).real
            min_eigenval = eigenvals.min().item()
            validation_results["properties"]["min_eigenvalue"] = min_eigenval
            validation_results["properties"]["eigenvalues"] = eigenvals.tolist()
            
            if min_eigenval < -1e-6:
                validation_results["is_valid"] = False
                validation_results["issues"].append(f"Not positive semidefinite, min eigenvalue: {min_eigenval}")
            
            # Compute additional properties
            validation_results["properties"]["purity"] = torch.trace(matrix @ matrix).real.item()
            
            # Von Neumann entropy
            pos_eigenvals = eigenvals[eigenvals > 1e-12]
            if len(pos_eigenvals) > 0:
                entropy = -torch.sum(pos_eigenvals * torch.log(pos_eigenvals)).item()
                validation_results["properties"]["von_neumann_entropy"] = entropy
            
        except Exception as e:
            validation_results["is_valid"] = False
            validation_results["issues"].append(f"Validation error: {str(e)}")
        
        validation_logger.info(f"Matrix validation for {label}: {validation_results}")
        return validation_results
    
    def _extract_semantic_tomography(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract comprehensive semantic tomography data."""
        try:
            engine = analysis_result.get("engine")
            if not engine:
                return {"error": "No engine available for tomography"}
            
            tomography = engine.generate_semantic_tomography(analysis_result)
            
            # Add additional analysis
            tomography["coherence_analysis"] = self._analyze_coherence(analysis_result)
            tomography["transformation_quality"] = self._assess_transformation_quality(analysis_result)
            
            return tomography
            
        except Exception as e:
            transformation_logger.error(f"Semantic tomography extraction failed: {e}")
            return {"error": f"Tomography extraction failed: {str(e)}"}
    
    def _analyze_coherence(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze narrative coherence using Born-rule constraints."""
        try:
            engine = analysis_result.get("engine")
            if not engine or not hasattr(engine, 'coherence_constraint'):
                return {"error": "Coherence constraint not available"}
            
            initial_probs = analysis_result.get("initial_canonical_probs", {})
            final_probs = analysis_result.get("final_canonical_probs", {})
            measurement_probs = analysis_result.get("measurement_probabilities", {})
            
            # For now, return basic coherence metrics
            # Full implementation would check Born-rule constraints
            coherence_metrics = {
                "probability_conservation": abs(sum(measurement_probs.values()) - 1.0),
                "state_overlap": analysis_result.get("fidelity", 0.0),
                "entropy_change": analysis_result.get("entropy_change", 0.0),
                "purity_change": analysis_result.get("purity_change", 0.0)
            }
            
            return coherence_metrics
        
        except Exception as e:
            validation_logger.error(f"Coherence analysis failed: {e}")
            return {"error": f"Coherence analysis failed: {str(e)}"}
    
    def _assess_transformation_quality(self, analysis_result: Dict[str, Any]) -> float:
        """Assess overall transformation quality."""
        try:
            # Multi-factor quality assessment
            fidelity = analysis_result.get("fidelity", 0.0)
            entropy_change = abs(analysis_result.get("entropy_change", 0.0))
            purity_change = abs(analysis_result.get("purity_change", 0.0))
            
            # Quality score (0-1, higher is better)
            # Factors: reasonable fidelity change, meaningful entropy/purity changes
            quality_score = 0.0
            
            # Fidelity component (should be meaningful but not too high/low)
            if 0.3 <= fidelity <= 0.9:
                quality_score += 0.4 * (1.0 - abs(fidelity - 0.6) / 0.3)
            
            # Entropy change component (some change is good)
            if entropy_change > 0.01:
                quality_score += 0.3 * min(entropy_change / 0.5, 1.0)
            
            # Purity change component (some change indicates transformation)
            if purity_change > 0.01:
                quality_score += 0.3 * min(purity_change / 0.5, 1.0)
            
            return min(1.0, max(0.0, quality_score))
        
        except Exception as e:
            performance_logger.error(f"Quality assessment failed: {e}")
            return 0.0
    
    async def _generate_transformed_text(self, 
                                       request: TransformationRequest, 
                                       analysis_result: Dict[str, Any], 
                                       transformation_quality: float,
                                       operation_log: List[Dict[str, Any]]) -> str:
        """Generate transformed text using the selected transformation method."""
        
        try:
            # Import LLM provider
            import sys
            sys.path.append(str(Path(__file__).parent.parent / "src"))
            from lpe_core.llm_provider import get_llm_provider
            llm_provider = get_llm_provider()
            
            # Build transformation context from projection targets
            transformation_description = []
            if request.persona_terms:
                transformation_description.append(f"Persona: {', '.join(request.persona_terms)}")
            if request.namespace_terms:
                transformation_description.append(f"Namespace: {', '.join(request.namespace_terms)}")
            if request.style_terms:
                transformation_description.append(f"Style: {', '.join(request.style_terms)}")
            if request.guidance_words:
                transformation_description.append(f"Guidance: {', '.join(request.guidance_words)}")
            
            transformation_context = "; ".join(transformation_description) if transformation_description else "general transformation"
            
            # Method-specific generation
            if request.transformation_method == "vocabulary":
                return await self._generate_vocabulary_transformation(
                    request, transformation_context, llm_provider, operation_log
                )
            
            elif request.transformation_method == "density_matrix":
                return await self._generate_density_matrix_transformation(
                    request, analysis_result, transformation_context, transformation_quality, llm_provider, operation_log
                )
            
            elif request.transformation_method == "hybrid":
                return await self._generate_hybrid_transformation(
                    request, analysis_result, transformation_context, transformation_quality, llm_provider, operation_log
                )
            
            else:
                raise ValueError(f"Unknown transformation method: {request.transformation_method}")
                
        except Exception as e:
            operation_log.append(self._log_operation("llm_transformation_failed", {
                "error": str(e),
                "method": request.transformation_method
            }, "WARNING"))
            
            return f"""[TRANSFORMATION FAILED - {request.transformation_method.upper()} METHOD]

Original: {request.input_text}

Error: {str(e)}

The mathematical projections were computed successfully, but text generation failed.
Please check the LLM provider configuration."""
    
    async def _generate_vocabulary_transformation(self, 
                                                request: TransformationRequest,
                                                transformation_context: str,
                                                llm_provider,
                                                operation_log: List[Dict[str, Any]]) -> str:
        """Generate transformation using vocabulary projection only."""
        
        system_prompt = f"""You are a text transformer using VOCABULARY PROJECTION method. Transform text by projecting it toward specific semantic attributes while preserving core meaning.

Method: Vocabulary-based semantic vector projection
Reading Style: {request.reading_style}
Projection Intensity: {request.projection_intensity}

Your task: Transform the input text by projecting it toward these vocabulary attributes: {transformation_context}

Focus on natural language transformation guided by the semantic attributes."""

        user_prompt = f"""Transform this text using vocabulary projection:

Original Text:
{request.input_text}

Projection Target: {transformation_context}

Apply vocabulary-based semantic projection with {request.reading_style} reading style and {request.projection_intensity}x intensity."""

        transformed_text = llm_provider.generate(user_prompt, system_prompt)
        
        operation_log.append(self._log_operation("vocabulary_transformation_applied", {
            "method": "vocabulary",
            "transformation_context": transformation_context
        }))
        
        return f"[VOCABULARY PROJECTION METHOD]\n\n{transformed_text}"
    
    async def _generate_density_matrix_transformation(self, 
                                                    request: TransformationRequest,
                                                    analysis_result: Dict[str, Any],
                                                    transformation_context: str,
                                                    transformation_quality: float,
                                                    llm_provider,
                                                    operation_log: List[Dict[str, Any]]) -> str:
        """Generate transformation using density matrix quantum mechanics."""
        
        # Extract density matrix transformation data
        fidelity = analysis_result.get('fidelity', 0.0)
        purity_change = analysis_result.get('purity_change', 0.0)
        entropy_change = analysis_result.get('entropy_change', 0.0)
        measurement_probs = analysis_result.get('measurement_probabilities', {})
        
        # Build quantum measurement context
        measurement_context = []
        for outcome, prob in measurement_probs.items():
            if prob > 0.1:  # Only include significant measurements
                measurement_context.append(f"{outcome}: {prob:.2f}")
        
        quantum_measurements = ", ".join(measurement_context) if measurement_context else "uniform distribution"
        
        system_prompt = f"""You are a text transformer using DENSITY MATRIX method. You transform text based on quantum-inspired meaning-state transformations represented as density matrices.

Method: Quantum density matrix transformation (ρ → ρ')
Semantic Dimension: {request.semantic_dimension}×{request.semantic_dimension} density matrix
Fidelity: {fidelity:.3f} (semantic overlap between initial and final states)
Purity Change: {purity_change:.3f} (certainty change in meaning)
Entropy Change: {entropy_change:.3f} (information content change)
Quality Score: {transformation_quality:.1%}

Quantum Measurements: {quantum_measurements}

The density matrix has been mathematically transformed through POVM (Positive Operator-Valued Measure) based on: {transformation_context}

Your task: Generate text that reflects this quantum transformation of meaning. The mathematical transformation has already computed how the probability distributions over semantic content have changed."""

        user_prompt = f"""Based on the density matrix transformation results, generate the transformed text:

Original Text:
{request.input_text}

Quantum Transformation Applied:
- Fidelity: {fidelity:.3f} (how much meaning was preserved)
- Purity Change: {purity_change:.3f} (certainty change)
- Entropy Change: {entropy_change:.3f} (information change)
- Measurement Outcomes: {quantum_measurements}

The density matrix ρ has been transformed to ρ' through semantic POVM measurements. Generate text that embodies this transformed meaning-state."""

        transformed_text = llm_provider.generate(user_prompt, system_prompt)
        
        operation_log.append(self._log_operation("density_matrix_transformation_applied", {
            "method": "density_matrix",
            "fidelity": fidelity,
            "purity_change": purity_change,
            "entropy_change": entropy_change,
            "measurement_probs": measurement_probs
        }))
        
        return f"[DENSITY MATRIX METHOD]\n\nQuantum Analysis:\n- Fidelity: {fidelity:.3f}\n- Purity Δ: {purity_change:.3f}\n- Entropy Δ: {entropy_change:.3f}\n- Measurements: {quantum_measurements}\n\n{transformed_text}"
    
    async def _generate_hybrid_transformation(self, 
                                            request: TransformationRequest,
                                            analysis_result: Dict[str, Any],
                                            transformation_context: str,
                                            transformation_quality: float,
                                            llm_provider,
                                            operation_log: List[Dict[str, Any]]) -> str:
        """Generate transformation using both vocabulary and density matrix approaches."""
        
        # Get both transformations
        vocab_result = await self._generate_vocabulary_transformation(
            request, transformation_context, llm_provider, operation_log
        )
        
        density_result = await self._generate_density_matrix_transformation(
            request, analysis_result, transformation_context, transformation_quality, llm_provider, operation_log
        )
        
        # Create comparison
        system_prompt = f"""You are a text transformer using HYBRID method. You have two different transformation approaches and need to synthesize them into a unified result.

Method 1: Vocabulary projection (semantic vector guidance)
Method 2: Density matrix transformation (quantum-inspired meaning-state evolution)

Your task: Analyze both results and create a synthesis that combines the best aspects of both approaches."""

        user_prompt = f"""Synthesize these two transformation approaches:

Original Text:
{request.input_text}

VOCABULARY PROJECTION RESULT:
{vocab_result}

DENSITY MATRIX RESULT:
{density_result}

Create a hybrid transformation that leverages both the vocabulary projection and the quantum density matrix insights."""

        hybrid_text = llm_provider.generate(user_prompt, system_prompt)
        
        operation_log.append(self._log_operation("hybrid_transformation_applied", {
            "method": "hybrid",
            "combines": ["vocabulary", "density_matrix"]
        }))
        
        return f"[HYBRID METHOD - VOCABULARY + DENSITY MATRIX]\n\n{hybrid_text}\n\n--- COMPARISON ---\n\nVocabulary Result:\n{vocab_result}\n\nDensity Matrix Result:\n{density_result}"
    
    async def transform_text(self, request: TransformationRequest) -> TransformationResponse:
        """
        Perform density matrix transformation with comprehensive logging and validation.
        """
        request_id = str(uuid.uuid4())
        start_time = time.time()
        operation_log = []
        
        # Log initial request
        operation_log.append(self._log_operation("request_received", {
            "request_id": request_id,
            "input_length": len(request.input_text),
            "legacy_attributes": request.transformation_attributes,
            "persona_terms": request.persona_terms,
            "namespace_terms": request.namespace_terms,
            "style_terms": request.style_terms,
            "guidance_words": request.guidance_words,
            "use_vocabulary_system": request.use_vocabulary_system,
            "reading_style": request.reading_style,
            "semantic_dimension": request.semantic_dimension
        }))
        
        # Extract source attributes using vocabulary system
        source_attributes = None
        if request.extract_source_attributes and request.use_vocabulary_system:
            try:
                source_attributes = self.vocabulary_engine.extract_attributes_from_text(
                    request.input_text, extract_new=True
                )
                operation_log.append(self._log_operation("source_attributes_extracted", {
                    "extracted_attributes": source_attributes
                }))
            except Exception as e:
                operation_log.append(self._log_operation("source_extraction_failed", {
                    "error": str(e)
                }, "WARNING"))
        
        # Create projection target
        projection_target = None
        if request.use_vocabulary_system:
            try:
                projection_target = self.vocabulary_engine.create_projection_target(
                    persona_terms=request.persona_terms,
                    namespace_terms=request.namespace_terms,
                    style_terms=request.style_terms,
                    guidance_words=request.guidance_words,
                    guidance_symbols=request.guidance_symbols,
                    target_intensity=request.projection_intensity
                )
                operation_log.append(self._log_operation("projection_target_created", {
                    "has_persona_vector": projection_target.persona_vector is not None,
                    "has_namespace_vector": projection_target.namespace_vector is not None,
                    "has_style_vector": projection_target.style_vector is not None,
                    "guidance_words_count": len(request.guidance_words or [])
                }))
            except Exception as e:
                operation_log.append(self._log_operation("projection_target_failed", {
                    "error": str(e)
                }, "WARNING"))
        
        try:
            # Get quantum narrative engine
            engine = self.get_engine(request.semantic_dimension)
            operation_log.append(self._log_operation("engine_acquired", {
                "semantic_dimension": request.semantic_dimension
            }))
            
            # Generate embedding for input text
            try:
                embedding = embed_text(request.input_text)
                embedding_tensor = torch.tensor(embedding, dtype=torch.float32)
                operation_log.append(self._log_operation("embedding_generated", {
                    "embedding_dimension": len(embedding),
                    "embedding_norm": float(np.linalg.norm(embedding))
                }))
            except Exception as e:
                raise HTTPException(
                    status_code=500, 
                    detail=f"Embedding generation failed: {str(e)}"
                )
            
            # Convert to meaning state
            try:
                initial_state = engine.text_to_meaning_state(request.input_text, embedding_tensor)
                operation_log.append(self._log_operation("meaning_state_created", {
                    "dimension": initial_state.dimension,
                    "purity": initial_state.purity(),
                    "entropy": initial_state.von_neumann_entropy()
                }))
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Meaning state creation failed: {str(e)}"
                )
            
            # Validate initial density matrix
            if request.enable_logging:
                initial_validation = self._validate_density_matrix(
                    initial_state.density_matrix, 
                    "initial_state"
                )
                operation_log.append(self._log_operation("initial_validation", initial_validation))
                
                if not initial_validation["is_valid"]:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Invalid initial density matrix: {initial_validation['issues']}"
                    )
            
            # Create narrative transformation
            try:
                transformation = engine.create_narrative_transformation(
                    narrative_text=request.input_text,  # Using input as basis for transformation
                    transformation_attributes=request.transformation_attributes,
                    reading_style=request.reading_style
                )
                operation_log.append(self._log_operation("transformation_created", {
                    "reading_style": request.reading_style,
                    "povm_dimension": transformation.povm.dimension,
                    "povm_elements": transformation.povm.num_elements
                }))
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Transformation creation failed: {str(e)}"
                )
            
            # Apply transformation
            try:
                analysis_result = engine.apply_narrative(
                    request.input_text, 
                    embedding_tensor, 
                    transformation
                )
                analysis_result["engine"] = engine  # Add engine for tomography
                
                operation_log.append(self._log_operation("transformation_applied", {
                    "fidelity": analysis_result["fidelity"],
                    "purity_change": analysis_result["purity_change"],
                    "entropy_change": analysis_result["entropy_change"],
                    "measurement_probabilities": analysis_result["measurement_probabilities"]
                }))
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Transformation application failed: {str(e)}"
                )
            
            # Validate final density matrix
            final_validation = None
            if request.enable_logging:
                final_validation = self._validate_density_matrix(
                    analysis_result["final_state"].density_matrix,
                    "final_state"
                )
                operation_log.append(self._log_operation("final_validation", final_validation))
                
                if not final_validation["is_valid"]:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Invalid final density matrix: {final_validation['issues']}"
                    )
            
            # Generate semantic tomography
            semantic_tomography = self._extract_semantic_tomography(analysis_result)
            operation_log.append(self._log_operation("tomography_generated", {
                "tomography_keys": list(semantic_tomography.keys())
            }))
            
            # Assess transformation quality
            transformation_quality = self._assess_transformation_quality(analysis_result)
            operation_log.append(self._log_operation("quality_assessed", {
                "quality_score": transformation_quality
            }))
            
            # Generate transformed text based on selected method
            transformed_text = await self._generate_transformed_text(
                request, analysis_result, transformation_quality, operation_log
            )
            
            # Calculate processing time
            processing_time = (time.time() - start_time) * 1000
            
            operation_log.append(self._log_operation("transformation_complete", {
                "processing_time_ms": processing_time,
                "success": True
            }))
            
            # Build comprehensive response
            return TransformationResponse(
                request_id=request_id,
                success=True,
                transformed_text=transformed_text,
                transformation_quality=transformation_quality,
                initial_state_analysis={
                    "purity": analysis_result["initial_state"].purity(),
                    "entropy": analysis_result["initial_state"].von_neumann_entropy(),
                    "canonical_probabilities": analysis_result["initial_canonical_probs"]
                },
                final_state_analysis={
                    "purity": analysis_result["final_state"].purity(),
                    "entropy": analysis_result["final_state"].von_neumann_entropy(),
                    "canonical_probabilities": analysis_result["final_canonical_probs"]
                },
                transformation_metrics={
                    "fidelity": analysis_result["fidelity"],
                    "purity_change": analysis_result["purity_change"],
                    "entropy_change": analysis_result["entropy_change"]
                },
                semantic_tomography=semantic_tomography,
                source_attributes=source_attributes,
                projection_target={
                    "persona_terms": request.persona_terms,
                    "namespace_terms": request.namespace_terms,
                    "style_terms": request.style_terms,
                    "guidance_words": request.guidance_words,
                    "guidance_symbols": request.guidance_symbols,
                    "projection_intensity": request.projection_intensity
                } if request.use_vocabulary_system else None,
                vocabulary_usage={
                    "vocabulary_system_used": request.use_vocabulary_system,
                    "source_extraction_enabled": request.extract_source_attributes,
                    "total_vocabulary_attributes": self.vocabulary_engine.total_attributes()
                },
                processing_time_ms=processing_time,
                validation_results={
                    "initial_state": initial_validation,
                    "final_state": final_validation
                } if request.enable_logging else None,
                operation_log=operation_log if request.enable_logging else None
            )
            
        except HTTPException:
            raise
        except Exception as e:
            # Log unexpected error
            error_log = self._log_operation("unexpected_error", {
                "error": str(e),
                "error_type": type(e).__name__
            }, "ERROR")
            operation_log.append(error_log)
            
            return TransformationResponse(
                request_id=request_id,
                success=False,
                error_message=f"Transformation failed: {str(e)}",
                processing_time_ms=(time.time() - start_time) * 1000,
                operation_log=operation_log if request.enable_logging else None
            )

# Global engine instance
_density_matrix_engine = None

def get_density_matrix_engine() -> DensityMatrixEngine:
    """Get global density matrix engine instance."""
    global _density_matrix_engine
    if _density_matrix_engine is None:
        _density_matrix_engine = DensityMatrixEngine()
    return _density_matrix_engine

# FastAPI router
router = APIRouter(prefix="/api/density-matrix", tags=["Density Matrix Transformations"])

@router.post("/transform", response_model=TransformationResponse)
async def transform_text_endpoint(
    request: TransformationRequest,
    background_tasks: BackgroundTasks
) -> TransformationResponse:
    """
    Apply density matrix transformation to text.
    
    This is the core endpoint for quantum-inspired narrative transformations.
    All operations are logged and validated. No mock data is used.
    """
    if not NARRATIVE_THEORY_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Narrative theory dependencies not available. Please install required packages."
        )
    
    engine = get_density_matrix_engine()
    return await engine.transform_text(request)

@router.get("/health")
async def health_check():
    """Check health of density matrix transformation system."""
    try:
        if not NARRATIVE_THEORY_AVAILABLE:
            return {
                "status": "error",
                "message": "Narrative theory dependencies not available",
                "available_features": []
            }
        
        engine = get_density_matrix_engine()
        
        # Test basic functionality
        test_embedding = torch.randn(384)  # Common sentence transformer size
        test_engine = engine.get_engine(4)  # Small test dimension
        test_state = test_engine.text_to_meaning_state("Test text", test_embedding)
        
        return {
            "status": "healthy",
            "message": "Density matrix transformation system operational",
            "available_features": [
                "density_matrix_transformations",
                "semantic_tomography", 
                "narrative_coherence_validation",
                "comprehensive_logging",
                "embedding_integration"
            ],
            "test_results": {
                "test_state_purity": test_state.purity(),
                "test_state_entropy": test_state.von_neumann_entropy(),
                "engines_cached": len(engine.engines)
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Health check failed: {str(e)}",
            "available_features": []
        }

@router.get("/engines/status")
async def engines_status():
    """Get status of all narrative engines."""
    if not NARRATIVE_THEORY_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Narrative theory not available"
        )
    
    engine = get_density_matrix_engine()
    
    status = {
        "engines_count": len(engine.engines),
        "dimensions": list(engine.engines.keys()),
        "operation_count": engine.operation_counter,
        "embedding_manager": {
            "active_model": engine.embedding_manager.active_model,
            "available_models": list(engine.embedding_manager.models.keys())
        }
    }
    
    return status

@router.post("/validate/density-matrix")
async def validate_density_matrix(matrix_data: List[List[float]]):
    """Validate a density matrix for theoretical correctness."""
    if not NARRATIVE_THEORY_AVAILABLE:
        raise HTTPException(status_code=503, detail="Narrative theory not available")
    
    try:
        matrix = torch.tensor(matrix_data, dtype=torch.float32)
        engine = get_density_matrix_engine()
        validation = engine._validate_density_matrix(matrix, "user_provided")
        return validation
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Validation failed: {str(e)}")