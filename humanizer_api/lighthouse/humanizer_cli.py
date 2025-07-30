#!/usr/bin/env python3
"""
Humanizer CLI - Minimal command-line interface for the Enhanced API
Pure CLI with file output support - no GUI, all business logic in API
"""

import requests
import json
import sys
import argparse
import time
from pathlib import Path
from typing import Dict, Any, Optional
import tempfile

API_BASE = "http://127.0.0.1:8100"

class HumanizerCLI:
    """Minimal CLI client for Humanizer Enhanced API"""
    
    def __init__(self, api_base: str = API_BASE):
        self.api_base = api_base
        self.session = requests.Session()
    
    def check_api_health(self) -> bool:
        """Check if API is responding"""
        try:
            response = self.session.get(f"{self.api_base}/health", timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def transform_text(self, 
                      narrative: str,
                      persona: str = "philosophical_narrator",
                      namespace: str = "existential_philosophy", 
                      style: str = "contemplative_prose",
                      output_file: Optional[str] = None) -> Dict[str, Any]:
        """Transform narrative text"""
        
        payload = {
            "narrative": narrative,
            "target_persona": persona,
            "target_namespace": namespace,
            "target_style": style
        }
        
        print(f"🔄 Transforming text (persona: {persona}, namespace: {namespace}, style: {style})")
        start_time = time.time()
        
        try:
            response = self.session.post(f"{self.api_base}/transform", json=payload, timeout=120)
            response.raise_for_status()
            
            result = response.json()
            duration = time.time() - start_time
            
            print(f"✅ Transform completed in {duration:.1f}s")
            
            # Save to file if requested
            if output_file:
                self.save_result(result, output_file)
                print(f"💾 Result saved to {output_file}")
            
            return result
            
        except requests.RequestException as e:
            print(f"❌ API Error: {e}")
            return {}
    
    def extract_attributes(self, text: str, output_file: Optional[str] = None) -> Dict[str, Any]:
        """Extract narrative attributes from text"""
        
        payload = {"text": text, "mode": "comprehensive"}
        
        print("🧬 Extracting narrative attributes...")
        start_time = time.time()
        
        try:
            response = self.session.post(f"{self.api_base}/api/extract-attributes", json=payload, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            duration = time.time() - start_time
            
            print(f"✅ Attributes extracted in {duration:.1f}s")
            
            if output_file:
                self.save_result(result, output_file)
                print(f"💾 Attributes saved to {output_file}")
            
            return result
            
        except requests.RequestException as e:
            print(f"❌ API Error: {e}")
            return {}
    
    def analyze_meaning(self, text: str, output_file: Optional[str] = None) -> Dict[str, Any]:
        """Analyze text using Lamish meaning analysis"""
        
        payload = {"text": text, "analysis_depth": "comprehensive"}
        
        print("🧠 Analyzing meaning with Lamish engine...")
        start_time = time.time()
        
        try:
            response = self.session.post(f"{self.api_base}/lamish/analyze", json=payload, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            duration = time.time() - start_time
            
            print(f"✅ Analysis completed in {duration:.1f}s")
            
            if output_file:
                self.save_result(result, output_file)
                print(f"💾 Analysis saved to {output_file}")
            
            return result
            
        except requests.RequestException as e:
            print(f"❌ API Error: {e}")
            return {}
    
    def quantum_analysis(self, text: str, output_file: Optional[str] = None) -> Dict[str, Any]:
        """Run quantum narrative theory analysis"""
        
        payload = {"text": text, "analysis_depth": "comprehensive"}
        
        print("⚛️ Running quantum narrative analysis...")
        start_time = time.time()
        
        try:
            response = self.session.post(f"{self.api_base}/api/narrative-theory/analyze", json=payload, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            duration = time.time() - start_time
            
            print(f"✅ Quantum analysis completed in {duration:.1f}s")
            
            if output_file:
                self.save_result(result, output_file)
                print(f"💾 Analysis saved to {output_file}")
            
            return result
            
        except requests.RequestException as e:
            print(f"❌ API Error: {e}")
            return {}
    
    def get_provider_status(self) -> Dict[str, Any]:
        """Get LLM provider status"""
        try:
            response = self.session.get(f"{self.api_base}/api/llm/status", timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"❌ API Error: {e}")
            return {}
    
    def save_result(self, result: Dict[str, Any], filename: str):
        """Save result to file"""
        output_path = Path(filename)
        
        if filename.endswith('.json'):
            with open(output_path, 'w') as f:
                json.dump(result, f, indent=2)
        else:
            # Save as formatted text
            with open(output_path, 'w') as f:
                if 'projection' in result:
                    # Transform result
                    f.write("NARRATIVE TRANSFORMATION\n")
                    f.write("=" * 50 + "\n\n")
                    f.write("ORIGINAL:\n")
                    f.write(result['original']['narrative'] + "\n\n")
                    f.write("TRANSFORMED:\n")
                    f.write(result['projection']['narrative'] + "\n\n")
                    f.write("REFLECTION:\n")
                    f.write(result['projection']['reflection'] + "\n\n")
                    f.write("PROCESS STEPS:\n")
                    for step in result.get('steps', []):
                        f.write(f"- {step['name']}: {step['duration_ms']}ms\n")
                elif 'attributes' in result:
                    # Attributes result
                    f.write("NARRATIVE ATTRIBUTES\n")
                    f.write("=" * 50 + "\n\n")
                    for attr in result['attributes']:
                        f.write(f"{attr['type'].upper()}: {attr['value']} (confidence: {attr['confidence']:.2f})\n")
                elif 'analysis' in result:
                    # Analysis result
                    f.write("NARRATIVE ANALYSIS\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(json.dumps(result, indent=2))
                else:
                    # Generic JSON result
                    f.write(json.dumps(result, indent=2))

def main():
    parser = argparse.ArgumentParser(description="Humanizer CLI - Narrative transformation and analysis")
    parser.add_argument("command", choices=["transform", "attributes", "analyze", "quantum", "status"], 
                       help="Command to execute")
    parser.add_argument("--text", "-t", help="Text to process (or use --file)")
    parser.add_argument("--file", "-f", help="Input file containing text")
    parser.add_argument("--output", "-o", help="Output file (JSON if .json, formatted text otherwise)")
    parser.add_argument("--persona", "-p", default="philosophical_narrator", 
                       help="Target persona for transformation")
    parser.add_argument("--namespace", "-n", default="existential_philosophy",
                       help="Target namespace for transformation") 
    parser.add_argument("--style", "-s", default="contemplative_prose",
                       help="Target style for transformation")
    parser.add_argument("--api-base", default=API_BASE, help="API base URL")
    
    args = parser.parse_args()
    
    cli = HumanizerCLI(args.api_base)
    
    # Check API health
    if not cli.check_api_health():
        print(f"❌ Cannot connect to API at {args.api_base}")
        print("Make sure the Enhanced API server is running:")
        print("  python api_enhanced.py")
        sys.exit(1)
    
    # Get input text
    if args.text:
        input_text = args.text
    elif args.file:
        try:
            input_text = Path(args.file).read_text()
        except FileNotFoundError:
            print(f"❌ File not found: {args.file}")
            sys.exit(1)
    elif args.command == "status":
        input_text = None
    else:
        # Read from stdin
        print("📝 Enter text (Ctrl+D to finish):")
        input_text = sys.stdin.read().strip()
        if not input_text:
            print("❌ No input text provided")
            sys.exit(1)
    
    # Execute command
    if args.command == "transform":
        result = cli.transform_text(input_text, args.persona, args.namespace, args.style, args.output)
        if result and not args.output:
            print("\n" + "="*60)
            print("TRANSFORMED TEXT:")
            print("="*60)
            print(result['projection']['narrative'])
            
    elif args.command == "attributes":
        result = cli.extract_attributes(input_text, args.output)
        if result and not args.output:
            print("\n" + "="*60) 
            print("EXTRACTED ATTRIBUTES:")
            print("="*60)
            for attr in result.get('attributes', []):
                print(f"{attr['type'].upper()}: {attr['value']} (confidence: {attr['confidence']:.2f})")
                
    elif args.command == "analyze":
        result = cli.analyze_meaning(input_text, args.output)
        if result and not args.output:
            print("\n" + "="*60)
            print("MEANING ANALYSIS:")
            print("="*60)
            print(json.dumps(result, indent=2))
            
    elif args.command == "quantum":
        result = cli.quantum_analysis(input_text, args.output)
        if result and not args.output:
            print("\n" + "="*60)
            print("QUANTUM ANALYSIS:")
            print("="*60)
            print(json.dumps(result, indent=2))
            
    elif args.command == "status":
        status = cli.get_provider_status()
        print("\n" + "="*60)
        print("LLM PROVIDER STATUS:")
        print("="*60)
        for provider, info in status.items():
            status_icon = "✅" if info.get('available') else "❌"
            print(f"{status_icon} {provider}: {info.get('status_message', 'Unknown')}")

if __name__ == "__main__":
    main()