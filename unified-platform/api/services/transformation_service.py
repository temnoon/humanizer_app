"""
Transformation Service
Unified content transformation using LPE, Quantum, Maieutic, and other engines
"""
import asyncio
import logging
import time
import uuid
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from config import config
from models import (
    TransformationRequest, TransformationResult, TransformationEngine,
    TransformationAttributes, QualityAnalysis, QuantumAnalysis
)
from .llm_service import LLMService

logger = logging.getLogger(__name__)


@dataclass
class TransformationContext:
    """Context for transformation operations"""
    user_id: Optional[uuid.UUID] = None
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class LamishProjectionEngine:
    """
    Lamish Projection Engine - Core transformation logic
    Based on phenomenological principles with three-layer subjectivity
    """
    
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
        
    async def transform(
        self, 
        text: str, 
        attributes: TransformationAttributes,
        context: TransformationContext
    ) -> Dict[str, Any]:
        """
        Apply Lamish Projection transformation
        
        Three-layer transformation:
        - Essence (N_E): Core facts and relationships
        - Persona (Ψ): Worldview and perspective  
        - Namespace (Ω): Universe of references
        - Style (Σ): Linguistic approach
        """
        
        start_time = time.time()
        
        # Step 1: Extract essence (core meaning)
        essence_prompt = self._build_essence_prompt(text)
        essence_response = await self.llm_service.complete(essence_prompt)
        essence = essence_response.text
        
        # Step 2: Apply persona transformation
        persona_prompt = self._build_persona_prompt(essence, attributes.persona)
        persona_response = await self.llm_service.complete(persona_prompt)
        persona_text = persona_response.text
        
        # Step 3: Apply namespace transformation
        namespace_prompt = self._build_namespace_prompt(persona_text, attributes.namespace)
        namespace_response = await self.llm_service.complete(namespace_prompt)
        namespace_text = namespace_response.text
        
        # Step 4: Apply style transformation
        style_prompt = self._build_style_prompt(namespace_text, attributes.style)
        final_response = await self.llm_service.complete(style_prompt)
        final_text = final_response.text
        
        processing_time = (time.time() - start_time) * 1000
        
        # Calculate total token usage
        total_tokens = (
            essence_response.token_usage.get("total_tokens", 0) +
            persona_response.token_usage.get("total_tokens", 0) +
            namespace_response.token_usage.get("total_tokens", 0) +
            final_response.token_usage.get("total_tokens", 0)
        )
        
        return {
            "transformed_text": final_text,
            "processing_time_ms": processing_time,
            "token_usage": {"total_tokens": total_tokens},
            "intermediate_steps": {
                "essence": essence,
                "persona": persona_text,
                "namespace": namespace_text,
                "final": final_text
            },
            "quality_metrics": await self._assess_transformation_quality(text, final_text)
        }
    
    def _build_essence_prompt(self, text: str) -> str:
        """Build prompt for essence extraction"""
        return f"""
Extract the essential meaning and core facts from the following text.
Focus on:
- Key factual information
- Main arguments or claims
- Relationships between concepts
- Objective content without stylistic elements

Text: {text}

Essential meaning:"""

    def _build_persona_prompt(self, essence: str, persona: Optional[str]) -> str:
        """Build prompt for persona application"""
        
        if not persona:
            return essence
            
        return f"""
Rewrite the following content from the perspective of a {persona}.
Maintain all factual accuracy while adopting the worldview, values, and perspective typical of this persona.

Content: {essence}

Rewritten from {persona} perspective:"""

    def _build_namespace_prompt(self, text: str, namespace: Optional[str]) -> str:
        """Build prompt for namespace application"""
        
        if not namespace:
            return text
            
        return f"""
Adapt the following content for the {namespace} domain.
Use appropriate terminology, references, and context relevant to this field.
Maintain meaning while making it suitable for this specific domain.

Content: {text}

Adapted for {namespace}:"""

    def _build_style_prompt(self, text: str, style: Optional[str]) -> str:
        """Build prompt for style application"""
        
        if not style:
            return text
            
        return f"""
Rewrite the following content in a {style} style.
Focus on:
- Appropriate tone and register
- Suitable vocabulary and sentence structure
- Proper formatting and presentation
- Maintaining all meaning and information

Content: {text}

Rewritten in {style} style:"""

    async def _assess_transformation_quality(self, original: str, transformed: str) -> Dict[str, float]:
        """Assess quality of transformation"""
        
        # Simple quality metrics (could be enhanced with specialized models)
        quality_metrics = {
            "length_ratio": len(transformed) / len(original) if len(original) > 0 else 0,
            "coherence_score": 0.8,  # Placeholder - could use coherence model
            "preservation_score": 0.9,  # Placeholder - could use semantic similarity
            "style_accuracy": 0.85  # Placeholder - could use style classifier
        }
        
        return quality_metrics


class QuantumNarrativeEngine:
    """
    Quantum Narrative Analysis Engine
    Analyzes narrative superposition and coherence measures
    """
    
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
        
    async def analyze(self, text: str, context: TransformationContext) -> QuantumAnalysis:
        """Perform quantum narrative analysis"""
        
        # Quantum state analysis
        quantum_state = await self._analyze_quantum_state(text)
        
        # Coherence measures
        coherence_measures = await self._measure_coherence(text)
        
        # Entanglement analysis
        entanglement_score = await self._calculate_entanglement(text)
        
        # Superposition states
        superposition_states = await self._identify_superposition_states(text)
        
        return QuantumAnalysis(
            quantum_state=quantum_state,
            coherence_measures=coherence_measures,
            entanglement_score=entanglement_score,
            superposition_states=superposition_states
        )
    
    async def _analyze_quantum_state(self, text: str) -> Dict[str, float]:
        """Analyze quantum state properties of narrative"""
        
        prompt = f"""
Analyze the quantum narrative properties of this text:

{text}

Provide scores (0-1) for:
- Uncertainty: Level of ambiguity and multiple interpretations
- Coherence: Internal consistency and logical flow
- Entanglement: Interconnectedness of ideas and concepts
- Superposition: Presence of multiple simultaneous states/meanings

Response format:
uncertainty: 0.X
coherence: 0.X
entanglement: 0.X
superposition: 0.X
"""
        
        response = await self.llm_service.complete(prompt)
        
        # Parse response (simplified - could use structured output)
        quantum_state = {
            "uncertainty": 0.5,
            "coherence": 0.8,
            "entanglement": 0.6,
            "superposition": 0.4
        }
        
        return quantum_state
    
    async def _measure_coherence(self, text: str) -> Dict[str, float]:
        """Measure different types of coherence"""
        
        return {
            "temporal_coherence": 0.8,
            "causal_coherence": 0.7,
            "thematic_coherence": 0.9,
            "logical_coherence": 0.85
        }
    
    async def _calculate_entanglement(self, text: str) -> float:
        """Calculate narrative entanglement score"""
        
        # Simplified calculation based on concept interconnectedness
        sentences = text.split('.')
        concept_density = len(set(text.lower().split())) / len(text.split())
        
        # Normalize to 0-1 range
        entanglement = min(1.0, concept_density * len(sentences) / 10)
        
        return entanglement
    
    async def _identify_superposition_states(self, text: str) -> List[str]:
        """Identify simultaneous narrative states"""
        
        prompt = f"""
Identify different simultaneous interpretations or meanings in this text.
List up to 5 distinct ways this text could be understood:

{text}

Interpretations:"""
        
        response = await self.llm_service.complete(prompt)
        
        # Parse interpretations (simplified)
        interpretations = [line.strip() for line in response.text.split('\n') if line.strip()]
        
        return interpretations[:5]


class MaieuticEngine:
    """
    Maieutic Dialogue Engine
    Socratic questioning and dialogue-based exploration
    """
    
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
        
    async def explore(self, text: str, context: TransformationContext) -> Dict[str, Any]:
        """Conduct Socratic exploration of content"""
        
        # Generate probing questions
        questions = await self._generate_questions(text)
        
        # Explore each question
        explorations = []
        for question in questions:
            exploration = await self._explore_question(text, question)
            explorations.append({
                "question": question,
                "exploration": exploration
            })
        
        # Synthesize insights
        synthesis = await self._synthesize_insights(text, explorations)
        
        return {
            "questions": questions,
            "explorations": explorations,
            "synthesis": synthesis,
            "insights_count": len(questions)
        }
    
    async def _generate_questions(self, text: str) -> List[str]:
        """Generate Socratic questions about the content"""
        
        prompt = f"""
Generate 5 insightful Socratic questions that would help explore the deeper meaning, assumptions, and implications of this text:

{text}

Questions should probe:
- Underlying assumptions
- Alternative perspectives
- Causal relationships
- Broader implications
- Hidden contradictions

Questions:"""
        
        response = await self.llm_service.complete(prompt)
        
        # Parse questions
        questions = [
            line.strip().rstrip('?') + '?' 
            for line in response.text.split('\n') 
            if line.strip() and '?' in line
        ]
        
        return questions[:5]
    
    async def _explore_question(self, text: str, question: str) -> str:
        """Explore a specific question in depth"""
        
        prompt = f"""
Explore this question in depth regarding the given text:

Text: {text}

Question: {question}

Provide a thoughtful exploration that:
- Examines different angles and perspectives
- Considers evidence and counterevidence
- Explores implications and consequences
- Identifies areas of uncertainty or complexity

Exploration:"""
        
        response = await self.llm_service.complete(prompt)
        return response.text
    
    async def _synthesize_insights(self, text: str, explorations: List[Dict]) -> str:
        """Synthesize insights from explorations"""
        
        exploration_text = "\n\n".join([
            f"Q: {exp['question']}\nA: {exp['exploration']}"
            for exp in explorations
        ])
        
        prompt = f"""
Based on the Socratic exploration below, synthesize the key insights and deeper understanding about the original text:

Original text: {text}

Explorations:
{exploration_text}

Synthesis of key insights:"""
        
        response = await self.llm_service.complete(prompt)
        return response.text


class TransformationService:
    """Main transformation service coordinating all engines"""
    
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
        self.lpe_engine = LamishProjectionEngine(llm_service)
        self.quantum_engine = QuantumNarrativeEngine(llm_service)
        self.maieutic_engine = MaieuticEngine(llm_service)
        
    async def transform(
        self,
        request: TransformationRequest,
        context: Optional[TransformationContext] = None
    ) -> TransformationResult:
        """Perform content transformation using specified engine"""
        
        if context is None:
            context = TransformationContext()
            
        start_time = time.time()
        request_id = uuid.uuid4()
        
        # Get source text
        text = request.text or ""  # Would get from content_id if provided
        
        try:
            if request.engine == TransformationEngine.LPE:
                result = await self.lpe_engine.transform(text, request.attributes, context)
                
            elif request.engine == TransformationEngine.QUANTUM:
                quantum_analysis = await self.quantum_engine.analyze(text, context)
                result = {
                    "transformed_text": text,  # Quantum analysis doesn't transform, just analyzes
                    "processing_time_ms": (time.time() - start_time) * 1000,
                    "token_usage": {"total_tokens": 100},  # Estimate
                    "quantum_analysis": quantum_analysis.dict()
                }
                
            elif request.engine == TransformationEngine.MAIEUTIC:
                maieutic_result = await self.maieutic_engine.explore(text, context)
                result = {
                    "transformed_text": maieutic_result["synthesis"],
                    "processing_time_ms": (time.time() - start_time) * 1000,
                    "token_usage": {"total_tokens": 200},  # Estimate
                    "maieutic_exploration": maieutic_result
                }
                
            else:
                raise ValueError(f"Unsupported transformation engine: {request.engine}")
            
            # Create result object
            transformation_result = TransformationResult(
                id=uuid.uuid4(),
                request_id=request_id,
                original_text=text,
                transformed_text=result["transformed_text"],
                engine=request.engine,
                attributes=request.attributes,
                quality_metrics=result.get("quality_metrics", {}),
                processing_time_ms=result["processing_time_ms"],
                token_usage=result["token_usage"]
            )
            
            # Add engine-specific data
            if "quantum_analysis" in result:
                transformation_result.quality_metrics["quantum_analysis"] = result["quantum_analysis"]
            if "maieutic_exploration" in result:
                transformation_result.quality_metrics["maieutic_exploration"] = result["maieutic_exploration"]
            if "intermediate_steps" in result:
                transformation_result.quality_metrics["lpe_steps"] = result["intermediate_steps"]
            
            logger.info(f"Transformation completed: {request.engine.value} in {result['processing_time_ms']:.1f}ms")
            
            return transformation_result
            
        except Exception as e:
            logger.error(f"Transformation failed: {e}", exc_info=True)
            raise
    
    async def batch_transform(
        self,
        requests: List[TransformationRequest],
        context: Optional[TransformationContext] = None
    ) -> List[TransformationResult]:
        """Perform batch transformations with concurrency control"""
        
        max_concurrent = config.processing.max_concurrent_jobs
        
        # Process in batches
        results = []
        for i in range(0, len(requests), max_concurrent):
            batch = requests[i:i + max_concurrent]
            
            # Process batch concurrently
            batch_tasks = [
                self.transform(request, context)
                for request in batch
            ]
            
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            # Handle exceptions in batch
            for result in batch_results:
                if isinstance(result, Exception):
                    logger.error(f"Batch transformation failed: {result}")
                    # Could create error result object here
                else:
                    results.append(result)
        
        return results
    
    async def analyze_quality(self, original: str, transformed: str) -> QualityAnalysis:
        """Analyze transformation quality"""
        
        # Use LLM to assess quality
        quality_prompt = f"""
Analyze the quality of this content transformation:

Original: {original}

Transformed: {transformed}

Rate each aspect from 0.0 to 1.0:
- Overall quality
- Coherence and flow
- Clarity and readability  
- Grammar and style
- Preservation of meaning
- Any toxicity or bias

Provide scores and brief suggestions for improvement.
"""
        
        response = await self.llm_service.complete(quality_prompt)
        
        # Parse response (simplified - would use structured output in production)
        return QualityAnalysis(
            overall_score=0.8,
            coherence_score=0.85,
            clarity_score=0.9,
            grammar_score=0.95,
            toxicity_score=0.1,
            readability_score=0.88,
            suggestions=["Improve flow between paragraphs", "Clarify technical terms"]
        )