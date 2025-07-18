"""Data models for LPE system."""
import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List, Optional

@dataclass
class ProjectionStep:
    """Represents a single step in the transformation chain."""
    name: str
    input_snapshot: str
    output_snapshot: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    duration_ms: int = 0

@dataclass
class Projection:
    """Complete projection with all transformation steps."""
    id: Optional[int]
    source_narrative: str
    final_projection: str
    reflection: str
    persona: str
    namespace: str
    style: str
    steps: List[ProjectionStep] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    embedding: Optional[List[float]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert projection to dictionary for storage."""
        return {
            'id': self.id,
            'source_narrative': self.source_narrative,
            'final_projection': self.final_projection,
            'reflection': self.reflection,
            'persona': self.persona,
            'namespace': self.namespace,
            'style': self.style,
            'steps': [
                {
                    'name': step.name,
                    'input_snapshot': step.input_snapshot,
                    'output_snapshot': step.output_snapshot,
                    'metadata': step.metadata,
                    'timestamp': step.timestamp.isoformat(),
                    'duration_ms': step.duration_ms
                }
                for step in self.steps
            ],
            'created_at': self.created_at.isoformat(),
            'embedding': self.embedding
        }

@dataclass
class DialogueTurn:
    """A single turn in the maieutic dialogue."""
    question: str
    answer: str
    timestamp: datetime = field(default_factory=datetime.now)
    insights: List[str] = field(default_factory=list)
    depth_level: int = 0

@dataclass
class MaieuticSession:
    """A complete maieutic dialogue session."""
    id: Optional[int] = None
    initial_narrative: str = ""
    goal: str = ""
    turns: List[DialogueTurn] = field(default_factory=list)
    extracted_elements: Dict[str, Any] = field(default_factory=dict)
    final_understanding: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary."""
        return {
            'id': self.id,
            'initial_narrative': self.initial_narrative,
            'goal': self.goal,
            'turns': [
                {
                    'question': turn.question,
                    'answer': turn.answer,
                    'insights': turn.insights,
                    'depth_level': turn.depth_level,
                    'timestamp': turn.timestamp.isoformat()
                }
                for turn in self.turns
            ],
            'extracted_elements': self.extracted_elements,
            'final_understanding': self.final_understanding,
            'created_at': self.created_at.isoformat()
        }

@dataclass
class LanguageTranslation:
    """Represents a single language translation."""
    source_text: str
    target_text: str
    source_language: str
    target_language: str
    timestamp: datetime = field(default_factory=datetime.now)
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RoundTripResult:
    """Result of a complete round-trip translation."""
    original_text: str
    final_text: str
    intermediate_language: str
    translations: List[LanguageTranslation] = field(default_factory=list)
    semantic_drift: float = 0.0
    linguistic_analysis: Dict[str, Any] = field(default_factory=dict)
    preserved_elements: List[str] = field(default_factory=list)
    lost_elements: List[str] = field(default_factory=list)
    gained_elements: List[str] = field(default_factory=list)