"""
Balanced LLM Transformer for Humanizer Lighthouse

This module provides an enhanced LLM transformation pipeline that uses the
Advanced Attribute Balancing System to prevent templated outputs while
preserving narrative essence.

Key features:
- Dynamic prompt generation based on narrative DNA
- Attribute dominance detection and mitigation
- Context-aware transformation with preservation scoring
- Template pattern avoidance through balanced prompting
- Natural language grounding for authentic results
"""

import json
import logging
import time
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass

from advanced_attribute_balancing import (
    AttributeBalancer, 
    NarrativeDNAExtractor,
    NarrativeDNA,
    BalancingResult
)

logger = logging.getLogger(__name__)

@dataclass
class BalancedTransformationStep:
    """Enhanced transformation step with balancing metadata."""
    name: str
    input_snapshot: str
    output_snapshot: str
    duration_ms: int
    preservation_score: float = 0.0
    template_risk_score: float = 0.0
    dna_drift_score: float = 0.0
    balancing_applied: bool = False
    metadata: Dict[str, Any] = None

@dataclass
class BalancedProjection:
    """Enhanced projection with balancing analysis."""
    id: Optional[str]
    source_narrative: str
    final_projection: str
    reflection: str
    persona: str
    namespace: str
    style: str
    steps: List[BalancedTransformationStep]
    source_dna: Optional[NarrativeDNA] = None
    final_dna: Optional[NarrativeDNA] = None
    overall_preservation_score: float = 0.0
    balancing_analysis: Optional[BalancingResult] = None
    embedding: Optional[List[float]] = None

class BalancedLLMTransformer:
    """LLM transformer with advanced attribute balancing."""
    
    def __init__(self, llm_provider, persona: str, namespace: str, style: str):
        self.provider = llm_provider
        self.persona = persona
        self.namespace = namespace
        self.style = style
        
        # Initialize balancing components
        self.balancer = AttributeBalancer()
        self.dna_extractor = NarrativeDNAExtractor()
        
        # Performance tracking
        self.transformation_history = []
        self.template_avoidance_stats = {
            'templates_detected': 0,
            'templates_avoided': 0,
            'preservation_scores': []
        }
    
    def transform_with_balancing(self, source_narrative: str, show_steps: bool = True) -> BalancedProjection:
        """Execute balanced transformation pipeline."""
        
        # Extract source narrative DNA
        source_dna = self.dna_extractor.extract_dna(source_narrative)
        
        # Analyze attribute combination
        balancing_analysis = self.balancer.analyze_combination(
            self.persona, self.namespace, self.style, source_narrative
        )
        
        # Generate balanced prompts
        balanced_prompts = self.balancer.generate_balanced_prompts(
            self.persona, self.namespace, self.style, source_dna
        )
        
        # Log balancing insights
        logger.info(f"Balancing Analysis - Balanced: {balancing_analysis.is_balanced}, "
                   f"Template Risk: {balancing_analysis.template_risk_score:.2f}, "
                   f"Preservation: {balancing_analysis.preservation_score:.2f}")
        
        if balancing_analysis.dominant_attributes:
            logger.warning(f"Dominant attributes detected: {balancing_analysis.dominant_attributes}")
        
        if balancing_analysis.conflicts:
            logger.warning(f"Attribute conflicts detected: {balancing_analysis.conflicts}")
        
        # Create projection
        projection = BalancedProjection(
            id=None,
            source_narrative=source_narrative,
            final_projection="",
            reflection="",
            persona=self.persona,
            namespace=self.namespace,
            style=self.style,
            steps=[],
            source_dna=source_dna,
            balancing_analysis=balancing_analysis
        )
        
        # Execute transformation pipeline
        current_text = source_narrative
        pipeline_steps = [
            ("Deconstructing narrative", "deconstruct"),
            ("Mapping to namespace", "map"), 
            ("Reconstructing allegory", "reconstruct"),
            ("Applying style", "stylize"),
            ("Generating reflection", "reflect")
        ]
        
        for step_name, step_type in pipeline_steps:
            logger.info(f"Starting balanced step: {step_name}")
            start_time = time.time()
            
            # Get balanced prompt for this step
            system_prompt = balanced_prompts.get(step_type, self._fallback_prompt(step_type))
            
            # Apply context-specific balancing
            if balancing_analysis.template_risk_score > 0.6:
                system_prompt = self._apply_template_mitigation(system_prompt, step_type)
            
            # Execute step with balanced prompting
            output_text, template_detected = self._execute_balanced_step(
                current_text, system_prompt, step_type, balancing_analysis
            )
            
            duration_ms = int((time.time() - start_time) * 1000)
            
            # Calculate step metrics
            preservation_score = self._calculate_preservation_score(
                current_text, output_text, source_dna, step_type
            )
            
            dna_drift = self._calculate_dna_drift(
                source_dna, output_text, step_type
            )
            
            # Record step
            step = BalancedTransformationStep(
                name=step_name,
                input_snapshot=current_text[:200] + "..." if len(current_text) > 200 else current_text,
                output_snapshot=output_text[:200] + "..." if len(output_text) > 200 else output_text,
                duration_ms=duration_ms,
                preservation_score=preservation_score,
                template_risk_score=balancing_analysis.template_risk_score,
                dna_drift_score=dna_drift,
                balancing_applied=template_detected,
                metadata={
                    "step_type": step_type,
                    "balanced_prompting": True,
                    "template_mitigation": template_detected
                }
            )
            projection.steps.append(step)
            
            # Update text for next step (except reflection)
            if step_type != "reflect":
                current_text = output_text
            
            logger.info(f"Completed balanced step: {step_name} "
                       f"(preservation: {preservation_score:.2f}, drift: {dna_drift:.2f})")
        
        # Set final outputs
        projection.final_projection = current_text
        projection.reflection = projection.steps[-1].output_snapshot
        
        # Extract final DNA
        projection.final_dna = self.dna_extractor.extract_dna(projection.final_projection)
        
        # Calculate overall preservation score
        projection.overall_preservation_score = self._calculate_overall_preservation(
            source_dna, projection.final_dna, projection.steps
        )
        
        # Update statistics
        self._update_stats(projection, balancing_analysis)
        
        # Generate embedding
        try:
            projection.embedding = self.provider.embed(projection.final_projection)
        except Exception as e:
            logger.warning(f"Could not generate embedding: {e}")
            projection.embedding = None
        
        return projection
    
    def _execute_balanced_step(self, input_text: str, system_prompt: str, 
                             step_type: str, analysis: BalancingResult) -> Tuple[str, bool]:
        """Execute transformation step with template detection and mitigation."""
        
        template_detected = False
        max_attempts = 3
        
        for attempt in range(max_attempts):
            try:
                # Generate output
                output = self.provider.generate(input_text, system_prompt)
                
                # Check for template patterns
                if self._detect_template_patterns(output, step_type):
                    template_detected = True
                    self.template_avoidance_stats['templates_detected'] += 1
                    
                    if attempt < max_attempts - 1:
                        # Modify prompt to avoid templating
                        system_prompt = self._enhance_anti_template_prompt(system_prompt, output, step_type)
                        logger.warning(f"Template detected in {step_type}, retrying with enhanced prompt")
                        continue
                    else:
                        logger.warning(f"Template persisted in {step_type} after {max_attempts} attempts")
                
                # Validate output quality
                if self._validate_output_quality(output, step_type):
                    if template_detected and attempt > 0:
                        self.template_avoidance_stats['templates_avoided'] += 1
                    return output, template_detected
                
            except Exception as e:
                logger.error(f"Error in balanced step {step_type}, attempt {attempt + 1}: {e}")
                if attempt == max_attempts - 1:
                    raise
        
        return output, template_detected
    
    def _detect_template_patterns(self, output: str, step_type: str) -> bool:
        """Detect if output contains templated patterns."""
        
        # Get known template phrases for current attributes
        template_phrases = []
        for attr_name in [self.persona, self.namespace, self.style]:
            if attr_name in self.balancer.attribute_registry:
                template_phrases.extend(
                    self.balancer.attribute_registry[attr_name].template_phrases
                )
        
        # Check for template phrase usage
        output_lower = output.lower()
        for phrase in template_phrases:
            if phrase.lower() in output_lower:
                logger.debug(f"Template phrase detected: '{phrase}' in {step_type} output")
                return True
        
        # Check for repetitive structures
        if self._detect_repetitive_structures(output):
            return True
        
        # Check for over-specification patterns
        if self._detect_over_specification(output, step_type):
            return True
        
        return False
    
    def _detect_repetitive_structures(self, output: str) -> bool:
        """Detect repetitive linguistic structures."""
        sentences = output.split('.')
        if len(sentences) < 3:
            return False
        
        # Check for repeated sentence starters
        starters = [sent.strip()[:10] for sent in sentences if sent.strip()]
        unique_starters = set(starters)
        
        if len(unique_starters) / len(starters) < 0.7:  # High repetition
            return True
        
        return False
    
    def _detect_over_specification(self, output: str, step_type: str) -> bool:
        """Detect over-specified patterns that indicate templating."""
        
        over_spec_patterns = {
            'reconstruct': [
                'the narrative demonstrates', 'this story reveals', 'the transformation shows',
                'in this allegorical', 'through this lens we see'
            ],
            'stylize': [
                'applying the style', 'in the manner of', 'characteristic of the style',
                'typical of this approach', 'following the conventions'
            ],
            'reflect': [
                'this transformation illustrates', 'the allegorical mapping reveals',
                'by examining this through', 'the analysis demonstrates'
            ]
        }
        
        patterns = over_spec_patterns.get(step_type, [])
        output_lower = output.lower()
        
        for pattern in patterns:
            if pattern in output_lower:
                return True
        
        return False
    
    def _enhance_anti_template_prompt(self, original_prompt: str, templated_output: str, step_type: str) -> str:
        """Enhance prompt to avoid template patterns."""
        
        anti_template_additions = {
            'deconstruct': "\n\nWrite in natural, analytical language. Avoid formulaic structures.",
            'map': "\n\nCreate organic equivalents. Avoid forced pattern matching or artificial correspondences.",
            'reconstruct': "\n\nTell this as a natural story. Avoid meta-commentary about transformation or allegory.",
            'stylize': "\n\nLet the style emerge naturally from word choice and rhythm. Avoid announcing stylistic choices.",
            'reflect': "\n\nProvide genuine insight based on the specific content. Avoid generic transformation commentary."
        }
        
        addition = anti_template_additions.get(step_type, "\n\nUse natural, unforced language.")
        return original_prompt + addition
    
    def _apply_template_mitigation(self, prompt: str, step_type: str) -> str:
        """Apply template mitigation strategies to prompts."""
        
        # Add specificity requirements
        specificity_prompt = "\n\nIMPORTANT: Focus on the specific content of this narrative. Avoid generic phrases or formulaic language patterns."
        
        # Add naturalness emphasis
        naturalness_prompt = "\n\nWrite in a natural, unforced way that serves the content rather than following predetermined patterns."
        
        return prompt + specificity_prompt + naturalness_prompt
    
    def _validate_output_quality(self, output: str, step_type: str) -> bool:
        """Validate that output meets quality standards."""
        
        if not output or len(output.strip()) < 10:
            return False
        
        # Check for error messages
        error_indicators = ['error', 'failed', 'cannot', 'unable to', 'sorry']
        output_lower = output.lower()
        for indicator in error_indicators:
            if indicator in output_lower:
                return False
        
        # Step-specific validation
        if step_type == "deconstruct":
            required_elements = ["WHO", "WHAT", "WHY", "HOW", "OUTCOME"]
            found = sum(1 for elem in required_elements if elem in output.upper())
            return found >= 3
        
        elif step_type == "map":
            return "→" in output or "becomes" in output.lower() or "equivalent" in output.lower()
        
        elif step_type in ["reconstruct", "stylize"]:
            # Should be narrative format
            return len(output.split('.')) >= 2
        
        elif step_type == "reflect":
            # Should contain analytical language
            analytical_words = ["reveals", "shows", "demonstrates", "illuminates", "pattern"]
            return any(word in output.lower() for word in analytical_words)
        
        return True
    
    def _calculate_preservation_score(self, input_text: str, output_text: str, 
                                    source_dna: NarrativeDNA, step_type: str) -> float:
        """Calculate how well the step preserved narrative essence."""
        
        if step_type == "reflect":
            return 1.0  # Reflection doesn't need to preserve content
        
        # Extract entities from both texts
        input_entities = set(self.dna_extractor._extract_entities(input_text))
        output_entities = set(self.dna_extractor._extract_entities(output_text))
        
        # Calculate entity preservation (with some allowance for transformation)
        if input_entities:
            entity_overlap = len(input_entities.intersection(output_entities)) / len(input_entities)
        else:
            entity_overlap = 1.0
        
        # Calculate length preservation (should not be drastically different)
        length_ratio = min(len(output_text), len(input_text)) / max(len(output_text), len(input_text), 1)
        
        # Calculate structural preservation
        input_sentences = len(input_text.split('.'))
        output_sentences = len(output_text.split('.'))
        structure_preservation = min(input_sentences, output_sentences) / max(input_sentences, output_sentences, 1)
        
        # Weighted average
        preservation_score = (entity_overlap * 0.4 + length_ratio * 0.3 + structure_preservation * 0.3)
        
        return min(1.0, preservation_score)
    
    def _calculate_dna_drift(self, source_dna: NarrativeDNA, output_text: str, step_type: str) -> float:
        """Calculate how much the output has drifted from source DNA."""
        
        if step_type == "reflect":
            return 0.0  # Reflection is expected to be different
        
        # Extract DNA from output
        output_dna = self.dna_extractor.extract_dna(output_text)
        
        # Compare key DNA elements
        drift_factors = []
        
        # Entity drift
        source_entities = set(source_dna.core_entities)
        output_entities = set(output_dna.core_entities)
        if source_entities:
            entity_retention = len(source_entities.intersection(output_entities)) / len(source_entities)
            drift_factors.append(1.0 - entity_retention)
        
        # Theme drift
        source_themes = set(source_dna.thematic_elements)
        output_themes = set(output_dna.thematic_elements)
        if source_themes:
            theme_retention = len(source_themes.intersection(output_themes)) / len(source_themes)
            drift_factors.append(1.0 - theme_retention)
        
        # Complexity drift
        complexity_drift = abs(source_dna.complexity_score - output_dna.complexity_score)
        drift_factors.append(complexity_drift)
        
        # Semantic density drift
        density_drift = abs(source_dna.semantic_density - output_dna.semantic_density)
        drift_factors.append(density_drift)
        
        return sum(drift_factors) / len(drift_factors) if drift_factors else 0.0
    
    def _calculate_overall_preservation(self, source_dna: NarrativeDNA, final_dna: NarrativeDNA, 
                                      steps: List[BalancedTransformationStep]) -> float:
        """Calculate overall preservation score across the entire transformation."""
        
        # Average step preservation scores (excluding reflection)
        content_steps = [s for s in steps if s.metadata and s.metadata.get('step_type') != 'reflect']
        if content_steps:
            avg_step_preservation = sum(s.preservation_score for s in content_steps) / len(content_steps)
        else:
            avg_step_preservation = 0.0
        
        # Overall DNA preservation
        source_entities = set(source_dna.core_entities)
        final_entities = set(final_dna.core_entities)
        
        entity_preservation = 0.0
        if source_entities:
            # Allow for some entity transformation in allegory
            direct_preservation = len(source_entities.intersection(final_entities)) / len(source_entities)
            # Also consider semantic similarity (simplified)
            semantic_preservation = 0.5  # Assume moderate semantic preservation for transformed entities
            entity_preservation = max(direct_preservation, semantic_preservation)
        
        # Thematic preservation
        source_themes = set(source_dna.thematic_elements)
        final_themes = set(final_dna.thematic_elements)
        theme_preservation = 1.0
        if source_themes:
            theme_preservation = len(source_themes.intersection(final_themes)) / len(source_themes)
        
        # Structural preservation
        structure_preservation = 1.0 if source_dna.narrative_structure == final_dna.narrative_structure else 0.7
        
        # Weighted combination
        overall_score = (
            avg_step_preservation * 0.4 +
            entity_preservation * 0.2 +
            theme_preservation * 0.2 +
            structure_preservation * 0.2
        )
        
        return min(1.0, overall_score)
    
    def _update_stats(self, projection: BalancedProjection, analysis: BalancingResult):
        """Update performance statistics."""
        self.template_avoidance_stats['preservation_scores'].append(projection.overall_preservation_score)
        
        # Keep last 100 transformations
        self.transformation_history.append({
            'preservation_score': projection.overall_preservation_score,
            'template_risk': analysis.template_risk_score,
            'balanced': analysis.is_balanced,
            'timestamp': time.time()
        })
        
        if len(self.transformation_history) > 100:
            self.transformation_history = self.transformation_history[-100:]
    
    def _fallback_prompt(self, step_type: str) -> str:
        """Fallback prompts if balanced prompt generation fails."""
        fallbacks = {
            'deconstruct': "Analyze this narrative and identify its core structural elements.",
            'map': f"Create appropriate equivalents for the narrative elements in the {self.namespace} universe.",
            'reconstruct': f"Retell this story from the {self.persona} perspective using the mapped elements.", 
            'stylize': f"Express this narrative in {self.style} style.",
            'reflect': "Provide analytical commentary on this transformation."
        }
        return fallbacks.get(step_type, "Process this text appropriately.")
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics for the balanced transformer."""
        preservation_scores = self.template_avoidance_stats['preservation_scores']
        
        return {
            'total_transformations': len(self.transformation_history),
            'templates_detected': self.template_avoidance_stats['templates_detected'],
            'templates_avoided': self.template_avoidance_stats['templates_avoided'],
            'avg_preservation_score': sum(preservation_scores) / len(preservation_scores) if preservation_scores else 0.0,
            'min_preservation_score': min(preservation_scores) if preservation_scores else 0.0,
            'max_preservation_score': max(preservation_scores) if preservation_scores else 0.0,
            'recent_transformations': self.transformation_history[-10:] if self.transformation_history else []
        }

# Export main classes
__all__ = ['BalancedLLMTransformer', 'BalancedProjection', 'BalancedTransformationStep']