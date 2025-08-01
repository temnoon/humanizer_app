#!/usr/bin/env python3
"""
Gilgamesh 10-Projection Test
Show the first page of Gilgamesh projected through 10 different attributes with metadata
"""

import json
import random
from pathlib import Path
from simple_projection_demo import extract_narrative_dna

def enhanced_transform(original_text: str, source_attr: dict, target_dna: dict) -> str:
    """Enhanced transformation with comprehensive DNA-based changes"""
    
    transformed = original_text
    persona = target_dna['persona']
    namespace = target_dna['namespace']
    style = target_dna['style']
    
    # Apply persona transformation
    if persona == 'philosophical_narrator':
        transformed = transformed.replace("Gilgamesh", "the seeker of wisdom, Gilgamesh")
        transformed = transformed.replace("king", "philosopher-king")
        transformed = transformed.replace("was", "existed in a state of being")
        
    elif persona == 'analytical_observer':
        transformed = transformed.replace("Gilgamesh", "Subject Gilgamesh")
        transformed = transformed.replace("oppressed", "demonstrated authoritarian control over")
        transformed = transformed.replace("cried out", "vocalized distress signals")
        
    elif persona == 'dramatic_voice':
        transformed = transformed.replace("Gilgamesh", "mighty Gilgamesh")
        transformed = transformed.replace("oppressed", "tyrannically crushed")
        transformed = transformed.replace("cried out", "screamed in anguish")
        
    elif persona == 'conversational_voice':
        transformed = transformed.replace("Gilgamesh", "this guy Gilgamesh")
        transformed = transformed.replace("two-thirds divine", "mostly divine")
        transformed = transformed.replace("oppressed", "was really tough on")
        
    elif persona == 'authoritative_narrator':
        transformed = transformed.replace("Gilgamesh", "King Gilgamesh")
        transformed = transformed.replace("oppressed", "ruled with absolute authority")
        transformed = transformed.replace("cried out", "petitioned")
        
    elif persona == 'intimate_storyteller':
        transformed = transformed.replace("Gilgamesh", "dear Gilgamesh")
        transformed = transformed.replace("his people", "his beloved people")
        transformed = transformed.replace("oppressed", "burdened")
        
    elif persona == 'poetic_speaker':
        transformed = transformed.replace("Gilgamesh", "golden Gilgamesh")
        transformed = transformed.replace("strength", "mighty sinews")
        transformed = transformed.replace("divine", "blessed by heaven")
        
    elif persona == 'omniscient_voice':
        transformed = transformed.replace("Gilgamesh", "Gilgamesh the Witnessed")
        transformed = transformed.replace("king", "sovereign ruler")
        transformed = transformed.replace("oppressed", "exercised dominion over")
        
    elif persona == 'reflective_narrator':
        transformed = transformed.replace("Gilgamesh", "Gilgamesh, upon reflection,")
        transformed = transformed.replace("was", "had become")
        transformed = transformed.replace("oppressed", "had grown to oppress")
    
    # Apply namespace transformation
    if namespace == 'moral_philosophy':
        transformed = transformed.replace("gods", "moral arbiters")
        transformed = transformed.replace("relief", "ethical justice")
        transformed = transformed.replace("wild man", "natural moral agent")
        
    elif namespace == 'psychological_narrative':
        transformed = transformed.replace("divine", "psychologically complex")
        transformed = transformed.replace("oppressed", "psychologically dominated")
        transformed = transformed.replace("relief", "therapeutic intervention")
        
    elif namespace == 'literary_realism':
        transformed = transformed.replace("gods", "authorities")
        transformed = transformed.replace("divine", "exceptional")
        transformed = transformed.replace("wild man", "untamed individual")
        
    elif namespace == 'social_commentary':
        transformed = transformed.replace("king", "autocratic leader")
        transformed = transformed.replace("people", "citizenry")
        transformed = transformed.replace("oppressed", "systematically marginalized")
        
    elif namespace == 'historical_fiction':
        transformed = transformed.replace("Uruk", "the ancient city of Uruk")
        transformed = transformed.replace("gods", "the pantheon")
        transformed = transformed.replace("divine", "of divine heritage")
    
    # Apply style transformation  
    if style == 'stream_of_consciousness':
        transformed = transformed.replace(". ", "... and then... ")
        transformed = transformed.replace("They", "They... yes, they")
        
    elif style == 'lyrical_prose':
        transformed = transformed.replace("strength", "terrible beauty of strength")
        transformed = transformed.replace("forest", "verdant wilderness")
        transformed = transformed.replace("heard", "hearkened to")
        
    elif style == 'analytical_writing':
        transformed = "Analysis reveals: " + transformed
        transformed = transformed.replace(". ", ". Furthermore, ")
        
    elif style == 'contemplative_style':
        transformed = "In contemplation of this tale: " + transformed
        transformed = transformed.replace("They", "In their wisdom, they")
        
    elif style == 'formal_literary':
        transformed = transformed.replace("man", "gentleman")
        transformed = transformed.replace("heard", "received word of")
        transformed = transformed.replace("created", "brought forth")
    
    return transformed

def gilgamesh_10_projections():
    """Show Gilgamesh projected through 10 different attributes"""
    
    # First page of Gilgamesh (Epic opening)
    gilgamesh_text = """Gilgamesh, king of Uruk, was two-thirds divine and one-third mortal. He oppressed his people with his strength, and they cried out to the gods for relief. The gods heard their pleas and created Enkidu, a wild man of the forest, to challenge the king. When Gilgamesh and Enkidu first met, they fought like wild bulls, shaking the very foundations of Uruk with their battle. But when their strength proved equal, they embraced as brothers, and their friendship became legendary throughout the land."""
    
    print("📜 GILGAMESH THROUGH 10 DIFFERENT NARRATIVE ATTRIBUTES")
    print("=" * 80)
    
    print("📖 ORIGINAL TEXT:")
    print("-" * 50)
    print(gilgamesh_text)
    print()
    
    # Check if we have generated attributes
    test_dir = Path("test_attributes")
    if test_dir.exists():
        attr_files = list(test_dir.glob("*.json"))
    else:
        print("⚠️  No generated attributes found. Running minimal harvest first...")
        # Run minimal harvest to generate test attributes
        import subprocess
        subprocess.run([sys.executable, "minimal_harvester_test.py"], check=True)
        attr_files = list(Path("test_attributes").glob("*.json"))
    
    if len(attr_files) < 10:
        print(f"⚠️  Only {len(attr_files)} attributes found. Generating more...")
        # Generate additional mock attributes for demonstration
        attr_files = generate_mock_attributes_for_demo()
    
    print("🧬 PROJECTIONS THROUGH DIFFERENT NARRATIVE DNA:")
    print("=" * 80)
    
    # Select 10 diverse attributes
    selected_files = attr_files[:10] if len(attr_files) >= 10 else attr_files
    
    for i, file_path in enumerate(selected_files, 1):
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Get the attribute
            attr = data['attributes'][0] if data['attributes'] else None
            if not attr:
                continue
                
            dna = extract_narrative_dna(attr)
            
            # Transform Gilgamesh text
            projected = enhanced_transform(gilgamesh_text, attr, dna)
            
            print(f"\n{i}. PROJECTION #{i}")
            print("=" * 60)
            print(f"📚 SOURCE ATTRIBUTE METADATA:")
            print(f"   File: {file_path.name}")
            print(f"   Book ID: {data.get('book_id', 'Unknown')}")
            print(f"   Extraction Time: {data.get('extraction_timestamp', 'Unknown')}")
            print(f"   Attribute ID: {attr.get('id', 'Unknown')}")
            print(f"   Paragraph Index: {attr.get('paragraph_index', 'Unknown')}")
            print(f"   Word Count: {attr.get('word_count', 'Unknown')}")
            print(f"   Content Hash: {attr.get('anchor', {}).get('content_hash', 'Unknown')[:16]}...")
            print()
            print(f"🧬 NARRATIVE DNA:")
            print(f"   Persona: {dna['persona']}")
            print(f"   Namespace: {dna['namespace']}")
            print(f"   Style: {dna['style']}")
            print(f"   Confidence: {dna['confidence']}")
            print()
            print(f"📖 SOURCE TEXT SAMPLE:")
            print(f"   {attr.get('text_sample', 'No sample available')[:100]}...")
            print()
            print(f"🔄 GILGAMESH PROJECTION:")
            print("-" * 40)
            print(projected)
            print()
            
        except Exception as e:
            print(f"❌ Error processing {file_path.name}: {e}")
            continue
    
    print("=" * 80)
    print("🎯 ANALYSIS COMPLETE")
    print(f"Showed Gilgamesh projected through {len(selected_files)} different narrative DNA patterns")
    print("Each projection demonstrates unique voice, context, and style transformations")
    print("while preserving the core narrative essence of the epic.")

def generate_mock_attributes_for_demo():
    """Generate additional mock attributes for demonstration"""
    import hashlib
    import time
    
    # Generate 10 mock attribute files with diverse DNA
    test_books = ["demo1", "demo2", "demo3", "demo4", "demo5", "demo6", "demo7", "demo8", "demo9", "demo10"]
    
    demo_texts = [
        "The ancient scrolls speak of wisdom beyond mortal comprehension, written in languages lost to time.",
        "Detective Morrison examined the evidence with methodical precision, noting every detail.",
        "In the bustling metropolis, concrete towers reached toward an indifferent sky while shadows pooled below.",
        "Consider, dear reader, the fundamental nature of existence and our place within the cosmic order.",
        "The ship's captain steered through treacherous waters, his crew depending on his steady hand.",
        "She reflected quietly on the meaning of home, watching autumn leaves dance in the morning light.",
        "Warriors of old sang battle hymns that echoed across mountain peaks and valley floors.",
        "The laboratory results indicated anomalous readings that defied conventional scientific explanation.",
        "Children played in meadows where wildflowers bloomed in abundance, their laughter carried by gentle breezes.",
        "Throughout history, great leaders have faced moments that tested the very core of their character."
    ]
    
    output_dir = Path("test_attributes")
    output_dir.mkdir(exist_ok=True)
    
    personas = ["philosophical_narrator", "analytical_observer", "dramatic_voice", "conversational_voice", 
               "authoritative_narrator", "intimate_storyteller", "poetic_speaker", "omniscient_voice", 
               "reflective_narrator", "dramatic_voice"]
    
    namespaces = ["moral_philosophy", "psychological_narrative", "literary_realism", "social_commentary",
                 "historical_fiction", "pastoral_literature", "urban_narrative", "philosophical_discourse",
                 "romantic_literature", "classical_literature"]
    
    styles = ["contemplative_style", "analytical_writing", "stream_of_consciousness", "formal_literary",
             "lyrical_prose", "descriptive_prose", "dialogue_heavy", "dramatic_narrative",
             "colloquial_narrative", "epic_verse"]
    
    files = []
    for i, (book_id, text) in enumerate(zip(test_books, demo_texts)):
        
        # Create diverse DNA
        dna = {
            'persona': personas[i],
            'namespace': namespaces[i],
            'style': styles[i],
            'confidence': round(0.75 + (i * 0.02), 2)
        }
        
        # Create attribute
        attr = {
            'id': f"{book_id}_0",
            'source_book': book_id,
            'paragraph_index': i * 10,
            'text_sample': text,
            'word_count': len(text.split()),
            'narrative_dna': dna,
            'anchor': {
                'canonical_offsets': {'start': 0, 'end': len(text)},
                'content_hash': hashlib.md5(text.encode()).hexdigest()
            }
        }
        
        # Create file data
        file_data = {
            'book_id': book_id,
            'extraction_timestamp': time.strftime('%Y-%m-%dT%H:%M:%S'),
            'total_paragraphs': 1,
            'attributes': [attr]
        }
        
        # Save file
        file_path = output_dir / f"attributes_{book_id}.json"
        with open(file_path, 'w') as f:
            json.dump(file_data, f, indent=2)
        
        files.append(file_path)
    
    return files

if __name__ == "__main__":
    import sys
    gilgamesh_10_projections()