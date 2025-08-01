#!/usr/bin/env python3
"""
Quick Status Checker - Simple command-line status without curses UI
"""

import os
import sys
import time
import sqlite3
import psutil
import json
from datetime import datetime, timedelta
from pathlib import Path

def get_batch_processes():
    """Find running batch processes"""
    processes = []
    batch_scripts = [
        'archive_cli.py', 'mass_attribute_harvester.py', 'run_literature_mining.py',
        'batch_monitor.py', 'batch_curator.py', 'embedding_service.py', 'api_enhanced.py'
    ]
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent', 'memory_info', 'create_time']):
        try:
            if proc.info['name'] in ['python', 'python3']:
                cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                for script in batch_scripts:
                    if script in cmdline:
                        runtime = time.time() - proc.info['create_time']
                        processes.append({
                            'pid': proc.info['pid'],
                            'script': script,
                            'cpu': proc.info['cpu_percent'],
                            'memory_mb': proc.info['memory_info'].rss / 1024 / 1024,
                            'runtime_hours': runtime / 3600
                        })
                        break
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    return processes

def check_recent_activity():
    """Check for recent file activity"""
    directories = [
        'processed_quantum', 'processed_consciousness', 'processed_AI',
        'quality', 'demo_attributes', 'discovered_attributes', 'chromadb_data'
    ]
    
    activity = {}
    cutoff_time = time.time() - 300  # 5 minutes ago
    
    for dir_name in directories:
        dir_path = Path(dir_name)
        if dir_path.exists():
            recent_count = sum(1 for f in dir_path.rglob('*') 
                             if f.is_file() and f.stat().st_mtime > cutoff_time)
            total_count = sum(1 for f in dir_path.rglob('*') if f.is_file())
            activity[dir_name] = {'recent': recent_count, 'total': total_count}
    
    return activity

def main():
    print("🚀 HUMANIZER BATCH STATUS SNAPSHOT")
    print("=" * 50)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check processes
    processes = get_batch_processes()
    print("📊 ACTIVE PROCESSES:")
    if processes:
        print(f"{'SCRIPT':<25} {'PID':<8} {'CPU%':<6} {'MEM(MB)':<8} {'HOURS':<6}")
        print("-" * 60)
        for proc in processes:
            print(f"{proc['script']:<25} {proc['pid']:<8} {proc['cpu']:<6.1f} "
                  f"{proc['memory_mb']:<8.1f} {proc['runtime_hours']:<6.1f}")
    else:
        print("  No batch processes running")
    print()
    
    # Check file activity
    activity = check_recent_activity()
    print("📁 RECENT ACTIVITY (last 5 minutes):")
    if activity:
        print(f"{'DIRECTORY':<25} {'RECENT':<8} {'TOTAL':<8}")
        print("-" * 45)
        for dir_name, counts in activity.items():
            marker = "🟢" if counts['recent'] > 0 else "⚪"
            print(f"{marker} {dir_name:<23} {counts['recent']:<8} {counts['total']:<8}")
    else:
        print("  No activity directories found")
    print()
    
    # Check database jobs if available
    batch_db = Path("batch_jobs.db")
    if batch_db.exists():
        try:
            conn = sqlite3.connect(str(batch_db))
            cursor = conn.cursor()
            cursor.execute("SELECT status, COUNT(*) FROM jobs GROUP BY status")
            job_counts = dict(cursor.fetchall())
            conn.close()
            
            print("🗄️  DATABASE JOBS:")
            for status, count in job_counts.items():
                emoji = {"completed": "✅", "running": "🟢", "failed": "❌", "pending": "⏳"}.get(status, "⚪")
                print(f"  {emoji} {status}: {count}")
        except Exception as e:
            print(f"  Database check failed: {e}")
        print()
    
    # Quick health check
    api_health = "❌"
    try:
        import requests
        response = requests.get("http://127.0.0.1:8100/health", timeout=2)
        if response.status_code == 200:
            api_health = "✅"
    except:
        pass
    
    print("🔧 SERVICES:")
    print(f"  Enhanced API (port 8100): {api_health}")
    
    # PostgreSQL check
    pg_health = "❌"
    try:
        import subprocess
        result = subprocess.run(['pg_isready'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            pg_health = "✅"
    except:
        pass
    print(f"  PostgreSQL: {pg_health}")
    
    print()
    print("💡 Use 'python batch_status_ui.py' for real-time monitoring")

if __name__ == "__main__":
    main()