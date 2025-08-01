#!/usr/bin/env python3
"""
Full Projection Demo - Show complete narrative transformations
"""

import json
import random
from pathlib import Path
from simple_projection_demo import extract_narrative_dna

def enhanced_transform(original_text: str, source_attr: dict, target_dna: dict) -> str:
    """Enhanced transformation with more comprehensive DNA-based changes"""
    
    # Get source text and DNA
    source_text = source_attr.get('text_sample', '')
    
    # Start with original text
    transformed = original_text
    
    # Apply persona transformation
    persona = target_dna['persona']
    
    if persona == 'philosophical_narrator':
        # Philosophical, reflective voice
        transformed = transformed.replace("I was", "I found myself in a state of being")
        transformed = transformed.replace("scared", "experiencing existential dread")
        transformed = transformed.replace("tired", "weary from the weight of circumstance")
        transformed = transformed.replace("What was", "One must ponder: what was")
        
    elif persona == 'analytical_observer':
        # Clinical, detached analysis
        transformed = transformed.replace("I was", "The subject exhibited signs of")
        transformed = transformed.replace("scared", "acute anxiety")
        transformed = transformed.replace("My phone", "The communication device")
        transformed = transformed.replace("dad", "paternal figure")
        
    elif persona == 'dramatic_voice':
        # Theatrical, emotional emphasis
        transformed = transformed.replace("I was", "There I was, utterly")
        transformed = transformed.replace("scared", "terrified beyond measure")
        transformed = transformed.replace("water leaking", "treacherous waters flooding")
        transformed = transformed.replace("no one was answering", "the world had abandoned me")
        
    elif persona == 'conversational_voice':
        # Casual, informal tone
        transformed = transformed.replace("I was tired, cold, scared", "So there I was, exhausted, freezing, and pretty freaked out")
        transformed = transformed.replace("What was the number?", "What was that number again?")
        transformed = transformed.replace("I hadn't called it", "I never got around to calling it")
        
    elif persona == 'authoritative_narrator':
        # Commanding, confident voice
        transformed = transformed.replace("I was", "I remained")
        transformed = transformed.replace("scared", "vigilant in the face of danger")
        transformed = transformed.replace("no one was answering", "my calls went unanswered")
        transformed = transformed.replace("What was", "I needed to recall")
        
    elif persona == 'intimate_storyteller':
        # Personal, confessional tone
        transformed = transformed.replace("I was", "Here I was, feeling so")
        transformed = transformed.replace("scared", "vulnerable and afraid")
        transformed = transformed.replace("My dad", "My dear father")
        transformed = transformed.replace("I hadn't called", "I'd been meaning to call but hadn't")
    
    # Apply namespace transformation
    namespace = target_dna['namespace']
    
    if namespace == 'moral_philosophy':
        # Ethical, value-based framing
        transformed = transformed.replace("basement", "depths of moral uncertainty")
        transformed = transformed.replace("water", "the rising tide of consequence")
        transformed = transformed.replace("phone", "instrument of human connection")
        
    elif namespace == 'psychological_narrative':
        # Mental/emotional focus
        transformed = transformed.replace("basement", "subconscious depths")
        transformed = transformed.replace("water up to my ankles", "anxiety washing over me")
        transformed = transformed.replace("phone was below 10%", "my lifeline was fading")
        
    elif namespace == 'urban_narrative':
        # City life, modern context
        transformed = transformed.replace("basement", "lower level of the building")
        transformed = transformed.replace("water leaking", "the building's plumbing failing")
        transformed = transformed.replace("phone", "smartphone")
        
    elif namespace == 'historical_fiction':
        # Period-appropriate language
        transformed = transformed.replace("phone", "telegraph device")
        transformed = transformed.replace("10% power", "nearly drained of its electrical essence")
        transformed = transformed.replace("dad", "father")
        
    elif namespace == 'literary_realism':
        # Detailed, realistic description
        transformed = transformed.replace("water leaking", "water seeping through the foundation")
        transformed = transformed.replace("up to my ankles", "pooling around my feet")
        transformed = transformed.replace("below 10%", "critically low on battery")
    
    # Apply style transformation
    style = target_dna['style']
    
    if style == 'stream_of_consciousness':
        # Flowing, unstructured thoughts
        transformed = transformed.replace(". ", "... ")
        transformed = transformed.replace("?", "? Or was it...?")
        transformed = "Thoughts racing: " + transformed
        
    elif style == 'lyrical_prose':
        # Poetic, musical language
        transformed = transformed.replace("cold", "bone-deep chill")
        transformed = transformed.replace("water", "liquid sorrow")
        transformed = transformed.replace("ankles", "weary feet")
        
    elif style == 'analytical_writing':
        # Structured, logical flow
        transformed = "Initial conditions: " + transformed
        transformed = transformed.replace(". ", ". Subsequently, ")
        transformed = transformed.replace("What was", "The critical question arose: what was")
        
    elif style == 'dialogue_heavy':
        # Add quoted thoughts
        transformed = transformed.replace("What was the number?", "'What was that number?' I asked myself.")
        transformed = transformed.replace("I hadn't called it", "I thought, 'I really should have called by now.'")
        
    elif style == 'contemplative_style':
        # Reflective, meditative
        transformed = transformed.replace("I was", "In that moment, I became aware I was")
        transformed = transformed.replace("What was", "I paused to consider what was")
        transformed = "In quiet reflection: " + transformed
    
    return transformed

def full_projection_test():
    """Show complete narrative with three distinct projections"""
    
    # A more substantial narrative for better projection demonstration
    original_narrative = """I was tired, cold, scared. The basement was flooding - water already up to my ankles, seeping through cracks in the old foundation. My phone was below 10% power, and no one was answering my desperate calls. What was the number? My dad had given me his new number just last week, but I hadn't called it yet. The darkness pressed in around me, and I could hear the water rising. Time was running out."""
    
    print("🎭 FULL NARRATIVE PROJECTION DEMONSTRATION")
    print("=" * 80)
    print("📖 ORIGINAL NARRATIVE:")
    print("-" * 40)
    print(f"{original_narrative}")
    print()
    
    # Load specific attributes with distinct DNA patterns
    test_files = [
        ('attributes_3207.json', 'Book 3207 (Leviathan - Political Philosophy)'),
        ('attributes_1056.json', 'Book 1056 (Literary Classic)'),
        ('attributes_5015.json', 'Book 5015 (Historical Document)')
    ]
    
    projections = []
    
    for i, (filename, description) in enumerate(test_files, 1):
        file_path = Path('mass_attributes') / filename
        
        if not file_path.exists():
            print(f"❌ File not found: {filename}")
            continue
        
        # Load file and get a specific attribute with interesting DNA
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Find an attribute with unique DNA (avoid duplicates)
        unique_attrs = []
        seen_dna = set()
        
        for attr in data['attributes']:
            dna = attr['narrative_dna']
            dna_signature = f"{dna['persona']}|{dna['namespace']}|{dna['style']}"
            if dna_signature not in seen_dna:
                unique_attrs.append(attr)
                seen_dna.add(dna_signature)
                if len(unique_attrs) >= 5:  # Get several options
                    break
        
        # Select one with distinct characteristics
        if unique_attrs:
            selected_attr = unique_attrs[min(i-1, len(unique_attrs)-1)]
        else:
            selected_attr = data['attributes'][0]
        
        dna = extract_narrative_dna(selected_attr)
        
        # Transform the narrative
        projected = enhanced_transform(original_narrative, selected_attr, dna)
        
        projections.append({
            'num': i,
            'source': description,
            'dna': dna,
            'projection': projected,
            'sample_text': selected_attr['text_sample'][:100] + "..."
        })
    
    # Display all projections
    print("🧬 PROJECTIONS THROUGH DIFFERENT NARRATIVE DNA:")
    print("=" * 80)
    
    for proj in projections:
        print(f"\n{proj['num']}. PROJECTION via {proj['dna']['persona'].upper().replace('_', ' ')}")
        print(f"   Source: {proj['source']}")
        print(f"   DNA: {proj['dna']['persona']} | {proj['dna']['namespace']} | {proj['dna']['style']}")
        print(f"   Confidence: {proj['dna']['confidence']}")
        print(f"   Sample from source: {proj['sample_text']}")
        print("-" * 60)
        print(f"{proj['projection']}")
        print()
    
    print("=" * 80)
    print("🎯 COMPARISON ANALYSIS:")
    print("-" * 40)
    print("Notice how each projection transforms the narrative through:")
    print("• PERSONA: Different narrative voices and perspectives")
    print("• NAMESPACE: Different world contexts and domain language")  
    print("• STYLE: Different linguistic patterns and structures")
    print()
    print("The same core story (flooding basement, phone dying, need to call dad)")
    print("becomes three distinct narrative experiences while preserving the essence.")
    print("=" * 80)

if __name__ == "__main__":
    full_projection_test()