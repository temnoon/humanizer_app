#!/usr/bin/env python3
"""Test script to check if LPE imports work correctly."""

import sys
from pathlib import Path

# Add the src directory to Python path for imports
current_dir = Path(__file__).parent
src_dir = current_dir.parent / "src"
sys.path.insert(0, str(src_dir))
sys.path.insert(0, str(current_dir))

print(f"Current directory: {current_dir}")
print(f"Src directory: {src_dir}")
print(f"Python path: {sys.path[:3]}")

try:
    print("Testing imports...")
    from lpe_core.projection import ProjectionEngine, TranslationChain
    from lpe_core.maieutic import MaieuticDialogue
    from lpe_core.translation_roundtrip import LanguageRoundTripAnalyzer
    from lpe_core.llm_provider import get_llm_provider
    from lpe_core.models import Projection, MaieuticSession, RoundTripResult
    
    print("✅ All imports successful!")
    
    # Test basic functionality
    print("Testing LLM provider...")
    provider = get_llm_provider()
    print(f"✅ LLM provider: {provider.__class__.__name__}")
    
    # Test basic generation
    print("Testing generation...")
    response = provider.generate("Hello, world!", "You are a helpful assistant.")
    print(f"✅ Generation response: {response[:50]}...")
    
    print("🎉 All tests passed!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)