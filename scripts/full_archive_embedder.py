#!/usr/bin/env python3
"""
Full Archive Hierarchical Embedder
Processes all suitable conversations in the archive with intelligent batching
"""

import os
import sys
import json
import time
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import psycopg2
from psycopg2.extras import RealDictCursor

class FullArchiveEmbedder:
    """Manages full archive embedding with intelligent batching"""
    
    def __init__(self, database_url: str = "postgresql://tem@localhost/humanizer_archive"):
        self.database_url = database_url
        self.script_dir = Path(__file__).parent
        self.embedder_script = self.script_dir / "hierarchical_embedder.py"
        self.log_dir = self.script_dir / "logs"
        self.results_dir = self.script_dir / "test_runs"
        
        # Create directories
        self.log_dir.mkdir(exist_ok=True)
        self.results_dir.mkdir(exist_ok=True)
        
        print("🚀 Full Archive Hierarchical Embedder")
        print("=" * 60)
    
    def get_archive_statistics(self) -> Dict[str, Any]:
        """Get archive statistics to plan batching strategy"""
        
        with psycopg2.connect(self.database_url, cursor_factory=RealDictCursor) as conn:
            cursor = conn.cursor()
            
            # Overall stats
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_conversations,
                    COUNT(CASE WHEN is_duplicate = FALSE THEN 1 END) as unique_conversations,
                    AVG(composite_score) as avg_score,
                    AVG(word_count) as avg_word_count
                FROM conversation_quality_assessments
            """)
            overall_stats = cursor.fetchone()
            
            # Quality distribution
            cursor.execute("""
                SELECT 
                    COUNT(CASE WHEN composite_score > 0.8 THEN 1 END) as excellent,
                    COUNT(CASE WHEN composite_score > 0.6 THEN 1 END) as good,
                    COUNT(CASE WHEN composite_score > 0.4 THEN 1 END) as fair,
                    COUNT(CASE WHEN composite_score > 0.2 THEN 1 END) as poor
                FROM conversation_quality_assessments
                WHERE is_duplicate = FALSE
            """)
            quality_stats = cursor.fetchone()
            
            # Suitable conversations (recommended thresholds)
            cursor.execute("""
                SELECT COUNT(*) as suitable_conversations
                FROM conversation_quality_assessments
                WHERE is_duplicate = FALSE 
                    AND composite_score > 0.3 
                    AND word_count > 200
            """)
            suitable_stats = cursor.fetchone()
            
            return {
                'total': overall_stats['total_conversations'],
                'unique': overall_stats['unique_conversations'],
                'avg_score': float(overall_stats['avg_score']) if overall_stats['avg_score'] else 0,
                'avg_word_count': float(overall_stats['avg_word_count']) if overall_stats['avg_word_count'] else 0,
                'quality_distribution': dict(quality_stats),
                'suitable_for_embedding': suitable_stats['suitable_conversations']
            }
    
    def estimate_processing_time(self, conversation_count: int, batch_size: int = 50) -> Dict[str, Any]:
        """Estimate processing time based on previous performance"""
        
        # Based on our test: 20 conversations in 2.6 minutes
        minutes_per_conversation = 2.6 / 20  # ~0.13 minutes per conversation
        
        total_minutes = conversation_count * minutes_per_conversation
        batch_count = (conversation_count + batch_size - 1) // batch_size
        
        return {
            'total_minutes': total_minutes,
            'total_hours': total_minutes / 60,
            'batch_count': batch_count,
            'minutes_per_batch': total_minutes / batch_count if batch_count > 0 else 0
        }
    
    def run_full_archive_embedding(self, 
                                 batch_size: int = 50,
                                 timeout_minutes: int = 120,
                                 min_score: float = 0.3,
                                 min_words: int = 200,
                                 dry_run: bool = False) -> Dict[str, Any]:
        """Run embedding for entire archive in batches"""
        
        print(f"📊 Analyzing archive...")
        stats = self.get_archive_statistics()
        
        print(f"📈 Archive Statistics:")
        print(f"   Total conversations: {stats['total']:,}")
        print(f"   Unique conversations: {stats['unique']:,}")
        print(f"   Average quality score: {stats['avg_score']:.3f}")
        print(f"   Suitable for embedding: {stats['suitable_for_embedding']:,}")
        
        if stats['suitable_for_embedding'] == 0:
            print("❌ No suitable conversations found")
            return {}
        
        # Estimate processing time  
        estimates = self.estimate_processing_time(stats['suitable_for_embedding'], batch_size)
        
        print(f"\n⏰ Processing Estimates:")
        print(f"   Batch size: {batch_size} conversations")
        print(f"   Number of batches: {estimates['batch_count']}")
        print(f"   Estimated total time: {estimates['total_hours']:.1f} hours")
        print(f"   Estimated per batch: {estimates['minutes_per_batch']:.1f} minutes")
        
        if dry_run:
            print("\n🧪 DRY RUN - No actual processing")
            return {
                'dry_run': True,
                'statistics': stats,
                'estimates': estimates
            }
        
        # Confirm before starting
        print(f"\n🤔 This will process {stats['suitable_for_embedding']:,} conversations")
        print(f"   Estimated time: {estimates['total_hours']:.1f} hours")
        confirm = input("   Proceed? (y/N): ").lower().strip()
        
        if confirm != 'y':
            print("🚫 Operation cancelled")
            return {}
        
        # Start processing
        print(f"\n🚀 STARTING FULL ARCHIVE EMBEDDING")
        print("=" * 60)
        
        start_time = datetime.now()
        batch_results = []
        total_chunks = 0
        total_processed = 0
        failed_batches = 0
        
        # Process in batches
        for batch_num in range(1, estimates['batch_count'] + 1):
            print(f"\n📦 BATCH {batch_num}/{estimates['batch_count']}")
            print(f"   Progress: {((batch_num-1) / estimates['batch_count'] * 100):.1f}%")
            
            batch_start = datetime.now()
            
            try:
                # Run batch
                cmd = [
                    sys.executable,
                    str(self.embedder_script),
                    "embed",
                    "--limit", str(batch_size),
                    "--timeout", str(timeout_minutes)
                ]
                
                print(f"   🔄 Running: {' '.join(cmd)}")
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_minutes*60+300)
                
                if result.returncode == 0:
                    print("   ✅ Batch completed successfully")
                    
                    # Try to parse the latest results file
                    latest_result = self._get_latest_result_file()
                    if latest_result:
                        with open(latest_result) as f:
                            batch_data = json.load(f)
                        
                        batch_chunks = batch_data.get('total_chunks_created', 0)
                        batch_processed = batch_data.get('processed_conversations', 0)
                        
                        total_chunks += batch_chunks
                        total_processed += batch_processed
                        
                        batch_results.append({
                            'batch_number': batch_num,
                            'chunks_created': batch_chunks,
                            'conversations_processed': batch_processed,
                            'processing_time': (datetime.now() - batch_start).total_seconds(),
                            'success': True
                        })
                        
                        print(f"   📝 Batch created {batch_chunks:,} chunks")
                        print(f"   📊 Running totals: {total_processed:,} conversations, {total_chunks:,} chunks")
                    
                else:
                    raise subprocess.CalledProcessError(result.returncode, cmd, result.stdout, result.stderr)
                
            except Exception as e:
                print(f"   ❌ Batch failed: {e}")
                failed_batches += 1
                
                batch_results.append({
                    'batch_number': batch_num,
                    'error': str(e),
                    'processing_time': (datetime.now() - batch_start).total_seconds(),
                    'success': False
                })
                
                # Ask to continue
                cont = input("   🤔 Continue with next batch? (y/N): ").lower().strip()
                if cont != 'y':
                    print("   🚫 Processing stopped by user")
                    break
            
            # Brief pause between batches
            if batch_num < estimates['batch_count']:
                print("   ⏸️ Pausing 10 seconds...")
                time.sleep(10)
        
        # Final results
        total_time = datetime.now() - start_time
        
        results = {
            'start_time': start_time.isoformat(),
            'end_time': datetime.now().isoformat(),
            'total_processing_time_minutes': total_time.total_seconds() / 60,
            'total_conversations_processed': total_processed,
            'total_chunks_created': total_chunks,
            'successful_batches': len([r for r in batch_results if r.get('success')]),
            'failed_batches': failed_batches,
            'batch_results': batch_results,
            'statistics': stats,
            'estimates': estimates
        }
        
        # Save final results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = self.results_dir / f"full_archive_embedding_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        # Print summary
        print(f"\n{'='*60}")
        print(f"🎉 FULL ARCHIVE EMBEDDING COMPLETE")
        print(f"{'='*60}")
        print(f"📊 Conversations processed: {total_processed:,}")
        print(f"📝 Total chunks created: {total_chunks:,}")
        print(f"✅ Successful batches: {len([r for r in batch_results if r.get('success')])}")
        print(f"❌ Failed batches: {failed_batches}")
        print(f"⏱️ Total time: {total_time}")
        print(f"📁 Results saved to: {results_file}")
        
        return results
    
    def _get_latest_result_file(self) -> Optional[Path]:
        """Get the most recent results file"""
        result_files = list(self.results_dir.glob("hierarchical_embedding_*.json"))
        if result_files:
            return max(result_files, key=lambda p: p.stat().st_mtime)
        return None

def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Full Archive Hierarchical Embedder",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run to see estimates
  python full_archive_embedder.py --dry-run

  # Process all suitable conversations (default settings)
  python full_archive_embedder.py

  # Custom batch size and quality threshold
  python full_archive_embedder.py --batch-size 25 --min-score 0.4

  # High-quality conversations only
  python full_archive_embedder.py --min-score 0.6 --min-words 500
        """
    )
    
    parser.add_argument('--batch-size', type=int, default=50, help='Conversations per batch')
    parser.add_argument('--timeout', type=int, default=120, help='Timeout per batch (minutes)')
    parser.add_argument('--min-score', type=float, default=0.3, help='Minimum quality score')
    parser.add_argument('--min-words', type=int, default=200, help='Minimum word count')
    parser.add_argument('--dry-run', action='store_true', help='Show estimates without processing')
    
    args = parser.parse_args()
    
    embedder = FullArchiveEmbedder()
    
    results = embedder.run_full_archive_embedding(
        batch_size=args.batch_size,
        timeout_minutes=args.timeout,
        min_score=args.min_score,
        min_words=args.min_words,
        dry_run=args.dry_run
    )
    
    if results and not args.dry_run:
        print(f"\n💡 Monitor progress with:")
        print(f"   python embedding_monitor.py dashboard")
        print(f"\n💡 Search the embedded archive with:")
        print(f"   python hierarchical_embedder.py search \"your query here\"")

if __name__ == "__main__":
    main()