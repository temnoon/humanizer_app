"""
Lamish Projection Engine core module for Humanizer API.
Integrated from lpe_dev project.
"""

from .projection import ProjectionEngine, TranslationChain, Projection
from .maieutic import MaieuticDialogue, MaieuticSession
from .translation_roundtrip import LanguageRoundTripAnalyzer, RoundTripResult
from .llm_provider import LLMProvider, get_llm_provider
from .models import ProjectionStep, DialogueTurn

__all__ = [
    'ProjectionEngine',
    'TranslationChain', 
    'Projection',
    'MaieuticDialogue',
    'MaieuticSession',
    'LanguageRoundTripAnalyzer',
    'RoundTripResult',
    'LLMProvider',
    'get_llm_provider',
    'ProjectionStep',
    'DialogueTurn'
]