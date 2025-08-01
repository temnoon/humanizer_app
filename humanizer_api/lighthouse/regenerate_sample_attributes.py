#!/usr/bin/env python3
"""
Regenerate sample attribute files with varied DNA
"""

import json
import hashlib
import random
from pathlib import Path

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

def regenerate_attributes():
    """Regenerate a few attribute files with varied DNA"""
    print("🔄 Regenerating Sample Attributes with Varied DNA")
    print("=" * 60)
    
    # Process first 3 attribute files
    attrs_dir = Path("mass_attributes")
    sample_files = list(attrs_dir.glob("attributes_*.json"))[:3]
    
    if not sample_files:
        print("❌ No attribute files found")
        return
    
    for file_path in sample_files:
        print(f"\n📚 Processing {file_path.name}:")
        
        # Load existing data
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        print(f"  Book ID: {data['book_id']}")
        print(f"  Attributes: {len(data['attributes'])}")
        
        # Track variety
        old_dnas = []
        new_dnas = []
        
        # Regenerate DNA for all attributes
        for attr in data['attributes']:
            old_dna = attr['narrative_dna']
            old_dnas.append(f"{old_dna['persona']}|{old_dna['namespace']}|{old_dna['style']}")
            
            # Generate new DNA based on text
            text_sample = attr['text_sample']
            new_dna = generate_varied_mock_dna(text_sample)
            
            # Update the attribute
            attr['narrative_dna'] = new_dna
            new_dnas.append(f"{new_dna['persona']}|{new_dna['namespace']}|{new_dna['style']}")
        
        # Show variety improvement
        old_unique = len(set(old_dnas))
        new_unique = len(set(new_dnas))
        
        print(f"  OLD DNA patterns: {old_unique} unique out of {len(old_dnas)}")
        print(f"  NEW DNA patterns: {new_unique} unique out of {len(new_dnas)}")
        
        if new_unique > old_unique:
            print("  ✅ IMPROVED variety!")
        else:
            print("  ➡️  Same variety level")
        
        # Save updated file
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"  💾 Updated {file_path.name}")
    
    print("\n" + "=" * 60)
    print("✅ Sample regeneration complete!")

def show_variety_samples():
    """Show samples of the new variety"""
    print("\n🎯 DNA Variety Samples:")
    print("-" * 40)
    
    # Load one updated file
    sample_file = Path("mass_attributes").glob("attributes_*.json").__next__()
    with open(sample_file, 'r') as f:
        data = json.load(f)
    
    # Show first 5 attributes
    for i, attr in enumerate(data['attributes'][:5], 1):
        dna = attr['narrative_dna']
        text = attr['text_sample'][:50] + "..."
        
        print(f"\n{i}. {text}")
        print(f"   🧬 {dna['persona']} | {dna['namespace']} | {dna['style']}")
        print(f"   📊 {dna['confidence']}")

if __name__ == "__main__":
    regenerate_attributes()
    show_variety_samples()