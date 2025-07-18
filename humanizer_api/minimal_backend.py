#!/usr/bin/env python3
"""
Minimal backend to support the frontend while resolving dependency issues.
Provides basic endpoints without heavy dependencies.
"""
import json
import subprocess
import sys
from pathlib import Path

# Try to import libraries, fallback gracefully
try:
    from http.server import HTTPServer, BaseHTTPRequestHandler
    import urllib.parse
    import urllib.request
    import socket
    import threading
    import time
except ImportError as e:
    print(f"Error importing basic libraries: {e}")
    sys.exit(1)

class MinimalAPIHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        """Handle GET requests"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        if self.path == '/health':
            response = {"status": "ok", "message": "Minimal backend running"}
        elif self.path == '/models':
            response = {
                "text_models": [
                    {"name": "mock-model", "size": "minimal"}
                ]
            }
        elif self.path == '/configurations':
            response = {
                "personas": [
                    {"id": "philosopher", "name": "Philosopher", "description": "Deep, contemplative perspective"},
                    {"id": "storyteller", "name": "Storyteller", "description": "Narrative-focused, engaging perspective"},
                    {"id": "scientist", "name": "Scientist", "description": "Analytical, evidence-based perspective"}
                ],
                "namespaces": [
                    {"id": "lamish-galaxy", "name": "Lamish Galaxy", "description": "Sci-fi universe with frequency-based technology"},
                    {"id": "natural-world", "name": "Natural World", "description": "Ecosystem and nature-based metaphors"},
                    {"id": "quantum-realm", "name": "Quantum Realm", "description": "Quantum physics and probability-based universe"}
                ],
                "styles": [
                    {"id": "poetic", "name": "Poetic", "description": "Lyrical, metaphorical language"},
                    {"id": "technical", "name": "Technical", "description": "Precise, specialized terminology"},
                    {"id": "casual", "name": "Casual", "description": "Conversational, informal tone"}
                ]
            }
        elif self.path.startswith('/api/llm/'):
            if 'status' in self.path:
                response = {
                    "mock": {
                        "available": True,
                        "model": "mock-model",
                        "has_key": True,
                        "key_valid": True,
                        "status_message": "Mock provider - always available"
                    }
                }
            elif 'configurations' in self.path:
                response = {
                    "task_configs": {
                        "deconstruct": {
                            "provider": "mock",
                            "model": "mock-model",
                            "temperature": 0.3,
                            "max_tokens": 800
                        }
                    }
                }
            elif 'keys' in self.path:
                response = {"stored_keys": [], "total_count": 0}
            else:
                response = {"message": "LLM endpoint placeholder"}
        else:
            response = {"message": "Minimal backend running", "endpoint": self.path}
        
        self.wfile.write(json.dumps(response).encode())

    def do_POST(self):
        """Handle POST requests"""
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        if self.path == '/transform':
            try:
                data = json.loads(post_data.decode())
                narrative = data.get('narrative', '')
                response = {
                    "original": {
                        "narrative": narrative,
                        "who": "Unknown",
                        "what": "Content",
                        "why": "Purpose unclear",
                        "how": "Method unspecified",
                        "outcome": "Result pending"
                    },
                    "projection": {
                        "narrative": f"[MOCK TRANSFORMATION] {narrative} → Transformed through {data.get('target_persona', 'default')} perspective in {data.get('target_namespace', 'default')} style.",
                        "embedding": [0.1, 0.2, 0.3, 0.4, 0.5]
                    },
                    "steps": [],
                    "total_duration_ms": 1000
                }
            except Exception as e:
                response = {"error": f"Transform error: {str(e)}"}
        else:
            response = {"message": "POST endpoint placeholder", "received_data": len(post_data)}
        
        self.wfile.write(json.dumps(response).encode())

def start_minimal_server(port=8100):
    """Start minimal HTTP server"""
    try:
        server = HTTPServer(('127.0.0.1', port), MinimalAPIHandler)
        print(f"\n🚀 Minimal Backend Server")
        print(f"================================")
        print(f"✅ Running on: http://127.0.0.1:{port}")
        print(f"✅ Health Check: http://127.0.0.1:{port}/health")
        print(f"✅ CORS enabled for frontend")
        print(f"✅ Basic endpoints: /health, /models, /configurations, /transform")
        print(f"\n🔧 This is a temporary backend while resolving dependency issues")
        print(f"📝 Supports basic frontend functionality")
        print(f"\nPress Ctrl+C to stop...")
        
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Shutting down minimal backend...")
        server.shutdown()
    except Exception as e:
        print(f"❌ Server error: {e}")

if __name__ == "__main__":
    start_minimal_server(8101)