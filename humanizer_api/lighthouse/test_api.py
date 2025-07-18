#!/usr/bin/env python3
"""
Test the Lighthouse API with example transformations
"""

import requests
import json
from typing import Dict, Any

API_URL = "http://localhost:8100"

def test_api_health():
    """Check if API is healthy"""
    response = requests.get(f"{API_URL}/health")
    if response.status_code == 200:
        print("✅ API is healthy")
        print(f"   Provider: {response.json()['llm_provider']}")
    else:
        print("❌ API health check failed")
        return False
    return True

def get_options() -> Dict[str, Any]:
    """Get available transformation options"""
    response = requests.get(f"{API_URL}/options")
    if response.status_code == 200:
        return response.json()
    return None

def transform_narrative(narrative: str, persona: str, namespace: str, style: str) -> Dict[str, Any]:
    """Transform a narrative"""
    payload = {
        "narrative": narrative,
        "target_persona": persona,
        "target_namespace": namespace,
        "target_style": style
    }
    
    response = requests.post(f"{API_URL}/transform", json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ Transformation failed: {response.status_code}")
        print(response.text)
    return None

def main():
    print("🔦 Lighthouse API Test Suite")
    print("=" * 40)
    
    # Test health
    if not test_api_health():
        return
    
    # Get options
    print("\n📋 Getting transformation options...")
    options = get_options()
    if options:
        print(f"   Personas: {len(options['personas'])}")
        print(f"   Namespaces: {len(options['namespaces'])}")
        print(f"   Styles: {len(options['styles'])}")
    
    # Test transformations
    test_cases = [
        {
            "narrative": "The team struggled with the deadline, but their determination saw them through.",
            "persona": "philosopher",
            "namespace": "lamish-galaxy",
            "style": "poetic"
        },
        {
            "narrative": "The algorithm efficiently sorted through millions of data points.",
            "persona": "mystic",
            "namespace": "dreamscape",
            "style": "mythological"
        },
        {
            "narrative": "Democracy requires active participation from informed citizens.",
            "persona": "poet",
            "namespace": "ancient-myths",
            "style": "baroque"
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n🧪 Test Case {i}")
        print(f"   Original: {test['narrative'][:50]}...")
        print(f"   Transform: {test['persona']} / {test['namespace']} / {test['style']}")
        
        result = transform_narrative(
            test['narrative'],
            test['persona'],
            test['namespace'],
            test['style']
        )
        
        if result:
            print(f"   ✅ Success!")
            print(f"   Essence: {result['original']['essence'][:80]}...")
            print(f"   Transformed: {result['projection']['narrative'][:80]}...")
            
            if result.get('lamish_pulse_signature'):
                print(f"   🔏 Pulse signature: {result['lamish_pulse_signature']['text_hash'][:32]}...")

if __name__ == "__main__":
    main()
