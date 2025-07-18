"""Core projection engine for narrative transformation."""
import json
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

from .models import ProjectionStep, Projection
from .llm_provider import LLMTransformer, get_llm_provider

logger = logging.getLogger(__name__)

class TranslationChain:
    """Orchestrates the complete translation chain process."""
    
    def __init__(self, persona: str, namespace: str, style: str, verbose: bool = True):
        self.persona = persona
        self.namespace = namespace
        self.style = style
        self.verbose = verbose
        self.transformer = LLMTransformer(persona, namespace, style)
    
    def run(self, source_narrative: str, show_steps: bool = True, transform_id: str = None, progress_callback = None) -> Projection:
        """Execute the complete translation chain."""
        projection = Projection(
            id=None,
            source_narrative=source_narrative,
            final_projection="",
            reflection="",
            persona=self.persona,
            namespace=self.namespace,
            style=self.style
        )
        
        # Define transformation pipeline
        pipeline = [
            ("Deconstructing narrative", "deconstruct"),
            ("Mapping to namespace", "map"),
            ("Reconstructing allegory", "reconstruct"),
            ("Applying style", "stylize"),
            ("Generating reflection", "reflect")
        ]
        
        current_text = source_narrative
        previous_step_type = None
        
        for step_name, step_type in pipeline:
            if self.verbose:
                logger.info(f"Starting step: {step_name}")
            
            # Send progress update - step started
            if progress_callback and transform_id:
                import asyncio
                try:
                    asyncio.create_task(progress_callback(transform_id, step_type, "started", {
                        "step_name": step_name,
                        "input_preview": current_text[:100] + "..." if len(current_text) > 100 else current_text
                    }))
                except:
                    pass  # Don't fail if progress callback fails
            
            start_time = time.time()
            output_text = self.transformer.transform(current_text, step_type, previous_step_type)
            duration_ms = int((time.time() - start_time) * 1000)
            
            # Send progress update - step completed
            if progress_callback and transform_id:
                import asyncio
                try:
                    asyncio.create_task(progress_callback(transform_id, step_type, "completed", {
                        "step_name": step_name,
                        "duration_ms": duration_ms,
                        "output_preview": output_text[:100] + "..." if len(output_text) > 100 else output_text
                    }))
                except:
                    pass  # Don't fail if progress callback fails
            
            # Record step
            step = ProjectionStep(
                name=step_name,
                input_snapshot=current_text[:200] + "..." if len(current_text) > 200 else current_text,
                output_snapshot=output_text[:200] + "..." if len(output_text) > 200 else output_text,
                metadata={"step_type": step_type},
                duration_ms=duration_ms
            )
            projection.steps.append(step)
            
            # Update for next iteration
            if step_type != "reflect":
                current_text = output_text
            
            # Update previous step type for next iteration
            previous_step_type = step_type
            
            if self.verbose:
                logger.info(f"Completed step: {step_name} in {duration_ms}ms")
        
        # Set final outputs
        projection.final_projection = current_text
        projection.reflection = projection.steps[-1].output_snapshot
        
        # Generate embedding for the final projection
        try:
            projection.embedding = self.transformer.generate_embedding(projection.final_projection)
            if self.verbose:
                logger.info(f"Generated embedding with {len(projection.embedding)} dimensions")
        except Exception as e:
            logger.warning(f"Could not generate embedding: {e}")
            projection.embedding = None
        
        return projection

class ProjectionEngine:
    """Main engine for managing projections."""
    
    def __init__(self):
        self.projections: List[Projection] = []
    
    def create_projection(self, narrative: str, persona: str, namespace: str, 
                         style: str, show_steps: bool = True, transform_id: str = None, 
                         progress_callback = None) -> Projection:
        """Create a new projection."""
        chain = TranslationChain(persona, namespace, style, verbose=show_steps)
        projection = chain.run(narrative, show_steps, transform_id, progress_callback)
        projection.id = len(self.projections) + 1
        self.projections.append(projection)
        return projection
    
    def get_projection(self, projection_id: int) -> Optional[Projection]:
        """Retrieve a projection by ID."""
        for proj in self.projections:
            if proj.id == projection_id:
                return proj
        return None
    
    def search_projections(self, query: str, limit: int = 10) -> List[Projection]:
        """Search projections (basic implementation)."""
        results = []
        query_lower = query.lower()
        
        for proj in self.projections:
            if (query_lower in proj.source_narrative.lower() or
                query_lower in proj.final_projection.lower() or
                query_lower in proj.reflection.lower()):
                results.append(proj)
                if len(results) >= limit:
                    break
        
        return results