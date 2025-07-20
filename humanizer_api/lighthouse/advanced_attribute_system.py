"""
Advanced Attribute System with Negative Scoping and Noetic Analysis
Implements sophisticated multi-dimensional attributes with filtered namespaces
and consciousness mapping for narrative analysis.
"""

import asyncio
import logging
import re
import json
import hashlib
from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Tuple, Any
from enum import Enum
from datetime import datetime
import numpy as np
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)

class AttributeType(Enum):
    """Enhanced attribute types for sophisticated analysis."""
    PERSONA = "persona"
    NAMESPACE = "namespace" 
    STYLE = "style"
    CONSCIOUSNESS_MAP = "consciousness_map"
    NOETIC_PATTERN = "noetic_pattern"
    SEMANTIC_CLUSTER = "semantic_cluster"
    INTENTIONAL_STRUCTURE = "intentional_structure"
    CONCEPTUAL_FILTER = "conceptual_filter"

class ScopeType(Enum):
    """Types of scoping for namespace filtering."""
    POSITIVE = "positive"  # Include these concepts
    NEGATIVE = "negative"  # Exclude these concepts
    FILTERED = "filtered"  # Transform these concepts through proxies

@dataclass
class SemanticConstraint:
    """Defines semantic constraints for name generation and filtering."""
    forbidden_patterns: List[str] = field(default_factory=list)
    required_patterns: List[str] = field(default_factory=list)
    phonetic_rules: Dict[str, Any] = field(default_factory=dict)
    semantic_distance_threshold: float = 0.8
    proper_noun_blacklist: Set[str] = field(default_factory=set)
    geographic_blacklist: Set[str] = field(default_factory=set)
    
@dataclass
class NoeticPattern:
    """Represents patterns of consciousness in narrative expression."""
    intentional_weight: float  # How much intention is behind the expression
    consciousness_depth: int  # Levels of awareness (1-5)
    projection_vector: List[float]  # Semantic direction of meaning projection
    meaning_coherence: float  # How well meaning maps to expression
    intersubjective_markers: List[str]  # Linguistic markers of shared understanding
    phenomenological_anchors: List[str]  # Connection points to lived experience

@dataclass
class AdvancedAttribute:
    """Sophisticated multi-dimensional attribute with scoping and analysis."""
    id: str
    name: str
    type: AttributeType
    description: str
    content: str
    
    # Core semantic properties
    semantic_vector: List[float] = field(default_factory=list)
    conceptual_density: float = 0.0
    abstraction_level: int = 1  # 1-5, concrete to abstract
    
    # Scoping and filtering
    scope_type: ScopeType = ScopeType.POSITIVE
    filtered_concepts: Set[str] = field(default_factory=set)
    proxy_mappings: Dict[str, str] = field(default_factory=dict)
    semantic_constraints: Optional[SemanticConstraint] = None
    
    # Noetic analysis
    noetic_patterns: List[NoeticPattern] = field(default_factory=list)
    consciousness_coherence: float = 0.0
    intentional_clarity: float = 0.0
    
    # Metadata and relationships
    source_content_hash: str = ""
    derivation_path: List[str] = field(default_factory=list)
    related_attributes: Set[str] = field(default_factory=set)
    confidence_score: float = 0.0
    validation_status: str = "pending"
    
    # Temporal tracking
    created: str = field(default_factory=lambda: datetime.now().isoformat())
    last_refined: str = field(default_factory=lambda: datetime.now().isoformat())
    usage_contexts: List[Dict[str, Any]] = field(default_factory=list)

class SemanticNameGenerator:
    """Generates pronounceable names that avoid proper nouns and geographical references."""
    
    def __init__(self):
        self.phoneme_patterns = self._load_phoneme_patterns()
        self.forbidden_roots = self._load_forbidden_roots()
        self.semantic_clusters = self._load_semantic_clusters()
        
    def _load_phoneme_patterns(self) -> Dict[str, List[str]]:
        """Load pronounceable phoneme patterns for name generation."""
        return {
            "syllable_onsets": ["bl", "br", "cl", "cr", "dr", "fl", "fr", "gl", "gr", "pl", "pr", "sc", "sk", "sl", "sm", "sn", "sp", "st", "sw", "tr", "tw", "th", "sh", "ch"],
            "vowel_clusters": ["a", "e", "i", "o", "u", "ae", "ai", "au", "ea", "ei", "ie", "oa", "ou"],
            "syllable_codas": ["ch", "ck", "dge", "gh", "ng", "nk", "ph", "sh", "tch", "th", "x", "ss", "ll", "nn", "rr"],
            "safe_consonants": ["b", "c", "d", "f", "g", "h", "j", "k", "l", "m", "n", "p", "q", "r", "s", "t", "v", "w", "x", "y", "z"]
        }
    
    def _load_forbidden_roots(self) -> Set[str]:
        """Load roots that should be avoided to prevent real-world associations."""
        return {
            # Earth geographical roots
            "america", "europe", "asia", "africa", "ocean", "pacific", "atlantic", "mediterranean",
            "london", "paris", "tokyo", "beijing", "moscow", "cairo", "delhi", "sydney",
            "earth", "terra", "world", "globe", "planet",
            
            # Common proper name roots
            "john", "mary", "david", "sarah", "michael", "elizabeth", "robert", "maria",
            "smith", "johnson", "williams", "brown", "jones", "garcia", "miller",
            
            # Religious/mythological references
            "god", "jesus", "buddha", "allah", "zeus", "thor", "apollo", "diana",
            "christian", "muslim", "jewish", "hindu", "catholic", "protestant",
            
            # Historical figures/events
            "napoleon", "caesar", "alexander", "cleopatra", "shakespeare", "newton",
            "einstein", "darwin", "lincoln", "washington", "gandhi", "churchill"
        }
    
    def _load_semantic_clusters(self) -> Dict[str, List[str]]:
        """Load semantic clusters for meaningful name generation."""
        return {
            "luminous": ["lum", "phos", "rad", "lux", "beam", "glow"],
            "crystalline": ["crys", "gem", "shard", "prism", "facet"],
            "flowing": ["flux", "stream", "riv", "cascade", "torr"],
            "atmospheric": ["aer", "nimb", "cirr", "strat", "vapor"],
            "temporal": ["chron", "temp", "epoch", "cycle", "phase"],
            "spatial": ["locus", "nexus", "vect", "coord", "matrix"],
            "cognitive": ["ment", "cogn", "nous", "intel", "percept"],
            "harmonic": ["reson", "vibr", "freq", "harmon", "tune"]
        }
    
    def generate_proxy_name(self, concept: str, semantic_category: str = "neutral") -> str:
        """Generate a pronounceable proxy name for a filtered concept."""
        
        # Extract semantic essence without forbidden elements
        essence = self._extract_semantic_essence(concept)
        
        # Select appropriate semantic cluster
        cluster_roots = self.semantic_clusters.get(semantic_category, ["gen", "form", "struct"])
        
        # Generate pronounceable syllables
        syllables = []
        target_length = np.random.choice([2, 3, 4], p=[0.4, 0.4, 0.2])
        
        for i in range(target_length):
            if i == 0:  # First syllable
                onset = np.random.choice(self.phoneme_patterns["syllable_onsets"])
                vowel = np.random.choice(self.phoneme_patterns["vowel_clusters"])
                if i == target_length - 1:  # Also last syllable
                    coda = np.random.choice([""] + self.phoneme_patterns["syllable_codas"][:5])
                else:
                    coda = ""
                syllables.append(onset + vowel + coda)
                
            elif i == target_length - 1:  # Last syllable
                if len(syllables) > 0:
                    vowel = np.random.choice(self.phoneme_patterns["vowel_clusters"])
                    coda = np.random.choice(self.phoneme_patterns["syllable_codas"][:8])
                    # Use semantic root in final syllable
                    root = np.random.choice(cluster_roots)
                    syllables.append(root[:2] + vowel + coda[-2:] if coda else "")
                    
            else:  # Middle syllable
                consonant = np.random.choice(self.phoneme_patterns["safe_consonants"])
                vowel = np.random.choice(self.phoneme_patterns["vowel_clusters"])
                syllables.append(consonant + vowel)
        
        # Combine and validate
        candidate_name = "".join(syllables).lower()
        
        # Ensure no forbidden roots
        for forbidden in self.forbidden_roots:
            if forbidden in candidate_name:
                # Regenerate with different roots
                return self.generate_proxy_name(concept, semantic_category)
        
        # Capitalize properly
        return candidate_name.capitalize()
    
    def _extract_semantic_essence(self, concept: str) -> Dict[str, Any]:
        """Extract the core semantic properties of a concept for proxy generation."""
        # Simple implementation - would use advanced NLP in production
        essence = {
            "abstract_level": len(concept.split()) > 2,
            "emotional_valence": 0.0,  # Would analyze sentiment
            "conceptual_weight": len(concept) / 10.0,
            "phonetic_pattern": re.findall(r'[aeiou]', concept.lower())
        }
        return essence
    
    def validate_name_safety(self, name: str) -> Tuple[bool, List[str]]:
        """Validate that a generated name doesn't conflict with real-world references."""
        issues = []
        
        # Check against forbidden roots
        name_lower = name.lower()
        for forbidden in self.forbidden_roots:
            if forbidden in name_lower:
                issues.append(f"Contains forbidden root: {forbidden}")
        
        # Check pronounceability
        vowel_count = len(re.findall(r'[aeiou]', name_lower))
        if vowel_count < 1:
            issues.append("Not pronounceable - insufficient vowels")
        
        # Check length appropriateness
        if len(name) < 3 or len(name) > 12:
            issues.append("Inappropriate length")
        
        return len(issues) == 0, issues

class NoeticAnalyzer:
    """Analyzes consciousness patterns and intentional structures in narrative content."""
    
    def __init__(self):
        self.consciousness_markers = self._load_consciousness_markers()
        self.intentional_patterns = self._load_intentional_patterns()
        
    def _load_consciousness_markers(self) -> Dict[str, List[str]]:
        """Load linguistic markers that indicate different levels of consciousness."""
        return {
            "direct_awareness": ["I realize", "I understand", "I see that", "it becomes clear", "I recognize"],
            "reflective_thought": ["I think", "I believe", "it seems", "perhaps", "I wonder"],
            "metacognitive": ["I know that I", "I'm aware of thinking", "my understanding of", "how I perceive"],
            "phenomenological": ["I experience", "it feels like", "my sense is", "I'm struck by", "it appears to me"],
            "intersubjective": ["we understand", "others would see", "anyone can see", "it's clear to all", "universally"]
        }
    
    def _load_intentional_patterns(self) -> Dict[str, List[str]]:
        """Load patterns that indicate intentional meaning projection."""
        return {
            "meaning_projection": ["what I mean is", "the point is", "what I'm getting at", "to put it simply"],
            "emphasis_markers": ["most importantly", "especially", "particularly", "above all", "crucially"],
            "clarification": ["in other words", "that is", "specifically", "namely", "to be precise"],
            "experiential_grounding": ["in my experience", "from what I've seen", "based on", "having lived through"],
            "universal_claims": ["always", "never", "everyone", "no one", "everything", "nothing"]
        }
    
    def analyze_noetic_patterns(self, text: str) -> List[NoeticPattern]:
        """Analyze text for patterns of consciousness and intentional meaning."""
        patterns = []
        sentences = self._segment_sentences(text)
        
        for sentence in sentences:
            pattern = self._analyze_sentence_consciousness(sentence)
            if pattern:
                patterns.append(pattern)
        
        return patterns
    
    def _segment_sentences(self, text: str) -> List[str]:
        """Segment text into sentences for analysis."""
        # Simple implementation - would use spaCy or NLTK in production
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _analyze_sentence_consciousness(self, sentence: str) -> Optional[NoeticPattern]:
        """Analyze a single sentence for consciousness patterns."""
        sentence_lower = sentence.lower()
        
        # Calculate intentional weight
        intentional_weight = 0.0
        for pattern_type, markers in self.intentional_patterns.items():
            for marker in markers:
                if marker in sentence_lower:
                    intentional_weight += 0.2
        
        # Determine consciousness depth
        consciousness_depth = 1
        for level, markers in self.consciousness_markers.items():
            for marker in markers:
                if marker in sentence_lower:
                    if level == "metacognitive":
                        consciousness_depth = max(consciousness_depth, 4)
                    elif level == "phenomenological":
                        consciousness_depth = max(consciousness_depth, 3)
                    elif level == "reflective_thought":
                        consciousness_depth = max(consciousness_depth, 2)
        
        # Generate simple projection vector (would use embeddings in production)
        projection_vector = [float(len(sentence)), float(intentional_weight), float(consciousness_depth)]
        
        # Calculate meaning coherence
        meaning_coherence = min(1.0, intentional_weight / 2.0 + 0.3)
        
        # Extract intersubjective markers
        intersubjective_markers = []
        for marker in self.consciousness_markers.get("intersubjective", []):
            if marker in sentence_lower:
                intersubjective_markers.append(marker)
        
        # Extract phenomenological anchors
        phenomenological_anchors = []
        for marker in self.consciousness_markers.get("phenomenological", []):
            if marker in sentence_lower:
                phenomenological_anchors.append(marker)
        
        if intentional_weight > 0.1 or consciousness_depth > 1:
            return NoeticPattern(
                intentional_weight=intentional_weight,
                consciousness_depth=consciousness_depth,
                projection_vector=projection_vector,
                meaning_coherence=meaning_coherence,
                intersubjective_markers=intersubjective_markers,
                phenomenological_anchors=phenomenological_anchors
            )
        
        return None

class AdvancedAttributeGenerator:
    """Generates sophisticated attributes with negative scoping and noetic analysis."""
    
    def __init__(self):
        self.name_generator = SemanticNameGenerator()
        self.noetic_analyzer = NoeticAnalyzer()
        self.attribute_cache = {}
        
    async def generate_from_content(self, content: str, target_namespace: str = None, 
                                  negative_scope: Set[str] = None) -> List[AdvancedAttribute]:
        """Generate advanced attributes from content with optional negative scoping."""
        
        if negative_scope is None:
            negative_scope = set()
        
        attributes = []
        
        # Generate base attributes
        persona_attrs = await self._extract_persona_attributes(content, negative_scope)
        namespace_attrs = await self._extract_namespace_attributes(content, target_namespace, negative_scope)
        style_attrs = await self._extract_style_attributes(content, negative_scope)
        
        # Generate noetic attributes
        noetic_attrs = await self._extract_noetic_attributes(content)
        
        attributes.extend(persona_attrs)
        attributes.extend(namespace_attrs)
        attributes.extend(style_attrs)
        attributes.extend(noetic_attrs)
        
        # Apply negative scoping and filtering
        filtered_attributes = self._apply_negative_scoping(attributes, negative_scope)
        
        # Generate semantic relationships
        self._generate_attribute_relationships(filtered_attributes)
        
        return filtered_attributes
    
    async def _extract_persona_attributes(self, content: str, negative_scope: Set[str]) -> List[AdvancedAttribute]:
        """Extract sophisticated persona attributes."""
        # Analyze consciousness patterns
        noetic_patterns = self.noetic_analyzer.analyze_noetic_patterns(content)
        
        # Calculate persona characteristics
        consciousness_coherence = np.mean([p.meaning_coherence for p in noetic_patterns]) if noetic_patterns else 0.0
        intentional_clarity = np.mean([p.intentional_weight for p in noetic_patterns]) if noetic_patterns else 0.0
        
        # Generate persona name that avoids negative scope
        persona_essence = self._extract_persona_essence(content)
        proxy_name = self.name_generator.generate_proxy_name(persona_essence, "cognitive")
        
        persona = AdvancedAttribute(
            id=f"persona_{hashlib.md5(content.encode()).hexdigest()[:8]}",
            name=proxy_name,
            type=AttributeType.PERSONA,
            description=f"A consciousness pattern characterized by {persona_essence}",
            content=f"This persona demonstrates {persona_essence} through narrative expression with consciousness coherence of {consciousness_coherence:.2f}",
            noetic_patterns=noetic_patterns,
            consciousness_coherence=consciousness_coherence,
            intentional_clarity=intentional_clarity,
            scope_type=ScopeType.FILTERED,
            filtered_concepts=negative_scope,
            confidence_score=min(1.0, consciousness_coherence + intentional_clarity)
        )
        
        return [persona]
    
    async def _extract_namespace_attributes(self, content: str, target_namespace: str, 
                                          negative_scope: Set[str]) -> List[AdvancedAttribute]:
        """Extract namespace attributes with negative scoping."""
        
        # Identify conceptual domains in content
        conceptual_domains = self._identify_conceptual_domains(content)
        
        # Filter out negative scope concepts
        filtered_domains = [domain for domain in conceptual_domains 
                          if not any(neg in domain.lower() for neg in negative_scope)]
        
        # Generate proxy namespace if target is specified
        if target_namespace:
            proxy_mappings = {}
            for domain in conceptual_domains:
                if any(neg in domain.lower() for neg in negative_scope):
                    proxy_name = self.name_generator.generate_proxy_name(domain, "spatial")
                    proxy_mappings[domain] = proxy_name
            
            namespace = AdvancedAttribute(
                id=f"namespace_{hashlib.md5(target_namespace.encode()).hexdigest()[:8]}",
                name=target_namespace,
                type=AttributeType.NAMESPACE,
                description=f"Conceptual domain excluding {', '.join(negative_scope)}",
                content=f"Universe of discourse encompassing {', '.join(filtered_domains)} with proxy mappings for filtered concepts",
                scope_type=ScopeType.NEGATIVE,
                filtered_concepts=negative_scope,
                proxy_mappings=proxy_mappings,
                confidence_score=0.8
            )
            
            return [namespace]
        
        return []
    
    async def _extract_style_attributes(self, content: str, negative_scope: Set[str]) -> List[AdvancedAttribute]:
        """Extract sophisticated style attributes."""
        # Analyze linguistic patterns
        style_markers = self._analyze_linguistic_style(content)
        
        # Generate style name avoiding negative scope
        style_essence = self._extract_style_essence(style_markers)
        proxy_name = self.name_generator.generate_proxy_name(style_essence, "harmonic")
        
        style = AdvancedAttribute(
            id=f"style_{hashlib.md5(content.encode()).hexdigest()[:8]}",
            name=proxy_name,
            type=AttributeType.STYLE,
            description=f"Linguistic expression pattern characterized by {style_essence}",
            content=f"This style employs {style_essence} with markers: {', '.join(style_markers[:3])}",
            scope_type=ScopeType.FILTERED,
            filtered_concepts=negative_scope,
            confidence_score=0.7
        )
        
        return [style]
    
    async def _extract_noetic_attributes(self, content: str) -> List[AdvancedAttribute]:
        """Extract noetic and consciousness-mapping attributes."""
        noetic_patterns = self.noetic_analyzer.analyze_noetic_patterns(content)
        
        if not noetic_patterns:
            return []
        
        # Create consciousness map attribute
        consciousness_map = AdvancedAttribute(
            id=f"consciousness_map_{hashlib.md5(content.encode()).hexdigest()[:8]}",
            name="Consciousness Topology",
            type=AttributeType.CONSCIOUSNESS_MAP,
            description="Mapping of intentional structures and meaning projections in narrative",
            content=f"Contains {len(noetic_patterns)} consciousness patterns with mean depth {np.mean([p.consciousness_depth for p in noetic_patterns]):.1f}",
            noetic_patterns=noetic_patterns,
            confidence_score=0.9
        )
        
        return [consciousness_map]
    
    def _apply_negative_scoping(self, attributes: List[AdvancedAttribute], 
                               negative_scope: Set[str]) -> List[AdvancedAttribute]:
        """Apply negative scoping filters to attributes."""
        filtered_attributes = []
        
        for attr in attributes:
            # Check if attribute content contains negative scope concepts
            attr_text = (attr.name + " " + attr.description + " " + attr.content).lower()
            
            contains_filtered = any(neg.lower() in attr_text for neg in negative_scope)
            
            if contains_filtered:
                # Generate proxy mappings for filtered concepts
                attr.scope_type = ScopeType.FILTERED
                attr.filtered_concepts = negative_scope
                
                # Update content to use proxy names
                updated_content = attr.content
                for neg_concept in negative_scope:
                    if neg_concept.lower() in attr_text:
                        proxy_name = self.name_generator.generate_proxy_name(neg_concept, "neutral")
                        attr.proxy_mappings[neg_concept] = proxy_name
                        updated_content = updated_content.replace(neg_concept, proxy_name)
                
                attr.content = updated_content
            
            filtered_attributes.append(attr)
        
        return filtered_attributes
    
    def _generate_attribute_relationships(self, attributes: List[AdvancedAttribute]):
        """Generate semantic relationships between attributes."""
        for i, attr1 in enumerate(attributes):
            for attr2 in attributes[i+1:]:
                # Simple similarity based on shared noetic patterns
                if attr1.noetic_patterns and attr2.noetic_patterns:
                    similarity = self._calculate_noetic_similarity(attr1.noetic_patterns, attr2.noetic_patterns)
                    if similarity > 0.5:
                        attr1.related_attributes.add(attr2.id)
                        attr2.related_attributes.add(attr1.id)
    
    def _calculate_noetic_similarity(self, patterns1: List[NoeticPattern], 
                                   patterns2: List[NoeticPattern]) -> float:
        """Calculate similarity between noetic pattern sets."""
        if not patterns1 or not patterns2:
            return 0.0
        
        # Simple similarity based on consciousness depth overlap
        depths1 = set(p.consciousness_depth for p in patterns1)
        depths2 = set(p.consciousness_depth for p in patterns2)
        
        intersection = len(depths1.intersection(depths2))
        union = len(depths1.union(depths2))
        
        return intersection / union if union > 0 else 0.0
    
    def _extract_persona_essence(self, content: str) -> str:
        """Extract core persona characteristics from content."""
        # Simple implementation - would use advanced NLP
        if "analytical" in content.lower() or "logical" in content.lower():
            return "analytical_reasoning"
        elif "creative" in content.lower() or "imaginative" in content.lower():
            return "creative_expression"
        elif "empathetic" in content.lower() or "understanding" in content.lower():
            return "empathetic_awareness"
        else:
            return "reflective_consciousness"
    
    def _identify_conceptual_domains(self, content: str) -> List[str]:
        """Identify conceptual domains present in content."""
        # Simple implementation - would use advanced semantic analysis
        domains = []
        content_lower = content.lower()
        
        domain_markers = {
            "technology": ["computer", "digital", "software", "algorithm", "data"],
            "nature": ["tree", "forest", "ocean", "mountain", "sky", "earth"],
            "society": ["community", "culture", "people", "social", "human"],
            "philosophy": ["meaning", "purpose", "existence", "consciousness", "truth"],
            "emotion": ["feeling", "emotion", "love", "fear", "joy", "sadness"]
        }
        
        for domain, markers in domain_markers.items():
            if any(marker in content_lower for marker in markers):
                domains.append(domain)
        
        return domains
    
    def _analyze_linguistic_style(self, content: str) -> List[str]:
        """Analyze linguistic style markers in content."""
        markers = []
        content_lower = content.lower()
        
        style_patterns = {
            "formal": ["furthermore", "moreover", "consequently", "nevertheless"],
            "casual": ["like", "you know", "kinda", "pretty much"],
            "academic": ["thus", "therefore", "hypothesis", "analysis"],
            "poetic": ["beautiful", "flowing", "rhythm", "imagery"],
            "technical": ["system", "process", "function", "parameter"]
        }
        
        for style, patterns in style_patterns.items():
            if any(pattern in content_lower for pattern in patterns):
                markers.append(style)
        
        return markers
    
    def _extract_style_essence(self, style_markers: List[str]) -> str:
        """Extract core style essence from markers."""
        if not style_markers:
            return "neutral_expression"
        
        # Prioritize style characteristics
        if "formal" in style_markers:
            return "formal_discourse"
        elif "academic" in style_markers:
            return "scholarly_exposition"
        elif "poetic" in style_markers:
            return "lyrical_expression"
        elif "technical" in style_markers:
            return "technical_precision"
        else:
            return "conversational_flow"


# Example usage and testing
if __name__ == "__main__":
    async def test_advanced_attributes():
        generator = AdvancedAttributeGenerator()
        
        # Test content with Earth references that should be filtered
        test_content = """
        I believe that understanding consciousness requires examining how we project meaning 
        through language. In my experience living on Earth, particularly in American society, 
        I've noticed that people often express deeper intentions than their surface words convey.
        When I think about the Pacific Ocean, I'm struck by how it represents both separation 
        and connection - much like human consciousness itself.
        """
        
        # Define negative scope to filter Earth references
        negative_scope = {"Earth", "American", "Pacific Ocean", "society"}
        
        attributes = await generator.generate_from_content(
            test_content, 
            target_namespace="Filtered Reality",
            negative_scope=negative_scope
        )
        
        print("Generated Advanced Attributes:")
        for attr in attributes:
            print(f"\nType: {attr.type.value}")
            print(f"Name: {attr.name}")
            print(f"Description: {attr.description}")
            print(f"Scope: {attr.scope_type.value}")
            if attr.proxy_mappings:
                print(f"Proxy Mappings: {attr.proxy_mappings}")
            if attr.noetic_patterns:
                print(f"Noetic Patterns: {len(attr.noetic_patterns)} consciousness patterns detected")
            print(f"Confidence: {attr.confidence_score:.2f}")
    
    # Run test
    asyncio.run(test_advanced_attributes())