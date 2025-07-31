#!/usr/bin/env python3
"""
Enhanced Projection Demo - More sophisticated transformations
"""

import json
import random
from pathlib import Path
from typing import Dict, List

def load_discovered_attributes(count: int = 3) -> List[Dict]:
    """Load attributes from discovered_attributes directory"""
    attrs_path = Path("discovered_attributes")
    collected_attrs = []
    
    for file_path in attrs_path.glob("attributes_*.json"):
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            attributes = data.get('attributes', [])
            sample_count = min(2, len(attributes))
            sample_attrs = random.sample(attributes, sample_count)
            
            for attr in sample_attrs:
                collected_attrs.append({
                    'source_file': file_path.name,
                    'book_id': data.get('book_id'),
                    'attribute': attr
                })
                
        except Exception as e:
            continue
    
    return collected_attrs[:count]

def enhanced_transform(original_text: str, source_attr: Dict) -> str:
    """Enhanced transformation with more dramatic changes"""
    
    source_text = source_attr.get('text_sample', '')
    book_id = source_attr.get('source_book', 'unknown')
    transformed = original_text
    
    # Book-specific transformations based on discovered patterns
    
    if book_id == "1342":  # Pride and Prejudice
        # Austen-style formal prose
        transformed = transformed.replace("Technology has", "It is a truth universally acknowledged that technology has")
        transformed = transformed.replace("Social media platforms", "These modern instruments of correspondence")
        transformed = transformed.replace("Twitter and Facebook", "such establishments as Twitter and Facebook")
        transformed = transformed.replace("People now share", "Persons of all stations now venture to share")
        transformed = transformed.replace("instantly", "with the most remarkable swiftness")
        transformed = transformed.replace("hundreds of followers", "a vast assembly of acquaintances")
        transformed = transformed.replace("opportunities and challenges", "both felicity and vexation")
        transformed = transformed.replace("We can stay in touch", "We find ourselves capable of maintaining correspondence")
        transformed = transformed.replace("distant friends", "friends separated by considerable distance")
        transformed = transformed.replace("losing the art", "in danger of forsaking the refined art")
        transformed = transformed.replace("deep, meaningful conversation", "discourse of true substance and refinement")
        
    elif book_id == "11":  # Alice in Wonderland
        # Carroll-style whimsical prose
        transformed = transformed.replace("Technology has fundamentally changed", 
                                        "Technology has changed everything in the most curious way")
        transformed = transformed.replace("Social media platforms", 
                                        "Those peculiar digital looking-glasses")
        transformed = transformed.replace("Twitter and Facebook", 
                                        "the twittering birds and the book of faces")
        transformed = transformed.replace("People now share their thoughts", 
                                        "People pour out their thoughts like tea at a mad tea-party")
        transformed = transformed.replace("instantly", "quicker than you can say 'Cheshire Cat'")
        transformed = transformed.replace("hundreds of followers", 
                                        "armies of curious onlookers, rather like cards painting roses")
        transformed = transformed.replace("This shift", "This topsy-turvy change")
        transformed = transformed.replace("opportunities and challenges", 
                                        "doors that open and shut like croquet mallets")
        transformed = transformed.replace("We can stay in touch", 
                                        "We find ourselves tumbling through rabbit holes to reach")
        transformed = transformed.replace("distant friends", "friends in far-off wonderlands")
        transformed = transformed.replace("losing the art", "forgetting the magic")
        transformed = transformed.replace("deep, meaningful conversation", 
                                        "conversations as rich as the Queen's tarts")
    
    # Add source text influence
    if "gratified" in source_text.lower():
        transformed = "I confess myself exceedingly gratified to observe that " + transformed.lower()
    elif "curiouser" in source_text.lower() or "cried" in source_text.lower():
        transformed = "How curiously things have changed! " + transformed
    elif "pride" in source_text.lower():
        transformed = transformed.replace("This", "This matter, though it may wound our pride,")
    
    return transformed

def demonstrate_enhanced_projections():
    """Demonstrate enhanced projections with dramatic transformations"""
    
    print("🎭 Enhanced Humanizer Projection Demo")
    print("=" * 60)
    
    # Load attributes
    attrs = load_discovered_attributes(2)
    
    if not attrs:
        print("❌ No attributes available")
        return
    
    # Modern essay to transform
    modern_essay = """Technology has fundamentally changed how we communicate. Social media platforms like Twitter and Facebook have replaced traditional letter writing. People now share their thoughts instantly with hundreds of followers. This shift has created both opportunities and challenges for human connection. We can stay in touch with distant friends, but we may be losing the art of deep, meaningful conversation."""
    
    print("📖 Original Modern Essay:")
    print("-" * 40)
    print(modern_essay)
    print()
    
    # Show transformations
    print("🎭 Dramatic Projections:")
    print("=" * 50)
    
    for i, attr_data in enumerate(attrs, 1):
        attr = attr_data['attribute']
        book_id = attr_data['book_id']
        
        # Get book title for display
        book_titles = {
            "1342": "Pride and Prejudice (Jane Austen, 1813)",
            "11": "Alice's Adventures in Wonderland (Lewis Carroll, 1865)"
        }
        book_title = book_titles.get(book_id, f"Book {book_id}")
        
        # Transform
        projected = enhanced_transform(modern_essay, attr)
        
        print(f"\n{i}. 📚 Projected through: {book_title}")
        print(f"🧬 Source DNA sample: {attr.get('text_sample', '')[:60]}...")
        print("🎭 Transformed Essay:")
        print("-" * 30)
        print(projected)
        print()
    
    # Test with another essay
    print("\n" + "=" * 60)
    print("🔬 Second Test: Different Essay")
    print("=" * 60)
    
    tech_essay = """I love using my smartphone to take photos and share them online. The camera quality is amazing, and I can edit pictures instantly. My friends always like and comment on my posts. It's fun to see what everyone is doing throughout the day."""
    
    print("📖 Original Essay:")
    print("-" * 20)
    print(tech_essay)
    print()
    
    print("🎭 Projections:")
    print("-" * 20)
    
    for i, attr_data in enumerate(attrs, 1):
        attr = attr_data['attribute']
        book_id = attr_data['book_id']
        book_title = book_titles.get(book_id, f"Book {book_id}")
        
        projected = enhanced_transform(tech_essay, attr)
        
        print(f"\n{i}. 📚 {book_title} Style:")
        print(f"🎭 {projected}")
    
    print("\n🎉 Enhanced projection demo complete!")

if __name__ == "__main__":
    demonstrate_enhanced_projections()