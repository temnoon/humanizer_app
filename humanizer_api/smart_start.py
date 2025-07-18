#!/usr/bin/env python3
"""
Smart startup script that tries full APIs first, falls back to simple versions
"""

import sys
import subprocess
import time
import os
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are available"""
    missing = []
    
    try:
        import httpx
    except ImportError:
        missing.append("httpx")
    
    try:
        import rich
    except ImportError:
        missing.append("rich")
    
    try:
        from pydantic_settings import BaseSettings
    except ImportError:
        missing.append("pydantic-settings")
    
    return missing

def start_simple_mode():
    """Start in simple mode with basic functionality"""
    print("🔧 Starting in Simple Mode")
    print("==========================")
    
    # Change to project directory
    os.chdir("/Users/tem/humanizer_api")
    
    print("🚀 Starting Simple Archive API...")
    
    # Try to start simple archive API
    try:
        subprocess.Popen([
            "venv/bin/python", "src/simple_archive_api.py"
        ], cwd="/Users/tem/humanizer_api")
        
        print("✅ Simple Archive API starting on port 7200")
        print("📚 Archive API: http://localhost:7200")
        print("📖 Try these endpoints:")
        print("   POST /ingest - Add content")
        print("   POST /search - Search content")
        print("   GET /stats - View statistics")
        print("   GET /health - Health check")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to start simple mode: {e}")
        return False

def start_full_mode():
    """Start in full mode with all features"""
    print("🚀 Starting in Full Mode")
    print("========================")
    
    # Change to project directory
    os.chdir("/Users/tem/humanizer_api")
    
    print("📦 Activating virtual environment...")
    
    services = [
        ("Archive API", "archive_api.py", 7200),
        ("LPE API", "lpe_api.py", 7201),
        ("Lawyer API", "lawyer_api.py", 7202)
    ]
    
    started = 0
    for name, script, port in services:
        try:
            print(f"🚀 Starting {name} on port {port}...")
            
            # Start service
            subprocess.Popen([
                "bash", "-c", f"cd /Users/tem/humanizer_api && source venv/bin/activate && cd src && python {script}"
            ])
            
            time.sleep(2)
            print(f"✅ {name} started")
            started += 1
            
        except Exception as e:
            print(f"❌ Failed to start {name}: {e}")
    
    if started > 0:
        print(f"\n🎉 Started {started}/{len(services)} services!")
        print("🔗 Service URLs:")
        for name, script, port in services[:started]:
            print(f"   {name}: http://localhost:{port}")
            print(f"   {name} docs: http://localhost:{port}/docs")
        return True
    else:
        print("❌ No services started successfully")
        return False

def main():
    print("🌐 Humanizer API Smart Starter")
    print("==============================")
    
    # Check dependencies
    missing_deps = check_dependencies()
    
    if missing_deps:
        print(f"⚠️  Missing dependencies: {', '.join(missing_deps)}")
        print("💡 To install: source venv/bin/activate && pip install " + " ".join(missing_deps))
        print("🔧 Trying Simple Mode instead...")
        
        if not start_simple_mode():
            print("\n❌ Both full and simple modes failed")
            print("💡 Try running: source venv/bin/activate && pip install -r requirements.txt")
            sys.exit(1)
    else:
        print("✅ All dependencies available")
        
        if not start_full_mode():
            print("🔧 Full mode failed, trying Simple Mode...")
            if not start_simple_mode():
                print("\n❌ Both full and simple modes failed")
                sys.exit(1)
    
    print("\n📊 To check status:")
    print("   python main.py status")
    print("🛑 To stop services:")
    print("   ./stop_humanizer_api.sh")

if __name__ == "__main__":
    main()
