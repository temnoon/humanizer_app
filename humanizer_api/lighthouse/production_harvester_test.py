#!/usr/bin/env python3
"""
Production Attribute Harvester Test
Test the production-ready harvester with real LLM analysis (no mock data)
"""

import asyncio
import sys
from pathlib import Path
from mass_attribute_harvester import MassAttributeHarvester, BatchJob

async def test_production_harvester():
    """Test the production harvester on a small set of books"""
    print("🚀 Testing Production-Ready Attribute Harvester")
    print("=" * 60)
    
    # Initialize harvester
    harvester = MassAttributeHarvester()
    
    print(f"📁 Output directory: {harvester.output_dir}")
    print(f"🤖 Real LLM available: {harvester.use_real_llm}")
    print(f"🔧 LLM provider: {type(harvester.llm_provider).__name__ if harvester.llm_provider else 'None'}")
    print()
    
    # Test on a few classic books
    test_books = [
        "1342",  # Pride and Prejudice
        "11",    # Alice in Wonderland  
        "84"     # Frankenstein
    ]
    
    print(f"📚 Testing on {len(test_books)} classic books:")
    for book_id in test_books:
        print(f"  - Book {book_id}")
    print()
    
    # Create test jobs
    jobs = []
    for i, book_id in enumerate(test_books):
        job = BatchJob(
            job_id=f"prod_test_{book_id}",
            book_id=book_id,
            priority=1,
            max_paragraphs=20  # Small sample for testing
        )
        jobs.append(job)
    
    # Process each book
    results = []
    for job in jobs:
        print(f"🔄 Processing Book {job.book_id}...")
        
        try:
            success, error_msg, stats = await harvester.process_single_book(job)
            
            if success:
                print(f"  ✅ Success: {stats.get('attributes_generated', 0)} attributes")
                results.append({
                    'book_id': job.book_id,
                    'success': True,
                    'attributes': stats.get('attributes_generated', 0),
                    'processing_time': stats.get('processing_time', 0)
                })
            else:
                print(f"  ❌ Failed: {error_msg}")
                results.append({
                    'book_id': job.book_id,
                    'success': False,
                    'error': error_msg
                })
                
        except Exception as e:
            print(f"  ❌ Exception: {e}")
            results.append({
                'book_id': job.book_id,
                'success': False,
                'error': str(e)
            })
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 PRODUCTION TEST RESULTS:")
    print("-" * 40)
    
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    print(f"✅ Successful: {len(successful)}/{len(results)}")
    print(f"❌ Failed: {len(failed)}/{len(results)}")
    
    if successful:
        total_attrs = sum(r['attributes'] for r in successful)
        avg_time = sum(r['processing_time'] for r in successful) / len(successful)
        print(f"📚 Total attributes generated: {total_attrs}")
        print(f"⏱️  Average processing time: {avg_time:.1f}s")
    
    if failed:
        print(f"\n❌ Failed books:")
        for result in failed:
            print(f"  - Book {result['book_id']}: {result['error']}")
    
    # Check output
    output_files = list(harvester.output_dir.glob("*.json"))
    print(f"\n📁 Output files generated: {len(output_files)}")
    for file_path in output_files:
        size_kb = file_path.stat().st_size // 1024
        print(f"  - {file_path.name} ({size_kb}KB)")

async def verify_no_mock_data():
    """Verify the generated attributes contain real DNA diversity"""
    print("\n🔍 VERIFYING NO MOCK DATA:")
    print("-" * 40)
    
    # Check if any files were generated
    output_dir = Path("mass_attributes")
    if not output_dir.exists():
        print("❌ No output directory found")
        return
    
    attr_files = list(output_dir.glob("attributes_*.json"))
    if not attr_files:
        print("❌ No attribute files generated")
        return
    
    print(f"📚 Found {len(attr_files)} attribute files")
    
    # Check DNA diversity in generated files
    import json
    all_dna_patterns = set()
    
    for file_path in attr_files[:3]:  # Check first 3 files
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            print(f"\n📖 {file_path.name} (Book {data.get('book_id')}):")
            
            # Check DNA patterns
            file_patterns = set()
            for attr in data.get('attributes', [])[:5]:  # Check first 5 attributes
                dna = attr.get('narrative_dna', {})
                pattern = f"{dna.get('persona')}|{dna.get('namespace')}|{dna.get('style')}"
                file_patterns.add(pattern)
                all_dna_patterns.add(pattern)
                
                print(f"  - {dna.get('persona')} | {dna.get('namespace')} | {dna.get('style')}")
            
            print(f"  📊 Unique patterns in file: {len(file_patterns)}")
            
        except Exception as e:
            print(f"  ❌ Error reading {file_path.name}: {e}")
    
    print(f"\n📊 DIVERSITY ANALYSIS:")
    print(f"  Total unique DNA patterns: {len(all_dna_patterns)}")
    
    if len(all_dna_patterns) > 1:
        print("  ✅ REAL DIVERSITY DETECTED - No identical mock data!")
    else:
        print("  ❌ WARNING: All patterns identical - possible mock data issue")

if __name__ == "__main__":
    asyncio.run(test_production_harvester())
    asyncio.run(verify_no_mock_data())