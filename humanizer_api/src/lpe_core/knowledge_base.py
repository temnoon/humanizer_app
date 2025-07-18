"""
Knowledge base for persona, namespace, and style definitions with RAG capabilities.

This module implements the vision for accumulating and enriching definitions 
based on successful transformations, creating a growing understanding of
Lamish projection elements.
"""
import json
import numpy as np
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import hashlib

logger = logging.getLogger(__name__)

@dataclass
class LamishConcept:
    """A concept in the Lamish knowledge base with embedding and examples."""
    id: str
    type: str  # 'persona', 'namespace', 'style'
    name: str
    description: str
    characteristics: List[str]
    examples: List[str]
    embedding: List[float]
    usage_count: int = 0
    quality_score: float = 0.0
    created_at: str = ""
    updated_at: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()

@dataclass
class LamishMeaning:
    """Embedding-based representation of narrative essence."""
    source_text: str
    essence_embedding: List[float]  # Core meaning vector
    narrative_elements: Dict[str, float]  # Weighted element scores
    transformation_signatures: List[List[float]]  # Embeddings from each step
    quality_indicators: Dict[str, float]
    created_at: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()

class LamishKnowledgeBase:
    """RAG-enabled knowledge base for Lamish projection concepts."""
    
    def __init__(self, data_path: str = "./data/lamish_kb.json"):
        self.data_path = data_path
        self.concepts: Dict[str, LamishConcept] = {}
        self.meanings: Dict[str, LamishMeaning] = {}
        self.load_knowledge_base()
    
    def load_knowledge_base(self):
        """Load existing knowledge base from storage."""
        try:
            with open(self.data_path, 'r') as f:
                data = json.load(f)
                
            # Load concepts
            for concept_data in data.get('concepts', []):
                concept = LamishConcept(**concept_data)
                self.concepts[concept.id] = concept
                
            # Load meanings
            for meaning_data in data.get('meanings', []):
                meaning = LamishMeaning(**meaning_data)
                self.meanings[meaning.source_text[:50]] = meaning
                
            logger.info(f"Loaded {len(self.concepts)} concepts and {len(self.meanings)} meanings")
            
        except FileNotFoundError:
            logger.info("No existing knowledge base found, starting fresh")
            self._initialize_base_concepts()
    
    def save_knowledge_base(self):
        """Save knowledge base to storage."""
        # Ensure directory exists
        import os
        os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
        
        data = {
            'concepts': [asdict(concept) for concept in self.concepts.values()],
            'meanings': [asdict(meaning) for meaning in self.meanings.values()],
            'metadata': {
                'total_concepts': len(self.concepts),
                'total_meanings': len(self.meanings),
                'last_updated': datetime.now().isoformat()
            }
        }
        
        with open(self.data_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _initialize_base_concepts(self):
        """Initialize with core Lamish concepts."""
        base_personas = [
            {
                'name': 'philosopher',
                'description': 'Contemplative thinker seeking deeper truths and universal patterns',
                'characteristics': ['analytical', 'questioning', 'abstract', 'reflective'],
                'examples': ['Explores underlying meaning', 'Questions assumptions', 'Seeks universal patterns']
            },
            {
                'name': 'storyteller', 
                'description': 'Narrative craftsperson weaving tales with emotional resonance',
                'characteristics': ['engaging', 'dramatic', 'character-focused', 'rhythmic'],
                'examples': ['Creates vivid scenes', 'Develops character arcs', 'Uses narrative tension']
            },
            {
                'name': 'scientist',
                'description': 'Empirical observer documenting phenomena with precision',
                'characteristics': ['methodical', 'evidence-based', 'systematic', 'precise'],
                'examples': ['Documents observations', 'Tests hypotheses', 'Measures outcomes']
            }
        ]
        
        base_namespaces = [
            {
                'name': 'lamish-galaxy',
                'description': 'Science fiction universe with frequency-based technology and cosmic consciousness',
                'characteristics': ['technological', 'cosmic', 'harmonic', 'vast'],
                'examples': ['Frequency manipulation', 'Crystalline cities', 'Galactic civilizations']
            },
            {
                'name': 'corporate-dystopia',
                'description': 'Near-future world dominated by corporate control and efficiency metrics',
                'characteristics': ['bureaucratic', 'controlled', 'measured', 'dehumanizing'],
                'examples': ['Performance metrics', 'Corporate hierarchies', 'Efficiency protocols']
            },
            {
                'name': 'medieval-realm',
                'description': 'Fantasy world of knights, magic, and feudal structures',
                'characteristics': ['hierarchical', 'honor-bound', 'mystical', 'traditional'],
                'examples': ['Chivalric codes', 'Magical elements', 'Noble houses']
            }
        ]
        
        base_styles = [
            {
                'name': 'poetic',
                'description': 'Lyrical language with rhythm, metaphor, and emotional resonance',
                'characteristics': ['rhythmic', 'metaphorical', 'evocative', 'musical'],
                'examples': ['Uses alliteration', 'Creates imagery', 'Employs metaphor']
            },
            {
                'name': 'formal',
                'description': 'Structured, precise language following established conventions',
                'characteristics': ['structured', 'precise', 'conventional', 'authoritative'],
                'examples': ['Clear organization', 'Formal vocabulary', 'Proper protocols']
            },
            {
                'name': 'casual',
                'description': 'Relaxed, conversational tone accessible to general audiences',
                'characteristics': ['accessible', 'conversational', 'friendly', 'direct'],
                'examples': ['Simple language', 'Personal examples', 'Informal tone']
            }
        ]
        
        # Create concept objects for each base type
        for persona in base_personas:
            self._create_concept('persona', persona)
        for namespace in base_namespaces:
            self._create_concept('namespace', namespace)
        for style in base_styles:
            self._create_concept('style', style)
    
    def _create_concept(self, concept_type: str, data: Dict[str, Any]):
        """Create a new concept in the knowledge base."""
        concept_id = self._generate_concept_id(concept_type, data['name'])
        
        # Generate embedding for concept (placeholder - would use actual embedding model)
        embedding = self._generate_concept_embedding(data)
        
        concept = LamishConcept(
            id=concept_id,
            type=concept_type,
            name=data['name'],
            description=data['description'],
            characteristics=data['characteristics'],
            examples=data['examples'],
            embedding=embedding
        )
        
        self.concepts[concept_id] = concept
    
    def _generate_concept_id(self, concept_type: str, name: str) -> str:
        """Generate unique ID for concept."""
        return hashlib.md5(f"{concept_type}:{name}".encode()).hexdigest()[:12]
    
    def _generate_concept_embedding(self, data: Dict[str, Any]) -> List[float]:
        """Generate embedding for concept (placeholder implementation)."""
        # In production, this would use the actual embedding model
        text = f"{data['description']} {' '.join(data['characteristics'])} {' '.join(data['examples'])}"
        # Placeholder: create deterministic but meaningless embedding
        hash_val = hashlib.md5(text.encode()).digest()
        embedding = []
        for i in range(0, len(hash_val), 2):
            val = int.from_bytes(hash_val[i:i+2], 'big') / 65535.0
            embedding.extend([val] * 48)  # Expand to 768 dimensions
        return embedding[:768]
    
    def enrich_concept_from_projection(self, concept_type: str, name: str, 
                                     projection_result: Dict[str, Any]):
        """Enrich concept definition based on successful projection."""
        concept_id = self._generate_concept_id(concept_type, name)
        
        if concept_id in self.concepts:
            concept = self.concepts[concept_id]
            concept.usage_count += 1
            
            # Extract new insights from projection
            if 'steps' in projection_result:
                new_examples = self._extract_examples_from_steps(projection_result['steps'])
                concept.examples.extend(new_examples)
                
            # Update quality score based on transformation success
            concept.quality_score = self._calculate_quality_score(concept, projection_result)
            concept.updated_at = datetime.now().isoformat()
            
            logger.info(f"Enriched {concept_type} '{name}' with new projection data")
    
    def _extract_examples_from_steps(self, steps: List[Dict[str, Any]]) -> List[str]:
        """Extract characteristic examples from transformation steps."""
        examples = []
        for step in steps:
            if 'output_snapshot' in step:
                # Extract meaningful phrases (simplified extraction)
                output = step['output_snapshot']
                if len(output) > 50:  # Only meaningful outputs
                    examples.append(output[:100] + "...")
        return examples[-3:]  # Keep most recent examples
    
    def _calculate_quality_score(self, concept: LamishConcept, 
                               projection_result: Dict[str, Any]) -> float:
        """Calculate quality score based on projection success."""
        base_score = concept.quality_score
        
        # Factors that indicate successful projection
        factors = []
        if 'total_duration_ms' in projection_result:
            # Reasonable duration (not too fast/slow) indicates good processing
            duration = projection_result['total_duration_ms']
            if 30000 <= duration <= 300000:  # 30s to 5min is reasonable
                factors.append(0.1)
        
        if 'steps' in projection_result:
            # All steps completed successfully
            if len(projection_result['steps']) == 5:
                factors.append(0.2)
        
        # Increment quality score
        new_score = min(1.0, base_score + sum(factors))
        return new_score
    
    def find_similar_concepts(self, query_embedding: List[float], 
                            concept_type: str = None, limit: int = 5) -> List[Tuple[LamishConcept, float]]:
        """Find concepts similar to query embedding."""
        similarities = []
        
        for concept in self.concepts.values():
            if concept_type and concept.type != concept_type:
                continue
                
            # Calculate cosine similarity
            similarity = self._cosine_similarity(query_embedding, concept.embedding)
            similarities.append((concept, similarity))
        
        # Sort by similarity and return top results
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:limit]
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        if len(vec1) != len(vec2):
            return 0.0
            
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = sum(a * a for a in vec1) ** 0.5
        magnitude2 = sum(b * b for b in vec2) ** 0.5
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
            
        return dot_product / (magnitude1 * magnitude2)
    
    def store_lamish_meaning(self, source_text: str, transformation_result: Dict[str, Any]):
        """Store the essence embedding and transformation signature."""
        # Generate essence embedding from source text
        essence_embedding = self._generate_concept_embedding({'description': source_text, 'characteristics': [], 'examples': []})
        
        # Extract transformation signatures from each step
        transformation_signatures = []
        for step in transformation_result.get('steps', []):
            step_embedding = self._generate_concept_embedding({
                'description': step.get('output_snapshot', ''),
                'characteristics': [],
                'examples': []
            })
            transformation_signatures.append(step_embedding)
        
        # Analyze narrative elements
        narrative_elements = self._analyze_narrative_elements(source_text)
        
        # Calculate quality indicators
        quality_indicators = {
            'coherence': 0.8,  # Placeholder
            'creativity': 0.7,
            'fidelity': 0.9
        }
        
        meaning = LamishMeaning(
            source_text=source_text,
            essence_embedding=essence_embedding,
            narrative_elements=narrative_elements,
            transformation_signatures=transformation_signatures,
            quality_indicators=quality_indicators
        )
        
        self.meanings[source_text[:50]] = meaning
        logger.info(f"Stored lamish meaning for: {source_text[:50]}...")
    
    def _analyze_narrative_elements(self, text: str) -> Dict[str, float]:
        """Analyze narrative elements and return weighted scores."""
        elements = {
            'character_focus': 0.0,
            'action_intensity': 0.0,
            'emotional_depth': 0.0,
            'descriptive_richness': 0.0,
            'temporal_complexity': 0.0
        }
        
        # Simple heuristic analysis (would be more sophisticated in production)
        text_lower = text.lower()
        
        # Character indicators
        character_words = ['he', 'she', 'they', 'character', 'person', 'man', 'woman']
        elements['character_focus'] = sum(text_lower.count(word) for word in character_words) / len(text.split())
        
        # Action indicators  
        action_words = ['ran', 'jumped', 'fought', 'moved', 'action', 'quickly']
        elements['action_intensity'] = sum(text_lower.count(word) for word in action_words) / len(text.split())
        
        # Emotional indicators
        emotion_words = ['felt', 'emotion', 'heart', 'soul', 'love', 'fear', 'joy', 'sadness']
        elements['emotional_depth'] = sum(text_lower.count(word) for word in emotion_words) / len(text.split())
        
        # Descriptive indicators
        descriptive_words = ['beautiful', 'dark', 'bright', 'color', 'texture', 'appearance']
        elements['descriptive_richness'] = sum(text_lower.count(word) for word in descriptive_words) / len(text.split())
        
        # Temporal indicators
        time_words = ['when', 'then', 'before', 'after', 'during', 'time', 'moment']
        elements['temporal_complexity'] = sum(text_lower.count(word) for word in time_words) / len(text.split())
        
        return elements
    
    def suggest_optimal_configuration(self, source_text: str) -> Dict[str, str]:
        """Suggest optimal persona/namespace/style based on narrative analysis."""
        # Generate embedding for source text
        source_embedding = self._generate_concept_embedding({
            'description': source_text,
            'characteristics': [],
            'examples': []
        })
        
        # Find best matches for each concept type
        best_persona = self.find_similar_concepts(source_embedding, 'persona', 1)[0][0].name
        best_namespace = self.find_similar_concepts(source_embedding, 'namespace', 1)[0][0].name  
        best_style = self.find_similar_concepts(source_embedding, 'style', 1)[0][0].name
        
        return {
            'persona': best_persona,
            'namespace': best_namespace,
            'style': best_style
        }
    
    def get_concept_details(self, concept_type: str, name: str) -> Optional[LamishConcept]:
        """Get detailed information about a specific concept."""
        concept_id = self._generate_concept_id(concept_type, name)
        return self.concepts.get(concept_id)
    
    def get_concept_evolution(self, concept_type: str, name: str) -> Dict[str, Any]:
        """Get the evolution history and learning for a concept."""
        concept = self.get_concept_details(concept_type, name)
        if not concept:
            return {}
        
        return {
            'usage_count': concept.usage_count,
            'quality_score': concept.quality_score,
            'examples_count': len(concept.examples),
            'characteristics': concept.characteristics,
            'last_updated': concept.updated_at,
            'maturity_level': 'nascent' if concept.usage_count < 5 else 'developing' if concept.usage_count < 20 else 'mature'
        }