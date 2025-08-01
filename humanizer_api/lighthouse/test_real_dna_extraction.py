#!/usr/bin/env python3
"""
Test real DNA extraction vs mock data
"""

import json
import asyncio
from pathlib import Path
from mass_attribute_harvester import MassAttributeHarvester

async def test_dna_extraction():
    print("🧬 Testing Real DNA Extraction vs Mock Data")
    print("=" * 60)
    
    # Initialize harvester
    harvester = MassAttributeHarvester()
    
    # Test sample texts from different genres
    test_texts = [
        "In a hole in the ground there lived a hobbit. Not a nasty, dirty, wet hole, filled with the ends of worms and an oozy smell, nor yet a dry, bare, sandy hole with nothing in it to sit down on or to eat: it was a hobbit-hole, and that means comfort.",
        
        "Call me Ishmael. Some years ago—never mind how long precisely—having little or no money in my purse, and nothing particular to interest me on shore, I thought I would sail about a little and see the watery part of the world.",
        
        "It was the best of times, it was the worst of times, it was the age of wisdom, it was the age of foolishness, it was the epoch of belief, it was the epoch of incredulity, it was the season of Light, it was the season of Darkness."
    ]
    
    print("📖 Testing DNA extraction on sample texts:")
    print("-" * 40)
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n{i}. Text sample:")
        print(f"   {text[:80]}...")
        
        # Extract DNA
        dna = await harvester._extract_real_dna_for_paragraph(text)
        
        print(f"   🧬 DNA: {dna['persona']} | {dna['namespace']} | {dna['style']}")
        print(f"   📊 Confidence: {dna['confidence']}")
    
    print("\n" + "=" * 60)
    print("✅ DNA extraction test complete!")
    
    # Show if using real LLM or varied mock
    if harvester.use_real_llm:
        print("🤖 Using REAL LLM analysis")
    else:
        print("🎭 Using VARIED mock data (not identical anymore)")

async def regenerate_sample_attributes():
    """Regenerate a few attribute files with new DNA system"""
    print("\n🔄 Regenerating sample attributes with new DNA system...")
    
    # Load existing attribute file to get text samples
    sample_file = Path("mass_attributes/attributes_1000.json")
    if not sample_file.exists():
        print("❌ Sample attribute file not found")
        return
    
    with open(sample_file, 'r') as f:
        data = json.load(f)
    
    harvester = MassAttributeHarvester()
    
    # Regenerate DNA for first 3 attributes
    print(f"📚 Regenerating DNA for first 3 attributes from Book {data['book_id']}:")
    
    for i, attr in enumerate(data['attributes'][:3]):
        old_dna = attr['narrative_dna']
        text_sample = attr['text_sample']
        
        # Generate new DNA
        new_dna = await harvester._extract_real_dna_for_paragraph(text_sample)
        
        print(f"\n  Attribute {i+1}:")
        print(f"    Text: {text_sample[:60]}...")
        print(f"    OLD DNA: {old_dna['persona']} | {old_dna['namespace']} | {old_dna['style']}")
        print(f"    NEW DNA: {new_dna['persona']} | {new_dna['namespace']} | {new_dna['style']}")
        print(f"    Confidence: {old_dna['confidence']} → {new_dna['confidence']}")

if __name__ == "__main__":
    asyncio.run(test_dna_extraction())
    asyncio.run(regenerate_sample_attributes())