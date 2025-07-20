#!/usr/bin/env python3
"""
Unified Archive System Demo
Shows how to set up and use the PostgreSQL unified archive with real Node Archive Browser data
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def print_header(title):
    """Print a fancy header"""
    print("\n" + "="*60)
    print(f"🎯 {title}")
    print("="*60)

def print_step(step_num, description):
    """Print a step with nice formatting"""
    print(f"\n📍 Step {step_num}: {description}")
    print("-" * 50)

def main():
    """Run the unified archive demo"""
    
    print_header("UNIFIED ARCHIVE SYSTEM DEMO")
    print("This demo shows how to consolidate Node Archive Browser conversations")
    print("into a single PostgreSQL database with powerful search capabilities.")
    
    # Demo configuration
    NODE_ARCHIVE_PATH = "/Users/tem/nab/exploded_archive_node"
    DATABASE_URL = "postgresql://localhost/humanizer_archive_demo"  # User can modify
    MAX_CONVERSATIONS = 50  # Limit for demo
    
    print(f"\n🔧 Demo Configuration:")
    print(f"   • Node Archive Path: {NODE_ARCHIVE_PATH}")
    print(f"   • Database URL: {DATABASE_URL}")
    print(f"   • Max Conversations: {MAX_CONVERSATIONS} (for demo)")
    
    # Check if Node archive exists
    if not Path(NODE_ARCHIVE_PATH).exists():
        print(f"\n❌ Error: Node archive path not found: {NODE_ARCHIVE_PATH}")
        print("Please update the NODE_ARCHIVE_PATH variable in this script.")
        return 1
    
    # Count available conversations
    conversation_dirs = list(Path(NODE_ARCHIVE_PATH).glob("*/conversation.json"))
    print(f"\n📊 Found {len(conversation_dirs)} conversations in Node archive")
    
    if len(conversation_dirs) == 0:
        print("❌ No conversation.json files found in the archive path")
        return 1
    
    # Show sample conversation info
    print(f"\n📋 Sample conversations found:")
    for i, conv_file in enumerate(conversation_dirs[:5]):
        folder_name = conv_file.parent.name
        print(f"   {i+1}. {folder_name}")
    if len(conversation_dirs) > 5:
        print(f"   ... and {len(conversation_dirs) - 5} more")
    
    print_step(1, "Database Setup")
    print("To set up the unified archive system:")
    print()
    print("1. Create PostgreSQL database:")
    print(f"   createdb humanizer_archive_demo")
    print()
    print("2. Install required extensions (optional):")
    print("   psql humanizer_archive_demo -c 'CREATE EXTENSION IF NOT EXISTS vector;'")
    print("   psql humanizer_archive_demo -c 'CREATE EXTENSION IF NOT EXISTS pg_trgm;'")
    print()
    print("3. Run the setup script:")
    
    setup_command = f"""python setup_unified_archive.py \\
  --database-url "{DATABASE_URL}" \\
  --node-archive-path "{NODE_ARCHIVE_PATH}" \\
  --max-conversations {MAX_CONVERSATIONS}"""
    
    print(f"   {setup_command}")
    
    print_step(2, "What the Setup Does")
    print("The setup script will:")
    print("✅ Create PostgreSQL unified archive schema")
    print("✅ Run Rails migrations for ActiveRecord models")
    print("✅ Import Node Archive Browser conversations")
    print("✅ Start Enhanced Archive API (port 7200)")
    print("✅ Start Rails API (port 3000)")
    print()
    print("Database schema includes:")
    print("• Full-text search indexes")
    print("• Conversation threading")
    print("• Semantic vector storage")
    print("• Quality scoring")
    print("• Multi-source support")
    
    print_step(3, "Example API Usage")
    print("Once setup is complete, you can:")
    print()
    
    print("🔍 Search across all conversations:")
    print("""curl -X POST http://localhost:7200/search \\
  -H "Content-Type: application/json" \\
  -d '{
    "query": "quantum mechanics",
    "source_types": ["node_conversation"],
    "limit": 10
  }'""")
    print()
    
    print("📊 Get archive statistics:")
    print("curl http://localhost:3000/api/v1/unified_archive/statistics")
    print()
    
    print("🧵 Get conversation thread:")
    print("curl http://localhost:3000/api/v1/unified_archive/123/thread")
    print()
    
    print("📤 Export data:")
    print('curl "http://localhost:3000/api/v1/unified_archive/export?format=json"')
    
    print_step(4, "Rails ActiveRecord Usage")
    print("In Rails applications:")
    print()
    print("```ruby")
    print("# Search across all archives")
    print('results = ArchivedContent.search_unified("consciousness", {')
    print('  source_types: ["node_conversation"],')
    print('  author: "user",')
    print('  date_from: 1.month.ago')
    print('})')
    print()
    print("# Get conversation threads")
    print("conversation = ArchivedContent.find(123)")
    print("messages = conversation.conversation_thread")
    print()
    print("# Statistics")
    print("stats = ArchivedContent.statistics")
    print("# => {")
    print('#   total_content: 15420,')
    print('#   by_source_type: {"node_conversation" => 8500},')
    print('#   conversations_count: 1200,')
    print('#   average_quality_score: 0.76')
    print("# }")
    print()
    print("# Convert to WriteBook format")
    print("content.to_writebook_section")
    print("```")
    
    print_step(5, "Expected Results")
    print("After importing your Node Archive Browser data, you'll have:")
    print()
    print("📈 Comprehensive Statistics:")
    print(f"   • ~{len(conversation_dirs)} conversations imported")
    print(f"   • ~{len(conversation_dirs) * 10} individual messages (estimated)")
    print("   • Full-text search across all content")
    print("   • Conversation threading preserved")
    print()
    print("🔍 Powerful Search Capabilities:")
    print("   • Search by keywords, author, date range")
    print("   • Cross-conversation discovery")
    print("   • Semantic similarity (with vectors)")
    print()
    print("🚀 Integration Ready:")
    print("   • WriteBook section generation")
    print("   • Discourse platform publishing")
    print("   • LPE enhancement pipeline")
    
    print_step(6, "Next Steps")
    print("1. Run the setup command above")
    print("2. Test the APIs with the example curl commands")
    print("3. Import additional archive sources:")
    print("   • Social media exports")
    print("   • Email archives")
    print("   • Chat platform data")
    print()
    print("4. Set up LPE processing:")
    print("   • Content quality assessment")
    print("   • Attribute extraction")
    print("   • Semantic enhancement")
    print()
    print("5. Configure WriteBook integration:")
    print("   • Automatic section generation")
    print("   • Quality-based filtering")
    print("   • Discourse publishing")
    
    print_header("READY TO CONSOLIDATE YOUR ARCHIVES! 🚀")
    print("Run the setup command when you're ready to begin.")
    print()
    print("💡 Tip: Start with a small max-conversations value (like 10) for testing,")
    print("   then increase once you've verified everything works correctly.")
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n🛑 Demo interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Demo failed: {e}")
        sys.exit(1)