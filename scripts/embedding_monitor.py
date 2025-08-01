#!/usr/bin/env python3
"""
Hierarchical Embedding Monitor
Real-time monitoring for embedding batch processes
"""

import sqlite3
import time
import os
import argparse
from datetime import datetime
from pathlib import Path

class EmbeddingMonitor:
    """Monitor hierarchical embedding batch processes"""
    
    def __init__(self, db_path: str = "./hierarchical_embeddings_batch.db"):
        self.db_path = db_path
        
    def show_live_dashboard(self, refresh_interval: int = 5):
        """Show live monitoring dashboard"""
        
        try:
            while True:
                # Clear screen
                os.system('clear' if os.name == 'posix' else 'cls')
                
                print("🏗️ HIERARCHICAL EMBEDDING BATCH MONITOR")
                print("=" * 80)
                print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"🗄️ Database: {self.db_path}")
                
                # Check if database exists
                if not Path(self.db_path).exists():
                    print("\n❌ Batch database not found - no jobs to monitor")
                    print("   Start a batch embedding process to create jobs")
                    time.sleep(refresh_interval)
                    continue
                
                # Show current batches
                self._show_batch_overview()
                
                # Show active jobs
                self._show_active_jobs()
                
                # Show recent completed jobs
                self._show_recent_jobs()
                
                # Show performance stats
                self._show_performance_stats()
                
                print(f"\n⏱️ Refreshing in {refresh_interval} seconds... (Ctrl+C to stop)")
                time.sleep(refresh_interval)
                
        except KeyboardInterrupt:
            print("\n👋 Monitoring stopped")
    
    def _show_batch_overview(self):
        """Show overview of current batches"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT batch_id, total_conversations, conversations_processed, 
                   conversations_failed, total_chunks_created, status, started_at
            FROM batch_stats
            ORDER BY started_at DESC
            LIMIT 5
        ''')
        
        batches = cursor.fetchall()
        conn.close()
        
        if not batches:
            print("\n📊 No batches found")
            return
        
        print(f"\n📊 RECENT BATCHES (Last 5)")
        print("-" * 60)
        
        for batch in batches:
            batch_id, total, processed, failed, chunks, status, started = batch
            
            status_emoji = {
                'running': '🔄',
                'completed': '✅',
                'failed': '❌'
            }.get(status, '❓')
            
            progress = (processed / total * 100) if total > 0 else 0
            success_rate = (processed / max(processed + failed, 1) * 100) if (processed + failed) > 0 else 0
            
            print(f"{status_emoji} {batch_id}")
            print(f"   📈 Progress: {processed}/{total} ({progress:.1f}%) | Success: {success_rate:.1f}%")
            print(f"   📝 Chunks: {chunks} | Failed: {failed} | Started: {started[:19] if started else 'Unknown'}")
            print()
    
    def _show_active_jobs(self):
        """Show currently active jobs"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT job_id, conversation_id, status, started_at, 
                   (julianday('now') - julianday(started_at)) * 24 * 60 as minutes_running
            FROM embedding_jobs
            WHERE status IN ('pending', 'processing')
            ORDER BY started_at DESC
            LIMIT 10
        ''')
        
        jobs = cursor.fetchall()
        conn.close()
        
        print(f"\n🔄 ACTIVE JOBS ({len(jobs)} jobs)")
        print("-" * 40)
        
        if not jobs:
            print("   No active jobs")
            return
        
        for job in jobs:
            job_id, conv_id, status, started, minutes = job
            
            status_emoji = {
                'pending': '⏳',
                'processing': '🔄'
            }.get(status, '❓')
            
            if status == 'processing' and minutes:
                print(f"{status_emoji} Conv {conv_id} | {status} for {minutes:.1f}m")
            else:
                print(f"{status_emoji} Conv {conv_id} | {status}")
    
    def _show_recent_jobs(self):
        """Show recently completed jobs"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT conversation_id, status, chunks_created, processing_time_seconds, completed_at
            FROM embedding_jobs
            WHERE status IN ('completed', 'failed')
            ORDER BY completed_at DESC
            LIMIT 8
        ''')
        
        jobs = cursor.fetchall()
        conn.close()
        
        print(f"\n📋 RECENT COMPLETIONS (Last 8)")
        print("-" * 45)
        
        if not jobs:
            print("   No completed jobs")
            return
        
        for job in jobs:
            conv_id, status, chunks, time_sec, completed = job
            
            status_emoji = {
                'completed': '✅',
                'failed': '❌'
            }.get(status, '❓')
            
            time_str = completed[:19] if completed else 'Unknown'
            
            if status == 'completed':
                print(f"{status_emoji} Conv {conv_id} | {chunks} chunks | {time_sec:.1f}s | {time_str}")
            else:
                print(f"{status_emoji} Conv {conv_id} | failed | {time_str}")
    
    def _show_performance_stats(self):
        """Show performance statistics"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Overall stats
        cursor.execute('''
            SELECT 
                COUNT(*) as total_jobs,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
                SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
                SUM(CASE WHEN status = 'processing' THEN 1 ELSE 0 END) as processing,
                SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending,
                AVG(CASE WHEN status = 'completed' THEN processing_time_seconds END) as avg_time,
                SUM(CASE WHEN status = 'completed' THEN chunks_created ELSE 0 END) as total_chunks
            FROM embedding_jobs
        ''')
        
        stats = cursor.fetchone()
        
        # Recent throughput (last hour)
        cursor.execute('''
            SELECT COUNT(*), AVG(processing_time_seconds)
            FROM embedding_jobs
            WHERE status = 'completed' 
            AND completed_at > datetime('now', '-1 hour')
        ''')
        
        recent_stats = cursor.fetchone()
        conn.close()
        
        if not stats or stats[0] == 0:
            print(f"\n⚡ PERFORMANCE: No jobs found")
            return
        
        total, completed, failed, processing, pending, avg_time, total_chunks = stats
        recent_count, recent_avg_time = recent_stats
        
        success_rate = (completed / max(completed + failed, 1) * 100) if (completed + failed) > 0 else 0
        
        print(f"\n⚡ PERFORMANCE STATS")
        print("-" * 25)
        print(f"📦 Total Jobs: {total} | ✅ {completed} | ❌ {failed} | 🔄 {processing} | ⏳ {pending}")
        print(f"🎯 Success Rate: {success_rate:.1f}%")
        print(f"⏱️ Avg Time: {avg_time:.1f}s | 📝 Total Chunks: {total_chunks}")
        print(f"🚀 Last Hour: {recent_count or 0} jobs | Avg: {recent_avg_time:.1f}s" if recent_avg_time else f"🚀 Last Hour: {recent_count or 0} jobs")
    
    def show_batch_details(self, batch_id: str = None):
        """Show detailed batch information"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if batch_id:
            cursor.execute('''
                SELECT * FROM batch_stats WHERE batch_id = ?
            ''', (batch_id,))
            batches = cursor.fetchall()
            
            if not batches:
                print(f"❌ Batch '{batch_id}' not found")
                return
        else:
            cursor.execute('''
                SELECT * FROM batch_stats ORDER BY started_at DESC LIMIT 10
            ''')
            batches = cursor.fetchall()
        
        for batch in batches:
            batch_id, total, processed, failed, chunks, started, completed, status = batch
            
            print(f"\n📊 BATCH DETAILS: {batch_id}")
            print("=" * 60)
            print(f"Status: {status}")
            print(f"Started: {started}")
            print(f"Completed: {completed or 'Still running'}")
            print(f"Conversations: {processed}/{total} processed, {failed} failed")
            print(f"Total Chunks Created: {chunks}")
            
            if started and completed:
                start_time = datetime.fromisoformat(started)
                end_time = datetime.fromisoformat(completed)
                duration = end_time - start_time
                print(f"Duration: {duration}")
        
        conn.close()

def main():
    """CLI entry point"""
    
    parser = argparse.ArgumentParser(description='Hierarchical Embedding Batch Monitor')
    parser.add_argument('command', 
                       choices=['dashboard', 'details'], 
                       help='Command to execute')
    
    parser.add_argument('--batch-id', help='Show details for specific batch')
    parser.add_argument('--refresh', type=int, default=5, help='Refresh interval in seconds')
    parser.add_argument('--db-path', default='./hierarchical_embeddings_batch.db', help='Batch database path')
    
    args = parser.parse_args()
    
    monitor = EmbeddingMonitor(db_path=args.db_path)
    
    if args.command == 'dashboard':
        monitor.show_live_dashboard(refresh_interval=args.refresh)
    elif args.command == 'details':
        monitor.show_batch_details(batch_id=args.batch_id)

if __name__ == "__main__":
    main()