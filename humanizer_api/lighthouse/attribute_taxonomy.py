#!/usr/bin/env python3
"""
Hierarchical Attribute Taxonomy System
=====================================

Human-readable, semantically organized narrative attribute classification
with Pydantic models and validation for the Allegory Engine pipeline.
"""

from typing import Dict, List, Optional, Union, Any, Literal
from pydantic import BaseModel, Field, validator, root_validator
from enum import Enum
from datetime import datetime
from dataclasses import dataclass
import uuid


class AttributeCategory(str, Enum):
    """Top-level semantic categories for narrative attributes"""
    TEXTUAL_RHYTHM = "textual_rhythm"           # Prosodic and rhythmic patterns
    LINGUISTIC_STRUCTURE = "linguistic_structure"  # Syntax and grammar patterns  
    NARRATIVE_VOICE = "narrative_voice"         # Persona and perspective
    CONTENT_DOMAIN = "content_domain"           # Namespace and topic areas
    STYLISTIC_SIGNATURE = "stylistic_signature" # Writing style markers
    DISCOURSE_PATTERNS = "discourse_patterns"   # Conversation and dialogue
    EMOTIONAL_RESONANCE = "emotional_resonance" # Sentiment and tone
    COGNITIVE_COMPLEXITY = "cognitive_complexity" # Readability and sophistication


class AttributeSubcategory(str, Enum):
    """Detailed subcategories for precise classification"""
    
    # Textual Rhythm subcategories
    SENTENCE_FLOW = "sentence_flow"
    PUNCTUATION_RHYTHM = "punctuation_rhythm" 
    PAUSE_PATTERNS = "pause_patterns"
    SYLLABIC_PATTERNS = "syllabic_patterns"
    
    # Linguistic Structure subcategories
    GRAMMATICAL_COMPLEXITY = "grammatical_complexity"
    PART_OF_SPEECH_DISTRIBUTION = "part_of_speech_distribution"
    DEPENDENCY_STRUCTURE = "dependency_structure"
    CLAUSE_ARCHITECTURE = "clause_architecture"
    
    # Narrative Voice subcategories
    PERSPECTIVE_MARKERS = "perspective_markers"
    AUTHORIAL_PRESENCE = "authorial_presence"
    CHARACTER_VOICE = "character_voice"
    NARRATIVE_DISTANCE = "narrative_distance"
    
    # Content Domain subcategories
    THEMATIC_RESONANCE = "thematic_resonance"
    CONCEPTUAL_DENSITY = "conceptual_density"
    DOMAIN_SPECIFICITY = "domain_specificity"
    CULTURAL_MARKERS = "cultural_markers"
    
    # Stylistic Signature subcategories
    RHETORICAL_DEVICES = "rhetorical_devices"
    IMAGERY_PATTERNS = "imagery_patterns"
    LEXICAL_SOPHISTICATION = "lexical_sophistication"
    REGISTER_CONSISTENCY = "register_consistency"
    
    # Discourse Patterns subcategories
    CONVERSATIONAL_FLOW = "conversational_flow"
    DIALOGUE_AUTHENTICITY = "dialogue_authenticity"
    INTERACTIVE_MARKERS = "interactive_markers"
    TURN_TAKING_PATTERNS = "turn_taking_patterns"
    
    # Emotional Resonance subcategories
    SENTIMENT_STABILITY = "sentiment_stability"
    EMOTIONAL_INTENSITY = "emotional_intensity"
    TONAL_CONSISTENCY = "tonal_consistency"
    AFFECTIVE_MARKERS = "affective_markers"
    
    # Cognitive Complexity subcategories
    CONCEPTUAL_ABSTRACTION = "conceptual_abstraction"
    LOGICAL_COHERENCE = "logical_coherence"
    INFORMATIONAL_DENSITY = "informational_density"
    PROCESSING_DIFFICULTY = "processing_difficulty"


class HumanReadableAttribute(BaseModel):
    """Human-readable attribute with semantic meaning"""
    
    # Identification
    attribute_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    canonical_name: str = Field(..., description="Technical canonical name")
    display_name: str = Field(..., description="Human-readable display name")
    description: str = Field(..., description="Clear explanation of what this measures")
    
    # Classification
    category: AttributeCategory = Field(..., description="Top-level semantic category")
    subcategory: AttributeSubcategory = Field(..., description="Detailed subcategory")
    
    # Value and metadata
    value: Union[float, int, str, bool] = Field(..., description="The measured value")
    confidence: float = Field(0.0, ge=0.0, le=1.0, description="Confidence in measurement")
    unit: Optional[str] = Field(None, description="Unit of measurement if applicable")
    
    # Semantic context
    interpretation_guide: str = Field(..., description="How to interpret this value")
    typical_range: Optional[Dict[str, float]] = Field(None, description="Expected range for this attribute")
    
    # Processing metadata
    extraction_method: str = Field(..., description="How this attribute was calculated")
    quality_score: float = Field(0.0, ge=0.0, le=1.0, description="Quality of the extraction")
    
    # Temporal tracking
    created_at: datetime = Field(default_factory=datetime.now)
    version: str = Field("1.0", description="Attribute definition version")
    
    @validator('display_name')
    def display_name_must_be_readable(cls, v):
        """Ensure display names are human-readable"""
        if len(v.split()) < 2:
            raise ValueError('Display name should be descriptive (multiple words)')
        return v
    
    @root_validator(skip_on_failure=True)
    def category_subcategory_consistency(cls, values):
        """Ensure subcategory matches category"""
        category = values.get('category')
        subcategory = values.get('subcategory')
        
        # Define valid subcategory mappings
        valid_mappings = {
            AttributeCategory.TEXTUAL_RHYTHM: [
                AttributeSubcategory.SENTENCE_FLOW,
                AttributeSubcategory.PUNCTUATION_RHYTHM,
                AttributeSubcategory.PAUSE_PATTERNS,
                AttributeSubcategory.SYLLABIC_PATTERNS
            ],
            AttributeCategory.LINGUISTIC_STRUCTURE: [
                AttributeSubcategory.GRAMMATICAL_COMPLEXITY,
                AttributeSubcategory.PART_OF_SPEECH_DISTRIBUTION,
                AttributeSubcategory.DEPENDENCY_STRUCTURE,
                AttributeSubcategory.CLAUSE_ARCHITECTURE
            ],
            # ... (other mappings would be defined here)
        }
        
        if category and subcategory:
            if category in valid_mappings and subcategory not in valid_mappings[category]:
                raise ValueError(f'Subcategory {subcategory} not valid for category {category}')
        
        return values


class AttributeCollection(BaseModel):
    """Collection of attributes for a text segment"""
    
    collection_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_id: str = Field(..., description="Source text identifier")
    text_sample: str = Field(..., max_length=500, description="Sample of analyzed text")
    
    # Attributes organized by category
    textual_rhythm: List[HumanReadableAttribute] = Field(default_factory=list)
    linguistic_structure: List[HumanReadableAttribute] = Field(default_factory=list)
    narrative_voice: List[HumanReadableAttribute] = Field(default_factory=list)
    content_domain: List[HumanReadableAttribute] = Field(default_factory=list)
    stylistic_signature: List[HumanReadableAttribute] = Field(default_factory=list)
    discourse_patterns: List[HumanReadableAttribute] = Field(default_factory=list)
    emotional_resonance: List[HumanReadableAttribute] = Field(default_factory=list)
    cognitive_complexity: List[HumanReadableAttribute] = Field(default_factory=list)
    
    # Collection metadata
    extraction_timestamp: datetime = Field(default_factory=datetime.now)
    total_attributes: int = Field(0, description="Total number of attributes")
    quality_metrics: Dict[str, float] = Field(default_factory=dict)
    
    def add_attribute(self, attribute: HumanReadableAttribute):
        """Add an attribute to the appropriate category"""
        category_map = {
            AttributeCategory.TEXTUAL_RHYTHM: self.textual_rhythm,
            AttributeCategory.LINGUISTIC_STRUCTURE: self.linguistic_structure,
            AttributeCategory.NARRATIVE_VOICE: self.narrative_voice,
            AttributeCategory.CONTENT_DOMAIN: self.content_domain,
            AttributeCategory.STYLISTIC_SIGNATURE: self.stylistic_signature,
            AttributeCategory.DISCOURSE_PATTERNS: self.discourse_patterns,
            AttributeCategory.EMOTIONAL_RESONANCE: self.emotional_resonance,
            AttributeCategory.COGNITIVE_COMPLEXITY: self.cognitive_complexity,
        }
        
        if attribute.category in category_map:
            category_map[attribute.category].append(attribute)
            self.total_attributes += 1
    
    def get_attributes_by_category(self, category: AttributeCategory) -> List[HumanReadableAttribute]:
        """Get all attributes in a specific category"""
        category_map = {
            AttributeCategory.TEXTUAL_RHYTHM: self.textual_rhythm,
            AttributeCategory.LINGUISTIC_STRUCTURE: self.linguistic_structure,
            AttributeCategory.NARRATIVE_VOICE: self.narrative_voice,
            AttributeCategory.CONTENT_DOMAIN: self.content_domain,
            AttributeCategory.STYLISTIC_SIGNATURE: self.stylistic_signature,
            AttributeCategory.DISCOURSE_PATTERNS: self.discourse_patterns,
            AttributeCategory.EMOTIONAL_RESONANCE: self.emotional_resonance,
            AttributeCategory.COGNITIVE_COMPLEXITY: self.cognitive_complexity,
        }
        return category_map.get(category, [])


# Attribute transformation mappings from technical to human-readable
ATTRIBUTE_TRANSFORMATIONS = {
    # Textual Rhythm transformations
    'avg_sentence_length': HumanReadableAttribute(
        canonical_name='avg_sentence_length',
        display_name='Average Sentence Flow Length',
        description='The typical number of words in sentences, indicating narrative pacing',
        category=AttributeCategory.TEXTUAL_RHYTHM,
        subcategory=AttributeSubcategory.SENTENCE_FLOW,
        interpretation_guide='Higher values indicate more complex, flowing prose; lower values suggest crisp, direct communication',
        typical_range={'min': 8.0, 'max': 25.0, 'optimal': 15.0},
        extraction_method='Statistical analysis of sentence word counts',
        value=0.0  # Will be populated during extraction
    ),
    
    'comma_density': HumanReadableAttribute(
        canonical_name='comma_density',
        display_name='Comma-Driven Pause Frequency',
        description='How often commas create micro-pauses in the narrative rhythm',
        category=AttributeCategory.TEXTUAL_RHYTHM,
        subcategory=AttributeSubcategory.PUNCTUATION_RHYTHM,
        interpretation_guide='Higher density indicates more complex, clause-heavy sentences with frequent pauses',
        typical_range={'min': 0.01, 'max': 0.08, 'optimal': 0.03},
        extraction_method='Ratio of commas to total character count',
        value=0.0
    ),
    
    'flesch_ease': HumanReadableAttribute(
        canonical_name='flesch_ease',
        display_name='Cognitive Accessibility Score',
        description='How easily the text can be understood by readers of different backgrounds',
        category=AttributeCategory.COGNITIVE_COMPLEXITY,
        subcategory=AttributeSubcategory.PROCESSING_DIFFICULTY,
        interpretation_guide='Scores 90-100: very easy; 60-70: standard; 30-50: difficult; 0-30: very difficult',
        typical_range={'min': 0.0, 'max': 100.0, 'optimal': 60.0},
        extraction_method='Flesch Reading Ease formula based on sentence and syllable patterns',
        value=0.0
    ),
    
    'noun_ratio': HumanReadableAttribute(
        canonical_name='noun_ratio',
        display_name='Substantive Content Density',
        description='The proportion of concrete concepts and entities in the text',
        category=AttributeCategory.LINGUISTIC_STRUCTURE,
        subcategory=AttributeSubcategory.PART_OF_SPEECH_DISTRIBUTION,
        interpretation_guide='Higher ratios indicate descriptive, entity-rich content; lower ratios suggest action-oriented or abstract prose',
        typical_range={'min': 0.15, 'max': 0.35, 'optimal': 0.25},
        extraction_method='Ratio of nouns to total non-punctuation tokens using POS tagging',
        value=0.0
    ),
    
    'subordination_ratio': HumanReadableAttribute(
        canonical_name='subordination_ratio',
        display_name='Narrative Complexity Architecture',
        description='How much the text uses layered, hierarchical sentence structures',
        category=AttributeCategory.LINGUISTIC_STRUCTURE,
        subcategory=AttributeSubcategory.CLAUSE_ARCHITECTURE,
        interpretation_guide='Higher values indicate sophisticated, multi-layered reasoning; lower values suggest direct communication',
        typical_range={'min': 0.05, 'max': 0.25, 'optimal': 0.12},
        extraction_method='Ratio of subordinate clauses to total clauses using dependency parsing',
        value=0.0
    ),
}


def transform_technical_attributes(technical_features: Dict[str, Any]) -> AttributeCollection:
    """Transform technical feature dictionary into human-readable attribute collection"""
    
    collection = AttributeCollection(
        source_id="conversion_source",
        text_sample="Sample text for attribute extraction"
    )
    
    for technical_name, value in technical_features.items():
        if technical_name in ATTRIBUTE_TRANSFORMATIONS:
            # Get the template and set the actual value
            attr_template = ATTRIBUTE_TRANSFORMATIONS[technical_name].copy(deep=True)
            attr_template.value = value
            
            # Calculate confidence based on value reasonableness
            if attr_template.typical_range:
                min_val = attr_template.typical_range['min']
                max_val = attr_template.typical_range['max']
                if min_val <= value <= max_val:
                    attr_template.confidence = 0.9
                else:
                    # Confidence decreases with distance from expected range
                    distance = min(abs(value - min_val), abs(value - max_val))
                    range_size = max_val - min_val
                    attr_template.confidence = max(0.1, 0.9 - (distance / range_size))
            else:
                attr_template.confidence = 0.7  # Default confidence
            
            collection.add_attribute(attr_template)
    
    return collection


if __name__ == "__main__":
    # Example usage
    technical_features = {
        'avg_sentence_length': 18.5,
        'comma_density': 0.045,
        'flesch_ease': 67.2,
        'noun_ratio': 0.28,
        'subordination_ratio': 0.15
    }
    
    human_readable = transform_technical_attributes(technical_features)
    print("Transformed attributes:")
    print(human_readable.json(indent=2))