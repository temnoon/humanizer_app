#!/usr/bin/env python3
"""
Unified API Transformations and CLI Commands Summary
"""

def list_api_transformations():
    """List all available transformations in the unified API"""
    
    print("🔄 UNIFIED API TRANSFORMATIONS")
    print("=" * 80)
    print("Server: http://127.0.0.1:8100")
    print("Docs: http://127.0.0.1:8100/docs")
    print()
    
    transformations = {
        "🧬 NARRATIVE TRANSFORMATION": {
            "POST /transform": "5-step LPE transformation (Deconstruct → Map → Reconstruct → Stylize → Reflect)",
            "POST /transform-large": "Large text transformation with context-aware splitting"
        },
        
        "🤔 MAIEUTIC DIALOGUE": {
            "POST /maieutic/start": "Start Socratic dialogue session",
            "POST /maieutic/question": "Generate next probing question",
            "POST /maieutic/answer": "Process answer and extract insights",
            "POST /maieutic/complete": "Complete dialogue session"
        },
        
        "🌐 TRANSLATION ANALYSIS": {
            "POST /translation/roundtrip": "Test semantic stability via round-trip translation",
            "POST /translation/stability": "Multi-language stability analysis"
        },
        
        "🧠 LAMISH MEANING ANALYSIS": {
            "POST /lamish/analyze": "Deep meaning analysis with concept extraction",
            "POST /lamish/extract-attributes": "Extract narrative attributes from text",
            "POST /lamish/sync-system": "Synchronize system attributes"
        },
        
        "⚛️ QUANTUM NARRATIVE THEORY": {
            "POST /api/narrative-theory/meaning-state": "Convert text to quantum meaning state",
            "POST /api/narrative-theory/semantic-tomography": "Semantic layer analysis",
            "POST /api/narrative-theory/coherence-check": "Check narrative coherence",
            "POST /api/narrative-theory/analyze": "Full QNT narrative analysis",
            "POST /quantum/narrative-spin": "Quantum narrative spin analysis"
        },
        
        "🧬 ATTRIBUTE EXTRACTION": {
            "POST /api/extract-attributes": "Extract narrative DNA attributes",
            "POST /literature/mine-attributes": "Mine literature for comprehensive attributes",
            "POST /literature/update-taxonomy": "Update system taxonomy with literature-derived attributes"
        },
        
        "👁️ VISION TRANSFORMATIONS": {
            "POST /vision/analyze": "Image analysis and description",
            "POST /vision/transcribe": "Handwriting transcription", 
            "POST /vision/redraw": "Artistic image analysis",
            "POST /image/generate": "Generate images from text"
        },
        
        "📚 GUTENBERG ANALYSIS": {
            "POST /gutenberg/analyze": "Analyze Project Gutenberg books",
            "POST /gutenberg/strategic-sample": "Strategic paragraph sampling",
            "POST /gutenberg/composite-analysis": "Composite narrative DNA analysis"
        }
    }
    
    for category, endpoints in transformations.items():
        print(f"{category}:")
        for endpoint, description in endpoints.items():
            print(f"  {endpoint} - {description}")
        print()
    
    print("=" * 80)
    print("🎯 KEY TRANSFORMATION FEATURES:")
    print("  • 5-Step LPE Process: Deconstruct → Map → Reconstruct → Stylize → Reflect")
    print("  • Quantum Meaning States: Advanced semantic analysis")
    print("  • Multi-language Stability: Translation consistency testing")
    print("  • Socratic Dialogue: AI-guided exploration")
    print("  • Vision Integration: Image analysis and generation")
    print("  • Literature Mining: Extract patterns from classic texts")

def list_cli_commands():
    """List all production CLI commands (non-test scripts)"""
    
    print("\n🖥️  PRODUCTION CLI COMMANDS")
    print("=" * 80)
    
    commands = {
        "🚀 API SERVER": {
            "python api_enhanced.py": "Start unified API server on port 8100"
        },
        
        "🧬 MASS ATTRIBUTE HARVESTER": {
            "python mass_attribute_harvester.py add-range --start-id N --end-id M": "Add book range to processing queue",
            "python mass_attribute_harvester.py add-classics": "Add curated classic literature to queue",
            "python mass_attribute_harvester.py process": "Process all queued jobs",
            "python mass_attribute_harvester.py status": "Show processing status and statistics"
        },
        
        "📊 BATCH MONITOR": {
            "python batch_monitor.py dashboard": "Interactive processing dashboard",
            "python batch_monitor.py status": "Show batch job status",
            "python batch_monitor.py cleanup --days N": "Clean up jobs older than N days",
            "python batch_monitor.py export --output file.json": "Export job data"
        },
        
        "🔄 PROJECTION DEMO": {
            "python simple_projection_demo.py --demo": "Run projection demonstration",
            "python simple_projection_demo.py --interactive": "Interactive projection mode"
        },
        
        "📚 LITERATURE MINING": {
            "python run_literature_mining.py --sample-size N": "Mine N literature samples",
            "python run_literature_mining.py --full-run": "Full literature mining run"
        },
        
        "💬 CONVERSATION IMPORTER": {
            "python conversation_importer_v2.py import path/to/file.json": "Import single conversation",
            "python conversation_importer_v2.py bulk path/to/directory/": "Bulk import conversations"
        },
        
        "🎭 GILGAMESH PROJECTION": {
            "python gilgamesh_projection_suite.py": "Interactive Gilgamesh projection suite"
        }
    }
    
    for category, command_list in commands.items():
        print(f"{category}:")
        for command, description in command_list.items():
            print(f"  {command}")
            print(f"    → {description}")
        print()
    
    print("🔧 COMMON OPTIONS:")
    print("  --help                  Show command help")
    print("  --output-dir DIR        Specify output directory")
    print("  --max-workers N         Set concurrent worker limit")
    print("  --priority N            Set job priority (1=highest, 5=lowest)")
    print("  --max-paragraphs N      Limit paragraphs per book")
    print("  --continuous            Continuous monitoring mode")
    print("  --force                 Force overwrite existing data")

def show_transformation_examples():
    """Show example transformation requests"""
    
    print("\n📋 TRANSFORMATION EXAMPLES")
    print("=" * 80)
    
    examples = [
        {
            "name": "Basic Narrative Transformation",
            "endpoint": "POST /transform",
            "payload": {
                "narrative": "The hero began his journey at dawn.",
                "target_persona": "philosophical_narrator",
                "target_namespace": "existential_philosophy", 
                "target_style": "contemplative_prose"
            }
        },
        {
            "name": "Maieutic Dialogue Start",
            "endpoint": "POST /maieutic/start",
            "payload": {
                "initial_text": "I believe artificial intelligence will replace human creativity.",
                "exploration_depth": "deep"
            }
        },
        {
            "name": "Quantum Meaning Analysis",
            "endpoint": "POST /api/narrative-theory/analyze",
            "payload": {
                "text": "Time flows like a river, carrying memories downstream.",
                "analysis_depth": "comprehensive"
            }
        },
        {
            "name": "Attribute Extraction",
            "endpoint": "POST /api/extract-attributes", 
            "payload": {
                "text": "She walked through the moonlit garden, lost in thought.",
                "mode": "comprehensive"
            }
        }
    ]
    
    for example in examples:
        print(f"🔹 {example['name']}:")
        print(f"   {example['endpoint']}")
        print(f"   Payload: {example['payload']}")
        print()

if __name__ == "__main__":
    list_api_transformations()
    list_cli_commands()  
    show_transformation_examples()