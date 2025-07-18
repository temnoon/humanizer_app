#!/usr/bin/env python3
"""
Simple startup script that works with minimal dependencies
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def check_port(port):
    """Check if a port is in use"""
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        return result == 0
    except:
        return False

def start_service(name, script, port):
    """Start a service"""
    if check_port(port):
        print(f"⚠️  {name} already running on port {port}")
        return True
    
    print(f"🚀 Starting {name} on port {port}...")
    
    # Change to project directory
    project_dir = Path("/Users/tem/humanizer_api")
    os.chdir(project_dir)
    
    # Create logs directory
    logs_dir = project_dir / "logs"
    logs_dir.mkdir(exist_ok=True)
    
    # Start the service
    log_file = logs_dir / f"{name}.log"
    
    try:
        # Activate virtual environment and start service
        cmd = f"source venv/bin/activate && cd src && python {script}"
        
        with open(log_file, 'w') as f:
            process = subprocess.Popen(
                cmd,
                shell=True,
                stdout=f,
                stderr=subprocess.STDOUT,
                cwd=project_dir
            )
        
        # Save PID
        pid_file = logs_dir / f"{name}.pid"
        with open(pid_file, 'w') as f:
            f.write(str(process.pid))
        
        # Wait a moment and check if it started
        time.sleep(3)
        
        if check_port(port):
            print(f"✅ {name} started successfully (PID: {process.pid})")
            return True
        else:
            print(f"❌ {name} failed to start (check {log_file})")
            return False
            
    except Exception as e:
        print(f"❌ Error starting {name}: {e}")
        return False

def main():
    print("🚀 Simple Humanizer API Starter")
    print("==============================")
    
    services = [
        ("archive_api", "archive_api.py", 7200),
        ("lpe_api", "lpe_api.py", 7201)
    ]
    
    success_count = 0
    for name, script, port in services:
        if start_service(name, script, port):
            success_count += 1
    
    print(f"\n📊 Started {success_count}/{len(services)} services")
    
    if success_count > 0:
        print("\n🎉 Services are starting!")
        print("========================")
        print("📚 Archive API:     http://localhost:7200")
        print("🧠 LPE API:         http://localhost:7201")
        print("")
        print("📖 API Documentation:")
        print("   Archive API docs: http://localhost:7200/docs")
        print("   LPE API docs:     http://localhost:7201/docs")
        print("")
        print("📝 Check logs:")
        print("   tail -f logs/archive_api.log")
        print("   tail -f logs/lpe_api.log")
        print("")
        print("🛑 To stop: ./stop_humanizer_api.sh")
    
    else:
        print("\n❌ No services started successfully")
        print("💡 Try installing missing dependencies:")
        print("   source venv/bin/activate")
        print("   pip install httpx rich pydantic-settings python-dotenv")

if __name__ == "__main__":
    main()
