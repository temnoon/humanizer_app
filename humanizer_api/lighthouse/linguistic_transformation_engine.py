# Linguistic Transformation Engine
# Implementing sophisticated namespace/persona/style framework with machine learning capabilities

import re
import json
import spacy
import numpy as np
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field, asdict
from collections import Counter, defaultdict
from enum import Enum
import statistics
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Load spaCy model for linguistic analysis
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    logger.warning("spaCy model not available - linguistic analysis will be limited")
    nlp = None

class AttributeType(Enum):
    NAMESPACE = "namespace"
    PERSONA = "persona" 
    STYLE = "style"

class MappingPolicy(Enum):
    SURROGATE_ON_EARTH_ENTITIES = "surrogate-on-earth-entities"
    REPLACE_ALL_PROPER_NOUNS = "replace-all-proper-nouns"
    ALIAS_ONLY_FICTIONALS = "alias-only-fictionals"
    PRESERVE_ABSTRACTS = "preserve-abstracts"

@dataclass
class NamespaceManifest:
    """JSON-serializable namespace specification following the theoretical framework"""
    id: str
    description: str
    lexicon_seed: List[str] = field(default_factory=list)
    phonotactic_pattern: str = ""
    mapping_policy: str = MappingPolicy.SURROGATE_ON_EARTH_ENTITIES.value
    vector_model: str = "sentence-transformer/all-mpnet-base-v2"
    phoneme_frequencies: Dict[str, float] = field(default_factory=dict)
    semantic_constraints: List[str] = field(default_factory=list)
    earthish_entities: Set[str] = field(default_factory=set)

@dataclass 
class PersonaManifest:
    """JSON-serializable persona specification with quantified markers"""
    label: str
    perspective: str = "first-person"
    register: str = "neutral"
    emotional_tone: str = "neutral"
    background: Dict[str, str] = field(default_factory=dict)
    stylistic_markers: Dict[str, Any] = field(default_factory=dict)
    pronoun_usage: Dict[str, float] = field(default_factory=dict)
    modality_usage: Dict[str, float] = field(default_factory=dict)
    cultural_markers: List[str] = field(default_factory=list)

@dataclass
class StyleManifest:
    """JSON-serializable style specification with quantified parameters"""
    avg_sentence_length: float = 15.0
    sentence_length_std: float = 5.0
    rhetorical_devices: List[str] = field(default_factory=list)
    formality_score: float = 0.5
    lexical_sophistication: float = 0.5
    imagery_density: float = 0.2
    punctuation_density: float = 0.1
    device_frequencies: Dict[str, float] = field(default_factory=dict)
    syntactic_patterns: List[str] = field(default_factory=list)
    register_markers: Dict[str, float] = field(default_factory=dict)

@dataclass
class LinguisticTransformationManifest:
    """Complete transformation specification combining all three attributes"""
    namespace: NamespaceManifest
    persona: PersonaManifest
    style: StyleManifest
    metadata: Dict[str, Any] = field(default_factory=dict)
    created: str = field(default_factory=lambda: datetime.now().isoformat())
    version: str = "1.0"

class PhonotacticAnalyzer:
    """Analyzes and generates phonotactic patterns from name examples"""
    
    @staticmethod
    def extract_pattern(names: List[str]) -> str:
        """Extract regex pattern from list of names"""
        if not names:
            return ""
        
        # Analyze common patterns
        consonants = set()
        vowels = set("aeiouAEIOU")
        patterns = []
        
        for name in names:
            name_pattern = ""
            for char in name:
                if char.isalpha():
                    if char.lower() in vowels:
                        name_pattern += "V"
                    else:
                        name_pattern += "C"
                        consonants.add(char.upper())
            patterns.append(name_pattern)
        
        # Find most common pattern structures
        pattern_counts = Counter(patterns)
        most_common = pattern_counts.most_common(3)
        
        # Generate regex based on common patterns
        if most_common:
            # Build regex that captures the most common structures
            consonant_class = "[" + "".join(sorted(consonants)) + "]"
            vowel_class = "[aeiouAEIOU]"
            
            # Convert pattern to regex
            pattern = most_common[0][0]
            regex_pattern = "^"
            for char in pattern:
                if char == "C":
                    regex_pattern += consonant_class
                elif char == "V":
                    regex_pattern += vowel_class
            regex_pattern += "$"
            
            return regex_pattern
        
        return ""

    @staticmethod
    def analyze_phoneme_frequencies(names: List[str]) -> Dict[str, float]:
        """Analyze phoneme frequencies in name corpus"""
        all_chars = "".join(names).lower()
        char_counts = Counter(c for c in all_chars if c.isalpha())
        total = sum(char_counts.values())
        
        return {char: count/total for char, count in char_counts.items()}

    @staticmethod
    def generate_name(pattern: str, phoneme_freqs: Dict[str, float], 
                     length_range: tuple = (4, 8)) -> str:
        """Generate new name following phonotactic constraints"""
        if not pattern or not phoneme_freqs:
            return "Generated"
        
        # Simple generation based on pattern and frequencies
        # This is a basic implementation - could be enhanced with more sophisticated methods
        consonants = [c for c in phoneme_freqs.keys() if c not in "aeiou"]
        vowels = [c for c in phoneme_freqs.keys() if c in "aeiou"]
        
        if not consonants or not vowels:
            return "Generated"
        
        # Weight selection by frequency
        consonant_weights = [phoneme_freqs.get(c, 0.1) for c in consonants]
        vowel_weights = [phoneme_freqs.get(v, 0.1) for v in vowels]
        
        length = np.random.randint(length_range[0], length_range[1] + 1)
        name = ""
        
        for i in range(length):
            if i % 2 == 0:  # Consonant position
                if consonants:
                    char = np.random.choice(consonants, p=np.array(consonant_weights)/sum(consonant_weights))
                    name += char.upper() if i == 0 else char
            else:  # Vowel position
                if vowels:
                    char = np.random.choice(vowels, p=np.array(vowel_weights)/sum(vowel_weights))
                    name += char
        
        return name.capitalize()

class StylometricAnalyzer:
    """Analyzes text for stylistic patterns and generates style manifests"""
    
    @staticmethod
    def analyze_text(text: str) -> Dict[str, Any]:
        """Extract comprehensive stylometric features from text"""
        if not nlp:
            return {"error": "spaCy not available for analysis"}
        
        doc = nlp(text)
        sentences = list(doc.sents)
        
        if not sentences:
            return {}
        
        # Sentence length analysis
        sentence_lengths = [len(sent.text.split()) for sent in sentences]
        avg_length = statistics.mean(sentence_lengths)
        length_std = statistics.stdev(sentence_lengths) if len(sentence_lengths) > 1 else 0
        
        # Pronoun analysis
        pronouns = ["i", "you", "he", "she", "it", "we", "they", "me", "him", "her", "us", "them"]
        pronoun_counts = defaultdict(int)
        total_words = len([token for token in doc if token.is_alpha])
        
        for token in doc:
            if token.text.lower() in pronouns:
                pronoun_counts[token.text.lower()] += 1
        
        pronoun_freqs = {p: pronoun_counts[p] / total_words for p in pronouns}
        
        # Modal verb analysis
        modals = ["can", "could", "may", "might", "must", "shall", "should", "will", "would"]
        modal_counts = defaultdict(int)
        
        for token in doc:
            if token.text.lower() in modals:
                modal_counts[token.text.lower()] += 1
        
        modal_freqs = {m: modal_counts[m] / total_words for m in modals}
        
        # Punctuation density
        punct_count = len([token for token in doc if token.is_punct])
        punct_density = punct_count / total_words if total_words > 0 else 0
        
        # Rhetorical device detection (basic patterns)
        devices = StylometricAnalyzer.detect_rhetorical_devices(text)
        
        # Formality scoring (basic heuristic)
        formality = StylometricAnalyzer.calculate_formality(doc)
        
        return {
            "avg_sentence_length": avg_length,
            "sentence_length_std": length_std,
            "pronoun_usage": pronoun_freqs,
            "modality_usage": modal_freqs,
            "punctuation_density": punct_density,
            "rhetorical_devices": devices,
            "formality_score": formality,
            "total_words": total_words,
            "total_sentences": len(sentences)
        }
    
    @staticmethod
    def detect_rhetorical_devices(text: str) -> List[str]:
        """Detect basic rhetorical devices in text"""
        devices = []
        
        # Anaphora detection (repeated sentence beginnings)
        sentences = re.split(r'[.!?]+', text)
        sentence_starts = [s.strip().split()[:3] for s in sentences if s.strip()]
        
        if len(sentence_starts) >= 2:
            start_counts = Counter([" ".join(start) for start in sentence_starts if start])
            if any(count >= 2 for count in start_counts.values()):
                devices.append("anaphora")
        
        # Parallelism detection (similar syntactic structures)
        if re.search(r'\b\w+ing\b.*\b\w+ing\b.*\b\w+ing\b', text):
            devices.append("parallelism")
        
        # Alliteration detection
        words = re.findall(r'\b\w+\b', text.lower())
        for i in range(len(words) - 2):
            if words[i][0] == words[i+1][0] == words[i+2][0]:
                devices.append("alliteration")
                break
        
        # Metaphor detection (simple pattern matching)
        if re.search(r'\bis\s+\w+\s+\w+\b', text) or 'like' in text.lower():
            devices.append("metaphor")
        
        return list(set(devices))
    
    @staticmethod
    def calculate_formality(doc) -> float:
        """Calculate formality score using linguistic features"""
        formal_indicators = 0
        informal_indicators = 0
        
        for token in doc:
            # Formal indicators
            if token.tag_ in ['VBZ', 'VBD', 'VBN']:  # More complex verb forms
                formal_indicators += 1
            if token.text.lower() in ['therefore', 'furthermore', 'consequently', 'nevertheless']:
                formal_indicators += 2
            if len(token.text) > 6 and token.is_alpha:  # Longer words
                formal_indicators += 1
                
            # Informal indicators  
            if token.text.lower() in ['gonna', 'wanna', 'yeah', 'ok', 'cool']:
                informal_indicators += 2
            if token.text in ["'ll", "'re", "'ve", "'d"]:  # Contractions
                informal_indicators += 1
        
        total_indicators = formal_indicators + informal_indicators
        if total_indicators == 0:
            return 0.5
        
        return formal_indicators / total_indicators

class TransformationInference:
    """Learn transformation patterns from examples and infer manifests"""
    
    @staticmethod
    def infer_namespace_from_examples(original_texts: List[str], 
                                    transformed_texts: List[str]) -> NamespaceManifest:
        """Reverse-engineer namespace manifest from transformation examples"""
        # Extract replaced entities
        if not nlp:
            return NamespaceManifest(id="inferred", description="Basic inferred namespace")
        
        replaced_entities = []
        mapping_policy = MappingPolicy.SURROGATE_ON_EARTH_ENTITIES.value
        
        for orig, trans in zip(original_texts, transformed_texts):
            orig_doc = nlp(orig)
            trans_doc = nlp(trans)
            
            # Extract entities that were replaced
            orig_entities = {ent.text for ent in orig_doc.ents if ent.label_ in ["PERSON", "GPE", "ORG"]}
            trans_entities = {ent.text for ent in trans_doc.ents if ent.label_ in ["PERSON", "GPE", "ORG"]}
            
            # Find new entities in transformed text
            new_entities = trans_entities - orig_entities
            replaced_entities.extend(new_entities)
        
        # Analyze phonotactic patterns
        phonotactic_pattern = PhonotacticAnalyzer.extract_pattern(replaced_entities)
        phoneme_freqs = PhonotacticAnalyzer.analyze_phoneme_frequencies(replaced_entities)
        
        return NamespaceManifest(
            id="inferred_namespace",
            description="Inferred from transformation examples",
            lexicon_seed=list(set(replaced_entities))[:20],  # Top 20 unique
            phonotactic_pattern=phonotactic_pattern,
            mapping_policy=mapping_policy,
            phoneme_frequencies=phoneme_freqs
        )
    
    @staticmethod
    def infer_persona_from_examples(transformed_texts: List[str]) -> PersonaManifest:
        """Infer persona manifest from transformed text examples"""
        if not transformed_texts:
            return PersonaManifest(label="inferred_persona")
        
        # Analyze all texts together for consistent patterns
        combined_analysis = {}
        dict_keys = set()
        
        for text in transformed_texts:
            analysis = StylometricAnalyzer.analyze_text(text)
            for key, value in analysis.items():
                if isinstance(value, dict):
                    dict_keys.add(key)
                    if key not in combined_analysis:
                        combined_analysis[key] = defaultdict(list)
                    for subkey, subvalue in value.items():
                        combined_analysis[key][subkey].append(subvalue)
                elif isinstance(value, (int, float)):
                    if key not in combined_analysis:
                        combined_analysis[key] = []
                    combined_analysis[key].append(value)
        
        # Average the values
        avg_pronoun_usage = {}
        avg_modality_usage = {}
        
        if 'pronoun_usage' in combined_analysis:
            for pronoun, values in combined_analysis['pronoun_usage'].items():
                avg_pronoun_usage[pronoun] = statistics.mean(values) if values else 0
        
        if 'modality_usage' in combined_analysis:
            for modal, values in combined_analysis['modality_usage'].items():
                avg_modality_usage[modal] = statistics.mean(values) if values else 0
        
        return PersonaManifest(
            label="inferred_persona",
            perspective="inferred",
            pronoun_usage=avg_pronoun_usage,
            modality_usage=avg_modality_usage,
            stylistic_markers={
                "pronoun_usage": avg_pronoun_usage,
                "modality": avg_modality_usage
            }
        )
    
    @staticmethod
    def infer_style_from_examples(transformed_texts: List[str]) -> StyleManifest:
        """Infer style manifest from transformed text examples"""
        if not transformed_texts:
            return StyleManifest()
        
        # Analyze each text and average the results
        all_analyses = [StylometricAnalyzer.analyze_text(text) for text in transformed_texts]
        
        # Extract numeric values and average them
        avg_sentence_length = statistics.mean([a.get('avg_sentence_length', 15) for a in all_analyses])
        sentence_length_std = statistics.mean([a.get('sentence_length_std', 5) for a in all_analyses])
        punctuation_density = statistics.mean([a.get('punctuation_density', 0.1) for a in all_analyses])
        formality_score = statistics.mean([a.get('formality_score', 0.5) for a in all_analyses])
        
        # Collect all rhetorical devices
        all_devices = []
        for analysis in all_analyses:
            all_devices.extend(analysis.get('rhetorical_devices', []))
        
        # Calculate device frequencies
        device_counts = Counter(all_devices)
        total_texts = len(transformed_texts)
        device_frequencies = {device: count/total_texts for device, count in device_counts.items()}
        
        return StyleManifest(
            avg_sentence_length=avg_sentence_length,
            sentence_length_std=sentence_length_std,
            rhetorical_devices=list(set(all_devices)),
            formality_score=formality_score,
            punctuation_density=punctuation_density,
            device_frequencies=device_frequencies
        )

class LinguisticTransformationEngine:
    """Main engine for creating and applying linguistic transformations"""
    
    def __init__(self):
        self.manifests: Dict[str, LinguisticTransformationManifest] = {}
    
    def create_manifest_from_examples(self, 
                                    original_texts: List[str],
                                    transformed_texts: List[str],
                                    manifest_id: str,
                                    description: str = "") -> LinguisticTransformationManifest:
        """Create a complete transformation manifest from examples"""
        
        # Infer each component
        namespace = TransformationInference.infer_namespace_from_examples(
            original_texts, transformed_texts
        )
        namespace.id = f"{manifest_id}_namespace"
        namespace.description = f"Namespace for {description}"
        
        persona = TransformationInference.infer_persona_from_examples(transformed_texts)
        persona.label = f"{manifest_id}_persona"
        
        style = TransformationInference.infer_style_from_examples(transformed_texts)
        
        manifest = LinguisticTransformationManifest(
            namespace=namespace,
            persona=persona,
            style=style,
            metadata={
                "manifest_id": manifest_id,
                "description": description,
                "source": "inferred_from_examples",
                "num_examples": len(transformed_texts)
            }
        )
        
        self.manifests[manifest_id] = manifest
        return manifest
    
    def export_manifest_json(self, manifest_id: str) -> str:
        """Export manifest as JSON string following the schema"""
        if manifest_id not in self.manifests:
            raise ValueError(f"Manifest {manifest_id} not found")
        
        manifest = self.manifests[manifest_id]
        return json.dumps(asdict(manifest), indent=2, default=str)
    
    def import_manifest_json(self, json_str: str) -> str:
        """Import manifest from JSON string"""
        data = json.loads(json_str)
        
        # Reconstruct manifest objects
        namespace = NamespaceManifest(**data['namespace'])
        persona = PersonaManifest(**data['persona'])
        style = StyleManifest(**data['style'])
        
        manifest = LinguisticTransformationManifest(
            namespace=namespace,
            persona=persona,
            style=style,
            metadata=data.get('metadata', {}),
            created=data.get('created', datetime.now().isoformat()),
            version=data.get('version', '1.0')
        )
        
        manifest_id = data.get('metadata', {}).get('manifest_id', f"imported_{len(self.manifests)}")
        self.manifests[manifest_id] = manifest
        
        return manifest_id
    
    def generate_name_for_namespace(self, manifest_id: str) -> str:
        """Generate a new name following the namespace's phonotactic patterns"""
        if manifest_id not in self.manifests:
            return "Generated"
        
        namespace = self.manifests[manifest_id].namespace
        return PhonotacticAnalyzer.generate_name(
            namespace.phonotactic_pattern,
            namespace.phoneme_frequencies
        )
    
    def analyze_text_stylometrics(self, text: str) -> Dict[str, Any]:
        """Analyze text and return detailed stylometric features"""
        return StylometricAnalyzer.analyze_text(text)
    
    def get_all_manifest_ids(self) -> List[str]:
        """Get list of all stored manifest IDs"""
        return list(self.manifests.keys())
    
    def get_manifest_summary(self, manifest_id: str) -> Dict[str, Any]:
        """Get summary information about a manifest"""
        if manifest_id not in self.manifests:
            return {}
        
        manifest = self.manifests[manifest_id]
        return {
            "id": manifest_id,
            "description": manifest.metadata.get("description", ""),
            "namespace_id": manifest.namespace.id,
            "persona_label": manifest.persona.label,
            "created": manifest.created,
            "lexicon_size": len(manifest.namespace.lexicon_seed),
            "avg_sentence_length": manifest.style.avg_sentence_length,
            "formality_score": manifest.style.formality_score,
            "rhetorical_devices": len(manifest.style.rhetorical_devices)
        }