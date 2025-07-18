#!/usr/bin/env python3
"""
Smart backend startup script that handles dependencies gracefully
and provides clear error messages.
"""
import sys
import subprocess
import os
from pathlib import Path

def check_and_install_basics():
    """Check for basic dependencies and install if needed"""
    required_packages = [
        'fastapi',
        'uvicorn', 
        'pydantic',
        'httpx'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"🔧 Installing missing basic packages: {', '.join(missing)}")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install'] + missing, check=True)
            print("✅ Basic packages installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install packages: {e}")
            return False
    
    return True

def start_enhanced_api():
    """Try to start the enhanced API with full features"""
    print("🚀 Starting Enhanced Lighthouse API...")
    try:
        # Change to lighthouse directory
        os.chdir('lighthouse')
        
        # Try to run with uvicorn
        cmd = [sys.executable, '-m', 'uvicorn', 'api_enhanced:app', '--host', '127.0.0.1', '--port', '8100', '--reload']
        print(f"Running: {' '.join(cmd)}")
        subprocess.run(cmd)
        
    except FileNotFoundError:
        print("❌ uvicorn not found, trying direct execution...")
        try:
            subprocess.run([sys.executable, 'api_enhanced.py'])
        except Exception as e:
            print(f"❌ Enhanced API failed: {e}")
            return False
    except Exception as e:
        print(f"❌ Enhanced API startup failed: {e}")
        return False
    
    return True

def start_minimal_fallback():
    """Start minimal backend as fallback"""
    print("🔧 Starting minimal fallback backend...")
    
    # Create a very simple FastAPI server
    minimal_code = '''
import sys
try:
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    import uvicorn
    import json
except ImportError as e:
    print(f"Missing dependency: {e}")
    sys.exit(1)

app = FastAPI(title="Minimal Lighthouse API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok", "mode": "minimal"}

@app.get("/models")
def models():
    return {"text_models": [{"name": "mock-model", "size": "minimal"}]}

@app.get("/configurations")
def configurations():
    return {
        "personas": [
            {"id": "philosopher", "name": "Philosopher", "description": "Deep, contemplative perspective"},
            {"id": "storyteller", "name": "Storyteller", "description": "Narrative-focused, engaging perspective"},
            {"id": "scientist", "name": "Scientist", "description": "Analytical, evidence-based perspective"}
        ],
        "namespaces": [
            {"id": "lamish-galaxy", "name": "Lamish Galaxy", "description": "Sci-fi universe"},
            {"id": "natural-world", "name": "Natural World", "description": "Nature-based metaphors"},
            {"id": "quantum-realm", "name": "Quantum Realm", "description": "Quantum physics universe"}
        ],
        "styles": [
            {"id": "poetic", "name": "Poetic", "description": "Lyrical, metaphorical language"},
            {"id": "technical", "name": "Technical", "description": "Precise, specialized terminology"},
            {"id": "casual", "name": "Casual", "description": "Conversational, informal tone"}
        ]
    }

@app.get("/api/llm/status")
def llm_status():
    return {
        "mock": {
            "available": True,
            "model": "mock-model", 
            "has_key": True,
            "key_valid": True,
            "status_message": "Mock provider - minimal mode"
        }
    }

@app.get("/api/llm/configurations")
def llm_configurations():
    return {
        "task_configs": {
            "deconstruct": {
                "provider": "mock",
                "model": "mock-model",
                "temperature": 0.3,
                "max_tokens": 800
            }
        }
    }

@app.post("/transform")
def transform(data: dict):
    narrative = data.get("narrative", "")
    return {
        "original": {
            "narrative": narrative,
            "who": "Unknown", "what": "Content", "why": "Purpose unclear",
            "how": "Method unspecified", "outcome": "Result pending"
        },
        "projection": {
            "narrative": f"[MINIMAL MODE] {narrative} → Transformed via {data.get('target_persona', 'default')} in {data.get('target_namespace', 'default')} style.",
            "embedding": [0.1, 0.2, 0.3, 0.4, 0.5]
        },
        "steps": [],
        "total_duration_ms": 500
    }

if __name__ == "__main__":
    print("🚀 Minimal Lighthouse API")
    print("=" * 40)
    print("✅ Running on: http://127.0.0.1:8100")
    print("⚠️  This is minimal mode - limited functionality")
    print("📋 Available endpoints: /health, /models, /configurations, /transform")
    uvicorn.run(app, host="127.0.0.1", port=8100)
'''
    
    try:
        with open('minimal_api.py', 'w') as f:
            f.write(minimal_code)
        
        subprocess.run([sys.executable, 'minimal_api.py'])
    except Exception as e:
        print(f"❌ Minimal fallback failed: {e}")
        return False
    
    return True

def main():
    print("🌟 Humanizer Lighthouse API Startup")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path('lighthouse').exists():
        print("❌ Must run from humanizer_api directory")
        print("💡 cd /Users/tem/humanizer-lighthouse/humanizer_api")
        sys.exit(1)
    
    # Install basic dependencies
    if not check_and_install_basics():
        print("❌ Could not install basic dependencies")
        sys.exit(1)
    
    # Try enhanced API first
    print("\n🎯 Attempting full-featured API...")
    try:
        if start_enhanced_api():
            return
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
        return
    except Exception as e:
        print(f"⚠️  Enhanced API failed: {e}")
    
    # Fallback to minimal
    print("\n🔧 Falling back to minimal mode...")
    try:
        start_minimal_fallback()
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
    except Exception as e:
        print(f"❌ All startup methods failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()