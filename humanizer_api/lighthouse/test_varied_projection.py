#!/usr/bin/env python3
"""
Test projection with newly varied DNA attributes
"""

import json
import random
from pathlib import Path
from simple_projection_demo import simple_transform, extract_narrative_dna

def test_varied_projections():
    narrative = """I was tired, cold, scared ... there was water leaking into the basement, 
water already up to my ankles. My phone was below 10% power, and no one was answering. 
What was the number? My dad gave me his new number, but I hadn't called it."""
    
    print("🧬 Testing Varied Narrative Projection")
    print("=" * 60)
    print(f"📖 Original narrative:")
    print(f"   {narrative}")
    print()
    
    # Load from the specific files we updated
    updated_files = ['attributes_3207.json', 'attributes_1056.json', 'attributes_5015.json']
    
    print(f"🔄 Projecting through attributes from 3 different books:")
    print("=" * 60)
    
    for i, fname in enumerate(updated_files, 1):
        file_path = Path('mass_attributes') / fname
        
        if not file_path.exists():
            print(f"❌ File not found: {fname}")
            continue
            
        # Load file
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Get a random attribute from this file
        attr = random.choice(data['attributes'])
        dna = extract_narrative_dna(attr)
        
        # Transform using this attribute
        projected = simple_transform(narrative, attr, dna)
        
        print(f"\n{i}. 🧬 DNA: {dna['persona']} | {dna['namespace']} | {dna['style']}")
        print(f"   📚 Source: Book {data['book_id']} ({fname})")
        print(f"   📊 Confidence: {dna['confidence']}")
        print(f"   🔄 Projected:")
        print(f"      {projected}")
    
    print("\n" + "=" * 60)
    print("✅ Varied DNA projection test complete!")

def show_dna_diversity():
    """Show the diversity of DNA patterns now available"""
    print("\n📊 DNA Diversity Analysis:")
    print("-" * 40)
    
    updated_files = ['attributes_3207.json', 'attributes_1056.json', 'attributes_5015.json']
    
    all_personas = set()
    all_namespaces = set()
    all_styles = set()
    
    for fname in updated_files:
        file_path = Path('mass_attributes') / fname
        if file_path.exists():
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Sample first 10 attributes from each file
            for attr in data['attributes'][:10]:
                dna = attr['narrative_dna']
                all_personas.add(dna['persona'])
                all_namespaces.add(dna['namespace'])
                all_styles.add(dna['style'])
    
    print(f"Found across 3 books (30 attributes sampled):")
    print(f"  📝 Personas: {len(all_personas)} types ({', '.join(sorted(all_personas))})")
    print(f"  🌍 Namespaces: {len(all_namespaces)} types ({', '.join(sorted(all_namespaces))})")
    print(f"  ✍️  Styles: {len(all_styles)} types ({', '.join(sorted(all_styles))})")
    
    total_combinations = len(all_personas) * len(all_namespaces) * len(all_styles)
    print(f"  🔀 Potential combinations: {total_combinations}")

if __name__ == "__main__":
    test_varied_projections()
    show_dna_diversity()