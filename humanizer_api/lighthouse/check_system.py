#!/usr/bin/env python3
"""
System Compatibility Check for Humanizer CLI
Verifies all requirements are met before using the CLI
"""

import sys
import subprocess
import platform

def check_python():
    """Check Python version"""
    version = sys.version_info
    print(f"🐍 Python: {version.major}.{version.minor}.{version.micro}")
    
    if version.major >= 3 and version.minor >= 7:
        print("✅ Python version is compatible")
        return True
    else:
        print("❌ Python 3.7+ required")
        return False

def check_requests():
    """Check requests library"""
    try:
        import requests
        print(f"📡 Requests: {requests.__version__}")
        print("✅ Requests library available")
        return True
    except ImportError:
        print("❌ Requests library not found")
        print("Install with: pip3 install requests")
        return False

def check_api_server():
    """Check if API server is accessible"""
    try:
        import requests
        response = requests.get("http://127.0.0.1:8100/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"🌐 API Server: ✅ Running")
            print(f"   Provider: {data.get('provider', 'Unknown')}")
            print(f"   Model: {data.get('model', 'Unknown')}")
            return True
        else:
            print(f"🌐 API Server: ❌ Error {response.status_code}")
            return False
    except Exception as e:
        print(f"🌐 API Server: ❌ Not accessible")
        print(f"   Error: {str(e)}")
        print("   Start with: python api_enhanced.py")
        return False

def check_system_info():
    """Display system information"""
    print("\n" + "="*50)
    print("🖥️  SYSTEM INFORMATION")
    print("="*50)
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Architecture: {platform.machine()}")
    print(f"Python executable: {sys.executable}")
    
def main():
    print("🔍 Humanizer CLI System Check")
    print("="*40)
    
    checks = []
    checks.append(check_python())
    checks.append(check_requests())
    
    print("\n" + "="*40)
    print("🌐 CONNECTIVITY CHECK")
    print("="*40)
    api_ok = check_api_server()
    
    check_system_info()
    
    print("\n" + "="*50)
    print("📋 SUMMARY")
    print("="*50)
    
    if all(checks):
        print("✅ All requirements met!")
        if api_ok:
            print("✅ CLI ready to use!")
            print("\nTest with:")
            print("  python3 humanizer_cli.py status")
        else:
            print("⚠️  CLI ready, but API server needs to be started:")
            print("  cd /path/to/lighthouse")
            print("  source venv/bin/activate")
            print("  python api_enhanced.py")
    else:
        print("❌ Some requirements missing")
        print("See above for installation instructions")
    
    print("\n📚 Documentation:")
    print("  Requirements: REQUIREMENTS.md")
    print("  Usage Guide: CLI_USAGE.md")

if __name__ == "__main__":
    main()