#!/usr/bin/env python3
"""
Quick test script to verify dependencies and start services manually
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        import fastapi
        print("✅ FastAPI available")
    except ImportError as e:
        print(f"❌ FastAPI missing: {e}")
        return False
    
    try:
        import httpx
        print("✅ HTTPX available")
    except ImportError as e:
        print(f"❌ HTTPX missing: {e}")
        return False
    
    try:
        import rich
        print("✅ Rich available")
    except ImportError as e:
        print(f"❌ Rich missing: {e}")
        return False
    
    try:
        import pydantic
        print("✅ Pydantic available")
    except ImportError as e:
        print(f"❌ Pydantic missing: {e}")
        return False
        
    try:
        from pydantic_settings import BaseSettings
        print("✅ Pydantic Settings available")
    except ImportError as e:
        print(f"❌ Pydantic Settings missing: {e}")
        print("💡 Install with: pip install pydantic-settings")
        return False
    
    try:
        import sqlalchemy
        print("✅ SQLAlchemy available")
    except ImportError as e:
        print(f"❌ SQLAlchemy missing: {e}")
        return False
    
    return True

def test_config():
    """Test configuration loading"""
    print("\n🔧 Testing configuration...")
    
    try:
        from config import get_config
        config = get_config()
        print(f"✅ Configuration loaded")
        print(f"   Archive API port: {config.api.archive_api_port}")
        print(f"   LPE API port: {config.api.lpe_api_port}")
        return True
    except Exception as e:
        print(f"❌ Configuration failed: {e}")
        return False

def start_archive_api():
    """Start Archive API manually"""
    print("\n🚀 Starting Archive API...")
    
    try:
        from archive_api import create_archive_api
        import uvicorn
        from config import get_config
        
        config = get_config()
        app = create_archive_api()
        
        print(f"Archive API starting on port {config.api.archive_api_port}...")
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=config.api.archive_api_port,
            log_level="info"
        )
        
    except Exception as e:
        print(f"❌ Archive API failed: {e}")
        return False

def start_lpe_api():
    """Start LPE API manually"""
    print("\n🚀 Starting LPE API...")
    
    try:
        from lpe_api import create_lpe_api
        import uvicorn
        from config import get_config
        
        config = get_config()
        app = create_lpe_api()
        
        print(f"LPE API starting on port {config.api.lpe_api_port}...")
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=config.api.lpe_api_port,
            log_level="info"
        )
        
    except Exception as e:
        print(f"❌ LPE API failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Humanizer API Test & Manual Startup")
    print("====================================")
    
    if not test_imports():
        print("\n❌ Some dependencies are missing. Please run:")
        print("   source venv/bin/activate")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    
    if not test_config():
        print("\n❌ Configuration test failed")
        sys.exit(1)
    
    print("\n✅ All tests passed!")
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "archive":
            start_archive_api()
        elif sys.argv[1] == "lpe":
            start_lpe_api()
        else:
            print(f"\nUsage: {sys.argv[0]} [archive|lpe]")
    else:
        print("\n💡 To start services:")
        print(f"   python {sys.argv[0]} archive    # Start Archive API")
        print(f"   python {sys.argv[0]} lpe        # Start LPE API")
        print("   ./start_humanizer_api.sh        # Start all services")
