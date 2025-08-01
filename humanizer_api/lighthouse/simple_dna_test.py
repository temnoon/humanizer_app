#!/usr/bin/env python3
"""
Simple test of the new varied DNA generation
"""

import json
import hashlib
import random

def generate_varied_mock_dna(paragraph_text: str) -> dict:
    """Generate varied mock DNA based on text analysis"""
    
    # Create deterministic but varied results based on text hash
    text_hash = hashlib.md5(paragraph_text.encode()).hexdigest()
    random.seed(int(text_hash[:8], 16))
    
    # Persona variations
    personas = [
        "reflective_narrator", "dramatic_voice", "analytical_observer", 
        "poetic_speaker", "philosophical_narrator", "conversational_voice",
        "authoritative_narrator", "intimate_storyteller", "omniscient_voice"
    ]
    
    # Namespace variations  
    namespaces = [
        "literary_realism", "romantic_literature", "philosophical_discourse",
        "social_commentary", "psychological_narrative", "historical_fiction",
        "pastoral_literature", "urban_narrative", "moral_philosophy"
    ]
    
    # Style variations
    styles = [
        "descriptive_prose", "dialogue_heavy", "stream_of_consciousness",
        "formal_literary", "colloquial_narrative", "lyrical_prose",
        "analytical_writing", "dramatic_narrative", "contemplative_style"
    ]
    
    return {
        'persona': random.choice(personas),
        'namespace': random.choice(namespaces), 
        'style': random.choice(styles),
        'confidence': round(random.uniform(0.75, 0.95), 2)
    }

def test_varied_dna():
    print("🧬 Testing Varied DNA Generation")
    print("=" * 50)
    
    # Test sample texts
    test_texts = [
        "In a hole in the ground there lived a hobbit.",
        "Call me Ishmael. Some years ago I thought I would sail.",
        "It was the best of times, it was the worst of times.",
        "The ancient wisdom speaks of cycles within cycles.",
        "She walked through the moonlit garden, thinking of tomorrow."
    ]
    
    print("📖 Generating DNA for different texts:")
    print("-" * 40)
    
    all_personas = set()
    all_namespaces = set()
    all_styles = set()
    
    for i, text in enumerate(test_texts, 1):
        dna = generate_varied_mock_dna(text)
        
        all_personas.add(dna['persona'])
        all_namespaces.add(dna['namespace'])
        all_styles.add(dna['style'])
        
        print(f"\n{i}. Text: {text[:40]}...")
        print(f"   🧬 DNA: {dna['persona']} | {dna['namespace']} | {dna['style']}")
        print(f"   📊 Confidence: {dna['confidence']}")
    
    print("\n" + "=" * 50)
    print("📊 Variety Analysis:")
    print(f"  Unique Personas: {len(all_personas)} ({', '.join(sorted(all_personas))})")
    print(f"  Unique Namespaces: {len(all_namespaces)} ({', '.join(sorted(all_namespaces))})")
    print(f"  Unique Styles: {len(all_styles)} ({', '.join(sorted(all_styles))})")
    
    if len(all_personas) > 1 and len(all_namespaces) > 1 and len(all_styles) > 1:
        print("✅ SUCCESS: DNA generation shows good variety!")
    else:
        print("❌ ISSUE: DNA generation still too uniform")

def test_determinism():
    """Test that same text always produces same DNA"""
    print("\n🔄 Testing Determinism:")
    print("-" * 30)
    
    test_text = "The quick brown fox jumps over the lazy dog."
    
    # Generate DNA multiple times
    results = []
    for i in range(3):
        dna = generate_varied_mock_dna(test_text)
        results.append(dna)
        print(f"  Run {i+1}: {dna['persona']} | {dna['namespace']} | {dna['style']}")
    
    # Check if all results are identical
    if all(r == results[0] for r in results):
        print("✅ DETERMINISTIC: Same text produces same DNA")
    else:
        print("❌ NON-DETERMINISTIC: Results vary between runs")

if __name__ == "__main__":
    test_varied_dna()
    test_determinism()