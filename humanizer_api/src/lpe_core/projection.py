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
            
            # Execute step with sanity checking and retry logic
            output_text, attempt_count = self._execute_step_with_retry(
                current_text, step_type, previous_step_type, step_name
            )
            
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
                metadata={
                    "step_type": step_type,
                    "attempt_count": attempt_count,
                    "sanity_checked": True
                },
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
    
    def _execute_step_with_retry(self, input_text: str, step_type: str, previous_step_type: str, step_name: str) -> tuple[str, int]:
        """Execute a transformation step with sanity checking and retry logic."""
        max_attempts = 3
        attempt = 0
        
        while attempt < max_attempts:
            attempt += 1
            
            # Execute the transformation
            output_text = self.transformer.transform(input_text, step_type, previous_step_type)
            
            # Sanity check the output
            if self._is_valid_output(output_text, step_type, step_name):
                if attempt > 1:
                    logger.info(f"Step '{step_name}' succeeded on attempt {attempt}")
                return output_text, attempt
            else:
                logger.warning(f"Step '{step_name}' failed sanity check on attempt {attempt}: {self._get_failure_reason(output_text, step_type)}")
                
                if attempt < max_attempts:
                    # Modify input for retry to be more explicit
                    input_text = self._prepare_retry_input(input_text, step_type, output_text, attempt)
        
        # If all attempts failed, return the last output with a warning
        logger.error(f"Step '{step_name}' failed all {max_attempts} attempts, using last output")
        return output_text, attempt
    
    def _is_valid_output(self, output: str, step_type: str, step_name: str) -> bool:
        """Check if the LLM output is valid content (not an error message)."""
        if not output or len(output.strip()) < 10:
            return False
        
        # Common error patterns
        error_patterns = [
            "i understand", "i'm ready", "please provide", "i need", "could you provide",
            "you are absolutely right", "my apologies", "i got ahead of myself",
            "just paste", "let me know", "what would you like", "i'd be happy to",
            "ready when you are", "waiting for", "need more information",
            "clarification", "specific details", "can you give me", "i'll need",
            "source material", "original text", "input text", "provide the"
        ]
        
        output_lower = output.lower()
        
        # Check for error patterns
        for pattern in error_patterns:
            if pattern in output_lower:
                return False
        
        # Step-specific validation
        if step_type == "deconstruct":
            # Should contain WHO/WHAT/WHY/HOW/OUTCOME structure
            required_elements = ["who:", "what:", "why:", "how:", "outcome:"]
            found_elements = sum(1 for elem in required_elements if elem in output_lower)
            return found_elements >= 3  # At least 3 out of 5 elements
        
        elif step_type == "map":
            # Should contain mappings or translations
            mapping_indicators = ["→", "becomes", "equivalent", "maps to", "translates to", "corresponds to"]
            return any(indicator in output_lower for indicator in mapping_indicators)
        
        elif step_type in ["reconstruct", "stylize"]:
            # Should be narrative text, not meta-commentary
            meta_indicators = ["this narrative", "the story", "the text", "analysis", "summary"]
            has_meta = any(indicator in output_lower for indicator in meta_indicators)
            return len(output.split()) > 20 and not has_meta
        
        elif step_type == "reflect":
            # Should contain reflective analysis
            reflection_indicators = ["transformation", "reveals", "illuminates", "pattern", "insight", "meaning"]
            return any(indicator in output_lower for indicator in reflection_indicators)
        
        return True  # Default to valid if no specific issues found
    
    def _get_failure_reason(self, output: str, step_type: str) -> str:
        """Get a description of why the output failed validation."""
        if not output or len(output.strip()) < 10:
            return "Output too short or empty"
        
        output_lower = output.lower()
        
        # Check for specific error patterns
        if "i understand" in output_lower or "i'm ready" in output_lower:
            return "LLM is asking for clarification instead of processing"
        elif "please provide" in output_lower or "need more" in output_lower:
            return "LLM is requesting additional input"
        elif "my apologies" in output_lower or "got ahead of myself" in output_lower:
            return "LLM is apologizing instead of transforming"
        
        # Step-specific failures
        if step_type == "deconstruct":
            return "Missing WHO/WHAT/WHY/HOW/OUTCOME structure"
        elif step_type == "map":
            return "No clear mappings or translations found"
        elif step_type in ["reconstruct", "stylize"]:
            return "Output appears to be meta-commentary rather than narrative"
        elif step_type == "reflect":
            return "Missing reflective analysis indicators"
        
        return "Unknown validation failure"
    
    def _prepare_retry_input(self, original_input: str, step_type: str, failed_output: str, attempt: int) -> str:
        """Prepare input for retry attempt with more explicit instructions."""
        retry_prefixes = {
            "deconstruct": f"TASK: Extract core narrative elements in this exact format:\nWHO: [specific characters/actors]\nWHAT: [specific actions/events]\nWHY: [motivations/conflicts]\nHOW: [methods/approaches]\nOUTCOME: [results/implications]\n\nNARRATIVE TO ANALYZE:\n",
            
            "map": f"TASK: Create specific mappings from the source elements to target universe equivalents. Use this format:\n[Source Element] → [Target Equivalent]\n\nSOURCE ELEMENTS TO MAP:\n",
            
            "reconstruct": f"TASK: Rewrite this as a complete flowing narrative story. Do not provide analysis or commentary, just tell the story.\n\nELEMENTS TO RECONSTRUCT INTO STORY:\n",
            
            "stylize": f"TASK: Rewrite this narrative in the specified style. Keep the same story but change only the tone and language.\n\nNARRATIVE TO STYLIZE:\n",
            
            "reflect": f"TASK: Provide analytical commentary on how this transformation reveals deeper patterns or universal truths.\n\nTRANSFORMATION TO REFLECT ON:\n"
        }
        
        prefix = retry_prefixes.get(step_type, f"TASK: Process this content for {step_type} step:\n")
        return prefix + original_input

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