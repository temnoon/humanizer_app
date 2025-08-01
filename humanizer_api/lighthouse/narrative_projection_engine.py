#!/usr/bin/env python3
"""
Narrative Projection Engine
Projects narratives through discovered DNA attributes while preserving essence
"""

import json
import re
import random
from pathlib import Path
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
import numpy as np


@dataclass
class ProjectionParameters:
    """Parameters for narrative projection"""
    target_persona: str
    target_namespace: str  
    target_style: str
    projection_strength: float = 0.8
    essence_preservation: float = 0.9
    creativity_factor: float = 0.6


@dataclass
class ProjectionResult:
    """Result of narrative projection"""
    original_text: str
    projected_text: str
    essence_preservation_score: float
    transformation_log: List[str]
    applied_patterns: Dict[str, Any]
    projection_confidence: float


class NarrativeProjectionEngine:
    """Core engine for narrative DNA projection"""
    
    def __init__(self, attributes_dir: str = "./discovered_attributes"):
        self.attributes_dir = Path(attributes_dir)
        self.loaded_attributes = {}
        self.projection_templates = {}
        self._load_discovered_attributes()
        self._initialize_projection_templates()
    
    def _load_discovered_attributes(self):
        """Load all discovered DNA attributes"""
        
        print("🧬 Loading discovered DNA attributes...")
        
        for attr_file in self.attributes_dir.glob("attributes_*.json"):
            book_id = attr_file.stem.replace("attributes_", "")
            try:
                with open(attr_file, 'r') as f:
                    data = json.load(f)
                    self.loaded_attributes[book_id] = data
                    print(f"  ✅ Loaded {len(data.get('attributes', []))} attributes from book {book_id}")
            except Exception as e:
                print(f"  ❌ Failed to load {attr_file}: {e}")
        
        print(f"📚 Total attributes loaded from {len(self.loaded_attributes)} books")
    
    def _initialize_projection_templates(self):
        """Initialize projection templates for different personas/namespaces/styles"""
        
        self.projection_templates = {
            # PERSONAS
            'tragic_chorus': {
                'voice_patterns': [
                    'We witness {event}, and know that {consequence} must follow',
                    'Behold how {character} {action}, yet understands not the price',
                    'The gods have woven {fate} into the very fabric of this tale'
                ],
                'syntax_transforms': {
                    'first_person': 'collective_we',
                    'tense_shift': 'prophetic_present',
                    'perspective': 'omniscient_dramatic'
                }
            },
            
            'cyberpunk_hacker': {
                'voice_patterns': [
                    'The data streams showed {event} cascading through the network',
                    '{character} jacked into the system and {action}',
                    'Neon-lit {setting} buzzed with {atmosphere}'
                ],
                'syntax_transforms': {
                    'tech_metaphors': True,
                    'present_tense': True,
                    'cynical_tone': True
                }
            },
            
            'victorian_narrator': {
                'voice_patterns': [
                    'It was with considerable {emotion} that {character} {action}',
                    'The reader will perhaps forgive my {observation} regarding {event}',
                    'Such was the nature of {character}, whose {quality} proved most {adjective}'
                ],
                'syntax_transforms': {
                    'formal_register': True,
                    'elaborate_clauses': True,
                    'moral_commentary': True
                }
            },
            
            # NAMESPACES
            'ancient_mesopotamia': {
                'cultural_mappings': {
                    'gods': ['Marduk', 'Ishtar', 'Enlil', 'Ea'],
                    'places': ['Uruk', 'the Cedar Forest', 'the underworld'],
                    'concepts': {'friendship': 'brotherhood forged by the gods', 
                                'death': 'journey to the land of no return',
                                'power': 'divine kingship'}
                }
            },
            
            'cyberpunk_dystopia': {
                'cultural_mappings': {
                    'gods': ['The Corporation', 'AI Overlords', 'Data Spirits'],
                    'places': ['Neo-Tokyo', 'the Grid', 'the Dark Web'],
                    'concepts': {'friendship': 'trusted connection in hostile network',
                                'death': 'permanent disconnection from the matrix',
                                'power': 'admin privileges'}
                }
            },
            
            'regency_england': {
                'cultural_mappings': {
                    'gods': ['Providence', 'Fortune', 'Society'],
                    'places': ['London', 'the countryside', 'Bath'],
                    'concepts': {'friendship': 'intimate acquaintance of long standing',
                                'death': 'departure from this mortal realm',
                                'power': 'influence in the finest circles'}
                }
            },
            
            # STYLES
            'epic_verse': {
                'linguistic_patterns': {
                    'repetition': True,
                    'epithets': True,
                    'parallel_structure': True,
                    'elevated_diction': True
                }
            },
            
            'noir_prose': {
                'linguistic_patterns': {
                    'short_sentences': True,
                    'metaphorical_descriptions': True,
                    'cynical_tone': True,
                    'urban_imagery': True
                }
            },
            
            'stream_of_consciousness': {
                'linguistic_patterns': {
                    'fragment_sentences': True,
                    'associative_jumps': True,
                    'present_tense': True,
                    'internal_monologue': True
                }
            }
        }
    
    def project_narrative(self, 
                         source_text: str,
                         projection_params: ProjectionParameters) -> ProjectionResult:
        """Project narrative through specified DNA attributes"""
        
        print(f"🎭 Projecting narrative...")
        print(f"  📖 Source length: {len(source_text)} characters")
        print(f"  🎭 Target persona: {projection_params.target_persona}")
        print(f"  🌍 Target namespace: {projection_params.target_namespace}")
        print(f"  ✍️  Target style: {projection_params.target_style}")
        
        transformation_log = []
        
        # Step 1: Extract essence (preserve semantic invariants)
        essence = self._extract_essence(source_text)
        transformation_log.append(f"Extracted essence: {len(essence['key_events'])} events, {len(essence['characters'])} characters")
        
        # Step 2: Apply persona transformation
        persona_transformed = self._apply_persona_transformation(
            source_text, projection_params.target_persona, essence
        )
        transformation_log.append(f"Applied persona transformation: {projection_params.target_persona}")
        
        # Step 3: Apply namespace transformation
        namespace_transformed = self._apply_namespace_transformation(
            persona_transformed, projection_params.target_namespace, essence
        )
        transformation_log.append(f"Applied namespace transformation: {projection_params.target_namespace}")
        
        # Step 4: Apply style transformation
        style_transformed = self._apply_style_transformation(
            namespace_transformed, projection_params.target_style, essence
        )
        transformation_log.append(f"Applied style transformation: {projection_params.target_style}")
        
        # Step 5: Validate essence preservation
        preservation_score = self._calculate_essence_preservation(
            source_text, style_transformed, essence
        )
        transformation_log.append(f"Essence preservation: {preservation_score:.2f}")
        
        return ProjectionResult(
            original_text=source_text,
            projected_text=style_transformed,
            essence_preservation_score=preservation_score,
            transformation_log=transformation_log,
            applied_patterns={
                'persona': projection_params.target_persona,
                'namespace': projection_params.target_namespace,
                'style': projection_params.target_style
            },
            projection_confidence=min(preservation_score * projection_params.projection_strength, 1.0)
        )
    
    def _extract_essence(self, text: str) -> Dict[str, Any]:
        """Extract semantic essence to preserve during transformation"""
        
        # Simple essence extraction (would be more sophisticated with NLP)
        essence = {
            'key_events': [],
            'characters': [],
            'relationships': [],
            'themes': [],
            'causal_structure': [],
            'emotional_arc': []
        }
        
        # Character detection (simple heuristics)
        characters = re.findall(r'\b[A-Z][a-z]+\b', text)
        character_counts = {}
        for char in characters:
            character_counts[char] = character_counts.get(char, 0) + 1
        
        # Keep frequently mentioned names (likely characters)
        essence['characters'] = [char for char, count in character_counts.items() 
                               if count >= 2 and len(char) > 3][:5]
        
        # Event detection (action verbs + subjects)
        action_patterns = re.findall(r'(\w+)\s+(went|came|said|saw|found|fought|died|lived|became)', text, re.IGNORECASE)
        essence['key_events'] = [f"{subj} {verb}" for subj, verb in action_patterns[:10]]
        
        # Theme detection (abstract concepts)
        theme_words = ['death', 'life', 'friendship', 'power', 'love', 'honor', 'destiny', 'gods', 'journey']
        essence['themes'] = [theme for theme in theme_words if theme.lower() in text.lower()]
        
        return essence
    
    def _apply_persona_transformation(self, text: str, persona: str, essence: Dict) -> str:
        """Apply persona transformation using voice patterns"""
        
        if persona not in self.projection_templates:
            return text
        
        persona_template = self.projection_templates[persona]
        transformed_sentences = []
        
        sentences = re.split(r'[.!?]+', text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # Apply persona-specific voice patterns
            if 'voice_patterns' in persona_template:
                pattern = random.choice(persona_template['voice_patterns'])
                
                # Simple pattern matching and substitution
                if '{event}' in pattern and essence['key_events']:
                    event = random.choice(essence['key_events'])
                    sentence = pattern.replace('{event}', event)
                elif '{character}' in pattern and essence['characters']:
                    character = random.choice(essence['characters'])
                    sentence = pattern.replace('{character}', character)
                else:
                    # Keep original sentence but apply syntax transforms
                    sentence = self._apply_syntax_transforms(sentence, persona_template.get('syntax_transforms', {}))
            
            transformed_sentences.append(sentence)
        
        return '. '.join(transformed_sentences[:5])  # Limit length for demo
    
    def _apply_namespace_transformation(self, text: str, namespace: str, essence: Dict) -> str:
        """Apply namespace transformation using cultural mappings"""
        
        if namespace not in self.projection_templates:
            return text
        
        namespace_template = self.projection_templates[namespace]
        transformed_text = text
        
        if 'cultural_mappings' in namespace_template:
            mappings = namespace_template['cultural_mappings']
            
            # Apply concept mappings
            if 'concepts' in mappings:
                for original_concept, mapped_concept in mappings['concepts'].items():
                    pattern = re.compile(r'\b' + re.escape(original_concept) + r'\b', re.IGNORECASE)
                    transformed_text = pattern.sub(mapped_concept, transformed_text)
            
            # Add namespace-specific elements
            if 'places' in mappings and essence['characters']:
                char = essence['characters'][0] if essence['characters'] else 'the hero'
                place = random.choice(mappings['places'])
                transformed_text += f" In {place}, {char} walked among the familiar streets."
        
        return transformed_text
    
    def _apply_style_transformation(self, text: str, style: str, essence: Dict) -> str:
        """Apply stylistic transformation using linguistic patterns"""
        
        if style not in self.projection_templates:
            return text
        
        style_template = self.projection_templates[style]
        
        if 'linguistic_patterns' in style_template:
            patterns = style_template['linguistic_patterns']
            
            # Apply style-specific transformations
            if patterns.get('short_sentences'):
                # Break long sentences into shorter ones
                text = re.sub(r',\s+', '. ', text)
            
            if patterns.get('repetition'):
                # Add epic repetition
                first_sentence = text.split('.')[0]
                if first_sentence:
                    text = f"{first_sentence}. {first_sentence}, again and again. {text}"
            
            if patterns.get('elevated_diction'):
                # Replace simple words with elevated versions
                elevations = {
                    'said': 'proclaimed',
                    'went': 'journeyed',
                    'big': 'mighty',
                    'good': 'noble'
                }
                for simple, elevated in elevations.items():
                    text = re.sub(r'\b' + simple + r'\b', elevated, text, flags=re.IGNORECASE)
        
        return text
    
    def _apply_syntax_transforms(self, sentence: str, transforms: Dict) -> str:
        """Apply syntax-level transformations"""
        
        if transforms.get('collective_we'):
            sentence = re.sub(r'\bI\b', 'we', sentence)
            sentence = re.sub(r'\bme\b', 'us', sentence)
        
        if transforms.get('present_tense'):
            # Simple past to present conversion
            sentence = re.sub(r'(\w+)ed\b', r'\1', sentence)
        
        if transforms.get('formal_register'):
            sentence = f"It must be observed that {sentence.lower()}"
        
        return sentence
    
    def _calculate_essence_preservation(self, original: str, transformed: str, essence: Dict) -> float:
        """Calculate how well the essence was preserved"""
        
        preservation_score = 0.0
        total_checks = 0
        
        # Check character preservation
        if essence['characters']:
            for character in essence['characters']:
                if character.lower() in transformed.lower():
                    preservation_score += 1
                total_checks += 1
        
        # Check theme preservation
        if essence['themes']:
            for theme in essence['themes']:
                if theme.lower() in transformed.lower():
                    preservation_score += 1
                total_checks += 1
        
        # Check event preservation (structural)
        if essence['key_events']:
            for event in essence['key_events']:
                # Check if event pattern is preserved (loosely)
                event_words = event.split()
                if any(word.lower() in transformed.lower() for word in event_words):
                    preservation_score += 0.5
                total_checks += 1
        
        return preservation_score / max(total_checks, 1)
    
    def get_available_projections(self) -> Dict[str, List[str]]:
        """Get all available projection options"""
        
        personas = [key for key in self.projection_templates.keys() 
                   if any(x in self.projection_templates[key] for x in ['voice_patterns', 'syntax_transforms'])]
        
        namespaces = [key for key in self.projection_templates.keys()
                     if 'cultural_mappings' in self.projection_templates[key]]
        
        styles = [key for key in self.projection_templates.keys()
                 if 'linguistic_patterns' in self.projection_templates[key]]
        
        return {
            'personas': personas,
            'namespaces': namespaces,
            'styles': styles
        }


def main():
    """CLI for testing projection engine"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Narrative Projection Engine')
    parser.add_argument('--text', required=True, help='Text to project')
    parser.add_argument('--persona', default='tragic_chorus', help='Target persona')
    parser.add_argument('--namespace', default='ancient_mesopotamia', help='Target namespace')
    parser.add_argument('--style', default='epic_verse', help='Target style')
    parser.add_argument('--attributes-dir', default='./discovered_attributes', help='Attributes directory')
    
    args = parser.parse_args()
    
    engine = NarrativeProjectionEngine(args.attributes_dir)
    
    params = ProjectionParameters(
        target_persona=args.persona,
        target_namespace=args.namespace,
        target_style=args.style
    )
    
    result = engine.project_narrative(args.text, params)
    
    print(f"\n🎭 PROJECTION RESULT")
    print(f"📖 Original: {result.original_text}")
    print(f"✨ Projected: {result.projected_text}")
    print(f"🔮 Essence Preservation: {result.essence_preservation_score:.2f}")
    print(f"🎯 Confidence: {result.projection_confidence:.2f}")
    print(f"📋 Transformations: {', '.join(result.transformation_log)}")


if __name__ == "__main__":
    main()