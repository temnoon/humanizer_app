#!/usr/bin/env python3
"""
Test Full Workflow - Complete essay transformation pipeline
"""

import json
import random
from pathlib import Path
from typing import Dict, List

def load_discovered_attributes(count: int = 3) -> List[Dict]:
    """Load attributes from discovered_attributes directory"""
    attrs_path = Path("discovered_attributes")
    collected_attrs = []
    
    # Load from available files
    for file_path in attrs_path.glob("attributes_*.json"):
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Get random attributes from this file
            attributes = data.get('attributes', [])
            sample_count = min(2, len(attributes))  # Take up to 2 per book
            sample_attrs = random.sample(attributes, sample_count)
            
            for attr in sample_attrs:
                collected_attrs.append({
                    'source_file': file_path.name,
                    'book_id': data.get('book_id'),
                    'attribute': attr
                })
                
            print(f"✅ Loaded {len(sample_attrs)} attributes from {file_path.name} (Book {data.get('book_id')})")
            
        except Exception as e:
            print(f"⚠️  Error loading {file_path.name}: {e}")
            continue
    
    # Return requested count
    if len(collected_attrs) > count:
        collected_attrs = random.sample(collected_attrs, count)
    
    return collected_attrs

def extract_dna(attribute: Dict) -> Dict:
    """Extract DNA components from attribute"""
    dna = attribute.get('narrative_dna', {})
    return {
        'persona': dna.get('persona', 'classical_narrator'),
        'namespace': dna.get('namespace', 'literary'),
        'style': dna.get('style', 'formal'),
        'confidence': dna.get('confidence', 0.8)
    }

def advanced_transform(original_text: str, source_attr: Dict, target_dna: Dict) -> str:
    """Advanced transformation using discovered DNA patterns"""
    
    source_text = source_attr.get('text_sample', '')
    transformed = original_text
    
    # Persona-based transformations
    persona = target_dna.get('persona', 'classical_narrator')
    
    if persona == 'classical_narrator' or 'formal' in persona:
        # Formal literary style
        transformed = transformed.replace("I was", "I found myself")
        transformed = transformed.replace("I went", "I proceeded")
        transformed = transformed.replace("really scared", "filled with considerable apprehension")
        transformed = transformed.replace("super tired", "exceedingly weary")
        transformed = transformed.replace("phone", "communication device")
        
    elif 'dialogue' in persona or 'conversational' in persona:
        # Conversational style
        transformed = transformed.replace("said", "remarked")
        transformed = transformed.replace("told", "informed")
        
    # Namespace-based transformations  
    namespace = target_dna.get('namespace', 'literary')
    
    if 'classical' in namespace or 'literary' in namespace:
        # Classical references and vocabulary
        transformed = transformed.replace("building", "edifice")
        transformed = transformed.replace("basement", "lower chambers")
        transformed = transformed.replace("dad", "father")
        transformed = transformed.replace("mom", "mother")
        
    # Style-based transformations
    style = target_dna.get('style', 'formal')
    
    if 'formal' in style or 'prose' in style:
        # Add descriptive elements and flowing prose
        transformed = transformed.replace("there was", "there existed")
        transformed = transformed.replace("I saw", "I observed")
        transformed = transformed.replace("very", "exceedingly")
        
    # Apply source text influence patterns
    if "strange" in source_text.lower():
        transformed = "In a most peculiar turn of events, " + transformed
    elif "performance" in source_text.lower():
        transformed = transformed.replace("I did", "I performed")
        
    return transformed

def test_projection_pipeline():
    """Test the complete projection pipeline"""
    
    print("🧬 Full Humanizer Workflow Test")
    print("=" * 60)
    
    # Step 1: Load discovered attributes
    print("📚 Step 1: Loading discovered DNA attributes...")
    sample_attrs = load_discovered_attributes(count=3)
    
    if not sample_attrs:
        print("❌ No attributes available. Please run attribute discovery first.")
        return
    
    print(f"✅ Loaded {len(sample_attrs)} DNA patterns\n")
    
    # Step 2: Sample essay to transform
    sample_essay = """The old building stood at the end of the street, its windows dark and empty. 
I was really scared as I approached the front door, but I knew I had to go inside.
My phone was almost dead, and I couldn't call my dad for help.
The basement was flooded, and there was water up to my ankles.
I went upstairs, but no one was answering when I called out."""
    
    print("📖 Step 2: Original Essay:")
    print("-" * 30)
    print(f"{sample_essay}")
    print()
    
    # Step 3: Show available DNA patterns
    print("🎯 Step 3: Available DNA Patterns:")
    print("-" * 40)
    for i, attr_data in enumerate(sample_attrs, 1):
        attr = attr_data['attribute']
        dna = extract_dna(attr)
        print(f"{i}. Book {attr_data['book_id']} ({attr_data['source_file']}):")
        print(f"   📝 Sample: {attr.get('text_sample', '')[:80]}...")
        print(f"   🧬 DNA: {dna['persona']} | {dna['namespace']} | {dna['style']}")
        print(f"   📊 Confidence: {dna['confidence']:.2f}")
        print()
    
    # Step 4: Apply transformations
    print("🔄 Step 4: Essay Projections:")
    print("=" * 50)
    
    for i, attr_data in enumerate(sample_attrs, 1):
        attr = attr_data['attribute']
        dna = extract_dna(attr)
        
        # Transform the essay using this DNA pattern
        projected_essay = advanced_transform(sample_essay, attr, dna)
        
        print(f"\n{i}. 🧬 DNA Pattern: {dna['persona']} ({dna['style']})")
        print(f"📚 Source: Book {attr_data['book_id']}")
        print(f"📊 Confidence: {dna['confidence']:.2f}")
        print("📖 Projected Essay:")
        print("-" * 30)
        print(f"{projected_essay}")
        print()
    
    # Step 5: Interactive mode
    print("🎮 Step 5: Interactive Testing")
    print("=" * 40)
    print("Try your own text with these discovered patterns!")
    
    return sample_attrs

def interactive_mode(available_attrs: List[Dict]):
    """Interactive projection testing"""
    
    print("\n🎮 Interactive Mode - Enter your text to transform")
    print("Type 'quit' to exit")
    
    while True:
        try:
            user_input = input("\n📝 Enter your text (or 'quit'): ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
                
            if not user_input:
                continue
            
            # Apply 2 random transformations
            test_attrs = random.sample(available_attrs, min(2, len(available_attrs)))
            
            print(f"\n🔄 Transforming through {len(test_attrs)} DNA patterns:")
            print("=" * 50)
            
            for i, attr_data in enumerate(test_attrs, 1):
                attr = attr_data['attribute']
                dna = extract_dna(attr)
                
                projected = advanced_transform(user_input, attr, dna)
                
                print(f"\n{i}. 🧬 {dna['persona']} | {dna['namespace']} | {dna['style']}")
                print(f"📚 Source: Book {attr_data['book_id']}")
                print(f"📖 Original:  {user_input}")
                print(f"🔄 Projected: {projected}")
                print(f"📊 Confidence: {dna['confidence']:.2f}")
            
            print("=" * 50)
            
        except (EOFError, KeyboardInterrupt):
            break
    
    print("\n👋 Interactive mode ended.")

def main():
    """Main test function"""
    
    # Run the complete workflow test
    attrs = test_projection_pipeline()
    
    if attrs:
        # Ask for interactive mode
        try:
            response = input("\n🎮 Try interactive mode? (y/n): ").strip().lower()
            if response in ['y', 'yes']:
                interactive_mode(attrs)
        except (EOFError, KeyboardInterrupt):
            pass
    
    print("\n🎉 Full workflow test complete!")

if __name__ == "__main__":
    main()