#!/usr/bin/env python3
"""
Test projection with your narrative
"""

from simple_projection_demo import load_sample_attributes, simple_transform, extract_narrative_dna

def test_your_narrative():
    # Your narrative
    narrative = """I was tired, cold, scared ... there was water leaking into the basement, 
water already up to my ankles. My phone was below 10% power, and no one was answering. 
What was the number? My dad gave me his new number, but I hadn't called it."""
    
    print("🧬 Testing Narrative Projection")
    print("=" * 60)
    print(f"📖 Original narrative:")
    print(f"   {narrative}")
    print()
    
    # Load 3 random attributes  
    attrs = load_sample_attributes(count=3)
    if not attrs:
        print("❌ No attributes loaded")
        return
        
    print(f"🔄 Projecting through {len(attrs)} different attributes:")
    print("=" * 60)
    
    for i, attr_data in enumerate(attrs, 1):
        attr = attr_data['attribute']
        dna = extract_narrative_dna(attr)
        
        # Show source attribute sample
        source_sample = attr.get('text_sample', '')[:100] + "..."
        
        # Transform using this attribute
        projected = simple_transform(narrative, attr, dna)
        
        print(f"\n{i}. 🧬 DNA: {dna['persona']} | {dna['namespace']} | {dna['style']}")
        print(f"   📚 Source: Book {attr_data['book_id']} - {source_sample}")
        print(f"   📊 Confidence: {dna['confidence']:.2f}")
        print(f"   🔄 Projected:")
        print(f"      {projected}")
        print()

if __name__ == "__main__":
    test_your_narrative()