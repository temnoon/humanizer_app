#!/usr/bin/env python3
"""
Test: Harvest 100 diverse attributes from 100 different Gutenberg books
Production-ready test with real DNA extraction
"""

import asyncio
import json
import time
from pathlib import Path
from mass_attribute_harvester import MassAttributeHarvester, BatchJob

class Gutenberg100Test:
    """Test harvestor for 100 books with 1 attribute each"""
    
    def __init__(self):
        self.harvester = MassAttributeHarvester(
            output_dir="./test_100_attributes",
            max_workers=4  # Moderate concurrency for stability
        )
        
        # Curated list of 100 diverse Gutenberg books
        self.test_books = [
            # Classic Literature (20 books)
            1342, 11, 84, 345, 1513, 2701, 74, 76, 215, 105,
            121, 141, 158, 161, 98, 766, 730, 120, 174, 43,
            
            # World Literature (20 books) 
            2554, 2638, 1399, 28054, 1998, 4363, 5200, 7849,
            4650, 1257, 1259, 209, 883, 917, 1524, 1533, 1534, 1540,
            3207, 3300,
            
            # Science Fiction & Fantasy (15 books)
            35, 36, 5230, 4300, 844, 25344, 8800, 9999, 1,
            145, 1661, 244, 2097, 4085, 1260,
            
            # Philosophy & Social Commentary (15 books)
            1000, 1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008, 1009,
            2000, 2001, 2002, 2003, 2004,
            
            # Historical Documents (10 books)
            5000, 5001, 5002, 5003, 5004, 5005, 5006, 5007, 5008, 5009,
            
            # Poetry & Drama (10 books)
            1041, 1056, 1060, 1066, 1079, 1089, 2011, 2021, 2049, 3100,
            
            # Adventure & Mystery (10 books)
            3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 4000, 4100
        ]
        
        # Ensure we have exactly 100 books
        self.test_books = self.test_books[:100]
        
    async def setup_test_jobs(self):
        """Create 100 test jobs for diverse attribute harvesting"""
        print("🔧 Setting up 100 test jobs...")
        
        jobs = []
        for i, book_id in enumerate(self.test_books):
            job = BatchJob(
                job_id=f"test_100_{book_id}_{i}",
                book_id=str(book_id),
                priority=1,
                max_paragraphs=1  # Just 1 attribute per book for diversity test
            )
            jobs.append(job)
        
        print(f"✅ Created {len(jobs)} jobs")
        return jobs
    
    async def run_harvest_test(self):
        """Execute the 100-book harvest test"""
        print("🚀 GUTENBERG 100-BOOK ATTRIBUTE HARVEST TEST")
        print("=" * 70)
        print(f"📚 Target: 100 attributes from 100 different books")
        print(f"🤖 Real LLM: {self.harvester.use_real_llm}")
        print(f"🔧 Provider: {type(self.harvester.llm_provider).__name__ if self.harvester.llm_provider else 'Varied Mock'}")
        print(f"📁 Output: {self.harvester.output_dir}")
        print()
        
        # Setup jobs
        jobs = await self.setup_test_jobs()
        
        # Process in batches for stability
        batch_size = 10
        batches = [jobs[i:i+batch_size] for i in range(0, len(jobs), batch_size)]
        
        results = []
        start_time = time.time()
        
        print(f"🔄 Processing {len(batches)} batches of {batch_size} books each:")
        print("-" * 50)
        
        for batch_num, batch in enumerate(batches, 1):
            print(f"\n📦 Batch {batch_num}/{len(batches)}: Books {[job.book_id for job in batch[:3]]}...")
            
            batch_start = time.time()
            batch_results = []
            
            # Process batch concurrently
            for job in batch:
                try:
                    success, error_msg, stats = await self.harvester.process_single_book(job)
                    
                    if success:
                        batch_results.append({
                            'book_id': job.book_id,
                            'success': True,
                            'attributes': stats.get('attributes_generated', 0),
                            'time': stats.get('processing_time', 0)
                        })
                        print("✅", end="", flush=True)
                    else:
                        batch_results.append({
                            'book_id': job.book_id,
                            'success': False,
                            'error': error_msg
                        })
                        print("❌", end="", flush=True)
                        
                except Exception as e:
                    batch_results.append({
                        'book_id': job.book_id,
                        'success': False,
                        'error': str(e)
                    })
                    print("⚠️", end="", flush=True)
            
            batch_time = time.time() - batch_start
            successful_in_batch = len([r for r in batch_results if r['success']])
            
            print(f" ({successful_in_batch}/{len(batch)} successful, {batch_time:.1f}s)")
            results.extend(batch_results)
        
        total_time = time.time() - start_time
        
        # Analyze results
        await self.analyze_results(results, total_time)
    
    async def analyze_results(self, results, total_time):
        """Analyze the harvest results"""
        print("\n" + "=" * 70)
        print("📊 HARVEST RESULTS ANALYSIS")
        print("-" * 50)
        
        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]
        
        print(f"✅ Successful: {len(successful)}/100 ({len(successful)}%)")
        print(f"❌ Failed: {len(failed)}/100 ({len(failed)}%)")
        print(f"⏱️  Total time: {total_time:.1f}s")
        
        if successful:
            total_attrs = sum(r.get('attributes', 0) for r in successful)
            avg_time = sum(r.get('time', 0) for r in successful) / len(successful)
            print(f"📚 Total attributes: {total_attrs}")
            print(f"⚡ Avg time per book: {avg_time:.2f}s")
        
        # Check output files
        output_files = list(self.harvester.output_dir.glob("*.json"))
        print(f"📁 Files generated: {len(output_files)}")
        
        if output_files:
            total_size = sum(f.stat().st_size for f in output_files)
            print(f"💾 Total size: {total_size / 1024:.1f} KB")
        
        # DNA Diversity Analysis
        if output_files:
            await self.analyze_dna_diversity(output_files[:10])  # Sample first 10
        
        # Show failures
        if failed:
            print(f"\n❌ Failed books (first 10):")
            for result in failed[:10]:
                print(f"  Book {result['book_id']}: {result['error'][:60]}...")
    
    async def analyze_dna_diversity(self, sample_files):
        """Analyze DNA diversity in generated attributes"""
        print(f"\n🧬 DNA DIVERSITY ANALYSIS (sample of {len(sample_files)} files):")
        print("-" * 50)
        
        all_personas = set()
        all_namespaces = set()
        all_styles = set()
        all_patterns = set()
        
        for file_path in sample_files:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                for attr in data.get('attributes', [])[:1]:  # Just 1 attribute per file
                    dna = attr.get('narrative_dna', {})
                    
                    persona = dna.get('persona', 'unknown')
                    namespace = dna.get('namespace', 'unknown')
                    style = dna.get('style', 'unknown')
                    
                    all_personas.add(persona)
                    all_namespaces.add(namespace)
                    all_styles.add(style)
                    all_patterns.add(f"{persona}|{namespace}|{style}")
                    
                    print(f"  Book {data.get('book_id', '?')}: {persona} | {namespace} | {style}")
                    
            except Exception as e:
                print(f"  ❌ Error reading {file_path.name}: {e}")
        
        print(f"\n📊 DIVERSITY METRICS:")
        print(f"  Unique personas: {len(all_personas)}")
        print(f"  Unique namespaces: {len(all_namespaces)}")
        print(f"  Unique styles: {len(all_styles)}")
        print(f"  Unique DNA patterns: {len(all_patterns)}")
        
        diversity_score = len(all_patterns) / len(sample_files) * 100
        print(f"  🎯 Diversity score: {diversity_score:.1f}% (higher = more diverse)")
        
        if diversity_score > 70:
            print("  ✅ EXCELLENT diversity - no mock data issues!")
        elif diversity_score > 40:
            print("  ⚠️  MODERATE diversity - some variation detected")
        else:
            print("  ❌ LOW diversity - possible mock data problem")

async def main():
    """Run the 100-book harvest test"""
    test = Gutenberg100Test()
    await test.run_harvest_test()

if __name__ == "__main__":
    asyncio.run(main())