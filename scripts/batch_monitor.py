#!/usr/bin/env python3
"""
Batch Processing Monitor
Real-time monitoring dashboard for mass attribute harvesting jobs
"""

import sys
import os
import json
import time
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import argparse

# Add lighthouse path for imports
lighthouse_path = '/Users/tem/humanizer-lighthouse/humanizer_api/lighthouse'
sys.path.insert(0, lighthouse_path)

from mass_attribute_harvester import MassAttributeHarvester, BatchJob, BatchStats


class BatchMonitor:
    """Real-time monitoring system for batch processing jobs"""
    
    def __init__(self, db_path: str = "./batch_jobs.db", refresh_interval: int = 5):
        self.db_path = db_path
        self.refresh_interval = refresh_interval
        self.harvester = MassAttributeHarvester(db_path=db_path)
        
    def show_dashboard(self, continuous: bool = False):
        """Show interactive monitoring dashboard"""
        
        try:
            while True:
                # Clear screen for continuous mode
                if continuous:
                    os.system('clear' if os.name == 'posix' else 'cls')
                
                print("🏭 MASS ATTRIBUTE HARVESTER - MONITORING DASHBOARD")
                print("=" * 80)
                print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                # Get current status
                status = self.harvester.get_job_status()
                
                # Overall statistics
                self._show_statistics(status)
                
                # Recent jobs
                self._show_recent_jobs(status)
                
                # Performance metrics
                self._show_performance_metrics()
                
                # Job distribution by priority
                self._show_priority_distribution()
                
                if not continuous:
                    break
                    
                print(f"\n⏱️ Refreshing in {self.refresh_interval} seconds... (Ctrl+C to stop)")
                time.sleep(self.refresh_interval)
                
        except KeyboardInterrupt:
            print("\n👋 Monitoring stopped")
    
    def show_detailed_status(self, job_id: str = None):
        """Show detailed status for specific job or all jobs"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if job_id:
            cursor.execute('''
                SELECT job_id, book_id, priority, status, created_at, 
                       started_at, completed_at, error_message, output_file
                FROM batch_jobs WHERE job_id = ?
            ''', (job_id,))
            jobs = cursor.fetchall()
            
            if not jobs:
                print(f"❌ Job '{job_id}' not found")
                return
                
        else:
            cursor.execute('''
                SELECT job_id, book_id, priority, status, created_at, 
                       started_at, completed_at, error_message, output_file
                FROM batch_jobs 
                ORDER BY priority ASC, created_at DESC
                LIMIT 50
            ''')
            jobs = cursor.fetchall()
        
        conn.close()
        
        print(f"📊 DETAILED JOB STATUS ({len(jobs)} jobs)")
        print("=" * 100)
        
        for job in jobs:
            job_id, book_id, priority, status, created_at, started_at, completed_at, error_msg, output_file = job
            
            # Status emoji
            status_emoji = {
                'pending': '⏳',
                'processing': '🔄', 
                'completed': '✅',
                'failed': '❌'
            }.get(status, '❓')
            
            print(f"\n{status_emoji} {job_id}")
            print(f"   📚 Book: {book_id} | Priority: {priority} | Status: {status}")
            print(f"   📅 Created: {created_at}")
            
            if started_at:
                print(f"   🚀 Started: {started_at}")
            if completed_at:
                print(f"   🏁 Completed: {completed_at}")
                
                # Calculate processing time
                if started_at:
                    start_time = datetime.fromisoformat(started_at)
                    end_time = datetime.fromisoformat(completed_at)
                    duration = end_time - start_time
                    print(f"   ⏱️ Duration: {duration}")
            
            if error_msg:
                print(f"   ❌ Error: {error_msg}")
            if output_file:
                print(f"   📁 Output: {output_file}")
    
    def _show_statistics(self, status: Dict[str, Any]):
        """Show overall statistics"""
        
        counts = status['status_counts']
        total = status['total_jobs']
        
        print(f"\n📊 OVERALL STATISTICS")
        print("-" * 40)
        print(f"📦 Total Jobs: {total}")
        print(f"⏳ Pending: {counts.get('pending', 0)}")
        print(f"🔄 Processing: {counts.get('processing', 0)}")
        print(f"✅ Completed: {counts.get('completed', 0)}")
        print(f"❌ Failed: {counts.get('failed', 0)}")
        
        if total > 0:
            completed = counts.get('completed', 0)
            failed = counts.get('failed', 0)
            progress = (completed + failed) / total * 100
            success_rate = completed / max(completed + failed, 1) * 100 if (completed + failed) > 0 else 0
            
            print(f"📈 Progress: {progress:.1f}%")
            print(f"🎯 Success Rate: {success_rate:.1f}%")
    
    def _show_recent_jobs(self, status: Dict[str, Any]):
        """Show recent job activity"""
        
        print(f"\n📋 RECENT ACTIVITY (Last 10 jobs)")
        print("-" * 50)
        
        for job in status['recent_jobs']:
            book_id, job_status, created_at, completed_at, error_message = job
            
            status_emoji = {
                'pending': '⏳',
                'processing': '🔄',
                'completed': '✅', 
                'failed': '❌'
            }.get(job_status, '❓')
            
            time_str = completed_at or created_at
            if time_str:
                try:
                    time_obj = datetime.fromisoformat(time_str)
                    time_display = time_obj.strftime('%H:%M:%S')
                except:
                    time_display = time_str[:8]
            else:
                time_display = "unknown"
            
            print(f"{status_emoji} Book {book_id} | {job_status} | {time_display}")
            if error_message:
                print(f"    ↳ {error_message[:60]}...")
    
    def _show_performance_metrics(self):
        """Show performance metrics"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Average processing time for completed jobs
        cursor.execute('''
            SELECT AVG(
                CASE 
                    WHEN started_at IS NOT NULL AND completed_at IS NOT NULL 
                    THEN (julianday(completed_at) - julianday(started_at)) * 24 * 60 * 60
                    ELSE NULL 
                END
            ) as avg_processing_time
            FROM batch_jobs 
            WHERE status = 'completed'
        ''')
        
        result = cursor.fetchone()
        avg_time = result[0] if result and result[0] else 0
        
        # Jobs processed in last hour
        cursor.execute('''
            SELECT COUNT(*) FROM batch_jobs 
            WHERE completed_at > datetime('now', '-1 hour')
        ''')
        
        recent_completions = cursor.fetchone()[0]
        
        # Error rate in last 100 jobs
        cursor.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed
            FROM (
                SELECT status FROM batch_jobs 
                WHERE status IN ('completed', 'failed')
                ORDER BY completed_at DESC 
                LIMIT 100
            )
        ''')
        
        error_stats = cursor.fetchone()
        error_rate = (error_stats[1] / max(error_stats[0], 1)) * 100 if error_stats[0] > 0 else 0
        
        conn.close()
        
        print(f"\n⚡ PERFORMANCE METRICS")
        print("-" * 30)
        print(f"⏱️ Avg Processing Time: {avg_time:.1f}s")
        print(f"🚀 Jobs/Hour: {recent_completions}")
        print(f"📉 Error Rate (last 100): {error_rate:.1f}%")
    
    def _show_priority_distribution(self):
        """Show job distribution by priority"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT priority, status, COUNT(*) as count
            FROM batch_jobs 
            GROUP BY priority, status
            ORDER BY priority, status
        ''')
        
        results = cursor.fetchall()
        conn.close()
        
        if not results:
            return
        
        print(f"\n🎯 PRIORITY DISTRIBUTION")
        print("-" * 25)
        
        priority_data = {}
        for priority, status, count in results:
            if priority not in priority_data:
                priority_data[priority] = {}
            priority_data[priority][status] = count
        
        for priority in sorted(priority_data.keys()):
            statuses = priority_data[priority]
            total = sum(statuses.values())
            
            print(f"Priority {priority}: {total} jobs")
            for status, count in statuses.items():
                print(f"  {status}: {count}")
    
    def cleanup_old_jobs(self, days: int = 30):
        """Clean up old completed jobs"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        cursor.execute('''
            SELECT COUNT(*) FROM batch_jobs 
            WHERE status IN ('completed', 'failed') 
            AND completed_at < ?
        ''', (cutoff_date,))
        
        old_jobs = cursor.fetchone()[0]
        
        if old_jobs == 0:
            print(f"✅ No jobs older than {days} days found")
            conn.close()
            return
        
        print(f"🧹 Found {old_jobs} jobs older than {days} days")
        confirm = input("Delete these jobs? (y/N): ").lower().strip()
        
        if confirm == 'y':
            cursor.execute('''
                DELETE FROM batch_jobs 
                WHERE status IN ('completed', 'failed') 
                AND completed_at < ?
            ''', (cutoff_date,))
            
            deleted = cursor.rowcount
            conn.commit()
            print(f"✅ Deleted {deleted} old jobs")
        else:
            print("🚫 Cleanup cancelled")
        
        conn.close()
    
    def export_job_history(self, output_file: str = None):
        """Export job history to JSON file"""
        
        if not output_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"job_history_{timestamp}.json"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT job_id, book_id, priority, max_paragraphs, retry_count,
                   status, created_at, started_at, completed_at, error_message, output_file
            FROM batch_jobs
            ORDER BY created_at DESC
        ''')
        
        jobs = []
        for row in cursor.fetchall():
            job_data = {
                'job_id': row[0],
                'book_id': row[1],
                'priority': row[2],
                'max_paragraphs': row[3],
                'retry_count': row[4],
                'status': row[5],
                'created_at': row[6],
                'started_at': row[7],
                'completed_at': row[8],
                'error_message': row[9],
                'output_file': row[10]
            }
            jobs.append(job_data)
        
        conn.close()
        
        export_data = {
            'export_timestamp': datetime.now().isoformat(),
            'total_jobs': len(jobs),
            'jobs': jobs
        }
        
        with open(output_file, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"📊 Exported {len(jobs)} jobs to {output_file}")


def main():
    """CLI entry point for batch monitoring"""
    
    parser = argparse.ArgumentParser(description='Batch Processing Monitor')
    parser.add_argument('command', 
                       choices=['dashboard', 'status', 'cleanup', 'export'], 
                       help='Command to execute')
    
    # Dashboard arguments
    parser.add_argument('--continuous', '-c', action='store_true',
                       help='Continuous monitoring (dashboard only)')
    parser.add_argument('--refresh', type=int, default=5,
                       help='Refresh interval in seconds')
    
    # Status arguments  
    parser.add_argument('--job-id', help='Show details for specific job')
    
    # Cleanup arguments
    parser.add_argument('--days', type=int, default=30,
                       help='Delete jobs older than N days')
    
    # Export arguments
    parser.add_argument('--output', help='Output file for export')
    
    # Database path
    parser.add_argument('--db-path', default='./batch_jobs.db',
                       help='Path to SQLite database')
    
    args = parser.parse_args()
    
    monitor = BatchMonitor(db_path=args.db_path, refresh_interval=args.refresh)
    
    if args.command == 'dashboard':
        monitor.show_dashboard(continuous=args.continuous)
    
    elif args.command == 'status':
        monitor.show_detailed_status(job_id=args.job_id)
    
    elif args.command == 'cleanup':
        monitor.cleanup_old_jobs(days=args.days)
    
    elif args.command == 'export':
        monitor.export_job_history(output_file=args.output)


if __name__ == "__main__":
    main()