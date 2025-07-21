"""
Advanced Attribute Balancing System for Humanizer Lighthouse

This module addresses the core issue of templated narrative outputs by implementing
sophisticated attribute balancing that preserves narrative essence while reducing
overpowering linguistic patterns.

Key innovations:
- Semantic weight balancing to prevent attribute dominance
- Narrative DNA preservation during transformation
- Context-aware prompt engineering with dynamic prompts
- Conflict detection and resolution between attribute combinations
- Natural language grounding to avoid template artifacts
"""

import json
import logging
import hashlib
import re
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

class AttributeType(Enum):
    PERSONA = "persona"
    NAMESPACE = "namespace" 
    STYLE = "style"
    TONE = "tone"
    VOICE = "voice"
    PERSPECTIVE = "perspective"

class InfluenceLevel(Enum):
    SUBTLE = "subtle"       # 0.1-0.3 weight
    MODERATE = "moderate"   # 0.3-0.6 weight  
    STRONG = "strong"       # 0.6-0.8 weight
    DOMINANT = "dominant"   # 0.8-1.0 weight

@dataclass
class AttributeSignature:
    """Represents the linguistic signature of an attribute."""
    name: str
    type: AttributeType
    semantic_markers: List[str] = field(default_factory=list)
    syntactic_patterns: List[str] = field(default_factory=list)
    lexical_preferences: List[str] = field(default_factory=list)
    template_phrases: List[str] = field(default_factory=list)
    influence_weight: float = 0.5
    conflict_tags: Set[str] = field(default_factory=set)
    embedding: Optional[List[float]] = None

@dataclass
class NarrativeDNA:
    """Captures the essential narrative elements that must be preserved."""
    core_entities: List[str] = field(default_factory=list)
    relationship_patterns: List[str] = field(default_factory=list) 
    causal_chains: List[str] = field(default_factory=list)
    emotional_trajectory: List[str] = field(default_factory=list)
    thematic_elements: List[str] = field(default_factory=list)
    narrative_structure: str = ""
    semantic_density: float = 0.0
    complexity_score: float = 0.0

@dataclass
class BalancingResult:
    """Result of attribute balancing analysis."""
    is_balanced: bool
    dominant_attributes: List[str] = field(default_factory=list)
    template_risk_score: float = 0.0
    conflicts: List[str] = field(default_factory=list)
    recommended_adjustments: Dict[str, float] = field(default_factory=dict)
    preservation_score: float = 0.0

class NarrativeDNAExtractor:
    """Extracts and analyzes the essential DNA of narratives."""
    
    def __init__(self):
        try:
            self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        except:
            logger.warning("SentenceTransformer not available, using mock embeddings")
            self.embedder = None
    
    def extract_dna(self, narrative: str) -> NarrativeDNA:
        """Extract the essential DNA from a narrative."""
        dna = NarrativeDNA()
        
        # Extract core entities (people, places, things)
        dna.core_entities = self._extract_entities(narrative)
        
        # Identify relationship patterns
        dna.relationship_patterns = self._extract_relationships(narrative)
        
        # Map causal chains
        dna.causal_chains = self._extract_causal_chains(narrative)
        
        # Track emotional trajectory
        dna.emotional_trajectory = self._extract_emotional_trajectory(narrative)
        
        # Identify thematic elements
        dna.thematic_elements = self._extract_themes(narrative)
        
        # Analyze narrative structure
        dna.narrative_structure = self._analyze_structure(narrative)
        
        # Calculate complexity metrics
        dna.semantic_density = self._calculate_semantic_density(narrative)
        dna.complexity_score = self._calculate_complexity(narrative)
        
        return dna
    
    def _extract_entities(self, text: str) -> List[str]:
        """Extract key entities from narrative."""
        # Simple entity extraction using patterns
        entities = []
        
        # Names (capitalized words)
        names = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        entities.extend(names[:10])  # Limit to top 10
        
        # Important nouns (look for repeated significant words)
        words = re.findall(r'\b[a-z]+\b', text.lower())
        word_freq = {}
        for word in words:
            if len(word) > 3:  # Filter short words
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Add frequent meaningful nouns
        frequent_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
        entities.extend([word for word, freq in frequent_words if freq > 1])
        
        return list(set(entities))
    
    def _extract_relationships(self, text: str) -> List[str]:
        """Extract relationship patterns."""
        relationships = []
        
        # Look for relationship indicators
        relationship_patterns = [
            r'(\w+)\s+(loves?|hates?|fears?|trusts?|betrays?)\s+(\w+)',
            r'(\w+)\s+(is|was|becomes?)\s+([^.]+)',
            r'(\w+)\s+(and|with|against)\s+(\w+)',
        ]
        
        for pattern in relationship_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches[:5]:  # Limit matches
                relationships.append(' '.join(match))
        
        return relationships
    
    def _extract_causal_chains(self, text: str) -> List[str]:
        """Extract cause-effect relationships."""
        causal_chains = []
        
        # Look for causal indicators
        causal_patterns = [
            r'because\s+([^.]+)',
            r'therefore\s+([^.]+)',
            r'as a result\s+([^.]+)',
            r'consequently\s+([^.]+)',
            r'which led to\s+([^.]+)',
        ]
        
        for pattern in causal_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            causal_chains.extend(matches[:3])
        
        return causal_chains
    
    def _extract_emotional_trajectory(self, text: str) -> List[str]:
        """Extract emotional progression."""
        # Simple emotion detection
        emotions = {
            'joy': ['happy', 'joy', 'celebration', 'triumph', 'elated'],
            'fear': ['afraid', 'terror', 'scared', 'frightened', 'dread'],
            'anger': ['angry', 'rage', 'furious', 'mad', 'enraged'],
            'sadness': ['sad', 'grief', 'sorrow', 'melancholy', 'despair'],
            'surprise': ['surprise', 'shocked', 'amazed', 'astonished'],
            'love': ['love', 'affection', 'adoration', 'cherish'],
        }
        
        emotional_trajectory = []
        sentences = text.split('.')
        
        for i, sentence in enumerate(sentences):
            sentence_lower = sentence.lower()
            for emotion, words in emotions.items():
                if any(word in sentence_lower for word in words):
                    emotional_trajectory.append(f"{i}: {emotion}")
                    break
        
        return emotional_trajectory[:10]
    
    def _extract_themes(self, text: str) -> List[str]:
        """Extract thematic elements."""
        themes = []
        
        # Look for thematic keywords
        theme_patterns = {
            'power': ['power', 'control', 'authority', 'dominance', 'rule'],
            'love': ['love', 'romance', 'relationship', 'marriage', 'partnership'],
            'death': ['death', 'mortality', 'dying', 'killed', 'perish'],
            'growth': ['growth', 'development', 'change', 'transformation', 'evolution'],
            'conflict': ['conflict', 'war', 'battle', 'fight', 'struggle'],
            'justice': ['justice', 'fairness', 'right', 'wrong', 'moral'],
            'identity': ['identity', 'self', 'who am i', 'belonging', 'purpose'],
        }
        
        text_lower = text.lower()
        for theme, keywords in theme_patterns.items():
            if any(keyword in text_lower for keyword in keywords):
                themes.append(theme)
        
        return themes
    
    def _analyze_structure(self, text: str) -> str:
        """Analyze narrative structure."""
        sentences = text.split('.')
        paragraphs = text.split('\n\n')
        
        if len(sentences) < 3:
            return "minimal"
        elif len(paragraphs) > 5:
            return "complex"
        elif len(sentences) > 20:
            return "extended"
        else:
            return "standard"
    
    def _calculate_semantic_density(self, text: str) -> float:
        """Calculate semantic density (meaningful words per total words)."""
        words = re.findall(r'\b\w+\b', text.lower())
        if not words:
            return 0.0
        
        # Simple meaningful word detection
        meaningful_words = [w for w in words if len(w) > 3 and w not in {
            'the', 'and', 'that', 'have', 'for', 'not', 'with', 'you', 'this', 'but',
            'his', 'from', 'they', 'she', 'her', 'been', 'than', 'what', 'were'
        }]
        
        return len(meaningful_words) / len(words)
    
    def _calculate_complexity(self, text: str) -> float:
        """Calculate narrative complexity score."""
        sentences = text.split('.')
        words = text.split()
        
        if not sentences or not words:
            return 0.0
        
        # Average sentence length
        avg_sentence_length = len(words) / len(sentences)
        
        # Vocabulary diversity
        unique_words = len(set(word.lower() for word in words))
        vocab_diversity = unique_words / len(words) if words else 0
        
        # Complexity score (0-1)
        complexity = min(1.0, (avg_sentence_length / 20.0) * 0.5 + vocab_diversity * 0.5)
        return complexity

class AttributeBalancer:
    """Advanced system for balancing narrative transformation attributes."""
    
    def __init__(self):
        self.dna_extractor = NarrativeDNAExtractor()
        self.attribute_registry: Dict[str, AttributeSignature] = {}
        self.load_attribute_signatures()
    
    def load_attribute_signatures(self):
        """Load known attribute signatures that can cause templating."""
        # Load common problematic patterns
        signatures = [
            AttributeSignature(
                name="storyteller",
                type=AttributeType.PERSONA,
                template_phrases=[
                    "Once upon a time", "In a land far away", "The tale begins",
                    "weaves the tale", "draws the audience", "unfolds in"
                ],
                semantic_markers=["narrative", "story", "tale", "chronicles"],
                influence_weight=0.8,
                conflict_tags={"formal", "technical", "scientific"}
            ),
            AttributeSignature(
                name="philosopher",
                type=AttributeType.PERSONA,
                template_phrases=[
                    "Through contemplative analysis", "deeper truths", "universal patterns",
                    "reveals profound questions", "meditation on", "examined through"
                ],
                semantic_markers=["truth", "universal", "existence", "meaning"],
                influence_weight=0.7,
                conflict_tags={"casual", "simple", "direct"}
            ),
            AttributeSignature(
                name="scientist",
                type=AttributeType.PERSONA,
                template_phrases=[
                    "Empirical observation suggests", "according to scientific methodology",
                    "data indicates", "documented according to", "systematic analysis"
                ],
                semantic_markers=["empirical", "systematic", "methodology", "data"],
                influence_weight=0.6,
                conflict_tags={"poetic", "mystical", "artistic"}
            ),
            AttributeSignature(
                name="lamish-galaxy",
                type=AttributeType.NAMESPACE,
                template_phrases=[
                    "resonant frequencies", "Crystal Citadel", "Frequency Masters",
                    "harmonic wealth", "Pulse-Master", "song-cycle"
                ],
                semantic_markers=["frequency", "resonance", "harmonic", "crystal"],
                influence_weight=0.9,  # Very high influence
                conflict_tags={"realistic", "contemporary", "earthbound"}
            ),
            AttributeSignature(
                name="poetic",
                type=AttributeType.STYLE,
                template_phrases=[
                    "crystalline spires where", "star-winds sing", "cosmic dance",
                    "rhythmic verse", "words dance like starlight", "lyrical grace"
                ],
                semantic_markers=["lyrical", "rhythmic", "flowing", "ethereal"],
                influence_weight=0.8,
                conflict_tags={"technical", "dry", "factual"}
            ),
        ]
        
        for sig in signatures:
            self.attribute_registry[sig.name] = sig
    
    def analyze_combination(self, persona: str, namespace: str, style: str, narrative: str) -> BalancingResult:
        """Analyze if attribute combination will create balanced output."""
        result = BalancingResult(is_balanced=False)  # Will be updated based on analysis
        
        # Extract narrative DNA
        narrative_dna = self.dna_extractor.extract_dna(narrative)
        
        # Get attribute signatures
        attributes = [
            self.attribute_registry.get(persona),
            self.attribute_registry.get(namespace), 
            self.attribute_registry.get(style)
        ]
        
        # Remove None values
        attributes = [attr for attr in attributes if attr is not None]
        
        if not attributes:
            result.is_balanced = True
            result.preservation_score = 1.0
            return result
        
        # Check for dominance
        total_weight = sum(attr.influence_weight for attr in attributes)
        max_weight = max(attr.influence_weight for attr in attributes)
        
        if max_weight / total_weight > 0.6:  # Single attribute dominates
            dominant_attr = max(attributes, key=lambda x: x.influence_weight)
            result.dominant_attributes.append(dominant_attr.name)
            result.is_balanced = False
        
        # Calculate template risk
        template_phrases = []
        for attr in attributes:
            template_phrases.extend(attr.template_phrases)
        
        result.template_risk_score = min(1.0, len(template_phrases) / 10.0)
        
        # Check for conflicts
        all_conflict_tags = set()
        for attr in attributes:
            all_conflict_tags.update(attr.conflict_tags)
        
        attr_names = {attr.name for attr in attributes}
        conflicts = all_conflict_tags.intersection(attr_names)
        result.conflicts = list(conflicts)
        
        # Calculate preservation score based on narrative complexity
        preservation_factors = [
            narrative_dna.semantic_density,
            min(1.0, narrative_dna.complexity_score * 2),  # Boost complexity impact
            1.0 - result.template_risk_score,
            1.0 if not result.conflicts else 0.5
        ]
        result.preservation_score = sum(preservation_factors) / len(preservation_factors)
        
        # Generate recommendations
        if not result.is_balanced:
            for attr in attributes:
                if attr.name in result.dominant_attributes:
                    # Reduce dominant attribute weight
                    result.recommended_adjustments[attr.name] = max(0.3, attr.influence_weight - 0.3)
                else:
                    # Boost non-dominant attributes
                    result.recommended_adjustments[attr.name] = min(0.8, attr.influence_weight + 0.2)
        
        result.is_balanced = (
            result.template_risk_score < 0.7 and
            len(result.conflicts) == 0 and 
            len(result.dominant_attributes) == 0
        )
        
        return result
    
    def generate_balanced_prompts(self, persona: str, namespace: str, style: str, 
                                narrative_dna: NarrativeDNA) -> Dict[str, str]:
        """Generate context-aware, balanced prompts for transformation."""
        
        # Get balancing analysis
        analysis = self.analyze_combination(persona, namespace, style, "")
        
        # Base prompts that focus on preservation rather than prescription
        base_prompts = {
            'deconstruct': self._generate_deconstruct_prompt(narrative_dna),
            'map': self._generate_map_prompt(namespace, narrative_dna, analysis),
            'reconstruct': self._generate_reconstruct_prompt(persona, narrative_dna, analysis),
            'stylize': self._generate_stylize_prompt(style, narrative_dna, analysis),
            'reflect': self._generate_reflect_prompt(namespace, narrative_dna)
        }
        
        return base_prompts
    
    def _generate_deconstruct_prompt(self, dna: NarrativeDNA) -> str:
        """Generate DNA-aware deconstruct prompt."""
        complexity_instruction = ""
        if dna.complexity_score > 0.7:
            complexity_instruction = "This is a complex narrative with multiple layers. Ensure you capture the full richness."
        elif dna.complexity_score < 0.3:
            complexity_instruction = "This is a concise narrative. Focus on the essential elements without over-analyzing."
        
        return f"""Extract the core structural elements of this narrative while preserving its essential DNA.

{complexity_instruction}

Identify these elements as they appear in the text:
- WHO: The actual entities, characters, or forces involved
- WHAT: The specific actions, events, or developments that occur  
- WHY: The motivations, conflicts, or driving forces
- HOW: The methods, processes, or approaches used
- OUTCOME: The concrete results, consequences, or resolutions

Focus on what actually happens in this specific story, not generic story categories.
Preserve the unique relationships and causal connections."""
    
    def _generate_map_prompt(self, namespace: str, dna: NarrativeDNA, analysis: BalancingResult) -> str:
        """Generate mapping prompt that avoids template artifacts."""
        
        weight_instruction = ""
        if analysis.template_risk_score > 0.6:
            weight_instruction = """
IMPORTANT: Create natural equivalents that feel organic to the target universe.
Avoid formulaic or templated language patterns. Focus on meaningful correspondence."""
        
        preservation_note = ""
        if dna.relationship_patterns:
            preservation_note = f"\nEnsure these key relationships are preserved: {', '.join(dna.relationship_patterns[:3])}"
        
        return f"""Create specific equivalents for each element in the {namespace} universe.

{weight_instruction}

For each extracted element, identify a natural {namespace} equivalent that:
- Serves the same narrative function
- Maintains the same relationships to other elements  
- Preserves the same emotional weight and significance
- Fits organically within {namespace} without forced connections

Format as clear correspondences: [Original] → [Equivalent]
{preservation_note}

Focus on functional equivalence rather than surface similarity."""
    
    def _generate_reconstruct_prompt(self, persona: str, dna: NarrativeDNA, analysis: BalancingResult) -> str:
        """Generate reconstruction prompt with persona balancing."""
        
        persona_instruction = f"from the {persona} perspective"
        if analysis.template_risk_score > 0.7:
            persona_instruction = f"in a way that reflects {persona} understanding, but without forcing artificial language patterns"
        
        structure_note = ""
        if dna.narrative_structure == "complex":
            structure_note = "Maintain the narrative's complexity and layered structure."
        elif dna.narrative_structure == "minimal":
            structure_note = "Preserve the concise, focused nature of the narrative."
        
        return f"""Reconstruct the complete narrative {persona_instruction}.

{structure_note}

Using the mapped elements, tell the same story with:
- The same sequence of events and causal relationships
- The same character dynamics and emotional trajectory
- The same conflicts, tensions, and resolutions
- The same thematic weight and significance

Express this through {persona} understanding while keeping the core story intact.
Let the {persona} perspective emerge naturally from how they would see and interpret these events,
not from imposed linguistic formulas."""
    
    def _generate_stylize_prompt(self, style: str, dna: NarrativeDNA, analysis: BalancingResult) -> str:
        """Generate style prompt that preserves narrative essence."""
        
        style_guidance = f"Apply {style} style characteristics"
        if analysis.template_risk_score > 0.6:
            style_guidance = f"Adjust the language toward {style} style in a natural way"
        
        preservation_emphasis = ""
        if dna.semantic_density > 0.6:
            preservation_emphasis = "\nThis narrative has rich semantic content - preserve all meaningful elements."
        
        return f"""{style_guidance} while preserving all narrative content.

Modify only the expression, not the story:
- Adjust word choice, sentence rhythm, and tone to reflect {style} characteristics
- Keep all plot points, character actions, and story outcomes unchanged
- Maintain the emotional trajectory and thematic elements
- Preserve the causal relationships and story logic
{preservation_emphasis}

The goal is stylistic adaptation, not story alteration."""
    
    def _generate_reflect_prompt(self, namespace: str, dna: NarrativeDNA) -> str:
        """Generate reflection prompt focused on genuine insight."""
        
        theme_focus = ""
        if dna.thematic_elements:
            theme_focus = f"\nPay particular attention to how the themes of {', '.join(dna.thematic_elements)} are illuminated."
        
        return f"""Provide analytical commentary on this narrative transformation.

Examine how viewing the story through the {namespace} lens reveals or emphasizes:
- Universal patterns that transcend the specific setting
- Deeper structures that become visible through the transformation
- New perspectives on the original themes and conflicts
- Insights that emerge from this particular allegorical mapping
{theme_focus}

Focus on genuine analytical insights rather than generic commentary about transformation."""

def create_balanced_transformation_pipeline():
    """Factory function to create a balanced transformation pipeline."""
    return AttributeBalancer()

# Export the main classes and functions
__all__ = [
    'AttributeBalancer',
    'NarrativeDNAExtractor', 
    'AttributeSignature',
    'NarrativeDNA',
    'BalancingResult',
    'create_balanced_transformation_pipeline'
]