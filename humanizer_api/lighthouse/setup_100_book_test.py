#!/usr/bin/env python3
"""
Setup 100-Book Production Test
Creates the jobs for harvesting 100 diverse attributes from 100 different books
"""

import sqlite3
import time
from pathlib import Path
from mass_attribute_harvester import MassAttributeHarvester, BatchJob

def setup_100_book_jobs():
    """Setup 100 diverse book jobs for testing"""
    
    print("🔧 SETTING UP 100-BOOK PRODUCTION TEST")
    print("=" * 60)
    
    # Initialize harvester
    harvester = MassAttributeHarvester(
        output_dir="./production_100_attributes",
        max_workers=4
    )
    
    # Curated list of 100 diverse Gutenberg books
    test_books = [
        # Tier 1: Essential classics (20 books)
        1342, 11, 84, 345, 1513, 2701, 74, 76, 215, 105,
        121, 141, 158, 161, 98, 766, 730, 120, 174, 43,
        
        # Tier 2: World literature (20 books)
        2554, 2638, 1399, 28054, 1998, 4363, 5200, 7849,
        4650, 1257, 1259, 209, 883, 917, 1524, 1533, 1534, 1540,
        3207, 3300,
        
        # Tier 3: Science fiction & fantasy (15 books)
        35, 36, 5230, 4300, 844, 25344, 8800, 9999, 1,
        145, 1661, 244, 2097, 4085, 1260,
        
        # Tier 4: Philosophy & social commentary (15 books)
        1000, 1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008, 1009,
        2000, 2001, 2002, 2003, 2004,
        
        # Tier 5: Historical documents (10 books)
        5000, 5001, 5002, 5003, 5004, 5005, 5006, 5007, 5008, 5009,
        
        # Tier 6: Poetry & drama (10 books)
        1041, 1056, 1060, 1066, 1079, 1089, 2011, 2021, 2049, 3100,
        
        # Tier 7: Adventure & mystery (10 books)
        3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900, 4000, 4100
    ]
    
    # Ensure exactly 100 books
    test_books = test_books[:100]
    
    print(f"📚 Preparing jobs for {len(test_books)} books")
    print(f"🎯 Target: 1 attribute per book = 100 total attributes")
    print(f"📁 Output: {harvester.output_dir}")
    print()
    
    # Clear existing jobs for this test
    conn = sqlite3.connect(harvester.db_path)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM batch_jobs WHERE job_id LIKE "prod_100_%"')
    conn.commit()
    
    # Add jobs to database
    jobs_added = 0
    for i, book_id in enumerate(test_books):
        job = BatchJob(
            job_id=f"prod_100_{book_id}_{int(time.time())}_{i}",
            book_id=str(book_id),
            priority=1,  # High priority
            max_paragraphs=1  # Just 1 attribute per book for diversity
        )
        
        # Insert into database
        cursor.execute('''
            INSERT INTO batch_jobs 
            (job_id, book_id, priority, max_paragraphs, status, created_at, retry_count, error_message, output_file)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            job.job_id, job.book_id, job.priority, job.max_paragraphs,
            job.status, job.created_at, job.retry_count, job.error_message, job.output_file
        ))
        
        jobs_added += 1
        
        if (i + 1) % 20 == 0:
            print(f"  ✅ Added {i + 1}/100 jobs")
    
    conn.commit()
    conn.close()
    
    print(f"\n🎯 SETUP COMPLETE:")
    print(f"  📊 Jobs added: {jobs_added}")
    print(f"  📁 Database: {harvester.db_path}")
    print(f"  📁 Output dir: {harvester.output_dir}")
    
    print(f"\n🚀 TO RUN THE TEST:")
    print(f"  python mass_attribute_harvester.py process --output-dir ./production_100_attributes --max-workers 4")
    
    print(f"\n📊 TO CHECK STATUS:")
    print(f"  python mass_attribute_harvester.py status")
    
    return jobs_added

def check_current_status():
    """Check status of any existing jobs"""
    
    print("\n📊 CURRENT JOB STATUS:")
    print("-" * 40)
    
    harvester = MassAttributeHarvester()
    
    try:
        status = harvester.get_job_status()
        
        print(f"📋 Job counts:")
        for status_name, count in status['status_counts'].items():
            print(f"  {status_name}: {count}")
        
        print(f"📁 Output directory: {status['output_directory']}")
        
        if status['recent_jobs']:
            print(f"\n📝 Recent jobs:")
            for job in status['recent_jobs'][:5]:
                print(f"  {job[1]} (Book {job[2]}) - {job[5]}")
                
    except Exception as e:
        print(f"❌ Error checking status: {e}")

if __name__ == "__main__":
    # Check current status first
    check_current_status()
    
    # Setup new test
    jobs_added = setup_100_book_jobs()
    
    # Check status again
    check_current_status()