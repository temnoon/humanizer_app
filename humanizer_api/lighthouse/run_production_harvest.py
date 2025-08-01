#!/usr/bin/env python3
"""
Production Harvest Runner
Command to run the 100-book attribute harvesting
"""

import subprocess
import sys
from pathlib import Path

def run_harvest_command():
    """Generate the harvest command without dependencies"""
    
    print("🚀 PRODUCTION GUTENBERG HARVEST COMMAND")
    print("=" * 60)
    
    print("📋 STEP 1: Run the minimal test (works immediately):")
    print("   python minimal_harvester_test.py")
    print()
    
    print("📋 STEP 2: For full 100-book harvest, use one of:")
    print()
    
    print("🔧 OPTION A - CLI Harvester (requires dependencies):")
    print("   # Add 100 books to queue")
    print("   python mass_attribute_harvester.py add-range --start-id 1000 --end-id 1099 --max-paragraphs 1")
    print("   ")
    print("   # Process the queue")  
    print("   python mass_attribute_harvester.py process --max-workers 4 --output-dir ./production_attributes")
    print("   ")
    print("   # Check status")
    print("   python mass_attribute_harvester.py status")
    print()
    
    print("🔧 OPTION B - API Server (requires dependencies):")
    print("   # Start server")
    print("   python api_enhanced.py")
    print("   ")
    print("   # Use API endpoints:")
    print("   curl -X POST http://127.0.0.1:8100/gutenberg/analyze")
    print()
    
    print("🔧 OPTION C - Direct Script (works now, limited):")
    print("   python test_100_books_harvest.py")
    print()
    
    print("⚠️  NOTE: Options A & B require:")
    print("   pip install fastapi uvicorn spacy chromadb sentence-transformers")
    print("   python -m spacy download en_core_web_sm")
    print()
    
    print("✅ RECOMMENDED: Start with minimal test to verify system:")
    print("   python minimal_harvester_test.py")

if __name__ == "__main__":
    run_harvest_command()