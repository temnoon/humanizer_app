#!/usr/bin/env python3
"""
Simple Projection Demo - Apply attributes to transform narratives
"""

import json
import sys
import random
from pathlib import Path
from typing import Dict, List, Any

def load_sample_attributes(attributes_dir: str = "mass_attributes", count: int = 3) -> List[Dict]:
    """Load sample attributes from the mass collection"""
    attrs_path = Path(attributes_dir)
    if not attrs_path.exists():
        print(f"❌ Attributes directory not found: {attributes_dir}")
        print(f"   Looking in: {attrs_path.absolute()}")
        return []
    
    # Get random attribute files
    files = list(attrs_path.glob("*.json"))
    if not files:
        print("❌ No attribute files found")
        print(f"   Checked: {attrs_path.absolute()}")
        return []
    
    print(f"📚 Found {len(files)} attribute files")
    sample_files = random.sample(files, min(count, len(files)))
    collected_attrs = []
    
    for file_path in sample_files:
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Get a random attribute from this file
            attributes = data.get('attributes', [])
            if attributes:
                attr = random.choice(attributes)
                collected_attrs.append({
                    'source_file': file_path.name,
                    'book_id': data.get('book_id'),
                    'attribute': attr
                })
                print(f"✅ Loaded attribute from {file_path.name} (Book {data.get('book_id')})")
        except Exception as e:
            print(f"⚠️  Error loading {file_path.name}: {e}")
            continue
    
    return collected_attrs

def extract_narrative_dna(attribute: Dict) -> Dict:
    """Extract the narrative DNA components"""
    dna = attribute.get('narrative_dna', {})
    return {
        'persona': dna.get('persona', 'unknown'),
        'namespace': dna.get('namespace', 'unknown'), 
        'style': dna.get('style', 'unknown'),
        'confidence': dna.get('confidence', 0.0)
    }

def simple_transform(original_text: str, source_attr: Dict, target_dna: Dict) -> str:
    """Simple transformation using attribute patterns"""
    
    # Get source text and DNA
    source_text = source_attr.get('text_sample', '')
    source_dna = extract_narrative_dna(source_attr)
    
    # Simple pattern matching and style transfer
    transformed = original_text
    
    # Apply persona transformation based on discovered attributes
    if target_dna['persona'] == 'extracted_narrator':
        # Classical literature style - more formal
        transformed = transformed.replace("I was", "I found myself")
        transformed = transformed.replace("scared", "filled with trepidation")
        transformed = transformed.replace("tired", "weary beyond measure")
        transformed = transformed.replace("What was", "What, pray tell, was")
        
    # Apply namespace transformation
    if target_dna['namespace'] == 'classical_literature':
        # Add period-appropriate language
        transformed = transformed.replace("phone", "communication device")
        transformed = transformed.replace("basement", "lower chambers")
        transformed = transformed.replace("10% power", "nearly depleted of energy")
        transformed = transformed.replace("dad", "father")
        
    # Apply style transformation
    if target_dna['style'] == 'prose_narrative':
        # Add narrative flow and descriptive elements
        transformed = transformed.replace("there was water", "the relentless waters had begun their invasion")
        transformed = transformed.replace("up to my ankles", "rising steadily about my person")
        transformed = transformed.replace("no one was answering", "my calls met only with silence")
        
    # Add some variation based on source text patterns
    if "captain" in source_text.lower() or "officer" in source_text.lower():
        # Military/authority influence
        transformed = "In this dire circumstance, " + transformed
        transformed = transformed.replace("I ", "I steadfastly ")
        
    elif "energy" in source_text.lower() or "persevering" in source_text.lower():
        # Determined/persistent influence
        transformed = transformed.replace("but ", "yet with unwavering resolve ")
        
    return transformed

def demo_projection():
    """Demonstrate narrative projection with attributes"""
    print("🧬 Simple Attribute Projection Demo")
    print("=" * 50)
    
    # Load sample attributes
    print("📚 Loading sample attributes...")
    sample_attrs = load_sample_attributes(count=3)
    
    if not sample_attrs:
        print("❌ No attributes loaded. Exiting.")
        return
    
    print(f"✅ Loaded {len(sample_attrs)} sample attributes\n")
    
    # Sample narrative to transform
    original_narrative = """The hero walked through the dark forest. 
He knew that danger awaited him, but he pressed on. 
The ancient trees whispered secrets in the wind."""
    
    print("📖 Original Narrative:")
    print(f"   {original_narrative}")
    print()
    
    # Show available attributes
    print("🎯 Available DNA Patterns:")
    for i, attr_data in enumerate(sample_attrs):
        attr = attr_data['attribute'] 
        dna = extract_narrative_dna(attr)
        print(f"   {i+1}. Book {attr_data['book_id']}: {dna['persona']} | {dna['namespace']} | {dna['style']}")
        print(f"      Sample: {attr.get('text_sample', '')[:80]}...")
        print()
    
    # Apply each attribute as transformation
    print("🔄 Projections:")
    print("-" * 30)
    
    for i, attr_data in enumerate(sample_attrs):
        attr = attr_data['attribute']
        dna = extract_narrative_dna(attr)
        
        # Transform using this attribute's DNA
        projected = simple_transform(original_narrative, attr, dna)
        
        print(f"\n{i+1}. Projection via {dna['persona']} ({dna['style']}):")
        print(f"   {projected}")
        print(f"   [Confidence: {dna['confidence']:.2f}]")

def interactive_mode():
    """Interactive projection mode"""
    print("\n🎮 Interactive Mode")
    print("Type your narrative, then we'll project it through 3 different random attributes")
    print("Type 'quit' to exit\n")
    
    while True:
        user_input = input("📝 Enter narrative (or 'quit'): ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            break
            
        if not user_input:
            continue
            
        # Load 3 random attributes
        attrs = load_sample_attributes(count=3)
        if not attrs:
            print("❌ No attributes available")
            continue
            
        print(f"\n🔄 Projecting through {len(attrs)} different attributes:")
        print("=" * 60)
        
        for i, attr_data in enumerate(attrs, 1):
            attr = attr_data['attribute']
            dna = extract_narrative_dna(attr)
            
            # Transform using this attribute
            projected = simple_transform(user_input, attr, dna)
            
            print(f"\n{i}. 🧬 DNA: {dna['persona']} | {dna['namespace']} | {dna['style']}")
            print(f"   📚 Source: Book {attr_data['book_id']} ({attr_data['source_file']})")
            print(f"   📖 Original:  {user_input}")
            print(f"   🔄 Projected: {projected}")
            print(f"   📊 Confidence: {dna['confidence']:.2f}")
        
        print("=" * 60)

def main():
    """Main demo function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Simple attribute projection demo")
    parser.add_argument('--interactive', '-i', action='store_true', help='Interactive mode')
    parser.add_argument('--demo', '-d', action='store_true', help='Run demo (default)')
    
    args = parser.parse_args()
    
    if args.interactive:
        interactive_mode()
    else:
        demo_projection()
        
        # Ask if they want interactive mode
        response = input("\n🎮 Try interactive mode? (y/n): ").strip().lower()
        if response in ['y', 'yes']:
            interactive_mode()

if __name__ == "__main__":
    main()