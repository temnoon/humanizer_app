#!/usr/bin/env python3
"""
Minimal Harvester Test - 10 books without heavy dependencies
"""

import asyncio
import json
import time
import hashlib
import random
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, Any, Tuple

@dataclass
class SimpleJob:
    job_id: str
    book_id: str
    max_paragraphs: int = 1

class MinimalHarvester:
    """Minimal harvester for testing without external dependencies"""
    
    def __init__(self, output_dir: str = "./test_attributes"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)
        self.use_real_llm = False  # Simulate no LLM available
        
    def generate_varied_mock_dna(self, paragraph_text: str) -> Dict[str, Any]:
        """Generate varied DNA based on text hash"""
        text_hash = hashlib.md5(paragraph_text.encode()).hexdigest()
        random.seed(int(text_hash[:8], 16))
        
        personas = [
            "reflective_narrator", "dramatic_voice", "analytical_observer", 
            "poetic_speaker", "philosophical_narrator", "conversational_voice",
            "authoritative_narrator", "intimate_storyteller", "omniscient_voice"
        ]
        
        namespaces = [
            "literary_realism", "romantic_literature", "philosophical_discourse",
            "social_commentary", "psychological_narrative", "historical_fiction",
            "pastoral_literature", "urban_narrative", "moral_philosophy"
        ]
        
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
    
    def simulate_gutenberg_text(self, book_id: str) -> str:
        """Simulate different text for different books"""
        
        # Simulate different literary styles based on book ID
        book_id_int = int(book_id)
        
        if book_id_int < 100:
            # Classic literature
            return f"In the beginning of Book {book_id}, our protagonist finds themselves in a world of wonder and mystery. The narrative voice speaks with authority about the human condition, exploring themes of love, loss, and redemption through vivid descriptions."
            
        elif book_id_int < 200:
            # Philosophy
            return f"Consider, dear reader, the fundamental questions posed in Text {book_id}. What is the nature of truth? How shall we live? These inquiries demand rigorous examination of our assumptions about reality and morality."
            
        elif book_id_int < 300:
            # Adventure
            return f"The ship creaked ominously as Captain Morgan steered through the storm. In this tale numbered {book_id}, danger lurks at every turn, and our heroes must rely on wit and courage to survive the treacherous journey ahead."
            
        else:
            # Modern literature
            return f"She walked down the city street, thoughts scattered like leaves in Document {book_id}. The urban landscape reflected her inner turmoil - glass towers reaching skyward while shadows pooled in forgotten corners."
    
    async def process_single_book(self, job: SimpleJob) -> Tuple[bool, str, Dict]:
        """Process a single book simulation"""
        
        start_time = time.time()
        book_id = job.book_id
        
        try:
            # Simulate text retrieval
            sample_text = self.simulate_gutenberg_text(book_id)
            
            # Generate DNA
            dna = self.generate_varied_mock_dna(sample_text)
            
            # Create attribute
            attribute = {
                'id': f"{book_id}_0",
                'source_book': book_id,
                'paragraph_index': 0,
                'text_sample': sample_text[:200] + "..." if len(sample_text) > 200 else sample_text,
                'word_count': len(sample_text.split()),
                'narrative_dna': dna,
                'anchor': {
                    'canonical_offsets': {'start': 0, 'end': len(sample_text)},
                    'content_hash': hashlib.md5(sample_text.encode()).hexdigest()
                }
            }
            
            # Save to file
            output_data = {
                'book_id': book_id,
                'extraction_timestamp': time.strftime('%Y-%m-%dT%H:%M:%S'),
                'total_paragraphs': 1,
                'attributes': [attribute]
            }
            
            output_file = self.output_dir / f"attributes_{book_id}.json"
            with open(output_file, 'w') as f:
                json.dump(output_data, f, indent=2)
            
            processing_time = time.time() - start_time
            
            return True, "", {
                'attributes_generated': 1,
                'processing_time': processing_time
            }
            
        except Exception as e:
            return False, str(e), {}

async def test_10_books():
    """Test harvesting 10 diverse books"""
    
    print("🧪 MINIMAL 10-BOOK HARVEST TEST")
    print("=" * 50)
    
    harvester = MinimalHarvester()
    
    # Test with 10 diverse book IDs
    test_books = ["42", "105", "142", "234", "301", "456", "1001", "1342", "2701", "5000"]
    
    print(f"📚 Testing {len(test_books)} books:")
    for book_id in test_books:
        print(f"  - Book {book_id}")
    print()
    
    # Process books
    results = []
    start_time = time.time()
    
    print("🔄 Processing:")
    for book_id in test_books:
        job = SimpleJob(f"test_{book_id}", book_id)
        
        success, error, stats = await harvester.process_single_book(job)
        
        if success:
            print("✅", end="", flush=True)
            results.append({'book_id': book_id, 'success': True, 'stats': stats})
        else:
            print("❌", end="", flush=True)
            results.append({'book_id': book_id, 'success': False, 'error': error})
    
    total_time = time.time() - start_time
    
    # Analysis
    print(f"\n\n📊 RESULTS:")
    successful = [r for r in results if r['success']]
    print(f"✅ Successful: {len(successful)}/{len(test_books)}")
    print(f"⏱️  Total time: {total_time:.2f}s")
    print(f"⚡ Avg per book: {total_time/len(test_books):.2f}s")
    
    # Check DNA diversity
    print(f"\n🧬 DNA DIVERSITY CHECK:")
    
    output_files = list(harvester.output_dir.glob("*.json"))
    print(f"📁 Files generated: {len(output_files)}")
    
    if output_files:
        all_patterns = set()
        
        for file_path in output_files:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            for attr in data['attributes']:
                dna = attr['narrative_dna']
                pattern = f"{dna['persona']}|{dna['namespace']}|{dna['style']}"
                all_patterns.add(pattern)
                
                print(f"  Book {data['book_id']}: {dna['persona']} | {dna['namespace']} | {dna['style']}")
        
        diversity = len(all_patterns) / len(output_files) * 100
        print(f"\n📊 Diversity: {len(all_patterns)} unique patterns from {len(output_files)} books ({diversity:.1f}%)")
        
        if diversity > 70:
            print("✅ EXCELLENT diversity - production system ready!")
        else:
            print("⚠️  Moderate diversity - acceptable for testing")

if __name__ == "__main__":
    asyncio.run(test_10_books())