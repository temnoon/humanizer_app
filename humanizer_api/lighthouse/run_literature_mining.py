#!/usr/bin/env python3
"""
Literature Mining CLI Runner
===========================

Simple script to run literature attribute mining from the command line.
This allows testing the system without going through the API.

Usage:
    python run_literature_mining.py --sample-size 3 --passages-per-work 20
    python run_literature_mining.py --full-run  # Mine all classic works (may take a while)
"""

import asyncio
import argparse
import json
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Mine Project Gutenberg literature for narrative attributes")
    
    parser.add_argument(
        "--sample-size", 
        type=int, 
        default=3,
        help="Number of literary works to analyze (default: 3)"
    )
    
    parser.add_argument(
        "--passages-per-work",
        type=int,
        default=25,
        help="Maximum passages to extract per work (default: 25)"
    )
    
    parser.add_argument(
        "--full-run",
        action="store_true",
        help="Mine all classic works (may take 30+ minutes)"
    )
    
    parser.add_argument(
        "--output-file",
        type=str,
        default="literature_mining_results.json",
        help="Output file for results (default: literature_mining_results.json)"
    )
    
    args = parser.parse_args()
    
    # Determine sample size
    if args.full_run:
        sample_size = None  # Mine all works
        logger.info("Running full literature mining (this may take 30+ minutes)")
    else:
        sample_size = args.sample_size
        logger.info(f"Running literature mining for {sample_size} works")
    
    # Run the mining
    results = asyncio.run(run_mining(
        sample_size=sample_size,
        max_passages_per_work=args.passages_per_work
    ))
    
    # Save results
    output_path = Path(args.output_file)
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    logger.info(f"Results saved to {output_path}")
    
    # Print summary
    if "error" not in results:
        print("\n" + "="*60)
        print("LITERATURE MINING RESULTS")
        print("="*60)
        print(f"Works processed: {results.get('total_works_processed', 0)}")
        print(f"Passages analyzed: {results.get('total_passages_analyzed', 0)}")
        print(f"Clusters discovered: {results.get('total_clusters_discovered', 0)}")
        print("\nAttribute categories discovered:")
        
        categories = results.get('attribute_categories', {})
        for category, count in categories.items():
            print(f"  {category}: {count} attributes")
        
        print("\nSample discovered attributes:")
        discovered = results.get('discovered_attributes_by_category', {})
        for category, attributes in discovered.items():
            print(f"\n{category.upper()}:")
            for attr in attributes[:5]:  # Show first 5
                print(f"  - {attr}")
            if len(attributes) > 5:
                print(f"  ... and {len(attributes) - 5} more")
    else:
        print(f"Error: {results['error']}")

async def run_mining(sample_size=None, max_passages_per_work=25):
    """Run the literature mining process."""
    
    try:
        from literature_attribute_miner import mine_literature_for_attributes, CLASSIC_LITERATURE_IDS
        
        # Determine which works to mine
        if sample_size is None:
            gutenberg_ids = CLASSIC_LITERATURE_IDS  # Mine all
        else:
            gutenberg_ids = CLASSIC_LITERATURE_IDS[:sample_size]
        
        logger.info(f"Mining {len(gutenberg_ids)} works from Project Gutenberg")
        
        # Run the mining
        results = await mine_literature_for_attributes(
            gutenberg_ids=gutenberg_ids,
            max_passages_per_work=max_passages_per_work
        )
        
        return results
        
    except Exception as e:
        logger.error(f"Mining failed: {e}")
        return {"error": str(e)}

async def show_discovered_attributes():
    """Show already discovered attributes from previous mining runs."""
    
    try:
        import sqlite3
        from collections import defaultdict
        
        db_path = "./data/literature_attributes.db"
        
        if not Path(db_path).exists():
            print("No literature analysis database found.")
            print("Run: python run_literature_mining.py --sample-size 3")
            return
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get statistics
        cursor.execute("SELECT COUNT(*) FROM literary_passages")
        total_passages = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT author) FROM literary_passages")
        unique_authors = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT gutenberg_id) FROM literary_passages")
        unique_works = cursor.fetchone()[0]
        
        # Get discovered attributes
        cursor.execute("""
            SELECT category, label, quality_score
            FROM discovered_attributes 
            ORDER BY category, quality_score DESC
        """)
        
        attributes_by_category = defaultdict(list)
        
        for category, label, quality_score in cursor.fetchall():
            attributes_by_category[category].append((label, quality_score))
        
        conn.close()
        
        print("\n" + "="*60)
        print("DISCOVERED LITERATURE-BASED ATTRIBUTES")
        print("="*60)
        print(f"Total passages analyzed: {total_passages}")
        print(f"Unique authors: {unique_authors}")
        print(f"Unique works: {unique_works}")
        print(f"Total attributes discovered: {sum(len(attrs) for attrs in attributes_by_category.values())}")
        
        for category, attributes in attributes_by_category.items():
            print(f"\n{category.upper()} ({len(attributes)} attributes):")
            for label, quality_score in attributes:
                print(f"  - {label} (quality: {quality_score:.3f})")
        
    except Exception as e:
        logger.error(f"Failed to show attributes: {e}")

if __name__ == "__main__":
    # Check if user wants to see existing results
    if len(__import__('sys').argv) == 1:
        print("Literature Attribute Mining System")
        print("=" * 40)
        print()
        print("Options:")
        print("  --help                    Show help")
        print("  --sample-size N           Mine N works (default: 3)")
        print("  --passages-per-work N     Extract N passages per work (default: 25)")
        print("  --full-run                Mine all classic works")
        print("  --show-existing           Show already discovered attributes")
        print()
        print("Examples:")
        print("  python run_literature_mining.py --sample-size 3")
        print("  python run_literature_mining.py --full-run")
        print()
        
        # Show existing attributes if database exists
        if Path("./data/literature_attributes.db").exists():
            asyncio.run(show_discovered_attributes())
        else:
            print("No existing attributes found. Run with --sample-size to start mining.")
    
    elif "--show-existing" in __import__('sys').argv:
        asyncio.run(show_discovered_attributes())
    else:
        main()