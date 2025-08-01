#!/usr/bin/env python3
"""
Batch Processing Status UI
Real-time terminal dashboard for monitoring archive processing jobs
"""

import os
import sys
import time
import sqlite3
import psutil
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
import curses
from collections import defaultdict, deque
import threading
import re

class BatchStatusUI:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.running = True
        self.refresh_interval = 2.0
        self.log_lines = deque(maxlen=100)
        self.job_history = deque(maxlen=50)
        self.error_patterns = [
            r'ERROR', r'FAILED', r'Exception', r'Traceback',
            r'Connection refused', r'timeout', r'killed'
        ]
        
        # Initialize colors
        curses.start_color()
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)   # Running
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # Pending/Warning
        curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)     # Error/Crashed
        curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)    # Info
        curses.init_pair(5, curses.COLOR_CYAN, curses.COLOR_BLACK)    # Highlight
        curses.init_pair(6, curses.COLOR_MAGENTA, curses.COLOR_BLACK) # Complete
        
        # Process tracking
        self.processes = {}
        self.last_activity = {}
        self.loop_detection = defaultdict(int)
        
        # Database paths
        self.batch_db = Path("batch_jobs.db")
        self.humanizer_db = Path("data/humanizer.db")
        
    def get_terminal_processes(self):
        """Find Python processes running our batch scripts"""
        processes = {}
        batch_scripts = [
            'archive_cli.py', 'mass_attribute_harvester.py', 'run_literature_mining.py',
            'batch_monitor.py', 'batch_curator.py', 'embedding_service.py',
            'api_enhanced.py', 'conversation_browser.py'
        ]
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent', 'memory_info', 'create_time']):
                try:
                    if proc.info['name'] == 'python' or proc.info['name'] == 'python3':
                        cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                        for script in batch_scripts:
                            if script in cmdline:
                                processes[proc.info['pid']] = {
                                    'script': script,
                                    'cmdline': cmdline,
                                    'cpu': proc.info['cpu_percent'],
                                    'memory': proc.info['memory_info'].rss / 1024 / 1024,  # MB
                                    'runtime': time.time() - proc.info['create_time'],
                                    'status': 'running'
                                }
                                break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            self.log_lines.append(f"ERROR: Process scan failed: {e}")
            
        return processes

    def check_database_status(self):
        """Check batch job database for job status"""
        jobs = []
        try:
            if self.batch_db.exists():
                conn = sqlite3.connect(str(self.batch_db))
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, job_type, status, created_at, updated_at, 
                           progress, error_message, metadata 
                    FROM jobs 
                    ORDER BY updated_at DESC 
                    LIMIT 20
                """)
                jobs = cursor.fetchall()
                conn.close()
        except Exception as e:
            self.log_lines.append(f"DB Error: {e}")
        
        return jobs

    def check_file_activity(self):
        """Monitor file system activity for processing indicators"""
        activity = {}
        directories = [
            'processed_quantum', 'processed_consciousness', 'processed_AI',
            'processed_philosophy', 'processed_narrative', 'quality',
            'demo_attributes', 'discovered_attributes', 'chromadb_data',
            'data', 'logs'
        ]
        
        for dir_name in directories:
            dir_path = Path(dir_name)
            if dir_path.exists():
                try:
                    # Count recent files (last 5 minutes)
                    recent_files = 0
                    total_files = 0
                    cutoff_time = time.time() - 300  # 5 minutes
                    
                    for item in dir_path.rglob('*'):
                        if item.is_file():
                            total_files += 1
                            if item.stat().st_mtime > cutoff_time:
                                recent_files += 1
                    
                    activity[dir_name] = {
                        'recent_files': recent_files,
                        'total_files': total_files,
                        'last_modified': max([f.stat().st_mtime for f in dir_path.rglob('*') if f.is_file()], default=0)
                    }
                except Exception as e:
                    activity[dir_name] = {'error': str(e)}
        
        return activity

    def detect_loops_and_crashes(self, processes):
        """Detect if processes are stuck in loops or have crashed"""
        current_time = time.time()
        
        for pid, proc_info in processes.items():
            script = proc_info['script']
            
            # Check for loops (low CPU usage for extended periods on active scripts)
            if proc_info['cpu'] < 1.0 and script in ['mass_attribute_harvester.py', 'run_literature_mining.py']:
                self.loop_detection[pid] += 1
                if self.loop_detection[pid] > 10:  # 20 seconds of low activity
                    proc_info['status'] = 'possibly_looped'
            else:
                self.loop_detection[pid] = 0
                
            # Check for excessive memory usage
            if proc_info['memory'] > 1000:  # 1GB
                proc_info['status'] = 'high_memory'
                
            # Check for very long runtime without progress
            if proc_info['runtime'] > 3600:  # 1 hour
                proc_info['status'] = 'long_running'

    def get_log_tail(self, log_file, lines=5):
        """Get last few lines from log file"""
        try:
            if Path(log_file).exists():
                result = subprocess.run(['tail', '-n', str(lines), log_file], 
                                      capture_output=True, text=True)
                return result.stdout.strip().split('\n') if result.stdout else []
        except Exception:
            pass
        return []

    def draw_header(self, y=0):
        """Draw the header section"""
        header = "🚀 HUMANIZER BATCH PROCESSING MONITOR"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        self.stdscr.addstr(y, 2, header, curses.color_pair(5) | curses.A_BOLD)
        self.stdscr.addstr(y, 60, f"Updated: {timestamp}", curses.color_pair(4))
        
        # Draw separator
        width = curses.COLS - 4
        self.stdscr.addstr(y + 1, 2, "═" * width, curses.color_pair(4))
        
        return y + 3

    def draw_processes(self, y):
        """Draw active processes section"""
        self.stdscr.addstr(y, 2, "📊 ACTIVE PROCESSES", curses.color_pair(5) | curses.A_BOLD)
        y += 2
        
        processes = self.get_terminal_processes()
        self.detect_loops_and_crashes(processes)
        
        if not processes:
            self.stdscr.addstr(y, 4, "No batch processes currently running", curses.color_pair(2))
            return y + 2
            
        # Header row
        self.stdscr.addstr(y, 4, "PID     SCRIPT                    CPU%   MEM(MB)  RUNTIME  STATUS", 
                          curses.color_pair(4) | curses.A_BOLD)
        y += 1
        
        for pid, proc in sorted(processes.items()):
            status = proc['status']
            runtime_str = f"{int(proc['runtime']//3600):02d}:{int((proc['runtime']%3600)//60):02d}:{int(proc['runtime']%60):02d}"
            
            # Choose color based on status
            if status == 'running':
                color = curses.color_pair(1)
            elif status in ['possibly_looped', 'long_running']:
                color = curses.color_pair(2)
            elif status in ['high_memory']:
                color = curses.color_pair(3)
            else:
                color = curses.color_pair(1)
                
            line = f"{pid:<7} {proc['script']:<25} {proc['cpu']:>5.1f}   {proc['memory']:>6.1f}  {runtime_str}  {status}"
            self.stdscr.addstr(y, 4, line, color)
            y += 1
            
        return y + 1

    def draw_database_jobs(self, y):
        """Draw database job status"""
        self.stdscr.addstr(y, 2, "🗄️  DATABASE JOBS", curses.color_pair(5) | curses.A_BOLD)
        y += 2
        
        jobs = self.check_database_status()
        
        if not jobs:
            self.stdscr.addstr(y, 4, "No database jobs found", curses.color_pair(2))
            return y + 2
            
        # Header
        self.stdscr.addstr(y, 4, "ID   TYPE                STATUS      PROGRESS  UPDATED", 
                          curses.color_pair(4) | curses.A_BOLD)
        y += 1
        
        for job in jobs[:8]:  # Show only first 8 jobs
            job_id, job_type, status, created, updated, progress, error, metadata = job
            
            # Format progress
            progress_str = f"{progress}%" if progress else "N/A"
            
            # Format updated time
            try:
                updated_dt = datetime.fromisoformat(updated.replace('Z', '+00:00'))
                time_ago = datetime.now() - updated_dt.replace(tzinfo=None)
                if time_ago.seconds < 60:
                    updated_str = f"{time_ago.seconds}s ago"
                elif time_ago.seconds < 3600:
                    updated_str = f"{time_ago.seconds//60}m ago"
                else:
                    updated_str = f"{time_ago.seconds//3600}h ago"
            except:
                updated_str = "unknown"
            
            # Choose color
            if status == 'completed':
                color = curses.color_pair(6)
            elif status == 'running':
                color = curses.color_pair(1)
            elif status == 'failed':
                color = curses.color_pair(3)
            else:
                color = curses.color_pair(2)
                
            line = f"{job_id:<4} {job_type:<19} {status:<11} {progress_str:<9} {updated_str}"
            self.stdscr.addstr(y, 4, line, color)
            y += 1
            
        return y + 1

    def draw_file_activity(self, y):
        """Draw file system activity"""
        self.stdscr.addstr(y, 2, "📁 FILE ACTIVITY", curses.color_pair(5) | curses.A_BOLD)
        y += 2
        
        activity = self.check_file_activity()
        
        if not activity:
            self.stdscr.addstr(y, 4, "No activity directories found", curses.color_pair(2))
            return y + 2
            
        # Header
        self.stdscr.addstr(y, 4, "DIRECTORY               RECENT  TOTAL   LAST_MODIFIED", 
                          curses.color_pair(4) | curses.A_BOLD)
        y += 1
        
        for dir_name, info in sorted(activity.items()):
            if 'error' in info:
                line = f"{dir_name:<23} ERROR: {info['error']}"
                color = curses.color_pair(3)
            else:
                # Format last modified
                if info['last_modified'] > 0:
                    last_mod = datetime.fromtimestamp(info['last_modified'])
                    time_ago = datetime.now() - last_mod
                    if time_ago.seconds < 60:
                        mod_str = f"{time_ago.seconds}s ago"
                    elif time_ago.seconds < 3600:
                        mod_str = f"{time_ago.seconds//60}m ago"
                    else:
                        mod_str = f"{time_ago.seconds//3600}h ago"
                else:
                    mod_str = "never"
                
                line = f"{dir_name:<23} {info['recent_files']:>6}  {info['total_files']:>5}   {mod_str}"
                
                # Color based on recent activity
                if info['recent_files'] > 0:
                    color = curses.color_pair(1)  # Green for active
                elif info['total_files'] > 0:
                    color = curses.color_pair(4)  # Blue for has files
                else:
                    color = curses.color_pair(2)  # Yellow for empty
                    
            self.stdscr.addstr(y, 4, line, color)
            y += 1
            
        return y + 1

    def draw_logs(self, y):
        """Draw recent log entries"""
        max_y = curses.LINES - 3
        available_lines = max_y - y
        
        if available_lines < 5:
            return y
            
        self.stdscr.addstr(y, 2, "📝 RECENT ACTIVITY", curses.color_pair(5) | curses.A_BOLD)
        y += 2
        
        # Collect recent log entries from various sources
        log_files = [
            'logs/api_enhanced.log',
            'logs/humanizer_api.log', 
            'api.log',
            'lighthouse_api.log'
        ]
        
        recent_logs = []
        for log_file in log_files:
            if Path(log_file).exists():
                lines = self.get_log_tail(log_file, 3)
                for line in lines:
                    if line.strip():
                        recent_logs.append(f"[{Path(log_file).stem}] {line.strip()}")
        
        # Add process monitoring logs
        recent_logs.extend(list(self.log_lines)[-5:])
        
        # Show most recent entries
        display_lines = min(available_lines - 2, len(recent_logs))
        for i in range(display_lines):
            if i < len(recent_logs):
                log_line = recent_logs[-(display_lines-i)]
                
                # Color code based on content
                color = curses.color_pair(4)  # Default blue
                for pattern in self.error_patterns:
                    if re.search(pattern, log_line, re.IGNORECASE):
                        color = curses.color_pair(3)  # Red for errors
                        break
                
                # Truncate if too long
                max_width = curses.COLS - 6
                if len(log_line) > max_width:
                    log_line = log_line[:max_width-3] + "..."
                    
                self.stdscr.addstr(y + i, 4, log_line, color)
        
        return y + display_lines + 1

    def draw_controls(self):
        """Draw control instructions at bottom"""
        controls = "Controls: 'q'=quit, 'r'=refresh, 'c'=clear logs, SPACE=pause"
        y = curses.LINES - 2
        self.stdscr.addstr(y, 2, controls, curses.color_pair(4))

    def refresh_display(self):
        """Refresh the entire display"""
        self.stdscr.clear()
        
        try:
            y = self.draw_header()
            y = self.draw_processes(y)
            y = self.draw_database_jobs(y)
            y = self.draw_file_activity(y)
            y = self.draw_logs(y)
            self.draw_controls()
            
            self.stdscr.refresh()
        except curses.error:
            # Handle terminal resize or other display errors
            pass

    def run(self):
        """Main UI loop"""
        self.stdscr.nodelay(True)  # Non-blocking input
        self.stdscr.timeout(int(self.refresh_interval * 1000))
        
        paused = False
        
        while self.running:
            if not paused:
                self.refresh_display()
            
            # Handle input
            try:
                key = self.stdscr.getch()
                if key == ord('q') or key == ord('Q'):
                    self.running = False
                elif key == ord('r') or key == ord('R'):
                    self.refresh_display()
                elif key == ord('c') or key == ord('C'):
                    self.log_lines.clear()
                    self.refresh_display()
                elif key == ord(' '):
                    paused = not paused
                    status = "PAUSED" if paused else "RUNNING"
                    self.stdscr.addstr(0, curses.COLS - 15, f"[{status}]", 
                                     curses.color_pair(2) if paused else curses.color_pair(1))
                    self.stdscr.refresh()
            except curses.error:
                pass
            
            if not paused:
                time.sleep(self.refresh_interval)

def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--help':
        print("""
Batch Status UI - Real-time monitoring for Humanizer batch processing

Usage: python batch_status_ui.py

Controls:
  q/Q     - Quit
  r/R     - Force refresh
  c/C     - Clear activity logs  
  SPACE   - Pause/resume updates

Features:
  - Real-time process monitoring
  - Database job status tracking
  - File system activity monitoring
  - Loop and crash detection
  - Recent log tail viewing
  - Color-coded status indicators

Status Colors:
  🟢 Green  - Running/Active/Recent activity
  🟡 Yellow - Pending/Warning/Old files
  🔴 Red    - Error/Crashed/Failed
  🔵 Blue   - Info/Stable
  🟣 Purple - Completed
  🟦 Cyan   - Highlighted
        """)
        return

    try:
        curses.wrapper(lambda stdscr: BatchStatusUI(stdscr).run())
    except KeyboardInterrupt:
        print("\nMonitoring stopped.")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()