#!/usr/bin/env python3
"""
Fix missing dependencies and configuration issues
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd):
    """Run a command and return success status"""
    try:
        result = subprocess.run(cmd, shell=True, check=True, 
                              capture_output=True, text=True, 
                              cwd="/Users/tem/humanizer_api")
        print(f"✅ {cmd}")
        if result.stdout:
            print(f"   {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {cmd}")
        print(f"   Error: {e.stderr.strip()}")
        return False

def main():
    print("🔧 Fixing Humanizer API Dependencies")
    print("===================================")
    
    # Change to project directory
    os.chdir("/Users/tem/humanizer_api")
    
    print("\n1. Installing missing dependencies...")
    commands = [
        "venv/bin/pip install httpx==0.25.2",
        "venv/bin/pip install rich==13.7.0", 
        "venv/bin/pip install pydantic-settings==2.0.3",
        "venv/bin/pip install python-dotenv==1.0.0",
        "venv/bin/pip install fastapi==0.104.1",
        "venv/bin/pip install uvicorn[standard]==0.24.0"
    ]
    
    success_count = 0
    for cmd in commands:
        if run_command(cmd):
            success_count += 1
    
    print(f"\n📊 Installation Results: {success_count}/{len(commands)} successful")
    
    if success_count == len(commands):
        print("\n✅ All dependencies installed successfully!")
        print("\n🚀 Ready to start services:")
        print("   python test_setup.py archive")
        print("   python test_setup.py lpe")
        print("   python main.py dashboard")
    else:
        print("\n❌ Some installations failed. Please check the errors above.")
    
    print("\n🔗 Service URLs (when running):")
    print("   Archive API: http://localhost:7200/docs")
    print("   LPE API: http://localhost:7201/docs")

if __name__ == "__main__":
    main()
